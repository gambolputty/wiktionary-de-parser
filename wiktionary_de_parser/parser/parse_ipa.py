import mwparserfromhell
from mwparserfromhell.nodes.tag import Tag
from mwparserfromhell.nodes.template import Template
from mwparserfromhell.nodes.text import Text
from mwparserfromhell.wikicode import Wikicode

from wiktionary_de_parser.models import ParseIpaResult
from wiktionary_de_parser.parser import (
    Parser,
    extract_first_positional_value as _extract_ipa,
)

# Text nodes whose stripped value equals one of these are accepted as
# a separator between two consecutive {{Lautschrift}} templates.
# Tolerant by design: handles ", ", ",  ", ",", "; " etc. uniformly.
LAUTSCHRIFT_SEPARATORS = {",", ";"}

# Both Lautschrift and Lautschrift? (unverified) carry IPA. The walker
# treats whichever one is not the current target as ignorable rather than
# as a chain-terminating "other template" — otherwise an interleaved
# {{Lautschrift?}} would silently drop trailing verified Lautschrift values.
IPA_TEMPLATE_NAMES = {"Lautschrift", "Lautschrift?"}


class ParseIpa(Parser):
    name = "ipa"

    @staticmethod
    def parse_ipa_strings(
        parsed_paragraph: Wikicode, template_name: str = "Lautschrift"
    ):
        """
        Parse IPA-strings inside `{{<template_name>}}`-templates.

        Only the first list of comma-separated templates that directly
        follows an {{IPA}} template is collected. Regional, dialectal or
        grammatically inflected variants are intentionally skipped — they
        introduce non-separator text or non-matching templates that stop
        the walk.

        Examples (the templates marked with ★ are kept):

            :{{IPA}} ★{{Lautschrift|ˈkøːnɪç}}, ★{{Lautschrift|ˈkøːnɪk}}

            :{{IPA}} ★{{Lautschrift|ˈdʏsəlˌdɔʁfɐ}}, ''regional:'' {{Lautschrift|ˈdʏsəlˌdɔχfɔʶ}}

            :{{IPA}} ★{{Lautschrift|kʁɪˈtiːk}}, ★{{Lautschrift|kʁiˈtiːk}}, ''mitteldeutsch …:'' {{Lautschrift|-ˈtɪk}}

        `template_name` lets us re-run the same walk against `{{Lautschrift?}}`
        as a fallback when no verified Lautschrift exists.

        Reference: https://de.wiktionary.org/wiki/Hilfe:Aussprache
        """

        found_ipa: list[str] = []
        found_ipa_tmpl = False

        for node in parsed_paragraph.nodes:
            # 1. The {{IPA}} template must come first. mwparserfromhell keeps
            #    template-name whitespace (`{{ IPA }}` → name == ' IPA '),
            #    so always compare against the stripped form.
            if not found_ipa_tmpl:
                if (
                    isinstance(node, Template)
                    and str(node.name).strip() == "IPA"
                ):
                    found_ipa_tmpl = True
                continue

            # 2. Target Lautschrift template: extract first non-empty
            #    positional param. Named params (spr=de, lang=pt, …) and
            #    empty slots are skipped. A non-target IPA template
            #    ({{Lautschrift?}} during the verified pass, {{Lautschrift}}
            #    during the fallback pass) is tolerated as a no-op so it
            #    doesn't terminate the chain.
            if isinstance(node, Template):
                node_name = str(node.name).strip()
                if node_name == template_name:
                    ipa_text = _extract_ipa(node)
                    if ipa_text and ipa_text not in found_ipa:
                        found_ipa.append(ipa_text)
                    continue
                if node_name in IPA_TEMPLATE_NAMES:
                    continue

            # 3. Plain text. Pure whitespace is neutral. Comma/semicolon
            #    (with arbitrary surrounding whitespace) acts as a separator
            #    between two target templates. Anything else stops the walk
            #    once we've collected at least one IPA.
            if isinstance(node, Text):
                stripped = node.value.strip()
                if not stripped:
                    continue
                if stripped in LAUTSCHRIFT_SEPARATORS:
                    continue
                if not found_ipa:
                    continue
                break

            # 4. <ref> tags are footnote references — they may appear
            #    between or after templates and never end the chain.
            if isinstance(node, Tag) and node.tag == "ref":
                continue

            # 5. Any other node (regional marker template, italic span,
            #    a non-matching Lautschrift?, …): ignore if we haven't
            #    collected anything yet, otherwise stop.
            if not found_ipa:
                continue
            break

        return found_ipa or None

    @classmethod
    def parse(cls, wikitext: str):
        parsed_paragraph = mwparserfromhell.parse(wikitext)
        if not parsed_paragraph:
            return None
        result = cls.parse_ipa_strings(parsed_paragraph, "Lautschrift")
        # Fallback: some entries only have {{Lautschrift?}} ("unverified
        # pronunciation"). Pick those up when no verified Lautschrift
        # was found in the same paragraph.
        if result is None:
            result = cls.parse_ipa_strings(parsed_paragraph, "Lautschrift?")
        return result

    def run(self) -> ParseIpaResult:
        paragraph = self.find_paragraph("Aussprache", self.entry.wikitext)
        if not paragraph:
            return None
        return self.parse(paragraph)

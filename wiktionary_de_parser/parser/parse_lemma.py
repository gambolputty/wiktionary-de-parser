import re

import mwparserfromhell
from mwparserfromhell.nodes.comment import Comment
from mwparserfromhell.nodes.template import Template
from mwparserfromhell.nodes.text import Text

from wiktionary_de_parser.models import (
    Lemma,
    ParseLemmaResult,
    ReferenceType,
)
from wiktionary_de_parser.parser import Parser, resolve_positional_params


class ParseLemma(Parser):
    name = "lemma"

    @staticmethod
    def parse_lemma(text) -> tuple[str | None, ReferenceType]:
        """
        Parse lemma references from German Wiktionary wikitext.

        Extracts the target lemma and reference type from two template types:
        1. {{Grundformverweis}} - Inflected forms (declension/conjugation)
        2. {{Lemmaverweis}} - Variant forms (alternative spellings, etc.)

        Args:
            text: The wikitext to parse

        Returns:
            Tuple of (target_lemma, reference_type):
            - (None, NONE) if no reference template found
            - (str, INFLECTED) if Grundformverweis template found
            - (str, VARIANT) if Lemmaverweis template found

        Examples:
            {{Grundformverweis|gehören}} → ("gehören", INFLECTED)
            {{Lemmaverweis|mild}} → ("mild", VARIANT)
            No template → (None, NONE)
        """
        # Walk top-level nodes only — a form-reference template nested
        # inside body prose or a <ref>…</ref> citation must not hijack the
        # page lemma. By Wiktionary convention these templates always sit
        # at the top of the entry.
        parsed = mwparserfromhell.parse(text)
        template = None
        for node in parsed.nodes:
            if not isinstance(node, Template):
                continue
            name = str(node.name).strip()
            if name.startswith(
                ("Grundformverweis", "Lemmaverweis", "Alte Schreibweise")
            ):
                template = node
                break

        if template is None:
            return None, ReferenceType.NONE

        template_name = str(template.name).strip()
        if template_name.startswith("Grundformverweis"):
            ref_type = ReferenceType.INFLECTED
        else:
            ref_type = ReferenceType.VARIANT

        positional_map = resolve_positional_params(template)

        # Walk positionals; pick the first that resolves to a non-empty lemma.
        # Three patterns need special handling:
        #  - the param wraps the target in a nested template
        #    `{{linkZiel|is|kaldur}}` — extract the inner template's last
        #    positional.
        #  - the param is a section anchor `#Übersetzungen` — strips to "",
        #    fall through to the next positional.
        #  - the param is genuinely empty (`{{Alte Schreibweise||Reform 1996}}`)
        #    — return None, don't accept the next positional as the lemma
        #    (it's a marker, not a target).
        for index in sorted(positional_map):
            param = positional_map[index]
            value = param.value
            raw_with_comments = str(value)
            raw = re.sub(
                r"<!--.*?-->", "", raw_with_comments, flags=re.DOTALL
            ).strip()

            if not raw:
                return None, ReferenceType.NONE

            # Pure nested-template wrapper: only a single template node
            # with no surrounding content. Whitespace-only Text nodes and
            # HTML comments are filtered out; mixed text+template like
            # `stem-{{X|y}}` falls through to the whole-value path below.
            nontrivial_nodes = [
                n
                for n in value.nodes
                if not isinstance(n, Comment)
                and not (isinstance(n, Text) and not n.value.strip())
            ]
            if len(nontrivial_nodes) == 1 and isinstance(
                nontrivial_nodes[0], Template
            ):
                inner_positional = [
                    p
                    for p in nontrivial_nodes[0].params
                    if not p.showkey
                ]
                if inner_positional:
                    candidate = str(inner_positional[-1].value).strip()
                    candidate = re.sub(r"\#.+", "", candidate).strip()
                    if candidate:
                        return candidate, ref_type
                # Wrapper yielded nothing usable — try the next positional.
                continue

            candidate = re.sub(r"\#.+", "", raw).strip()
            if candidate:
                return candidate, ref_type

        return None, ReferenceType.NONE

    @classmethod
    def parse(cls, page_name: str, wikitext: str) -> Lemma:
        """
        Parse lemma information from a Wiktionary entry.

        Args:
            page_name: The name of the Wiktionary page
            wikitext: The wikitext content of the entry

        Returns:
            Lemma object with canonical form and reference type
        """
        found_lemma = page_name
        reference_type = ReferenceType.NONE

        parsed_lemma, ref_type = cls.parse_lemma(wikitext)
        if parsed_lemma:
            found_lemma = parsed_lemma
            reference_type = ref_type

        return Lemma(lemma=found_lemma, reference_type=reference_type)

    def run(self) -> ParseLemmaResult:
        """
        Parse lemma references from Wiktionary entries.

        Supports two types of references:

        1. Grundformverweis (inflected forms):
           - Declination: nouns, adjectives, pronouns
           - Conjugation: verbs
           Examples:
           - "gehörte" → "gehören" (verb conjugation)
           - "Häuser" → "Haus" (noun declension)

        2. Lemmaverweis (variant forms):
           - Alternative spellings: "Geografie" → "Geographie"
           - Regional variants: "Kücken" → "Küken"
           - Pronunciation variants: "milde" → "mild"

        References:
        - https://de.wiktionary.org/wiki/Kategorie:Flektierte_Form_(Deutsch)
        - https://de.wiktionary.org/wiki/Vorlage:Grundformverweis_Konj
        - https://de.wiktionary.org/wiki/Vorlage:Grundformverweis_Dekl
        - https://de.wiktionary.org/wiki/Vorlage:Grundformverweis (deprecated)
        - https://de.wiktionary.org/wiki/Vorlage:Lemmaverweis
        - https://de.wiktionary.org/wiki/Hilfe:Lemmaverweis
        """
        return self.parse(self.entry.page.name, self.entry.wikitext)

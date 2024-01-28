from dataclasses import dataclass
from typing import Union

import mwparserfromhell
from mwparserfromhell.nodes.tag import Tag
from mwparserfromhell.nodes.template import Template
from mwparserfromhell.nodes.text import Text
from mwparserfromhell.wikicode import Wikicode

from wiktionary_de_parser.helper import find_paragraph


@dataclass
class IPAType:
    ipa: list[str] | None
    rhymes: list[str] | None


def parse_paragraph(text: str):
    paragraph = find_paragraph("Aussprache", text)

    if not paragraph:
        return False

    return mwparserfromhell.parse(paragraph)


def parse_ipa_strings(text: Union[str, Wikicode]):
    """
    Parse IPA-strings inside "{{Lautschrift}}"-template

    Only allow the first list of comma separated {{Lautschrift}}-templates.
    Stop parsing when other node types follow (ignore inflected forms, regional slang, Austrian/Swiss dialect etc.)

    For example, only the first {{Lautschrift}}-template is parsed here:
        :{{IPA}} {{Lautschrift|ˈdʏsəlˌdɔʁfɐ}}, ''regional:'' {{Lautschrift|ˈdʏsəlˌdɔχfɔʶ}}
        :{{IPA}} {{Lautschrift|veːk}}, ''norddeutsch:'' {{Lautschrift|veːç}}, ''mitteldeutsch:'' {{Lautschrift|veːɕ}},
        :{{IPA}} {{Lautschrift|ˈçeːmɪʃ}}, ''[[süddeutsch]], [[österreichisch]], [[schweizerisch]]'' {{Lautschrift|ˈkeːmɪʃ}}, ''[[norddeutsch]]'' {{Lautschrift|ˈʃeːmɪʃ}}
    But all templates are parsed in this example:
        :{{IPA}} {{Lautschrift|ˈkøːnɪç}}, {{Lautschrift|ˈkøːnɪk}}
        :{{IPA}} {{Lautschrift|ʃtipuˈliːʁən}}, {{Lautschrift|stipuˈliːʁən}}
    Only the first two templates are parsed in this example:
        :{{IPA}} {{Lautschrift|kʁɪˈtiːk}}, {{Lautschrift|kʁiˈtiːk}}, ''mitteldeutsch, süddeutsch, österreichisch, schweizerisch vorwiegend:'' {{Lautschrift|-ˈtɪk}}<ref>Nach: {{Lit-Duden: Aussprachewörterbuch|A=7}}, Stichwort: ''Kritik''.</ref>

    Reference: https://de.wiktionary.org/wiki/Hilfe:Aussprache
    """

    parsed = parse_paragraph(text) if isinstance(text, str) else text

    if not parsed:
        return

    found_ipa: list[str] = []
    found_ipa_tmpl = False

    for node in parsed.nodes:
        # IPA-template must be present to start parsing Lautschrift-template
        if found_ipa_tmpl is False:
            if isinstance(node, Template) and node.name == "IPA":
                found_ipa_tmpl = True

        # allow "Lautschrift"-templates to follow
        elif isinstance(node, Template) and node.name == "Lautschrift" and node.params:
            ipa_text = str(node.params[0]).replace("…", "").strip()

            if ipa_text and ipa_text not in found_ipa:
                found_ipa.append(ipa_text)

        # allow commas between "Lautschrift"-template to follow
        elif isinstance(node, Text) and node.value == ", ":
            continue

        # allow "<ref>"-tags to follow
        elif isinstance(node, Tag) and node.tag == "ref":
            continue

        else:
            # skip if no IPA-string has been found yet
            if not found_ipa:
                continue
            # break if another not supported node follows
            else:
                break

    if found_ipa:
        return found_ipa


def parse_rhymes(text: Union[str, Wikicode]):
    parsed = parse_paragraph(text) if isinstance(text, str) else text

    if not parsed:
        return

    found_rhymes: list[str] = []
    found_rhyme_tmpl = False

    for node in parsed.nodes:
        # Reime-template must be present to start parsing Reim-template
        if found_rhyme_tmpl is False:
            if isinstance(node, Template) and node.name == "Reime":
                found_rhyme_tmpl = True

        # allow "Reim"-templates to follow
        elif isinstance(node, Template) and node.name == "Reim" and node.params:
            rhyme_text = str(node.params[0]).replace("…", "").strip()

            if rhyme_text and rhyme_text not in found_rhymes:
                found_rhymes.append(rhyme_text)

        # allow commas between "Reim"-template to follow
        elif isinstance(node, Text) and node.value == ", ":
            continue

        # allow "<ref>"-tags to follow
        elif isinstance(node, Tag) and node.tag == "ref":
            continue

        else:
            # skip if no Reim-template has been found yet
            if not found_rhymes:
                continue
            # break if another not supported node follows
            else:
                break

    if found_rhymes:
        return found_rhymes


def init(title: str, text: str, current_record) -> IPAType:
    result = {
        "ipa": None,
        "rhymes": None,
    }
    parsed = parse_paragraph(text)

    if parsed:
        ipa = parse_ipa_strings(parsed)
        if ipa:
            result["ipa"] = ipa  # type: ignore

        rhymes = parse_rhymes(parsed)
        if rhymes:
            result["rhymes"] = rhymes  # type: ignore

    return IPAType(**result)

import re
from typing import Dict, List, Literal, Union
import mwparserfromhell
from mwparserfromhell.nodes.template import Template
from mwparserfromhell.nodes.text import Text
from mwparserfromhell.nodes.tag import Tag

from wiktionary_de_parser.helper import find_paragraph


IPAInfo = Dict[Literal["ipa"], List[str]]
IPAResult = Union[Literal[False], IPAInfo]


def parse_ipa_strings(text: str):
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

    paragraph = find_paragraph("Aussprache", text)

    if not paragraph:
        return False

    found_ipa = []
    found_ipa_tmpl = False
    parsed = mwparserfromhell.parse(paragraph)

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

    return found_ipa if found_ipa else False


def init(title: str, text: str, current_record) -> IPAResult:
    result = parse_ipa_strings(text)

    return {"ipa": result} if result else False

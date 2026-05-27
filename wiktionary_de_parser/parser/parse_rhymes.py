import mwparserfromhell
from mwparserfromhell.nodes.tag import Tag
from mwparserfromhell.nodes.template import Template
from mwparserfromhell.nodes.text import Text
from mwparserfromhell.wikicode import Wikicode

from wiktionary_de_parser.models import ParseRhymesResult
from wiktionary_de_parser.parser import (
    Parser,
    extract_first_positional_value as _extract_rhyme,
)

# Same tolerance as parse_ipa: any comma/semicolon, with arbitrary
# surrounding whitespace, is a valid separator.
REIM_SEPARATORS = {",", ";"}


class ParseRhymes(Parser):
    name = "rhymes"

    @staticmethod
    def parse_rhymes(parsed_paragraph: Wikicode):
        found_rhymes: list[str] = []
        found_rhyme_tmpl = False

        for node in parsed_paragraph.nodes:
            if not found_rhyme_tmpl:
                if (
                    isinstance(node, Template)
                    and str(node.name).strip() == "Reime"
                ):
                    found_rhyme_tmpl = True
                continue

            if (
                isinstance(node, Template)
                and str(node.name).strip() == "Reim"
            ):
                rhyme_text = _extract_rhyme(node)
                if rhyme_text and rhyme_text not in found_rhymes:
                    found_rhymes.append(rhyme_text)
                continue

            if isinstance(node, Text):
                stripped = node.value.strip()
                if not stripped:
                    continue
                if stripped in REIM_SEPARATORS:
                    continue
                if not found_rhymes:
                    continue
                break

            if isinstance(node, Tag) and node.tag == "ref":
                continue

            if not found_rhymes:
                continue
            break

        return found_rhymes or None

    @classmethod
    def parse(cls, wikitext: str):
        parsed_paragraph = mwparserfromhell.parse(wikitext)
        if not parsed_paragraph:
            return None
        return cls.parse_rhymes(parsed_paragraph)

    def run(self) -> ParseRhymesResult:
        paragraph = self.find_paragraph("Aussprache", self.entry.wikitext)
        if not paragraph:
            return None
        return self.parse(paragraph)

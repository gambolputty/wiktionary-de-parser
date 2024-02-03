import mwparserfromhell
from mwparserfromhell.nodes.tag import Tag
from mwparserfromhell.nodes.template import Template
from mwparserfromhell.nodes.text import Text
from mwparserfromhell.wikicode import Wikicode

from wiktionary_de_parser.parser import Parser, ParserResult


class ParseRhymes(Parser):
    @staticmethod
    def parse_rhymes(parsed_paragraph: Wikicode):
        found_rhymes: list[str] = []
        found_rhyme_tmpl = False

        for node in parsed_paragraph.nodes:
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

    def run(self):
        paragraph = self.find_paragraph("Aussprache")
        parsed_paragraph = mwparserfromhell.parse(paragraph)
        result = None

        if parsed_paragraph:
            rhymes = self.parse_rhymes(parsed_paragraph)
            if rhymes:
                result = rhymes

        return ParserResult(name="rhymes", value=result)

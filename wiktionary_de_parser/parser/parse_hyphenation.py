import re

from wiktionary_de_parser.models import ParseHyphenationResult
from wiktionary_de_parser.parser import Parser


class ParseHyphenation(Parser):
    name = "hyphenation"

    @classmethod
    def parse_hyphenation(cls, name: str, wikitext: str):
        """
        Parse hyphenation
        "{{Worttrennung}}"-template.

        Problem:
        Commas can be part of the "title", but we don't know where they are and are not.

        Commas are part of "title":
            ge·sagt, ge·tan
        Commas are not part of "title":
            zwan·zig, zwan·zi·ge
            In·tel·li·genz·quo·ti·ent; In·tel·li·genz·quo·ti·en·ten

        Solution:
        Find "title" inside paragraph by determing start- and end-index and extract it with middle dots.

        Reference: https://de.wiktionary.org/wiki/Hilfe:Worttrennung
        """
        text = cls.strip_html_tags(wikitext)
        paragraph = cls.find_paragraph("Worttrennung", text)

        if not paragraph:
            return

        # remove false mid dot at the beginning that breaks the parser (":·nutz·lo·se")
        paragraph = paragraph.lstrip(":·")

        title_index = 0
        start_index = -1
        end_index = -1
        last_title_index = len(name) - 1
        last_paragraph_index = len(paragraph) - 1
        for index, char in enumerate(paragraph):
            # find index to start parsing from
            # test if title can be inserted from current index
            # remove mid dots for testing
            if start_index == -1:
                if paragraph[index:].replace("·", "").startswith(name):
                    start_index = index
                    end_index = index
                continue

            end_index += 1
            if char == "·":
                continue

            title_index += 1
            if (
                title_index >= last_title_index
                or char != name[title_index]
                or index == last_paragraph_index
            ):
                end_index += 1
                break

        # remove everything after actual_index
        clean_string = paragraph[start_index:end_index]

        # Remove comma and dot
        clean_string = re.sub(r"[.,]", "", clean_string)

        # split syllables, remove empty strings (ugly side effect of re.split)
        result = list(filter(None, re.split(r" |·|-", clean_string)))

        if result:
            return result

    @classmethod
    def parse(cls, name: str, wikitext: str):
        return cls.parse_hyphenation(name, wikitext)

    def run(self) -> ParseHyphenationResult:
        return self.parse(self.entry.page.name, self.entry.wikitext)

import re

from wiktionary_de_parser.models import ParseSyllablesResult
from wiktionary_de_parser.parser import Parser


class ParseSyllables(Parser):

    @classmethod
    def parse_syllables(cls, name: str, wikitext: str):
        """
        Parse syllables below "{{Worttrennung}}"-template.

        Problem:
        Commas can be part of the title, but we don't know when they are and are not.

        Commas are part of title:
            ge·sagt, ge·tan
        Commas are not part of title:
            zwan·zig, zwan·zi·ge
            In·tel·li·genz·quo·ti·ent; In·tel·li·genz·quo·ti·en·ten

        Solution:
        Find title inside paragraph by determing start- and end-index and extract it with middle dots.

        Reference: https://de.wiktionary.org/wiki/Hilfe:Worttrennung
        """
        title = name
        text = cls.strip_html_tags(wikitext)
        paragraph = cls.find_paragraph("Worttrennung", text)

        if not paragraph:
            return

        # remove false mid dot at the beginning that breaks the parser (":·nutz·lo·se")
        paragraph = paragraph.lstrip(":·")

        title_index = 0
        start_index = -1
        end_index = -1
        last_title_index = len(title) - 1
        last_paragraph_index = len(paragraph) - 1
        for index, char in enumerate(paragraph):
            # find index to start parsing from
            # test if title can be inserted from current index
            # remove mid dots for testing
            if start_index == -1:
                if paragraph[index:].replace("·", "").startswith(title):
                    start_index = index
                    end_index = index
                continue

            end_index += 1
            if char == "·":
                continue

            title_index += 1
            if (
                title_index >= last_title_index
                or char != title[title_index]
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
        return cls.parse_syllables(name, wikitext)

    def run(self) -> ParseSyllablesResult:
        return self.parse(self.entry.page.name, self.entry.wikitext)

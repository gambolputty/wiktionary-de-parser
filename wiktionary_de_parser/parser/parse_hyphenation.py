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

        # Affix markers on the lemma — "auto-" (prefix), "-ow" (suffix),
        # "-s-" (fugenelement). The hyphens are semantic markers, not
        # syllable separators. Re-attach them after splitting so callers
        # can still tell an affix entry from a regular lemma.
        has_prefix_marker = name.endswith("-")
        has_suffix_marker = name.startswith("-")

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

        # Strip stray template syntax left over by the char-walk when the
        # lemma sits inside a wrapper template like {{Polytonisch|ἡ}}.
        clean_string = re.sub(r"[{}|]", "", clean_string)
        # Replace "comma + whitespace" with whitespace so it acts as a word
        # separator ("gesagt, getan" → two words). Standalone commas inside
        # the lemma (chemical names: "1,2,3-Propan") and standalone dots
        # ("Web 2.0") are preserved.
        clean_string = re.sub(r"\s*,\s+", " ", clean_string)
        # The char-walk has an off-by-one for single-char lemmas that pulls
        # the next char in ("A," for the lemma "A"). Strip dangling
        # punctuation rather than rewriting the walk — but only what the
        # lemma itself doesn't end with, so abbreviations like "Mr.", "etc."
        # keep their trailing dot.
        trailing = "".join(c for c in ",.;:" if not name.endswith(c))
        if trailing:
            clean_string = clean_string.rstrip(trailing)

        # Split syllables. Use \s so trailing newlines don't end up glued
        # to the final syllable.
        result = list(filter(None, re.split(r"\s|·|-", clean_string)))

        if result:
            if has_suffix_marker:
                result[0] = "-" + result[0]
            if has_prefix_marker:
                result[-1] = result[-1] + "-"
            return result

    @classmethod
    def parse(cls, name: str, wikitext: str):
        return cls.parse_hyphenation(name, wikitext)

    def run(self) -> ParseHyphenationResult:
        return self.parse(self.entry.page.name, self.entry.wikitext)

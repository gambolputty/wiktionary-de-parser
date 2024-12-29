import re
from dataclasses import dataclass

import wikitextparser as wtp

from wiktionary_de_parser.models import MeaningDict, ParseMeaningsResults
from wiktionary_de_parser.parser import Parser

TEMPLATE_NAME_MAPPING = {
    "kPl.": "kein Plural",
    "übertr.": "übertragen",
    "ugs.": "umgangssprachlich",
    "intrans.": "intransitiv",
    "refl.": "reflexiv",
    "geh.": "gehoben",
    "süddt.": "süddeutsch",
    "nordd.": "norddeutsch",
    "norddt.": "norddeutsch",
    "südd.": "süddeutsch",
    "österr.": "österreichisch",
    "schweiz.": "schweizerisch",
    "reg.": "regional",
    "va.": "veraltet",
    "kSt.": "keine Steigerung",
    "hist.": "historisch",
    "fachspr.": "fachsprachlich",
    "BE": "britisch",
    "brit.": "britisch",
    "vul.": "vulgär",
    "vulg.": "vulgär",
    "adv.": "adverbial",
    "abw.": "abwertend",
    "scherzh.": "scherzhaft",
    "landsch.": "landschaftlich",
}

LEADING_DASH_PATTERN = re.compile(r"^— ")
NUMBERED_LIST_PATTERN = re.compile(r"^\[\d+[a-z]?\] ")

"""
TODO:
    Vorlage "Üt" (Übersetzung) -> https://de.wiktionary.org/wiki/Vorlage:%C3%9Ct
    Beispiel: https://de.wiktionary.org/wiki/%CF%87
"""


class WikiListItem:
    __slots__ = ["tags", "text", "sublist", "pattern"]

    def __init__(
        self, wikitext: str, pattern: str, sublist: "WikiList | None"
    ) -> None:
        parsed_wikitext = wtp.parse(wikitext)

        self.pattern = pattern
        self.text = self.parse_text(parsed_wikitext)
        self.tags = self.parse_templates(parsed_wikitext)
        self.sublist = sublist

    @staticmethod
    def parse_text(parsed_wikitext: wtp.WikiText) -> str:
        text = parsed_wikitext.plain_text()

        text = LEADING_DASH_PATTERN.sub("", text)
        text = NUMBERED_LIST_PATTERN.sub("", text)

        return text.strip()

    @staticmethod
    def parse_templates(parsed_wikitext: wtp.WikiText) -> list[str] | None:
        """
        Reference: https://de.wiktionary.org/wiki/Vorlage:K

        """
        templates = parsed_wikitext.templates

        if not templates:
            return None

        # Optimierte Template-Verarbeitung
        result = []
        for template in templates:
            if template.name == "K":
                # Flatten arguments direkt beim Einlesen
                result.extend(arg.value for arg in template.arguments)
            else:
                result.append(template.name)

        # Mapping nur auf das finale Ergebnis anwenden
        return [TEMPLATE_NAME_MAPPING.get(tag, tag) for tag in result]

    def export(self) -> MeaningDict:
        result: MeaningDict = {}

        if self.text:
            result["text"] = self.text

        if self.tags:
            result["tags"] = self.tags

        if self.sublist:
            result["sublist"] = self.sublist.export()

        return result


@dataclass(slots=True)
class WikiList:
    items: list[WikiListItem]

    def export(self) -> list[MeaningDict]:
        return [item.export() for item in self.items]


class ParseMeanings(Parser):
    name = "meanings"

    @classmethod
    def parse_wiki_list(cls, wiki_lists: list[wtp.WikiList]) -> WikiList | None:
        """
        List items might have empty text and tags, but a sublist.
        Example: https://de.wiktionary.org/wiki/Skizze

        Lists could have a depth of 3 (or more?)
        Example: https://de.wiktionary.org/wiki/wegen
        """

        list_items: list[WikiListItem] = []

        for wiki_list in wiki_lists:
            for index, raw_list_item in enumerate(wiki_list.items):
                # Parse nested lists, example:
                # https://de.wiktionary.org/wiki/ordo
                # Check if current list items has sublist
                sublists = wiki_list.sublists(index)
                sublist_parsed = (
                    cls.parse_wiki_list(sublists) if sublists else None
                )
                new_item = WikiListItem(
                    wikitext=raw_list_item,
                    pattern=wiki_list.pattern,
                    sublist=sublist_parsed,
                )

                # Check if last list item has pattern '\\*' and current new_item has not that pattern. If so, add new_item to
                # the sublist of the last list item
                last_item = list_items[-1] if list_items else None
                if (
                    list_items
                    and last_item
                    and last_item.pattern == "\\*"
                    and new_item.pattern != "\\*"
                ):
                    if not last_item.sublist:
                        last_item.sublist = WikiList(items=[])
                    last_item.sublist.items.append(new_item)
                else:
                    list_items.append(new_item)

        return WikiList(items=list_items) if list_items else None

    @classmethod
    def parse_meanings(cls, parsed_paragraph: wtp.WikiText):
        """
        Parse meanings from a given paragraph.

        """

        parsed_list = cls.parse_wiki_list(parsed_paragraph.get_lists())

        return parsed_list

    @classmethod
    def parse(cls, wikitext: str):
        parsed_paragraph = wtp.parse(wikitext)
        result = None

        if parsed_paragraph:
            meanings = cls.parse_meanings(parsed_paragraph)
            if meanings:
                result = meanings.export()

        return result

    def run(self) -> ParseMeaningsResults:
        paragraph = self.find_paragraph("Bedeutungen", self.entry.wikitext)
        result = None

        if paragraph:
            result = self.parse(paragraph)

        return result


def format_meaning_dict(meaning_dict: MeaningDict, level: int = 0) -> str:
    lines = []
    indent = "  " * level

    # Handle main text with bullet point
    text = meaning_dict.get("text", "").strip()
    if text:
        lines.append(f"{indent}• {text}")

    # Handle tags right after the text
    if "tags" in meaning_dict and meaning_dict["tags"]:
        tags_str = ", ".join(meaning_dict["tags"])
        # If there was no text, add bullet point with tags
        if not text:
            lines.append(f"{indent}• [{tags_str}]")
        else:
            # Add tags to the last line
            if lines:
                lines[-1] = f"{lines[-1]} [{tags_str}]"

    # Handle sublist with increased indentation
    if "sublist" in meaning_dict:
        for sub_item in meaning_dict["sublist"]:
            lines.append(format_meaning_dict(sub_item, level + 1))

    return "\n".join(lines)


def format_meanings(meanings: ParseMeaningsResults) -> str:
    if not meanings:
        return ""
    return "\n".join(format_meaning_dict(m) for m in meanings)

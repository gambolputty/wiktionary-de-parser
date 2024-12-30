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
    "bildungsspr.": "bildungssprachlich",
}

LEADING_DASH_PATTERN = re.compile(r"^— ")
NUMBERED_LIST_PATTERN = re.compile(r"^\[(?:\d+(?:\.\d+)*[a-z]?|[a-z])\] ")
IGNORED_TAG_NAMES = {
    "ft",
    "spr",
    "t1",
    "t2",
    "t3",
    "t4",
    "t5",
    "t6",
    "t7",
    "Prä",
    "Kas",
}
IGNORED_TAG_VALUES = {
    "QS Herkunft",
}

"""
TODO:
    Vorlage "Üt" (Übersetzung) -> https://de.wiktionary.org/wiki/Vorlage:%C3%9Ct
    Beispiel: https://de.wiktionary.org/wiki/%CF%87
"""


class WikiListItem:
    __slots__ = ["tags", "raw_tags", "text", "sublist", "pattern"]

    def __init__(
        self, wikitext: str, pattern: str, sublist: "WikiList | None"
    ) -> None:
        parsed_wikitext = wtp.parse(wikitext)

        self.pattern = pattern
        self.text = self.parse_text(parsed_wikitext)
        self.tags = self.parse_templates(parsed_wikitext)
        self.raw_tags, self.text = self.parse_raw_tags(self.text)
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


        TODO: fußnote?? https://de.wiktionary.org/wiki/Bifurkation

        """
        templates = parsed_wikitext.templates

        if not templates:
            return None

        # Optimierte Template-Verarbeitung
        result = []
        for template in templates:
            if template.name == "K":
                # Flatten arguments direkt beim Einlesen
                new_tags = [
                    arg.value
                    for arg in template.arguments
                    if arg.name not in IGNORED_TAG_NAMES
                    and arg.value not in IGNORED_TAG_VALUES
                ]
                if new_tags:
                    result.extend(new_tags)
            else:
                result.append(template.name)

        # Mapping nur auf das finale Ergebnis anwenden
        return [TEMPLATE_NAME_MAPPING.get(tag, tag) for tag in result]

    @staticmethod
    def parse_raw_tags(text: str) -> tuple[list[str] | None, str]:
        """
        When the text starts with one or few words before a colon, it is considered as tags.
        Returns a tuple of (tags, remaining_text) where tags is the list of tags before the colon and remaining_text is the text after the colon.
        """
        if not text:
            return None, text

        if ":" not in text:
            return None, text

        # Split the text by colon
        parts = text.split(":", 1)
        tags = None
        remaining_text = text

        if len(parts) > 1:
            # starting text should not be too long
            if len(parts[0]) > 50:
                return None, text

            tags = parts[0].split(", ")
            remaining_text = parts[1].strip()

        return tags, remaining_text

    def export(self) -> MeaningDict:
        result: MeaningDict = {}

        if self.text:
            result["text"] = self.text

        if self.tags:
            result["tags"] = self.tags

        if self.raw_tags:
            result["raw_tags"] = self.raw_tags

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

                # Dont save it if it has no text, tags or sublist
                if (
                    not new_item.text
                    and not new_item.tags
                    and not new_item.sublist
                ):
                    continue

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

    # Erstelle die Grundzeile mit Bullet Point
    current_line = f"{indent}• "

    # Füge zuerst raw_tags hinzu
    if "raw_tags" in meaning_dict and meaning_dict["raw_tags"]:
        raw_tags_str = ", ".join(meaning_dict["raw_tags"])
        current_line += f"<{raw_tags_str}> "

    # Füge dann tags hinzu
    if "tags" in meaning_dict and meaning_dict["tags"]:
        tags_str = ", ".join(meaning_dict["tags"])
        current_line += f"[{tags_str}] "

    # Füge den Haupttext hinzu
    text = meaning_dict.get("text", "").strip()
    if text:
        current_line += text

    # Füge die Zeile nur hinzu, wenn sie mehr als den Bullet Point enthält
    if len(current_line) > len(f"{indent}• "):
        lines.append(current_line.rstrip())

    # Handle sublist with increased indentation
    if "sublist" in meaning_dict:
        for sub_item in meaning_dict["sublist"]:
            lines.append(format_meaning_dict(sub_item, level + 1))

    return "\n".join(lines)


def format_meanings(meanings: list[list[MeaningDict]]) -> str:
    if not meanings:
        return ""

    lines = []

    for index, meanings_list in enumerate(meanings):
        if index > 0:
            lines.append(f"\nBedeutungen für den {index + 2}. Eintrag:")
        for meaning_dict in meanings_list:
            lines.append(format_meaning_dict(meaning_dict))

    return "\n".join(lines)

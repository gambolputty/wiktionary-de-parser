import wikitextparser as wtp

from wiktionary_de_parser.models import MeaningDict, ParseMeaningsResults
from wiktionary_de_parser.parser import Parser
from wiktionary_de_parser.utils.meanings.wiki_list import (
    WikiList,
    WikiListItem,
)


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
            lines.append("\nBedeutungen für den nächsten Eintrag:")
        for meaning_dict in meanings_list:
            lines.append(format_meaning_dict(meaning_dict))

    return "\n".join(lines)

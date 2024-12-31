import re
from dataclasses import dataclass

import wikitextparser as wtp

from wiktionary_de_parser.models import MeaningDict, ParseMeaningsResults
from wiktionary_de_parser.parser import Parser

# Reference:
# - https://de.wiktionary.org/wiki/Vorlage:K
# - https://de.wiktionary.org/wiki/Vorlage:K/Abk
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
    "Abl.": "mit Ablativ",
    "Ablativ": "mit Ablativ",
    "AE": "US-amerikanisch",
    "AmE": "US-amerikanisch",
    "Akkusativ": "mit Akkusativ",
    "alemann.": "alemannisch",
    "alemannisch": "alemannisch",
    "allg.": "allgemein",
    "allgemein": "allgemein",
    "alltagsspr.": "alltagssprachlich",
    "amtsspr.": "amtssprachlich",
    "ansonsten": "ansonsten",
    "attr.": "attributiv",
    "auch": "auch",
    "bair.": "bairisch",
    "bairisch": "bairisch",
    "bar.": "bairisch",
    "BrE": "britisch",
    "Bedva.": "veraltete Bedeutung",
    "Bedvatd.": "veraltende Bedeutung",
    "bei": "bei",
    "bes.": "besonders",
    "besonders": "besonders",
    "beziehungsweise": "beziehungsweise",
    "bzw.": "beziehungsweise",
    "bis": "bis",
    "bisweilen": "bisweilen",
    "das": "das",
    "Dativ": "mit Dativ",
    "DDR": "DDR",
    "der": "der",
    "dichter.": "dichterisch",
    "die": "die",
    "Dim.": "Diminutiv",
    "Dimin.": "Diminutiv",
    "Diminutiv": "Diminutiv",
    "eher": "eher",
    "erzg.": "erzgebirgisch",
    "erzgeb.": "erzgebirgisch",
    "erzgebirgisch": "erzgebirgisch",
    "euph.": "euphemistisch",
    "fam.": "familiär",
    "fig": "figürlich",
    "fig.": "figurativ",
    "früher": "früher",
    "Genitiv": "mit Genitiv",
    "gsm": "schweizerdeutsch",
    "häufig": "häufig",
    "haben": "Hilfsverb haben",
    "hebben": "Hilfsverb hebben",
    "hauptsächlich": "hauptsächlich",
    "ieS": "im engeren Sinne",
    "i.e.S.": "im engeren Sinne",
    "i. e. S.": "im engeren Sinne",
    "im": "im",
    "in": "in",
    "in Bezug auf": "in Bezug auf",
    "indekl.": "indeklinabel",
    "insbes.": "insbesondere",
    "Instrumental": "mit Instrumental",
    "intransitiv": "intransitiv",
    "iPl": "im Plural",
    "iron.": "ironisch",
    "iwS": "im weiteren Sinne",
    "i.w.S.": "im weiteren Sinne",
    "i. w. S.": "im weiteren Sinne",
    "jugendspr.": "jugendsprachlich",
    "kinderspr.": "kindersprachlich",
    "kirchenlateinisch": "kirchenlateinisch",
    "klasslat.": "klassischlateinisch",
    "klassischlateinisch": "klassischlateinisch",
    "kSg.": "kein Singular",
    "lautm.": "lautmalerisch",
    "leicht": "leicht",
    "Ling.": "Linguistik",
    "mA": "mit Akkusativ",
    "md.": "mitteldeutsch",
    "mdal.": "mundartlich",
    "Med.": "Medizin",
    "meißnisch": "meißnisch",
    "Meißnisch": "Meißnisch",
    "meist": "meist",
    "meistens": "meistens",
    "metaphor.": "metaphorisch",
    "meton.": "metonymisch",
    "mG": "mit Genitiv",
    "mit": "mit",
    "mitteld.": "mitteldeutsch",
    "mitunter": "mitunter",
    "mlat.": "mittellateinisch",
    "mittellateinisch": "mittellateinisch",
    "mundartl.": "mundartlich",
    "nDu.": "nur Dual",
    "nigr.": "nigrisch",
    "nkLat.": "nachklassischlateinisch",
    "nlat.": "neulateinisch",
    "noch": "noch",
    "noch in": "noch in",
    "nordwestd.": "nordwestdeutsch",
    "nPl.": "nur Plural",
    "nur": "nur",
    "nur noch": "nur noch",
    "obersächsisch": "obersächsisch",
    "Obersächsisch": "Obersächsisch",
    "oder": "oder",
    "oft": "oft",
    "oftmals": "oftmals",
    "ohne": "ohne",
    "osterländisch": "osterländisch",
    "Osterländisch": "Osterländisch",
    "Österreich": "Österreich",
    "ostfränkisch": "ostfränkisch",
    "pej.": "pejorativ",
    "Plural": "im Plural",
    "poet.": "poetisch",
    "PräpmG": "Präposition mit Genitiv",
    "PmG": "Präposition mit Genitiv",
    "respektive": "respektive",
    "sal.": "salopp",
    "schriftspr.": "schriftsprachlich",
    "schülerspr.": "schülersprachlich",
    "schwäb.": "schwäbisch",
    "schwäbisch": "schwäbisch",
    "Schweiz": "Schweiz",
    "Schweizerdeutsch": "Schweizerdeutsch",
    "seemannsspr.": "seemannssprachlich",
    "sein": "Hilfsverb sein",
    "sehr": "sehr",
    "seltener": "seltener",
    "seltener auch": "seltener auch",
    "soldatenspr.": "soldatensprachlich",
    "sonderspr.": "sondersprachlich",
    "sonst": "sonst",
    "sowie": "sowie",
    "spätlat.": "spätlateinisch",
    "spätlateinisch": "spätlateinisch",
    "später": "später",
    "speziell": "speziell",
    "techn.": "technisch",
    "teils": "teils",
    "teilweise": "teilweise",
    "tlwva.": "veraltete Bedeutung",
    "tlwvatd.": "veraltende Bedeutung",
    "trans.": "transitiv",
    "transitiv": "transitiv",
    "über": "über",
    "überwiegend": "überwiegend",
    "ungebr.": "ungebräuchlich",
    "unpers.": "unpersönlich",
    "unpersönlich": "unpersönlich",
    "ursprünglich": "ursprünglich",
    "vatd.": "veraltend",
    "verh.": "verhüllend",
    "volkst.": "volkstümlich",
    "von": "von",
    "vor allem": "vor allem",
    "vor allem in": "vor allem in",
    "vlat.": "vulgärlateinisch",
    "vulgärlat.": "vulgärlateinisch",
    "vulgärlateinisch": "vulgärlateinisch",
    "wien.": "wienerisch",
    "wienerisch": "wienerisch",
    "Wpräp": "Wechselpräposition",
    "z. B.": "zum Beispiel",
    "z. T.": "zum Teil",
    "zijn": "Hilfsverb zijn",
    "zum Beispiel": "zum Beispiel",
    "zum Teil": "zum Teil",
    "zumeist": "zumeist",
}
IGNORED_K_PARAMS = {
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
IGNORED_TEMPLATES = {"WP", "Internetquelle"}
LEADING_DASH_PATTERN = re.compile(r"^— ")
NUMBERED_LIST_PATTERN = re.compile(r"^\[(?:\d+(?:\.\d+)*[a-z]?|[a-z])\] ")
PAREN_MATCH_PATTERN = re.compile(r"^\s*\(([^)]+)\)\s*(.+)")
TAG_GROUP_PATTERN = re.compile(r"([^,()]+(?:\([^)]+\))?)")
HTML_TAG_PATTERN = re.compile(r"<[^>]+>.*?</[^>]+>|<[^>]+/>")
TAG_PAREN_PATTERN = re.compile(r"^(.+?)\s*\(([^)]+)\)$")

"""
TODO:
    Vorlage "Üt" (Übersetzung) -> https://de.wiktionary.org/wiki/Vorlage:%C3%9Ct
    Beispiel: https://de.wiktionary.org/wiki/%CF%87
"""


class TemplateParser:
    def __init__(self, template: wtp.Template):
        self.template = template

    def parse_k_template(self) -> list[str] | None:
        arguments = self.template.arguments
        new_tags = [
            arg.value for arg in arguments if arg.name not in IGNORED_K_PARAMS
        ]

        if new_tags:
            return new_tags

    def parse_ut_template(self) -> str | None:
        return self.template.arguments[1].value


class WikiListItem:
    __slots__ = ["tags", "raw_tags", "text", "sublist", "pattern"]

    def __init__(
        self, wikitext: str, pattern: str, sublist: "WikiList | None"
    ) -> None:
        parsed_wikitext = wtp.parse(wikitext)

        self.pattern = pattern
        self.text = self.parse_text(parsed_wikitext)
        self.tags = self.retrieve_template_tags(parsed_wikitext)
        self.raw_tags, self.text = self.parse_raw_tags(self.text)
        self.sublist = sublist

    @staticmethod
    def is_valid_template_name(template_name: str) -> bool:
        """
        Check if the template is valid.
        """
        blocked_prefixes = ("QS", "Ref-", "Lit-", "Wiki")

        return (
            len(template_name) < 50
            and len(template_name) > 1
            # Disallow lowercase templates with 2 or fewer characters
            and not (template_name.islower() and len(template_name) <= 2)
            and template_name not in IGNORED_TEMPLATES
            and not template_name.startswith(blocked_prefixes)
        )

    @staticmethod
    def parse_text(parsed_wikitext: wtp.WikiText) -> str:
        def replace_templates(template):
            name = template.name

            if name == "K":
                return ""

            if name == "Üt":
                return TemplateParser(template).parse_ut_template()

            if not WikiListItem.is_valid_template_name(template.name):
                return ""

            return TEMPLATE_NAME_MAPPING.get(template.name, template.name)

        text = parsed_wikitext.plain_text(
            replace_templates=(lambda template: replace_templates(template)),
        )

        text = LEADING_DASH_PATTERN.sub("", text)
        text = NUMBERED_LIST_PATTERN.sub("", text)

        return text.strip()

    @staticmethod
    def sanitize_template_name(text: str) -> str:
        """
        Sanitize the tag by removing unwanted characters.
        """

        """
        Strip html tags AND their content from the text.
        Example: 'text <ref>reference content</ref> more text' -> 'text more text'
        """
        text = HTML_TAG_PATTERN.sub("", text)

        # Replace &nbsp with space
        text = text.replace("&nbsp", " ")

        # Remove wiki markup
        text = wtp.remove_markup(text)

        """
        If the text starts with "(" and ends with ")", remove them.
        Examples:
            - (Rio Grande do Sul)
        """
        if text.startswith("(") and text.endswith(")"):
            text = text[1:-1]

        """
        TODO: What to do with "(Argentinien, Uruguay) ländlich"?
        """

        text = text.strip()

        return TEMPLATE_NAME_MAPPING.get(text, text)

    @staticmethod
    def retrieve_template_tags(
        parsed_wikitext: wtp.WikiText,
    ) -> list[str] | None:
        """
        Reference: https://de.wiktionary.org/wiki/Vorlage:K


        TODO: fußnote?? https://de.wiktionary.org/wiki/Bifurkation

        """
        templates = parsed_wikitext.templates

        if not templates:
            return None

        found_tags = []
        for template in templates:
            template_name = template.name
            parser = TemplateParser(template)

            if template_name == "K":
                new_tags = parser.parse_k_template()
                if new_tags:
                    found_tags.extend(new_tags)
            elif template_name == "Üt":
                new_tag = parser.parse_ut_template()
                if new_tag:
                    found_tags.append(new_tag)
            elif WikiListItem.is_valid_template_name(template_name):
                found_tags.append(template_name)

        # Sanitize tags
        found_tags = [
            tag_cleaned
            for tag in found_tags
            if (tag_cleaned := WikiListItem.sanitize_template_name(tag))
        ]

        return found_tags

    @staticmethod
    def has_multiple_parentheses(text: str) -> bool:
        """
        Check if the text contains multiple opening or closing parentheses.
        Returns True if there are multiple pairs or unmatched parentheses.
        """
        open_count = text.count("(")
        close_count = text.count(")")
        return open_count > 1 or close_count > 1 or open_count != close_count

    @staticmethod
    def parse_raw_tags(text: str) -> tuple[list[str] | None, str]:
        """
        Parses tags from text in the following formats:
        1. Leading parenthetical content: "(tag1, tag2) text"
        2. Colon-separated tags: "tag1, tag2: text"
        3. Tags with nested parentheses: "tag1 (subtag1, subtag2): text"

        Returns (tags, remaining_text) or (None, original_text) if no tags found.
        """
        if not text:
            return None, text

        # Pattern für Text der mit Klammern beginnt: (content) rest
        paren_match = PAREN_MATCH_PATTERN.match(text)
        if paren_match:
            content, remaining = paren_match.groups()
            # Nur verarbeiten wenn der Inhalt ein einzelnes Wort oder Komma-Liste ist
            if "," in content or " " not in content:
                raw_tags = [t.strip() for t in content.split(",") if t.strip()]
                raw_tags = [
                    t_clean
                    for t in raw_tags
                    if (t_clean := WikiListItem.sanitize_template_name(t))
                    and WikiListItem.is_valid_template_name(t_clean)
                ]
                if raw_tags:
                    return raw_tags, remaining.strip()

        # Pattern für Text mit Doppelpunkt
        # Teile den Text am ersten Doppelpunkt, der nicht in Klammern steht
        parts = []
        paren_level = 0

        for i, char in enumerate(text):
            if char == "(":
                paren_level += 1
            elif char == ")":
                paren_level -= 1
            elif char == ":" and paren_level == 0:
                parts = [text[:i], text[i + 1 :]]
                break

        if len(parts) == 2:
            before_colon, after_colon = parts[0].strip(), parts[1].strip()

            # Extrahiere Tags und handle verschachtelte Klammern
            raw_tags = []
            # Pattern für Tags mit optionalen Klammern: word1 (sub1, sub2), word2
            for tag_group in TAG_GROUP_PATTERN.finditer(before_colon):
                tag = tag_group.group(1).strip()
                if not tag:
                    continue

                # Prüfe auf Klammern-Tags
                paren_match = TAG_PAREN_PATTERN.match(tag)
                if paren_match:
                    main_tag, paren_content = paren_match.groups()
                    if main_tag.strip():
                        raw_tags.append(main_tag.strip())
                    raw_tags.extend(t.strip() for t in paren_content.split(","))
                else:
                    raw_tags.append(tag)

            raw_tags = [
                t_clean
                for t in raw_tags
                if (t_clean := WikiListItem.sanitize_template_name(t))
                and WikiListItem.is_valid_template_name(t_clean)
            ]

            if raw_tags:
                return raw_tags, after_colon

        return None, text

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
            lines.append("\nBedeutungen für den nächsten Eintrag:")
        for meaning_dict in meanings_list:
            lines.append(format_meaning_dict(meaning_dict))

    return "\n".join(lines)

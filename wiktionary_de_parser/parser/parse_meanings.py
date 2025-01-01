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
    # not K-Template
    "kStg.": "keine Steigerung",
    "amer.": "US-amerikanisch",
    "mD": "mit Dativ",
}
# Referenz: https://de.wiktionary.org/wiki/Vorlage:K
K_TEMPLATE_WHITESPACE_TRIGGERS = {
    "allg.",
    "allgemein",
    "ansonsten",
    "auch",
    "bei",
    "bes.",
    "besonders",
    "bis",
    "bisweilen",
    "das",
    "der",
    "die",
    "eher",
    "früher",
    "häufig",
    "hauptsächlich",
    "im",
    "in",
    "in Bezug auf",
    "insbes.",
    "leicht",
    "meist",
    "meistens",
    "mit",
    "mitunter",
    "noch",
    "noch in",
    "nur",
    "nur noch",
    "oft",
    "oftmals",
    "ohne",
    "sehr",
    "seltener",
    "seltener auch",
    "sonst",
    "später",
    "speziell",
    "teils",
    "teilweise",
    "über",
    "überwiegend",
    "ursprünglich",
    "von",
    "vor allem",
    "vor allem in",
    "z. B.",
    "z. T.",
    "zum Beispiel",
    "zum Teil",
    "zumeist",
}
IGNORED_TEMPLATES = {"WP", "Internetquelle", "NNBSP", "MZ", "DOI"}
LEADING_DASH_PATTERN = re.compile(r"^— ")
NUMBERED_LIST_PATTERN = re.compile(r"^\[(?:\d+(?:\.\d+)*[a-z]?|[a-z])\] ")
PAREN_MATCH_PATTERN = re.compile(r"^\s*\(([^)]+)\)\s*(.+)")
TAG_GROUP_PATTERN = re.compile(r"([^,()]+(?:\([^)]+\))?)")
HTML_TAG_PATTERN = re.compile(r"<[^>]+>.*?</[^>]+>|<[^>]+/>")
TAG_PAREN_PATTERN = re.compile(r"^(.+?)\s*\(([^)]+)\)$")

# Liste der Konjunktionen die im Modul:Kontext definiert sind
CONJUNCTIONS = {
    "beziehungsweise",
    "bzw.",
    "oder",
    "respektive",
    "sowie",
    "und",
}


class TemplateParser:
    def __init__(self, template: wtp.Template):
        self.template = template

    def parse_k_template(self) -> list[str] | None:
        arguments = self.template.arguments

        # Collect the positional parameters (1-7)
        positional_args: list[str] = []
        for i in range(1, 8):
            arg = next((a for a in arguments if a.name == str(i)), None)
            if arg and arg.value.strip():
                value = arg.value.strip()
                positional_args.append(TEMPLATE_NAME_MAPPING.get(value, value))

        if not positional_args:
            return None

        tags = []
        current_tag = ""

        # Iterate over the positional arguments, check for separators and
        # create tags
        for i, arg in enumerate(positional_args, 1):
            # Check for seperator value
            current_separator = next(
                (a.value for a in arguments if a.name == f"t{i}"), None
            )

            # If the separator is not defined, check if arg is in
            # K_TEMPLATE_WHITESPACE_TRIGGERS
            if not current_separator:
                if arg in K_TEMPLATE_WHITESPACE_TRIGGERS or arg in CONJUNCTIONS:
                    current_separator = "_"
                else:
                    current_separator = ","

            # If the separator is "," or ";", start a new tag
            if current_separator in (",", ";"):
                current_tag += arg
                tags.append(current_tag)
                current_tag = ""
            # If the separator is "_" add a whitespace
            elif current_separator == "_":
                current_tag += f"{arg} "
            # If the separator is ":" add a colon
            elif current_separator == ":":
                current_tag += f"{arg}: "

        # Add the last tag
        if current_tag:
            tags.append(current_tag.strip())

        return tags

    def parse_ut_template(self) -> str | None:
        return self.template.arguments[1].value

    def parse_ch_template(self) -> str | None:
        return "Schweiz und Liechtenstein"


class WikiListItem:
    __slots__ = ["tags", "raw_tags", "text", "sublist", "pattern"]

    def __init__(
        self, wikitext: str, pattern: str, sublist: "WikiList | None"
    ) -> None:
        wikitext = WikiListItem.strip_html_tags(wikitext)
        parsed_wikitext = wtp.parse(wikitext)

        self.pattern = pattern
        self.text = self.parse_text(parsed_wikitext)
        self.tags = self.get_template_tags(parsed_wikitext)
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
            # Allow only certain characters
            and re.match(r"^[a-zA-ZäöüÄÖÜß0-9\- \.]+$", template_name)
            is not None
        )

    @staticmethod
    def parse_text(parsed_wikitext: wtp.WikiText) -> str:
        def replace_templates(template):
            name = template.name

            if name == "K":
                return ""

            if name == "Üt":
                return TemplateParser(template).parse_ut_template()

            if name == "CH&LI":
                return TemplateParser(template).parse_ch_template()

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
    def strip_html_tags(text: str) -> str:
        """
        Strip html tags AND their content from the text.
        Example: 'text <ref>reference content</ref> more text' -> 'text more text'
        """
        return HTML_TAG_PATTERN.sub("", text)

    @staticmethod
    def sanitize_template_name(text: str) -> str:
        """
        Sanitize the tag by removing unwanted characters.
        """

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
    def get_template_tags(
        parsed_wikitext: wtp.WikiText,
    ) -> list[str]:
        """
        Reference: https://de.wiktionary.org/wiki/Vorlage:K


        TODO: fußnote?? https://de.wiktionary.org/wiki/Bifurkation

        """
        templates = parsed_wikitext.templates

        if not templates:
            return []

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
            elif template_name == "CH&LI":
                new_tag = parser.parse_ch_template()
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

    def parse_raw_tags(self, text: str) -> tuple[list[str], str]:
        """
        Parses tags from text in the following formats:
        1. Leading parenthetical content: "(tag1, tag2) text"
        2. Colon-separated tags: "tag1, tag2: text"
        3. Tags with nested parentheses: "tag1 (subtag1, subtag2): text"

        Returns (tags, remaining_text) or ([], original_text) if no tags found.
        """
        raw_tags = []
        remaining_text = text

        if text:
            # Pattern für Text der mit Klammern beginnt: (content) rest
            paren_match = PAREN_MATCH_PATTERN.match(text)
            if paren_match:
                # Inhalt in Klammern und der Rest des Textes
                content, after_paren = paren_match.groups()
                # Nur verarbeiten wenn der Inhalt der Klammer ein einzelnes
                # Wort oder Komma-Liste ist
                if ", " in content or " " not in content:
                    candidate_tags = [
                        t.strip() for t in content.split(",") if t.strip()
                    ]
                    valid_tags = [
                        t_clean
                        for t in candidate_tags
                        if (t_clean := WikiListItem.sanitize_template_name(t))
                        and WikiListItem.is_valid_template_name(t_clean)
                    ]
                    if valid_tags:
                        raw_tags = valid_tags
                        remaining_text = after_paren.strip()

            # Wenn keine Klammer-Tags gefunden wurden, suche nach Doppelpunkt-Tags
            if not raw_tags:
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

                if len(parts) == 2 and len(parts[0]) <= 50:
                    before_colon, after_colon = (
                        parts[0].strip(),
                        parts[1].strip(),
                    )
                    candidate_tags = []

                    # Pattern für Tags mit optionalen Klammern
                    for tag_group in TAG_GROUP_PATTERN.finditer(before_colon):
                        tag = tag_group.group(1).strip()
                        if tag:
                            # Prüfe auf Klammern-Tags
                            paren_match = TAG_PAREN_PATTERN.match(tag)
                            if paren_match:
                                main_tag, paren_content = paren_match.groups()
                                if main_tag.strip():
                                    candidate_tags.append(main_tag.strip())
                                candidate_tags.extend(
                                    t.strip() for t in paren_content.split(",")
                                )
                            else:
                                candidate_tags.append(tag)

                    valid_tags = [
                        t_clean
                        for t in candidate_tags
                        if (t_clean := WikiListItem.sanitize_template_name(t))
                        and WikiListItem.is_valid_template_name(t_clean)
                    ]

                    if valid_tags:
                        raw_tags = valid_tags
                        remaining_text = after_colon

        # Remove raw tags that is already saved in self.tags
        raw_tags = [tag for tag in raw_tags if tag not in self.tags]

        return raw_tags, remaining_text

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

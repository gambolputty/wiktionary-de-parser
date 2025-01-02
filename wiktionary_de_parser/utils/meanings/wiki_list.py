import re
from dataclasses import dataclass

import wikitextparser as wtp

from wiktionary_de_parser.models import MeaningDict
from wiktionary_de_parser.utils.meanings.tags import TEMPLATE_NAME_MAPPING
from wiktionary_de_parser.utils.meanings.template_parser import TemplateParser

IGNORED_TEMPLATES = {"WP", "Internetquelle", "NNBSP", "MZ", "DOI"}
LEADING_DASH_PATTERN = re.compile(r"^— ")
NUMBERED_LIST_PATTERN = re.compile(r"^\[(?:\d+(?:\.\d+)*[a-z]?|[a-z])\] ")
PAREN_MATCH_PATTERN = re.compile(r"^\s*\(([^)]{2,50})\)\s*(.+)")
TAG_GROUP_PATTERN = re.compile(r"([^,()]+(?:\([^)]+\))?)")
HTML_TAG_PATTERN = re.compile(r"<[^>]+>.*?</[^>]+>|<[^>]+/>")
TAG_PAREN_PATTERN = re.compile(r"^(.+?)\s*\(([^)]+)\)$")


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

            name = TEMPLATE_NAME_MAPPING.get(template.name, template.name)

            # if template has a single argument that is a comma, colon or ; append it to the name
            if len(template.arguments) == 1:
                arg = template.arguments[0].value.strip()
                if arg in {",", ":", ";"}:
                    name += arg

            return name

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

        1. Leading parentheses:
           "(tag1, tag2) remaining text"
           Example: "(colloq., joc.) to tease someone"

        2. Tags with colon:
           "tag1, tag2: remaining text"
           Example: "Medicine, Surgery: surgical removal"

        3. Tags with nested parentheses:
           "tag1 (subtag1, subtag2): remaining text"
           Example: "Medicine (Anatomy, Surgery): tissue structure"

        The method only recognizes tags that:
        - Are maximum 50 characters long
        - Only contain letters, numbers, hyphens, spaces and periods
        - Don't start with certain prefixes (QS, Ref-, etc.)
        - Are not in the IGNORED_TEMPLATES list

        Args:
            text: The text to parse

        Returns:
            tuple containing:
            - List of found tags (cleaned and validated)
            - Remaining text without tags
        """
        raw_tags = []
        remaining_text = text

        if text:
            # Pattern for text starting with parentheses: (content) rest
            paren_match = PAREN_MATCH_PATTERN.match(text)
            if paren_match:
                # Extract content inside parentheses and remaining text
                paren_content, after_paren = paren_match.groups()
                # Only process if content is a single word or comma-separated list
                if ", " in paren_content or " " not in paren_content:
                    candidate_tags = [
                        t.strip() for t in paren_content.split(",") if t.strip()
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

            # If no parentheses tags found, look for colon-separated tags
            if not raw_tags:
                # Split text at first colon that is not inside parentheses
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

                    # Pattern for tags with optional parentheses
                    for tag_group in TAG_GROUP_PATTERN.finditer(before_colon):
                        tag = tag_group.group(1).strip()
                        if tag:
                            # Check for tags with nested parentheses
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

        # Remove duplicates that are already present in self.tags
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

"""Hierarchical sense extraction from a Bedeutungen list.

Builds a tree of ``Meaning`` dataclasses (see ``models``) from the
``wikitextparser`` list structure.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import wikitextparser as wtp

from wiktionary_de_parser.models import Meaning
from wiktionary_de_parser.utils.meanings.tags import TEMPLATE_NAME_MAPPING
from wiktionary_de_parser.utils.meanings.template_parser import TemplateParser

IGNORED_TEMPLATES = {"WP", "Internetquelle", "NNBSP", "MZ", "DOI"}
LEADING_DASH_PATTERN = re.compile(r"^— ")
NUMBERED_LIST_PATTERN = re.compile(r"^\[(?:\d+(?:\.\d+)*[a-z]?|[a-z])\] ")
PAREN_MATCH_PATTERN = re.compile(r"^\s*\(([^)]{2,50})\)\s*(.+)")
TAG_GROUP_PATTERN = re.compile(r"([^,()]+(?:\([^)]+\))?)")
# Multi-line tag bodies are real (e.g. ``<ref>line1\nline2</ref>`` on
# ``omnis cellula e cellula``, ``Landschaftsschutz``, several Cuneiform
# entries). The backreference ``\1`` requires the closing tag to match
# the opening one, so an unclosed ``<ref>`` cannot over-match to the
# next unrelated ``</…>`` and swallow content in between.
HTML_TAG_PATTERN = re.compile(r"<(\w+)[^>]*>.*?</\1>|<[^>]+/>", re.DOTALL)
VALID_TEMPLATE_NAME_PATTERN = re.compile(r"^[a-zA-ZäöüÄÖÜß0-9\- \.]+$")
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
        blocked_prefixes = ("QS", "Ref-", "Lit-", "Wiki")
        return (
            len(template_name) < 50
            and len(template_name) > 1
            # Disallow lowercase templates with 2 or fewer characters
            and not (template_name.islower() and len(template_name) <= 2)
            and template_name not in IGNORED_TEMPLATES
            and not template_name.startswith(blocked_prefixes)
            # Allow only certain characters
            and VALID_TEMPLATE_NAME_PATTERN.match(template_name) is not None
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
            # If template has a single argument that is a comma, colon
            # or ; append it to the name.
            if len(template.arguments) == 1:
                arg = template.arguments[0].value.strip()
                if arg in {",", ":", ";"}:
                    name += arg
            return name

        text = parsed_wikitext.plain_text(replace_templates=replace_templates)
        text = LEADING_DASH_PATTERN.sub("", text)
        text = NUMBERED_LIST_PATTERN.sub("", text)
        return text.strip()

    @staticmethod
    def strip_html_tags(text: str) -> str:
        """Strip HTML tags AND their content from the text."""
        return HTML_TAG_PATTERN.sub("", text)

    @staticmethod
    def sanitize_template_name(text: str) -> str:
        """Sanitize a tag/template name."""
        text = text.replace("&nbsp", " ")
        text = wtp.remove_markup(text)
        # If the text starts with "(" and ends with ")", remove them.
        if text.startswith("(") and text.endswith(")"):
            text = text[1:-1]
        text = text.strip()
        return TEMPLATE_NAME_MAPPING.get(text, text)

    @staticmethod
    def get_template_tags(parsed_wikitext: wtp.WikiText) -> list[str]:
        """Reference: https://de.wiktionary.org/wiki/Vorlage:K"""
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

        return [
            cleaned
            for tag in found_tags
            if (cleaned := WikiListItem.sanitize_template_name(tag))
        ]

    def parse_raw_tags(self, text: str) -> tuple[list[str], str]:
        """Pull leading parenthetical / colon-tagged labels off the text.

        Supports three patterns:

        1. Leading parentheses: ``(tag1, tag2) remaining text``
        2. Tags with colon: ``tag1, tag2: remaining text``
        3. Nested parens: ``tag1 (subtag1, subtag2): remaining text``

        Only recognises tags that are ≤50 chars, contain only
        ``[a-zA-Z0-9 .-]``, don't start with a blocked prefix, and
        aren't in IGNORED_TEMPLATES.
        """
        raw_tags: list[str] = []
        remaining_text = text

        if text:
            paren_match = PAREN_MATCH_PATTERN.match(text)
            if paren_match:
                paren_content, after_paren = paren_match.groups()
                if ", " in paren_content or " " not in paren_content:
                    candidate_tags = [
                        t.strip() for t in paren_content.split(",") if t.strip()
                    ]
                    valid_tags = [
                        c
                        for t in candidate_tags
                        if (c := WikiListItem.sanitize_template_name(t))
                        and WikiListItem.is_valid_template_name(c)
                    ]
                    if valid_tags:
                        raw_tags = valid_tags
                        remaining_text = after_paren.strip()

            if not raw_tags:
                # Split text at first colon that is not inside parens.
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
                    before_colon = parts[0].strip()
                    after_colon = parts[1].strip()
                    candidate_tags: list[str] = []
                    for tag_group in TAG_GROUP_PATTERN.finditer(before_colon):
                        tag = tag_group.group(1).strip()
                        if not tag:
                            continue
                        m = TAG_PAREN_PATTERN.match(tag)
                        if m:
                            main_tag, paren_content = m.groups()
                            if main_tag.strip():
                                candidate_tags.append(main_tag.strip())
                            candidate_tags.extend(
                                t.strip() for t in paren_content.split(",")
                            )
                        else:
                            candidate_tags.append(tag)
                    valid_tags = [
                        c
                        for t in candidate_tags
                        if (c := WikiListItem.sanitize_template_name(t))
                        and WikiListItem.is_valid_template_name(c)
                    ]
                    if valid_tags:
                        raw_tags = valid_tags
                        remaining_text = after_colon

        # Drop raw_tags duplicates already present in self.tags.
        raw_tags = [tag for tag in raw_tags if tag not in self.tags]
        return raw_tags, remaining_text

    def export(self) -> Meaning:
        return Meaning(
            text=self.text or "",
            tags=list(self.tags),
            raw_tags=list(self.raw_tags),
            sublist=self.sublist.export() if self.sublist else None,
        )


@dataclass(slots=True)
class WikiList:
    items: list[WikiListItem]

    def export(self) -> list[Meaning]:
        return [item.export() for item in self.items]

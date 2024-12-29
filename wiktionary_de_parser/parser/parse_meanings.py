import re
from dataclasses import dataclass

import wikitextparser as wtp

from wiktionary_de_parser.models import ParseMeaningsResults
from wiktionary_de_parser.parser import Parser

SKIP_TAGS = {"ref", "br", "hr", "nowiki", "syntaxhighlight"}
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

"""
TODO:
    Vorlage "Üt" (Übersetzung) -> https://de.wiktionary.org/wiki/Vorlage:%C3%9Ct
    Beispiel: https://de.wiktionary.org/wiki/%CF%87
"""


# def parse_tag(tag: Tag):
#     if str(tag.tag).lower() in SKIP_TAGS:
#         return None

#     if tag.tag == "sup" or tag.tag == "sub" or tag.tag == "math":
#         return str(tag)

#     return tag.contents.strip_code()


# def parse_k_template(template: Template):
#     """
#     Reference: https://de.wiktionary.org/wiki/Vorlage:K

#     """
#     params = [param.value.strip_code() for param in template.params]

#     return params


# def parse_ü_template(template: Template):
#     """
#     Reference: https://de.wiktionary.org/wiki/Vorlage:%C3%9C

#     """
#     if len(template.params) == 3:
#         return template.params[2].strip_code()

#     return template.params[1].strip_code()


# def parse_template(template: Template):
#     template_name = template.name.strip_code()

#     if template_name == "K":
#         return parse_k_template(template)
#     elif template_name == "Ü":
#         return parse_ü_template(template)
#     elif template_name == "QS Bedeutungen":
#         # Template indicating that the meaning is missing references
#         return None
#     else:
#         # Check if the template is a mapping
#         if template_name in TEMPLATE_NAME_MAPPING:
#             return TEMPLATE_NAME_MAPPING[template_name]

#     return None


# def parse_list_item(nodes: list[Node]):
#     """
#     Possible types of nodes:
#         mwparserfromhell.nodes.tag.Tag
#         mwparserfromhell.nodes.template.Template
#         mwparserfromhell.nodes.text.Text
#         mwparserfromhell.nodes.wikilink.Wikilink

#     Possible templates:
#         K
#     """
#     result = []

#     for node in nodes:
#         if isinstance(node, Tag):
#             parsed_tag = parse_tag(node)
#             if parsed_tag:
#                 result.append(parsed_tag)

#         elif isinstance(node, Template):
#             parsed_template = parse_template(node)
#             if parsed_template:
#                 result.append(parsed_template)

#         elif isinstance(node, Text):
#             result.append(node.value)
#         elif isinstance(node, Wikilink):
#             result.append(node.title)
#         else:
#             raise NotImplementedError(
#                 f"Node type {type(node)} is not implemented"
#             )

#     return result


class WikiListItem:
    tags: list[str] | None
    text: str | None
    sublist: "WikiList"
    pattern: str

    # ol_pattern = "[:;]"
    # ul_pattern = "\\*"

    def __init__(
        self, wikitext: str, pattern: str, sublist: "WikiList | None"
    ) -> None:
        self.pattern = pattern

        if isinstance(wikitext, str):
            self.text = self.parse_text(wikitext)
            self.tags = self.parse_templates(wikitext)

        if isinstance(sublist, WikiList):
            self.sublist = sublist

    @staticmethod
    def parse_text(wikitext: str):
        text = wtp.parse(wtp.remove_markup(wikitext)).plain_text()

        # Remove leading marker symbols
        # "— "
        text = text.lstrip("— ")

        # Followed by a space: [1], [2], [3], [5a], [5b] ...
        text = re.sub(r"^\[\d+[a-z]?\] ", "", text)

        return text

    @staticmethod
    def parse_templates(wikitext: str) -> list[str] | None:
        """
        Reference: https://de.wiktionary.org/wiki/Vorlage:K

        """
        templates = wtp.parse(wikitext).templates

        # parse k-templates
        k_templates = [
            tmplt.arguments for tmplt in templates if tmplt.name == "K"
        ]

        # make k_templates a flat list of values
        k_template_values = [
            item.value for sublist in k_templates for item in sublist
        ]

        # parse other templates
        other_templates = [tmplt.name for tmplt in templates]

        return k_template_values + other_templates

    def to_string(self, indent: int = 0) -> str:
        """Convert the list item and its sublist to a string representation."""
        indent_str = "  " * indent
        text_parts = []

        if self.tags:
            tags_str = f"[{', '.join(self.tags)}]"
            text_parts.append(tags_str)

        if self.text:
            text_parts.append(self.text)

        text = " ".join(text_parts)
        result = [f"{indent_str}• {text}"]

        if hasattr(self, "sublist") and self.sublist:
            result.append(self.sublist.to_string(indent + 1))

        return "\n".join(result)


@dataclass(slots=True)
class WikiList:
    items: list[WikiListItem]

    def to_string(self, indent: int = 0) -> str:
        """Convert the entire list to a string representation."""
        return "\n".join(item.to_string(indent) for item in self.items)


class ParseMeanings(Parser):
    name = "meanings"

    @classmethod
    def parse_wiki_list(cls, wiki_lists: list[wtp.WikiList]):
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
                    raw_list_item, wiki_list.pattern, sublist_parsed
                )

                # Check cases where fields are missing
                # if not new_item.text and not new_item.tags:
                #     continue

                # Check if last list item has pattern '\\*' and current new_item has not that pattern. If so, add new_item to
                # the sublist of the last list item
                if (
                    list_items
                    and list_items[-1].pattern == "\\*"
                    and new_item.pattern != "\\*"
                ):
                    if not hasattr(list_items[-1], "sublist"):
                        list_items[-1].sublist = WikiList(items=[])
                    list_items[-1].sublist.items.append(new_item)
                else:
                    list_items.append(new_item)

        return WikiList(items=list_items)

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
                result = meanings

        return result

    def run(self) -> ParseMeaningsResults:
        paragraph = self.find_paragraph("Bedeutungen", self.entry.wikitext)
        result = None

        if paragraph:
            result = self.parse(paragraph)

        return result

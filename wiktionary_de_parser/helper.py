import re

from mwparserfromhell.nodes.tag import Tag
from mwparserfromhell.nodes.template import Template
from mwparserfromhell.nodes.text import Text
from mwparserfromhell.nodes.wikilink import Wikilink
from mwparserfromhell.wikicode import Wikicode


def strip_html_tags(text: str):
    return re.sub(r"<[^>]+>", " ", text)


def find_paragraph(heading: str, wikitext: str):
    pattern = re.compile(r"{{" + heading + r"}}\n((?:[^\n][\n]?)+)")
    match = re.search(pattern, wikitext)

    return match.group(1) if match is not None else None


def extract_paragraph(
    wikicode: Wikicode, wanted_template_name: str, ignored_tags: set[str] = set()
) -> Wikicode:
    """
    Takes a template name and returns the paragraph that follows it.
    """
    found_nodes = Wikicode([])
    found_wanted_template = False

    for node in wikicode.filter(recursive=False):
        if isinstance(node, Template) and node.name == wanted_template_name:
            found_wanted_template = True
            continue

        if not found_wanted_template:
            continue

        # skip tags
        if isinstance(node, Tag) and str(node.tag) in ignored_tags:
            continue

        found_nodes.append(node)

        if isinstance(node, Text) and "\n\n" in node.value:
            break

    return found_nodes


def get_lines(wikicode: Wikicode, keep_italics: bool = True) -> list[str]:
    """
    Loop over all nodes.
    If a node is a text node, add it to the current line.
    If a node is a line break, add the current line to the list of
    lines and start a new line.
    If a node is an italic tag, recursivly loop it's text node children in
    node.contents and wrap them in italics (<i>text</i>).
    """
    lines = []
    current_line = []

    for node in wikicode.filter(recursive=False):
        if isinstance(node, Text):
            current_line.append(node.value)

            if "\n" in node.value:
                # break line on newlines
                line = "".join(current_line).strip()

                # skip empty lines
                if line:
                    lines.append(line)

                current_line = []

        elif isinstance(node, Wikilink):
            current_line.extend([t.value for t in node.title.filter_text()])
        elif isinstance(node, Template):
            # Keep template names
            list_of_text = []

            if str(node.name) == "ugs.":
                list_of_text.append("ugs.")

                if node.params[0] and str(node.params[0]) == ":":
                    list_of_text.append(":")

            elif str(node.name) == "K":
                list_of_text.append("<i>")
                list_of_text.append(", ".join([str(n.value) for n in node.params]))
                list_of_text.append(":</i>")

            current_line.extend(list_of_text)

        elif isinstance(node, Tag):
            if not node.contents:
                # Ignore empty tags
                continue

            text_nodes = [node.value for node in node.contents.filter_text()]
            wrap_in_italics = keep_italics and node.tag == "i"

            if wrap_in_italics:
                text_nodes = ["<i>"] + text_nodes + ["</i>"]

            current_line.extend(text_nodes)

    if current_line:
        lines.append("".join(current_line))

    return lines

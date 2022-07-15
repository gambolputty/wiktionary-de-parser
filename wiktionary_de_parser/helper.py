import re


def strip_html_tags(text: str):
    return re.sub(r"<[^>]+>", " ", text)


def find_paragraph(heading: str, wikitext: str):
    pattern = re.compile(r"{{" + heading + r"}}\n((?:[^\n][\n]?)+)")
    match = re.search(pattern, wikitext)

    return match.group(1) if match is not None else None

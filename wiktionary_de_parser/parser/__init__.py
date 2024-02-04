import re
from dataclasses import dataclass, field

from wiktionary_de_parser.models import WiktionaryPageEntry


@dataclass(slots=True)
class Parser:
    entry: WiktionaryPageEntry
    name: str = field(init=False)

    def __post_init__(self):
        # Get the class name
        self.name = self.get_class_name()

    def get_class_name(self):
        name = self.__class__.__name__

        # Remove "Parse" from the class name
        if name.startswith("Parse"):
            name = name[5:]

        # Make the all letters lowercase
        name = name.lower()

        return name

    def run(self):
        # Raise to be implemented error
        raise NotImplementedError

    @staticmethod
    def find_paragraph(heading: str, wikitext: str) -> str | None:
        pattern = re.compile(r"{{" + heading + r"}}\n((?:[^\n][\n]?)+)")
        match = re.search(pattern, wikitext)

        return match.group(1) if match is not None else None

    @staticmethod
    def strip_html_tags(text: str):
        return re.sub(r"<[^>]+>", " ", text)

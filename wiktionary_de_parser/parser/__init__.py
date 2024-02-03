import re
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

from wiktionary_de_parser import WiktionaryPageEntry


class ParserResult(BaseModel):
    name: str
    value: Any


@dataclass(slots=True)
class Parser:
    entry: WiktionaryPageEntry

    @classmethod
    def __subclasshook__(cls, C):
        return NotImplemented

    def run(self) -> ParserResult:
        # Raise to be implemented error
        raise NotImplementedError

    def find_paragraph(self, heading: str, wikitext: str | None = None):
        wikitext = wikitext or self.entry.wikitext
        pattern = re.compile(r"{{" + heading + r"}}\n((?:[^\n][\n]?)+)")
        match = re.search(pattern, wikitext)

        return match.group(1) if match is not None else None

    @staticmethod
    def strip_html_tags(text: str):
        return re.sub(r"<[^>]+>", " ", text)

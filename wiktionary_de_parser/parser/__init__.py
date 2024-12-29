import re
from dataclasses import dataclass, field

from wiktionary_de_parser.models import WiktionaryPageEntry


@dataclass(slots=True)
class Parser:
    entry: WiktionaryPageEntry
    name: str = field(init=False)

    def run(self):
        # Raise to be implemented error
        raise NotImplementedError

    @staticmethod
    def find_paragraph(heading: str, wikitext: str) -> str | None:
        pattern = re.compile(
            r"{{" + re.escape(heading) + r"}}\n(.*?)(?=\n{{|\Z)", re.DOTALL
        )

        match = re.search(pattern, wikitext)

        return match.group(1) if match is not None else None

    @staticmethod
    def strip_html_tags(text: str):
        return re.sub(r"<[^>]+>", " ", text)

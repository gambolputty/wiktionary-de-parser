from dataclasses import dataclass

from mwparserfromhell.wikicode import Wikicode

from wiktionary_de_parser.helper import extract_paragraph, get_lines


@dataclass
class MeaningsType:
    meanings: list[str] | None


def init(title: str, wikicode: Wikicode) -> MeaningsType:
    paragraph = extract_paragraph(
        wikicode,
        wanted_template_name="Bedeutungen",
        ignored_tags={"sup", "ref"},
    )
    lines = get_lines(paragraph)

    return MeaningsType(meanings=lines if lines else None)

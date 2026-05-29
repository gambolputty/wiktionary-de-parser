"""Shared test helpers."""

from wiktionary_de_parser.entry import WiktionaryEntry
from wiktionary_de_parser.models import WiktionaryPage


def make_entry(
    wikitext: str, name: str = "Test", index: int = 0
) -> WiktionaryEntry:
    """Build a WiktionaryEntry from raw wikitext for parser tests."""
    page = WiktionaryPage(page_id=1, name=name, wikitext=wikitext)
    return WiktionaryEntry(page=page, index=index, wikitext=wikitext)


def case_id(text: str, maxlen: int = 50) -> str:
    """Short, readable pytest id from a wikitext snippet so a failing
    parametrized case names the input instead of dumping the whole blob
    (with mangled newlines) as the node id."""
    collapsed = " ".join(text.split())
    return collapsed[:maxlen] if collapsed else "empty"

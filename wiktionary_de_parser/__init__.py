"""Public API for the German Wiktionary parser.

Typical usage::

    from wiktionary_de_parser import WiktionaryParser, WiktionaryDump

    dump = WiktionaryDump(dump_file_path="…/dewiktionary-latest.xml.bz2")
    parser = WiktionaryParser()
    for page in dump.pages():
        if page.redirect_to or not page.wikitext:
            continue
        for entry in parser.entries(page):
            parsed = parser.parse(entry)
            ...

For parallel processing, use ``WiktionaryDump.iter_parsed(workers=N)``.
"""

from wiktionary_de_parser.dump import WiktionaryDump
from wiktionary_de_parser.entry import WiktionaryEntry
from wiktionary_de_parser.models import (
    LemmaReference,
    Meaning,
    ParsedEntry,
    PosTag,
    ReferenceType,
    WiktionaryPage,
)
from wiktionary_de_parser.parser import WiktionaryParser

__all__ = [
    "LemmaReference",
    "Meaning",
    "ParsedEntry",
    "PosTag",
    "ReferenceType",
    "WiktionaryDump",
    "WiktionaryEntry",
    "WiktionaryPage",
    "WiktionaryParser",
]

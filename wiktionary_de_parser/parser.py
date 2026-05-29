"""Top-level parser that drives every feature parser per entry."""

from __future__ import annotations

import re
from typing import Iterator

from wiktionary_de_parser._wikitext import WORTART_TEMPLATE_NAME_RE
from wiktionary_de_parser.entry import WiktionaryEntry
from wiktionary_de_parser.models import ParsedEntry, WiktionaryPage
from wiktionary_de_parser.parsers import (
    parse_hyphenation,
    parse_inflection,
    parse_ipa,
    parse_language,
    parse_lemma,
    parse_meanings,
    parse_pos,
    parse_rhymes,
)

# Wortart-headers usually look like ``=== {{Wortart|<POS>|<Lang>}} ===``.
# Two real-world deviations the regex needs to tolerate:
#  - Double space: ``===  {{Wortart|Substantiv|Französisch}}  ===``
#    (seen e.g. on ``bimbo``, ``Portus Cale``, ``ad circ.``, several
#    Latin phrases).
#  - Lemma prefix before the template: ``=== ombrello
#    {{Wortart|Substantiv|Italienisch}} ===`` (Italian-style entries
#    like ``ombrello``, ``civetta``, ``meringa``, ``stupefatto``, …).
# ``[^\n]*?`` non-greedily eats any header text between ``=== `` and
# ``{{Wortart``.
_ENTRY_HEADER_RE = re.compile(
    r"^=== [^\n]*?" + WORTART_TEMPLATE_NAME_RE + r"\|",
    re.MULTILINE,
)

# Any H2 (``==``) or H3 (``===``) header at the start of a line ends an
# entry. H4+ (``==== `` and deeper, e.g. ``Übersetzungen``) is NOT a
# boundary — it's a subsection inside the current entry. ``={2,3} ``
# matches exactly two or three ``=`` followed by a space, so ``==== ``
# never matches (greedy 3-= run leaves no space afterwards, 2-= backtrack
# also fails).
_SECTION_HEADER_RE = re.compile(r"^={2,3} ", re.MULTILINE)


def _split_entries(wikitext: str) -> list[str]:
    """Split a page's wikitext into per-entry slices.

    Linear-scan replacement for the previous quadratic regex
    ``(?:[\\w\\W](?!^===? ))+``. Collects entry-header positions and
    section-boundary positions in two passes, then cuts each entry at
    the next section boundary strictly after its start.
    """
    starts = [m.start() for m in _ENTRY_HEADER_RE.finditer(wikitext)]
    if not starts:
        return []

    headers = [m.start() for m in _SECTION_HEADER_RE.finditer(wikitext)]
    headers.append(len(wikitext))

    entries: list[str] = []
    h_index = 0
    for start in starts:
        # Advance h_index to the first header strictly after ``start``.
        while h_index < len(headers) and headers[h_index] <= start:
            h_index += 1
        end = headers[h_index] if h_index < len(headers) else len(wikitext)
        entries.append(wikitext[start:end])
    return entries


class WiktionaryParser:
    """Splits pages into entries and parses each entry into a
    ``ParsedEntry``.

    Stateless: instances hold no per-page state, so they're cheap.
    Kept as a class for the convenience of a grouped public API.
    """

    def entries(self, page: WiktionaryPage) -> Iterator[WiktionaryEntry]:
        """Yield one ``WiktionaryEntry`` per Wortart header on the page.

        Pages can carry multiple entries (one per language and POS) —
        e.g. https://de.wiktionary.org/wiki/instrument.
        """
        if not page.wikitext:
            return
        for index, slice_ in enumerate(_split_entries(page.wikitext)):
            yield WiktionaryEntry(page=page, index=index, wikitext=slice_)

    def parse(self, entry: WiktionaryEntry) -> ParsedEntry:
        """Run every feature parser on the entry."""
        language, language_code = parse_language(entry)
        reference = parse_lemma(entry)
        lemma = reference.target if reference else entry.page_name
        return ParsedEntry(
            page_name=entry.page_name,
            page_id=entry.page.page_id,
            entry_index=entry.index,
            language=language,
            language_code=language_code,
            lemma=lemma,
            reference=reference,
            pos=parse_pos(entry),
            inflection=parse_inflection(entry),
            ipa=parse_ipa(entry),
            hyphenation=parse_hyphenation(entry),
            rhymes=parse_rhymes(entry),
            meanings=parse_meanings(entry),
        )

"""Per-entry context with cached lookups.

Each ``WiktionaryEntry`` carries the raw wikitext plus lazily computed
section map, header line, and pronunciation Wikicode. Parsers read from
these cached views instead of running their own section search or
``mwparserfromhell.parse`` on the full text.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import cached_property

import mwparserfromhell
from mwparserfromhell.wikicode import Wikicode

from wiktionary_de_parser._wikitext import (
    WORTART_TEMPLATE_NAME_RE,
    find_sections,
)
from wiktionary_de_parser.models import WiktionaryPage

_HEADER_LINE_RE = re.compile(
    r"=== [^\n]*?" + WORTART_TEMPLATE_NAME_RE + r"\|[^\n]+",
)


@dataclass
class WiktionaryEntry:
    """One Wortart entry within a Wiktionary page.

    Holds the raw wikitext plus cached lookups (sections, header line)
    so each parser stays cheap. Not ``slots=True`` because
    ``cached_property`` writes into ``__dict__``.
    """

    page: WiktionaryPage
    index: int
    wikitext: str

    @property
    def page_name(self) -> str:
        return self.page.name

    @cached_property
    def sections(self) -> dict[str, str]:
        return find_sections(self.wikitext)

    @cached_property
    def header_line(self) -> str | None:
        """The ``=== … {{Wortart|<POS>|<Lang>}} …`` line of this entry."""
        m = _HEADER_LINE_RE.search(self.wikitext)
        return m.group(0) if m else None

    @cached_property
    def pronunciation_wikicode(self) -> Wikicode | None:
        """``mwparserfromhell``-parsed Aussprache body.

        Shared between the IPA and rhymes parsers — both walk the same
        node sequence. Parsing it once saves one ``mwparserfromhell.parse``
        call per entry.
        """
        body = self.sections.get("Aussprache")
        if body is None:
            return None
        return mwparserfromhell.parse(body)

    @cached_property
    def header_wikicode(self) -> Wikicode | None:
        """``mwparserfromhell``-parsed header line.

        Shared between the POS and language parsers — both pull
        positional params out of the same ``{{Wortart}}`` template.
        """
        header = self.header_line
        if header is None:
            return None
        return mwparserfromhell.parse(header)

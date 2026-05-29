"""Public data models for parsed Wiktionary entries."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


@dataclass(slots=True)
class WiktionaryPage:
    """A raw page yielded by the dump iterator. `wikitext` is None for
    redirect pages (`redirect_to` is set instead)."""

    page_id: int
    name: str
    wikitext: str | None = None
    redirect_to: str | None = None


class ReferenceType(str, Enum):
    """Form-reference templates that point one entry at another lemma.

    INFLECTED — Grundformverweis: declined or conjugated form
                e.g. ``gehörte`` → ``gehören``
    VARIANT   — Lemmaverweis / Alte Schreibweise: alternative spelling
                or pronunciation variant
                e.g. ``Geografie`` → ``Geographie``
    """

    INFLECTED = "inflected"
    VARIANT = "variant"


@dataclass(slots=True, frozen=True)
class LemmaReference:
    """Pointer from an inflected/variant entry to its canonical lemma."""

    target: str
    type: ReferenceType


@dataclass(slots=True, frozen=True)
class PosTag:
    """A part-of-speech tag with optional subtypes.

    Values stay in the original German Wiktionary vocabulary
    (``Substantiv``, ``Toponym``, …) — only the surrounding structure
    is in English.
    """

    pos: str
    subtypes: tuple[str, ...] = ()


@dataclass(slots=True)
class ParsedEntry:
    """One word entry extracted from a Wiktionary page.

    A page can contain multiple entries (one per language and POS), so
    ``page_name`` is repeated across entries and ``entry_index`` records
    the position on the page.
    """

    page_name: str
    page_id: int
    entry_index: int
    language: str | None
    language_code: str | None
    lemma: str
    reference: LemmaReference | None
    pos: list[PosTag] = field(default_factory=list)
    inflection: dict[str, str] | None = None
    ipa: list[str] | None = None
    hyphenation: list[str] | None = None
    rhymes: list[str] | None = None
    meanings: list[Meaning] | None = None


@dataclass(slots=True)
class Meaning:
    """A single sense/meaning of a word.

    ``tags`` are extracted from ``{{K}}`` templates (canonical), ``raw_tags``
    are leading parenthetical / colon-tagged labels in the body text.
    ``sublist`` carries nested meanings.
    """

    text: str = ""
    tags: list[str] = field(default_factory=list)
    raw_tags: list[str] = field(default_factory=list)
    sublist: list[Meaning] | None = None

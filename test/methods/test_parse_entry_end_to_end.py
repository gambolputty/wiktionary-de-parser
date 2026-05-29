"""End-to-end tests for ``WiktionaryParser.parse``.

The individual feature parsers are covered by their own test files.
This module pins the *combined* ``ParsedEntry`` output for a handful of
real-world page shapes so the schema and the cross-parser wiring stay
stable. If one of these breaks, something in the orchestration changed
(field rename, parser reordering, caching regression, …) — not just one
feature parser.
"""

from __future__ import annotations

import pytest

from wiktionary_de_parser import WiktionaryParser
from wiktionary_de_parser.models import (
    LemmaReference,
    PosTag,
    ReferenceType,
    WiktionaryPage,
)


@pytest.fixture
def parser() -> WiktionaryParser:
    return WiktionaryParser()


def _single_entry(parser: WiktionaryParser, name: str, wikitext: str):
    """Return the only ``ParsedEntry`` for a single-entry page."""
    page = WiktionaryPage(page_id=1, name=name, wikitext=wikitext)
    entries = list(parser.entries(page))
    assert len(entries) == 1, f"expected exactly one entry, got {len(entries)}"
    return parser.parse(entries[0])


class TestStandaloneNoun:
    """A vanilla German noun ("Abend") — exercises every feature parser
    on a single entry."""

    WIKITEXT = """== Abend ({{Sprache|Deutsch}}) ==
=== {{Wortart|Substantiv|Deutsch}}, {{m}} ===

{{Deutsch Substantiv Übersicht
|Genus=m
|Nominativ Singular=Abend
|Nominativ Plural=Abende
|Genitiv Singular=Abends
|Genitiv Plural=Abende
|Dativ Singular=Abend
|Dativ Plural=Abenden
|Akkusativ Singular=Abend
|Akkusativ Plural=Abende
}}

{{Worttrennung}}
:Abend, {{Pl.}} Aben·de

{{Aussprache}}
:{{IPA}} {{Lautschrift|ˈaːbn̩t}}
:{{Reime}} {{Reim|aːbn̩t|Deutsch}}

{{Bedeutungen}}
:[1] der Übergang vom Tag zur Nacht
"""

    def test_parsed_entry_full(self, parser):
        entry = _single_entry(parser, "Abend", self.WIKITEXT)
        assert entry.page_name == "Abend"
        assert entry.page_id == 1
        assert entry.entry_index == 0
        assert entry.language == "Deutsch"
        assert entry.language_code == "de"
        assert entry.lemma == "Abend"
        assert entry.reference is None
        assert entry.pos == [PosTag(pos="Substantiv", subtypes=())]
        assert entry.ipa == ["ˈaːbn̩t"]
        assert entry.rhymes == ["aːbn̩t"]
        assert entry.hyphenation == ["Abend"]
        assert entry.inflection is not None
        assert entry.inflection["gender"] == "m"
        assert entry.inflection["nominative_singular"] == "Abend"
        assert entry.inflection["genitive_plural"] == "Abende"
        assert entry.meanings is not None
        assert entry.meanings[0].text == "der Übergang vom Tag zur Nacht"


class TestInflectedForm:
    """A ``{{Grundformverweis}}`` entry must set ``lemma`` to the target
    and record an INFLECTED reference."""

    WIKITEXT = """== gehörte ({{Sprache|Deutsch}}) ==
=== {{Wortart|Deklinierte Form|Deutsch}} ===

{{Grundformverweis Konj|gehören}}
"""

    def test_lemma_points_to_grundform(self, parser):
        entry = _single_entry(parser, "gehörte", self.WIKITEXT)
        assert entry.lemma == "gehören"
        assert entry.reference == LemmaReference(
            target="gehören", type=ReferenceType.INFLECTED
        )
        # "Deklinierte Form" without grammatical features in the body
        # yields no POS — that's the correct shape.
        assert entry.pos == []


class TestVariantSpelling:
    """``{{Lemmaverweis}}`` — alternative spelling. lemma should point
    at the canonical form, reference type VARIANT."""

    WIKITEXT = """== Geografie ({{Sprache|Deutsch}}) ==
=== {{Wortart|Substantiv|Deutsch}}, {{f}} ===

{{Lemmaverweis|Geographie}}
"""

    def test_lemma_points_to_canonical(self, parser):
        entry = _single_entry(parser, "Geografie", self.WIKITEXT)
        assert entry.lemma == "Geographie"
        assert entry.reference == LemmaReference(
            target="Geographie", type=ReferenceType.VARIANT
        )


class TestMultiEntryPage:
    """A page can carry one entry per language and POS. The splitter
    must produce one ``ParsedEntry`` per Wortart header with stable
    ``entry_index`` values."""

    WIKITEXT = """== Hallo ({{Sprache|Deutsch}}) ==
=== {{Wortart|Interjektion|Deutsch}} ===

{{Bedeutungen}}
:[1] Grußformel

=== {{Wortart|Substantiv|Deutsch}}, {{n}} ===

{{Deutsch Substantiv Übersicht
|Genus=n
|Nominativ Singular=Hallo
|Nominativ Plural=Hallos
|Genitiv Singular=Hallos
|Genitiv Plural=Hallos
|Dativ Singular=Hallo
|Dativ Plural=Hallos
|Akkusativ Singular=Hallo
|Akkusativ Plural=Hallos
}}
"""

    def test_two_entries(self, parser):
        page = WiktionaryPage(page_id=555, name="Hallo", wikitext=self.WIKITEXT)
        entries = [parser.parse(e) for e in parser.entries(page)]
        assert len(entries) == 2

        interjection, noun = entries
        assert interjection.entry_index == 0
        assert interjection.pos == [
            PosTag(pos="Partikel", subtypes=("Interjektion",))
        ]
        assert interjection.meanings is not None
        assert interjection.meanings[0].text == "Grußformel"

        assert noun.entry_index == 1
        assert noun.pos == [PosTag(pos="Substantiv", subtypes=())]
        assert noun.inflection is not None
        assert noun.inflection["gender"] == "n"
        # Both entries share the page_name / page_id.
        assert interjection.page_name == noun.page_name == "Hallo"
        assert interjection.page_id == noun.page_id == 555


class TestRedirectAndEmptyPage:
    """Pages without wikitext and pure-redirect pages must yield zero
    entries — the loop is the caller's responsibility."""

    def test_empty_wikitext(self, parser):
        page = WiktionaryPage(page_id=1, name="Empty", wikitext="")
        assert list(parser.entries(page)) == []

    def test_no_wikitext(self, parser):
        page = WiktionaryPage(
            page_id=1, name="Redirect", wikitext=None, redirect_to="Target"
        )
        assert list(parser.entries(page)) == []

    def test_wikitext_without_wortart_header(self, parser):
        wikitext = "== Foo ({{Sprache|Deutsch}}) ==\n\nJust prose.\n"
        page = WiktionaryPage(page_id=1, name="Foo", wikitext=wikitext)
        assert list(parser.entries(page)) == []

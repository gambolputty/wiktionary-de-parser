"""Tests for WiktionaryParser.entries() header-shape tolerance."""

import pytest

from wiktionary_de_parser import WiktionaryParser
from wiktionary_de_parser.models import WiktionaryPage


@pytest.fixture
def wp():
    return WiktionaryParser()


def make_page(wikitext: str, name: str = "test") -> WiktionaryPage:
    return WiktionaryPage(page_id=1, name=name, wikitext=wikitext)


def test_standard_german_header(wp):
    wt = """== Hallo ({{Sprache|Deutsch}}) ==
=== {{Wortart|Interjektion|Deutsch}} ===

text
"""
    entries = list(wp.entries(make_page(wt, "Hallo")))
    assert len(entries) == 1


def test_double_space_header(wp):
    """`=== {{Wortart|...}}` with double space — seen on `bimbo`,
    `Portus Cale`, several Latin phrases. Was lost before the fix."""
    wt = """== bimbo ({{Sprache|Englisch}}) ==
=== {{Wortart|Substantiv|Englisch}} ===

text en

== bimbo ({{Sprache|Französisch}}) ==
===  {{Wortart|Substantiv|Französisch}}, {{f}}  ===

text fr

== bimbo ({{Sprache|Italienisch}}) ==
=== {{Wortart|Substantiv|Italienisch}}, {{m}} ===

text it
"""
    entries = list(wp.entries(make_page(wt, "bimbo")))
    assert len(entries) == 3
    assert "Französisch" in entries[1].wikitext


def test_lemma_prefix_header(wp):
    """Italian-style headers put the lemma before the Wortart template:
    `=== ombrello {{Wortart|...}}`."""
    wt = """== ombrello ({{Sprache|Italienisch}}) ==
=== ombrello {{Wortart|Substantiv|Italienisch}}, {{m}} ===

text
"""
    entries = list(wp.entries(make_page(wt, "ombrello")))
    assert len(entries) == 1
    assert "Italienisch" in entries[0].wikitext


def test_multiple_entries_split(wp):
    """Two entries for the same language must both be captured."""
    wt = """== Foo ({{Sprache|Deutsch}}) ==
=== {{Wortart|Substantiv|Deutsch}}, {{m}} ===

text a

=== {{Wortart|Verb|Deutsch}} ===

text b
"""
    entries = list(wp.entries(make_page(wt, "Foo")))
    assert len(entries) == 2


def test_empty_wikitext(wp):
    entries = list(wp.entries(make_page("", "Empty")))
    assert entries == []


def test_no_wortart_header(wp):
    """Pages that only contain a Sprache section but no Wortart yield zero
    entries — that's the correct shape for a redirect-target stub."""
    wt = """== Foo ({{Sprache|Deutsch}}) ==

Just prose, no Wortart template.
"""
    entries = list(wp.entries(make_page(wt, "Foo")))
    assert entries == []

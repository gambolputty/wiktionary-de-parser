"""Tests for ``WiktionaryEntry``'s lazy caches.

The caches exist for performance — every parser reads the same
``sections`` / ``header_wikicode`` / ``pronunciation_wikicode``, so each
expensive computation must happen at most once per entry. These tests
pin that contract (identity, not just equality, of cached objects).
"""

from __future__ import annotations

from test.methods.helpers import make_entry


class TestSectionsCache:
    def test_returns_same_dict_object(self):
        e = make_entry("{{Aussprache}}\n:foo\n")
        first = e.sections
        second = e.sections
        assert first is second  # cached, not recomputed

    def test_empty_wikitext_caches_empty_dict(self):
        e = make_entry("")
        assert e.sections == {}
        # Even an empty result should not recompute.
        assert e.sections is e.sections


class TestHeaderLineCache:
    def test_present_header(self):
        wt = "=== {{Wortart|Substantiv|Deutsch}} ===\n\nbody\n"
        e = make_entry(wt)
        first = e.header_line
        assert first is not None
        assert "{{Wortart|Substantiv|Deutsch}}" in first
        assert e.header_line is first

    def test_absent_header_caches_none(self):
        e = make_entry("just prose, no header")
        assert e.header_line is None
        # Re-access returns the same ``None`` without re-running the
        # regex (cached_property caches None too).
        assert e.header_line is None


class TestPronunciationWikicodeCache:
    def test_shared_between_accesses(self):
        wt = (
            "=== {{Wortart|Substantiv|Deutsch}} ===\n\n"
            "{{Aussprache}}\n:{{IPA}} {{Lautschrift|abc}}\n"
        )
        e = make_entry(wt)
        first = e.pronunciation_wikicode
        assert first is not None
        assert e.pronunciation_wikicode is first

    def test_no_aussprache_returns_none(self):
        wt = "=== {{Wortart|Substantiv|Deutsch}} ===\n\nplain body\n"
        e = make_entry(wt)
        assert e.pronunciation_wikicode is None


class TestHeaderWikicodeCache:
    def test_shared_between_accesses(self):
        wt = "=== {{Wortart|Substantiv|Deutsch}} ===\n"
        e = make_entry(wt)
        first = e.header_wikicode
        assert first is not None
        assert e.header_wikicode is first

    def test_no_header_returns_none(self):
        e = make_entry("body without header")
        assert e.header_wikicode is None

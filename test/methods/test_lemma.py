from test.test_data.lemma_data import lemma_data

import pytest

from wiktionary_de_parser.models import Lemma, ReferenceType
from wiktionary_de_parser.parser.parse_lemma import ParseLemma


class TestLemmaParsing:
    @pytest.mark.parametrize("test_input,expected", lemma_data)
    def test_parsing_lemmas(self, test_input, expected):
        wikitext = test_input
        result = ParseLemma.parse("Untitled", wikitext)
        assert result == Lemma(**expected)


class TestLemmaTopLevelOnly:
    """Code-review #2 finding 2 — a reference template buried inside a
    `<ref>…</ref>` citation in body prose must NOT hijack the page lemma.
    Only top-level templates count as the form reference."""

    def test_reference_inside_ref_is_ignored(self):
        wikitext = (
            "Some body prose with a citation"
            "<ref>see {{Alte Schreibweise|fake|Reform 1996}} in source</ref>"
            " and that's it."
        )
        result = ParseLemma.parse("Untitled", wikitext)
        # No top-level reference template → no lemma found, falls back to
        # the page name.
        assert result == Lemma(lemma="Untitled", reference_type=ReferenceType.NONE)

    def test_top_level_template_after_ref_in_prose_wins(self):
        wikitext = (
            "Body<ref>see {{Alte Schreibweise|fake|Reform}} here</ref>\n"
            "{{Grundformverweis|real}}"
        )
        result = ParseLemma.parse("Untitled", wikitext)
        assert result.lemma == "real"
        assert result.reference_type == ReferenceType.INFLECTED

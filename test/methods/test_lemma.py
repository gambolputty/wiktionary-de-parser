from test.methods.helpers import make_entry
from test.test_data.lemma_data import lemma_data

import pytest

from wiktionary_de_parser.models import LemmaReference, ReferenceType
from wiktionary_de_parser.parsers.lemma import parse, parse_lemma


def _ref(expected: dict) -> LemmaReference | None:
    """Convert legacy ``{lemma, reference_type}`` shape to the new
    ``LemmaReference`` object — keeps the existing test data file as the
    single source of truth for the edge cases we care about."""
    ref_type = expected["reference_type"]
    lemma = expected["lemma"]
    # The legacy "no reference" rows used ``reference_type=None`` (was
    # ``ReferenceType.NONE`` before the schema flattening) — those map
    # to ``reference = None`` in the new model.
    if ref_type is None:
        return None
    return LemmaReference(target=lemma, type=ref_type)


class TestLemmaParsing:
    @pytest.mark.parametrize("test_input,expected", lemma_data)
    def test_parsing_lemmas(self, test_input, expected):
        target, ref_type = parse_lemma(test_input)
        result: LemmaReference | None
        if target is not None and ref_type is not None:
            result = LemmaReference(target=target, type=ref_type)
        else:
            result = None
        assert result == _ref(expected)


class TestLemmaTopLevelOnly:
    """A reference template buried inside a ``<ref>…</ref>`` citation in
    body prose must NOT hijack the page lemma. Only top-level templates
    count as the form reference."""

    def test_reference_inside_ref_is_ignored(self):
        wikitext = (
            "Some body prose with a citation"
            "<ref>see {{Alte Schreibweise|fake|Reform 1996}} in source</ref>"
            " and that's it."
        )
        assert parse(make_entry(wikitext)) is None

    def test_top_level_template_after_ref_in_prose_wins(self):
        wikitext = (
            "Body<ref>see {{Alte Schreibweise|fake|Reform}} here</ref>\n"
            "{{Grundformverweis|real}}"
        )
        ref = parse(make_entry(wikitext))
        assert ref is not None
        assert ref.target == "real"
        assert ref.type == ReferenceType.INFLECTED

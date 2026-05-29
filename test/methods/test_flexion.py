from test.methods.helpers import case_id
from test.test_data.flexion_tables import tables

import pytest

from wiktionary_de_parser.parsers.inflection import (
    parse_inflection_from_wikitext,
    translate_inflection_key,
)


def _to_english_keys(expected: dict[str, str] | None) -> dict[str, str] | None:
    """The test data files still use the original German Übersicht
    parameter names (``"Genitiv Singular stark"``, …). The new parser
    emits English token-translated keys (``"genitive_singular_strong"``).
    Conversion is centralised in ``translate_inflection_key`` and the
    same function is applied here so test data stays single-source."""
    if expected is None:
        return None
    return {translate_inflection_key(k): v for k, v in expected.items()}


class TestInflectionParsing:
    @pytest.mark.parametrize(
        "test_input,expected",
        tables,
        ids=[case_id(inp) for inp, _ in tables],
    )
    def test_parsing_table_values(self, test_input, expected):
        parse_result = parse_inflection_from_wikitext(test_input)
        translated_expected = _to_english_keys(expected)

        if translated_expected is None:
            assert parse_result is None
            return

        assert parse_result is not None
        assert len(parse_result) == len(translated_expected)
        for key, value in translated_expected.items():
            assert key in parse_result
            assert parse_result[key] == value

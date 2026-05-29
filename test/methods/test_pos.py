from test.methods.helpers import case_id, make_entry
from test.test_data.pos_data import pos_test_data

import pytest

from wiktionary_de_parser.parsers.pos import parse as parse_pos


def _as_set(pos_list):
    """Normalise a list[PosTag] to a comparable {(pos, frozenset(subtypes))}."""
    return {(p.pos, frozenset(p.subtypes)) for p in pos_list}


def _expected_set(expected_dict):
    """The test data still uses the legacy {pos: [subtypes]} shape."""
    return {(k, frozenset(v)) for k, v in expected_dict.items()}


class TestPOSParsing:
    @pytest.mark.parametrize(
        "test_input,expected",
        pos_test_data,
        ids=[case_id(inp) for inp, _ in pos_test_data],
    )
    def test_parsing_pos_strings(self, test_input, expected):
        result = parse_pos(make_entry(test_input))
        assert _as_set(result) == _expected_set(expected)

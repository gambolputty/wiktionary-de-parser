from test.methods.helpers import case_id, make_entry
from test.test_data.rhymes_test_data import rhymes_test_data

import pytest

from wiktionary_de_parser.parsers.rhymes import parse as parse_rhymes


class TestRhymesParsing:
    @pytest.mark.parametrize(
        "test_input,expected",
        rhymes_test_data,
        ids=[case_id(inp) for inp, _ in rhymes_test_data],
    )
    def test_parsing_rhymes(self, test_input, expected):
        assert parse_rhymes(make_entry(test_input)) == expected

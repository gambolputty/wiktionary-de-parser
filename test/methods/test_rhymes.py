from test.test_data.rhymes_test_data import rhymes_test_data

import pytest

from wiktionary_de_parser.parser.parse_rhymes import ParseRhymes


class TestRhymesParsing:

    @pytest.mark.parametrize("test_input,expected", rhymes_test_data)
    def test_parsing_rhymes(self, test_input, expected):
        wikitext = test_input
        results = ParseRhymes.parse(wikitext)
        assert results == expected

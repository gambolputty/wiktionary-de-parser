import pytest

from wiktionary_de_parser.methods.syllables import init, parse_syllables
from test.test_data.syllables_data import data


class TestSyllablesParsing:
    def test_returns_false(self):
        assert init("test", "test", {}) == False

    @pytest.mark.parametrize("title,test_input,expected", data)
    def test_parsing_syllables(self, title, test_input, expected):
        parse_result = parse_syllables(title, test_input)
        assert parse_result == expected

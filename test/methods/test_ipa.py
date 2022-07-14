import pytest

from wiktionary_de_parser.methods.ipa import init, parse_ipa_strings
from test.test_data.ipa_data import data


class TestIPAParsing:
    def test_returns_false(self):
        assert init("test", "test", {}) == False

    @pytest.mark.parametrize("test_input,expected", data)
    def test_parsing_syllables(self, test_input, expected):
        parse_result = parse_ipa_strings(test_input)
        assert parse_result == expected

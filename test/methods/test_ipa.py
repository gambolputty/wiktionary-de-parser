import pytest

from wiktionary_de_parser.methods.ipa import init, parse_ipa_strings, parse_rhymes
from test.test_data.ipa_data import ipa_test_data, rhymes_test_data


class TestIPAParsing:
    def test_returns_false(self):
        assert init("test", "test", {}) == False

    @pytest.mark.parametrize("test_input,expected", ipa_test_data)
    def test_parsing_ipa_strings(self, test_input, expected):
        parse_result = parse_ipa_strings(test_input)
        assert parse_result == expected

    @pytest.mark.parametrize("test_input,expected", rhymes_test_data)
    def test_parsing_rhymes(self, test_input, expected):
        parse_result = parse_rhymes(test_input)
        assert parse_result == expected

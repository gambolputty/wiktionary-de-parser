import pytest

from wiktionary_de_parser.methods.lemma import init, parse_lemma
from test.test_data.lemma_data import data


class TestLemmaParsing:
    def test_returns_false(self):
        assert init("test", "test", {}) == {"inflected": False, "lemma": "test"}

    @pytest.mark.parametrize("test_input,expected", data)
    def test_parsing_lemmas(self, test_input, expected):
        parse_result = parse_lemma(test_input)
        assert parse_result == expected

from test.test_data.lemma_data import data

import mwparserfromhell
import pytest

from wiktionary_de_parser.methods.lemma import LemmaInfo, init, parse_lemma


class TestLemmaParsing:
    def test_returns_false(self):
        wikicode = mwparserfromhell.parse("test")
        assert init("test", wikicode) == LemmaInfo(inflected=False, lemma="test")

    @pytest.mark.parametrize("test_input,expected", data)
    def test_parsing_lemmas(self, test_input, expected):
        parse_result = parse_lemma(test_input)
        assert parse_result == expected

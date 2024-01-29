from test.test_data.syllables_data import data

import mwparserfromhell
import pytest

from wiktionary_de_parser.methods.syllables import SyllablesType, init, parse_syllables


class TestSyllablesParsing:
    def test_returns_false(self):
        wikicode = mwparserfromhell.parse("test")
        assert init("test", wikicode) == SyllablesType(syllables=None)

    @pytest.mark.parametrize("title,test_input,expected", data)
    def test_parsing_syllables(self, title, test_input, expected):
        parse_result = parse_syllables(title, test_input)
        assert parse_result == expected

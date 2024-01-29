from test.test_data.language_data import lang_test_data

import mwparserfromhell
import pytest

from wiktionary_de_parser.methods.language import LangType, init


class TestLanguageParsing:
    def test_returns_false(self):
        wikicode = mwparserfromhell.parse("test")
        assert init("test", wikicode) == LangType(lang=None, lang_code=None)

    @pytest.mark.parametrize("test_input,expected", lang_test_data)
    def test_parsing_lang_strings(self, test_input, expected):
        wikicode = mwparserfromhell.parse(test_input)
        parse_result = init("test", wikicode)
        assert parse_result == LangType(**expected)

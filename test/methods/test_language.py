from test.test_data.language_data import lang_test_data

import pytest

from wiktionary_de_parser.parser.parse_language import ParseLanguage


class TestLanguageParsing:
    @pytest.mark.parametrize("test_input,expected", lang_test_data)
    def test_parsing_lang_strings(self, test_input, expected):
        wikitext = test_input
        parse_result = ParseLanguage.parse(wikitext)
        assert parse_result == expected

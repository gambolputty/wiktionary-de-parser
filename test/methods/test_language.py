from test.test_data.language_data import lang_test_data

import pytest

from wiktionary_de_parser.methods.language import LangType, init


class TestLanguageParsing:
    def test_returns_false(self):
        assert init("test", "test", {}) == LangType(lang=None, lang_code=None)

    @pytest.mark.parametrize("test_input,expected", lang_test_data)
    def test_parsing_lang_strings(self, test_input, expected):
        parse_result = init("test", test_input, "")
        assert parse_result == LangType(**expected)

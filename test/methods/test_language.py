from test.methods.helpers import case_id, make_entry
from test.test_data.language_data import lang_test_data

import pytest

from wiktionary_de_parser.parsers.language import parse as parse_language


class TestLanguageParsing:
    @pytest.mark.parametrize(
        "test_input,expected",
        lang_test_data,
        ids=[case_id(inp) for inp, _ in lang_test_data],
    )
    def test_parsing_lang_strings(self, test_input, expected):
        lang, code = parse_language(make_entry(test_input))
        assert lang == expected["lang"]
        assert code == expected["lang_code"]

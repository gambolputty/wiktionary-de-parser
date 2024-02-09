from test.test_data.hyphenation_data import hyphenation_data

import pytest

from wiktionary_de_parser.parser.parse_hyphenation import ParseHyphenation


class TestHyphenationParsing:

    @pytest.mark.parametrize("title,test_input,expected", hyphenation_data)
    def test_parsing_hyphenation(self, title, test_input, expected):
        result = ParseHyphenation.parse(title, test_input)
        assert result == expected

from test.test_data.syllables_data import syllables_data

import pytest

from wiktionary_de_parser.parser.parse_syllables import ParseSyllables


class TestSyllablesParsing:

    @pytest.mark.parametrize("title,test_input,expected", syllables_data)
    def test_parsing_syllables(self, title, test_input, expected):
        result = ParseSyllables.parse(title, test_input)
        assert result == expected

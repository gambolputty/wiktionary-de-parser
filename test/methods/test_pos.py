from test.test_data.pos_data import pos_test_data

import pytest

from wiktionary_de_parser.parser.parse_pos import ParsePos


class TestPOSParsing:
    @pytest.mark.parametrize("test_input,expected", pos_test_data)
    def test_parsing_pos_strings(self, test_input, expected):
        wikitext = test_input
        result = ParsePos.parse(wikitext)
        assert result == expected

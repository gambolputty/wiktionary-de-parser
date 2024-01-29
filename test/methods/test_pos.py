from test.test_data.pos_data import pos_test_data

import mwparserfromhell
import pytest

from wiktionary_de_parser.methods.pos import POSType, init


class TestPOSParsing:
    def test_returns_false(self):
        wikicode = mwparserfromhell.parse("test")
        assert init("test", wikicode) == POSType(pos=None)

    @pytest.mark.parametrize("test_input,expected", pos_test_data)
    def test_parsing_pos_strings(self, test_input, expected):
        wikicode = mwparserfromhell.parse(test_input)
        parse_result = init("test", wikicode)
        assert parse_result == POSType(**expected)

from test.test_data.pos_data import pos_test_data

import pytest

from wiktionary_de_parser.methods.pos import POSType, init


class TestPOSParsing:
    def test_returns_false(self):
        assert init("test", "test", {}) == POSType(pos=None)

    @pytest.mark.parametrize("test_input,expected", pos_test_data)
    def test_parsing_pos_strings(self, test_input, expected):
        parse_result = init("test", test_input, {})
        assert parse_result == POSType(**expected)

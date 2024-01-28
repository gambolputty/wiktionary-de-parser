from test.test_data.flexion_tables import tables

import pytest

from wiktionary_de_parser.methods.flexion import FlexionType, init, parse_table_values


class TestFlexionParsing:
    def test_returns_false(self):
        assert init("test", "test", {}) == FlexionType(flexion=None)

    @pytest.mark.parametrize("test_input,expected", tables)
    def test_parsing_table_values(self, test_input, expected):
        parse_result = parse_table_values(test_input)

        assert parse_result is not None
        assert len(parse_result.keys()) == len(expected.keys())

        for key_expected, value_excpected in expected.items():
            assert key_expected in parse_result
            assert parse_result[key_expected] == value_excpected

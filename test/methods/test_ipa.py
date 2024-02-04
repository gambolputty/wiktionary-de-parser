from test.test_data.ipa_data import ipa_test_data

import pytest

from wiktionary_de_parser.parser.parse_ipa import ParseIpa


class TestIPAParsing:

    @pytest.mark.parametrize("test_input,expected", ipa_test_data)
    def test_parsing_ipa_strings(self, test_input, expected):
        wikitext = test_input
        results = ParseIpa.parse(wikitext)
        assert results == expected

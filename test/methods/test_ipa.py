from test.methods.helpers import case_id, make_entry
from test.test_data.ipa_data import ipa_test_data

import pytest

from wiktionary_de_parser.parsers.ipa import parse as parse_ipa


class TestIPAParsing:
    @pytest.mark.parametrize(
        "test_input,expected",
        ipa_test_data,
        ids=[case_id(inp) for inp, _ in ipa_test_data],
    )
    def test_parsing_ipa_strings(self, test_input, expected):
        # test_input is an Aussprache section block; parse via the real
        # entry API (section extraction + walk).
        assert parse_ipa(make_entry(test_input)) == expected

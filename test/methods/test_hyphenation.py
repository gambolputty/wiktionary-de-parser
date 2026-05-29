from test.methods.helpers import make_entry
from test.test_data.hyphenation_data import hyphenation_data

import pytest

from wiktionary_de_parser.parsers.hyphenation import parse as parse_hyphenation


class TestHyphenationParsing:
    @pytest.mark.parametrize(
        "title,test_input,expected",
        hyphenation_data,
        ids=[title for title, _, _ in hyphenation_data],
    )
    def test_parsing_hyphenation(self, title, test_input, expected):
        # title is the lemma (entry.page_name drives the char-walk).
        result = parse_hyphenation(make_entry(test_input, name=title))
        assert result == expected

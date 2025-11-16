from test.test_data.lemma_data import lemma_data

import pytest

from wiktionary_de_parser.models import Lemma
from wiktionary_de_parser.parser.parse_lemma import ParseLemma


class TestLemmaParsing:
    @pytest.mark.parametrize("test_input,expected", lemma_data)
    def test_parsing_lemmas(self, test_input, expected):
        wikitext = test_input
        result = ParseLemma.parse("Untitled", wikitext)
        assert result == Lemma(**expected)

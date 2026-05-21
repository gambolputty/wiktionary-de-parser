from test.test_data.etymology_data import etymology_test_data

import pytest

from wiktionary_de_parser.models import EtymologyResult
from wiktionary_de_parser.parser.parse_etymology import ParseEtymology


class TestEtymologyParsing:
    @pytest.mark.parametrize("lemma,wikitext,expected", etymology_test_data)
    def test_parsing_etymology(self, lemma, wikitext, expected):
        result = ParseEtymology.parse(lemma, wikitext)
        if expected is None:
            assert result is None
        else:
            assert result == EtymologyResult(**expected)

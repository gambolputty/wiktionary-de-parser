"""Feature parsers. Each module exposes a ``parse(entry)`` function."""

from wiktionary_de_parser.parsers.hyphenation import parse as parse_hyphenation
from wiktionary_de_parser.parsers.inflection import parse as parse_inflection
from wiktionary_de_parser.parsers.ipa import parse as parse_ipa
from wiktionary_de_parser.parsers.language import parse as parse_language
from wiktionary_de_parser.parsers.lemma import parse as parse_lemma
from wiktionary_de_parser.parsers.meanings import parse as parse_meanings
from wiktionary_de_parser.parsers.pos import parse as parse_pos
from wiktionary_de_parser.parsers.rhymes import parse as parse_rhymes

__all__ = [
    "parse_hyphenation",
    "parse_inflection",
    "parse_ipa",
    "parse_language",
    "parse_lemma",
    "parse_meanings",
    "parse_pos",
    "parse_rhymes",
]

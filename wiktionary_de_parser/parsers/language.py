"""Extract the entry's language (and ISO 639 code, if known).

The language is the *second* positional parameter of the first
``{{Wortart|<POS>|<Lang>}}`` template on the header line. Editors
occasionally mix in a named parameter (``{{Wortart|Substantiv|spr=en}}``)
— those must not be treated as the language.

Header-shape tolerance matches the entry splitter:
- double space ``=== {{Wortart…``
- lemma prefix ``=== ombrello {{Wortart…`` (Italian-style entries)
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from mwparserfromhell.wikicode import Wikicode

from wiktionary_de_parser._wikitext import (
    WORTART_TEMPLATE_NAMES,
    resolve_positional_params,
)
from wiktionary_de_parser.entry import WiktionaryEntry

_LANG_CODE_FILE = (
    Path(__file__).parent.parent / "assets" / ("sprachcodes_iso639-1.txt")
)


@lru_cache(maxsize=1)
def _lang_codes() -> dict[str, str]:
    # https://de.wiktionary.org/wiki/Hilfe:Sprachcodes
    table: dict[str, str] = {}
    with open(_LANG_CODE_FILE, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < 2 or not parts[0]:
                continue
            table[parts[0]] = parts[1]
    return table


def _language_from_parsed_header(parsed: Wikicode) -> str | None:
    for tmpl in parsed.filter_templates():
        if str(tmpl.name).strip() not in WORTART_TEMPLATE_NAMES:
            continue
        positional_map = resolve_positional_params(tmpl)
        if 2 not in positional_map:
            return None
        lang = str(positional_map[2].value).strip()
        return lang or None
    return None


def lookup_language_code(language: str | None) -> str | None:
    if not language:
        return None
    return _lang_codes().get(language.lower())


def parse(entry: WiktionaryEntry) -> tuple[str | None, str | None]:
    """Return ``(language, language_code)``. Both may be ``None``."""
    parsed = entry.header_wikicode
    language = (
        _language_from_parsed_header(parsed) if parsed is not None else None
    )
    return language, lookup_language_code(language)

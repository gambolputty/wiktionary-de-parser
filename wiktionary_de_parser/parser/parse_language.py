import re

import mwparserfromhell

from wiktionary_de_parser.config import PACKAGE_PATH
from wiktionary_de_parser.models import Language, ParseLanuageResult
from wiktionary_de_parser.parser import (
    WORTART_TEMPLATE_NAME_RE,
    Parser,
    resolve_positional_params,
)

# https://de.wiktionary.org/wiki/Hilfe:Sprachcodes
LANG_CODES = {}
with open(
    PACKAGE_PATH.joinpath("assets/sprachcodes_iso639-1.txt"), encoding="utf-8"
) as f:
    for line in f:
        parts = line.strip().split(",")
        if len(parts) < 2 or not parts[0]:
            continue
        LANG_CODES[parts[0]] = parts[1]


class ParseLanguage(Parser):
    name = "language"

    @staticmethod
    def parse_language(text: str):
        # The language is the *second* positional parameter of the first
        # {{Wortart|<POS>|<Lang>}} template on the Wortart-header line.
        # Editors sometimes mix in a named parameter ({{Wortart|Substantiv|
        # spr=en}}) — those must not be treated as the language.
        # Tolerate the same header shapes that WiktionaryParser.entries_from_page
        # accepts: double space (`===  {{Wortart…`) and lemma prefix
        # (`=== ombrello {{Wortart…`, Italian-style entries).
        match_line = re.search(
            r"=== [^\n]*?(" + WORTART_TEMPLATE_NAME_RE + r"\|[^\n]+)", text
        )
        if not match_line:
            return None

        parsed = mwparserfromhell.parse(match_line.group(1))
        for tmpl in parsed.filter_templates():
            tmpl_name = str(tmpl.name).strip()
            if tmpl_name not in ("Wortart", "Wortart-Test"):
                continue
            positional_map = resolve_positional_params(tmpl)
            if 2 not in positional_map:
                return None
            lang = str(positional_map[2].value).strip()
            return lang or None
        return None

    @classmethod
    def parse(cls, wikitext: str):
        result = {
            "lang": cls.parse_language(wikitext),
            "lang_code": None,
        }
        if result["lang"]:
            # get language code
            lang_lower = result["lang"].lower()

            if lang_lower in LANG_CODES:
                result["lang_code"] = LANG_CODES[lang_lower]

        return result

    def run(self) -> ParseLanuageResult:
        result = self.parse(self.entry.wikitext)

        return Language(**result)

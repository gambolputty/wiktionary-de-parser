import re

from wiktionary_de_parser.config import PACKAGE_PATH
from wiktionary_de_parser.models import ParseLanuageResult
from wiktionary_de_parser.parser import Parser

# https://de.wiktionary.org/wiki/Hilfe:Sprachcodes
LANG_CODES = {}
with open(
    PACKAGE_PATH.joinpath("assets/sprachcodes_iso639-1.txt"), encoding="utf-8"
) as f:
    lines = f.read().split("\n")
    for line in lines:
        x = line.split(",")
        LANG_CODES[x[0]] = x[1]


class ParseLanguage(Parser):
    @staticmethod
    def parse_language(text: str):
        match_lang = re.search(r"=== ?{{Wortart\|[^}|]+\|([^}|]+)(?:\|[^}|]+)*}}", text)

        if not match_lang:
            return

        lang_name: str = match_lang.group(1).strip()

        return lang_name

    def run(self) -> ParseLanuageResult:
        result = {
            "lang": self.parse_language(self.entry.wikitext),
            "lang_code": None,
        }
        if result["lang"]:
            # get language code
            lang_lower = result["lang"].lower()

            if lang_lower in LANG_CODES:
                result["lang_code"] = LANG_CODES[lang_lower]

        return result

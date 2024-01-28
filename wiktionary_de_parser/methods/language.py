import re
from dataclasses import dataclass

from wiktionary_de_parser.config import PACKAGE_PATH


@dataclass
class LangType:
    lang: str | None
    lang_code: str | None


# https://de.wiktionary.org/wiki/Hilfe:Sprachcodes
lang_codes = {}
with open(
    PACKAGE_PATH.joinpath("assets/sprachcodes_iso639-1.txt"), encoding="utf-8"
) as f:
    lines = f.read().split("\n")
    for line in lines:
        x = line.split(",")
        lang_codes[x[0]] = x[1]


def parse_language(text: str):
    match_lang = re.search(r"=== ?{{Wortart\|[^}|]+\|([^}|]+)(?:\|[^}|]+)*}}", text)

    if not match_lang:
        return

    lang_name: str = match_lang.group(1).strip()

    return lang_name


def init(title: str, text: str, current_record) -> LangType:
    result = {
        "lang": parse_language(text),
        "lang_code": None,
    }
    if result["lang"]:
        # get language code
        lang_lower = result["lang"].lower()
        if lang_lower in lang_codes:
            result["lang_code"] = lang_codes[lang_lower]

    return LangType(**result)

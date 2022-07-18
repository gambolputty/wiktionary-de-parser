from pathlib import Path
import re
from typing import Literal, TypedDict, Union

from wiktionary_de_parser.config import PACKAGE_PATH


class LangType(TypedDict, total=False):
    lang: str
    lang_code: str


LanguageResult = Union[Literal[False], LangType]

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
        return False

    lang_name: str = match_lang.group(1).strip()

    return lang_name


def init(title: str, text: str, current_record) -> LanguageResult:
    result: LangType = {}
    lang = parse_language(text)

    if lang:
        result["lang"] = lang

        # get language code
        lang_lower = lang.lower()
        if lang_lower in lang_codes:
            result["lang_code"] = lang_codes[lang_lower]

    return result if result else False

import re
from typing import Literal, TypedDict, Union

from wiktionary_de_parser import PACKAGE_PATH


class LangInfo(TypedDict, total=False):
    lang: str
    lang_code: str


LanguageResult = Union[Literal[False], LangInfo]

# https://de.wiktionary.org/wiki/Hilfe:Sprachcodes
langcodes = {}
with open(PACKAGE_PATH.joinpath('assets/sprachcodes_iso639-1.txt'), encoding='utf-8') as f:
    lines = f.read().split('\n')
    for line in lines:
        x = line.split(',')
        langcodes[x[0]] = x[1]


def init(
    title: str,
    text: str,
    current_record
) -> LanguageResult:
    match_lang_name = re.search(r'=== ?{{Wortart(?:-Test)?\|[^}|]+\|([^}|]+)(?:\|[^}|]+)*}}', text)
    if not match_lang_name:
        return False

    lang_name: str = match_lang_name.group(1) if match_lang_name.group(1) else match_lang_name.group(2)
    lang_name = lang_name.strip()

    # get lang code
    result: LangInfo = {'lang': lang_name}

    lang_name_low = lang_name.lower()
    if lang_name_low in langcodes:
        result['lang_code'] = langcodes[lang_name_low]

    return result

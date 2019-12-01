import os
import re
import sys
from os.path import dirname, abspath

parent_path = dirname(dirname(abspath(__file__)))

# https://de.wiktionary.org/wiki/Hilfe:Sprachcodes
langcodes = {}
with open(f'{parent_path}/assets/sprachcodes_iso639-1.txt', encoding='utf-8') as f:
    lines = f.read().split('\n')
    for line in lines:
        x = line.split(',')
        langcodes[x[0]] = x[1]


def init(title, text, current_record):
    match_lang_name = re.search(r'=== ?{{Wortart(?:-Test)?\|[^}|]+\|([^}|]+)(?:\|[^}|]+)*}}', text)
    if not match_lang_name:
        return False

    lang_name = match_lang_name.group(1) if match_lang_name.group(1) else match_lang_name.group(2)
    lang_name = lang_name.strip()

    # get lang code
    result = { 'lang': lang_name }

    lang_name_low = lang_name.lower()
    if lang_name_low in langcodes:
        result['langCode'] = langcodes[lang_name_low]

    return result

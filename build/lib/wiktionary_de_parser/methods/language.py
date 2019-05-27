import re


def init(title, text, current_record):
    match_lang_name = re.search(r'=== ?{{Wortart(?:-Test)?\|[^}|]+\|([^}|]+)(?:\|[^}|]+)*}}', text)
    if not match_lang_name:
        return False

    lang_name = match_lang_name.group(1) if match_lang_name.group(1) else match_lang_name.group(2)
    lang_name = lang_name.strip()

    return {'language': lang_name}

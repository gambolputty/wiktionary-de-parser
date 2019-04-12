import re


def init(title, text, current_record):
    match_firstline = re.search(r'({{Aussprache}}\n[^\n]+)', text)
    if not match_firstline:
        return False

    first_line = match_firstline.group(1)
    found_ipa = re.findall(r'{{Lautschrift\|([^}]+)}}', first_line)
    if not found_ipa:
        return False

    result = found_ipa[0]

    # compare with ryme ipa field
    # prioritize ipa value that is part of a rhyme
    reim_match = re.search(r'{{Reim\|([^}|]+)(?:\|[^}]+)*}}', text)
    if reim_match:
        r = reim_match.group(1)
        m = [x for x in found_ipa if x.endswith(r)]
        if m:
            result = m[0]

    return {'ipa': result}

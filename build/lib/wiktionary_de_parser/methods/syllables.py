import re
import pyphen


def init(title, text, current_record):
    # find syllables in wikitext
    # reference: https://de.wiktionary.org/wiki/Hilfe:Worttrennung

    # match_test = re.search(r'({{Worttrennung}}\n:?[^\n]+)', text)
    # if match_test:
    #     print(match_test.group(1))
    #     print()

    result = False
    matched = re.findall(r'{{Worttrennung}}\n::?(?:{{[^}]+}},? )*([\w· ]+|[\w·]+)', text)
    if matched:
        result = re.split(r' |·', matched[0])
    elif 'language' in current_record and current_record['language'] in pyphen.LANGUAGES:
        # get syllables with PyHyphen
        dic = pyphen.Pyphen(lang=current_record['language'])
        syl_string = dic.inserted(title)
        # split by "-" and remove empty entries
        result = [x for x in re.split(r' |-', syl_string) if x]

    return {'syllables': result} if result else False

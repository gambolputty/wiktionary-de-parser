import re
import pyphen


def init(title, text, record):
    # find syllables in wikitext
    # reference: https://de.wiktionary.org/wiki/Hilfe:Worttrennung

    # match_test = re.search(r'({{Worttrennung}}\n:?[^\n]+)', text)
    # if match_test:
    #     print(match_test.group(1))
    #     print()

    matched = re.findall(r'{{Worttrennung}}\n::?(?:{{[^}]+}},? )*([\w· ]+|[\w·]+)', text)
    if matched:
        return re.split(r' |·', matched[0])
    elif 'language' in record and record['language'] in pyphen.LANGUAGES:
        # get syllables with PyHyphen
        dic = pyphen.Pyphen(lang=record['language'])
        syl_string = dic.inserted(title)
        # split by "-" and remove empty entries
        return [x for x in re.split(r' |-', syl_string) if x]

    return False

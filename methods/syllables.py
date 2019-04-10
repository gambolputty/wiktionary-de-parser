import re
from hyphen import Hyphenator


def init(title, text, result):

    # PyHyphen
    if result['language'] == 'de':
        lang_code = 'de_DE'
    elif result['language'] == 'en':
        lang_code = 'en_US'
    else:
        lang_code = 'de_DE'

    h_de = Hyphenator(lang_code)

    match_wt = re.search(r'{{Worttrennung}}\n:?(?:{{.+}},? )*([^ \n]+)(?:, .+|\n)', text)
    if match_wt:
        syls = match_wt.group(1)
        return syls.split('·')
    else:
        # Hole Sylben mit PyHyphen
        syls_list = [x.strip() for x in h_de.syllables(title) if x != u'-']
        return syls_list

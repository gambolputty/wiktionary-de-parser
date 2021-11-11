import re

"""
Reference:
https://de.wiktionary.org/wiki/Kategorie:Wiktionary:Flexionstabelle_(Deutsch)
https://de.wiktionary.org/wiki/Hilfe:Flexionstabellen
"""
# TODO: find values:
# "}" - Frauenzimmer
# "&nbsp" - Fischer Random Chess
# Tausendfache|kein Plural=jas
# Wissenswerte|kein Plural=ja
# ? - Alf

wanted_table_names = [
    'Deutsch Adjektiv Übersicht',
    'Deutsch Adverb Übersicht',
    'Deutsch Eigenname Übersicht',
    'Deutsch Nachname Übersicht',
    'Deutsch Pronomen Übersicht',
    'Deutsch Substantiv Übersicht',
    'Deutsch Substantiv Übersicht -sch',
    'Deutsch adjektivisch Übersicht',
    'Deutsch Toponym Übersicht',
    'Deutsch Verb Übersicht',
]


def find_table(text):
    re_string = '({{(' + '|'.join(wanted_table_names) + ')[^}]+}})'
    match_table = re.search(re_string, text)
    if not match_table:
        return False
    return match_table.group(1)


def parse_table_values(table_string):
    table_tuples = re.findall(r'(?:^\|([^=]+)=([^\n]+)$)+', table_string, re.MULTILINE)
    if not table_tuples:
        return False

    # normalize values
    result = {}
    for (key, value) in table_tuples:
        if key.startswith('Bild'):
            continue

        if key in ('Flexion', 'Weitere Konjugationen'):
            continue

        # clean text

        # strip comments, <ref>-tags etc.
        text = re.sub(r'<[^>]+>', ' ', text)
        # trim
        text = text.strip()

        # genus
        if key in ['Genus', 'Genus 1', 'Genus 2', 'Genus 3', 'Genus 4']:
            # the Genus of plural words is set to 0 (or other value)
            # reference: https://de.wiktionary.org/wiki/Wiktionary:Teestube/Archiv/2015/11#Genus_in_der_Flexionstabelle_bei_Pluralw%C3%B6rtern
            # -> normalize
            text = text.lower()
            if text not in ['f', 'm', 'n']:
                text = None

        # none dash to None type
        if text in ('—', '-', '–'):
            text = None

        result[key] = text

    return result if result.keys() else False


def init(title, text, current_record):
    table_string = find_table(text)
    if not table_string:
        return False

    table_dict = parse_table_values(table_string)
    if table_dict is False:
        return False

    return {'flexion': table_dict}

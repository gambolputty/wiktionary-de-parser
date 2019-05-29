import re
import itertools

"""
reference: https://de.wiktionary.org/wiki/Hilfe:Wortart
"""
debug = False

pos_map = {
    'Abkürzung': [
        'Kurzwort'
    ],
    'Adjektiv': [
        'Partizip',
        'Partizip I',
        'Partizip II',
        'Komparativ',
        'Superlativ',
        'Gerundivum',
        'Dekliniertes Gerundivum',
    ],
    'Adposition': [
        'Postposition',
        'Präposition',
        'Zirkumposition',
    ],
    'Adverb': [
        'Fokuspartikel',
        'Gradpartikel',
        'Interrogativadverb',
        'Konjunktionaladverb',
        'Lokaladverb',
        'Modalpartikel',
        'Negationspartikel',
        'Pronominaladverb',
        'Temporaladverb',
        'Modaladverb',
        'Relativadverb',
    ],
    'Affix': [
        'Präfix',
        'Suffix',
        'Infix',
        'Interfix',
        'Zirkumfix',
        'Präfixoid',
        'Suffixoid',
    ],
    'Gebundenes Lexem': [],
    'Artikel': [],
    'Konjunktion': [
        'Subjunktion'
    ],
    'Kontraktion': [],
    'Numerale': [
        'Kardinalzahl',
        'Ordinalzahl',
    ],
    'Partikel': [
        'Interjektion',
        'Antwortpartikel',
        'Grußformel',
        'Onomatopoetikum',
        'Vergleichspartikel',
        'Fragepartikel',
    ],
    'Pronomen': [
        'Indefinitpronomen',
        'Interrogativpronomen',
        'Demonstrativpronomen',
        'Personalpronomen',
        'Possessivpronomen',
        'Reflexivpronomen',
        'Reflexives Personalpronomen',
        'Relativpronomen',
        'Reziprokpronomen',
    ],
    'Redewendung': [],
    'Sprichwort': [],
    'Geflügeltes Wort': [],
    'Merkspruch': [],
    'Formel': [],
    'Substantiv': [
        'Toponym',
        'Vorname',
        'Nachname',
        'Familienname',
        'Patronym',
        'Eigenname',
        'Straßenname',
        'Zahlklassifikator',
        'Singularetantum',
        'Pluraletantum',
        'adjektivische Deklination',
        'Substantivierter Infinitiv',
    ],
    'Ortsnamengrundwort': [],
    'Symbol': [
        'Buchstabe',
        'Zahlzeichen',
        'Schriftzeichen',
    ],
    'Verb': [
        'Konjugierte Form',
        'Hilfsverb',
        'Erweiterter Infinitiv',
    ],
    'Wortverbindung': [],
    'Flektierte Form': [],
}

if debug is True:
    not_in_map = set()
    all_pos_names = list(pos_map.keys()) + list(itertools.chain.from_iterable(list(pos_map.values())))
    all_pos_names = [x.lower() for x in all_pos_names]


def find_pos(title, pos_names, text):
    result = {}

    # check for "Deklinierte Form" first
    # can be both: Substantiv/Adjektiv
    if 'Deklinierte Form' in pos_names:
        # get first uppercase letter
        upper_chars = []
        for char in title:
            if char.isupper():
                upper_chars.append(char)
                break
        if upper_chars:
            result['Substantiv'] = ['Deklinierte Form']
        else:
            result['Adjektiv'] = ['Deklinierte Form']
        # remove from names
        del pos_names[pos_names.index('Deklinierte Form')]

    # fix POS when there is a certain POS template, but POS is not in pos_names
    # example "Substantiv": https://de.wiktionary.org/wiki/wei%C3%9Fes_Gold

    # Substantiv
    if '{{Deutsch adjektivisch Übersicht' in text \
        or '{{Deutsch Substantiv Übersicht - sch' in text \
        or '{{Deutsch Substantiv Übersicht' in text \
        or '{{Deutsch Toponym Übersicht' in text:
        if 'Substantiv' not in result:
            result['Substantiv'] = []
    if '{{Deutsch adjektivisch Übersicht' in text and 'adjektivische Deklination' not in result['Substantiv']:
        result['Substantiv'].append('adjektivische Deklination')
    if '{{Deutsch Toponym Übersicht' in text and 'Toponym' not in result['Substantiv']:
        result['Substantiv'].append('Toponym')    
    # Adjektiv
    if '{{Deutsch Adjektiv Übersicht' in text and 'Adjektiv' not in result:
        result['Adjektiv'] = []
    # Adverb
    if '{{Deutsch Adverb Übersicht' in text and 'Adverb' not in result:
        result['Adverb'] = []
    # Pronomen
    if '{{Deutsch Pronomen Übersicht' in text and 'Pronomen' not in result:
        result['Pronomen'] = []
    # Verb
    if '{{Deutsch Verb Übersicht' in text and 'Verb' not in result:
        result['Verb'] = []

    # map other pos names
    for key, values in pos_map.items():
        # maintain letter case of position map
        key_low = key.lower()
        for name in pos_names:
            name_low = name.lower()
            if name_low == key_low and key not in result:
                result[key] = []
            values_low = [x.lower() for x in values]
            if name_low in values_low:
                name_idx = values_low.index(name_low)
                if key not in result:
                    result[key] = []
                result[key].append(values[name_idx])

    if debug is True:
        not_found_names = [x for x in pos_names if x.lower() not in all_pos_names and x not in not_in_map]
        if not_found_names:
            not_in_map.update(not_found_names)
            for name in not_found_names:
                print('"{}" not in POS-map (all: {})'.format(name, ', '.join(pos_names)))

    return result


def init(title, text, current_record):
    # find line
    match_line = re.search(r'(=== ?{{Wortart(?:-Test)?\|[^\n]+)', text)
    if not match_line:
        return False

    # can have multiple POS values
    line = match_line.group(1)
    pos_names = re.findall(r'{{Wortart(?:-Test)?\|([^}|]+)(?:\|[^}|]+)*}}', line)
    if not pos_names:
        return False

    if not pos_names:
        return False

    pos_normalized = find_pos(title, pos_names, text)
    if not pos_normalized.keys():
        return False

    return {'pos': pos_normalized}

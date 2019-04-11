import re
import itertools

"""
reference: https://de.wiktionary.org/wiki/Hilfe:Wortart
"""
debug = True

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


def find_pos(title, pos_names):
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
            result['Substantiv'] = []
        else:
            result['Adjektiv'] = []
        # remove from names
        del pos_names[pos_names.index('Deklinierte Form')]

    # map other pos names
    for key, values in pos_map.items():
        # maintain letter case of position map
        key_low = key.lower()
        for name in pos_names:
            name_low = name.lower()
            if name_low == key_low:
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


def init(title, text, record):

    # multiple POS values
    found_pos = re.search(r'=== ?{{Wortart\|([^}|]+)(?:\|[^}|]+)*}}(?:, .+{{Wortart\|([^}|]+)(?:\|[^}|]+)*}})*', text)
    if not found_pos:
        return False
    pos_names = [x.strip() for x in found_pos.groups() if x is not None]
    if not pos_names:
        return False
    return find_pos(title, pos_names)


"""
Alle gefundenen Wortarten:

Substantiv
Konjugierte Form
Deklinierte Form
Nachname
Vorname
Personalpronomen
Numerale
Verb
Toponym
Possessivpronomen
Adjektiv
Interjektion
Eigenname
Schriftzeichen
Zahlklassifikator
Abkürzung
Wortverbindung
Gebundenes Lexem
Präfix
Indefinitpronomen
Adverb
Konjunktion
Buchstabe
Symbol
Zahlzeichen
Präposition
Partikel
Relativpronomen
Interrogativpronomen
Partizip II
Redewendung
Modalpartikel
Antwortpartikel
Demonstrativpronomen
Pronomen
Temporaladverb
Kontraktion
Artikel
Negationspartikel
Grußformel
Subjunktion
Suffix
Reflexivpronomen
Lokaladverb
Gradpartikel
Reflexives Personalpronomen
Partizip I
Onomatopoetikum
Umschrift
Fokuspartikel
Sprichwort
Hilfsverb
Komparativ
Superlativ
Vergleichspartikel
Konjunktionaladverb
Pronominaladverb
Präfixoid
Postposition
Geflügeltes Wort
Ortsnamengrundwort
Straßenname
Modaladverb
Interrogativadverb
Hiragana
Gerundium
Merkspruch
Adjektiv
Kurzwort
Kognomen
deklinierte Form
Formel
Abkürzung (Deutsch)
gebundenes Lexem
Gerundium
Affix
Reziprokpronomen
Zusammengesetztes Prädikatwort
Erweiterter Infinitiv
Suffixoid
Relativadverb
Zirkumposition
Gentilname
unbekannt
Kausaladverb
Partikelverb
adverbialer Ausdruck
Personalpronomen
Flektierte Form
Infix
Substantivierter Infinitiv
Kardinalzahl
Ordinalzahl
Infinitiv
Familienname
Partizip
Fragepartikel
Adverb
adjektivische Deklination
Dekliniertes Gerundivum
Patronym
Adjetiv

"""

import re
import itertools
from typing import Dict, List, Literal, TypedDict, Union

"""
Reference: https://de.wiktionary.org/wiki/Hilfe:Wortart
"""


class POSType(TypedDict, total=False):
    pos: Dict[str, List[str]]


POSResult = Union[Literal[False], POSType]
debug = False

pos_map = {
    "Abkürzung": ["Kurzwort"],
    "Adjektiv": [
        "Partizip",
        "Partizip I",
        "Partizip II",
        "Komparativ",
        "Superlativ",
        "Gerundivum",
        "Dekliniertes Gerundivum",
    ],
    "Adposition": [
        "Postposition",
        "Präposition",
        "Zirkumposition",
    ],
    "Adverb": [
        "Fokuspartikel",
        "Gradpartikel",
        "Interrogativadverb",
        "Konjunktionaladverb",
        "Lokaladverb",
        "Modalpartikel",
        "Negationspartikel",
        "Pronominaladverb",
        "Temporaladverb",
        "Modaladverb",
        "Relativadverb",
    ],
    "Affix": [
        "Präfix",
        "Suffix",
        "Infix",
        "Interfix",
        "Zirkumfix",
        "Präfixoid",
        "Suffixoid",
    ],
    "Gebundenes Lexem": [],
    "Artikel": [],
    "Konjunktion": ["Subjunktion"],
    "Kontraktion": [],
    "Numerale": [
        "Kardinalzahl",
        "Ordinalzahl",
    ],
    "Partikel": [
        "Interjektion",
        "Antwortpartikel",
        "Grußformel",
        "Onomatopoetikum",
        "Vergleichspartikel",
        "Fragepartikel",
    ],
    "Pronomen": [
        "Indefinitpronomen",
        "Interrogativpronomen",
        "Demonstrativpronomen",
        "Personalpronomen",
        "Possessivpronomen",
        "Reflexivpronomen",
        "Reflexives Personalpronomen",
        "Relativpronomen",
        "Reziprokpronomen",
    ],
    "Redewendung": [],
    "Sprichwort": [],
    "Geflügeltes Wort": [],
    "Merkspruch": [],
    "Formel": [],
    "Substantiv": [
        "Toponym",
        "Vorname",
        "Nachname",
        "Familienname",
        "Patronym",
        "Eigenname",
        "Straßenname",
        "Zahlklassifikator",
        "Singularetantum",
        "Pluraletantum",
        "adjektivische Deklination",
        "Substantivierter Infinitiv",
    ],
    "Ortsnamengrundwort": [],
    "Symbol": [
        "Buchstabe",
        "Zahlzeichen",
        "Schriftzeichen",
    ],
    "Verb": [
        "Konjugierte Form",
        "Hilfsverb",
        "Erweiterter Infinitiv",
    ],
    "Wortverbindung": [],
    # needs additional parsing; can be: Substantiv, Adjektiv, Artikel, Pronomen
    "Deklinierte Form": [],
}

if debug is True:
    not_in_map = set()
    all_pos_names = list(pos_map.keys()) + list(
        itertools.chain.from_iterable(list(pos_map.values()))
    )
    all_pos_names = [x.lower() for x in all_pos_names]


def find_pos(title, pos_names, text, current_record):
    result = {}

    # fix POS when there is a certain POS template, but POS is not in pos_names
    # example "Substantiv": https://de.wiktionary.org/wiki/wei%C3%9Fes_Gold

    if (
        "{{Deutsch adjektivisch Übersicht" in text
        or "{{Deutsch Substantiv Übersicht - sch" in text
        or "{{Deutsch Substantiv Übersicht" in text
        or "{{Deutsch Toponym Übersicht" in text
    ):
        if "Substantiv" not in result:
            result["Substantiv"] = []
    if (
        "{{Deutsch adjektivisch Übersicht" in text
        and "adjektivische Deklination" not in result["Substantiv"]
    ):
        result["Substantiv"].append("adjektivische Deklination")
    if "{{Deutsch Toponym Übersicht" in text and "Toponym" not in result["Substantiv"]:
        result["Substantiv"].append("Toponym")
    # Adjektiv
    if "{{Deutsch Adjektiv Übersicht" in text and "Adjektiv" not in result:
        result["Adjektiv"] = []
    # Adverb
    if "{{Deutsch Adverb Übersicht" in text and "Adverb" not in result:
        result["Adverb"] = []
    # Pronomen
    if "{{Deutsch Pronomen Übersicht" in text and "Pronomen" not in result:
        result["Pronomen"] = []
    # Verb
    if "{{Deutsch Verb Übersicht" in text and "Verb" not in result:
        result["Verb"] = []

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
                if key not in result:
                    result[key] = []
                name_idx = values_low.index(name_low)
                value = values[name_idx]
                if value not in result[key]:
                    result[key].append(value)

    if debug is True:
        not_found_names = [
            x
            for x in pos_names
            if x.lower() not in all_pos_names and x not in not_in_map
        ]
        if not_found_names:
            not_in_map.update(not_found_names)
            for name in not_found_names:
                print(
                    '"{}" not in POS-map (all: {})'.format(name, ", ".join(pos_names))
                )

    return result


def init(title: str, text: str, current_record) -> POSResult:
    # find line
    match_line = re.search(r"(=== ?{{Wortart(?:-Test)?\|[^\n]+)", text)
    if not match_line:
        return False

    # can have multiple POS values
    line = match_line.group(1)
    pos_names = re.findall(r"{{Wortart(?:-Test)?\|([^}|]+)(?:\|[^}|]+)*}}", line)
    if not pos_names:
        return False

    # strip
    pos_names = [name.strip() for name in pos_names]

    # find in map
    pos_normalized = find_pos(title, pos_names, text, current_record)
    if not pos_normalized.keys():
        return False

    return {"pos": pos_normalized}

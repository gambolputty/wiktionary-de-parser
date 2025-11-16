import itertools
import re

from wiktionary_de_parser.models import ParsePosResult
from wiktionary_de_parser.parser import Parser

DEBUG = False

# Mapping from genitive forms in "Grammatische Merkmale" to (POS, subtype)
# Format: "Genitive" -> (pos, subtype) or (pos, None) if no subtype
DEKLINIERTE_FORM_POS_MAP = {
    "Substantivs": ("Substantiv", None),
    "Adjektivs": ("Adjektiv", None),
    "Positivs": ("Adjektiv", "Positiv"),
    "Superlativs": ("Adjektiv", "Superlativ"),
    "Komparativs": ("Adjektiv", "Komparativ"),
    "Personalpronomens": ("Pronomen", "Personalpronomen"),
    "Possessivpronomens": ("Pronomen", "Possessivpronomen"),
    "Demonstrativpronomens": ("Pronomen", "Demonstrativpronomen"),
    "Indefinitpronomens": ("Pronomen", "Indefinitpronomen"),
    "Relativpronomens": ("Pronomen", "Relativpronomen"),
    "Reflexivpronomens": ("Pronomen", "Reflexivpronomen"),
    "Pronomens": ("Pronomen", None),
    "Numerales": ("Numerale", None),
}

POS_MAP = {
    "Abkürzung": ["Kurzwort"],
    "Adjektiv": [
        "Partizip",
        "Partizip I",
        "Partizip II",
        "Positiv",
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
}

NOT_IN_MAP = set()

if DEBUG is True:
    all_pos_names = list(POS_MAP.keys()) + list(
        itertools.chain.from_iterable(list(POS_MAP.values()))
    )
    all_pos_names = [x.lower() for x in all_pos_names]


class ParsePos(Parser):
    name = "pos"

    @staticmethod
    def find_pos(pos_names, text):
        result: dict[str, list[str]] = {}

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
        if (
            "{{Deutsch Toponym Übersicht" in text
            and "Toponym" not in result["Substantiv"]
        ):
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
        for key, values in POS_MAP.items():
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

        if DEBUG is True:
            not_found_names = [
                x
                for x in pos_names
                if x.lower() not in all_pos_names and x not in NOT_IN_MAP
            ]
            if not_found_names:
                NOT_IN_MAP.update(not_found_names)
                for name in not_found_names:
                    print(
                        '"{}" not in POS-map (all: {})'.format(
                            name, ", ".join(pos_names)
                        )
                    )

        return result

    @staticmethod
    def extract_pos_from_deklinierte_form(wikitext: str):
        """
        Extract the actual POS from 'Deklinierte Form' entries.

        Deklinierte Form entries contain grammatical features like:
        "Genitiv Singular des Substantivs [[Word]]"

        We extract "Substantivs" and map it to "Substantiv".
        """
        # Look for the pattern "des/der <POS-genitive>"
        # Account for optional empty lines after the template
        match = re.search(
            r'{{Grammatische Merkmale}}\s*(.*?)(?:\n\n{{|{{Grundformverweis|$)',
            wikitext,
            re.DOTALL
        )

        if not match:
            return None

        features_text = match.group(1).strip()

        if not features_text:
            return None

        # Extract all POS mentions in genitive form
        pos_matches = re.findall(
            r'des?\s+(' + '|'.join(DEKLINIERTE_FORM_POS_MAP.keys()) + r')\b',
            features_text
        )

        if not pos_matches:
            return None

        # Take the first match and map it to the base form
        pos_genitive = pos_matches[0]
        pos_info = DEKLINIERTE_FORM_POS_MAP.get(pos_genitive)

        if pos_info:
            pos_base, subtype = pos_info
            if subtype:
                return {pos_base: [subtype]}
            else:
                return {pos_base: []}

        return None

    @classmethod
    def parse(cls, wikitext: str):
        match_line = re.search(r"(=== ?{{Wortart(?:-Test)?\|[^\n]+)", wikitext)
        result = None

        if match_line:
            # can have multiple POS values
            line = match_line.group(1)
            pos_names = re.findall(
                r"{{Wortart(?:-Test)?\|([^}|]+)(?:\|[^}|]+)*}}", line
            )

            if pos_names:
                # strip
                pos_names = [name.strip() for name in pos_names]

                # Special handling for "Deklinierte Form"
                # Extract the actual POS from grammatical features
                if "Deklinierte Form" in pos_names:
                    deklinierte_pos = cls.extract_pos_from_deklinierte_form(
                        wikitext
                    )
                    if deklinierte_pos:
                        return deklinierte_pos

                # find in map
                pos_normalized = cls.find_pos(pos_names, wikitext)

                if pos_normalized.keys():
                    result = pos_normalized

        return result

    def run(self) -> ParsePosResult:
        return self.parse(self.entry.wikitext)

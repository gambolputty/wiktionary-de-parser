import re
from typing import Dict, Literal, TypedDict, Union

"""
Reference:
https://de.wiktionary.org/wiki/Kategorie:Wiktionary:Flexionstabelle_(Deutsch)
https://de.wiktionary.org/wiki/Hilfe:Flexionstabellen
"""


class FlexionType(TypedDict, total=False):
    flexion: Dict[str, str]


FlexionResult = Union[Literal[False], FlexionType]

wanted_table_names = [
    "Deutsch Adjektiv Übersicht",
    "Deutsch Adverb Übersicht",
    "Deutsch Eigenname Übersicht",
    "Deutsch Nachname Übersicht",
    "Deutsch Pronomen Übersicht",
    "Deutsch Substantiv Übersicht",
    "Deutsch Substantiv Übersicht -sch",
    "Deutsch adjektivisch Übersicht",
    "Deutsch Toponym Übersicht",
    "Deutsch Verb Übersicht",
]


def find_table(text):
    re_string = "({{(" + "|".join(wanted_table_names) + ")[^}]+}})"
    match_table = re.search(re_string, text)

    if not match_table:
        return False

    return match_table.group(1)


def parse_table_values(table_string):
    table_values = re.findall(
        r"(?:\|([^=\n]+)=([^\n|}]+))+?", table_string, re.MULTILINE
    )

    if not table_values:
        return False

    # normalize values
    result = {}
    for key, text in table_values:
        if key.startswith("Bild"):
            continue

        if key in ("Flexion", "Weitere Konjugationen"):
            continue

        # clean text
        text = text.strip()
        text = text.replace("&nbsp", " ")
        text = re.sub(r"<[^>]+>", " ", text)  # strip comments, <ref>-tags etc.

        # genus
        if key in ["Genus", "Genus 1", "Genus 2", "Genus 3", "Genus 4"]:
            # the Genus of plural words is set to 0 (or other value)
            # reference: https://de.wiktionary.org/wiki/Wiktionary:Teestube/Archiv/2015/11#Genus_in_der_Flexionstabelle_bei_Pluralw%C3%B6rtern
            # -> normalize
            text = text.lower()
            if text not in ["f", "m", "n"]:
                continue

        if not text or text in ("—", "-", "–", "−", "?"):
            continue

        result[key] = text

    return result if result.keys() else False


def init(title: str, text: str, current_record) -> FlexionResult:
    table_string = find_table(text)
    if not table_string:
        return False

    table_dict = parse_table_values(table_string)
    if table_dict is False:
        return False

    return {"flexion": table_dict}

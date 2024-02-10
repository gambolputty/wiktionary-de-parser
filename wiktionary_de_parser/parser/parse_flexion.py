import re

from wiktionary_de_parser.models import ParseFlexionResult
from wiktionary_de_parser.parser import Parser

WANTED_TABLE_NAMES = [
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


class ParseFlexion(Parser):
    name = "flexion"

    @staticmethod
    def find_table(text):
        re_string = "({{(" + "|".join(WANTED_TABLE_NAMES) + ")[^}]+}})"
        match_table = re.search(re_string, text)

        if not match_table:
            return

        return match_table.group(1)

    @staticmethod
    def parse_table_values(table_string):
        table_values = re.findall(
            r"(?:\|([^=\n]+)=([^\n|}]+))+?", table_string, re.MULTILINE
        )

        if not table_values:
            return

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

        if result.keys():
            return result

    @classmethod
    def parse(cls, wikitext: str):
        table_string = cls.find_table(wikitext)
        result = None

        if table_string:
            table_dict = cls.parse_table_values(table_string)
            if table_dict:
                result = table_dict

        return result

    def run(self) -> ParseFlexionResult:
        return self.parse(self.entry.wikitext)

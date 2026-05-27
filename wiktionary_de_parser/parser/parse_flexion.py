import re

import mwparserfromhell

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
        """Locate the first Übersicht-table template in the wikitext.

        Uses brace-balanced parsing so nested templates inside table cells
        (e.g. `|Genus={{m}}`, `|Bild=…{{Per-Deutschlandradio|…}}`) don't
        truncate the result.
        """
        parsed = mwparserfromhell.parse(text)
        for tmpl in parsed.filter_templates():
            if str(tmpl.name).strip() in WANTED_TABLE_NAMES:
                return str(tmpl)
        return None

    @staticmethod
    def parse_table_values(table_string):
        # Walk the parsed template instead of regex-matching |key=value pairs.
        # Regex would also catch |key=val pairs sitting *inside* a nested
        # template like {{Per-Deutsche Welle|Autor=...|Titel=...}} embedded in
        # the |Bild= caption, producing junk fields ("Autor", "Titel", ...).
        parsed = mwparserfromhell.parse(table_string)
        top_templates = parsed.filter_templates(recursive=False)
        if not top_templates:
            return None
        table_tmpl = top_templates[0]

        result = {}
        for param in table_tmpl.params:
            # Skip positional params — they show up when an editor writes
            # `|Bild=foo.jpg|mini|1|caption` (mini/1/caption are positional).
            if not param.showkey:
                continue

            key = str(param.name).strip()

            # Drop noise keys: empty, numeric (broken Übersicht with |3=…|2=…),
            # image fields, and Flexion/Konjugation links that aren't values.
            if not key or key.isdigit():
                continue
            if key.startswith("Bild"):
                continue
            if key in ("Flexion", "Weitere Konjugationen"):
                continue

            # Clean text: strip comments, refs, &nbsp;. DOTALL so a multi-line
            # `<ref>line1\nline2</ref>` inside a cell value is removed in full
            # rather than leaving the ref body and a stray newline behind.
            # The paired form requires the closing tag name to match the
            # opening one (\\1), otherwise a self-closing `<ref name="x"/>`
            # would greedily pair with a later unrelated `</sup>` and delete
            # everything between.
            text = str(param.value).strip()
            text = text.replace("&nbsp;", " ")
            text = re.sub(
                r"<(\w+)[^>]*>.*?</\1>|<[^>]+/>|<[^>]+>",
                " ",
                text,
                flags=re.DOTALL,
            )
            text = text.strip()

            # Genus normalization. Plural-only words sometimes carry "0" or
            # other placeholder values — drop them.
            # https://de.wiktionary.org/wiki/Wiktionary:Teestube/Archiv/2015/11#Genus_in_der_Flexionstabelle_bei_Pluralw%C3%B6rtern
            if key in ["Genus", "Genus 1", "Genus 2", "Genus 3", "Genus 4"]:
                text = text.lower()
                if text not in ["f", "m", "n"]:
                    continue

            if not text or text in ("—", "-", "–", "−", "?"):
                continue

            result[key] = text

        return result or None

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

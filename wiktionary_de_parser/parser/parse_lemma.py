import re

import mwparserfromhell
from mwparserfromhell.nodes.template import Template

from wiktionary_de_parser.models import Lemma, ParseLemmaResult
from wiktionary_de_parser.parser import Parser


class ParseLemma(Parser):
    name = "lemma"

    @staticmethod
    def parse_lemma(text):
        match_template = re.search(r"({{Grundformverweis.+)", text)

        if not match_template:
            return

        template_text = match_template.group(1)
        parsed = mwparserfromhell.parse(template_text)
        template = parsed.nodes[0] if parsed.nodes else None

        if (
            template
            and isinstance(template, Template)
            and template.name.startswith("Grundformverweis")
        ):
            attribute = template.get(1, None)
            if attribute:
                # remove "#" and everything after
                return re.sub(r"\#.+", "", str(attribute.value))  # type: ignore

    @classmethod
    def parse(cls, page_name: str, wikitext: str):
        found_lemma = page_name
        inflected = False

        parsed = cls.parse_lemma(wikitext)
        if parsed:
            found_lemma = parsed
            inflected = True

        return dict(lemma=found_lemma, inflected=inflected)

    def run(self) -> ParseLemmaResult:
        """
        Grundformverweis
        Von einer Deklination spricht man beim Beugen von Substantiven und den
        dazugehörigen Adjektiven und Pronomen (Nominalflexion),
        von einer Konjugation beim Beugen eines Verbs (Verbalflexion).

        Reference:
        https://de.wiktionary.org/wiki/Kategorie:Flektierte_Form_(Deutsch)
        https://de.wiktionary.org/wiki/Vorlage:Grundformverweis_Konj
        https://de.wiktionary.org/wiki/Vorlage:Grundformverweis_Dekl
        https://de.wiktionary.org/wiki/Vorlage:Grundformverweis (deprecated)
        """
        result = self.parse(self.entry.page.name, self.entry.wikitext)
        return Lemma(**result)  # type: ignore

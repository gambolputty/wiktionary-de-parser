import re

import mwparserfromhell
from mwparserfromhell.nodes.template import Template

from wiktionary_de_parser.models import (
    Lemma,
    ParseLemmaResult,
    ReferenceType,
)
from wiktionary_de_parser.parser import Parser


class ParseLemma(Parser):
    name = "lemma"

    @staticmethod
    def parse_lemma(text) -> tuple[str | None, ReferenceType]:
        """
        Parse lemma references from German Wiktionary wikitext.

        Extracts the target lemma and reference type from two template types:
        1. {{Grundformverweis}} - Inflected forms (declension/conjugation)
        2. {{Lemmaverweis}} - Variant forms (alternative spellings, etc.)

        Args:
            text: The wikitext to parse

        Returns:
            Tuple of (target_lemma, reference_type):
            - (None, NONE) if no reference template found
            - (str, INFLECTED) if Grundformverweis template found
            - (str, VARIANT) if Lemmaverweis template found

        Examples:
            {{Grundformverweis|gehören}} → ("gehören", INFLECTED)
            {{Lemmaverweis|mild}} → ("mild", VARIANT)
            No template → (None, NONE)
        """
        # Search for either Grundformverweis or Lemmaverweis templates
        match = re.search(r"({{(?:Grundformverweis|Lemmaverweis).+)", text)
        if not match:
            return None, ReferenceType.NONE

        template_text = match.group(1)
        parsed = mwparserfromhell.parse(template_text)
        template = (
            parsed.nodes[0]
            if parsed.nodes and isinstance(parsed.nodes[0], Template)
            else None
        )

        if not template:
            return None, ReferenceType.NONE

        # Determine reference type based on template name
        template_name = str(template.name).strip()
        if template_name.startswith("Grundformverweis"):
            ref_type = ReferenceType.INFLECTED
        elif template_name.startswith("Lemmaverweis"):
            ref_type = ReferenceType.VARIANT
        else:
            return None, ReferenceType.NONE

        # Extract the target lemma from the first template parameter
        attribute = template.get(1, None)
        if attribute:
            # Remove anchor (#) and everything after it
            lemma_target = re.sub(r"\#.+", "", str(attribute.value))
            return lemma_target, ref_type

        return None, ReferenceType.NONE

    @classmethod
    def parse(cls, page_name: str, wikitext: str) -> Lemma:
        """
        Parse lemma information from a Wiktionary entry.

        Args:
            page_name: The name of the Wiktionary page
            wikitext: The wikitext content of the entry

        Returns:
            Lemma object with canonical form and reference type
        """
        found_lemma = page_name
        reference_type = ReferenceType.NONE

        parsed_lemma, ref_type = cls.parse_lemma(wikitext)
        if parsed_lemma:
            found_lemma = parsed_lemma
            reference_type = ref_type

        return Lemma(lemma=found_lemma, reference_type=reference_type)

    def run(self) -> ParseLemmaResult:
        """
        Parse lemma references from Wiktionary entries.

        Supports two types of references:

        1. Grundformverweis (inflected forms):
           - Declination: nouns, adjectives, pronouns
           - Conjugation: verbs
           Examples:
           - "gehörte" → "gehören" (verb conjugation)
           - "Häuser" → "Haus" (noun declension)

        2. Lemmaverweis (variant forms):
           - Alternative spellings: "Geografie" → "Geographie"
           - Regional variants: "Kücken" → "Küken"
           - Pronunciation variants: "milde" → "mild"

        References:
        - https://de.wiktionary.org/wiki/Kategorie:Flektierte_Form_(Deutsch)
        - https://de.wiktionary.org/wiki/Vorlage:Grundformverweis_Konj
        - https://de.wiktionary.org/wiki/Vorlage:Grundformverweis_Dekl
        - https://de.wiktionary.org/wiki/Vorlage:Grundformverweis (deprecated)
        - https://de.wiktionary.org/wiki/Vorlage:Lemmaverweis
        - https://de.wiktionary.org/wiki/Hilfe:Lemmaverweis
        """
        return self.parse(self.entry.page.name, self.entry.wikitext)

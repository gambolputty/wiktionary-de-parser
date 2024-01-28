import re
from dataclasses import dataclass

import mwparserfromhell
from mwparserfromhell.nodes.template import Template


@dataclass
class LemmaInfo:
    lemma: str
    inflected: bool


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
            return re.sub(r"\#.+", "", str(attribute.value))


def init(title: str, text: str, current_record) -> LemmaInfo:
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

    found_lemma = title
    inflected = False

    parsed = parse_lemma(text)
    if parsed:
        found_lemma = parsed
        inflected = True

    return LemmaInfo(lemma=found_lemma, inflected=inflected)

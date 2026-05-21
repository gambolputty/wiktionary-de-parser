from enum import Enum

from pydantic import BaseModel
from typing_extensions import TypedDict


class WiktionaryPage(BaseModel):
    page_id: int
    name: str
    wikitext: str | None
    redirect_to: str | None = None


class WiktionaryPageEntry(BaseModel):
    page: WiktionaryPage
    index: int
    wikitext: str


class Language(BaseModel):
    lang: str | None
    lang_code: str | None


class ReferenceType(str, Enum):
    """
    Type of lemma reference in German Wiktionary.

    Reference types distinguish different ways a word entry points to another:
    - NONE: Standalone lemma, no reference to another word
    - INFLECTED: Inflected/declined form ({{Grundformverweis}})
      Examples: "gehörte" → "gehören" (verb conjugation),
                "Häuser" → "Haus" (noun declension)
    - VARIANT: Alternative form or variant ({{Lemmaverweis}})
      Examples: "milde" → "mild" (pronunciation variant),
                "Geografie" → "Geographie" (alternative spelling),
                "Kücken" → "Küken" (regional variant)

    References:
    - https://de.wiktionary.org/wiki/Vorlage:Grundformverweis
    - https://de.wiktionary.org/wiki/Vorlage:Lemmaverweis
    """

    NONE = "none"
    INFLECTED = "inflected"
    VARIANT = "variant"


class Lemma(BaseModel):
    """
    Lemma information for a Wiktionary entry.

    Attributes:
        lemma: The canonical form of the word. If the entry contains a
               reference template (Grundformverweis or Lemmaverweis), this
               points to the target lemma. Otherwise, it's the page name.
        reference_type: Type of reference (NONE, INFLECTED, or VARIANT)
    """

    lemma: str
    reference_type: ReferenceType = ReferenceType.NONE


class EtymologyType(str, Enum):
    """
    Word formation type detected in the Herkunft section.

    The parser picks the most specific marker present. A
    Determinativkompositum maps to COMPOUND (not the generic Zusammensetzung);
    an "Ableitung (Movierung)" maps to MOVIERUNG (not generic DERIVATION).

    - COMPOUND: Determinativkompositum, Kompositum, Zusammensetzung,
      Wortverbindung, Zusammenbildung, Possessivkompositum, Zusammenrückung,
      Univerbierung.
    - DERIVATION: Ableitung, Derivation, Rückbildung, Diminutiv. Also covers
      prefixed verbs handled via the {{Verbherkunft|W=Partikel}} template.
    - MOVIERUNG: Geschlechts-Movierung (a special derivation), marked inline
      as [[Ableitung]] ([[Motion]], [[Movierung]]) or as "weibliche Form von".
    - CONVERSION: Konversion, Substantivierung, Nominalisierung — word-class
      change without explicit derivational morpheme.
    - LOANWORD: Entlehnung, Lehnwort, Lehnübersetzung, Erbwort, and free-text
      etymologies like "von [lang] X" or "mittelhochdeutsch X". Note that
      Erbwörter (native inheritance) fall under LOANWORD too.
    - SHORTENING: Kurzwort, Kurzform, Akronym, Initialwort, Abkürzung,
      Kofferwort, Kontamination.
    - VARIANT: Nebenform, Schreibvariante.
    - UNKNOWN: Section exists but no recognised pattern matched. The outer
      result is None when no Herkunft section is present at all.
    """

    COMPOUND = "compound"
    DERIVATION = "derivation"
    MOVIERUNG = "movierung"
    CONVERSION = "conversion"
    LOANWORD = "loanword"
    SHORTENING = "shortening"
    VARIANT = "variant"
    UNKNOWN = "unknown"


class EtymologyResult(BaseModel):
    """
    Structured representation of the {{Herkunft}} section of a Wiktionary entry.

    Components are wikilink targets (lemma form, not surface form). Fugenelement
    is reported with surrounding hyphens stripped ("-s-" → "s"). For multi-sense
    sections only the first sense block is captured. For loanword chains
    ("über französisch X aus lateinisch Y"), source_language reports the
    deepest source ("Latein").
    """

    type: EtymologyType
    components: list[str] = []
    fugenelement: str | None = None
    suffix: str | None = None
    prefix: str | None = None
    source_language: str | None = None


ParseEtymologyResult = EtymologyResult | None

ParseFlexionResult = dict | None
ParseIpaResult = list[str] | None
ParseLanuageResult = Language
ParseLemmaResult = Lemma
ParsePosResult = dict[str, list[str]] | None
ParseRhymesResult = list[str] | None
ParseHyphenationResult = list[str] | None


class MeaningDict(TypedDict, total=False):
    text: str
    tags: list[str]
    raw_tags: list[str]
    sublist: list["MeaningDict"]


ParseMeaningsResults = list[MeaningDict] | None


class ParsedWiktionaryPageEntry(BaseModel):
    name: str
    hyphenation: ParseHyphenationResult
    flexion: ParseFlexionResult
    ipa: ParseIpaResult
    language: ParseLanuageResult
    lemma: ParseLemmaResult
    pos: ParsePosResult
    rhymes: ParseRhymesResult
    etymology: ParseEtymologyResult = None
    meanings: ParseMeaningsResults | None = None

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
    meanings: ParseMeaningsResults | None = None

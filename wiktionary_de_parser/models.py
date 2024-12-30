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


class Lemma(BaseModel):
    lemma: str
    inflected: bool


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

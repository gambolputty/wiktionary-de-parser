from typing import Any

from pydantic import BaseModel


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
ParseMeaningsResults = Any


class ParsedWiktionaryPageEntry(BaseModel):
    name: str
    hyphenation: ParseHyphenationResult
    flexion: ParseFlexionResult
    ipa: ParseIpaResult
    language: ParseLanuageResult
    lemma: ParseLemmaResult
    pos: ParsePosResult
    rhymes: ParseRhymesResult
    meanings: ParseMeaningsResults

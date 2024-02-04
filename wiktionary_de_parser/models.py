from mwparserfromhell.wikicode import Wikicode
from pydantic import BaseModel, ConfigDict


class WiktionaryPage(BaseModel):
    page_id: int
    name: str
    wikitext: str | None
    redirect_to: str | None = None


class WiktionaryPageEntry(BaseModel):
    page: WiktionaryPage
    index: int
    wikitext: str
    wikicode: Wikicode

    model_config = ConfigDict(arbitrary_types_allowed=True)


class Language(BaseModel):
    lang: str
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
ParseSyllablesResult = list[str] | None


class ParsedWiktionaryPageEntry(BaseModel):
    name: str
    flexion: ParseFlexionResult
    ipa: ParseIpaResult
    language: ParseLanuageResult
    lemma: ParseLemmaResult
    pos: ParsePosResult
    rhymes: ParseRhymesResult
    syllables: ParseSyllablesResult

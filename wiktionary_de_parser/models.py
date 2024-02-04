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


ParseFlexionResult = dict | None
ParseIpaResult = list[str] | None
ParseLanuageResult = dict[str, str | None]
ParseLemmaResult = dict[str, str | bool]
ParsePosResult = dict[str, list[str]] | None
ParseRhymesResult = list[str] | None
ParseSyllablesResult = list[str] | None


class ParsedWiktionaryPageEntry(BaseModel):
    flexion: ParseFlexionResult
    ipa: ParseIpaResult
    language: ParseLanuageResult
    lemma: ParseLemmaResult
    pos: ParsePosResult
    rhymes: ParseRhymesResult
    syllables: ParseSyllablesResult

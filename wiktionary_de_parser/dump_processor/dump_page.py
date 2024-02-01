from mwparserfromhell.wikicode import Wikicode
from pydantic import BaseModel, ConfigDict


class WiktionaryPage(BaseModel):
    page_id: int
    name: str
    wikitext: str | None
    redirect_to: str | None = None


class WiktionaryPageEntry(BaseModel):
    index: int
    wikicode: Wikicode
    page: WiktionaryPage

    model_config = ConfigDict(arbitrary_types_allowed=True)

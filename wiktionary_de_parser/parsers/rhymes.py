"""Extract rhyme strings from the Aussprache section.

Mirrors ``parse_ipa``: the first comma-separated chain of ``{{Reim}}``
templates directly following a ``{{Reime}}`` is captured. Regional,
dialectal or grammatically inflected variants stop the walk.
"""

from __future__ import annotations

from wiktionary_de_parser._wikitext import walk_template_chain
from wiktionary_de_parser.entry import WiktionaryEntry


def parse(entry: WiktionaryEntry) -> list[str] | None:
    parsed = entry.pronunciation_wikicode
    if parsed is None:
        return None
    return walk_template_chain(parsed, "Reime", "Reim") or None

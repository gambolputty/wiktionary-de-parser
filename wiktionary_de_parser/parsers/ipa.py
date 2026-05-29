"""Extract IPA pronunciation from the Aussprache section.

Both ``{{Lautschrift}}`` (verified) and ``{{Lautschrift?}}`` (unverified)
carry IPA. The walker treats whichever one is not the current target as
ignorable rather than as a chain-terminating "other template" — otherwise
an interleaved ``{{Lautschrift?}}`` would silently drop trailing verified
Lautschrift values.

Reference: https://de.wiktionary.org/wiki/Hilfe:Aussprache
"""

from __future__ import annotations

from mwparserfromhell.wikicode import Wikicode

from wiktionary_de_parser._wikitext import walk_template_chain
from wiktionary_de_parser.entry import WiktionaryEntry

# {{Lautschrift}} (verified) and {{Lautschrift?}} (unverified) both carry
# IPA; whichever is not the current target is an ignorable no-op rather
# than a chain-terminating "other template" — otherwise an interleaved
# {{Lautschrift?}} would silently drop trailing verified values.
_IPA_TEMPLATE_NAMES = frozenset({"Lautschrift", "Lautschrift?"})


def _walk_ipa_chain(parsed: Wikicode) -> list[str] | None:
    """First chain of verified ``{{Lautschrift}}`` after ``{{IPA}}``, or
    the unverified ``{{Lautschrift?}}`` chain when no verified one exists.

    Examples (★ marks kept values):
        :{{IPA}} ★{{Lautschrift|ˈkøːnɪç}}, ★{{Lautschrift|ˈkøːnɪk}}
        :{{IPA}} ★{{Lautschrift|ˈdʏsəlˌdɔʁfɐ}}, ''regional:''
                 {{Lautschrift|ˈdʏsəlˌdɔχfɔʶ}}
    """
    result = walk_template_chain(
        parsed, "IPA", "Lautschrift", ignorable=_IPA_TEMPLATE_NAMES
    )
    if not result:
        result = walk_template_chain(
            parsed, "IPA", "Lautschrift?", ignorable=_IPA_TEMPLATE_NAMES
        )
    return result or None


def parse(entry: WiktionaryEntry) -> list[str] | None:
    parsed = entry.pronunciation_wikicode
    if parsed is None:
        return None
    return _walk_ipa_chain(parsed)

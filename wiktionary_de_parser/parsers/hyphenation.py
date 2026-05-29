"""Extract syllable hyphenation ("Worttrennung") from a Wiktionary entry.

The hyphenation paragraph lists the lemma split by middle dots
(``·``). It can also contain commas separating multiple forms
(``ge·sagt, ge·tan``) — but commas can legitimately appear *inside*
the lemma (chemical names: ``1,2,3-Propan``), so we cannot split on
commas blindly. Instead we walk the paragraph char-by-char looking
for the title shape.

Reference: https://de.wiktionary.org/wiki/Hilfe:Worttrennung
"""

from __future__ import annotations

import re

from wiktionary_de_parser._wikitext import strip_html_tags
from wiktionary_de_parser.entry import WiktionaryEntry


def _parse_body(name: str, paragraph: str) -> list[str] | None:
    """Char-walk extraction. Tolerates a long list of edge cases:

    - Affix markers on the lemma — ``auto-`` (prefix), ``-ow`` (suffix),
      ``-s-`` (fugenelement) — kept as semantic markers, re-attached
      after splitting so callers can tell an affix entry apart.
    - False mid dot at the beginning that breaks the walk
      (``:·nutz·lo·se``) is stripped.
    - Wrapper templates like ``{{Polytonisch|ἡ}}`` leave behind ``{|}``
      tokens after the walk — stripped post hoc.
    - ``", "`` as a word separator (``gesagt, getan`` → two words).
      Bare commas inside the lemma (``1,2,3-Propan``) and bare dots
      (``Web 2.0``) are preserved.
    - Single-char lemmas (``"A"``) trigger an off-by-one in the walk
      that pulls in the next char (``"A,"``); we trim trailing
      punctuation, but only chars the lemma itself doesn't end with —
      otherwise ``"Mr."`` and ``"etc."`` would lose their trailing dot.
    """
    has_prefix_marker = name.endswith("-")
    has_suffix_marker = name.startswith("-")

    paragraph = paragraph.lstrip(":·")

    title_index = 0
    start_index = -1
    end_index = -1
    last_title_index = len(name) - 1
    last_paragraph_index = len(paragraph) - 1
    for index, char in enumerate(paragraph):
        if start_index == -1:
            if paragraph[index:].replace("·", "").startswith(name):
                start_index = index
                end_index = index
            continue

        end_index += 1
        if char == "·":
            continue

        title_index += 1
        if (
            title_index >= last_title_index
            or char != name[title_index]
            or index == last_paragraph_index
        ):
            end_index += 1
            break

    if start_index == -1:
        return None

    clean = paragraph[start_index:end_index]
    clean = re.sub(r"[{}|]", "", clean)
    clean = re.sub(r"\s*,\s+", " ", clean)

    trailing = "".join(c for c in ",.;:" if not name.endswith(c))
    if trailing:
        clean = clean.rstrip(trailing)

    result = list(filter(None, re.split(r"\s|·|-", clean)))
    if not result:
        return None

    if has_suffix_marker:
        result[0] = "-" + result[0]
    if has_prefix_marker:
        result[-1] = result[-1] + "-"
    return result


def parse(entry: WiktionaryEntry) -> list[str] | None:
    body = entry.sections.get("Worttrennung")
    if body is None:
        return None
    # The section body comes from find_sections() which already strips
    # refs — so we only need to strip HTML and run the char-walk.
    body = strip_html_tags(body)
    return _parse_body(entry.page_name, body)

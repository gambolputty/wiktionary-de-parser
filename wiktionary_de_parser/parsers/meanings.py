"""Extract meanings ("Bedeutungen") from a Wiktionary entry.

Uses ``wikitextparser`` here because its ``WikiList`` / ``plain_text``
APIs map cleanly to the hierarchical sense structure (numbered items,
sub-items, nested ``[a]`` lists). ``mwparserfromhell`` is excellent at
template traversal but doesn't have a native list abstraction.

For everything else in the parser pipeline ``wikitextparser`` is no
longer used.
"""

from __future__ import annotations

import wikitextparser as wtp

from wiktionary_de_parser.entry import WiktionaryEntry
from wiktionary_de_parser.models import Meaning
from wiktionary_de_parser.utils.meanings.wiki_list import (
    WikiList,
    WikiListItem,
)


def _parse_wiki_lists(wiki_lists) -> WikiList | None:
    """Recursively assemble a ``WikiList`` from ``wtp.WikiList`` objects.

    Two subtle behaviours that real Wiktionary pages depend on:

    - List items may have empty text and tags but a non-empty sublist
      (see https://de.wiktionary.org/wiki/Skizze). The item is kept
      only when at least one of the three is populated.
    - Lists can be nested ≥3 levels deep (e.g.
      https://de.wiktionary.org/wiki/wegen). The function recurses on
      ``wiki_list.sublists(index)``.
    - When a top-level item with pattern ``\\*`` is followed by a
      non-``\\*`` item, that next item is attached as a sublist of the
      previous one.
    """
    list_items: list[WikiListItem] = []

    for wiki_list in wiki_lists:
        for index, raw_list_item in enumerate(wiki_list.items):
            sublists = wiki_list.sublists(index)
            sublist_parsed = _parse_wiki_lists(sublists) if sublists else None
            new_item = WikiListItem(
                wikitext=raw_list_item,
                pattern=wiki_list.pattern,
                sublist=sublist_parsed,
            )

            if not new_item.text and not new_item.tags and not new_item.sublist:
                continue

            if (
                list_items
                and list_items[-1].pattern == "\\*"
                and new_item.pattern != "\\*"
            ):
                last_item = list_items[-1]
                if not last_item.sublist:
                    last_item.sublist = WikiList(items=[])
                last_item.sublist.items.append(new_item)
            else:
                list_items.append(new_item)

    return WikiList(items=list_items) if list_items else None


def parse(entry: WiktionaryEntry) -> list[Meaning] | None:
    body = entry.sections.get("Bedeutungen")
    if body is None:
        return None
    parsed = wtp.parse(body)
    wiki_list = _parse_wiki_lists(parsed.get_lists())
    if wiki_list is None:
        return None
    return wiki_list.export()

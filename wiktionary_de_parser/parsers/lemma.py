"""Extract form-reference templates that point to a canonical lemma.

Two template families are recognised:

1. ``{{Grundformverweis…}}`` — inflected forms (declension/conjugation).
   ``gehörte`` → ``gehören``,  ``Häuser`` → ``Haus``
2. ``{{Lemmaverweis}}`` / ``{{Alte Schreibweise}}`` — variants
   (alternative spelling, regional, pronunciation).
   ``Geografie`` → ``Geographie``,  ``Kücken`` → ``Küken``

Only *top-level* nodes count: a reference template buried in body prose
or inside a ``<ref>…</ref>`` citation must NOT hijack the page lemma.
By Wiktionary convention these templates sit at the very top of the
entry, so we cap how much wikitext we parse for the cheap path.

References:
- https://de.wiktionary.org/wiki/Vorlage:Grundformverweis
- https://de.wiktionary.org/wiki/Vorlage:Lemmaverweis
- https://de.wiktionary.org/wiki/Vorlage:Alte_Schreibweise
"""

from __future__ import annotations

import re

import mwparserfromhell
from mwparserfromhell.nodes.comment import Comment
from mwparserfromhell.nodes.template import Template
from mwparserfromhell.nodes.text import Text

from wiktionary_de_parser._wikitext import (
    resolve_positional_params,
    strip_comments,
)
from wiktionary_de_parser.entry import WiktionaryEntry
from wiktionary_de_parser.models import LemmaReference, ReferenceType

# A trailing section anchor (``Geographie#Übersetzungen``) is not part of
# the lemma target.
_ANCHOR_RE = re.compile(r"\#.+")


def _strip_anchor(value: str) -> str:
    return _ANCHOR_RE.sub("", value).strip()


def parse_lemma(text: str) -> tuple[str | None, ReferenceType | None]:
    """Return ``(target_lemma, reference_type)`` or ``(None, None)``."""
    # Walk top-level nodes only — a form-reference template nested
    # inside body prose or a <ref>…</ref> citation must not hijack the
    # page lemma. By Wiktionary convention these templates always sit
    # at the top of the entry.
    parsed = mwparserfromhell.parse(text)
    template = None
    for node in parsed.nodes:
        if not isinstance(node, Template):
            continue
        name = str(node.name).strip()
        if name.startswith(
            ("Grundformverweis", "Lemmaverweis", "Alte Schreibweise")
        ):
            template = node
            break

    if template is None:
        return None, None

    template_name = str(template.name).strip()
    if template_name.startswith("Grundformverweis"):
        ref_type = ReferenceType.INFLECTED
    else:
        ref_type = ReferenceType.VARIANT

    positional_map = resolve_positional_params(template)

    # Walk positionals; pick the first that resolves to a non-empty lemma.
    # Three patterns need special handling:
    #  - the param wraps the target in a nested template
    #    ``{{linkZiel|is|kaldur}}`` — extract the inner template's last
    #    positional.
    #  - the param is a section anchor ``#Übersetzungen`` — strips to "",
    #    fall through to the next positional.
    #  - the param is genuinely empty (``{{Alte Schreibweise||Reform 1996}}``)
    #    — return None, don't accept the next positional as the lemma
    #    (it's a marker, not a target).
    for index in sorted(positional_map):
        param = positional_map[index]
        value = param.value
        raw = strip_comments(str(value)).strip()

        if not raw:
            return None, None

        # Pure nested-template wrapper: only a single template node with
        # no surrounding content. Whitespace-only Text nodes and HTML
        # comments are filtered out; mixed text+template like
        # ``stem-{{X|y}}`` falls through to the whole-value path below.
        nontrivial_nodes = [
            n
            for n in value.nodes
            if not isinstance(n, Comment)
            and not (isinstance(n, Text) and not n.value.strip())
        ]
        if len(nontrivial_nodes) == 1 and isinstance(
            nontrivial_nodes[0], Template
        ):
            inner_positional = [
                p for p in nontrivial_nodes[0].params if not p.showkey
            ]
            if inner_positional:
                candidate = _strip_anchor(str(inner_positional[-1].value))
                if candidate:
                    return candidate, ref_type
            # Wrapper yielded nothing usable — try the next positional.
            continue

        candidate = _strip_anchor(raw)
        if candidate:
            return candidate, ref_type

    return None, None


# Cheap string-level prefilter — skip mwparserfromhell entirely when no
# reference template appears anywhere in the entry. Roughly 60 % of
# entries carry no form reference at all, so this short-circuit alone
# avoids most of the per-entry parse cost.
#
# Parse the whole entry, not just a leading prefix: ~2 % of entries put
# the reference past the first 800 bytes (max observed ≈ 16 KB), common
# in `Deklinierte Form` pages that list Worttrennung / Aussprache /
# Grammatische Merkmale before the Grundformverweis.
_HAS_REF_RE = re.compile(
    r"\{\{(?:Grundformverweis|Lemmaverweis|Alte Schreibweise)"
)


def parse(entry: WiktionaryEntry) -> LemmaReference | None:
    """Return the form reference or ``None`` when the entry has none."""
    if not _HAS_REF_RE.search(entry.wikitext):
        return None

    target, ref_type = parse_lemma(entry.wikitext)
    # ref_type is always set whenever target is — they originate from the
    # same matched template — so guarding on target alone is sufficient.
    if target:
        return LemmaReference(target=target, type=ref_type)
    return None

"""Shared wikitext utilities used by every parser.

These primitives stay regex- or string-based wherever possible:
``mwparserfromhell.parse()`` is the dominant cost in the pipeline, so we
keep it confined to the narrowest possible slices of wikitext.
"""

from __future__ import annotations

import re

from mwparserfromhell.nodes.extras.parameter import Parameter
from mwparserfromhell.nodes.tag import Tag
from mwparserfromhell.nodes.template import Template
from mwparserfromhell.nodes.text import Text
from mwparserfromhell.wikicode import Wikicode

# `<ref>…</ref>` blocks can span multiple lines and may contain wikitext
# (`\n{{Lit-Foo}}`) that would otherwise terminate a section capture early.
# Self-closing forms are stripped first so the paired pattern's open-tag
# body can stay simple — that also tolerates attribute values with `/`
# (e.g. `<ref name="https://…/x">`).
_REF_SELF_CLOSING_RE = re.compile(r"<ref[^>]*/>")
_REF_BLOCK_RE = re.compile(r"<ref[^>]*>.*?</ref>", re.DOTALL)
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

# Wortart-header template flavours that count as a real header. The set
# is the single source of truth for membership checks (language/POS
# parsers); the regex is the text-matching form used by the entry
# splitter. Both must stay in lock-step.
WORTART_TEMPLATE_NAMES = frozenset({"Wortart", "Wortart-Test"})
WORTART_TEMPLATE_NAME_RE = r"{{Wortart(?:-Test)?"


def strip_refs(text: str) -> str:
    """Remove ``<ref …/>`` and ``<ref …>…</ref>`` blocks."""
    text = _REF_SELF_CLOSING_RE.sub("", text)
    return _REF_BLOCK_RE.sub("", text)


def strip_comments(text: str) -> str:
    """Remove ``<!-- … -->`` HTML comments (DOTALL, multi-line)."""
    return _COMMENT_RE.sub("", text)


def strip_html_tags(text: str) -> str:
    """Replace all HTML tags with spaces (content kept)."""
    return _HTML_TAG_RE.sub(" ", text)


# Known German Wiktionary section headings (Textbausteine). The section
# scanner is restricted to these names on purpose: a single non-overlapping
# regex pass would otherwise mistake an ordinary on-its-own-line template
# (``{{Wort des Jahres|…}}``, ``{{erweitern|…}}``, ``{{Slowenisch Pronomen}}``)
# for a section heading and let its "body" swallow the real section that
# follows. Restricting to the whitelist prevents that.
#
# https://de.wiktionary.org/wiki/Hilfe:Formatvorlage
KNOWN_SECTIONS = frozenset(
    {
        "Nebenformen",
        "Alte Schreibweise",
        "Alte Schreibweisen",
        "Alternative Schreibweisen",
        "Nicht mehr gültige Schreibweisen",
        "Worttrennung",
        "In arabischer Schrift",
        "In kyrillischer Schrift",
        "In lateinischer Schrift",
        "Vokalisierung",
        "Umschrift",
        "Aussprache",
        "Grammatische Merkmale",
        "Anmerkung",
        "Anmerkungen",
        "Anmerkung zur Verwendung",
        "Bedeutungen",
        "Abkürzungen",
        "Symbole",
        "Herkunft",
        "Synonyme",
        "Sinnverwandte Wörter",
        "Sinnverwandte Zeichen",
        "Gegenwörter",
        "Weibliche Wortformen",
        "Männliche Wortformen",
        "Sächliche Wortformen",
        "Verkleinerungsformen",
        "Vergrößerungsformen",
        "Koseformen",
        "Kurzformen",
        "Oberbegriffe",
        "Unterbegriffe",
        "Teilbegriffe",
        "Meronyme",
        "Holonyme",
        "Umfeld",
        "Verbandsbegriffe",
        "Beispiele",
        "Redewendungen",
        "Sprichwörter",
        "Charakteristische Wortkombinationen",
        "Wortbildungen",
        "Wortfamilie",
        "Entlehnungen",
        "Übersetzungen",
        "Referenzen",
        "Quellen",
        "Ähnlichkeiten",
        "Vergleiche",
    }
)

# The whitelist must live INSIDE the regex (not as a post-match filter):
# ``finditer`` is non-overlapping, so if the pattern matched an arbitrary
# template like ``{{Slowenisch Pronomen|…}}`` its body capture would
# already have swallowed the following real section before a post-filter
# could reject it. Longer names are listed first so e.g.
# "Alte Schreibweisen" wins over "Alte Schreibweise".
_SECTION_NAME_ALT = "|".join(
    re.escape(s) for s in sorted(KNOWN_SECTIONS, key=len, reverse=True)
)
_SECTION_RE = re.compile(
    r"{{(?P<name>"
    + _SECTION_NAME_ALT
    + r")(?:\|[^}\n]*)?}}[ \t]*\n(?P<body>.*?)(?=\n{{|\Z)",
    re.DOTALL,
)


def find_sections(wikitext: str) -> dict[str, str]:
    """Return a mapping of section heading → section body.

    Only headings in :data:`KNOWN_SECTIONS` are recognised (see the note
    there for why). Comments and refs are stripped first: a
    ``\\n{{Lit-Foo}}`` inside a citation must not terminate a body capture
    early, and a section parked inside ``<!-- … -->`` must not be parsed
    at all.
    """
    if not wikitext:
        return {}
    wikitext = strip_comments(strip_refs(wikitext))
    sections: dict[str, str] = {}
    for m in _SECTION_RE.finditer(wikitext):
        # Keep first occurrence — duplicate headings are extremely rare
        # and the first one is the canonical section by convention.
        sections.setdefault(m.group("name").strip(), m.group("body"))
    return sections


def extract_first_positional_value(template: Template) -> str | None:
    """First non-empty positional parameter value of a template.

    Named params (``spr=de``, ``lang=pt``, …) and empty positional slots
    are skipped. HTML markup inside the value is stripped, ellipses
    (``…``) are removed. Used by ``{{Lautschrift}}``/``{{Reim}}`` and
    friends.
    """
    for param in template.params:
        if param.showkey:
            continue
        value = str(param.value).replace("…", "")
        value = _HTML_TAG_RE.sub("", value).strip()
        if value:
            return value
    return None


_CHAIN_SEPARATORS = frozenset({",", ";"})


def walk_template_chain(
    parsed: Wikicode,
    trigger: str,
    target: str,
    *,
    ignorable: frozenset[str] = frozenset(),
) -> list[str]:
    """Collect first-positional values from the first separator-joined chain
    of ``{{<target>}}`` templates that directly follows a ``{{<trigger>}}``.

    Powers both the IPA walk (``{{IPA}}`` → ``{{Lautschrift}}``) and the
    rhymes walk (``{{Reime}}`` → ``{{Reim}}``); they differ only in their
    template names and in IPA's ``ignorable`` set. Regional, dialectal or
    inflected variants are intentionally skipped — they introduce
    non-separator text or non-matching templates that stop the walk.

    ``ignorable`` template names are treated as no-ops rather than as
    chain-terminating "other" templates (IPA uses this so an interleaved
    ``{{Lautschrift?}}`` doesn't silently drop trailing verified values).
    A text node that is pure whitespace is neutral; one equal to a member
    of ``separators`` joins the chain; anything else stops the walk once at
    least one value has been collected. ``<ref>`` tags never end the chain.
    """
    found: list[str] = []
    found_trigger = False

    for node in parsed.nodes:
        if not found_trigger:
            # mwparserfromhell keeps template-name whitespace (`{{ IPA }}`
            # → name == ' IPA '), so always compare the stripped form.
            if isinstance(node, Template) and str(node.name).strip() == trigger:
                found_trigger = True
            continue

        if isinstance(node, Template):
            node_name = str(node.name).strip()
            if node_name == target:
                value = extract_first_positional_value(node)
                if value and value not in found:
                    found.append(value)
                continue
            if node_name in ignorable:
                continue

        if isinstance(node, Text):
            stripped = node.value.strip()
            if not stripped:
                continue
            if stripped in _CHAIN_SEPARATORS:
                continue
            if not found:
                continue
            break

        if isinstance(node, Tag) and node.tag == "ref":
            continue

        # Any other node (regional marker template, italic span, a
        # non-matching template, …): ignore until we have collected
        # something, then stop.
        if not found:
            continue
        break

    return found


def resolve_positional_params(template: Template) -> dict[int, Parameter]:
    """Resolve MediaWiki positional parameters of a template.

    Bare params (no ``key=``) get the next free positional index; named
    params whose name is a digit (``|2=value``) explicitly set that
    index. When source order produces a collision the later assignment
    wins — matches MediaWiki's last-write-wins semantics. Non-digit
    named params (``|spr=de``) are skipped.
    """
    positional_map: dict[int, Parameter] = {}
    counter = 0
    for p in template.params:
        if not p.showkey:
            counter += 1
            positional_map[counter] = p
        else:
            pname = str(p.name).strip()
            if pname.isascii() and pname.isdigit():
                positional_map[int(pname)] = p
    return positional_map


def slice_balanced_template(text: str, start: int) -> str | None:
    """Cut a brace-balanced ``{{…}}`` template starting at ``text[start]``.

    Faster than parsing the whole entry with mwparserfromhell when we
    only care about one specific template that we located by regex.
    Returns the full template string or ``None`` if braces don't balance.
    """
    if text[start : start + 2] != "{{":
        return None
    depth = 0
    i = start
    n = len(text)
    while i < n - 1:
        if text[i] == "{" and text[i + 1] == "{":
            depth += 1
            i += 2
            continue
        if text[i] == "}" and text[i + 1] == "}":
            depth -= 1
            i += 2
            if depth == 0:
                return text[start:i]
            continue
        i += 1
    return None

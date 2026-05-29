"""Extract inflection tables (Flexion) from a German entry.

The data lives in the first ``{{Deutsch … Übersicht}}`` template on
the page. To avoid running ``mwparserfromhell.parse()`` over the entire
entry (the previous code's hottest call), we locate the table by regex
and brace-balance the substring before handing it to the parser.

Keys are translated to English lowercase + underscore form
(``Nominativ Singular`` → ``nominative_singular``,
``Präsens_er, sie, es`` → ``present_3sg``). Translation is token-wise:
known grammar terms are mapped, unknown tokens are kept lowercase.
"""

from __future__ import annotations

import re

import mwparserfromhell

from wiktionary_de_parser._wikitext import (
    slice_balanced_template,
    strip_comments,
)
from wiktionary_de_parser.entry import WiktionaryEntry

_WANTED_TABLE_NAMES = frozenset(
    {
        "Deutsch Adjektiv Übersicht",
        "Deutsch Adverb Übersicht",
        "Deutsch Eigenname Übersicht",
        "Deutsch Nachname Übersicht",
        "Deutsch Pronomen Übersicht",
        "Deutsch Substantiv Übersicht",
        "Deutsch Substantiv Übersicht -sch",
        "Deutsch adjektivisch Übersicht",
        "Deutsch Toponym Übersicht",
        "Deutsch Verb Übersicht",
    }
)

# Locates the start of any potential Übersicht template. We accept any
# alphabetical token between "Deutsch" and "Übersicht" and place no
# constraint on what follows — variants like "Übersicht -sch" exist,
# and editors occasionally use tabs, CRLF, or extra whitespace after
# the name. The actual name check happens after brace-balanced slicing,
# against ``_WANTED_TABLE_NAMES``, so locator permissiveness is safe.
_UEBERSICHT_RE = re.compile(
    r"\{\{Deutsch\s+[A-Za-zÄÖÜäöüß]+\s+Übersicht",
    re.UNICODE,
)

# Token translation for inflection keys. Single linguistic terms only —
# the splitter joins them with underscores afterwards. Person tokens map
# to standard linguistic codes (1sg/2pl/3sg/…); ``er``, ``sie``, ``es``
# all collapse to ``3sg`` and adjacent duplicates are deduplicated, so
# ``Präsens_er, sie, es`` → ``present_3sg``.
_DE_EN_TOKEN: dict[str, str] = {
    # Cases
    "nominativ": "nominative",
    "genitiv": "genitive",
    "dativ": "dative",
    "akkusativ": "accusative",
    # Number
    "singular": "singular",
    "plural": "plural",
    # Adjective declension classes
    "stark": "strong",
    "schwach": "weak",
    "gemischt": "mixed",
    # Adjective grades
    "positiv": "positive",
    "komparativ": "comparative",
    "superlativ": "superlative",
    # Verb tenses / moods
    "präsens": "present",
    "präteritum": "preterite",
    "perfekt": "perfect",
    "plusquamperfekt": "pluperfect",
    "futur": "future",
    "indikativ": "indicative",
    "konjunktiv": "subjunctive",
    "imperativ": "imperative",
    "partizip": "participle",
    "infinitiv": "infinitive",
    "aktiv": "active",
    "passiv": "passive",
    # Misc grammar terms
    "genus": "gender",
    "stamm": "stem",
    "hilfsverb": "auxiliary",
    "kein": "no",
    "weitere": "further",
    "konjugationen": "conjugations",
    "alternative": "alternative",
    # Person → linguistic codes
    "ich": "1sg",
    "du": "2sg",
    "er": "3sg",
    "sie": "3sg",
    "es": "3sg",
    "wir": "1pl",
    "ihr": "2pl",
    # Roman numerals (Konjunktiv I/II, Futur I/II, Partizip I/II, …)
    "i": "1",
    "ii": "2",
    "iii": "3",
    "iv": "4",
}


def translate_inflection_key(key: str) -> str:
    """Token-wise German→English translation for an Übersicht parameter."""
    # ", " and "_" act as token separators alongside whitespace.
    normalized = key.replace(", ", " ").replace("_", " ")
    tokens = [t for t in normalized.split() if t]
    translated: list[str] = []
    for tok in tokens:
        tok_lc = tok.lower()
        translated.append(_DE_EN_TOKEN.get(tok_lc, tok_lc))
    # Collapse adjacent duplicates ("3sg 3sg 3sg" → "3sg"). Comes from
    # "er, sie, es" all mapping to the same code.
    collapsed: list[str] = []
    for t in translated:
        if collapsed and collapsed[-1] == t:
            continue
        collapsed.append(t)
    return "_".join(collapsed)


def _find_table(text: str) -> str | None:
    """Locate the first Übersicht-table template via regex + brace match.

    Regex + brace matching avoids parsing the entire entry just to find
    one template. HTML comments are stripped first: editors park
    alternative tables inside ``<!-- … -->``, which must not be parsed.
    Brace-balanced cutting tolerates nested templates inside table cells
    (``|Genus={{m}}``, ``|Bild=…{{Per-Deutschlandradio|…}}``) that would
    otherwise truncate the result.
    """
    # Cheap substring prefilter — the comment-strip + regex scan below run
    # over the whole entry, so skip them entirely when no Übersicht
    # template can be present (the majority of entries).
    if "Übersicht" not in text:
        return None
    text = strip_comments(text)
    for m in _UEBERSICHT_RE.finditer(text):
        start = m.start()
        # Verify the template name (the regex is permissive on suffix).
        # Use mwparserfromhell on the candidate slice only, not the full
        # entry. The slice is bounded by brace balance.
        sliced = slice_balanced_template(text, start)
        if sliced is None:
            continue
        # Extract the name segment up to the first `|` or `\n`.
        head = sliced[2:]  # drop leading "{{"
        name_end = len(head)
        for ch in ("|", "\n", "}"):
            i = head.find(ch)
            if i != -1 and i < name_end:
                name_end = i
        name = head[:name_end].strip()
        if name in _WANTED_TABLE_NAMES:
            return sliced
    return None


# Inside a single template-value cell, strip HTML tags (refs, sup,
# small, …). Multi-line bodies are real, so DOTALL. The backreference
# requires the closing tag name to match the opening one so a
# self-closing `<ref name="x"/>` cannot pair with a later unrelated
# `</sup>` and delete everything in between.
_CELL_HTML_RE = re.compile(
    r"<(\w+)[^>]*>.*?</\1>|<[^>]+/>|<[^>]+>",
    re.DOTALL,
)

# A legitimate Übersicht parameter key (verified against all 172 distinct
# keys in the dump): letters, digits, space, underscore, dot, asterisk,
# comma, hyphen. Keys with wiki markup / brackets / "=" are caption junk.
_VALID_KEY_RE = re.compile(r"[A-Za-zÄÖÜäöüß0-9 _.*,-]+")


def parse_table_values(table_string: str) -> dict[str, str] | None:
    """Parse the key=value pairs out of an Übersicht template.

    Walks the parsed template instead of regex-matching ``|key=value``
    pairs. Regex would also catch ``|key=val`` pairs sitting *inside*
    a nested template like ``{{Per-Deutsche Welle|Autor=...}}`` embedded
    in the ``|Bild=`` caption, producing junk fields ("Autor", "Titel",
    ...).
    """
    parsed = mwparserfromhell.parse(table_string)
    top_templates = parsed.filter_templates(recursive=False)
    if not top_templates:
        return None
    table_tmpl = top_templates[0]

    result: dict[str, str] = {}
    for param in table_tmpl.params:
        # Skip positional params — they show up when an editor writes
        # ``|Bild=foo.jpg|mini|1|caption`` (mini/1/caption are positional).
        if not param.showkey:
            continue

        raw_key = str(param.name).strip()

        # Drop noise keys: empty, numeric (broken Übersicht with
        # `|3=…|2=…`), image fields, and Flexion/Konjugation links
        # that aren't values.
        if not raw_key or raw_key.isdigit():
            continue
        if raw_key.startswith("Bild"):
            continue
        if raw_key in ("Flexion", "Weitere Konjugationen"):
            continue
        # Caption fragments leak in as bogus named params when a
        # ``|Bild=…|caption`` positional contains an ``=`` — e.g. on
        # `polytrop`: ``…(p = Druck, V = Volumen…)`` makes mwparserfromhell
        # read ``''polytrope'' Zustandsänderungen (p`` as a key. Every
        # legitimate Übersicht key is plain text (letters, digits, space,
        # ``_ . * , -``); anything carrying wiki markup or brackets is junk.
        if not _VALID_KEY_RE.fullmatch(raw_key):
            continue

        text = str(param.value).strip()
        text = text.replace("&nbsp;", " ")
        text = _CELL_HTML_RE.sub(" ", text)
        text = text.strip()

        # Genus normalization. Plural-only words sometimes carry "0" or
        # other placeholder values — drop them.
        # https://de.wiktionary.org/wiki/Wiktionary:Teestube/Archiv/2015/11
        if raw_key in ("Genus", "Genus 1", "Genus 2", "Genus 3", "Genus 4"):
            text = text.lower()
            if text not in ("f", "m", "n"):
                continue

        if not text or text in ("—", "-", "–", "−", "?"):
            continue

        result[translate_inflection_key(raw_key)] = text

    return result or None


def parse_inflection_from_wikitext(
    wikitext: str,
) -> dict[str, str] | None:
    """Locate and parse the first Übersicht table in ``wikitext``."""
    if not wikitext:
        return None
    table_string = _find_table(wikitext)
    if not table_string:
        return None
    return parse_table_values(table_string)


def parse(entry: WiktionaryEntry) -> dict[str, str] | None:
    return parse_inflection_from_wikitext(entry.wikitext)

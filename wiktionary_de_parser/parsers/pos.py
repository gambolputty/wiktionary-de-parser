"""Extract part-of-speech tags from a Wortart-header line.

Two cases need handling that a naive ``{{Wortart|<POS>|<Lang>}}`` regex
would miss:

1. A named parameter sneaks in (``{{Wortart|spr=de|Substantiv}}``).
   We resolve positional params with MediaWiki semantics so ``spr=de``
   doesn't leak as POS.
2. "Deklinierte Form" entries don't put the real POS on the header line
   — it sits in ``{{Grammatische Merkmale}}`` body text as e.g.
   "Genitiv Singular des Substantivs [[Wort]]". We extract the
   genitive ("Substantivs") and map it back to the base POS.

In addition, the presence of certain ``Übersicht`` templates is itself
a POS signal (a page with ``{{Deutsch Substantiv Übersicht}}`` is a
Substantiv even if Wortart says otherwise).
"""

from __future__ import annotations

import re

from mwparserfromhell.wikicode import Wikicode

from wiktionary_de_parser._wikitext import (
    WORTART_TEMPLATE_NAMES,
    resolve_positional_params,
)
from wiktionary_de_parser.entry import WiktionaryEntry
from wiktionary_de_parser.models import PosTag

# Mapping from genitive forms in "Grammatische Merkmale" to (POS, subtype)
_DEKLINIERTE_FORM_POS_MAP = {
    "Substantivs": ("Substantiv", None),
    "Adjektivs": ("Adjektiv", None),
    "Positivs": ("Adjektiv", "Positiv"),
    "Superlativs": ("Adjektiv", "Superlativ"),
    "Komparativs": ("Adjektiv", "Komparativ"),
    "Personalpronomens": ("Pronomen", "Personalpronomen"),
    "Possessivpronomens": ("Pronomen", "Possessivpronomen"),
    "Demonstrativpronomens": ("Pronomen", "Demonstrativpronomen"),
    "Indefinitpronomens": ("Pronomen", "Indefinitpronomen"),
    "Relativpronomens": ("Pronomen", "Relativpronomen"),
    "Reflexivpronomens": ("Pronomen", "Reflexivpronomen"),
    "Pronomens": ("Pronomen", None),
    "Numerales": ("Numerale", None),
}

_DEKLINIERTE_FORM_POS_RE = re.compile(
    r"des?\s+(" + "|".join(_DEKLINIERTE_FORM_POS_MAP.keys()) + r")\b"
)

# Canonical POS → known subtypes. Lookup is case-insensitive but the
# canonical letter case is preserved in the output.
_POS_MAP: dict[str, list[str]] = {
    "Abkürzung": ["Kurzwort"],
    "Adjektiv": [
        "Partizip",
        "Partizip I",
        "Partizip II",
        "Positiv",
        "Komparativ",
        "Superlativ",
        "Gerundivum",
        "Dekliniertes Gerundivum",
        "Pseudopartizip",
    ],
    "Adposition": [
        "Postposition",
        "Präposition",
        "Zirkumposition",
    ],
    "Adverb": [
        "Fokuspartikel",
        "Gradpartikel",
        "Interrogativadverb",
        "Konjunktionaladverb",
        "Kausaladverb",
        "Lokaladverb",
        "Modalpartikel",
        "Negationspartikel",
        "Pronominaladverb",
        "Temporaladverb",
        "Modaladverb",
        "Relativadverb",
    ],
    "Affix": [
        "Präfix",
        "Suffix",
        "Infix",
        "Interfix",
        "Zirkumfix",
        "Präfixoid",
        "Suffixoid",
    ],
    "Gebundenes Lexem": [],
    "Artikel": [],
    "Konjunktion": ["Subjunktion"],
    "Kontraktion": [],
    "Numerale": [
        "Kardinalzahl",
        "Ordinalzahl",
        "Bruchzahlwort",
        "Vervielfältigungszahlwort",
        "Wiederholungszahlwort",
    ],
    "Partikel": [
        "Interjektion",
        "Antwortpartikel",
        "Grußformel",
        "Onomatopoetikum",
        "Vergleichspartikel",
        "Fragepartikel",
    ],
    "Pronomen": [
        "Indefinitpronomen",
        "Interrogativpronomen",
        "Demonstrativpronomen",
        "Personalpronomen",
        "Possessivpronomen",
        "Reflexivpronomen",
        "Reflexives Personalpronomen",
        "Relativpronomen",
        "Reziprokpronomen",
    ],
    "Redewendung": [],
    "Sprichwort": [],
    "Geflügeltes Wort": [],
    "Merkspruch": [],
    "Formel": [],
    "Substantiv": [
        "Toponym",
        "Vorname",
        "Nachname",
        "Familienname",
        "Patronym",
        "Eigenname",
        "Straßenname",
        "Bauwerksname",
        "Göttername",
        "Zahlklassifikator",
        "Singularetantum",
        "Pluraletantum",
        "adjektivische Deklination",
        "Substantivierter Infinitiv",
    ],
    "Ortsnamengrundwort": [],
    "Symbol": [
        "Buchstabe",
        "Zahlzeichen",
        "Schriftzeichen",
        "Hiragana",
        "Katakana",
    ],
    "Verb": [
        "Konjugierte Form",
        "Hilfsverb",
        "Erweiterter Infinitiv",
    ],
    "Wortverbindung": [],
}

# Precomputed lowercase lookup tables for performance.
_POS_KEY_LOWER: dict[str, str] = {k.lower(): k for k in _POS_MAP}
_POS_SUBTYPE_LOWER: dict[str, list[tuple[str, str]]] = {}
for _key, _values in _POS_MAP.items():
    for _v in _values:
        _POS_SUBTYPE_LOWER.setdefault(_v.lower(), []).append((_key, _v))


def _wortart_template_names_from_parsed(parsed: Wikicode) -> list[str]:
    """Names of the Wortart templates on the header line, in order.

    Uses MediaWiki positional semantics so ``{{Wortart|spr=de|Substantiv}}``
    correctly yields ``["Substantiv"]`` rather than ``["spr=de"]``.
    """
    names: list[str] = []
    for tmpl in parsed.filter_templates():
        if str(tmpl.name).strip() not in WORTART_TEMPLATE_NAMES:
            continue
        positional_map = resolve_positional_params(tmpl)
        param = positional_map.get(1)
        if param is None:
            continue
        pos = str(param.value).strip()
        if pos:
            names.append(pos)
    return names


# Übersicht-template marker → (canonical POS, optional subtype). Order
# matters: it fixes both the POS key insertion order and the subtype
# order within a POS.
_UEBERSICHT_POS: tuple[tuple[str, str, str | None], ...] = (
    ("{{Deutsch Substantiv Übersicht", "Substantiv", None),
    (
        "{{Deutsch adjektivisch Übersicht",
        "Substantiv",
        "adjektivische Deklination",
    ),
    ("{{Deutsch Toponym Übersicht", "Substantiv", "Toponym"),
    ("{{Deutsch Adjektiv Übersicht", "Adjektiv", None),
    ("{{Deutsch Adverb Übersicht", "Adverb", None),
    ("{{Deutsch Pronomen Übersicht", "Pronomen", None),
    ("{{Deutsch Verb Übersicht", "Verb", None),
)


def _pos_from_uebersicht_templates(wikitext: str) -> dict[str, list[str]]:
    """``{{Deutsch … Übersicht}}`` templates imply a POS even when the
    Wortart header disagrees."""
    result: dict[str, list[str]] = {}
    if "Übersicht" not in wikitext:
        return result
    for marker, pos, subtype in _UEBERSICHT_POS:
        if marker in wikitext:
            subtypes = result.setdefault(pos, [])
            if subtype is not None:
                subtypes.append(subtype)
    return result


def _normalize_pos_names(
    pos_names: list[str], result: dict[str, list[str]]
) -> dict[str, list[str]]:
    """Map raw Wortart names to canonical POS + subtypes, merging into
    ``result`` (which may already carry Übersicht-derived entries)."""
    for name in pos_names:
        name_low = name.lower()
        if name_low in _POS_KEY_LOWER:
            key = _POS_KEY_LOWER[name_low]
            result.setdefault(key, [])
        for parent, value in _POS_SUBTYPE_LOWER.get(name_low, ()):
            subs = result.setdefault(parent, [])
            if value not in subs:
                subs.append(value)
    return result


def _extract_deklinierte_pos(wikitext: str) -> dict[str, list[str]] | None:
    """Extract the actual POS from "Deklinierte Form" entries via the
    "Grammatische Merkmale" body. Terminates at the next top-level
    template (``{{Grundformverweis…}}``, ``{{Synonyme}}``, …) or end of
    text. The lookahead matches both ``\\n\\n{{`` and ``\\n{{``."""
    match = re.search(
        r"{{Grammatische Merkmale}}\s*(.*?)(?=\n{{|$)",
        wikitext,
        re.DOTALL,
    )
    if not match:
        return None
    features_text = match.group(1).strip()
    if not features_text:
        return None

    pos_matches = _DEKLINIERTE_FORM_POS_RE.findall(features_text)
    if not pos_matches:
        return None

    pos_genitive = pos_matches[0]
    pos_info = _DEKLINIERTE_FORM_POS_MAP.get(pos_genitive)
    if not pos_info:
        return None
    pos_base, subtype = pos_info
    return {pos_base: [subtype] if subtype else []}


def _dict_to_postags(d: dict[str, list[str]]) -> list[PosTag]:
    return [PosTag(pos=k, subtypes=tuple(v)) for k, v in d.items()]


def parse(entry: WiktionaryEntry) -> list[PosTag]:
    """Return the list of ``PosTag``\\s. Empty list when nothing found."""
    parsed = entry.header_wikicode
    if parsed is None:
        return []

    pos_names = _wortart_template_names_from_parsed(parsed)
    if not pos_names:
        return []

    if "Deklinierte Form" in pos_names:
        deklinierte = _extract_deklinierte_pos(entry.wikitext)
        if deklinierte:
            return _dict_to_postags(deklinierte)

    result = _pos_from_uebersicht_templates(entry.wikitext)
    _normalize_pos_names(pos_names, result)
    return _dict_to_postags(result)

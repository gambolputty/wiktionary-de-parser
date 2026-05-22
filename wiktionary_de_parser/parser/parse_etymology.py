import re
from typing import cast

import mwparserfromhell
from mwparserfromhell.nodes.extras import Parameter
from mwparserfromhell.nodes.template import Template

from wiktionary_de_parser.models import (
    EtymologyResult,
    EtymologyType,
    ParseEtymologyResult,
)
from wiktionary_de_parser.parser import Parser

# Structural wikilinks that mark the word formation type. The wikilink scan
# returns the first match — more specific markers like Determinativkompositum
# are not prioritised by ordering here, but in practice Wiktionary entries
# place the specific marker first. Movierung is handled separately as an
# upgrade from DERIVATION when an inline Motion/Movierung marker is present.
MARKER_TO_TYPE: dict[str, EtymologyType] = {
    "Determinativkompositum": EtymologyType.COMPOUND,
    "Possessivkompositum": EtymologyType.COMPOUND,
    "Kopulativkompositum": EtymologyType.COMPOUND,
    "Kompositum": EtymologyType.COMPOUND,
    "Komposition": EtymologyType.COMPOUND,
    "Zusammensetzung": EtymologyType.COMPOUND,
    "Zusammenrückung": EtymologyType.COMPOUND,
    # Zusammenbildung = Wortgruppe + Suffix ("fern bedienen + -ung →
    # Fernbedienung"). Linguistically a derivation from a phrase, not a true
    # compound — group it with DERIVATION so the suffix slot stays meaningful.
    "Zusammenbildung": EtymologyType.DERIVATION,
    "Univerbierung": EtymologyType.COMPOUND,
    "Wortverbindung": EtymologyType.COMPOUND,
    "Ableitung": EtymologyType.DERIVATION,
    "Derivation": EtymologyType.DERIVATION,
    "Rückbildung": EtymologyType.DERIVATION,
    "Diminutiv": EtymologyType.DERIVATION,
    "Konversion": EtymologyType.CONVERSION,
    "Substantivierung": EtymologyType.CONVERSION,
    "Nominalisierung": EtymologyType.CONVERSION,
    "Verbalisierung": EtymologyType.CONVERSION,
    "Entlehnung": EtymologyType.LOANWORD,
    "Lehnwort": EtymologyType.LOANWORD,
    "Lehnübersetzung": EtymologyType.LOANWORD,
    "Lehnübertragung": EtymologyType.LOANWORD,
    "Lehnbedeutung": EtymologyType.LOANWORD,
    "Lehnschöpfung": EtymologyType.LOANWORD,
    "Erbwort": EtymologyType.LOANWORD,
    "Pseudoanglizismus": EtymologyType.LOANWORD,
    "Scheinentlehnung": EtymologyType.LOANWORD,
    "Internationalismus": EtymologyType.LOANWORD,
    "Kurzwort": EtymologyType.SHORTENING,
    "Kurzform": EtymologyType.SHORTENING,
    "Akronym": EtymologyType.SHORTENING,
    "Initialwort": EtymologyType.SHORTENING,
    "Abkürzung": EtymologyType.SHORTENING,
    "Kofferwort": EtymologyType.SHORTENING,
    "Kontamination": EtymologyType.SHORTENING,
    "Wortkreuzung": EtymologyType.SHORTENING,
    "Nebenform": EtymologyType.VARIANT,
    "Schreibvariante": EtymologyType.VARIANT,
}

# Plaintext head-words that imply a type when no wikilink marker is found.
# Used for sections phrased as "zusammengesetzt aus …", "abgeleitet von …",
# etc. Keyed lowercase. Built from MARKER_TO_TYPE plus extras observed in
# free-text Herkunft prose.
PLAINTEXT_HEAD_MARKERS: dict[str, EtymologyType] = {
    name.lower(): t for name, t in MARKER_TO_TYPE.items()
} | {
    "zusammengesetzt": EtymologyType.COMPOUND,
    "abgeleitet": EtymologyType.DERIVATION,
    "entlehnt": EtymologyType.LOANWORD,
    "verkürzt": EtymologyType.SHORTENING,
    "variante": EtymologyType.VARIANT,
    "alternative": EtymologyType.VARIANT,
    "koseform": EtymologyType.VARIANT,
    "verkleinerungsform": EtymologyType.DERIVATION,
    "partizip": EtymologyType.CONVERSION,
}

# Wikilinks pointing at word-formation terminology rather than at lemma
# components. Components extraction filters these out.
TERMINOLOGY: set[str] = set(MARKER_TO_TYPE) | {
    "Suffix",
    "Präfix",
    "Präfixoid",
    "Suffixoid",
    "Affix",
    "Konfix",
    "Infix",
    "Interfix",
    "Fugenelement",
    "Gleitlaut",
    "Derivatem",
    "Ableitungsmorphem",
    "Wortbildungsmorphem",
    "Morphem",
    "Stamm",
    "Wortstamm",
    "Verbstamm",
    "Verbzusatz",
    "Verbsuffix",
    "Verb",
    "Substantiv",
    "Adjektiv",
    "Adverb",
    "Partikel",
    "Pronomen",
    "Präposition",
    "Konjunktion",
    "Interjektion",
    "Numerale",
    "Artikel",
    "Partizip",
    "Partizip I",
    "Partizip II",
    "Infinitiv",
    "Imperativ",
    "Singular",
    "Plural",
    "Genitiv",
    "Akkusativ",
    "Dativ",
    "Nominativ",
    "Komparativ",
    "Superlativ",
    "Positiv",
    "Motion",
    "Movierung",
    "etymologisch",
    "strukturell",
    "Etymologie",
    "Neuwort",
    "Neologismus",
    "Kunstwort",
    "Onomatopoetikum",
    "implizite Ableitung",
    "syntaktische Umsetzung",
    "Flexionsendung",
    "Femininum",
    "Maskulinum",
    "Neutrum",
    "Umlaut",
    "Ablaut",
    "präpositionales Rektionskompositum",
    "Rektionskompositum",
    "Hausname",
    "Herkunftsname",
    "Rufname",
    "Übername",
    "Verbalstamm",
    "Diminutivendung",
    "Lexem",
    "Schimpfwort",
    "Possessivpronomen",
    "Demonstrativpronomen",
    "Relativpronomen",
    "Personalpronomen",
    "Indefinitpronomen",
    "Reflexivpronomen",
    "Interrogativpronomen",
    "Toponym",
    "Ortsname",
    "Personenname",
    "Eigenname",
    "Vorname",
    "Nachname",
    "Familienname",
    "Patronym",
    "Beiname",
    "Spitzname",
    "Grundwort",
    "Bestimmungswort",
    "Determinatum",
    "Determinans",
    "partielles Kurzwort",
    "Denominativ",
    "gebundenes Lexem",
    "Wortbildung",
    "Standardwortschatz",
    "Ziffer",
}

# Adjectival language wikilinks observed in the corpus, lowercase. Detect the
# source language of loanwords by collecting all such links and returning the
# last (deepest in the etymology chain). Matching against the wikilink target
# is case-insensitive via `.lower()`; the surface form is recapitalised on the
# way out by `_canonicalise_language`.
LANGUAGE_WIKILINKS: set[str] = {
    "lateinisch",
    "latein",
    "mittellateinisch",
    "mittellatein",
    "spätlateinisch",
    "spätlatein",
    "vulgärlatein",
    "griechisch",
    "altgriechisch",
    "mittelgriechisch",
    "neugriechisch",
    "englisch",
    "altenglisch",
    "mittelenglisch",
    "französisch",
    "altfranzösisch",
    "mittelfranzösisch",
    "italienisch",
    "altitalienisch",
    "spanisch",
    "altspanisch",
    "portugiesisch",
    "altportugiesisch",
    "katalanisch",
    "altkatalanisch",
    "rumänisch",
    "okzitanisch",
    "altokzitanisch",
    "altprovenzalisch",
    "iberoromanisch",
    "romanisch",
    "germanisch",
    "westgermanisch",
    "ostgermanisch",
    "nordgermanisch",
    "protogermanisch",
    "indogermanisch",
    "indoeuropäisch",
    "mittelhochdeutsch",
    "althochdeutsch",
    "frühneuhochdeutsch",
    "spätmittelhochdeutsch",
    "neuhochdeutsch",
    "mittelfränkisch",
    "altfränkisch",
    "altsächsisch",
    "niederdeutsch",
    "mittelniederdeutsch",
    "niederländisch",
    "mittelniederländisch",
    "altniederländisch",
    "altfriesisch",
    "westfriesisch",
    "gotisch",
    "altnordisch",
    "altschwedisch",
    "schwedisch",
    "dänisch",
    "norwegisch",
    "isländisch",
    "finnisch",
    "ungarisch",
    "estnisch",
    "russisch",
    "altrussisch",
    "polnisch",
    "tschechisch",
    "slowakisch",
    "ukrainisch",
    "kroatisch",
    "serbisch",
    "bulgarisch",
    "slowenisch",
    "litauisch",
    "lettisch",
    "arabisch",
    "hebräisch",
    "althebräisch",
    "neuhebräisch",
    "biblisch-hebräisch",
    "mittelhebräisch",
    "jiddisch",
    "westjiddisch",
    "ostjiddisch",
    "rotwelsch",
    "aramäisch",
    "persisch",
    "altpersisch",
    "akkadisch",
    "hethitisch",
    "umbrisch",
    "altäthiopisch",
    "sanskrit",
    "altindisch",
    "hindi",
    "urdu",
    "japanisch",
    "chinesisch",
    "koreanisch",
    "türkisch",
    "afrikaans",
    "swahili",
    "slawisch",
    "altslawisch",
    "kirchenslawisch",
    "altkirchenslawisch",
    "neulateinisch",
    "mitteldeutsch",
    "oberdeutsch",
    "süddeutsch",
    "skandinavisch",
    "urgermanisch",
}

# Verb prefixes recognised by the {{Verbherkunft}} template, ported 1:1 from
# Modul:Verb (function Verb.vorsilbe) on de.wiktionary. Sorted by length
# descending below for longest-match. After a prefix is stripped, at least
# 4 chars must remain for the stem (3 for -tun verbs).
VERB_PREFIXES: tuple[str, ...] = tuple(
    sorted(
        {
            "hintereinander",
            "durcheinander",
            "gegeneinander",
            "nebeneinander",
            "untereinander",
            "widereinander",
            "übereinander",
            "aufeinander",
            "auseinander",
            "beieinander",
            "miteinander",
            "voneinander",
            "aneinander",
            "dazwischen",
            "hintenüber",
            "ineinander",
            "zueinander",
            "beisammen",
            "gegenüber",
            "hernieder",
            "hinterher",
            "rückwärts",
            "aufwärts",
            "beiseite",
            "dahinter",
            "drauflos",
            "einwärts",
            "entgegen",
            "herunter",
            "hindurch",
            "hinunter",
            "vornüber",
            "vorwärts",
            "zunichte",
            "zusammen",
            "zwischen",
            "abwärts",
            "dagegen",
            "daneben",
            "darüber",
            "entlang",
            "entzwei",
            "fürlieb",
            "herüber",
            "hierher",
            "hinüber",
            "instand",
            "schwarz",
            "trocken",
            "überein",
            "vorüber",
            "zurecht",
            "zuwider",
            "bereit",
            "einher",
            "falsch",
            "fertig",
            "geheim",
            "gerade",
            "gleich",
            "herauf",
            "heraus",
            "herbei",
            "herein",
            "hervor",
            "hinauf",
            "hinaus",
            "hinein",
            "hintan",
            "hinter",
            "hinweg",
            "kaputt",
            "nieder",
            "runter",
            "sauber",
            "scharf",
            "schief",
            "schutz",
            "tiefer",
            "voraus",
            "vorbei",
            "vorher",
            "vorweg",
            "weiter",
            "wieder",
            "zugute",
            "zurück",
            "abhin",
            "anhin",
            "bauch",
            "bevor",
            "blond",
            "breit",
            "dabei",
            "dafür",
            "daher",
            "dahin",
            "daran",
            "davon",
            "davor",
            "dicht",
            "drauf",
            "drein",
            "durch",
            "empor",
            "flach",
            "flott",
            "fremd",
            "gegen",
            "glatt",
            "herab",
            "heran",
            "herum",
            "hinab",
            "hinan",
            "hinzu",
            "klein",
            "krank",
            "näher",
            "offen",
            "platt",
            "reich",
            "rüber",
            "schön",
            "still",
            "übrig",
            "umher",
            "umhin",
            "unter",
            "voran",
            "weich",
            "wider",
            "zuvor",
            "acht",
            "blau",
            "bloß",
            "dazu",
            "dort",
            "dran",
            "fehl",
            "feil",
            "fein",
            "fern",
            "fest",
            "fort",
            "frei",
            "gelb",
            "groß",
            "grün",
            "heim",
            "hier",
            "hoch",
            "kahl",
            "kalt",
            "klar",
            "kurz",
            "lieb",
            "leer",
            "mies",
            "miss",
            "nach",
            "nahe",
            "nass",
            "quer",
            "raus",
            "rein",
            "rück",
            "satt",
            "seil",
            "übel",
            "über",
            "voll",
            "wach",
            "wahr",
            "warm",
            "weis",
            "weiß",
            "wert",
            "wohl",
            "auf",
            "aus",
            "bei",
            "dar",
            "ein",
            "ent",
            "für",
            "gut",
            "her",
            "hin",
            "los",
            "mit",
            "out",
            "rum",
            "tot",
            "ver",
            "vor",
            "weg",
            "zer",
            "ab",
            "an",
            "be",
            "da",
            "de",
            "er",
            "ge",
            "re",
            "um",
            "zu",
        },
        key=len,
        reverse=True,
    )
)


SENSE_MARKER_RE = re.compile(
    r"^\s*:?\s*\[\d+(?:[-–,]\s*\d+)*\]\s*", re.MULTILINE
)


def _label_re(word: str) -> re.Pattern[str]:
    # Match both ":strukturell:" and "*strukturell:" line-start variants —
    # the entry for Weihnachtsbaum uses the *-bullet form.
    return re.compile(rf"[:*]\s*''?\[?\[?{word}\]?\]?:?''?\s*", re.IGNORECASE)


STRUCT_LABEL_RE = _label_re("strukturell")
ETYM_LABEL_RE = _label_re("etymologisch")
MOVIERUNG_INLINE_RE = re.compile(
    r"(?:\[\[(?:Motion|Movierung)\]\]|\bMovierung\b)"
)
WEIBLICHE_FORM_RE = re.compile(r"weibliche\s+Form\s+(?:zu|von)", re.IGNORECASE)
_LANG_ALT = "|".join(sorted(LANGUAGE_WIKILINKS, key=len, reverse=True))
# Allow trailing declension endings ("lateinisch" → "lateinischen",
# "lateinischer"). `\w*` is outside the capture group so findall() returns the
# base form, which _canonicalise_language can then title-case without
# dragging the ending along.
LANGUAGE_PLAIN_RE = re.compile(r"\b(" + _LANG_ALT + r")\w*", re.IGNORECASE)
QS_ONLY_RE = re.compile(r"(?:\{\{QS[^}]*\}\}\s*)+")
INTERWIKI_PREFIX_RE = re.compile(
    r"^(?:w|s|b|q|v|n|commons|wikt|mw|doi|isbn|incubator|meta):",
    re.IGNORECASE,
)
HEAD_WORD_RE = re.compile(r"[A-Za-zÄÖÜäöüß]+")
NEXT_BLOCK_LINE_RE = re.compile(r"\n\s*:")

# Verbherkunft W-values that indicate the prefix is itself a lexeme (noun/adj)
# rather than a particle. For these, the result is a COMPOUND, not a derivation.
VERBHERKUNFT_COMPOUND_WORDARTS = {"Adjektiv", "Substantiv", "Numerale"}


def _strip_bound_morpheme(target: str) -> tuple[str, bool, bool]:
    """Parse a wikilink target into (stem, leading_hyphen, trailing_hyphen).

    Examples:
        "-in"   -> ("in", True, False)
        "un-"   -> ("un", False, True)
        "-s-"   -> ("s", True, True)
        "Haus"  -> ("Haus", False, False)
    """
    leading = target.startswith("-")
    trailing = target.endswith("-")
    stem = target.strip("-")
    return stem, leading, trailing


def _select_first_sense(section: str) -> str:
    """Multi-sense Herkunft sections (`:[1] ... :[2] ...`): keep only the
    first sense block."""
    matches = list(SENSE_MARKER_RE.finditer(section))
    if len(matches) < 2:
        return section
    return section[matches[0].end() : matches[1].start()].strip()


def _select_structural_block(section: str) -> str:
    """When a section uses the :strukturell: / :etymologisch: convention,
    return only the strukturell block — that's the one carrying components."""
    struct_match = STRUCT_LABEL_RE.search(section)
    etym_match = ETYM_LABEL_RE.search(section)
    if not (struct_match and etym_match):
        return section
    if etym_match.start() > struct_match.end():
        return section[struct_match.end() : etym_match.start()].strip()
    # Etymologisch comes first → strukturell block runs from its label to EOF.
    return section[struct_match.end() :].strip()


def _select_first_line(section: str) -> str:
    """Keep only the first ":"-prefixed line. Multi-paragraph Herkunft sections
    typically have the actual word-formation claim on line 1 and historical
    prose ("Die Bezeichnung tritt zuerst …", "Im 15. Jahrhundert …") on later
    lines. Those follow-up lines are full of wikilinks that pollute the
    components list. The first line carries the structural information."""
    match = NEXT_BLOCK_LINE_RE.search(section)
    if match is None:
        return section
    return section[: match.start()].rstrip()


def _select_first_sentence(section: str) -> str:
    """Cut the section at the first sentence boundary (";" or ". ") so trailing
    explanatory prose doesn't pollute the component list.

    Many Herkunft sections cram structural claim and historical commentary into
    a single line, separated by a semicolon: "[[Determinativkompositum]] aus X
    und Y; das Wort geht zurück auf …". After the cut, the [X, Y]-style
    composition is intact and the [[zehn]] / [[sechs]] / [[Frau]] gloss
    wikilinks in the explanation are gone.

    Comma is *not* a boundary — it appears inside compositions
    ("X, Y und Z", "X, mit dem Fugenelement Y").
    """
    semicolon = section.find(";")
    # Sentence end = ". " followed by a capital letter. The negative lookbehind
    # for a digit prevents matching "17. Jahrhundert" or "16. Jahrhundert" as
    # sentence boundaries, which they aren't.
    period_match = re.search(r"(?<!\d)\.\s+(?=[A-ZÄÖÜ])", section)
    cuts = [
        c for c in (semicolon, period_match.start() if period_match else -1)
        if c >= 0
    ]
    if not cuts:
        return section
    return section[: min(cuts)].rstrip()


def _is_empty_or_qs(section: str) -> bool:
    text = section.strip().lstrip(":").strip()
    text = SENSE_MARKER_RE.sub("", text).strip()
    if not text:
        return True
    if text in {"-", "—", "?"}:
        return True
    if QS_ONLY_RE.fullmatch(text):
        return True
    return False


def _detect_verb_prefix(lemma: str) -> tuple[str, str] | None:
    """Reproduce Modul:Verb.vorsilbe() for German prefixed verbs.

    Longest-match against the whitelist of recognised prefixes; the stem must
    be at least 4 chars long (3 for -tun verbs). Returns (prefix, stem) or
    None if no prefix matches.
    """
    geslang = len(lemma)
    if lemma.endswith("tun"):
        max_prefix_len = geslang - 3
    elif geslang >= 7:
        max_prefix_len = geslang - 4
    else:
        return None
    for prefix in VERB_PREFIXES:
        if len(prefix) <= max_prefix_len and lemma.startswith(prefix):
            return prefix, lemma[len(prefix) :]
    return None


def _find_verbherkunft_template(templates: list[Template]) -> Template | None:
    return next(
        (t for t in templates if str(t.name).strip() == "Verbherkunft"), None
    )


def _detect_type_marker(
    link_pairs: list[tuple[str, str]], section: str
) -> EtymologyType | None:
    """Find the first structural marker and map it to an EtymologyType.

    Tries first a wikilink (e.g. [[Determinativkompositum]]), then falls
    back to a plaintext word at the head of the section (e.g. "Nebenform zu
    …", "Substantivierung des …"). None if no recognised marker appears.
    """
    for target, _ in link_pairs:
        if target in MARKER_TO_TYPE:
            return MARKER_TO_TYPE[target]
    # Plaintext fallback: only the first ~5 words, to avoid matching markers
    # buried deep in free-text etymology.
    head = section.lstrip(":").strip()
    head = SENSE_MARKER_RE.sub("", head).lstrip()
    for word in HEAD_WORD_RE.findall(head)[:5]:
        lw = word.lower()
        if lw in PLAINTEXT_HEAD_MARKERS:
            return PLAINTEXT_HEAD_MARKERS[lw]
    return None


def _extract_components_and_morphemes(
    link_pairs: list[tuple[str, str]],
) -> tuple[list[str], str | None, str | None, str | None]:
    """Walk the section's wikilinks and bucket them into:
    - components: free lemmas (filtered against terminology)
    - prefix: bound morpheme like [[un-]]
    - suffix: bound morpheme like [[-ung]], [[-in]]
    - fugenelement: bound morpheme on both sides, like [[-s-]]
    """
    components: list[str] = []
    prefix: str | None = None
    suffix: str | None = None
    fugenelement: str | None = None

    for target, target_lower in link_pairs:
        if target_lower in LANGUAGE_WIKILINKS or target in TERMINOLOGY:
            continue
        # Skip interwiki / cross-project / external-id links: w:Wikipedia,
        # s:Wikisource, b:Wikibooks, q:Wikiquote, v:Wikiversity, n:Wikinews,
        # commons:, wikt:, mw:, doi:, isbn:, ...
        if INTERWIKI_PREFIX_RE.match(target):
            continue
        # Skip wikilinks with stray punctuation in the target like "[[(-ung]]"
        # — those are Wiktionary typos, not real lemmas.
        if any(c in target for c in "()[]{}<>"):
            continue
        stem, lead, trail = _strip_bound_morpheme(target)
        if lead and trail:
            if fugenelement is None:
                fugenelement = stem
            continue
        if lead and not trail:
            if suffix is None:
                suffix = stem
            continue
        if trail and not lead:
            if prefix is None:
                prefix = stem
            continue
        # The wikilink target before "#" is the lemma; drop the section anchor.
        cleaned = target.split("#", 1)[0].strip()
        if cleaned and cleaned not in components:
            components.append(cleaned)
    return components, prefix, suffix, fugenelement


def _canonicalise_language(name: str) -> str:
    """Capitalise each hyphen-separated part, e.g. "biblisch-hebräisch" →
    "Biblisch-Hebräisch". Avoids str.capitalize() (lowercases the tail) and
    str.title() (mangles non-ASCII letters)."""
    return "-".join(p[:1].upper() + p[1:] for p in name.split("-"))


def _extract_source_language(
    link_pairs: list[tuple[str, str]],
    plain_lang_matches: list[str],
    templates: list[Template],
) -> str | None:
    """Return the deepest language reference in the etymology chain.

    Primary signal: language wikilinks ([[lateinisch]], [[mittelhochdeutsch]]).
    Falls back to plain-text language names, then to the language code of the
    last {{Ü|<code>|...}} translation template. Returns the *last* match —
    that's the deepest source in chains like "über französisch X aus
    lateinisch Y", where Latin is the etymological root.
    """
    last_lang: str | None = None
    for target, target_lower in link_pairs:
        if target_lower in LANGUAGE_WIKILINKS:
            last_lang = target
    if last_lang is not None:
        return _canonicalise_language(last_lang)
    if plain_lang_matches:
        return _canonicalise_language(plain_lang_matches[-1])
    last_code: str | None = None
    for tpl in templates:
        tname = str(tpl.name).strip()
        if tname in ("Ü", "Üt", "Üxx4") and tpl.has(1):
            code = str(cast(Parameter, tpl.get(1)).value).strip()
            if code:
                last_code = code
    return last_code


def _build_from_verbherkunft(
    lemma: str, tpl: Template
) -> EtymologyResult | None:
    """Translate {{Verbherkunft|W=...}} into a structured EtymologyResult by
    reapplying the Wiktionary prefix-detection heuristic on the lemma."""
    wortart = (
        str(cast(Parameter, tpl.get("W")).value).strip() if tpl.has("W") else ""
    )

    split = _detect_verb_prefix(lemma)
    if split is None:
        return None
    prefix, stem = split

    if wortart in VERBHERKUNFT_COMPOUND_WORDARTS:
        return EtymologyResult(
            type=EtymologyType.COMPOUND,
            components=[prefix, stem],
        )
    return EtymologyResult(
        type=EtymologyType.DERIVATION,
        components=[stem],
        prefix=prefix,
    )


class ParseEtymology(Parser):
    name = "etymology"

    @classmethod
    def parse(cls, lemma: str, wikitext: str) -> ParseEtymologyResult:
        section = cls.find_paragraph("Herkunft", wikitext)
        if section is None:
            return None

        section = section.strip()
        if not section:
            return EtymologyResult(type=EtymologyType.UNKNOWN)

        if _is_empty_or_qs(section):
            return EtymologyResult(type=EtymologyType.UNKNOWN)

        section = _select_structural_block(section)
        section = _select_first_sense(section)
        section = _select_first_line(section)
        section = _select_first_sentence(section)
        parsed = mwparserfromhell.parse(section)
        wikilinks = parsed.filter_wikilinks()
        has_verbherkunft = "{{Verbherkunft" in section
        has_translation = "{{Ü" in section
        needs_templates = has_verbherkunft or has_translation
        templates = parsed.filter_templates() if needs_templates else []

        if has_verbherkunft:
            verbherkunft = _find_verbherkunft_template(templates)
            if verbherkunft is not None:
                result = _build_from_verbherkunft(lemma, verbherkunft)
                if result is not None:
                    return result

        # Materialise each wikilink target once — three helpers below would
        # otherwise re-stringify and re-lowercase the same nodes.
        link_pairs: list[tuple[str, str]] = []
        for link in wikilinks:
            target = str(link.title).strip()
            link_pairs.append((target, target.lower()))
        plain_lang_matches = LANGUAGE_PLAIN_RE.findall(section)
        has_language_signal = has_translation or bool(plain_lang_matches)

        etype = _detect_type_marker(link_pairs, section)
        components, prefix, suffix, fugenelement = (
            _extract_components_and_morphemes(link_pairs)
        )

        # Only Ableitung-shaped or unclassified sections can be Movierung —
        # skip the regex scans otherwise.
        if etype in (EtymologyType.DERIVATION, None) and (
            MOVIERUNG_INLINE_RE.search(section)
            or WEIBLICHE_FORM_RE.search(section)
        ):
            etype = EtymologyType.MOVIERUNG

        # "Ableitung von lateinisch X" looks structurally like a derivation
        # but is semantically a loanword — the base lemma is foreign, not a
        # German word the entry is derived from. Promote when *any* foreign
        # source signal is present (translation template or plaintext
        # language name).
        if etype == EtymologyType.DERIVATION and has_language_signal:
            etype = EtymologyType.LOANWORD

        # Resolve source_language before the final type fallback so it can
        # disambiguate ambiguous UNKNOWN sections (Erbwort vs derivation).
        source_language: str | None = None
        if etype == EtymologyType.LOANWORD or etype is None:
            source_language = _extract_source_language(
                link_pairs, plain_lang_matches, templates
            )

        if etype is None:
            if source_language is not None:
                # "[[mittelhochdeutsch]] *[[wedra-]] „Wetter"": a reconstructed
                # form with a foreign-language signal is an Erbwort, not a
                # German derivation, even if the wikilink shape looks like
                # a prefix.
                etype = EtymologyType.LOANWORD
            elif suffix or prefix:
                # No foreign source signal but a clear morpheme marker
                # ("von [[Hamm]] mit dem [[Suffix]] [[-er]] abgeleitet") —
                # almost certainly a derivation phrased unconventionally.
                etype = EtymologyType.DERIVATION
            else:
                etype = EtymologyType.UNKNOWN

        # In a compound, bound morphemes have different semantics than in a
        # derivation. Promote them to the right slot:
        #  - [[Untersee-]] (trailing hyphen) is the first part of the compound
        #  - [[-logie]] (leading hyphen, multi-letter) is a gebundenes Lexem
        #    at the end
        #  - [[-s]] (leading hyphen, 1–2 letters) is a Fugenelement between
        #    two components
        # None of these are true derivational affixes. Promote prefix before
        # suffix so the "suffix between two components" rule sees the right
        # components count for Önophilie-style cases (öno- + -philie).
        if etype == EtymologyType.COMPOUND:
            if prefix:
                # Promote [[Untersee-]] to a leading component, but avoid
                # duplicates when both [[Untersee-]] and [[Untersee]] appear.
                if prefix not in components:
                    components.insert(0, prefix)
                prefix = None
            if suffix and components:
                if not fugenelement and len(suffix) <= 2:
                    # Short single-sided morpheme between components →
                    # Fugenelement (Straßenbahn -n-, Adamsapfel -s).
                    fugenelement = suffix
                else:
                    # Longer bound morpheme or already-present fuge — treat
                    # as a final gebundenes Lexem component (Önophilie:
                    # öno + philie; Vexillologie: Vexill + o + logie).
                    # Dedupe: [[frei]] + [[-frei]] would otherwise appear
                    # twice (einwandfrei).
                    if suffix not in components:
                        components.append(suffix)
                suffix = None
            # If components is empty even after the prefix promotion, the
            # suffix stays a suffix — happens with malformed/sparse sections.

        # In word-formation types other than COMPOUND/SHORTENING, a
        # single-letter wikilink like [[e]] or [[ä]] is virtually always an
        # Umlaut marker or an "Auslassung des e" gloss, not an actual
        # component. (For COMPOUND/SHORTENING, [[H]] in H-Milch and similar
        # are legitimate letter-components.)
        if etype in (
            EtymologyType.DERIVATION,
            EtymologyType.MOVIERUNG,
            EtymologyType.CONVERSION,
        ):
            components = [
                c for c in components if not (len(c) == 1 and c.isalpha())
            ]

        # Loanwords carry their substance in source_language. Any morphemes
        # extracted from the section are reconstructed forms ("*sīna-",
        # "Rekonstruktion:Urgermanisch/landa") or foreign suffixes, not
        # information the consumer can use. Components are glosses
        # (handled above). Wipe the lot.
        if etype == EtymologyType.LOANWORD:
            components = []
            prefix = None
            suffix = None
            fugenelement = None
        # CONVERSION sections that reference a foreign source ("Substantivierung
        # von <foreign>") — German wikilinks around them are glosses, not
        # components.
        elif etype == EtymologyType.CONVERSION and has_language_signal:
            components = []
        # UNKNOWN with no morpheme structure detected: the wikilinks the
        # extractor collected are typically free-text wikilinks from
        # explanatory prose ("nach dem römischen [[Kaiser]] [[Augustus]]
        # benannt") rather than building blocks. Better to report no
        # components than noise.
        elif etype == EtymologyType.UNKNOWN and not (
            suffix or prefix or fugenelement
        ):
            components = []

        return EtymologyResult(
            type=etype,
            components=components,
            fugenelement=fugenelement,
            suffix=suffix,
            prefix=prefix,
            source_language=source_language,
        )

    def run(self) -> ParseEtymologyResult:
        return self.parse(self.entry.page.name, self.entry.wikitext)

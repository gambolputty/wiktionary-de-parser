"""Test data for ParseEtymology.

Each entry is a 3-tuple (lemma, wikitext, expected_dict). The lemma is needed
because the Verbherkunft template heuristic reconstructs the prefix from the
lemma rather than reading it from the wikitext. Wikitext snippets are
realistic excerpts drawn from the dewiktionary dump (with surrounding sections
trimmed for readability).
"""

from wiktionary_de_parser.models import EtymologyType


etymology_test_data: list[tuple[str, str, dict | None]] = [
    # ---- COMPOUND ----
    # Determinativkompositum with two components and explicit Fugenelement
    (
        "Geschichtswissenschaft",
        "{{Herkunft}}\n"
        ":[[Determinativkompositum]], zusammengesetzt aus dem Substantiv "
        "''[[Geschichte]]'', dem [[Fugenelement]] ''[[-s-]]'' und dem "
        "Substantiv ''[[Wissenschaft]]''\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.COMPOUND,
            "components": ["Geschichte", "Wissenschaft"],
            "fugenelement": "s",
            "suffix": None,
            "prefix": None,
            "source_language": None,
        },
    ),
    # Determinativkompositum with three components
    (
        "Adamsapfel",
        "{{Herkunft}}\n"
        ":[[Determinativkompositum]], zusammengesetzt aus ''[[Adam]],'' dem "
        "[[Fugenelement]] ''[[-s]]'' und ''[[Apfel]]''\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.COMPOUND,
            "components": ["Adam", "Apfel"],
            "fugenelement": "s",
            "suffix": None,
            "prefix": None,
            "source_language": None,
        },
    ),
    # Compound without explicit Determinativkompositum marker, plaintext only
    (
        "Salzsäure",
        "{{Herkunft}}\n"
        ":zusammengesetzt aus den Substantiven ''[[Salz]]'' und "
        "''[[Säure]]''\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.COMPOUND,
            "components": ["Salz", "Säure"],
            "fugenelement": None,
            "suffix": None,
            "prefix": None,
            "source_language": None,
        },
    ),
    # ---- DERIVATION ----
    # Suffix derivation
    (
        "lesbar",
        "{{Herkunft}}\n"
        ":[[Ableitung]] vom [[Stamm]] des [[Verb]]s ''[[lesen]]'' mit dem "
        "[[Suffix]] ''[[-bar]]''\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.DERIVATION,
            "components": ["lesen"],
            "fugenelement": None,
            "suffix": "bar",
            "prefix": None,
            "source_language": None,
        },
    ),
    # Prefix derivation
    (
        "Unglück",
        "{{Herkunft}}\n"
        ":[[Ableitung]] vom Substantiv ''[[Glück]]'' mit dem [[Präfix]] "
        "''[[un-]]''\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.DERIVATION,
            "components": ["Glück"],
            "fugenelement": None,
            "suffix": None,
            "prefix": "un",
            "source_language": None,
        },
    ),
    # ---- MOVIERUNG ----
    # Inline (Movierung) marker, suffix -in
    (
        "Geschichtswissenschaftlerin",
        "{{Herkunft}}\n"
        ":[[Ableitung]] (speziell [[Motion]], [[Movierung]]) zu "
        "[[Geschichtswissenschaftler]] mit dem [[Derivatem]] "
        "(hier: [[Suffix]]) ''[[-in]]''\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.MOVIERUNG,
            "components": ["Geschichtswissenschaftler"],
            "fugenelement": None,
            "suffix": "in",
            "prefix": None,
            "source_language": None,
        },
    ),
    # Movierung via plaintext "weibliche Form zu"
    (
        "Petra",
        "{{Herkunft}}\n:weibliche Form zu ''[[Peter]]''\n{{Synonyme}}",
        {
            "type": EtymologyType.MOVIERUNG,
            "components": ["Peter"],
            "fugenelement": None,
            "suffix": None,
            "prefix": None,
            "source_language": None,
        },
    ),
    # ---- CONVERSION ----
    # Konversion with explicit marker
    (
        "Retten",
        "{{Herkunft}}\n:[[Konversion]] von [[retten]]\n{{Synonyme}}",
        {
            "type": EtymologyType.CONVERSION,
            "components": ["retten"],
            "fugenelement": None,
            "suffix": None,
            "prefix": None,
            "source_language": None,
        },
    ),
    # Substantivierung (counts as CONVERSION)
    (
        "Wiedersehen",
        "{{Herkunft}}\n"
        ":Substantivierung des Verbs ''[[wiedersehen]]'' durch [[Konversion]]\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.CONVERSION,
            "components": ["wiedersehen"],
            "fugenelement": None,
            "suffix": None,
            "prefix": None,
            "source_language": None,
        },
    ),
    # ---- LOANWORD ----
    # Direct Entlehnung
    (
        "demonstrieren",
        "{{Herkunft}}\n"
        ":[[Entlehnung]] aus dem [[Latein]] ''demonstrare''\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.LOANWORD,
            "components": [],
            "fugenelement": None,
            "suffix": None,
            "prefix": None,
            "source_language": "Latein",
        },
    ),
    # Loanword chain: deepest source wins
    (
        "Affäre",
        "{{Herkunft}}\n"
        ":über das [[Französisch|französische]] ''affaire'' aus dem "
        "[[Latein|lateinischen]] ''ad facere''\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.LOANWORD,
            "components": [],
            "fugenelement": None,
            "suffix": None,
            "prefix": None,
            "source_language": "Latein",
        },
    ),
    # ---- SHORTENING ----
    (
        "TÜV",
        "{{Herkunft}}\n"
        ":[[Akronym]], zusammengesetzt aus den Anfangsbuchstaben von "
        "''Technischer Überwachungsverein''\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.SHORTENING,
            "components": [],
            "fugenelement": None,
            "suffix": None,
            "prefix": None,
            "source_language": None,
        },
    ),
    # Kontamination / blend → also SHORTENING in our schema
    (
        "Pokémon",
        "{{Herkunft}}\n"
        ":[[Kontamination]] aus den englischen Wörtern ''[[pocket]]'' und "
        "''[[monster]]''\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.SHORTENING,
            "components": ["pocket", "monster"],
            "fugenelement": None,
            "suffix": None,
            "prefix": None,
            "source_language": None,
        },
    ),
    # ---- VARIANT ----
    # Plaintext "Nebenform zu …" — no structural wikilink
    (
        "Geografie",
        "{{Herkunft}}\n:Nebenform zu ''[[Geographie]]''\n{{Synonyme}}",
        {
            "type": EtymologyType.VARIANT,
            "components": ["Geographie"],
            "fugenelement": None,
            "suffix": None,
            "prefix": None,
            "source_language": None,
        },
    ),
    # ---- VERBHERKUNFT TEMPLATE ----
    # W=Partikel → DERIVATION with prefix
    (
        "abbrechen",
        "{{Herkunft}}\n:{{Verbherkunft|W=Partikel}}\n{{Synonyme}}",
        {
            "type": EtymologyType.DERIVATION,
            "components": ["brechen"],
            "fugenelement": None,
            "suffix": None,
            "prefix": "ab",
            "source_language": None,
        },
    ),
    # Long prefix - longest-match
    (
        "auseinanderbrechen",
        "{{Herkunft}}\n:{{Verbherkunft|W=Partikel}}\n{{Synonyme}}",
        {
            "type": EtymologyType.DERIVATION,
            "components": ["brechen"],
            "fugenelement": None,
            "suffix": None,
            "prefix": "auseinander",
            "source_language": None,
        },
    ),
    # W=Adjektiv → COMPOUND
    (
        "freisprechen",
        "{{Herkunft}}\n:{{Verbherkunft|W=Adjektiv}}\n{{Synonyme}}",
        {
            "type": EtymologyType.COMPOUND,
            "components": ["frei", "sprechen"],
            "fugenelement": None,
            "suffix": None,
            "prefix": None,
            "source_language": None,
        },
    ),
    # ---- STRUKTURELL / ETYMOLOGISCH SPLIT ----
    # Should prefer the structural block
    (
        "Zoologin",
        "{{Herkunft}}\n"
        ":''[[strukturell]]:'' [[Ableitung]] ([[Motion]], [[Movierung]]) "
        "des Femininums aus der männlichen Form ''[[Zoologe]]'' mit dem "
        "[[Derivatem]] ([[Ableitungsmorphem]]) ''[[-in]]''\n"
        ":''[[etymologisch]]:'' aus dem Griechischen "
        "''λόγος'' „[[Wort]]“\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.MOVIERUNG,
            "components": ["Zoologe"],
            "fugenelement": None,
            "suffix": "in",
            "prefix": None,
            "source_language": None,
        },
    ),
    # ---- MULTI-SENSE ----
    # Pick the first sense block
    (
        "Maus",
        "{{Herkunft}}\n"
        ":[1] [[mittelhochdeutsch]], [[althochdeutsch]]: ''mūs,'' aus "
        "[[germanisch]]: ''*mūs-''\n"
        ":[2] [[Jugendsprache]] zwischen etwa 1900 und 1930 für ''[[Frau]]''\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.LOANWORD,
            "components": [],
            "fugenelement": None,
            "suffix": None,
            "prefix": None,
            "source_language": "Germanisch",
        },
    ),
    # ---- EMPTY / MISSING ----
    # No Herkunft section at all → None
    (
        "NoSection",
        "{{Bedeutungen}}\n:[1] foo\n{{Synonyme}}",
        None,
    ),
    # Section with only QS placeholder → UNKNOWN
    (
        "Empty",
        "{{Herkunft}}\n{{QS Herkunft|fehlt}}\n{{Synonyme}}",
        {
            "type": EtymologyType.UNKNOWN,
            "components": [],
            "fugenelement": None,
            "suffix": None,
            "prefix": None,
            "source_language": None,
        },
    ),
    # Section present but no recognisable pattern
    (
        "Cryptic",
        "{{Herkunft}}\n:???\n{{Synonyme}}",
        {
            "type": EtymologyType.UNKNOWN,
            "components": [],
            "fugenelement": None,
            "suffix": None,
            "prefix": None,
            "source_language": None,
        },
    ),
    # ---- REGRESSION TESTS ----
    # These guard fixes discovered during systematic bug hunting on the dump.
    # Each one corresponds to a real entry that misbehaved before a specific
    # heuristic was added.
    #
    # Hammer: section starts with "von …", no structural marker, but a clear
    # suffix is detected → upgrade UNKNOWN to DERIVATION.
    (
        "Hammer",
        "{{Herkunft}}\n"
        ":von ''[[Hamm]]'' mit dem [[Suffix]] ''[[-er]]'' abgeleitet\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.DERIVATION,
            "components": ["Hamm"],
            "fugenelement": None,
            "suffix": "er",
            "prefix": None,
            "source_language": None,
        },
    ),
    # Subfamilia: "abgeleitet von … {{Ü|la|…}}" looks like derivation but is
    # semantically a loanword (foreign base) → promote DERIVATION → LOANWORD,
    # wipe components (the [[unter]], [[Familie]] wikilinks are glosses).
    (
        "Subfamilia",
        "{{Herkunft}}\n"
        ":abgeleitet von den lateinischen Wörtern ''{{Ü|la|sub}}'' "
        "„[[unter]]“ und ''{{Ü|la|familia}}'' „[[Familie]]“\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.LOANWORD,
            "components": [],
            "fugenelement": None,
            "suffix": None,
            "prefix": None,
            "source_language": "Lateinisch",
        },
    ),
    # Subregnum: same as Subfamilia but without {{Ü|...}} templates — the
    # foreign-source signal comes from a plaintext "lateinisch" with a
    # declension ending. Regex must match "lateinisch" inside "lateinischen".
    (
        "Subregnum",
        "{{Herkunft}}\n"
        ":abgeleitet von lateinisch [[sub]] (= [[unter]]) und [[regnum]] "
        "(= Königreich)\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.LOANWORD,
            "components": [],
            "fugenelement": None,
            "suffix": None,
            "prefix": None,
            "source_language": "Lateinisch",
        },
    ),
    # Adamsapfel: multi-paragraph section. Only the first ":"-line carries
    # the structural composition; the rest is historical prose. Without
    # _select_first_line() this entry returned 20+ components from the prose.
    (
        "Adamsapfel",
        "{{Herkunft}}\n"
        ":[[Determinativkompositum]], zusammengesetzt aus ''[[Adam]],'' "
        "dem [[Fugenelement]] ''[[-s]]'' und ''[[Apfel]]''\n"
        ":Die Bezeichnung tritt zuerst im 15. Jahrhundert im Gebiet der "
        "[[romanisch]]en [[Sprache]]n auf …\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.COMPOUND,
            "components": ["Adam", "Apfel"],
            "fugenelement": "s",
            "suffix": None,
            "prefix": None,
            "source_language": None,
        },
    ),
    # Unterseeboot: [[Untersee-]] has a trailing hyphen and is initially
    # bucketed as a prefix; in a COMPOUND it must be promoted to the
    # leading component.
    (
        "Unterseeboot",
        "{{Herkunft}}\n"
        ":[[Zusammensetzung]] ([[Determinativkompositum]]) aus "
        "''[[Untersee-]]'' und ''[[Boot]]''\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.COMPOUND,
            "components": ["Untersee", "Boot"],
            "fugenelement": None,
            "suffix": None,
            "prefix": None,
            "source_language": None,
        },
    ),
    # Vexillologie: leading-hyphen bound lexeme [[-logie]] together with an
    # explicit Fugenelement [[-o-]]. The bound lexeme is *not* a true
    # suffix — it's a final component (gebundenes Lexem).
    (
        "Vexillologie",
        "{{Herkunft}}\n"
        ":[[Komposition]] aus dem [[Substantiv]] ''[[Vexillum]],'' dem "
        "[[Fugenelement]] ''[[-o-]]'' und dem [[Suffix]] ''[[-logie]]''\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.COMPOUND,
            "components": ["Vexillum", "logie"],
            "fugenelement": "o",
            "suffix": None,
            "prefix": None,
            "source_language": None,
        },
    ),
    # Önophilie: both parts are bound morphemes ([[öno-]] and [[-philie]]),
    # both belong in components — trailing-hyphen → leading component,
    # leading-hyphen with len>2 → trailing component (gebundenes Lexem).
    (
        "Önophilie",
        "{{Herkunft}}\n"
        ":[[Kompositum]] aus den [[gebundenes Lexem|gebundenen Lexemen]] "
        "[[öno-]] und [[-philie]]\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.COMPOUND,
            "components": ["öno", "philie"],
            "fugenelement": None,
            "suffix": None,
            "prefix": None,
            "source_language": None,
        },
    ),
    # Fernbedienung: Zusammenbildung is a phrase + suffix, classified as
    # DERIVATION (not COMPOUND) — the suffix slot must stay populated.
    (
        "Fernbedienung",
        "{{Herkunft}}\n"
        ":[[Zusammenbildung]] der Wortgruppe ''(etwas von) fern bedienen'' "
        "mit dem [[Derivatem]] ([[Ableitungsmorphem]]) ''[[-ung]]''\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.DERIVATION,
            "components": [],
            "fugenelement": None,
            "suffix": "ung",
            "prefix": None,
            "source_language": None,
        },
    ),
    # Weihnachtsbaum: uses "*''strukturell:''" with a bullet-star instead
    # of ":''strukturell:''" — the structural-block selector must match both.
    (
        "Weihnachtsbaum",
        "{{Herkunft}}\n"
        "*''strukturell:''\n"
        ":[[Determinativkompositum]] aus dem [[Substantiv]] "
        "''[[Weihnacht]],'' dem [[Fugenelement]] ''[[-s]]'' und dem "
        "Substantiv ''[[Baum]]''\n"
        "*''[[etymologisch]]:''\n"
        ":[1] Laut Kluge älteste Belege im 16. Jahrhundert …\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.COMPOUND,
            "components": ["Weihnacht", "Baum"],
            "fugenelement": "s",
            "suffix": None,
            "prefix": None,
            "source_language": None,
        },
    ),
    # einwandfrei: [[frei]] and [[-frei]] both appear; the latter must not
    # be appended again as a duplicate component.
    (
        "einwandfrei",
        "{{Herkunft}}\n"
        ":[[Kompositum]] aus dem [[Substantiv]] „[[Einwand]]“ und dem "
        "Adjektiv „[[frei]]“ (oder der zugehörigen Endung „[[-frei]]“)\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.COMPOUND,
            "components": ["Einwand", "frei"],
            "fugenelement": None,
            "suffix": None,
            "prefix": None,
            "source_language": None,
        },
    ),
    # Erschließung: a Wiktionary typo gives "[[(-ung]]" with a stray
    # opening paren in the link target. That's never a real lemma — skip.
    (
        "Erschließung",
        "{{Herkunft}}\n"
        ":[[Derivation]]/[[Ableitung]], vom Stamm des Verbs "
        "''[[erschließen]]'' zum Substantiv mit Suffigierung durch "
        "[[Derivatem]] ([[Ableitungsmorphem]]) ''[[(-ung]]''\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.DERIVATION,
            "components": ["erschließen"],
            "fugenelement": None,
            "suffix": None,
            "prefix": None,
            "source_language": None,
        },
    ),
    # Wetter: reconstructed form "*[[wedra-]]" looks like a prefix wikilink,
    # but the language signal ([[mittelhochdeutsch]], [[althochdeutsch]],
    # [[germanisch]]) plus {{Ü|...}} templates makes it an Erbwort →
    # LOANWORD, no prefix.
    (
        "Wetter",
        "{{Herkunft}}\n"
        ":[[mittelhochdeutsch]] ''{{Ü|gmh|weter}}'', [[althochdeutsch]] "
        "''{{Ü|goh|wetar}}'', [[germanisch]] ''*[[wedra-]]'' „Wetter“\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.LOANWORD,
            "components": [],
            "fugenelement": None,
            "suffix": None,
            "prefix": None,
            "source_language": "Germanisch",
        },
    ),
    # Mensch: CONVERSION + {{Ü|...}} → the [[menschlich]], [[mannhaft]]
    # wikilinks are glosses, not components.
    (
        "Mensch",
        "{{Herkunft}}\n"
        ":[[mittelhochdeutsch]] ''{{Ü|gmh|mensch}}'' durch "
        "[[Substantivierung]] von ''{{Ü|goh|mennisc}}'' "
        "„[[menschlich]], [[mannhaft]]“\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.CONVERSION,
            "components": [],
            "fugenelement": None,
            "suffix": None,
            "prefix": None,
            "source_language": None,
        },
    ),
    # Ärztin: [[Umlaut]] is terminology and must not appear in components.
    (
        "Ärztin",
        "{{Herkunft}}\n"
        ":[[Ableitung]] ([[Motion]], [[Movierung]]) von ''[[Arzt]]'' mit "
        "dem [[Derivatem]] ([[Ableitungsmorphem]]) ''[[-in]]'' "
        "(und zusätzlichem [[Umlaut]])\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.MOVIERUNG,
            "components": ["Arzt"],
            "fugenelement": None,
            "suffix": "in",
            "prefix": None,
            "source_language": None,
        },
    ),
    # Land: reconstructed-form wikilink with namespace prefix
    # ("Rekonstruktion:Urgermanisch/landa") must not leak as a prefix; the
    # final result is a LOANWORD with prefix/suffix wiped. The deepest
    # language wikilink is [[urgermanisch]], so that's the source_language.
    (
        "Land",
        "{{Herkunft}}\n"
        ":[[Erbwort]] aus dem [[mittelhochdeutsch]]en ''{{Ü|gmh|lant}}'', "
        "das auf das [[urgermanisch]]e "
        "''[[Rekonstruktion:Urgermanisch/landa]]'' zurückgeht\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.LOANWORD,
            "components": [],
            "fugenelement": None,
            "suffix": None,
            "prefix": None,
            "source_language": "Urgermanisch",
        },
    ),
    # 8-seitig: numeric wikilink [[8]] is a legitimate component for
    # numeric-prefixed lemmas — must NOT be filtered out by the
    # single-letter heuristic (which only removes alphabetic 1-chars).
    (
        "8-seitig",
        "{{Herkunft}}\n"
        ":[[Ziffer]] ''[[8]]'', Substantiv ''[[Seite]]'' und [[Suffix]] "
        "''[[-ig]]''\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.DERIVATION,
            "components": ["8", "Seite"],
            "fugenelement": None,
            "suffix": "ig",
            "prefix": None,
            "source_language": None,
        },
    ),
    # Sensenmann: [[Mann]] is a legitimate compound component, not a gloss.
    # Guards against over-eager filtering of common gloss tokens.
    (
        "Sensenmann",
        "{{Herkunft}}\n"
        ":[[Determinativkompositum]], zusammengesetzt aus ''[[Sense]],'' "
        "[[Fugenelement]] ''[[-n]]'' und ''[[Mann]]''\n"
        "{{Synonyme}}",
        {
            "type": EtymologyType.COMPOUND,
            "components": ["Sense", "Mann"],
            "fugenelement": "n",
            "suffix": None,
            "prefix": None,
            "source_language": None,
        },
    ),
]

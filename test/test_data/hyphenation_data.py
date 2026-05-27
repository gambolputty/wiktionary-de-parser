hyphenation_data = [
    (
        "gesagt, getan",
        """
{{Worttrennung}}
:ge·sagt, ge·tan
""",
        ["ge", "sagt", "ge", "tan"],
    ),
    (
        "Ton",
        """
{{Worttrennung}}
:Ton {{Pl.}} To·ne
        """,
        ["Ton"],
    ),
    (
        "neunzehn",
        """
{{Worttrennung}}
:neun·zehn
        """,
        ["neun", "zehn"],
    ),
    (
        "bald",
        """
{{Worttrennung}}
:bald, {{Komp.}} bäl·der, eher, {{Sup.}} am bäl·des·ten, am ehes·ten
        """,
        ["bald"],
    ),
    (
        "zwanzig",
        """
{{Worttrennung}}
:zwan·zig, zwan·zi·ge
        """,
        ["zwan", "zig"],
    ),
    (
        "reden",
        """
{{Worttrennung}}
:re·den, {{Prät.}} re·de·te, {{Part.}} ge·re·det

        """,
        ["re", "den"],
    ),
    (
        "dreißig",
        """
{{Worttrennung}}
:drei·ßig, ''[[veraltend]]:'' drei·ßi·ge
        """,
        ["drei", "ßig"],
    ),
    (
        "einundzwanzig",
        """
{{Worttrennung}}
:ein·und·zwan·zig
        """,
        ["ein", "und", "zwan", "zig"],
    ),
    (
        "Melone",
        """
{{Worttrennung}}
:Me·lo·ne, {{Pl.}} Me·lo·nen
        """,
        ["Me", "lo", "ne"],
    ),
    (
        "Narr",
        """
{{Worttrennung}}
:Narr, {{Pl.}} Nar·ren
        """,
        ["Narr"],
    ),
    (
        "Vereinte Nationen",
        """
{{Worttrennung}}
:{{kSg.}}, Ver·ein·te Na·ti·o·nen
        """,
        ["Ver", "ein", "te", "Na", "ti", "o", "nen"],
    ),
    (
        "Mückenstich",
        """
{{Worttrennung}}
:''Neue Worttrennung:'' Mü·cken·stich, {{Pl.}} Mü·cken·sti·che
:''Alte Worttrennung:'' Mük·ken·stich, {{Pl.}} Mük·ken·sti·che
        """,
        ["Mü", "cken", "stich"],
    ),
    (
        "Liebeskummer",
        """
{{Worttrennung}}
:Lie·bes·kum·mer, {{kPl.}}
        """,
        ["Lie", "bes", "kum", "mer"],
    ),
    (
        "Packerin",
        """
{{Worttrennung}}
:Pa·cke·rin, {{Pl.}} Pa·cke·rin·nen
        """,
        ["Pa", "cke", "rin"],
    ),
    (
        "palavern",
        """
{{Worttrennung}}
:pa·la·vern, {{Prät.}} pa·la·ver·te, {{Part.}} pa·la·vert
        """,
        ["pa", "la", "vern"],
    ),
    (
        "Tollpatsch",
        """
{{Worttrennung}}
:Toll·patsch, {{Pl.}} Toll·pat·sche
        """,
        ["Toll", "patsch"],
    ),
    (
        "Irgendwas",
        """
{{Worttrennung}}
:, {{Pl.}}
        """,
        None,
    ),
    (
        "einwirken",
        """
{{Worttrennung}}
:
:ein·wir·ken, {{Prät.}} wirk·te ein, {{Part.}} ein·ge·wirkt
        """,
        ["ein", "wir", "ken"],
    ),
    (
        "nutzlose",
        """
{{Worttrennung}}
:·nutz·lo·se
        """,
        ["nutz", "lo", "se"],
    ),
    (
        "mitgegangen, mitgefangen",
        """
{{Worttrennung}}
:·mit·ge·gan·gen, mit·ge·fan·gen
        """,
        ["mit", "ge", "gan", "gen", "mit", "ge", "fan", "gen"],
    ),
    (
        "A",
        """
{{Worttrennung}}
:A, {{Pl.}} A, {{ugs.}} As
        """,
        ["A"],
    ),
    (
        "X",
        """
{{Worttrennung}}
:X, {{Pl.1}} X, ''ausschließlich umgangssprachlich:'' {{Pl.2}} Xe
        """,
        ["X"],
    ),
    (
        "Intelligenzquotient",
        """
{{Worttrennung}}
:In·tel·li·genz·quo·ti·ent; {{Pl.}} In·tel·li·genz·quo·ti·en·ten
        """,
        ["In", "tel", "li", "genz", "quo", "ti", "ent"],
    ),
    (
        "bisexuell",
        """
{{Worttrennung}}
:bi·se·xu·ell, {{kSt.}}
        """,
        ["bi", "se", "xu", "ell"],
    ),
    (
        "ziehen",
        """
{{Worttrennung}}
:zie·hen, {{Prät.}} zog, {{Part.}} ge·zo·gen
        """,
        ["zie", "hen"],
    ),
    # ── Affix markers — the trailing/leading hyphen on the lemma is a
    # semantic marker (prefix / suffix / fugenelement) and must survive
    # the syllable split.
    (
        "auto-",
        """
{{Worttrennung}}
:au·to-
        """,
        ["au", "to-"],
    ),
    (
        "-ow",
        """
{{Worttrennung}}
:-ow
        """,
        ["-ow"],
    ),
    (
        "stief-",
        """
{{Worttrennung}}
:stief-
        """,
        ["stief-"],
    ),
    (
        "-s-",
        """
{{Worttrennung}}
:-s-
        """,
        ["-s-"],
    ),
    # ── Hyphenated compounds — hyphen acts as a syllable boundary for
    # mono-syllabic components (no mid-dot needed). Output must remain
    # the flat list it was before the affix fix.
    (
        "E-Mail",
        """
{{Worttrennung}}
:E-Mail, {{Pl.}} E-Mails
        """,
        ["E", "Mail"],
    ),
    (
        "Audio-Designer",
        """
{{Worttrennung}}
:Au·dio-De·sig·ner
        """,
        ["Au", "dio", "De", "sig", "ner"],
    ),
    # H_BUG1 — lemma wrapped in a wikitext template ({{Polytonisch|ἡ}}).
    # Off-by-one in the char-walk used to include the trailing `}` in the
    # syllable; the bracket-strip in re.sub fixes it.
    (
        "ἡ",
        """
{{Worttrennung}}
:{{Polytonisch|ἡ}}
        """,
        ["ἡ"],
    ),
    # HYPH_BUG2 — minimal worttrennung followed by newline.
    (
        "A",
        """{{Worttrennung}}
:A
""",
        ["A"],
    ),
    # HYPH_BUG3 — chemical names with commas inside the lemma.
    # The comma is part of the lemma, not a word separator.
    (
        "1,2,3-Propentricarbonsäure",
        """{{Worttrennung}}
:1,2,3-Pro·pen·tri·car·bon·säu·re
""",
        ["1,2,3", "Pro", "pen", "tri", "car", "bon", "säu", "re"],
    ),
    # Web 2.0 — dot between digits, part of the lemma.
    (
        "Web 2.0",
        """{{Worttrennung}}
:Web 2.0
""",
        ["Web", "2.0"],
    ),
    # Code-review #2 finding 6 — abbreviations that end with a dot must
    # keep their trailing dot. `rstrip(",.;:")` used to strip it blindly
    # even when the lemma itself ended with the dot. Now only chars not
    # in the lemma's own suffix are stripped.
    (
        "Mr.",
        """{{Worttrennung}}
:Mr.
""",
        ["Mr."],
    ),
    (
        "etc.",
        """{{Worttrennung}}
:etc.
""",
        ["etc."],
    ),
]

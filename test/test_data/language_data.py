lang_test_data = [
    (
        """
{{Siehe auch|[[jähr]]}}
{{Wort der Woche|1|2006}}
== Jahr ({{Sprache|Deutsch}}) ==
=== {{Wortart|Substantiv|Deutsch}}, {{n}} ===
        """,
        {"lang": "Deutsch", "lang_code": "de"},
    ),
    (
        """
== seltsam ({{Sprache|Deutsch}}) ==
=== {{Wortart|Adjektiv|Deutsch}} ===

{{Deutsch Adjektiv Übersicht
|Positiv=seltsam
|Komparativ=seltsamer
|Superlativ=seltsamsten
}}
        """,
        {"lang": "Deutsch", "lang_code": "de"},
    ),
    (
        """
{{Siehe auch|[[Break]]}}
== break ({{Sprache|Englisch}}) ==
=== {{Wortart|Verb|Englisch}}, unregelmäßig ===

{{Englisch Verb Übersicht
|present_I=break
|present_he, she, it=breaks
|past_simple_I=broke
|present participle=breaking
|past participle=broken
}}
        """,
        {"lang": "Englisch", "lang_code": "en"},
    ),
    (
        """

=== {{Wortart|Substantiv|Englisch}} ===

{{Englisch Substantiv Übersicht
|Singular=break
|Plural=breaks
}}
        """,
        {"lang": "Englisch", "lang_code": "en"},
    ),
    # LANG_BUG1 — second positional missing because second slot is the
    # named param `spr=en`. Must return None (no language) rather than
    # capturing "spr=en" as the language name.
    (
        """
=== {{Wortart|Substantiv|spr=en}} ===
        """,
        {"lang": None, "lang_code": None},
    ),
    # Code-review finding 1 — Italian-style headers put the lemma before
    # the Wortart template. parse_language must extract the second
    # positional from inside the {{Wortart}} template, not from the regex
    # capture group.
    (
        """
=== ombrello {{Wortart|Substantiv|Italienisch}}, {{m}} ===
        """,
        {"lang": "Italienisch", "lang_code": "it"},
    ),
    # Double-space variant — same tolerance as entries_from_page.
    (
        """
===  {{Wortart|Substantiv|Französisch}}, {{f}}  ===
        """,
        {"lang": "Französisch", "lang_code": "fr"},
    ),
    # Code-review finding 11 — `|2=Englisch` (explicit numeric-named) must
    # be treated as the second positional, equivalent to a bare positional.
    (
        """
=== {{Wortart|Substantiv|2=Englisch}} ===
        """,
        {"lang": "Englisch", "lang_code": "en"},
    ),
    # Code-review #2 finding 7 — source-order differs from numeric position.
    # `|2=Englisch` is explicit position 2; the bare `Substantiv` becomes
    # position 1 (counter starts at 0, incremented by bare positionals).
    # MediaWiki semantics: numeric position wins over source order.
    (
        """
=== {{Wortart|2=Englisch|Substantiv}} ===
        """,
        {"lang": "Englisch", "lang_code": "en"},
    ),
]

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
]

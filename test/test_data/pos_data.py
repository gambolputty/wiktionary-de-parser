pos_test_data = [
    (
        """
== weißes Gold ({{Sprache|Deutsch}}) ==
=== {{Wortart|Wortverbindung|Deutsch}}, {{n}}, {{adjektivische Deklination}} ===

{{Deutsch adjektivisch Übersicht
|Genus=n
|kein Plural=1
|Nominativ Singular stark=weißes Gold
|Genitiv Singular stark=weißen Golds
|Genitiv Singular stark*=weißen Goldes
|Dativ Singular stark=weißem Gold
|Dativ Singular stark*=weißem Golde
|Akkusativ Singular stark=weißes Gold
|Nominativ Singular schwach=weiße Gold
|Genitiv Singular schwach=weißen Golds
|Genitiv Singular schwach*=weißen Goldes
|Dativ Singular schwach=weißen Gold
|Dativ Singular schwach*=weißen Golde
|Akkusativ Singular schwach=weiße Gold
|Nominativ Singular gemischt=weißes Gold
|Genitiv Singular gemischt=weißen Golds
|Genitiv Singular gemischt*=weißen Goldes
|Dativ Singular gemischt=weißen Gold
|Dativ Singular gemischt*=weißen Golde
|Akkusativ Singular gemischt=weißes Gold
}}
        """,
        {"Substantiv": ["adjektivische Deklination"], "Wortverbindung": []},
    ),
    (
        """
== Fragesteller ({{Sprache|Deutsch}}) ==
=== {{Wortart|Substantiv|Deutsch}}, {{m}} ===

{{Deutsch Substantiv Übersicht
|Genus=m
|Nominativ Singular=Fragesteller
|Nominativ Plural=Fragesteller
|Genitiv Singular=Fragestellers
|Genitiv Plural=Fragesteller
|Dativ Singular=Fragesteller
|Dativ Plural=Fragestellern
|Akkusativ Singular=Fragesteller
|Akkusativ Plural=Fragesteller
}}

{{Worttrennung}}
:Fra·ge·stel·ler, {{Pl.}} Fra·ge·stel·ler

""",
        {"Substantiv": []},
    ),
    (
        """
{Siehe auch|[[verdächtiger]]}}
== Verdächtiger ({{Sprache|Deutsch}}) ==
=== {{Wortart|Substantiv|Deutsch}}, {{m}}, {{adjektivische Deklination}} ===

{{Deutsch adjektivisch Übersicht
|Genus=m
|Stamm=Verdächtige
}}

""",
        {"Substantiv": ["adjektivische Deklination"]},
    ),
    (
        """
{{Zeichen|P|3=#FFC1C1;}}
== P ({{Sprache|Deutsch}}) ==
=== {{Wortart|Substantiv|Deutsch}}, {{n}}, {{Wortart|Buchstabe|Deutsch}} ===

{{Deutsch Substantiv Übersicht
|Genus=n
|Nominativ Singular=P
|Nominativ Plural=P
|Nominativ Plural*=Ps
|Genitiv Singular=P
|Genitiv Singular*=Ps
|Genitiv Plural=P
|Genitiv Plural*=Ps
|Dativ Singular=P
|Dativ Plural=P
|Dativ Plural*=Ps
|Akkusativ Singular=P
|Akkusativ Plural=P
|Akkusativ Plural*=Ps
}}
""",
        {"Substantiv": [], "Symbol": ["Buchstabe"]},
    ),
    (
        """
== vollständig ({{Sprache|Deutsch}}) ==
=== {{Wortart|Adjektiv|Deutsch}} ===

{{Deutsch Adjektiv Übersicht
|Positiv=vollständig
|Komparativ=vollständiger
|Superlativ=vollständigsten
}}
""",
        {"Adjektiv": []},
    ),
    (
        """
{{Siehe auch|[[Pflanzen]]}}
== pflanzen ({{Sprache|Deutsch}}) ==
=== {{Wortart|Verb|Deutsch}} ===

{{Deutsch Verb Übersicht
|Präsens_ich=pflanze
|Präsens_du=pflanzt
|Präsens_er, sie, es=pflanzt
|Präteritum_ich=pflanzte
|Partizip II=gepflanzt
|Konjunktiv II_ich=pflanzte
|Imperativ Singular=pflanze
|Imperativ Singular*=pflanz
|Imperativ Plural=pflanzt
|Imperativ Plural*=pflanzet
|Hilfsverb=haben
|Bild 1=DSC 0912 (4996034567).jpg|mini|1|''Pflanzen'' einer [[Kastanie]]
|Bild 2=HUERTO ESCOLAR 011 (2).jpg|mini|1|[[Kind]]er ''pflanzen'' [[Salat]]
|Bild 3=India - Sights & Culture - Planting Rice Paddy 5 (3245008474).jpg|mini|1|''Pflanzen'' von [[Reis]]
|Bild 4=Ap14 flag.ogv|mini|2|[[Astronaut]]en von [[w:Apollo 14|Apollo 14]] ''pflanzen'' auf dem [[Mond]] die US-[[Flagge]]
}}
""",
        {"Verb": []},
    ),
]

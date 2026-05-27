tables = [
    # "Stamm" & "kein Plural" in one line
    (
        """{{Deutsch adjektivisch Übersicht
|Genus=n
|Stamm=Tausendfache|kein Plural=ja
}}""",
        {"Genus": "n", "Stamm": "Tausendfache", "kein Plural": "ja"},
    ),
    (
        """{{Deutsch adjektivisch Übersicht
|Genus=n
|Stamm=Bare|kein Plural=ja
}}""",
        {"Genus": "n", "Stamm": "Bare", "kein Plural": "ja"},
    ),
    (
        """{{Deutsch adjektivisch Übersicht
|Genus=m
|Nominativ Singular stark=falscher Hase
|Nominativ Plural stark=falsche Hasen
|Genitiv Singular stark=falschen Hasen
|Genitiv Plural stark=falscher Hasen
|Dativ Singular stark=falschem Hasen
|Dativ Plural stark=falschen Hasen
|Akkusativ Singular stark=falschen Hasen
|Akkusativ Plural stark=falsche Hasen
|Nominativ Singular schwach=falsche Hase
|Nominativ Plural schwach=falschen Hasen
|Genitiv Singular schwach=falschen Hasen
|Genitiv Plural schwach=falschen Hasen
|Dativ Singular schwach=falschen Hasen
|Dativ Plural schwach=falschen Hasen
|Akkusativ Singular schwach=falschen Hasen
|Akkusativ Plural schwach=falschen Hasen
|Nominativ Singular gemischt=falscher Hase
|Nominativ Plural gemischt=falschen Hasen
|Genitiv Singular gemischt=falschen Hasen
|Genitiv Plural gemischt=falschen Hasen
|Dativ Singular gemischt=falschen Hasen
|Dativ Plural gemischt=falschen Hasen
|Akkusativ Singular gemischt=falschen Hasen
|Akkusativ Plural gemischt=falschen Hasen
|Bild=Hackbraten01.jpg
|Bildbreite=mini
|Bildbezug=1
|Bildbeschreibung=''falscher Hase''
}}""",
        {
            "Genus": "m",
            "Nominativ Singular stark": "falscher Hase",
            "Nominativ Plural stark": "falsche Hasen",
            "Genitiv Singular stark": "falschen Hasen",
            "Genitiv Plural stark": "falscher Hasen",
            "Dativ Singular stark": "falschem Hasen",
            "Dativ Plural stark": "falschen Hasen",
            "Akkusativ Singular stark": "falschen Hasen",
            "Akkusativ Plural stark": "falsche Hasen",
            "Nominativ Singular schwach": "falsche Hase",
            "Nominativ Plural schwach": "falschen Hasen",
            "Genitiv Singular schwach": "falschen Hasen",
            "Genitiv Plural schwach": "falschen Hasen",
            "Dativ Singular schwach": "falschen Hasen",
            "Dativ Plural schwach": "falschen Hasen",
            "Akkusativ Singular schwach": "falschen Hasen",
            "Akkusativ Plural schwach": "falschen Hasen",
            "Nominativ Singular gemischt": "falscher Hase",
            "Nominativ Plural gemischt": "falschen Hasen",
            "Genitiv Singular gemischt": "falschen Hasen",
            "Genitiv Plural gemischt": "falschen Hasen",
            "Dativ Singular gemischt": "falschen Hasen",
            "Dativ Plural gemischt": "falschen Hasen",
            "Akkusativ Singular gemischt": "falschen Hasen",
            "Akkusativ Plural gemischt": "falschen Hasen",
        },
    ),
    (
        """{{Deutsch adjektivisch Übersicht
|Genus=f
|kein Plural=1
|Nominativ Singular stark=Russische Föderation
|Genitiv Singular stark=Russischer Föderation
|Dativ Singular stark=Russischer Föderation
|Akkusativ Singular stark=Russische Föderation
|Nominativ Singular schwach=Russische Föderation
|Genitiv Singular schwach= Russischen Föderation
|Dativ Singular schwach=Russischen Föderation
|Akkusativ Singular schwach=Russische Föderation
|Nominativ Singular gemischt=Russische Föderation
|Genitiv Singular gemischt=Russischen Föderation
|Dativ Singular gemischt= Russischen Föderation
|Akkusativ Singular gemischt= Russische Föderation
|Bild=Map_of_subdivisions_of_Russia.svg|mini|1|Politische Gliederung der ''Russischen Föderation''
}}""",
        {
            "Genus": "f",
            "kein Plural": "1",
            "Nominativ Singular stark": "Russische Föderation",
            "Genitiv Singular stark": "Russischer Föderation",
            "Dativ Singular stark": "Russischer Föderation",
            "Akkusativ Singular stark": "Russische Föderation",
            "Nominativ Singular schwach": "Russische Föderation",
            "Genitiv Singular schwach": "Russischen Föderation",
            "Dativ Singular schwach": "Russischen Föderation",
            "Akkusativ Singular schwach": "Russische Föderation",
            "Nominativ Singular gemischt": "Russische Föderation",
            "Genitiv Singular gemischt": "Russischen Föderation",
            "Dativ Singular gemischt": "Russischen Föderation",
            "Akkusativ Singular gemischt": "Russische Föderation",
        },
    ),
    (
        """{{Deutsch Substantiv Übersicht
|Genus=f
|Nominativ Singular=Alternative
|Nominativ Plural=Alternativen
|Genitiv Singular=Alternative
|Genitiv Plural=Alternativen
|Dativ Singular=Alternative
|Dativ Plural=Alternativen
|Akkusativ Singular=Alternative
|Akkusativ Plural=Alternativen
}}""",
        {
            "Genus": "f",
            "Nominativ Singular": "Alternative",
            "Nominativ Plural": "Alternativen",
            "Genitiv Singular": "Alternative",
            "Genitiv Plural": "Alternativen",
            "Dativ Singular": "Alternative",
            "Dativ Plural": "Alternativen",
            "Akkusativ Singular": "Alternative",
            "Akkusativ Plural": "Alternativen",
        },
    ),
    (
        """{{Deutsch Substantiv Übersicht
|Genus=n
|Nominativ Singular=Frauenzimmer
|Nominativ Plural=Frauenzimmer
|Genitiv Singular=Frauenzimmers
|Genitiv Plural=Frauenzimmer
|Dativ Singular=Frauenzimmer
|Dativ Plural=Frauenzimmern
|Akkusativ Singular=Frauenzimmer
|Akkusativ Plural=Frauenzimmer}}""",  # brackets on the last line
        {
            "Genus": "n",
            "Nominativ Singular": "Frauenzimmer",
            "Nominativ Plural": "Frauenzimmer",
            "Genitiv Singular": "Frauenzimmers",
            "Genitiv Plural": "Frauenzimmer",
            "Dativ Singular": "Frauenzimmer",
            "Dativ Plural": "Frauenzimmern",
            "Akkusativ Singular": "Frauenzimmer",
            "Akkusativ Plural": "Frauenzimmer",
        },
    ),
    (
        """{{Deutsch Substantiv Übersicht
|Genus=m
|Nominativ Singular=Alf
|Nominativ Plural=?
|Genitiv Singular=Alfs
|Genitiv Singular*=Alfes
|Genitiv Plural=?
|Dativ Singular=Alf
|Dativ Singular*=Alfe
|Dativ Plural=?
|Akkusativ Singular=Alf
|Akkusativ Plural=?
}}""",
        {
            "Genus": "m",
            "Nominativ Singular": "Alf",
            "Genitiv Singular": "Alfs",
            "Genitiv Singular*": "Alfes",
            "Dativ Singular": "Alf",
            "Dativ Singular*": "Alfe",
            "Akkusativ Singular": "Alf",
        },
    ),
    # Bug D — table with nested templates (e.g. {{Per-Deutschlandradio|…}}
    # inside |Bild=). With the old regex-based find_table the result was
    # truncated at the first inner `}`. All Kasus-fields must survive now.
    (
        """{{Deutsch Substantiv Übersicht
|Genus=f
|Nominativ Singular=Hand
|Nominativ Plural=Hände
|Genitiv Singular=Hand
|Genitiv Plural=Hände
|Dativ Singular=Hand
|Dativ Plural=Händen
|Akkusativ Singular=Hand
|Akkusativ Plural=Hände
|Bild=Mosaic of Christ.jpg|mini|1|{{Per-Deutschlandradio|Online|Beispieltext|Autor|Titel|Tag|Monat|Jahr|Zugriff|Kommentar}}
}}""",
        {
            "Genus": "f",
            "Nominativ Singular": "Hand",
            "Nominativ Plural": "Hände",
            "Genitiv Singular": "Hand",
            "Genitiv Plural": "Hände",
            "Dativ Singular": "Hand",
            "Dativ Plural": "Händen",
            "Akkusativ Singular": "Hand",
            "Akkusativ Plural": "Hände",
        },
    ),
    # F1 — nested {{Per-Deutsche Welle|Autor=…|Titel=…}} inside |Bild=
    # caption must NOT leak its named params as table fields.
    (
        """{{Deutsch Substantiv Übersicht
|Genus=f
|Nominativ Singular=Geothermie
|Genitiv Singular=Geothermie
|Dativ Singular=Geothermie
|Akkusativ Singular=Geothermie
|Bild 1=Erdwaermesondenbohrung01.JPG|mini|1|„Bohrung"<ref name="dw_01" >{{Per-Deutsche Welle | Online=https://p.dw.com/p/46SBc | Autor=Jan D. Walter | Titel=Energiewende | Tag=04 | Monat=02 | Jahr=2022 | Zugriff=2022-08-14 }}</ref>
}}""",
        {
            "Genus": "f",
            "Nominativ Singular": "Geothermie",
            "Genitiv Singular": "Geothermie",
            "Dativ Singular": "Geothermie",
            "Akkusativ Singular": "Geothermie",
        },
    ),
    # F2 — broken Übersicht with only numeric keys (Kyoto wikitext)
    # produces None instead of {'3': "''Kyoto''", '2': '1'}.
    (
        """{{Deutsch Toponym Übersicht
|Bild=Kyoto_city1.jpg|3=''Kyoto''|2=1
}}""",
        None,
    ),
    # Code-review finding 4 — multi-line `<ref>` inside a cell value.
    # Without DOTALL on the tag-stripper the ref body and the trailing
    # `</ref>` leaked into the cell text.
    (
        """{{Deutsch Substantiv Übersicht
|Genus=f
|Nominativ Singular=Hand<ref>source line 1
source line 2</ref>
|Nominativ Plural=Hände
|Genitiv Singular=Hand
|Genitiv Plural=Hände
|Dativ Singular=Hand
|Dativ Plural=Händen
|Akkusativ Singular=Hand
|Akkusativ Plural=Hände
}}""",
        {
            "Genus": "f",
            "Nominativ Singular": "Hand",
            "Nominativ Plural": "Hände",
            "Genitiv Singular": "Hand",
            "Genitiv Plural": "Hände",
            "Dativ Singular": "Hand",
            "Dativ Plural": "Händen",
            "Akkusativ Singular": "Hand",
            "Akkusativ Plural": "Hände",
        },
    ),
    # Code-review #2 finding 4 — same over-match issue as in wiki_list:
    # a self-closing `<ref name="x"/>` paired with a later unrelated
    # `</sup>` would delete cell content between them. The backreference
    # in `<(\w+)…</\1>` requires the closer to match the opener.
    (
        """{{Deutsch Substantiv Übersicht
|Genus=m
|Nominativ Singular=Test<ref name="x"/><sup>1</sup>
|Nominativ Plural=Tests
|Genitiv Singular=Tests
|Genitiv Plural=Tests
|Dativ Singular=Test
|Dativ Plural=Tests
|Akkusativ Singular=Test
|Akkusativ Plural=Tests
}}""",
        {
            "Genus": "m",
            "Nominativ Singular": "Test",
            "Nominativ Plural": "Tests",
            "Genitiv Singular": "Tests",
            "Genitiv Plural": "Tests",
            "Dativ Singular": "Test",
            "Dativ Plural": "Tests",
            "Akkusativ Singular": "Test",
            "Akkusativ Plural": "Tests",
        },
    ),
]

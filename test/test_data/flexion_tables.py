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
]

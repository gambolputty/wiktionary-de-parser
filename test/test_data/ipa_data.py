ipa_test_data = [
    (
        """
{{Aussprache}}
:{{IPA}} ein {{Lautschrift|ˈaltɐ}}
:{{Hörbeispiele}} {{Audio|De-Alter.ogg}}
:{{Reime}} {{Reim|altɐ|Deutsch}}
        """,
        ["ˈaltɐ"],
    ),
    (
        """
{{Aussprache}}
:{{IPA}} {{Lautschrift||spr=la}}
:{{Hörbeispiele}} {{Audio|La-cls-species.ogg|spr=cls}} und {{Audio|La-ecc-species.ogg|spr=ecc}}
        """,
        None,
    ),
    (
        """
{{Aussprache}}
:{{IPA}} {{Lautschrift|oˈʁɑ̃ːʒə}}<ref name="DAW">{{Lit-Duden: Aussprachewörterbuch|A=7}}, Stichwort »¹Orange ''(Frucht)''«, Seite 651.</ref>
::''standardsprachlich besonders'' {{nordd.|,}} ''[[ostdeutsch]] und'' {{schweiz.}} ''auch:'' {{Lautschrift|oˈʁaŋʒə}}<ref name="DAW"/>
::''standardsprachlich'' {{südd.|}} ''und'' {{österr.}} ''auch:'' {{Lautschrift|oˈʁanʒə}}<ref name="DAW"/>
::''standardsprachlich'' {{schweiz.}} ''auch:'' {{Lautschrift|oˈʁanʒ̊ə}}<ref name="dGDW">{{Lit-De Gruyter: Deutsches Aussprachewörterbuch|A=1}}, Stichpunkt »C. 3 Wortliste«, Seite 275.</ref>, ''zumeist:'' {{Lautschrift|ˈoʁanʒ̊ə}}<ref name="dGDW"/><ref name="DAW"/>
:{{Hörbeispiele}} {{Audio|De-Orange.ogg|{{Lautschrift|oˈʁɑ̃ːʒə}}}}, {{Audio|De-Orange4.ogg|{{Lautschrift|oˈʁɑ̃ːʒə}}}}, {{Audio|De-Orange2.ogg|{{Lautschrift|oˈʁaŋʒə}}}}
:{{Reime}} {{Reim|ɑ̃ːʒə|Deutsch}}
        """,
        ["oˈʁɑ̃ːʒə"],
    ),
    (
        """
{{Aussprache}}
:{{IPA}} {{Lautschrift|kʁɪˈtiːk}}, {{Lautschrift|kʁiˈtiːk}}, ''mitteldeutsch, süddeutsch, österreichisch, schweizerisch vorwiegend:'' {{Lautschrift|-ˈtɪk}}<ref>Nach: {{Lit-Duden: Aussprachewörterbuch|A=7}}, Stichwort: ''Kritik''.</ref>
:{{Hörbeispiele}} {{Audio|De-Kritik.ogg}}
:{{Reime}} {{Reim|iːk|Deutsch}}
        """,
        ["kʁɪˈtiːk", "kʁiˈtiːk"],
    ),
    (
        """
{{Aussprache}}
:{{IPA}}
::bei Plural 1: {{Lautschrift|balˈkɔ̃ː}};<ref name="DAW">{{Lit-Duden: Aussprachewörterbuch|A=7}}, Stichwort »Balkon«, Seite 216.</ref> ''besonders nord- und ostdeutsch oft auch:'' {{Lautschrift|balˈkɔŋ}}<ref name="DAW"/>
::bei Plural 2: {{Lautschrift|balˈkoːn}};<ref name="DAW"/> {{schweiz.}} ''oft auch:'' {{Lautschrift|ˈbalkoːn}}<ref name="DAW"/>
:{{Hörbeispiele}} {{Audio|De-Balkon.ogg|{{Lautschrift|balˈkɔŋ}}}}, {{Audio|De-Balkon2.ogg|{{Lautschrift|balˈkɔ̃ː}}}}
:{{Reime}} {{Reim|ɔŋ|Deutsch}}, {{Reim|ɔ̃ː|Deutsch}}, {{Reim|oːn|Deutsch}}
        """,
        ["balˈkɔ̃ː"],
    ),
    (
        """

{{Aussprache}}
:{{IPA}} {{Lautschrift|toˈlɛtə}}, schweizerisch meist, sonst auch {{Lautschrift|to̯aˈlɛtə}}, besonders süddeutsch/österreichisch {{Lautschrift|tɔɪ̯ˈlɛtə}}<ref>Nach: {{Lit-Duden: Aussprachewörterbuch|A=7}}, Stichwort: ''Toilette''.</ref>
:{{Hörbeispiele}} {{Audio|De-Toilette.ogg}}, {{Audio|De-Toilette2.ogg}}, {{Audio|De-at-Toilette.ogg|spr=at}}
:{{Reime}} {{Reim|ɛtə|Deutsch}}
        """,
        ["toˈlɛtə"],
    ),
    (
        """
{{Aussprache}}
:{{IPA}} {{Lautschrift|ʃtipuˈliːʁən}}, {{Lautschrift|stipuˈliːʁən}}
:{{Hörbeispiele}} {{Audio|De-stipulieren.ogg}}
:{{Reime}} {{Reim|iːʁən|Deutsch}}
        """,
        ["ʃtipuˈliːʁən", "stipuˈliːʁən"],
    ),
    (
        """
{{Aussprache}}
:{{IPA}} {{Lautschrift|ˈliːɡn̩}}, {{Lautschrift|ˈliːɡŋ̍}}
:{{Hörbeispiele}} {{Audio|De-liegen.ogg}}, {{Audio|De-liegen2.ogg}}, {{Audio|De-liegen3.ogg}}
:{{Reime}} {{Reim|iːɡn̩|Deutsch}}
        """,
        ["ˈliːɡn̩", "ˈliːɡŋ̍"],
    ),
    (
        """
{{Aussprache}}
:{{IPA}} {{Lautschrift|ˈliːti̯ʊm}}<ref>{{Lit-Duden: Aussprachewörterbuch|A=6}}, Seite 514.</ref><ref name=Duden>{{Ref-Duden|Lithium}}</ref>, {{Lautschrift|ˈliːt͡si̯ʊm}}<ref name=Duden/>
:{{Hörbeispiele}} ''umgangssprachlich meistens'' {{Audio|De-Lithium2.ogg}}, ''fachsprachlich'' {{Audio|De-Lithium.ogg}}, {{Audio|De-at-Lithium.ogg|Lithium (österreichisch [ˈliːʦi̯ʊm-Variante])}}
        """,
        ["ˈliːti̯ʊm", "ˈliːt͡si̯ʊm"],
    ),
    (
        """
{{Aussprache}}
:{{IPA}} {{Lautschrift|ˈçeːmɪʃ}}, ''[[süddeutsch]], [[österreichisch]], [[schweizerisch]]'' {{Lautschrift|ˈkeːmɪʃ}}, ''[[norddeutsch]]'' {{Lautschrift|ˈʃeːmɪʃ}}
:{{Hörbeispiele}} {{Audio|De-chemisch.ogg}} {{Audio|De-at-chemisch.ogg|spr=at}}
:{{Reime}} {{Reim|eːmɪʃ|Deutsch}}
        """,
        ["ˈçeːmɪʃ"],
    ),
    (
        """
{{Aussprache}}
:{{IPA}} {{Lautschrift|ˈbiːsɛksuˌɛl}}, {{Lautschrift|ˈbiːzɛksuˌɛl}}, {{Lautschrift|bisɛksuˈɛl}}, {{Lautschrift|bisɛksuˈʔɛl}}, {{Lautschrift|bizɛksuˈɛl}}, {{Lautschrift|bizɛksuˈʔɛl}}
:{{Hörbeispiele}} {{Audio|De-bisexuell.ogg}},  {{Audio|De-bisexuell2.ogg}}
:{{Reime}} {{Reim|ɛl|Deutsch}}
        """,
        [
            "ˈbiːsɛksuˌɛl",
            "ˈbiːzɛksuˌɛl",
            "bisɛksuˈɛl",
            "bisɛksuˈʔɛl",
            "bizɛksuˈɛl",
            "bizɛksuˈʔɛl",
        ],
    ),
    (
        """
{{Aussprache}}
:{{IPA}} {{brit.|:}} {{Lautschrift|ɪɡˈzaːmpl}}, {{amer.|:}} {{Lautschrift|ɪɡˈzæmpl}}
:{{Hörbeispiele}} {{Audio|En-us-example.ogg|spr=us}}
        """,
        ["ɪɡˈzaːmpl"],
    ),
]

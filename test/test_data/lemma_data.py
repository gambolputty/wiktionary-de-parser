from wiktionary_de_parser.models import ReferenceType

lemma_data = [
    # Grundformverweis tests (inflected forms)
    (
        "{{Grundformverweis|ni#Personalpronomen|ni}}",
        {"reference_type": ReferenceType.INFLECTED, "lemma": "ni"},
    ),
    (
        "{{Grundformverweis Konj|1=bereiten|Abschnitt=Verb.2C_unregelm.C3.A4.C3.9Fig}}",
        {"reference_type": ReferenceType.INFLECTED, "lemma": "bereiten"},
    ),
    (
        "{{Grundformverweis|hunger}}",
        {"reference_type": ReferenceType.INFLECTED, "lemma": "hunger"},
    ),
    (
        "{{Grundformverweis Konj|zeichnen}}",
        {"reference_type": ReferenceType.INFLECTED, "lemma": "zeichnen"},
    ),
    (
        "{{Grundformverweis Konj|Abschnitt=Verb, untrennbar|AbschnittK=unterliegen (Konjugation), untrennbar, Hilfsverb haben (Deutsch)|unterliegen}}",
        {"reference_type": ReferenceType.INFLECTED, "lemma": "unterliegen"},
    ),
    (
        "{{Grundformverweis Konj|fara|Abschnitt=Verb 2|Flexion=0|spr=sv}}",
        {"reference_type": ReferenceType.INFLECTED, "lemma": "fara"},
    ),
    (
        "{{Grundformverweis Konj|dare|spr=en}}",
        {"reference_type": ReferenceType.INFLECTED, "lemma": "dare"},
    ),
    (
        "{{Grundformverweis Dekl|anal|Abschnitt=Adjektiv 6|Flexion=0}}",
        {"reference_type": ReferenceType.INFLECTED, "lemma": "anal"},
    ),
    (
        "{{Grundformverweis Dekl|pur|Abschnitt=pur (Deutsch)}}",
        {"reference_type": ReferenceType.INFLECTED, "lemma": "pur"},
    ),
    (
        "{{Grundformverweis Dekl|geschafft|Abschnitt=Adjektiv}}",
        {"reference_type": ReferenceType.INFLECTED, "lemma": "geschafft"},
    ),
    (
        "{{Grundformverweis Dekl|aufwärmen|Flexionsseite=aufzuwärmen}}",
        {"reference_type": ReferenceType.INFLECTED, "lemma": "aufwärmen"},
    ),
    (
        "{{Grundformverweis Dekl|Falschmeldung}}",
        {"reference_type": ReferenceType.INFLECTED, "lemma": "Falschmeldung"},
    ),
    (
        "{{Grundformverweis Dekl|červený|spr=cs}}",
        {"reference_type": ReferenceType.INFLECTED, "lemma": "červený"},
    ),
    (
        "{{Grundformverweis Dekl|decir#Substantiv, m|decir|Flexion=0}}",
        {"reference_type": ReferenceType.INFLECTED, "lemma": "decir"},
    ),
    # Lemmaverweis tests (variant forms)
    (
        "{{Lemmaverweis|mild}}",
        {"reference_type": ReferenceType.VARIANT, "lemma": "mild"},
    ),
    (
        "{{Lemmaverweis|Geographie}}",
        {"reference_type": ReferenceType.VARIANT, "lemma": "Geographie"},
    ),
    (
        "{{Lemmaverweis|Küken}}",
        {"reference_type": ReferenceType.VARIANT, "lemma": "Küken"},
    ),
    # No reference template (standalone lemma)
    (
        "== Hund ({{Sprache|Deutsch}}) ==\n=== {{Wortart|Substantiv|Deutsch}} ===",
        {"reference_type": ReferenceType.NONE, "lemma": "Untitled"},
    ),
]

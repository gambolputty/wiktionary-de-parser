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
    # LEMMA_BUG1 — first positional param is a nested {{linkZiel|<lang>|<target>}}
    # template. The target lemma is the inner template's last positional param.
    (
        "{{Grundformverweis Dekl|{{linkZiel|is|kaldur}}|kaldur|spr=is}}",
        {"reference_type": ReferenceType.INFLECTED, "lemma": "kaldur"},
    ),
    (
        "{{Grundformverweis Dekl|{{linkZiel|is|viður}}|viður|spr=is}}",
        {"reference_type": ReferenceType.INFLECTED, "lemma": "viður"},
    ),
    # LEMMA_BUG2 — first positional is a section anchor (#Übersetzungen).
    # The real lemma is the next positional.
    (
        "{{Lemmaverweis|#Übersetzungen|Abbé|Grund=Ü}}",
        {"reference_type": ReferenceType.VARIANT, "lemma": "Abbé"},
    ),
    # {{Alte Schreibweise|<post-reform>|Reform 1996}} — semantically a
    # variant reference: the page is the pre-reform spelling, the real
    # lemma is the first positional param of the template.
    (
        "{{Alte Schreibweise|Mopps|Reform 1996}}",
        {"reference_type": ReferenceType.VARIANT, "lemma": "Mopps"},
    ),
    # Code-review finding 2 — inner wrapper template carries only named
    # parameters (no positionals to extract). Must fall through to the
    # next positional of the outer template, not return the raw template
    # markup as the lemma.
    (
        "{{Grundformverweis Dekl|{{linkZiel|spr=is}}|kaldur|spr=is}}",
        {"reference_type": ReferenceType.INFLECTED, "lemma": "kaldur"},
    ),
    # Code-review finding 3 — reference template body spans multiple lines.
    # The regex-based pre-filter used to truncate at the first newline,
    # leaving mwparserfromhell with an unclosed template.
    (
        "{{Alte Schreibweise|Mopps\n|Reform 1996}}",
        {"reference_type": ReferenceType.VARIANT, "lemma": "Mopps"},
    ),
    # Code-review finding 9 — first positional empty. The second positional
    # is a marker ("Reform 1996"), NOT the lemma. Must return None / page
    # name, not the marker.
    (
        "{{Alte Schreibweise||Reform 1996}}",
        {"reference_type": ReferenceType.NONE, "lemma": "Untitled"},
    ),
    # Code-review finding 10 — `|2=Wrong|Real`: the bare `Real` occupies
    # position 1 (counter increments past the explicit `|2=`), so Real
    # should win even though Wrong appears first in source order.
    (
        "{{Grundformverweis|2=Wrong|Real}}",
        {"reference_type": ReferenceType.INFLECTED, "lemma": "Real"},
    ),
    # Code-review finding 12 — text + template mix in a positional value.
    # Not a pure wrapper, so the inner template must NOT be unwrapped —
    # otherwise the `stem-` prefix would silently disappear.
    (
        "{{Grundformverweis|stem-{{linkZiel|is|kaldur}}|fallback}}",
        {
            "reference_type": ReferenceType.INFLECTED,
            "lemma": "stem-{{linkZiel|is|kaldur}}",
        },
    ),
    # Code-review #2 finding 1 — whitespace around inner template must not
    # disqualify the pure-wrapper detection. value.nodes yields Text nodes
    # for whitespace, never bare str — the filter had to compare against
    # Text, not str.
    (
        "{{Grundformverweis Dekl| {{linkZiel|is|kaldur}} |kaldur|spr=is}}",
        {"reference_type": ReferenceType.INFLECTED, "lemma": "kaldur"},
    ),
    # Wikitext HTML comments inside a positional must be ignored — they
    # used to leak into the returned lemma string (`target<!-- old -->`).
    (
        "{{Lemmaverweis|target<!-- prev: oldtarget -->}}",
        {"reference_type": ReferenceType.VARIANT, "lemma": "target"},
    ),
]

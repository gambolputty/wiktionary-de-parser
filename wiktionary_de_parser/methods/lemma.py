import re


def init(title, text, current_record):
    """
    Grundformverweis
    Von einer Deklination spricht man beim Beugen von Substantiven und den
    dazugehörigen Adjektiven und Pronomen (Nominalflexion),
    von einer Konjugation beim Beugen eines Verbs (Verbalflexion).

    Reference:
    https://de.wiktionary.org/wiki/Kategorie:Flektierte_Form_(Deutsch)
    https://de.wiktionary.org/wiki/Vorlage:Grundformverweis_Konj
    https://de.wiktionary.org/wiki/Vorlage:Grundformverweis_Dekl
    """

    # match_test = re.search(r'({{Grundformverweis[^}]+}})', text)
    # if match_test:
    #     print(match_test.group(1))
    #     print()

    found_lemma = title
    inflected = False
    match_lemma = re.search(r'{{Grundformverweis[^|]*\|(?:\w+=[^\|]+\|)*([^\|\#\}]+)', text)
    if match_lemma:
        found_lemma = match_lemma.group(1).strip()
        inflected = True

    # title is lemma
    return {
        'lemma': found_lemma,
        'inflected': inflected
    }

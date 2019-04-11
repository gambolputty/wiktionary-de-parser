import re


def init(title, text, current_record):
    """
    Grundformverweis
    Von einer Deklination spricht man beim Beugen von Substantiven und den
    dazugehörigen Adjektiven und Pronomen (Nominalflexion),
    von einer Konjugation beim Beugen eines Verbs (Verbalflexion).

    Reference:
    https://de.wiktionary.org/wiki/Vorlage:Grundformverweis_Konj
    """

    # match_test = re.search(r'({{Grundformverweis[^}]+}})', text)
    # if match_test:
    #     print(match_test.group(1))
    #     print()

    match_lemma = re.search(r'{{Grundformverweis[^|]*\|(?:\w+=[^\|]+\|)*([^\|\#\}]+)', text)
    if match_lemma:
        return match_lemma.group(1)
    # title is lemma
    return title

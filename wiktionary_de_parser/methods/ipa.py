import re
from pdb import set_trace as bp

"""
Reference: https://de.wiktionary.org/wiki/Hilfe:Aussprache

The WiktionaryDe community decided in 2015 to only add IPA transcriptions
for the lemma (and not for inflected forms; these are on a seperate page).
Unfortunately there are still many pages with inflected forms.
For example: "Schweizerdeutsch" and Singular 2 "(das) Schweizerdeutsche":
    - :{{IPA}} {{Lautschrift|ˈʃvaɪ̯t͡sɐˌdɔɪ̯t͡ʃ}}, {{Sg.2}} {{Lautschrift|ˈʃvaɪ̯t͡sɐˌdɔɪ̯t͡ʃə}}

Sometimes they are just seperated by comma and no additional info about the grammatical form is present:
    Example "Aserbaidschanisch" and Singular 2 "(das) Aserbaidschanische":
    - :{{IPA}} {{Lautschrift|ˌazɐbaɪ̯ˈd͡ʒaːnɪʃ}}, {{Lautschrift|ˌazɐbaɪ̯ˈd͡ʒaːnɪʃə}}

In the last example we can't say whether the two entries are just two different IPA
transcriptions for the same word or for two different words (lemma & inflected form). 

Temporary solution:
Keep the first entry. Check if the last IPA letter of every other entry is the same
as the one in the first match (because it's likely that the last character doesn't
change in different IPA transcriptions for the same word)

"""

vowels = r'aɪ̯|aʊ̯|ɛɪ̯|ɔɪ̯|ʊɪ̯|aː|eː|ɛː|iː|oː|øː|õː|uː|yː|ɨ|i̯|ʉ|ɯ|ɪ|ʏ|ʊ|ø|ɑ|ɘ|ɵ|ɤ|ə|ɛ|œ|ɜ|ɞ|ʌ|ɔ|æ|ɐ|ɶ|ɒ|ã|ɐ̯|a|e|i|o|u|y'
consonants = r'ʈ|ɖ|ɟ|ɢ|ʔ|ɸ|β|v|θ|ð|ʃ|ʒ|ʂ|ʐ|ç|ʝ|l̩|ɣ|χ|ʁ|ħ|ʕ|ɦ|ɬ|ɮ|ɱ|m̩|ɱ̍|ɱ̩|n̩|ɳ|ɲ|ŋ|ŋ̍|ŋ̩|ɴ|ʙ|ʀ|ⱱ|ɾ|ʦ|ʧ|ʤ|ɽ|ɺ|ʋ|ɹ|ɻ|ɰ|ɭ|ʎ|ʟ|p|b|t|d|c|k|ɡ|q|f|s|z|x|h|m|n|r|l|j|ɫ'
ipa_letters_re = re.compile(r'(' + vowels + '|' + consonants + ')')


def init(title, text, current_record):
    # search line by line, headline {{Aussprache}} must come first
    lines = text.split('\n')
    found_head = False
    found_ipa = []
    for line in lines:
        if title == 'Dosenfisch':
            print(line)
        if line.startswith('{{Aussprache}}'):
            found_head = True
            continue
        if found_head is False:
            continue
        # break on empty newline
        if line.strip() == '':
            break
        # find IPA string(s)
        match_ipa = re.findall(r'{{Lautschrift\|([^}]+)}}', line)
        if not match_ipa:
            continue
        found_ipa = [x.strip() for x in match_ipa if x != '…' and x.strip() != '']
        if found_ipa:
           break
    
    if not found_ipa:
        return False


    
    # if title == 'Dosenfisch':
    #     print(found_ipa)

    # workaround for problem described above
    # keep IPA strings, that have the same ending as the first one in the row
    wanted_last_ipa_char = None
    result = [found_ipa[0]]
    for idx, ipa_str in enumerate(found_ipa):
        try:
            last_ipa_char = ipa_letters_re.findall(ipa_str)[-1]
        except IndexError:
            if idx == 0:
                return False
            else:
                break
        if idx == 0:
            wanted_last_ipa_char = last_ipa_char
            continue
        if last_ipa_char == wanted_last_ipa_char and ipa_str not in result:
            result.append(ipa_str)
        else:
            break

    return {'ipa': result}

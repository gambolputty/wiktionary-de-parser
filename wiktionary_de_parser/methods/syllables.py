import re
import pyphen

"""
Test strings: 

{{Worttrennung}}
:ge·sagt, ge·tan

{{Worttrennung}}
:Ton {{Pl.}} To·ne

{{Worttrennung}}
:neun·zehn

{{Worttrennung}}
:bald, {{Komp.}} eher, {{Sup.}} am ehes·ten

{{Worttrennung}}
:ge·sagt, ge·tan (umgangssprachlich oft: gra·de, grad)

{{Worttrennung}}
:zwan·zig, zwan·zi·ge

{{Worttrennung}}
:re·den, {{Prät.}} re·de·te, {{Part.}} ge·re·det

{{Worttrennung}}
:re·den, {{Pl.}} re·de·nen

{{Worttrennung}}
:drei·ßig, ''[[veraltend]]:'' drei·ßi·ge

{{Worttrennung}}
:ein·und·zwan·zig

{{Worttrennung}}
:pa·cken, {{Prät.}} pack·te, {{Part.}} ge·packt

{{Worttrennung}}
:Skiz·ze, {{Pl.}} Skiz·zen

{{Worttrennung}}
:Me·lo·ne, {{Pl.}} Me·lo·nen

{{Worttrennung}}
:Narr, {{Pl.}} Nar·ren

{{Worttrennung}}
:{{kSg.}}, Ver·ein·te Na·ti·o·nen

{{Worttrennung}}
:Pa·cker, {{Pl.}} Pa·cker

{{Worttrennung}}
:''Neue Worttrennung:'' Mü·cken·stich, {{Pl.}} Mü·cken·sti·che
:''Alte Worttrennung:'' Mük·ken·stich, {{Pl.}} Mük·ken·sti·che

{{Worttrennung}}
:Lie·bes·kum·mer, {{kPl.}}

{{Worttrennung}}
:Pa·cke·rin, {{Pl.}} Pa·cke·rin·nen

{{Worttrennung}}
:rei·zen, {{Prät.}} reiz·te, {{Part.}} ge·reizt

{{Worttrennung}}
:rei·zen

{{Worttrennung}}
:pa·la·vern, {{Prät.}} pa·la·ver·te, {{Part.}} pa·la·vert

{{Worttrennung}}
:Toll·patsch, {{Pl.}} Toll·pat·sche

{{Worttrennung}}
:kir·ren, {{Prät.}} kirr·te, {{Part.}} ge·kirrt

{{Worttrennung}}
:Arzt, {{Pl.}} Ärz·te

{{Worttrennung}}
:Arzt, {{Pl.}} Arzts

{{Worttrennung}}
:Pflan·ze, {{Pl.}} Pflan·zen
"""


def init(title, text, current_record):
    # find syllables in wikitext
    # reference: https://de.wiktionary.org/wiki/Hilfe:Worttrennung
    result = False

    # strip comments, <ref>-tags etc.
    text = re.sub(r'<[^>]+>', ' ', text)

    matched = re.search(r"{{Worttrennung}}\n::?(?:''[^']+'' )?(?:{{[^}]+}}, )?((?:(?!,? {{|,? ''| \().)+)", text)
    if matched is not None:
        found_string = matched.group(1)

        """
        check if comma found and string, check if comma is part of title
        valid:
            ge·sagt, ge·tan
        invalid (inflected form):
            zwan·zig, zwan·zi·ge
        """
        if ',' in found_string:
            found_string_split = found_string.split(',')
            if found_string_split[0].replace('·', '') == title:
                # comma does not belong to title, take first chunk
                found_string = found_string_split[0]

        # split syllables, remove empty strings (ugly side effect of re.split)
        result = list(filter(None, re.split(r' |·|-', found_string)))
    elif 'language' in current_record and current_record['language'] in pyphen.LANGUAGES:
        # get syllables with PyHyphen
        dic = pyphen.Pyphen(lang=current_record['language'])
        syl_string = dic.inserted(title)
        # split by "-" and remove empty entries
        result = [x for x in re.split(r' |-', syl_string) if x]

    return {'syllables': result} if result else False

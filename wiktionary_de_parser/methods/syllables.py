import re
from typing import Dict, List, Literal, Union
import pyphen

SyllablesInfo = Dict[Literal['syllables'], List[str]]
SyllablesResult = Union[Literal[False], SyllablesInfo]

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

{{Worttrennung}}
:, {{Pl.}}

{{Worttrennung}}
:
:ein·wir·ken, {{Prät.}} wirk·te ein, {{Part.}} ein·ge·wirkt

"""


def init(
    title: str,
    text: str,
    current_record
) -> SyllablesResult:
    # find syllables in wikitext
    # reference: https://de.wiktionary.org/wiki/Hilfe:Worttrennung
    result = False

    # strip comments, <ref>-tags etc.
    text = re.sub(r'<[^>]+>', ' ', text)

    # find paragraph
    match_p = re.search(r'{{Worttrennung}}\n(?::?\n)?([^\n]+)', text)
    if match_p is not None:
        paragraph = match_p.group(1)

        """
        Find title in wikitext under "{{Worttrennung}}".
        Keep characters, that are also part of title.
        Find start and end index.
        Paragraph can have commas/semicolons, but we don't know if they are part of title.
        valid:
            ge·sagt, ge·tan
        invalid (inflected form):
            zwan·zig, zwan·zi·ge
            In·tel·li·genz·quo·ti·ent; In·tel·li·genz·quo·ti·en·ten

        """
        title_index = 0
        start_index = -1
        end_index = -1
        last_title_index = len(title) - 1
        last_paragraph_index = len(paragraph) - 1
        for index, char in enumerate(paragraph):
            # get start index
            # test if title can be inserted from current index
            # remove mid dots for testing
            if start_index == -1:
                if paragraph[index:].replace('·', '').startswith(title):
                    start_index = index
                    end_index = index
                continue

            end_index += 1
            if char == '·':
                continue

            title_index += 1
            if title_index >= last_title_index or char != title[title_index] or index == last_paragraph_index:
                end_index += 1
                break

        # remove everything after actual_index
        clean_string = paragraph[start_index:end_index]

        # split syllables, remove empty strings (ugly side effect of re.split)
        result = list(filter(None, re.split(r' |·|-', clean_string)))

    if not result and 'lang_code' in current_record and current_record['lang_code'] in pyphen.LANGUAGES:
        # get syllables with PyHyphen
        dic = pyphen.Pyphen(lang=current_record['lang_code'])
        syl_string = dic.inserted(title)
        # split by "-" and remove empty entries
        result = [x for x in re.split(r' |-', syl_string) if x]

    return {'syllables': result} if result else False

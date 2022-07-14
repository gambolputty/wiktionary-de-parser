import re
from typing import Dict, List, Literal, Union
import pyphen

from wiktionary_de_parser.helper import find_paragraph, strip_html_tags

SyllablesInfo = Dict[Literal["syllables"], List[str]]
SyllablesResult = Union[Literal[False], SyllablesInfo]


def parse_syllables(title: str, text: str):
    """
    Parse syllables below "{{Worttrennung}}"-template.

    Keep non-word-characters that are part of the title:
    Paragraph can have commas/semicolons, but we don't know if they are part of title.
    Find start and end index and extract string with middle dots.
    valid (with comma):
        ge·sagt, ge·tan
    invalid (with comma):
        zwan·zig, zwan·zi·ge
        In·tel·li·genz·quo·ti·ent; In·tel·li·genz·quo·ti·en·ten

    Reference: https://de.wiktionary.org/wiki/Hilfe:Worttrennung
    """

    # find syllables in wikitext

    text = strip_html_tags(text)
    paragraph = find_paragraph("Worttrennung", text)

    if not paragraph:
        return False

    # remove false mid dot at the beginning that breaks the parser (":·nutz·lo·se")
    paragraph = paragraph.lstrip(":·")

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
            if paragraph[index:].replace("·", "").startswith(title):
                start_index = index
                end_index = index
            continue

        end_index += 1
        if char == "·":
            continue

        title_index += 1
        if (
            title_index >= last_title_index
            or char != title[title_index]
            or index == last_paragraph_index
        ):
            end_index += 1
            break

    # remove everything after actual_index
    clean_string = paragraph[start_index:end_index]

    # Remove comma and dot
    clean_string = re.sub(r"[.,]", "", clean_string)

    # split syllables, remove empty strings (ugly side effect of re.split)
    result = list(filter(None, re.split(r" |·|-", clean_string)))

    return result if result else False


def parse_syllables_fallback(title: str, current_record):
    if (
        "lang_code" in current_record
        and current_record["lang_code"] in pyphen.LANGUAGES
    ):
        # get syllables with PyHyphen
        dic = pyphen.Pyphen(lang=current_record["lang_code"])
        syl_string = dic.inserted(title)
        # split by "-" and remove empty entries
        return [x for x in re.split(r" |-", syl_string) if x]

    return False


def init(title: str, text: str, current_record) -> SyllablesResult:
    result = parse_syllables(title, text)

    if not result:
        result = parse_syllables_fallback(title, current_record)

    return {"syllables": result} if result else False

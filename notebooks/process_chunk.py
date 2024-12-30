from collections import defaultdict

from wiktionary_de_parser import WiktionaryParser


def process_chunk(pages_chunk):
    local_dict = defaultdict(list)
    parser = WiktionaryParser()

    for page in pages_chunk:
        for entry in parser.entries_from_page(page):
            entry_parsed = parser.parse_entry(entry, include_meanings=True)

            if entry_parsed.meanings is None:
                continue

            local_dict[page.name].append(entry_parsed.meanings)

    return local_dict

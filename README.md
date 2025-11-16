# wiktionary-de-parser

A Python module to extract data from German Wiktionary XML files (for Python 3.11+).

## Features

- Extracts _IPA transcriptions_, _hyphenation_, _language_, _part of speech_ information (basic), _genus_ and _flexion tables_ of a word.
- Yields per entry, not per page (a page can have multiple entries/ words can have different meanings)

## Installation

`pip install wiktionary-de-parser`

Or with [Poetry](https://python-poetry.org/):

`poetry add wiktionary-de-parser`

## Usage

### Loading the XML dump file
```python
from wiktionary_de_parser import WiktionaryParser
from wiktionary_de_parser.dump_processor import WiktionaryDump

# To download the dump file, specify the directory where the
# dump file should be stored.
dump = WiktionaryDump(dump_dir_path="directory-of-dump-file")

# This will download "dewiktionary-latest-pages-articles-multistream.xml.bz2" to
# the directory specified in `dump_dir_path`.
dump.download_dump()

# Alternatively you can specify a different dump file to download.
dump = WiktionaryDump(
    dump_dir_path="directory-of-dump-file",
    dump_download_url="url-to-dump-file.xml.bz2",
)
dump.download_dump()

# If you already have the dump file locally, specify the path to the file.
dump = WiktionaryDump(dump_file_path="path-to-dump-file.xml.bz2")
dump.download_dump()
```

### Parsing the dump file
```python
from pprint import pprint
from wiktionary_de_parser import WiktionaryParser

# ... (see above)

parser = WiktionaryParser()

for page in dump.pages():
    # Skip redirects
    if page.redirect_to:
        continue

    if page.name == "Abend":
        # Parse all entries for "Abend"
        for entry in parser.entries_from_page(page):
            results = parser.parse_entry(entry)
            pprint(results)
        break
```

## Output
All page entries for "Abend":

```python
ParsedWiktionaryPageEntry(
    name="Abend",
    hyphenation=["Abend"],
    flexion={
        "Genus": "m",
        "Nominativ Singular": "Abend",
        "Nominativ Plural": "Abende",
        "Genitiv Singular": "Abends",
        "Genitiv Plural": "Abende",
        "Dativ Singular": "Abend",
        "Dativ Plural": "Abenden",
        "Akkusativ Singular": "Abend",
        "Akkusativ Plural": "Abende",
    },
    ipa=["ˈaːbn̩t", "ˈaːbm̩t"],
    language=Language(lang="Deutsch", lang_code="de"),
    lemma=Lemma(lemma="Abend", reference_type=<ReferenceType.NONE: 'none'>),
    pos={"Substantiv": []},
    rhymes=["aːbn̩t"],
)
ParsedWiktionaryPageEntry(
    name="Abend",
    hyphenation=["Abend"],
    flexion=None,
    ipa=["ˈaːbn̩t"],
    language=Language(lang="Deutsch", lang_code="de"),
    lemma=Lemma(lemma="Abend", reference_type=<ReferenceType.NONE: 'none'>),
    pos={"Substantiv": ["Nachname"]},
    rhymes=["aːbn̩t"],
)
ParsedWiktionaryPageEntry(
    name="Abend",
    hyphenation=["Abend"],
    flexion=None,
    ipa=["ˈaːbn̩t", "ˈaːbm̩t"],
    language=Language(lang="Deutsch", lang_code="de"),
    lemma=Lemma(lemma="Abend", reference_type=<ReferenceType.NONE: 'none'>),
    pos={"Substantiv": ["Toponym"]},
    rhymes=["aːbn̩t"],
)

```

## Development
This project uses [Poetry](https://python-poetry.org/).

1. Install [Poetry](https://python-poetry.org/).
2. Clone this repository
3. Run `poetry install` inside of the project folder to install dependencies.
4. There is a `notebook.ipynb` to test the parser.
5. Run `poetry run pytest` to run tests.

## License

[MIT](https://github.com/gambolputty/wiktionary-de-parser/blob/master/LICENSE.md) © Gregor Weichbrodt

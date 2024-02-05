# wiktionary-de-parser

A Python module to extract data from German Wiktionary XML files (for Python 3.11+).

## Features

- Extracts flexion tables, IPA transcriptions, language, genus, lemma, part of speech information (basic) and syllables of a word.
- Yields per entry, not per page (a page can have multiple entries/ words can have different meanings)

## Installation

`pip install wiktionary-de-parser`

Or with [Poetry](https://python-poetry.org/):

`poetry add wiktionary-de-parser`

## Usage

The following example will download the latest Wiktionary dump file ([from here](https://dumps.wikimedia.org/dewiktionary/latest)) and parse all German entries.

```python
from wiktionary_de_parser import WiktionaryParser
from wiktionary_de_parser.dump_processor import WiktionaryDump

# Specify the directory where the dump file should be stored.
dump = WiktionaryDump(dump_dir_path="directory-of-dump-file")

# This will download "dewiktionary-latest-pages-articles-multistream.xml.bz2" to
# the directory specified in `dump_dir_path`.
dump.download_dump()

# Alternatively you can also specify a different dump file to download.
dump = WiktionaryDump(
    dump_dir_path="directory-of-dump-file",
    dump_download_url="url-to-dump-file.xml.bz2",
)
dump.download_dump()

# If you already have the dump file, you can also specify the path to the file.
dump = WiktionaryDump(dump_file_path="path-to-dump-file.xml.bz2")
dump.download_dump()

# Next, we can parse the dump file.
parser = WiktionaryParser()
for page in dump.pages():
    # Skip redirects
    if page.redirect_to:
        continue

    for entry in parser.entries_from_page(page):
        parsed = parser.parse_entry(entry)

       #  Ignore non-German entries
       if parsed.language.lang_code != "de":
            continue

        # do something with "parsed
        ...

```

## Output
All entries for "Abend":

```python
ParsedWiktionaryPageEntry(
    name="Abend",
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
    lemma=Lemma(lemma="Abend", inflected=False),
    pos={"Substantiv": []},
    rhymes=["aːbn̩t"],
    syllables=["Abend"],
)
ParsedWiktionaryPageEntry(
    name="Abend",
    flexion=None,
    ipa=["ˈaːbn̩t"],
    language=Language(lang="Deutsch", lang_code="de"),
    lemma=Lemma(lemma="Abend", inflected=False),
    pos={"Substantiv": ["Nachname"]},
    rhymes=["aːbn̩t"],
    syllables=["Abend"],
)
ParsedWiktionaryPageEntry(
    name="Abend",
    flexion=None,
    ipa=["ˈaːbn̩t", "ˈaːbm̩t"],
    language=Language(lang="Deutsch", lang_code="de"),
    lemma=Lemma(lemma="Abend", inflected=False),
    pos={"Substantiv": ["Toponym"]},
    rhymes=["aːbn̩t"],
    syllables=["Abend"],
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

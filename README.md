# wiktionary-de-parser

A Python library (3.13+) that extracts structured data from
German Wiktionary XML dumps: IPA, hyphenation, inflection tables,
part-of-speech tags, lemma references, rhymes, and meanings.

## Features

- Streams compressed XML dumps memory-efficiently.
- Yields one structured entry per language and part of speech (a single
  Wiktionary page often holds several).
- Optional `multiprocessing` mode for full-dump throughput.

## Installation

```bash
pip install wiktionary-de-parser
```

The project uses [uv](https://docs.astral.sh/uv/) for development; any
standard `pip`/PyPI install works for consumers.

## Usage

### Locating the dump file

```python
from wiktionary_de_parser import WiktionaryDump

# Either point at an existing local file.
dump = WiktionaryDump(
    dump_file_path="path/to/dewiktionary-latest-pages-articles-multistream.xml.bz2"
)

# Or download into a directory on first call.
dump = WiktionaryDump(dump_dir_path="dumps/")
dump.download_dump()
```

### Parsing entries (serial)

```python
from wiktionary_de_parser import WiktionaryParser

parser = WiktionaryParser()

for page in dump.pages():
    if page.redirect_to or not page.wikitext:
        continue
    for entry in parser.entries(page):
        parsed = parser.parse(entry)
        if parsed.page_name == "Abend":
            print(parsed)
```

### Parsing entries (parallel)

For full-dump runs use `iter_parsed`. XML iteration stays on the main
process while parsing is sharded over a worker pool.

```python
for parsed in dump.iter_parsed(workers=15):
    ...  # ParsedEntry instances yielded across all workers
```

`workers` defaults to `os.cpu_count() - 1`. Pass `workers=1` to skip
multiprocessing entirely (useful with `pdb`).

## Output schema

```python
ParsedEntry(
    page_name="Abend",
    page_id=2742,
    entry_index=0,
    language="Deutsch",
    language_code="de",
    lemma="Abend",
    reference=None,                          # LemmaReference if the page is an inflected/variant form
    pos=[PosTag(pos="Substantiv", subtypes=())],
    inflection={
        "gender": "m",
        "nominative_singular": "Abend",
        "nominative_plural": "Abende",
        "genitive_singular": "Abends",
        "genitive_plural": "Abende",
        "dative_singular": "Abend",
        "dative_plural": "Abenden",
        "accusative_singular": "Abend",
        "accusative_plural": "Abende",
    },
    ipa=["ˈaːbn̩t", "ˈaːbm̩t"],
    hyphenation=["Abend"],
    rhymes=["aːbn̩t"],
    meanings=[Meaning(text="…", tags=["Astronomie"], raw_tags=[])],
)
```

All result containers are `@dataclass(slots=True)`. The full schema
lives in [`wiktionary_de_parser/models.py`](wiktionary_de_parser/models.py).

### Inflection keys

Inflection-table parameter names are token-translated to English
lowercase + underscore: `"Nominativ Singular"` → `"nominative_singular"`,
`"Präsens_er, sie, es"` → `"present_3sg"`. Unknown tokens are kept
verbatim (lowercased).

### Lemma references

If the entry is an inflected form or alternative spelling, `lemma`
holds the canonical target and `reference` records the type:

```python
# "gehörte" → "gehören"
parsed.lemma == "gehören"
parsed.reference == LemmaReference(target="gehören", type=ReferenceType.INFLECTED)

# "Geografie" → "Geographie"
parsed.reference == LemmaReference(target="Geographie", type=ReferenceType.VARIANT)
```

## Development

```bash
uv sync                 # install dependencies
uv run pytest           # run the test suite
uv run ruff format
uv run ruff check
```

## License

[MIT](LICENSE.txt) © Gregor Weichbrodt

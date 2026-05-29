# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python library that extracts linguistic data (IPA, hyphenation,
inflection, POS, lemma references, rhymes, meanings) from German
Wiktionary XML dumps. Streams compressed XML, yields one structured
entry per Wortart section.

## Key Commands

### Development setup
- `uv sync` — install dependencies (project uses uv, not poetry)

### Testing
- `uv run pytest`
- `uv run pytest test/methods/test_<module>.py`
- `uv run pytest test/methods/test_<module>.py::TestClass::test_function`

### Linting & formatting
- `uv run ruff format`
- `uv run ruff check`
- `uv run ruff check --fix`

## Architecture

### Core modules
- `wiktionary_de_parser/__init__.py` — public API re-exports.
- `wiktionary_de_parser/parser.py` — `WiktionaryParser` with
  `entries(page)` and `parse(entry)` methods. Stateless; splits page
  wikitext into entry slices and runs every feature parser.
- `wiktionary_de_parser/dump.py` — `WiktionaryDump`: download,
  decompress (bzcat subprocess preferred over `bz2.open`), iterate
  pages via `lxml.iterparse`. `iter_parsed(workers=N)` shards parsing
  across a multiprocessing pool.
- `wiktionary_de_parser/entry.py` — `WiktionaryEntry` with cached
  lookups (sections, header line, parsed pronunciation/header Wikicode).
  Shared cache means each `mwparserfromhell.parse()` runs at most once
  per entry per "view".
- `wiktionary_de_parser/models.py` — `@dataclass(slots=True)` types:
  `ParsedEntry`, `PosTag`, `LemmaReference`, `Meaning`, `WiktionaryPage`,
  `ReferenceType`. No Pydantic.
- `wiktionary_de_parser/_wikitext.py` — shared regex/template helpers:
  `strip_refs`, `find_sections`, `resolve_positional_params`,
  `extract_first_positional_value`, `slice_balanced_template`.

### Feature parsers (`wiktionary_de_parser/parsers/`)
Each module exposes a `parse(entry)` function:
- `language.py` — language name and ISO 639 code from the Wortart
  header.
- `pos.py` — POS list with subtypes; handles `Deklinierte Form` (POS
  lives in `{{Grammatische Merkmale}}` body) and Übersicht-derived POS
  signals.
- `ipa.py` — IPA from `{{Lautschrift}}` chain after `{{IPA}}`; falls
  back to `{{Lautschrift?}}` when no verified Lautschrift exists.
- `rhymes.py` — same walker as IPA, applied to `{{Reim}}` after
  `{{Reime}}`. Shares the pre-parsed Aussprache Wikicode with IPA.
- `hyphenation.py` — char-walk over the Worttrennung body, retains
  affix markers, tolerates wrappers like `{{Polytonisch|…}}`.
- `inflection.py` — locates the first `{{Deutsch … Übersicht}}` by
  regex + brace-balanced cut, then parses only that slice. Keys are
  token-translated to English (`Nominativ Singular` → `nominative_singular`).
- `lemma.py` — top-level form references (`Grundformverweis`,
  `Lemmaverweis`, `Alte Schreibweise`), gated by a cheap string
  prefilter so entries without a reference skip parsing entirely.
- `meanings.py` — hierarchical senses from the Bedeutungen list. Uses
  `wikitextparser` for `WikiList` traversal (the one place where
  mwparserfromhell isn't a clean fit).

### Data flow
1. `WiktionaryDump.pages()` yields `WiktionaryPage` from compressed XML.
2. `WiktionaryParser.entries(page)` slices the page wikitext at
   `=== {{Wortart…}} ===` boundaries.
3. `WiktionaryParser.parse(entry)` runs every parser, returns
   `ParsedEntry`.

For full-dump runs use `WiktionaryDump.iter_parsed(workers=N)` —
parsing is sharded across a process pool while XML iteration stays on
the main process.

### Testing structure
- `test/methods/` — unit tests per parser module.
- `test/test_data/` — fixtures (real wikitext snippets, not mocks).

Edge cases are documented inline in each parser. The tests pin
behaviour against specific Wiktionary pages that previously broke the
parser.

## Important details

- Python 3.13+ required.
- `lxml` for streaming XML, `mwparserfromhell` for templates,
  `wikitextparser` for the meanings list traversal only.
- Dump XML is parsed namespace-agnostically (`{*}` wildcard), so a future
  MediaWiki export schema bump (0.11 → 0.12 …) won't silently break it.
- Entry-splitter tolerates: double space (`===  {{Wortart…`),
  lemma-prefix headers (`=== ombrello {{Wortart…`).
- `find_sections` strips refs and HTML comments first so `\n{{Lit-…}}`
  inside a citation can't truncate a section body and a commented-out
  section isn't parsed. Only `KNOWN_SECTIONS` headings are recognised.
- Default dump URL:
  `https://dumps.wikimedia.org/dewiktionary/latest/dewiktionary-latest-pages-articles-multistream.xml.bz2`

## Notebook
- `notebooks/demo.ipynb` — concise usage demo
- `uv run jupyter notebook` to launch

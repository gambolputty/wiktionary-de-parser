# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Fixed
- `ipa` parser: tolerate `, `, `,  `, `; `, `,` as separators between
  `{{Lautschrift}}` templates (was strict on single `", "`). Recovers
  multi-variant IPAs on ~340 pages including `Kaffee`, `Leipzig`,
  `Inkongruenz`, `Alpenrepublik`, `New Orleans`, `Stahlbeton`, …
- `ipa` parser: `{{Lautschrift|spr=de|ˈxyz}}` (named parameter before
  the positional IPA) used to return `['spr=de']`. Now correctly skips
  named params and picks the positional IPA value (`verwehen`, `Bane`,
  `Arnis`, `meh` and similar pages).
- `ipa` parser: HTML markup like `<sup>ə</sup>` inside Lautschrift values
  is stripped (e.g. `elf` now yields `['ˈɛləf']` instead of leaking the
  tags).
- `ipa` parser: `{{Lautschrift?}}` (unverified pronunciation) is used as
  a fallback when an entry has no verified `{{Lautschrift}}`. Adds IPA
  for ~230 entries including `Betriebswirtschaftslehre`,
  `Niederschöneweide`, `Maßband`. Verified Lautschrift still wins when
  both are present in the same paragraph.
- `ipa` parser: interleaved `{{Lautschrift?}}` between two verified
  `{{Lautschrift}}` templates no longer terminates the chain.
- `ipa` parser: tolerates whitespace inside the `{{IPA}}` template name
  (`{{ IPA }}`).
- `rhymes` parser: same separator and named-param fixes as `ipa`.
- `pos` parser: typo `{{Deutsch Substantiv Übersicht - sch` (stray
  space) corrected to `-sch`; matches 514 real templates.
- `pos` parser: `{{Wortart|spr=de|Substantiv}}` (named parameter before
  positional) now correctly returns `Substantiv` instead of `spr=de`.
- `pos` parser: `Grammatische Merkmale` extraction tolerates a section
  followed by a single-newline `\n{{…}}` (previously required
  `\n\n{{…}}`).
- `pos` parser: redundant `Übersicht - sch` substring check removed (the
  shorter `Übersicht` already matches).
- `flexion` parser: nested templates inside Übersicht tables
  (`|Genus={{m}}`, `|Bild=…{{Per-Deutschlandradio|…}}`) no longer
  truncate the table at the first inner `}`. Rewrites the table walk to
  brace-balanced parsing via `mwparserfromhell`. 203 pages got
  full-coverage flexion tables.
- `flexion` parser: caption-side `<ref>` blocks with named parameters
  (`Autor=`, `Titel=`, `ISBN=`, …) no longer leak as table fields.
- `flexion` parser: numeric-only keys from broken Übersicht tables are
  dropped (`Kyoto` no longer returns `{'3': "''Kyoto''", '2': '1'}`).
- `flexion` parser: multi-line `<ref>` inside a cell value is stripped
  in full (was leaving the ref body and a stray `</ref>`).
- `flexion` parser: `&nbsp;` is now actually replaced with a space (the
  trailing `;` used to leak).
- `hyphenation` parser: affix markers on the lemma (`auto-`, `-ow`,
  `-s-`) survive the syllable split instead of disappearing.
- `hyphenation` parser: trailing newline no longer glued to the last
  syllable (`A` → `['A']`, not `['A\n']`).
- `hyphenation` parser: standalone commas and dots inside chemical
  names like `1,2,3-Propentricarbonsäure` and `Web 2.0` are preserved
  (only `, ` with whitespace is treated as a word separator).
- `hyphenation` parser: abbreviation lemmas (`Mr.`, `etc.`) keep their
  trailing dot — `rstrip` now only removes characters the lemma itself
  doesn't end with.
- `hyphenation` parser: lemmas wrapped in a `{{Polytonisch|…}}` (or
  similar) template no longer leak a `}` into the last syllable.
- `language` parser: `{{Wortart|Substantiv|spr=en}}` (named instead of
  positional language) now correctly returns `lang=None` instead of
  capturing `spr=en` as the language name.
- `language` parser: tolerates Italian-style and double-space Wortart
  headers (same shapes that `entries_from_page` now accepts).
- `language` parser: `{{Wortart|Substantiv|2=Englisch|Adjektiv}}` etc.
  follow MediaWiki positional semantics (numeric position beats source
  order).
- `language` parser: the language-code loader skips empty / malformed
  lines instead of raising `IndexError` (defense against future code
  files with a trailing newline).
- `lemma` parser: nested `{{linkZiel|<lang>|<lemma>}}` templates inside
  `{{Grundformverweis Dekl|…}}` are now resolved (`kalt` → `kaldur`,
  `við` → `viður`, `hin` → `hinn`, etc.).
- `lemma` parser: `{{Lemmaverweis|#anchor|RealLemma}}` (first positional
  is just a section anchor) returns `RealLemma` instead of `None`.
- `lemma` parser: `{{Alte Schreibweise|<post-reform>|Reform …}}` is
  recognised as a VARIANT reference, pointing at the post-reform
  spelling.
- `lemma` parser: reference templates spanning multiple lines
  (`{{Alte Schreibweise|Mopps\n|Reform 1996}}`) are no longer truncated.
- `lemma` parser: reference templates buried inside `<ref>` citations
  in body prose no longer hijack the page lemma — only top-level
  templates count.
- `lemma` parser: `{{Lemmaverweis|target<!-- comment -->}}` returns
  `target` instead of the raw string with the comment.
- `lemma` parser: explicit-numeric positional `|2=value` follows
  MediaWiki semantics; whitespace around the inner wrapper template
  (`| {{linkZiel|is|kaldur}} |…`) no longer disqualifies wrapper
  detection.
- `meanings` parser: multi-line `<ref>…</ref>` blocks (whose body may
  contain a line starting with `{{…}}`) are now stripped before
  list-tokenization, so they don't truncate the section or leak `<ref>`
  fragments into the meaning text.
- `meanings` parser: `<ref name="https://…/x">` (attribute value
  containing slashes) is now matched in full.
- `meanings` parser: backref-style HTML-tag stripper in `wiki_list`
  prevents an unclosed `<ref>` from over-matching to an unrelated
  `</sup>`/`</small>` further in the text.
- `entries_from_page`: accepts double-space (`===  {{Wortart…`) and
  Italian-style headers with a lemma before the template
  (`=== ombrello {{Wortart…`). Recovers ~30 entries on pages like
  `bimbo`, `ombrello`, `civetta`, `Portus Cale`.
- `Parser.find_paragraph`: tolerates trailing whitespace
  (`{{Aussprache}} \n`, `{{Aussprache}}\t\n`) and templates with a
  parameter (`{{Herkunft|fehlt}}`) — ~600 pages got their sections
  detected for the first time.
- `Parser.find_paragraph`: strips `<ref>` blocks (multi-line and
  self-closing) before locating the section so a `\n{{…}}` inside a
  citation can no longer terminate the section capture early. All
  callers (IPA, Rhymes, Hyphenation, Meanings, Etymology) benefit.

### Added
- `pos` parser POS_MAP additions: `Bauwerksname`, `Göttername`,
  `Wiederholungszahlwort`, `Bruchzahlwort`,
  `Vervielfältigungszahlwort`, `Hiragana`, `Katakana`, `Kausaladverb`,
  `Pseudopartizip`. Recovers POS subtype info for ~260 pages.
- Shared helpers in `wiktionary_de_parser.parser`:
  - `strip_refs(text)` — remove `<ref …>…</ref>` and `<ref …/>` blocks.
  - `extract_first_positional_value(template)` — return the first
    non-empty positional parameter of a template, ignoring named
    parameters.
  - `resolve_positional_params(template)` — resolve MediaWiki positional
    semantics (bare params get the next free index, `|N=value` sets the
    explicit position, later assignments win on collision).
  - `WORTART_TEMPLATE_NAME_RE` constant shared across
    `entries_from_page`, `parse_pos`, `parse_language`.

### Removed
- `parse_ipa.WANTED_TABLE_NAMES` constant (was declared but unused; the
  flexion parser has its own active copy).

### Changed
- Bumped dependencies to current major releases:
  `lxml` 5.4 → 6.1, `mwparserfromhell` 0.6.6 → 0.7.2, `pydantic` 2.12 →
  2.13, `requests` 2.32 → 2.34, `tqdm` 4.67.1 → 4.67.3, `ipykernel`
  6.31 → 7.2, `pytest` 7.4 → 9.0, `ruff` 0.14 → 0.15. No code changes
  required.

## [0.14.2] - 2026-05-22
### Fixed
- `etymology` parser: `"zusammengesetzt aus X und dem Suffix [[-Y]]"` is now
  classified as DERIVATION (was COMPOUND). Triggered by the word "Suffix" or
  "Präfix" in the section; gated by a "Fugenelement" / "gebundenes Lexem"
  marker so genuine bound-lexeme compounds like Vexillologie or Tridecan
  stay COMPOUND.
- `etymology` parser: sections that offer two competing etymologies
  separated by `oder` / `bzw.` / `alternativ` / `auch:` (e.g.
  Alkoholabhängigkeit) are now cut at the first connector, so wikilinks
  from the alternative branch don't leak into `components`.
- `etymology` parser: interwiki/cross-project wikilinks with a leading
  colon (`[[:w:Karl Steinbuch]]`) are now filtered, plus additional
  namespace prefixes (`Hilfe:`, `Wikipedia:`, `Wiktionary:`,
  `Wikisource:`).
- `etymology` parser: wikilinks with no Latin/Greek/Cyrillic letters
  (CJK, Arabic, Hebrew) are filtered — they're glosses for foreign source
  words, not components of a German lemma.
- `etymology` parser: declined forms of POS terminology (`Substantiven`,
  `Substantivs`, `Adjektivs`, `Adjektiven`, `Verbs`, `Verben`,
  `Adverbs`) added to TERMINOLOGY filter.
- `etymology` parser: additional meta-linguistic terminology filtered
  out of components: `Flexion`, `Wortgruppe`, `Syntagma`,
  `substantiviert`, `substantivisch`, `Wortbildungselement`,
  `gebundenes lexikalisches Morphem`, `lexikalisches Morphem`,
  `implizite Derivation`, `implizite Ableitung`, `Suffigierung`,
  `Verkleinerungsform`, `Verkleinerungsendung`, `Ursprungsbedeutung`.

## [0.14.1] - 2026-05-22
### Fixed
- `etymology` parser: `[[Gleitlaut]]` is now recognised as terminology (like
  `[[Fugenelement]]`) and no longer leaks into `components`.
- `etymology` parser: sections that pack the structural claim and explanatory
  prose into a single line are now cut at the first sentence boundary
  (`;` or `. `). This prevents gloss wikilinks in trailing explanations
  (e.g. `[[sechs]]`, `[[zehn]]` after `{{Üt|grc|ἕξ}}` / `{{Ü|la|decem}}`) from
  ending up in `components`, and lets entries like `Detektiv` be classified as
  LOANWORD instead of COMPOUND when `[[Kompositum]]` only appears deep in
  explanatory text.

## [0.14.0] - 2026-05-22
### Added
- `etymology` parser for the `{{Herkunft}}` section. Returns
  `EtymologyResult` with `type` (COMPOUND, DERIVATION, MOVIERUNG, CONVERSION,
  LOANWORD, SHORTENING, VARIANT, UNKNOWN), `components`, `prefix`, `suffix`,
  `fugenelement`, and `source_language`. Exposed via
  `ParsedWiktionaryPageEntry.etymology`.

## [0.13.1] - 2025-11-16
### Changed
- Moved `ruff` from runtime dependencies to dev dependencies

## [0.13.0] - 2025-11-16
### Added
- Support for `{{Lemmaverweis}}` template to handle variant forms (alternative spellings, regional variants, pronunciation variants)
- New `ReferenceType` enum to distinguish between inflected forms and variants
- Extended lemma parsing documentation with examples

### Changed
- **BREAKING**: Replaced `Lemma.inflected: bool` with `Lemma.reference_type: ReferenceType`
  - Old: `lemma.inflected` (boolean)
  - New: `lemma.reference_type` (enum: NONE, INFLECTED, or VARIANT)
- Enhanced lemma parser to recognize both `{{Grundformverweis}}` (inflected forms) and `{{Lemmaverweis}}` (variants)
- Improved code documentation in `parse_lemma.py` with detailed examples
- updated dependencies

### Migration Guide
If you were checking for inflected forms:
```python
# Before (0.12.x):
if lemma.inflected:
    ...

# After (0.13.0):
if lemma.reference_type != ReferenceType.NONE:
    ...

# Or more specifically:
if lemma.reference_type == ReferenceType.INFLECTED:  # Only inflected forms
    ...
if lemma.reference_type == ReferenceType.VARIANT:    # Only variants
    ...
```

## [0.12.15] - 2025-11-16
### Changed
- add support for extracting POS from declinable forms in German

## [0.12.14] - 2025-11-16
### Changed
- add ruff
- add CLAUDE.md file

## [0.12.13] - 2024-12-30
### Changed
- Improved meanings parsing (experimental)

## [0.12.5] - 2024-12-30
### Changed
- Update dependencies
- Improved meanings parsing (experimental)

## [0.12.1] - 2024-12-30
### Added
- Parse meanings and add "meanings" field to output, when `include_meanings`-param ist True in `parse_entry`-call.

## [0.12.0] - 2024-07-29
### Changed
- Update value for xml property "xsi:schemaLocation" to "http://www.mediawiki.org/xml/export-0.11/"

## [0.11.5] - 2024-02-10
### Removed
- "wikicode" field from page model (not used)

### Fixed
- Performance improvements

## [0.11.4] - 2024-02-09
### Changed
- Add dict comprehension to improve performance

## [0.11.3] - 2024-02-09
### Changed
- Add None type to language
- Small improvements

## [0.11.2] - 2024-02-09
### Changed
- Rename "syllables" to "hyphenation"

## [0.11.1] - 2024-02-05
### Changed
- Allow to specify path to dump file in `WiktionaryDump` class

## [0.11.0] - 2024-02-04
### Changed
- Update dependencies
- Refactor internally to use `pydantic` models

### Removed
- Remove `Record` class
- Remove config options

### Added
- Add pydantic models
- Add WiktionaryParser and WiktionaryDump classes

## [0.10.1] - 2024-01-29
### Changed
- pass parsed wikitext internally to extraction methods
- update tests

## [0.10.0] - 2024-01-29
### Changed
- Update dependencies
- Use dataclasses instead of dicts internally
### Added
- Add "page_id" and "index" field to output (if a page contains multiple entries, the index indicates the position of the word in the page)
- Add tests for POS and language parsing
### Removed
- __BREAKING__: Removed the ability to load custom methods from outside the package. The same can be achieved by setting the "wiki_text" field in the config dict and parsing the Wikitext manually.

## [0.9.5] - 2022-07-26
### Fixed
- Make sure "title" is of base string type (not `etree._ElementUnicodeResult`)

## [0.9.4] - 2022-07-18
### Changed
- Improve typing

## [0.9.3] - 2022-07-18
### Fixed
- Fix type errors
### Added
- Add method to parse rhymes
- Add tests for rhymes parsing

## [0.9.2] - 2022-07-17
### Fixed
- Improve lemma parsing
### Added
- Add tests for lemma parsing

## [0.9.1] - 2022-07-15
### Fixed
- Make config dict keys optional

## [0.9.0] - 2022-07-13
### Added
- Add development instructions to README.md
- Add tests for syllable parsing
- Add tests for IPA parsing
- Add VSCode launch.json
- Add config dict
- Add config option to optionally include wikitext in output (disabled by default)
### Changed
- Update dependencies
- Replace Autopep with black
- Ignore inflected forms, regional slang, Austrian/Swiss dialect etc. when parsing IPA-templates from now on
- `ignored_prefixes` is now part of a config dict
### Fixed
- Improve syllable parsing
- Improve IPA parsing
### Removed
- `pyphen` as fallback for syllables parsing


## [0.8.9] - 2021-11-13
### Changed
- Change repository and package name from `wiktionary_de_parser` to `wiktionary-de-parser`

## [0.8.8] - 2021-11-12
### Changed
- Make `lemma` and `inflected` fields required fields

## [0.8.7] - 2021-11-12
### Changed
- Removed typing_extensions again

## [0.8.6] - 2021-11-12
### Added
- Added typing_extensions

## [0.8.5] - 2021-11-12
### Added
- More type hints

## [0.8.4] - 2021-11-12
### Added
- Type hint for iterable (Record)
### Changed
- removed None type dict entries in flexion parsing result
### Fixed
- minor flexion parsing improvements

## [0.8.3] - 2021-11-12
### Changed
- Converted repository to [Poetry](https://python-poetry.org/) project
- Renamed `langCode` to `lang_code`
### Added
- Started to implement tests and type hints
### Fixed
- Updated regular expression and improved flexion parsing

## [0.8.1] - 2020-07-10
### Fixed
- improve dash parsing in table values

## [0.8.0] - 2019-12-01
### Fixed
- `MANIFEST.in` added langcode files

## [0.7.9] - 2019-12-01
### Fixed
- `syllables.py` improvemed syllables parsing
### Added
- `language.py` added field `langCode` (providing ISO639-1 language code)
### Changed
- `language.py` renamed field `language` to `lang`
- `README.md` updated readme

## [0.7.8] - 2019-12-01
### Fixed
- `ipa.py` IPA parsing improvement

## [0.7.7] - 2019-07-16
### Fixed
- `pos.py` added 'Deklinierte Form' as POS (can be Substantiv, Adjektiv, Artikel, Pronomen)

## [0.7.6] - 2019-07-13
### Fixed
- `ipa.py` Match correct paragraph in WikiText for parsing IPA

## [0.7.5] - 2019-07-13
### Fixed
- `syllables.py` Improved syllables parsing

## [0.7.4] - 2019-07-13
### Changed
- `ipa.py` Make IPA field a `list` (support multiple IPA transcriptions for one word)

### Fixed
- `ipa.py` Improved IPA parsing

## [0.7.3] - 2019-05-29
### Fixed
- `pos.py` Prevent duplicate POS names

## [0.7.2] - 2019-05-29
### Fixed
- `pos.py` Toponym was a Dict key, when Template 'Deutsch Toponym Übersicht' was present (should be nested noun value)

## [0.7.1] - 2019-05-27
### Added
- [Python package](https://pypi.org) support

### Changed
- repository structure
- README.md

## [0.6.6] - 2019-04-14
### Added
- allow 'Genus 1' - 'Genus 4' in flexion dictionary
- added `inflected` field to indicate whether entry is for inflected word

### Changed
- put 'Genus' back to to flexion dictionary

### Fixed
- strip values in `lemma.py`, `language.py`, `ipa.py`

## [0.6.5] - 2019-04-14
### Added
- accept `Vorlage-Test` in regex pattern in `pos.py` & `language.py`
- accept `Merkspruch` in `pos.py`

### Fixed
- improved regex for section splitting
- improved regex for POS matching
- fix missing POS names when there is a POS template

### Removed
- language codes

## [0.6.0] - 2019-04-12
### Added
- loading custom methods via `custom_methods` argument in class constructor and `load_methods` function
- Changelog.md (this file)

### Changed
- load all files from `methods` folder and initialize them as extraction methods
- extraction methods must return a `Dict()` now
- `flexion.py`: returns 'genus' and flexion info separately

### Removed
- `method_names` in `__init__.py`

## [0.5.0] - 2019-04-11
### Added
- initial release
# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
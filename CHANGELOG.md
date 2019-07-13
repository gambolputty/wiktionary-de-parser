# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
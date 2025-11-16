# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python library that extracts linguistic data (IPA, hyphenation, flexion, POS, etc.) from German Wiktionary XML dumps. The parser processes compressed XML dumps and yields structured data per entry using Pydantic models.

## Key Commands

### Development Setup
- `poetry install` - Install all dependencies
- `poetry shell` - Activate virtual environment

### Testing
- `poetry run pytest` - Run all tests
- `poetry run pytest test/methods/test_<module>.py` - Run specific test module
- `poetry run pytest test/methods/test_<module>.py::test_function_name` - Run specific test

### Code Formatting
- `poetry run black .` - Format code with Black

### Build & Distribution
- `poetry build` - Build distribution packages
- `poetry publish` - Publish to PyPI (requires credentials)

## Architecture

### Core Components

**WiktionaryParser** (`wiktionary_de_parser/__init__.py`)
- Main entry point for parsing
- Dynamically discovers and instantiates all Parser subclasses from `parser/` directory
- Splits pages into entries (one page can contain multiple word entries)
- Orchestrates parsing by running all parser modules on each entry

**WiktionaryDump** (`wiktionary_de_parser/dump_processor/__init__.py`)
- Handles downloading and decompressing German Wiktionary XML dumps
- Provides iterator over pages using lxml's `iterparse` for memory efficiency
- Uses `bzcat`/`lbzcat` subprocess for decompression
- Filters to namespace 0 (main namespace)

**Parser Base Class** (`wiktionary_de_parser/parser/__init__.py`)
- Abstract base for all feature-specific parsers
- Each parser extracts one type of data (IPA, flexion, POS, etc.)
- Parsers are auto-discovered via directory scanning in `WiktionaryParser.__init__`

**Parser Modules** (`wiktionary_de_parser/parser/parse_*.py`)
- `parse_ipa.py` - Extracts IPA pronunciation
- `parse_hyphenation.py` - Extracts word hyphenation
- `parse_flexion.py` - Extracts declension/conjugation tables
- `parse_pos.py` - Extracts part of speech information
- `parse_language.py` - Extracts language and language code
- `parse_lemma.py` - Extracts lemma and inflection status
- `parse_rhymes.py` - Extracts rhyme information
- `parse_meanings.py` - Extracts word meanings (optional, disabled by default)

Each parser subclass must:
- Inherit from `Parser`
- Set `self.name` attribute
- Implement `run()` method returning parsed data

**Data Models** (`wiktionary_de_parser/models.py`)
- `WiktionaryPage` - Represents a raw page from XML dump
- `WiktionaryPageEntry` - Represents one entry within a page (pages can have multiple entries)
- `ParsedWiktionaryPageEntry` - Final structured output with all extracted features
- `Language`, `Lemma` - Nested data structures
- Type aliases for parser return values (`ParseIpaResult`, `ParseFlexionResult`, etc.)

### Data Flow

1. `WiktionaryDump.pages()` yields `WiktionaryPage` objects from compressed XML
2. `WiktionaryParser.entries_from_page()` splits pages into `WiktionaryPageEntry` objects using regex on wikitext
3. `WiktionaryParser.parse_entry()` runs all parser modules on an entry
4. Each parser extracts its feature from the wikitext
5. Results combined into `ParsedWiktionaryPageEntry` Pydantic model

### Testing Structure

Tests are organized in `test/`:
- `test/methods/` - Unit tests for each parser module
- `test/test_data/` - Test data for each parser module

Tests use real wikitext snippets, not mocks, to verify complete functionality.

## Important Details

- Python 3.11+ required
- Uses `lxml` for XML parsing (memory-efficient streaming)
- Uses `wikitextparser` and `mwparserfromhell` for wikitext processing
- Regex pattern for splitting entries: `r"(=== {{Wortart(?:[\w\W](?!^===? ))+)"`
- Entry splitting occurs at `==` and `===` boundaries in wikitext
- Default dump URL: `https://dumps.wikimedia.org/dewiktionary/latest/dewiktionary-latest-pages-articles-multistream.xml.bz2`

## Notebook Development

- `notebooks/notebook.ipynb` exists for interactive testing
- Use `poetry run jupyter notebook` to launch Jupyter

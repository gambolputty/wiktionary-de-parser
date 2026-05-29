"""Tests for assorted public-API behaviour not pinned elsewhere.

- ``lookup_language_code`` (case-insensitive, unknown → None)
- ``parse_lemma`` finds the form reference regardless of its position
- ``WiktionaryDump.iter_parsed(workers=1)`` smoke
- ``WiktionaryDump.pages()`` incl. the ``bz2.open`` fallback path
- ``WiktionaryDump`` constructor variants
"""

from __future__ import annotations

import bz2
from pathlib import Path

import pytest

from test.methods.helpers import make_entry

from wiktionary_de_parser import WiktionaryDump
from wiktionary_de_parser.parsers.hyphenation import parse as parse_hyphenation
from wiktionary_de_parser.parsers.inflection import (
    parse_inflection_from_wikitext,
)
from wiktionary_de_parser.parsers.language import lookup_language_code
from wiktionary_de_parser.parsers.lemma import parse


class TestLookupLanguageCode:
    def test_known_languages(self):
        assert lookup_language_code("Deutsch") == "de"
        assert lookup_language_code("Englisch") == "en"
        assert lookup_language_code("Französisch") == "fr"

    def test_case_insensitive(self):
        """The lookup table is keyed on lowercase, so editor casing
        (``DEUTSCH``, ``deutsch``, ``Deutsch``) all yield the same code."""
        assert lookup_language_code("deutsch") == "de"
        assert lookup_language_code("DEUTSCH") == "de"

    def test_unknown_returns_none(self):
        assert lookup_language_code("Klingonisch") is None

    def test_empty_and_none(self):
        assert lookup_language_code(None) is None
        assert lookup_language_code("") is None


class TestLemmaReferenceLocation:
    """Form references can appear anywhere in an entry. On real dewikt
    ``Deklinierte Form`` pages the ``{{Grundformverweis}}`` is often
    placed AFTER Worttrennung / Aussprache / Grammatische Merkmale
    (≈ 2 % of references sit past the first 800 bytes, max observed
    position ≈ 16 KB). The parser must find them regardless of position.
    """

    def test_reference_at_start_found(self):
        wt = "{{Grundformverweis|target}}\n" + ("body line\n" * 50)
        ref = parse(make_entry(wt))
        assert ref is not None
        assert ref.target == "target"

    def test_reference_past_800_chars_found(self):
        """Regression guard: a real Deklinierte-Form entry can run for
        ~1.5 KB of Worttrennung / Aussprache / Grammatische Merkmale
        before the Grundformverweis. The prefix-cutoff optimisation
        that used to live here ate ~2 % of references in production."""
        body = (
            "{{Worttrennung}}\n:lie·ben\n\n"
            "{{Aussprache}}\n:{{IPA}} {{Lautschrift|ˈliːbn̩}}\n"
            ":{{Hörbeispiele}} {{Audio|De-lieben.ogg}}\n"
            + ("\n:''note line''" * 60)
            + "\n\n{{Grammatische Merkmale}}\n"
            "*1. Person Singular Indikativ Präsens des Verbs '''[[lieben]]'''\n"
        )
        assert len(body) > 800  # sanity: header really sits past the old cutoff
        wt = (
            "=== {{Wortart|Deklinierte Form|Deutsch}} ===\n\n"
            + body
            + "\n{{Grundformverweis Konj|lieben}}\n"
        )
        ref = parse(make_entry(wt))
        assert ref is not None
        assert ref.target == "lieben"

    def test_no_reference_returns_none(self):
        wt = "no reference here, just {{not_a_reference|x}} and more text"
        assert parse(make_entry(wt)) is None

    def test_prefilter_short_circuit_on_unrelated_template(self):
        """A template whose name happens to *contain* 'Lemma' but isn't
        a reference template (e.g. ``{{LemmaTabelle}}``) must not
        trigger the prefilter."""
        wt = "{{LemmaTabelle|x}}\n"
        # ``Lemmaverweis`` is required as a complete name, ``LemmaTabelle``
        # doesn't match the prefilter — short-circuits to None.
        assert parse(make_entry(wt)) is None


# --- Iter-parsed smoke ---------------------------------------------------

# Minimal wiktionary XML dump containing one real entry. Wrapped in the
# multistream XML envelope so ``etree.iterparse`` finds the ``<page>``
# element.
_MINIMAL_DUMP_XML = """<?xml version="1.0" encoding="utf-8"?>
<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.11/" version="0.11">
  <page>
    <title>Abend</title>
    <ns>0</ns>
    <id>1</id>
    <revision>
      <model>wikitext</model>
      <text>== Abend ({{Sprache|Deutsch}}) ==
=== {{Wortart|Substantiv|Deutsch}}, {{m}} ===

{{Deutsch Substantiv Übersicht
|Genus=m
|Nominativ Singular=Abend
}}

{{Worttrennung}}
:Abend

{{Bedeutungen}}
:[1] sense
</text>
    </revision>
  </page>
</mediawiki>
"""


@pytest.fixture
def minimal_dump_path(tmp_path: Path) -> Path:
    """A real ``.xml.bz2`` file on disk so we exercise the production
    iteration path (bzcat / bz2.open) instead of stubbing it out."""
    path = tmp_path / "mini.xml.bz2"
    with bz2.open(path, "wb") as f:
        f.write(_MINIMAL_DUMP_XML.encode("utf-8"))
    return path


def _page_xml(
    title, ns, page_id, *, model="wikitext", text=None, redirect=None
):
    redirect_line = f'    <redirect title="{redirect}" />\n' if redirect else ""
    body = (
        ""
        if text is None
        else f"    <revision>\n      <model>{model}</model>\n"
        f"      <text>{text}</text>\n    </revision>\n"
    )
    return (
        f"  <page>\n    <title>{title}</title>\n    <ns>{ns}</ns>\n"
        f"    <id>{page_id}</id>\n{redirect_line}{body}  </page>\n"
    )


# A dump mixing the four shapes `_process_page_element` must distinguish:
# two real content pages, a redirect, a non-main-namespace page (ns=4),
# and a content page carrying a non-content model (css → skipped).
_NOUN_TEXT = (
    "=== {{Wortart|Substantiv|Deutsch}}, {{m}} ===\n"
    "{{Aussprache}}\n:{{IPA}} {{Lautschrift|x}}\n"
)
_MULTI_DUMP_XML = (
    '<?xml version="1.0" encoding="utf-8"?>\n'
    '<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.11/" '
    'version="0.11">\n'
    + _page_xml("Hund", 0, 1, text=_NOUN_TEXT)
    + _page_xml("hund", 0, 2, redirect="Hund")
    + _page_xml("Wiktionary:Löschkandidaten", 4, 3, text="project page")
    + _page_xml("Katze", 0, 4, text=_NOUN_TEXT)
    + _page_xml("Style", 0, 5, model="css", text=".x{}")
    + "</mediawiki>\n"
)


@pytest.fixture
def multi_dump_path(tmp_path: Path) -> Path:
    path = tmp_path / "multi.xml.bz2"
    with bz2.open(path, "wb") as f:
        f.write(_MULTI_DUMP_XML.encode("utf-8"))
    return path


class TestIterParsedSerial:
    """``workers=1`` skips the process pool and runs the orchestration
    inline. The serial path is what tests and pdb use."""

    def test_yields_parsed_entry(self, minimal_dump_path):
        dump = WiktionaryDump(dump_file_path=minimal_dump_path)
        entries = list(dump.iter_parsed(workers=1))
        assert len(entries) == 1
        e = entries[0]
        assert e.page_name == "Abend"
        assert e.language == "Deutsch"
        assert e.lemma == "Abend"
        assert e.inflection is not None
        assert e.inflection["gender"] == "m"

    @pytest.mark.parametrize("bad", [0, -1])
    def test_invalid_workers_raises(self, minimal_dump_path, bad):
        """``workers < 1`` is a usage error — raise a clear ValueError
        instead of a cryptic ``Pool(processes=0)`` failure deep in
        multiprocessing."""
        dump = WiktionaryDump(dump_file_path=minimal_dump_path)
        with pytest.raises(ValueError, match="workers must be >= 1"):
            list(dump.iter_parsed(workers=bad))


def _entry_key(e):
    return (e.page_name, e.entry_index)


class TestIterParsedParallel:
    """``workers >= 2`` takes the spawn-pool branch (``_chunks`` +
    ``_worker_parse_chunk``). Output must be identical to the serial
    path — this guards ``ParsedEntry`` picklability, spawn-import side
    effects, and batch ordering."""

    def test_parallel_matches_serial(self, multi_dump_path):
        dump = WiktionaryDump(dump_file_path=multi_dump_path)
        serial = list(dump.iter_parsed(workers=1))
        parallel = list(
            WiktionaryDump(dump_file_path=multi_dump_path).iter_parsed(
                workers=2, chunk_size=1
            )
        )
        # Same set of entries (order across pool batches is preserved by
        # imap, but compare as keyed maps to be robust either way).
        assert {_entry_key(e) for e in serial} == {
            _entry_key(e) for e in parallel
        }
        by_key = {_entry_key(e): e for e in parallel}
        for e in serial:
            p = by_key[_entry_key(e)]
            assert (e.lemma, e.language, e.ipa, e.pos) == (
                p.lemma,
                p.language,
                p.ipa,
                p.pos,
            )

    def test_parallel_yields_only_content_pages(self, multi_dump_path):
        """The redirect, ns=4, and css pages never reach the workers."""
        dump = WiktionaryDump(dump_file_path=multi_dump_path)
        names = {e.page_name for e in dump.iter_parsed(workers=2, chunk_size=1)}
        assert names == {"Hund", "Katze"}


class TestPageFiltering:
    """`_process_page_element` keeps only main-namespace content. Redirects
    pass through ``pages()`` (with ``redirect_to`` set, ``wikitext`` None);
    ns≠0 and non-content models are dropped entirely."""

    def test_pages_filters_namespace_and_model(self, multi_dump_path):
        pages = list(WiktionaryDump(dump_file_path=multi_dump_path).pages())
        by_name = {p.name: p for p in pages}

        # ns=4 project page and css-model page are gone.
        assert "Wiktionary:Löschkandidaten" not in by_name
        assert "Style" not in by_name

        # Content pages present with wikitext.
        assert by_name["Hund"].wikitext is not None
        assert by_name["Katze"].wikitext is not None

        # Redirect passes through, flagged, with no wikitext.
        assert by_name["hund"].redirect_to == "Hund"
        assert by_name["hund"].wikitext is None

    def test_content_pages_skips_redirects(self, multi_dump_path):
        """``_content_pages`` (used by iter_parsed) drops redirects and
        empties, leaving only parseable content."""
        dump = WiktionaryDump(dump_file_path=multi_dump_path)
        content = list(dump._content_pages())
        assert {p.name for p in content} == {"Hund", "Katze"}
        assert all(p.wikitext for p in content)


class TestDumpPages:
    """Direct ``pages()`` iteration on a real bz2-wrapped dump fixture."""

    def test_yields_page_with_wikitext(self, minimal_dump_path):
        dump = WiktionaryDump(dump_file_path=minimal_dump_path)
        pages = list(dump.pages())
        assert len(pages) == 1
        page = pages[0]
        assert page.page_id == 1
        assert page.name == "Abend"
        assert page.wikitext is not None
        assert "{{Wortart|Substantiv|Deutsch}}" in page.wikitext

    def test_missing_dump_file_raises(self, tmp_path):
        missing = tmp_path / "does_not_exist.xml.bz2"
        dump = WiktionaryDump(dump_file_path=missing)
        with pytest.raises(FileNotFoundError):
            list(dump.pages())

    def test_bz2_fallback_when_no_bzcat(self, minimal_dump_path, monkeypatch):
        """When neither bzcat nor lbzcat is on PATH, decoding must fall
        back to Python's ``bz2.open``. On the dev box bzcat exists, so the
        subprocess path always runs — this forces the fallback that real
        users on Windows / minimal macOS hit."""
        import wiktionary_de_parser.dump as dump_mod

        monkeypatch.setattr(dump_mod.shutil, "which", lambda _name: None)
        dump = WiktionaryDump(dump_file_path=minimal_dump_path)
        pages = list(dump.pages())
        assert len(pages) == 1
        assert pages[0].name == "Abend"
        assert "{{Wortart|Substantiv|Deutsch}}" in pages[0].wikitext

    def test_parses_newer_schema_version(self, tmp_path):
        """Namespace-agnostic parsing: a dump using a future export schema
        (here 0.12 instead of 0.11) must still yield pages. Guards against
        the hardcoded-namespace fragility."""
        xml = (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.12/" '
            'version="0.12">\n'
            "  <page>\n"
            "    <title>Zukunft</title>\n"
            "    <ns>0</ns>\n"
            "    <id>42</id>\n"
            "    <revision>\n"
            "      <model>wikitext</model>\n"
            "      <text>=== {{Wortart|Substantiv|Deutsch}} ===</text>\n"
            "    </revision>\n"
            "  </page>\n"
            "</mediawiki>\n"
        )
        path = tmp_path / "future.xml.bz2"
        with bz2.open(path, "wb") as f:
            f.write(xml.encode("utf-8"))
        dump = WiktionaryDump(dump_file_path=path)
        pages = list(dump.pages())
        assert len(pages) == 1
        assert pages[0].name == "Zukunft"
        assert pages[0].page_id == 42


class TestDumpConstructor:
    def test_dump_dir_path_builds_filename_from_url(self, tmp_path):
        """``dump_dir_path`` constructor derives the filename from the
        download URL and creates the directory."""
        target = tmp_path / "dumps"
        dump = WiktionaryDump(dump_dir_path=target)
        assert target.is_dir()
        assert dump.dump_file_path.parent == target
        assert dump.dump_file_path.name.endswith(".xml.bz2")

    def test_requires_a_path(self):
        with pytest.raises(ValueError):
            WiktionaryDump()


class TestHyphenationReturnsNoneWithoutSection:
    """With no ``{{Worttrennung}}`` section the parser must return None,
    not parse arbitrary dotted text as a hyphenation line."""

    def test_no_worttrennung_section_returns_none(self):
        # Input that contains some dotted text but no Worttrennung header.
        wikitext = (
            "== Foo ({{Sprache|Deutsch}}) ==\n"
            "=== {{Wortart|Substantiv|Deutsch}} ===\n"
            "\n"
            ":fa·ke·hyphenation·line\n"
        )
        assert parse_hyphenation(make_entry(wikitext, name="Foo")) is None


class TestInflectionTableRegexTolerance:
    """The Übersicht locator regex must tolerate whitespace and line-end
    variants editors occasionally use. Earlier versions hard-required
    one of ``[|\\n}]`` directly after ``Übersicht``, which would have
    missed e.g. tabs."""

    def _parse(self, wikitext):
        return parse_inflection_from_wikitext(wikitext)

    def test_tab_after_name(self):
        wt = (
            "{{Deutsch Substantiv Übersicht\t\n"
            "|Genus=m\n|Nominativ Singular=X\n}}"
        )
        result = self._parse(wt)
        assert result is not None
        assert result["gender"] == "m"

    def test_crlf_after_name(self):
        wt = (
            "{{Deutsch Substantiv Übersicht\r\n"
            "|Genus=f\r\n|Nominativ Singular=Y\r\n}}"
        )
        result = self._parse(wt)
        assert result is not None
        assert result["gender"] == "f"

    def test_dash_sch_variant(self):
        """``Deutsch Substantiv Übersicht -sch`` (substantivierte
        Adjektive) carries no inflection params → no data to extract."""
        assert self._parse("{{Deutsch Substantiv Übersicht -sch}}") is None

    def test_unknown_uebersicht_variant_ignored(self):
        """A template that fits the locator pattern but isn't in the
        wanted-names list must NOT be picked up."""
        wt = (
            "{{Deutsch Foobar Übersicht\n|x=1\n}}\n"
            "{{Deutsch Substantiv Übersicht\n|Genus=m\n}}"
        )
        # The unknown variant comes first in text order, but should be
        # skipped; the real Substantiv Übersicht must win.
        result = self._parse(wt)
        assert result is not None
        assert result["gender"] == "m"

    def test_commented_out_table_is_ignored(self):
        """Regression: an Übersicht template parked inside an HTML comment
        (``<!-- … -->``) must NOT be parsed — matches the old
        mwparserfromhell behaviour. Real case: 'Demodex folliculorum'."""
        wt = (
            "{{Artikel Biologische Taxonomie}}\n"
            "<!---\n"
            "{{Deutsch Substantiv Übersicht\n"
            "|Nominativ Singular= Demodex folliculorum\n"
            "|Nominativ Plural= Demodices folliculorum\n"
            "}} --->\n"
            "{{Worttrennung}}\n"
            ":De·mo·dex fol·li·cu·lo·rum\n"
        )
        assert self._parse(wt) is None

    def test_real_table_after_commented_one_wins(self):
        """If a commented-out table precedes a real one, the real one
        must still be found."""
        wt = (
            "<!-- {{Deutsch Substantiv Übersicht\n|Genus=f\n}} -->\n"
            "{{Deutsch Substantiv Übersicht\n|Genus=m\n}}\n"
        )
        result = self._parse(wt)
        assert result is not None
        assert result["gender"] == "m"

    def test_caption_fragment_with_equals_is_dropped(self):
        """A ``|Bild=…|caption`` positional containing ``=`` makes
        mwparserfromhell read the caption fragment as a named param.
        Real case 'polytrop': ``…(p = Druck, V = Volumen…)``. The bogus
        key (wiki markup + bracket) must be dropped, the real
        ``Positiv`` kept."""
        wt = (
            "{{Deutsch Adjektiv Übersicht\n"
            "|Positiv=polytrop\n"
            "|Bild 1=Pic.jpg|mini|2|''polytrope'' Zustandsänderungen "
            "(p = Druck, V = Volumen)\n"
            "}}"
        )
        result = self._parse(wt)
        assert result == {"positive": "polytrop"}


class TestSplitEntriesLinearScan:
    """``_split_entries`` is the linear-scan replacement for the old
    O(n²) regex. These tests pin specific shapes the previous version
    handled — in particular the H2/H3 boundary semantics that the
    regex bug (the one this whole test module also covers) was
    silently breaking."""

    def _parser_split(self, wikitext: str) -> list[str]:
        from wiktionary_de_parser.parser import _split_entries

        return _split_entries(wikitext)

    def test_h3_boundary_separates_entries(self):
        """``=== {{Wortart…}}`` marks both the start of an entry AND
        the boundary that ends the previous one."""
        wt = (
            "== Hallo ({{Sprache|Deutsch}}) ==\n"
            "=== {{Wortart|Interjektion|Deutsch}} ===\n\nbody A\n\n"
            "=== {{Wortart|Substantiv|Deutsch}} ===\n\nbody B\n"
        )
        slices = self._parser_split(wt)
        assert len(slices) == 2
        assert "Interjektion" in slices[0]
        assert "Substantiv" not in slices[0]
        assert "Substantiv" in slices[1]

    def test_h2_boundary_separates_languages(self):
        """A new ``== … ==`` (different language section) must end the
        current entry."""
        wt = (
            "== bimbo ({{Sprache|Englisch}}) ==\n"
            "=== {{Wortart|Substantiv|Englisch}} ===\n\nen body\n\n"
            "== bimbo ({{Sprache|Italienisch}}) ==\n"
            "=== {{Wortart|Substantiv|Italienisch}} ===\n\nit body\n"
        )
        slices = self._parser_split(wt)
        assert len(slices) == 2
        assert "Englisch" in slices[0]
        assert "Italienisch" not in slices[0]
        assert "Italienisch" in slices[1]

    def test_h4_subsection_does_not_split(self):
        """``==== Übersetzungen ====`` is a subsection inside the entry,
        NOT a boundary. The whole entry incl. subsections must end up
        in the same slice."""
        wt = (
            "=== {{Wortart|Substantiv|Deutsch}} ===\n\n"
            "{{Bedeutungen}}\n:[1] foo\n\n"
            "==== Übersetzungen ====\n"
            "{{Ü-Tabelle|1|en=foo}}\n"
        )
        slices = self._parser_split(wt)
        assert len(slices) == 1
        assert "Übersetzungen" in slices[0]
        assert "Ü-Tabelle" in slices[0]

    def test_no_wortart_header_yields_nothing(self):
        wt = "== Foo ({{Sprache|Deutsch}}) ==\n\nprose only\n"
        assert self._parser_split(wt) == []

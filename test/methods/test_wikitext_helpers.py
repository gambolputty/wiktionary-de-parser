"""Tests for primitives in ``_wikitext`` that aren't covered elsewhere.

``resolve_positional_params``, ``extract_first_positional_value`` and
``strip_refs`` are in ``test_parser_helpers.py``; header-shape
tolerances are in ``test_find_sections.py``. This module pins the
remaining primitives: ``slice_balanced_template`` (inflection's fast
path) and ``find_sections`` non-section/comment guards.
"""

from __future__ import annotations

from wiktionary_de_parser._wikitext import (
    find_sections,
    slice_balanced_template,
)


class TestSliceBalancedTemplate:
    def test_simple_template(self):
        text = "{{Foo|a|b}}"
        assert slice_balanced_template(text, 0) == "{{Foo|a|b}}"

    def test_offset_start(self):
        """``start`` doesn't have to be 0 — used by the regex-find +
        cut pattern in ``parse_inflection``."""
        text = "prefix {{Foo|x}} suffix"
        start = text.index("{{")
        assert slice_balanced_template(text, start) == "{{Foo|x}}"

    def test_nested_template(self):
        """One ``{{Per-Foo|…}}`` nested in a ``|Bild=`` caption used to
        break the previous regex-based cutting. Brace counting must
        descend into it."""
        text = "{{Outer|Bild=image.jpg{{Per-Foo|Autor=X}}|Pos=1}}"
        assert slice_balanced_template(text, 0) == text

    def test_deeply_nested(self):
        """Three levels deep — defends against off-by-one in the depth
        counter."""
        text = "{{A|{{B|{{C|x}}|y}}|z}}"
        assert slice_balanced_template(text, 0) == text

    def test_multiline_body(self):
        """Real Übersicht templates span many lines."""
        text = (
            "{{Deutsch Substantiv Übersicht\n"
            "|Genus=m\n"
            "|Nominativ Singular=Abend\n"
            "}}"
        )
        assert slice_balanced_template(text, 0) == text

    def test_unbalanced_returns_none(self):
        """If the closing ``}}`` is missing, return ``None`` rather than
        a truncated string — the caller can fall through to the regex
        path or skip the entry."""
        text = "{{Foo|a|b"
        assert slice_balanced_template(text, 0) is None

    def test_not_at_template_start_returns_none(self):
        """``start`` must point at ``{{`` — otherwise None."""
        text = "prefix {{Foo}}"
        assert slice_balanced_template(text, 0) is None  # 'p'
        assert slice_balanced_template(text, 6) is None  # ' '

    def test_template_at_end_of_text(self):
        """A balanced template touching ``len(text)`` must not trigger
        the index-out-of-range guard."""
        text = "x{{F|a}}"
        assert slice_balanced_template(text, 1) == "{{F|a}}"

    def test_only_opening_braces(self):
        """``{{`` with no body, no close — ``None`` (the guard above
        prevents an infinite loop)."""
        assert slice_balanced_template("{{", 0) is None


class TestFindSections:
    def test_single_section(self):
        wt = "{{Aussprache}}\n:body\n"
        assert find_sections(wt) == {"Aussprache": ":body\n"}

    def test_multiple_sections_first_wins(self):
        """Duplicate headings on the same page are extremely rare but
        legitimate; the first occurrence is the canonical one and the
        second is treated as content (ignored)."""
        wt = "{{Aussprache}}\n:first\n{{Aussprache}}\n:second\n"
        result = find_sections(wt)
        assert result["Aussprache"] == ":first"

    def test_empty_wikitext(self):
        assert find_sections("") == {}
        assert find_sections(None) == {}  # type: ignore[arg-type]

    def test_sections_are_independent(self):
        wt = (
            "{{Aussprache}}\n:foo\n"
            "{{Bedeutungen}}\n:[1] bar\n"
            "{{Synonyme}}\n:[1] baz\n"
        )
        result = find_sections(wt)
        assert result["Aussprache"] == ":foo"
        assert result["Bedeutungen"] == ":[1] bar"
        # last section keeps its trailing newline (runs to \Z)
        assert result["Synonyme"] == ":[1] baz\n"


class TestFindSectionsNonSectionTemplateGuard:
    """Regression: a non-section template sitting on its own line directly
    before a real section must NOT be mistaken for a section heading and
    swallow the following section's body.

    These are real dewikt cases that the first refactor broke (a single
    non-overlapping ``finditer`` pass treated the maintenance / inflection
    templates below as section headings):
      - ``{{Wort des Jahres|…}}`` before ``{{Worttrennung}}`` (Konkordanz)
      - ``{{erweitern|…}}`` before ``{{Worttrennung}}`` (-druff)
      - ``{{überarbeiten|…}}`` before ``{{Worttrennung}}`` (versus)
      - ``{{Slowenisch Pronomen|…}}`` before ``{{Aussprache}}`` (moj)
      - ``{{Slowenisch Eigenname f|…}}`` before ``{{Aussprache}}`` (Italija)
    """

    def test_wort_des_jahres_before_worttrennung(self):
        wt = "{{Wort des Jahres|2003||CH}}\n{{Worttrennung}}\n:Kon·kor·danz\n"
        result = find_sections(wt)
        assert "Worttrennung" in result
        assert result["Worttrennung"].strip() == ":Kon·kor·danz"
        # The maintenance template must not appear as a section.
        assert "Wort des Jahres" not in result

    def test_inflection_template_before_aussprache(self):
        wt = (
            "{{Slowenisch Pronomen|moj|mojega|mojemu}}\n"
            "{{Aussprache}}\n:{{IPA}} {{Lautschrift|ˈmoːj}}\n"
        )
        result = find_sections(wt)
        assert "Aussprache" in result
        assert "{{Lautschrift|ˈmoːj}}" in result["Aussprache"]

    def test_maintenance_template_with_pipe_before_worttrennung(self):
        wt = (
            "{{erweitern|weitere Kandidaten|Deutsch}}\n"
            "{{Worttrennung}}\n:-druff\n"
        )
        result = find_sections(wt)
        assert "Worttrennung" in result
        assert result["Worttrennung"].strip() == ":-druff"

    def test_non_section_template_is_not_a_section(self):
        """A template whose name isn't a known section heading never
        becomes a key, even when shaped exactly like a section."""
        wt = "{{Wort der Woche|1|2006}}\n:some body\n"
        result = find_sections(wt)
        assert result == {}


class TestFindSectionsIgnoresComments:
    """A section parked inside an HTML comment must not be parsed.

    Real case: Armenian entries (որոշիչ, ցուցական դերանուն) keep a
    placeholder ``{{Aussprache}}`` inside ``<!-- … -->`` with a stray
    ``{{Lautschrift|nɛɾ}}`` that must not be picked up as the IPA."""

    def test_commented_section_directly_after_header(self):
        wt = (
            "<!--{{Aussprache}}\n"
            ":{{IPA}} {{Lautschrift|xyz}}-->\n"
            "{{Bedeutungen}}\n:[1] sense\n"
        )
        result = find_sections(wt)
        assert "Aussprache" not in result
        assert "Bedeutungen" in result

    def test_real_section_after_commented_one(self):
        wt = (
            "<!--{{Aussprache}}\n:{{IPA}} {{Lautschrift|wrong}}-->\n"
            "{{Aussprache}}\n:{{IPA}} {{Lautschrift|right}}\n"
        )
        result = find_sections(wt)
        assert "Aussprache" in result
        assert "right" in result["Aussprache"]
        assert "wrong" not in result["Aussprache"]

"""Tests for ``find_sections`` (one-pass section extraction).

Every parser reads its section body from the entry's pre-computed
section map. These tests pin the header-shape tolerances (trailing
whitespace, pipe parameters, ref/comment stripping) on the
``find_sections`` lookup result.
"""

from wiktionary_de_parser._wikitext import find_sections


def _section(name: str, wikitext: str) -> str | None:
    return find_sections(wikitext).get(name)


def test_strict_header():
    wt = "{{Aussprache}}\n:{{IPA}} foo\n"
    assert _section("Aussprache", wt) == ":{{IPA}} foo\n"


def test_trailing_space():
    """Real Wiktionary pages (~430) put a stray space after `}}`."""
    wt = "{{Aussprache}} \n:{{IPA}} foo\n"
    assert _section("Aussprache", wt) == ":{{IPA}} foo\n"


def test_trailing_tab():
    """`euklidisch` and others use a tab after the closing braces."""
    wt = "{{Aussprache}}\t\n:{{IPA}} foo\n"
    assert _section("Aussprache", wt) == ":{{IPA}} foo\n"


def test_double_trailing_space():
    """Latin entries (morbus, maculosus, …) use two trailing spaces."""
    wt = "{{Worttrennung}}  \n:foo·bar\n"
    assert _section("Worttrennung", wt) == ":foo·bar\n"


def test_empty_pipe_param():
    """`{{Herkunft|}}` shape — empty positional parameter."""
    wt = "{{Herkunft|}}\nfrom Latin\n"
    assert _section("Herkunft", wt) == "from Latin\n"


def test_pipe_with_value():
    """`{{Herkunft|fehlt}}` — pipe with a marker value (Reno)."""
    wt = "{{Herkunft|fehlt}}\n:[1] something\n"
    assert _section("Herkunft", wt) == ":[1] something\n"


def test_section_not_found():
    wt = "{{Other}}\n:not the heading\n"
    assert _section("Aussprache", wt) is None


def test_section_terminates_at_next_template():
    """Content cuts off at next `\\n{{...`."""
    wt = "{{Aussprache}}\n:line1\n:line2\n{{Bedeutungen}}\n:[1] foo\n"
    assert _section("Aussprache", wt) == ":line1\n:line2"


def test_multiline_ref_with_nested_template_does_not_truncate():
    """Refs are stripped before section walking, so a `\\n{{Lit-…}}`
    inside a `<ref>` body cannot terminate a section capture."""
    wt = (
        "{{Aussprache}}\n"
        ":{{IPA}} {{Lautschrift|foo}}<ref>citation\n"
        "{{Lit-Bar|A=1}}</ref>\n"
        "{{Bedeutungen}}\n"
        ":[1] meaning\n"
    )
    result = _section("Aussprache", wt)
    assert result is not None
    # Must contain the IPA line, must not bleed into Bedeutungen.
    assert "{{Lautschrift|foo}}" in result
    assert "[1] meaning" not in result


def test_ref_with_url_attribute_is_stripped():
    """`<ref name="https://…">` — attribute values legitimately contain
    slashes (URLs). The ref block must still be removed in full,
    otherwise its body's `\\n{{…}}` would terminate the section
    capture."""
    wt = (
        "{{Aussprache}}\n"
        ':{{IPA}} {{Lautschrift|foo}}<ref name="https://example.com/page">cite\n'
        "{{Lit-X|A=1}}</ref>\n"
        "{{Bedeutungen}}\n"
        ":[1] meaning\n"
    )
    result = _section("Aussprache", wt)
    assert result is not None
    assert "{{Lautschrift|foo}}" in result
    assert "[1] meaning" not in result
    assert "Lit-X" not in result


def test_self_closing_ref_does_not_overmatch():
    """A self-closing `<ref name="x"/>` plus a later unrelated `</ref>`
    must not pair up and delete content between them. `strip_refs`
    removes self-closing refs first so the paired form cannot
    mis-pair."""
    wt = (
        "{{Aussprache}}\n"
        ':{{IPA}} {{Lautschrift|foo}}<ref name="x"/>\n'
        ":second line<ref>note</ref>\n"
    )
    result = _section("Aussprache", wt)
    assert result is not None
    # The unrelated `</ref>` doesn't pair with the self-closing one,
    # so the "second line" content survives.
    assert "second line" in result

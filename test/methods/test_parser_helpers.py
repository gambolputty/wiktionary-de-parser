"""Direct unit tests for the helpers in wiktionary_de_parser.parser.__init__.

These helpers (resolve_positional_params, extract_first_positional_value,
strip_refs) are shared across multiple parsers and so far were only
covered indirectly through parse_lemma / parse_language / parse_pos /
parse_ipa / parse_rhymes tests. The tests here pin their invariants
directly so a future refactor cannot quietly change semantics.
"""

import mwparserfromhell

from wiktionary_de_parser.parser import (
    extract_first_positional_value,
    resolve_positional_params,
    strip_refs,
)


def _parse_template(wikitext: str):
    """Return the first Template node parsed from wikitext."""
    parsed = mwparserfromhell.parse(wikitext)
    return parsed.filter_templates()[0]


class TestResolvePositionalParams:
    def test_bare_positionals(self):
        tmpl = _parse_template("{{T|a|b|c}}")
        result = resolve_positional_params(tmpl)
        assert {k: str(v.value) for k, v in result.items()} == {
            1: "a",
            2: "b",
            3: "c",
        }

    def test_named_param_is_ignored(self):
        """`spr=de` is a regular named param (non-digit name), not a
        positional one — must be skipped."""
        tmpl = _parse_template("{{T|spr=de|first|second}}")
        result = resolve_positional_params(tmpl)
        assert {k: str(v.value) for k, v in result.items()} == {
            1: "first",
            2: "second",
        }

    def test_numeric_named_sets_explicit_position(self):
        """`|2=Wrong|Real`: bare param gets the next free position (1);
        the explicit `|2=` sets position 2. Numeric position beats source
        order."""
        tmpl = _parse_template("{{T|2=Wrong|Real}}")
        result = resolve_positional_params(tmpl)
        assert str(result[1].value) == "Real"
        assert str(result[2].value) == "Wrong"

    def test_collision_last_write_wins(self):
        """When the explicit numeric name collides with a bare-positional
        counter, the later assignment wins — MediaWiki's last-write-wins
        rule."""
        tmpl = _parse_template("{{T|first|1=overwrite}}")
        result = resolve_positional_params(tmpl)
        assert str(result[1].value) == "overwrite"

    def test_mixed_bare_and_numeric(self):
        tmpl = _parse_template("{{T|a|3=c|b}}")
        result = resolve_positional_params(tmpl)
        assert str(result[1].value) == "a"
        assert str(result[2].value) == "b"
        assert str(result[3].value) == "c"

    def test_no_positionals(self):
        tmpl = _parse_template("{{T|spr=de|lang=en}}")
        result = resolve_positional_params(tmpl)
        assert result == {}

    def test_empty_positional_kept(self):
        """An empty value still occupies its position — the caller decides
        whether to skip empties."""
        tmpl = _parse_template("{{T||second}}")
        result = resolve_positional_params(tmpl)
        assert 1 in result
        assert str(result[1].value) == ""
        assert str(result[2].value) == "second"


class TestExtractFirstPositionalValue:
    def test_simple_positional(self):
        tmpl = _parse_template("{{Lautschrift|ˈabc}}")
        assert extract_first_positional_value(tmpl) == "ˈabc"

    def test_named_param_skipped(self):
        tmpl = _parse_template("{{Lautschrift|spr=de|ˈabc}}")
        assert extract_first_positional_value(tmpl) == "ˈabc"

    def test_empty_first_positional_skipped(self):
        tmpl = _parse_template("{{Lautschrift||ˈabc}}")
        assert extract_first_positional_value(tmpl) == "ˈabc"

    def test_all_empty_returns_none(self):
        tmpl = _parse_template("{{Lautschrift|}}")
        assert extract_first_positional_value(tmpl) is None

    def test_only_named_returns_none(self):
        tmpl = _parse_template("{{Lautschrift|spr=de}}")
        assert extract_first_positional_value(tmpl) is None

    def test_html_tag_marker_stripped(self):
        """Typographic markers like <sup>…</sup> are stripped, the
        phonetic content is kept."""
        tmpl = _parse_template("{{Lautschrift|ˈɛl<sup>ə</sup>f}}")
        assert extract_first_positional_value(tmpl) == "ˈɛləf"

    def test_ellipsis_removed(self):
        """The placeholder `…` is filtered out so a Lautschrift like
        `…ɪk` (suffix-only) returns just `ɪk`."""
        tmpl = _parse_template("{{Lautschrift|…ɪk}}")
        assert extract_first_positional_value(tmpl) == "ɪk"

    def test_pure_ellipsis_returns_none(self):
        tmpl = _parse_template("{{Lautschrift|…}}")
        assert extract_first_positional_value(tmpl) is None


class TestStripRefs:
    def test_paired_ref(self):
        assert strip_refs("a<ref>note</ref>b") == "ab"

    def test_self_closing_ref(self):
        assert strip_refs('a<ref name="x"/>b') == "ab"

    def test_multi_line_ref(self):
        assert strip_refs("a<ref>line1\nline2</ref>b") == "ab"

    def test_url_in_attribute_value(self):
        """Slashes in attribute values (URLs) must not block the match."""
        text = 'a<ref name="https://example.com/page">body</ref>b'
        assert strip_refs(text) == "ab"

    def test_self_closing_before_paired(self):
        """`<ref name="x"/>middle<ref>note</ref>` — self-closing is
        stripped first, so the paired form cannot mis-pair the unrelated
        `</ref>` with the self-closing open tag."""
        text = 'before<ref name="x"/>middle<ref>note</ref>after'
        assert strip_refs(text) == "beforemiddleafter"

    def test_no_refs(self):
        assert strip_refs("just plain text") == "just plain text"

    def test_unclosed_ref_kept(self):
        """An unclosed `<ref>` has no matching close → no match → stays in
        the output rather than over-matching to something unrelated."""
        text = "a<ref>note <sup>x</sup> rest"
        result = strip_refs(text)
        # The unclosed ref remains; rest of text is untouched.
        assert "<ref>" in result
        assert "rest" in result

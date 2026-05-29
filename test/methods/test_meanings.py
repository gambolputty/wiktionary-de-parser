"""Basic tests for the meanings parser."""

from test.methods.helpers import make_entry

from wiktionary_de_parser.models import Meaning
from wiktionary_de_parser.parsers.meanings import parse
from wiktionary_de_parser.utils.meanings.wiki_list import WikiListItem


class TestStripHtmlTags:
    def test_single_line_ref(self):
        assert (
            WikiListItem.strip_html_tags("text<ref>note</ref>more")
            == "textmore"
        )

    def test_multi_line_ref(self):
        """Multi-line refs appear on real pages (omnis cellula e cellula,
        Landschaftsschutz, Cuneiform entries). Must be stripped end-to-end."""
        assert (
            WikiListItem.strip_html_tags("text<ref>line1\nline2</ref>more")
            == "textmore"
        )

    def test_self_closing(self):
        assert (
            WikiListItem.strip_html_tags("text<ref name='x'/>more")
            == "textmore"
        )

    def test_no_tags(self):
        assert WikiListItem.strip_html_tags("plain text") == "plain text"


class TestParseMeanings:
    def test_simple_meaning(self):
        wikitext = """{{Bedeutungen}}
:[1] eine kleine Hütte
"""
        result = parse(make_entry(wikitext))
        assert result == [Meaning(text="eine kleine Hütte")]

    def test_meaning_with_multiline_ref(self):
        """The ref content (including the newline inside it) must not leak
        into the meaning text — regression for the DOTALL fix."""
        wikitext = """{{Bedeutungen}}
:[1] etwas Definition<ref>source line 1
source line 2</ref>
"""
        result = parse(make_entry(wikitext))
        assert result is not None
        assert result[0].text == "etwas Definition"
        assert "ref" not in result[0].text
        assert "source" not in result[0].text

    def test_no_meanings_section(self):
        assert parse(make_entry("just plain text")) is None


class TestHierarchicalMeanings:
    """The headline feature of meanings.py: numbered senses, nested
    sub-senses, and the tag channels. Pins the tree shape, not just a
    single flat sense."""

    def test_multiple_flat_senses(self):
        wikitext = (
            "{{Bedeutungen}}\n"
            ":[1] erster Wortsinn\n"
            ":[2] zweiter Wortsinn\n"
            ":[3] dritter Wortsinn\n"
        )
        result = parse(make_entry(wikitext))
        assert result is not None
        assert [m.text for m in result] == [
            "erster Wortsinn",
            "zweiter Wortsinn",
            "dritter Wortsinn",
        ]
        assert all(m.sublist is None for m in result)

    def test_nested_sub_sense(self):
        """``::[2.1]`` becomes a sublist of the preceding ``:[2]``."""
        wikitext = (
            "{{Bedeutungen}}\n"
            ":[1] oben eins\n"
            ":[2] oben zwei\n"
            "::[2.1] unter zwei\n"
        )
        result = parse(make_entry(wikitext))
        assert result is not None
        assert len(result) == 2
        assert result[0].sublist is None
        assert result[1].text == "oben zwei"
        assert result[1].sublist is not None
        assert [m.text for m in result[1].sublist] == ["unter zwei"]

    def test_three_levels_deep(self):
        """Lists can nest ≥3 levels (e.g. the page ``wegen``)."""
        wikitext = (
            "{{Bedeutungen}}\n"
            ":[1] ebene eins\n"
            "::[1.1] ebene zwei\n"
            ":::[1.1.1] ebene drei\n"
        )
        result = parse(make_entry(wikitext))
        assert result is not None
        level2 = result[0].sublist
        assert level2 is not None and level2[0].text == "ebene zwei"
        level3 = level2[0].sublist
        assert level3 is not None and level3[0].text == "ebene drei"

    def test_k_template_tags_are_canonicalised(self):
        """``{{K|…}}`` tags land in ``tags`` and abbreviations are
        expanded (``ugs.`` → ``umgangssprachlich``)."""
        wikitext = (
            "{{Bedeutungen}}\n"
            ":[1] {{K|Astronomie}} ein Sinn\n"
            ":[2] {{K|ugs.}} anderer Sinn\n"
        )
        result = parse(make_entry(wikitext))
        assert result is not None
        assert result[0].tags == ["Astronomie"]
        assert result[0].text == "ein Sinn"
        assert result[1].tags == ["umgangssprachlich"]

    def test_raw_tags_from_colon_prefix(self):
        """Leading ``Tag1, Tag2:`` labels become ``raw_tags`` and are
        split off the body text."""
        wikitext = (
            "{{Bedeutungen}}\n"
            ":[1] Medizin, Chirurgie: chirurgische Entfernung\n"
        )
        result = parse(make_entry(wikitext))
        assert result is not None
        assert result[0].raw_tags == ["Medizin", "Chirurgie"]
        assert result[0].text == "chirurgische Entfernung"


class TestStripRefs:
    """``strip_refs`` removes self-closing forms before paired ones so a
    ``<ref name="x"/>`` cannot pair with a later unrelated ``</ref>`` and
    delete everything in between."""

    def test_self_closing_ref_does_not_eat_until_later_close(self):
        from wiktionary_de_parser._wikitext import strip_refs

        text = 'before<ref name="x"/>middle<ref>note</ref>after'
        assert strip_refs(text) == "beforemiddleafter"

    def test_attribute_value_with_slash(self):
        """Ref attribute values can contain ``/`` (URLs). The paired form
        must still match — otherwise the ref body remains and a ``\\n{{…}}``
        inside it would truncate the section-body capture."""
        from wiktionary_de_parser._wikitext import strip_refs

        text = 'pre<ref name="https://example.com/page">body</ref>post'
        assert strip_refs(text) == "prepost"


class TestStripHtmlTagsOverMatch:
    """The backreference in ``HTML_TAG_PATTERN`` prevents an unclosed
    ``<ref>`` from over-matching to an unrelated ``</…>`` further in the
    text."""

    def test_unclosed_ref_does_not_swallow_sup(self):
        # `<ref>` has no `</ref>`. The standalone `<sup>x</sup>` later in
        # the text must be matched on its own; the unclosed `<ref>` must
        # stay (and not over-match).
        result = WikiListItem.strip_html_tags(
            "before<ref>note <sup>x</sup> after"
        )
        assert "<sup>" not in result
        assert "</sup>" not in result
        assert "x" not in result
        assert "after" in result


class TestRunWithMultilineRefBeforeFindParagraph:
    """Refs must be stripped before the section walk, otherwise a
    ``\\n{{Lit-…}}`` *inside* a ref body would truncate the Bedeutungen
    section before parse() gets a chance to strip them."""

    def test_run_strips_ref_with_nested_template_before_section_end(self):
        wikitext = (
            "{{Bedeutungen}}\n"
            ":[1] etwas Definition<ref>citation text\n"
            "{{Lit-Foo|A=1}}</ref>\n"
            "\n"
            "{{Synonyme}}\n"
            ":[1] [[other]]\n"
        )
        result = parse(make_entry(wikitext, name="test"))
        assert result is not None
        assert result[0].text == "etwas Definition"
        # The Synonyme section's ``[[other]]`` must not leak into Bedeutungen.
        assert "other" not in result[0].text

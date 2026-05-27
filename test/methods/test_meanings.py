"""Basic tests for parse_meanings — there were none before."""

from wiktionary_de_parser.parser.parse_meanings import ParseMeanings
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
        result = ParseMeanings.parse(wikitext)
        assert result == [{"text": "eine kleine Hütte"}]

    def test_meaning_with_multiline_ref(self):
        """The ref content (including the newline inside it) must not leak
        into the meaning text — regression for the DOTALL fix."""
        wikitext = """{{Bedeutungen}}
:[1] etwas Definition<ref>source line 1
source line 2</ref>
"""
        result = ParseMeanings.parse(wikitext)
        assert result is not None
        assert result[0]["text"] == "etwas Definition"
        assert "ref" not in result[0]["text"]
        assert "source" not in result[0]["text"]

    def test_no_meanings_section(self):
        assert ParseMeanings.parse("just plain text") is None


class TestStripRefs:
    """`strip_refs` removes self-closing forms before paired ones so a
    `<ref name="x"/>` cannot pair with a later unrelated `</ref>` and
    delete everything in between."""

    def test_self_closing_ref_does_not_eat_until_later_close(self):
        from wiktionary_de_parser.parser import strip_refs

        text = 'before<ref name="x"/>middle<ref>note</ref>after'
        assert strip_refs(text) == "beforemiddleafter"

    def test_attribute_value_with_slash(self):
        """Ref attribute values can contain `/` (URLs). The paired form
        must still match — otherwise the ref body remains and a `\\n{{…}}`
        inside it would truncate find_paragraph's section capture."""
        from wiktionary_de_parser.parser import strip_refs

        text = 'pre<ref name="https://example.com/page">body</ref>post'
        assert strip_refs(text) == "prepost"


class TestStripHtmlTagsOverMatch:
    """Code-review finding 8 — backreference in HTML_TAG_PATTERN prevents
    an unclosed `<ref>` from over-matching to an unrelated `</…>` further
    in the text."""

    def test_unclosed_ref_does_not_swallow_sup(self):
        # `<ref>` has no `</ref>`. The standalone `<sup>x</sup>` later in
        # the text must be matched on its own; the unclosed `<ref>` must
        # stay (and not over-match).
        from wiktionary_de_parser.utils.meanings.wiki_list import WikiListItem

        result = WikiListItem.strip_html_tags("before<ref>note <sup>x</sup> after")
        # The `<sup>x</sup>` block is stripped; the unclosed `<ref>note `
        # remains because no `</ref>` exists.
        assert "<sup>" not in result
        assert "</sup>" not in result
        assert "x" not in result
        # The unclosed ref must NOT have eaten the rest of the text.
        assert "after" in result


class TestRunWithMultilineRefBeforeFindParagraph:
    """Code-review finding 5 — refs must be stripped before find_paragraph,
    otherwise a `\\n{{Lit-…}}` *inside* a ref body would truncate the
    Bedeutungen section before parse() gets a chance to strip them."""

    def test_run_strips_ref_with_nested_template_before_section_end(self):
        from wiktionary_de_parser.models import (
            WiktionaryPage,
            WiktionaryPageEntry,
        )
        from wiktionary_de_parser.parser.parse_meanings import ParseMeanings

        wikitext = (
            "{{Bedeutungen}}\n"
            ":[1] etwas Definition<ref>citation text\n"
            "{{Lit-Foo|A=1}}</ref>\n"
            "\n"
            "{{Synonyme}}\n"
            ":[1] [[other]]\n"
        )
        page = WiktionaryPage(page_id=1, name="test", wikitext=wikitext)
        entry = WiktionaryPageEntry(page=page, index=0, wikitext=wikitext)
        result = ParseMeanings(entry).run()
        assert result is not None
        assert result[0]["text"] == "etwas Definition"
        # The Synonyme section's `[[other]]` must not leak into Bedeutungen.
        assert "other" not in result[0]["text"]

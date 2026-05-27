import re
from dataclasses import dataclass, field

from mwparserfromhell.nodes.extras.parameter import Parameter
from mwparserfromhell.nodes.template import Template

from wiktionary_de_parser.models import WiktionaryPageEntry

# `<ref>…</ref>` blocks can span multiple lines and may contain wikitext
# like `\n{{Lit-Foo}}` that would otherwise terminate find_paragraph's
# body capture early. `strip_refs` removes self-closing forms first so the
# paired pattern can use the simple `[^>]*` open-tag body — that also
# tolerates attribute values containing `/` (e.g. `<ref name="https://…/x">`).
REF_SELF_CLOSING_RE = re.compile(r"<ref[^>]*/>")
REF_BLOCK_RE = re.compile(r"<ref[^>]*>.*?</ref>", re.DOTALL)


def strip_refs(text: str) -> str:
    """Remove `<ref …/>` and `<ref …>…</ref>` blocks from wikitext."""
    text = REF_SELF_CLOSING_RE.sub("", text)
    return REF_BLOCK_RE.sub("", text)

# Wortart-header template name. Used by three independent regexes
# (entries_from_page, parse_pos, parse_language) that all need to stay in
# lock-step about which template flavours count as a real Wortart header.
WORTART_TEMPLATE_NAME_RE = r"{{Wortart(?:-Test)?"

# HTML tags occasionally embedded in single-value templates ({{Lautschrift}},
# {{Reim}}): typographic markup (<sup>, <small>) is stripped, the phonetic
# content is kept.
_HTML_TAG_RE = re.compile(r"<[^>]+>")


def extract_first_positional_value(template: Template) -> str | None:
    """Return the first non-empty positional parameter value of a template.

    Named parameters (`spr=de`, `lang=pt`, …) and empty positional slots
    are skipped. HTML markup inside the value is stripped, ellipses
    (`…`) are removed.

    Used by {{Lautschrift}}/{{Lautschrift?}} and {{Reim}} extraction.
    """
    for param in template.params:
        if param.showkey:
            continue
        value = str(param.value).replace("…", "")
        value = _HTML_TAG_RE.sub("", value).strip()
        if value:
            return value
    return None


def resolve_positional_params(template: Template) -> dict[int, Parameter]:
    """Resolve MediaWiki positional parameters of a template.

    Bare params (no `key=`) get the next free positional index; named
    params whose name is a digit (`|2=value`) explicitly set that index.
    When source order produces a collision the later assignment wins —
    this matches MediaWiki's last-write-wins semantics. Non-digit named
    params (`|spr=de`) are skipped.
    """
    positional_map: dict[int, Parameter] = {}
    counter = 0
    for p in template.params:
        if not p.showkey:
            counter += 1
            positional_map[counter] = p
        else:
            pname = str(p.name).strip()
            if pname.isascii() and pname.isdigit():
                positional_map[int(pname)] = p
    return positional_map


@dataclass(slots=True)
class Parser:
    entry: WiktionaryPageEntry
    name: str = field(init=False)

    def run(self):
        # Raise to be implemented error
        raise NotImplementedError

    @staticmethod
    def find_paragraph(heading: str, wikitext: str) -> str | None:
        # Tolerate two header-shape variations that the strict pattern
        # `{{<heading>}}\n` used to miss (~600 affected pages in the dump):
        #  - trailing whitespace before the newline:
        #    `{{Aussprache}} \n`, `{{Aussprache}}\t\n`, `{{Worttrennung}}  \n`
        #  - the template carrying a parameter:
        #    `{{Herkunft|}}`, `{{Herkunft|fehlt}}`, `{{Herkunft|}}`
        wikitext = strip_refs(wikitext)
        pattern = re.compile(
            r"{{"
            + re.escape(heading)
            + r"(?:\|[^}\n]*)?}}[ \t]*\n(.*?)(?=\n{{|\Z)",
            re.DOTALL,
        )

        match = re.search(pattern, wikitext)

        return match.group(1) if match is not None else None

    @staticmethod
    def strip_html_tags(text: str):
        return re.sub(r"<[^>]+>", " ", text)

"""Stream Wiktionary pages out of a compressed XML dump.

The dump file is a multistream ``.bz2`` archive (~300 MB for German
Wiktionary). We decompress via a ``bzcat`` subprocess pipe — Python's
``bz2.open`` works fine but ``bzcat`` releases the GIL while
decompressing, which is a small but free win.

For parallel processing, ``iter_parsed(workers=N)`` shards the parsing
work over a process pool while the main process owns the XML iteration.
"""

from __future__ import annotations

import multiprocessing
import os
import shutil
import subprocess
from pathlib import Path
from typing import Iterator

import requests
from lxml import etree
from tqdm import tqdm

from wiktionary_de_parser.models import ParsedEntry, WiktionaryPage

# Credits: https://github.com/tatuylonen/wikitextprocessor/blob/958098c50df1a116ee5549f7e4d9352f349265d7/src/wikitextprocessor/dumpparser.py

DEFAULT_WIKTIONARY_DUMP_URL = (
    "https://dumps.wikimedia.org/dewiktionary/latest/"
    "dewiktionary-latest-pages-articles-multistream.xml.bz2"
)

# Namespace-agnostic parsing via lxml's ``{*}`` wildcard. The dump uses
# the MediaWiki export schema (``…/export-0.11/`` today) — matching the
# namespace literally would silently yield zero pages the day Wikimedia
# bumps the schema to 0.12. The wildcard matches any export version.
_PAGE_TAG = "{*}page"
_NAMESPACE_IDS = {0}  # only main namespace
# https://de.wiktionary.org/wiki/Hilfe:Namensr%C3%A4ume

# Subprocess decoders to try, in order. ``bzcat`` and ``lbzcat`` take the
# same args (``-d -c``); ``lbzcat`` is a parallel drop-in. We deliberately
# do NOT use pbzip2: it needs different flags and the bz2 decode is not
# the pipeline bottleneck (mwparserfromhell parsing dominates), so the
# extra special-cased code path isn't worth the risk.
_BZIP2_DECODERS = ("bzcat", "lbzcat")


def _decompress_pipe(path: Path):
    """Return a binary stream that decompresses ``path`` on the fly.

    Prefers a ``bzcat``/``lbzcat`` subprocess over Python's ``bz2.open``
    — the subprocess releases the GIL while decompressing, overlapping a
    little with XML parsing — and falls back to ``bz2.open`` when neither
    is on PATH (e.g. on Windows).
    """
    for name in _BZIP2_DECODERS:
        exe = shutil.which(name)
        if exe is None:
            continue
        proc = subprocess.Popen(
            [exe, "-d", "-c", str(path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        assert proc.stdout is not None
        return proc.stdout, proc

    import bz2

    return bz2.open(path, "rb"), None


def _process_page_element(page_element) -> WiktionaryPage | None:
    """Build a ``WiktionaryPage`` from a parsed ``<page>`` element."""
    page_id_text = page_element.findtext("{*}id", "")
    title = page_element.findtext("{*}title", "")
    namespace_id = int(page_element.findtext("{*}ns", "0"))

    if namespace_id not in _NAMESPACE_IDS:
        return None

    redirect_element = page_element.find("{*}redirect")
    if redirect_element is not None:
        # ``redirect_to`` defaults to "" in the XML attribute — odd, but
        # matches the original semantics.
        return WiktionaryPage(
            page_id=int(page_id_text),
            name=title,
            wikitext=None,
            redirect_to=redirect_element.get("title", ""),
        )

    # Skip CSS / JavaScript / sanitized-css pages — only wikitext and
    # the listed source-code models carry real content.
    model = page_element.findtext("{*}revision/{*}model", "")
    if model not in ("wikitext", "Scribunto", "json"):
        return None

    text = page_element.findtext("{*}revision/{*}text", "")
    return WiktionaryPage(
        page_id=int(page_id_text),
        name=title,
        wikitext=text,
        redirect_to=None,
    )


class WiktionaryDump:
    """Locate / download a Wiktionary dump and iterate its pages."""

    def __init__(
        self,
        dump_dir_path: Path | str | None = None,
        dump_download_url: str = DEFAULT_WIKTIONARY_DUMP_URL,
        dump_file_path: Path | str | None = None,
    ):
        self.dump_download_url = dump_download_url

        if dump_file_path:
            self.dump_file_path = Path(dump_file_path)
        elif dump_dir_path:
            dump_dir_path = Path(dump_dir_path)
            self.dump_file_path = (
                dump_dir_path / self.dump_download_url.split("/")[-1]
            )
            dump_dir_path.mkdir(parents=True, exist_ok=True)
        else:
            raise ValueError(
                "Either dump_dir_path or dump_file_path must be provided."
            )

    def download_dump(self) -> None:
        """Download the dump file if it isn't already present."""
        if self.dump_file_path.exists():
            return

        response = requests.get(self.dump_download_url, stream=True)
        total = int(response.headers.get("content-length", 0))
        bar = tqdm(
            total=total,
            unit="iB",
            unit_scale=True,
            unit_divisor=1024,
            desc="Downloading Wiktionary dump",
        )

        with open(self.dump_file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                size = f.write(chunk)
                bar.update(size)

    def pages(self) -> Iterator[WiktionaryPage]:
        """Yield ``WiktionaryPage`` objects from the dump."""
        if not self.dump_file_path.exists():
            raise FileNotFoundError(
                f"Dump file {self.dump_file_path} does not exist. "
                "Please download the dump file first."
            )

        stream, proc = _decompress_pipe(self.dump_file_path)
        try:
            for _, page_element in etree.iterparse(stream, tag=_PAGE_TAG):
                page = _process_page_element(page_element)

                # Always clear the element, even when we filter it out,
                # otherwise the lxml tree retains every parsed page in
                # memory.
                page_element.clear(keep_tail=True)
                # Walk back to drop already-cleared siblings — keeps
                # lxml's working set bounded.
                while page_element.getprevious() is not None:
                    del page_element.getparent()[0]

                if page is None:
                    continue
                yield page
        finally:
            stream.close()
            if proc is not None:
                proc.wait()

    def iter_parsed(
        self,
        workers: int | None = None,
        chunk_size: int = 64,
    ) -> Iterator[ParsedEntry]:
        """Yield ``ParsedEntry`` objects in parallel.

        The XML iteration stays on the main process; pages are batched
        and shipped to a ``multiprocessing.Pool`` for parsing. Order
        across batches is preserved via ``imap`` (within a batch the
        order matches the input page order).

        ``workers`` defaults to ``os.cpu_count() - 1``. Set ``workers=1``
        to skip multiprocessing entirely (useful for debugging / pdb).
        """
        if workers is None:
            workers = max(1, (os.cpu_count() or 2) - 1)
        elif workers < 1:
            raise ValueError(f"workers must be >= 1, got {workers}")

        from wiktionary_de_parser.parser import WiktionaryParser

        if workers == 1:
            parser = WiktionaryParser()
            for page in self._content_pages():
                for entry in parser.entries(page):
                    yield parser.parse(entry)
            return

        ctx = multiprocessing.get_context("spawn")
        with ctx.Pool(processes=workers) as pool:
            it = self._chunks(self._content_pages(), chunk_size)
            for batch in pool.imap(_worker_parse_chunk, it, chunksize=1):
                yield from batch

    def _content_pages(self) -> Iterator[WiktionaryPage]:
        """Skip redirects and empty pages (workers never see them)."""
        for page in self.pages():
            if page.redirect_to or not page.wikitext:
                continue
            yield page

    @staticmethod
    def _chunks(
        it: Iterator[WiktionaryPage], size: int
    ) -> Iterator[list[WiktionaryPage]]:
        buf: list[WiktionaryPage] = []
        for x in it:
            buf.append(x)
            if len(buf) >= size:
                yield buf
                buf = []
        if buf:
            yield buf


def _worker_parse_chunk(pages: list[WiktionaryPage]) -> list[ParsedEntry]:
    """Pool worker: parse every entry on every page in the chunk."""
    from wiktionary_de_parser.parser import WiktionaryParser

    parser = WiktionaryParser()
    out: list[ParsedEntry] = []
    for page in pages:
        for entry in parser.entries(page):
            out.append(parser.parse(entry))
    return out

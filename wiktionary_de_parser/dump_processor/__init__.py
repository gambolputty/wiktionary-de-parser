import bz2
import shutil
import subprocess
from pathlib import Path

import requests
from lxml import etree
from tqdm import tqdm

from wiktionary_de_parser.models import WiktionaryPage

# Credits: https://github.com/tatuylonen/wikitextprocessor/blob/958098c50df1a116ee5549f7e4d9352f349265d7/src/wikitextprocessor/dumpparser.py

DEFAULT_WIKTIONARY_DUMP_URL = "https://dumps.wikimedia.org/dewiktionary/latest/dewiktionary-latest-pages-articles-multistream.xml.bz2"  # noqa: E501


class WiktionaryDump:
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

            # Create dunp_dir_path if it does not exist
            dump_dir_path.mkdir(parents=True, exist_ok=True)
        else:
            raise ValueError(
                "Either dump_dir_path or dump_file_path must be provided."
            )

    def download_dump(self):
        """
        Download the dump file to the directory specified by "dump_dir_path".
        """

        # Check if dump file already exists
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

    @staticmethod
    def process_page_data(
        page_element, namespaces: dict[None, str], namespace_ids: set[int]
    ):
        page_id = int(page_element.findtext("id", "", namespaces))
        title = page_element.findtext("title", "", namespaces)
        namespace_id = int(page_element.findtext("ns", "0", namespaces))

        if namespace_id not in namespace_ids:
            page_element.clear(keep_tail=True)
            return

        text: str | None = None
        redirect_to: str | None = None
        model = page_element.findtext("revision/model", "", namespaces)

        if (
            redirect_element := page_element.find(
                "redirect", namespaces=namespaces
            )
        ) is not None:
            redirect_to = redirect_element.get("title", "")
            # redirect_to existing implies a redirection, but having a
            # .get default to "" is a bit weird: redirect to empty string?
            # But you can't use None either..?
        else:
            if model not in {"wikitext", "Scribunto", "json"}:
                # ignore css, javascript and sanitized-css pages
                page_element.clear(keep_tail=True)
                return
            text = page_element.findtext("revision/text", "", namespaces)

        return WiktionaryPage(
            page_id=page_id,
            name=title,
            wikitext=text,
            redirect_to=redirect_to,
        )

    def pages(self):
        """
        Iterates over dump file.
        """

        # Check if dump file exists
        if not self.dump_file_path.exists():
            raise FileNotFoundError(
                f"Dump file {self.dump_file_path} does not exist. "
                "Please download the dump file first."
            )

        namespace_ids = {
            0
        }  # see https://de.wiktionary.org/wiki/Hilfe:Namensr%C3%A4ume

        with bz2.open(self.dump_file_path) as p:
            namespace_str = "http://www.mediawiki.org/xml/export-0.11/"
            namespaces = {None: namespace_str}

            for _, page_element in etree.iterparse(
                p, tag=f"{{{namespace_str}}}page"
            ):
                page = self.process_page_data(
                    page_element, namespaces, namespace_ids
                )

                if not page:
                    continue

                yield page

                page_element.clear()
                while page_element.getprevious() is not None:
                    del page_element.getparent()[0]

                # Or: page_element.clear(keep_tail=True) ?

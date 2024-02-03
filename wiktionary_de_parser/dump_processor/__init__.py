import shutil
import subprocess
from pathlib import Path

import requests
from lxml import etree
from tqdm import tqdm

from wiktionary_de_parser.models import WiktionaryPage

# Credits: https://github.com/tatuylonen/wikitextprocessor/blob/958098c50df1a116ee5549f7e4d9352f349265d7/src/wikitextprocessor/dumpparser.py

WIKTIONARY_DUMP_URL = "https://dumps.wikimedia.org/dewiktionary/latest/dewiktionary-latest-pages-articles-multistream.xml.bz2"  # noqa: E501


class WiktionaryDump:
    def __init__(self, dump_dir_path: Path | str):
        self.dump_dir_path = Path(dump_dir_path)
        self.dump_file_name = WIKTIONARY_DUMP_URL.split("/")[-1]

    # Computed property that returns the path to the dump file
    @property
    def dump_file_path(self):
        return self.dump_dir_path / self.dump_file_name

    def download_latest_dump(self):
        """
        Download the latest dump of the German Wiktionary to
        the directory specified by "dump_dir_path".
        This will download "dewiktionary-latest-pages-articles-multistream.xml.bz2".
        """

        # Check if dump file already exists
        if self.dump_file_path.exists():
            print("Dump file already exists.")
            return

        # Create dunp_dir_path if it does not exist
        self.dump_dir_path.mkdir(parents=True, exist_ok=True)

        response = requests.get(WIKTIONARY_DUMP_URL, stream=True)
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
    def decompress_dump_file(dump_path: Path) -> subprocess.Popen:
        if str(dump_path).endswith(".bz2"):
            decompress_command = (
                "lbzcat" if shutil.which("lbzcat") is not None else "bzcat"
            )
            p = subprocess.Popen(
                [decompress_command, str(dump_path)], stdout=subprocess.PIPE
            )
            if p.stdout is not None:
                return p
            else:
                raise Exception(f"No stdout from command {decompress_command}")
        else:
            raise ValueError("Dump file extension is not .bz2")

    @staticmethod
    def process_data(
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
            redirect_element := page_element.find("redirect", namespaces=namespaces)
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

        namespace_ids = {0}  # see https://de.wiktionary.org/wiki/Hilfe:Namensr%C3%A4ume

        with self.decompress_dump_file(self.dump_file_path) as p:
            namespace_str = "http://www.mediawiki.org/xml/export-0.10/"
            namespaces = {None: namespace_str}

            for _, page_element in etree.iterparse(
                p.stdout, tag=f"{{{namespace_str}}}page"
            ):
                page = self.process_data(page_element, namespaces, namespace_ids)

                if not page:
                    continue

                yield page

                page_element.clear()
                while page_element.getprevious() is not None:
                    del page_element.getparent()[0]

                # Or: page_element.clear(keep_tail=True) ?

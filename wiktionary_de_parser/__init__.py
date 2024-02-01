import re
from copy import deepcopy
from importlib.machinery import SourceFileLoader
from typing import Any, Callable, Iterable, Iterator, Tuple, TypedDict, Union

import mwparserfromhell
from lxml import etree

from wiktionary_de_parser.config import PACKAGE_PATH


class Config(TypedDict, total=False):
    ignored_prefixes: Tuple[str, ...]
    include_wikitext: bool


default_config: Config = {
    # Ignore page titles starting with these prefixes followed by ":"
    "ignored_prefixes": (
        "mediawiki:",
        "vorlage:",
        "wiktionary:",
        "hilfe:",
        "flexion:",
        "datei:",
        "verzeichnis:",
        "kategorie:",
        "reim:",
        "modul:",
        "fn:",
    ),
    # Option to make wikitext available in output
    "include_wikitext": False,
}


class Parser:
    def __init__(
        self,
        source: Any,
        config: Union[Config, None] = None,
    ) -> None:
        # Initialize 'iterparse' to only generate 'end' events on tag '<entity>'
        # Credits: https://stackoverflow.com/a/55147982/5732518
        # Prepend the default Namespace {*} to get anything.
        self.context = etree.iterparse(source, events=("end",), tag=["{*}" + "page"])

        # Create config
        user_config = deepcopy(default_config)
        if config:
            user_config.update(config)
        self.config = user_config

        # load extraction methods
        self.extraction_methods: list[Callable] = []
        self.load_methods()

    def load_methods(self) -> None:
        # load extraction methods from folder
        methods_path = PACKAGE_PATH.joinpath("methods")
        method_files = [
            f
            for f in methods_path.iterdir()
            if not f.name.startswith("__") and f.name.endswith(".py")
        ]

        for idx, file_path in enumerate(method_files):
            fullname = "method-" + str(idx)
            module: Any = SourceFileLoader(
                fullname=fullname, path=str(file_path)
            ).load_module()

            if not hasattr(module, "init"):
                raise Exception(f'No init() method found in file "{file_path.name}"')
            if not callable(module.init):
                raise Exception(f'init() method in "{file_path.name}" is not callable')

            # append method
            self.extraction_methods.append(module.init)

    def parse_page(self) -> Iterator[Tuple[int, str, str]]:
        """
        Parse the XML File for title and revision tag
        Clear/Delete the Element Tree after processing

        :return: yield title and revision wikitext
        """
        for event, elem in self.context:
            # Assign the 'elem.namespace' to the 'xpath'
            elem_namespace: str = etree.QName(elem).namespace

            _title: list[etree._ElementUnicodeResult] = elem.xpath(
                "./xmlns:title/text( )", namespaces={"xmlns": elem_namespace}
            )
            _wikitext: list[etree._ElementUnicodeResult] = elem.xpath(
                "./xmlns:revision/xmlns:text/text( )",
                namespaces={"xmlns": elem_namespace},
            )
            _page_id: list[etree._ElementUnicodeResult] = elem.xpath(
                "./xmlns:id/text( )", namespaces={"xmlns": elem_namespace}
            )

            page_id = int(_page_id[0].__str__()) if _page_id else -1
            title = _title[0].__str__() if _title else ""
            wikitext = _wikitext[0].__str__() if _wikitext else ""

            yield page_id, title, wikitext

            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]

    def parse_sections(self, wikitext: str) -> Iterable[str]:
        """
        Split page into sections. One page can have multiple word sections, for example:
            - https://de.wiktionary.org/wiki/instrument

        New sections begin at "==" and "===" (sometimes there is no "==")
        Compare:
            - https://de.wiktionary.org/wiki/instrument
            - https://de.wiktionary.org/wiki/Becken
        """
        sections: list[str] = re.findall(
            r"(=== {{Wortart(?:[\w\W](?!^===? ))+)", wikitext, re.MULTILINE
        )

        for entry in sections:
            yield entry

    def __iter__(self) -> Iterator[Record]:
        """
        Iterate all pages yielded from self.parse_page() and all word sections yielded from self.parse_sections()

        :return: Dict with final result
        """
        ignored_prefixes = self.config.get("ignored_prefixes", ())
        include_wikitext = self.config.get("include_wikitext", False)

        for page_id, title, wikitext in self.parse_page():
            # check for ignored titles
            if title.lower().startswith(ignored_prefixes):
                continue

            for index, section_text in enumerate(self.parse_sections(wikitext)):
                current_record = {
                    "page_id": page_id,
                    "index": index,
                    "title": title,
                }

                if include_wikitext:
                    current_record["wikitext"] = section_text

                # execute parse methods & update current_record
                wiki_code = mwparserfromhell.parse(section_text)
                for method in self.extraction_methods:
                    data = method(title, wiki_code)
                    current_record.update(data.__dict__)

                yield Record(**current_record)  # type: ignore

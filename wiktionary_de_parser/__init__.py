import os
import re
from pathlib import Path
from importlib.machinery import SourceFileLoader
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, TypedDict

from lxml import etree

PACKAGE_PATH = Path(__file__).parent.absolute()


class Record(TypedDict, total=False):
    title: str
    wikitext: str
    flexion: Optional[Dict[str, str]]
    ipa: Optional[List[str]]
    lang: Optional[str]
    lang_code: Optional[str]
    lemma: Optional[str]
    inflected: Optional[bool]
    pos: Optional[Dict[str, List[str]]]
    syllables: Optional[List[str]]


class Parser:
    def __init__(
        self,
        source: Any,
        custom_methods: List[Callable] = [],
        ignored_prefixes: Tuple[str, ...] = ('mediawiki:', 'vorlage:', 'wiktionary:', 'hilfe:', 'flexion:',
                                             'datei:', 'verzeichnis:', 'kategorie:', 'reim:', 'modul:', 'fn:')
    ) -> None:
        # Initialize 'iterparse' to only generate 'end' events on tag '<entity>'
        # Credits: https://stackoverflow.com/a/55147982/5732518
        # Prepend the default Namespace {*} to get anything.
        self.context = etree.iterparse(source, events=("end",), tag=['{*}' + 'page'])

        # ignore page titles starting with these prefixes followed by ":"
        self.ignored_prefixes = ignored_prefixes

        # load default & custom methods
        self.extraction_methods: List[Callable] = []
        self.load_methods(custom_methods)

    def load_methods(self, custom_methods: List[Callable]) -> None:
        # load extraction methods from folder
        methods_path = PACKAGE_PATH.joinpath('methods')
        method_files = [f for f in methods_path.iterdir() if not f.name.startswith('__') and f.name.endswith('.py')]

        for idx, file_path in enumerate(method_files):
            fullname = 'method-' + str(idx)
            module: Any = SourceFileLoader(fullname=fullname, path=str(file_path)).load_module()

            if not hasattr(module, 'init'):
                raise Exception(f'No init() method found in file "{file_path.name}"')
            if not callable(module.init):
                raise Exception(f'init() method in "{file_path.name}" is not callable')

            # append method
            self.extraction_methods.append(module.init)

        # load custom exctraction methods
        if custom_methods and isinstance(custom_methods, list):
            for method in custom_methods:
                if not callable(method):
                    raise Exception(f'Provided extraction method "{str(method)}" is not callable')
                self.extraction_methods.append(method)

    def parse_page(self) -> Iterator[Tuple[str, str]]:
        """
        Parse the XML File for title and revision tag
        Clear/Delete the Element Tree after processing

        :return: yield title and revision wikitext
        """
        for event, elem in self.context:
            # Assign the 'elem.namespace' to the 'xpath'
            elem_namespace: str = etree.QName(elem).namespace

            _title: List[str] = elem.xpath('./xmlns:title/text( )', namespaces={'xmlns': elem_namespace})
            _wikitext: List[str] = elem.xpath('./xmlns:revision/xmlns:text/text( )',
                                              namespaces={'xmlns': elem_namespace})

            title = _title[0] if _title else ''
            wikitext = _wikitext[0] if _wikitext else ''

            yield title, wikitext

            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]

    def parse_sections(self, wikitext: str) -> List[str]:
        """
        Split page into sections. One page can have multiple word sections, for example:
            - https://de.wiktionary.org/wiki/instrument

        New sections begin at "==" and "===" (sometimes there is no "==")
        Compare:
            - https://de.wiktionary.org/wiki/instrument
            - https://de.wiktionary.org/wiki/Becken
        """
        sections: List[str] = re.findall(r'(=== {{Wortart(?:[\w\W](?!^===? ))+)', wikitext, re.MULTILINE)

        for entry in sections:
            yield entry

    def __iter__(self) -> Iterator[Record]:
        """
        Iterate all pages yielded from self.parse_page() and all word sections yielded from self.parse_sections()

        :return: Dict with final result
        """
        for title, wikitext in self.parse_page():
            # check for ignored titles
            if title.lower().startswith(self.ignored_prefixes):
                continue

            for section_text in self.parse_sections(wikitext):
                current_record: Record = {
                    'title': title,
                    'wikitext': section_text
                }

                # execute parse methods & update current_record
                for method in self.extraction_methods:
                    data = method(title, section_text, current_record)
                    if data is False:
                        continue
                    current_record.update(data)

                yield current_record

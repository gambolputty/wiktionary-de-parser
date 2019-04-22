from lxml import etree
from importlib.machinery import SourceFileLoader
import os
import re


class Parser:
    def __init__(self, fh, custom_methods=[], ignored_prefixes=('mediawiki:', 'vorlage:', 'wiktionary:', 'hilfe:', 'flexion:',
                                                                'datei:', 'verzeichnis:', 'kategorie:', 'reim:', 'modul:', 'fn:')):
        # Initialize 'iterparse' to only generate 'end' events on tag '<entity>'
        # Credits: https: // stackoverflow.com/a/55147982/5732518
        # Prepend the default Namespace {*} to get anything.
        self.context = etree.iterparse(fh, events=("end",), tag=['{*}' + 'page'])

        # ignore page titles starting with these prefixes followed by ":"
        self.ignored_prefixes = ignored_prefixes

        # load default & custom methods
        self.load_methods(custom_methods)

    def load_methods(self, custom_methods):
        self.extraction_methods = []

        # load extraction methods from folder
        methods_path = os.path.join(os.path.dirname(__file__), 'methods')
        method_files = [f for f in os.listdir(methods_path) if not f.startswith('__') and f.endswith('.py')]
        for idx, f in enumerate(method_files):
            full_path = os.path.join(methods_path, f)
            module = SourceFileLoader('method-' + str(idx), full_path).load_module()

            if not hasattr(module, 'init'):
                raise Exception(f'No init() method found in file "{f}"')
            if not callable(module.init):
                raise Exception(f'init() method in "{f}" is not callable')

            # append method
            self.extraction_methods.append(module.init)

        # load custom exctraction methods
        if isinstance(custom_methods, list) and custom_methods:
            for method in custom_methods:
                if not callable(method):
                    raise Exception(f'Provided extraction method "{str(method)}" is not callable')
                self.extraction_methods.append(method)

    def parse_page(self):
        """
        Parse the XML File for title and revision tag
        Clear/Delete the Element Tree after processing

        :return: yield title and revision wikitext
        """
        for event, elem in self.context:
            # Assign the 'elem.namespace' to the 'xpath'
            elem_namespace = etree.QName(elem).namespace

            title = elem.xpath('./xmlns:title/text( )', namespaces={'xmlns': elem_namespace})
            wikitext = elem.xpath('./xmlns:revision/xmlns:text/text( )', namespaces={'xmlns': elem_namespace})

            title = title[0] if title else ''
            wikitext = wikitext[0] if wikitext else ''

            yield title, wikitext

            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]

    def parse_sections(self, wikitext):
        """
        Split page into sections. One page can have multiple word sections, for example:
            - https://de.wiktionary.org/wiki/instrument

        New sections begin at "==" and "===" (sometimes there is no "==")
        Compare:
            - https://de.wiktionary.org/wiki/instrument
            - https://de.wiktionary.org/wiki/Becken
        """
        sections = re.findall(r'(=== {{Wortart(?:[\w\W](?!^===? ))+)', wikitext, re.MULTILINE)
        for entry in sections:
            yield entry

    def __iter__(self):
        """
        Iterate all pages yielded from self.parse_page() and all word sections yielded from self.parse_sections()

        :return: Dict with final result
        """
        for title, wikitext in self.parse_page():
            # check for ignored titles
            if title.lower().startswith(self.ignored_prefixes):
                continue

            for section_text in self.parse_sections(wikitext):
                current_record = {
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

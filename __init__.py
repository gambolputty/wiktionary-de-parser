from lxml import etree
import re
import importlib


class Parser:
    def __init__(self, fh):
        """
        Initialize 'iterparse' to only generate 'end' events on tag '<entity>'
        Credits: https://stackoverflow.com/a/55147982/5732518

        :param fh: File Handle from the XML File to parse
        """

        # Prepend the default Namespace {*} to get anything.
        self.context = etree.iterparse(fh, events=("end",), tag=['{*}' + 'page'])

        # ignore page titles starting with these prefixes followed by ":"
        self.ignored_prefixes = ('mediawiki:', 'vorlage:', 'wiktionary:', 'hilfe:', 'flexion:',
                                 'datei:', 'verzeichnis:', 'kategorie:', 'reim:', 'modul:', 'fn:')

        # parse methods to apply on wikitext
        method_names = ['get_syllables']
        self.methods = {lib: importlib.import_module(
            'wiktionary_de_parser.methods.' + lib) for lib in method_names}

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
        """
        sections = re.findall(r'(^== (?:[\w\W](?!^== ))+)', wikitext, re.MULTILINE)
        for entry in sections:
            yield entry

    def __iter__(self):
        """
        Iterate all '<tag>...</tag>' Element Trees yielded from self._parse()

        :return: Dict var 'entity' {tag1, value, tag2, value, ... ,tagn, value}}
        """
        for title, wikitext in self.parse_page():
            # check for ignored titles
            if title.lower().startswith(self.ignored_prefixes):
                continue

            for section_text in self.parse_sections(wikitext):
                result = {
                    'title': title
                }

                # apply parse methods
                for module in self.methods.values():
                    result.update(module.init(title, section_text))

                yield result

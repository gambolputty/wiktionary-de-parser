import importlib.util
import inspect
import re
from pathlib import Path
from typing import Type

from wiktionary_de_parser.models import (
    ParsedWiktionaryPageEntry,
    WiktionaryPage,
    WiktionaryPageEntry,
)
from wiktionary_de_parser.parser import Parser


class WiktionaryParser:
    parser_classes: list[Type[Parser]]

    def __init__(self):
        self.parser_classes = self.find_parser_classes()

    @staticmethod
    def find_parser_classes():
        path = Path(__file__).parent / "parser"
        parent_class = Parser
        classes: list[Type[Parser]] = []

        for child in path.iterdir():
            if (
                child.is_file()
                and child.name.endswith(".py")
                and child.name != "__init__.py"
            ):
                module_name = child.stem  # Entfernen Sie die .py-Endung
                spec = importlib.util.spec_from_file_location(
                    module_name, child
                )

                if not spec or not spec.loader:
                    raise Exception(f"Could not load {child}")

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for name, obj in inspect.getmembers(module):
                    if (
                        inspect.isclass(obj)
                        and issubclass(obj, parent_class)
                        and (obj != parent_class)
                    ):
                        classes.append(obj)

        return classes

    def entries_from_page(self, page: WiktionaryPage):
        """
        Split page into entries. One page can have multiple word entries, for example:
            - https://de.wiktionary.org/wiki/instrument

        New entries begin at "==" and "===" (sometimes there is no "==")
        Compare:
            - https://de.wiktionary.org/wiki/instrument
            - https://de.wiktionary.org/wiki/Becken
        """
        if not page.wikitext:
            return

        entries: list[str] = re.findall(
            r"(=== {{Wortart(?:[\w\W](?!^===? ))+)", page.wikitext, re.MULTILINE
        )

        for index, entry in enumerate(entries):
            yield WiktionaryPageEntry(
                page=page,
                index=index,
                wikitext=entry,
            )

    def parse_entry(
        self,
        wiktionary_entry: WiktionaryPageEntry,
        include_meanings: bool = False,
    ):
        """
        Parses an entry of a page.
        """

        # Instantiate all subclasses and run them
        results = {
            instance.name: instance.run()
            for subclass in self.parser_classes
            if (instance := subclass(wiktionary_entry))
            and (include_meanings or instance.name != "meanings")
        }

        # Add the page name
        results["name"] = wiktionary_entry.page.name

        return ParsedWiktionaryPageEntry(**results)

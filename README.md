# wiktionary-de-parser

This is a Python module to extract data from German Wiktionary XML files (for Python 3.7+). It allows you to add your own extraction methods.

## Installation

`pip install wiktionary-de-parser`

## Features

- Extracts: flexion tables, genus, IPA, language, lemma, part of speech (basic), syllables, raw Wikitext
- Allows you to add your own extraction methods (pass them as argument)
- Yields per section, not per page (a word can have multiple meanings --> multiple sections of a Wiktionary pages)

## Usage

```python
from bz2 import BZ2File
from wiktionary_de_parser import Parser

bzfile_path = '/tmp/dewiktionary-latest-pages-articles-multistream.xml.bz2'
bz_file = BZ2File(bzfile_path)

for record in Parser(bz_file):
    if 'lang_code' not in record or record['lang_code'] != 'de':
      continue
    # do stuff with 'record'
```

Note: In this example we load a compressed Wiktionary dump file that was [obtained from here](https://dumps.wikimedia.org/dewiktionary/latest/dewiktionary-latest-pages-articles-multistream.xml.bz2).

### Adding new extraction methods

An extraction method takes the following arguments:

- `title` (_string_): The title of the current Wiktionary page
- `text` (_string_): The [Wikitext](https://en.wikipedia.org/wiki/Wiki#Editing) of the current word entry/section
- `current_record` (_Dict_): A dictionary with all values of the current iteration (e. g. `current_record['lang_code']`)

It returns a `Dict` with the results or `False` if the record was processed unsuccesfully.

```python
# Create a new extraction method
def my_method(title, text, current_record):
  # do stuff
  return {'my_field': my_data} if my_data else False

# Pass a list with all extraction methods to the class constructor:
for record in Parser(bz_file, custom_methods=[my_method]):
    print(record['my_field'])
```

## Sample data:

```python
{'flexion': {'Akkusativ Plural': 'Trittbrettfahrer',
             'Akkusativ Singular': 'Trittbrettfahrer',
             'Dativ Plural': 'Trittbrettfahrern',
             'Dativ Singular': 'Trittbrettfahrer',
             'Genitiv Plural': 'Trittbrettfahrer',
             'Genitiv Singular': 'Trittbrettfahrers',
             'Genus': 'm',
             'Nominativ Plural': 'Trittbrettfahrer',
             'Nominativ Singular': 'Trittbrettfahrer'},
 'inflected': False,
 'ipa': ['ˈtʁɪtbʁɛtˌfaːʁɐ'],
 'lang': 'Deutsch',
 'lang_code': 'de',
 'lemma': 'Trittbrettfahrer',
 'pos': {'Substantiv': []},
 'syllables': ['Tritt', 'brett', 'fah', 'rer'],
 'title': 'Trittbrettfahrer',
 'wikitext': '=== {{Wortart|Substantiv|Deutsch}}, {{m}} ===\n'
             '\n'
             '{{Deutsch Substantiv Übersicht\n'
             '|Genus=m\n'
             '|Nominativ Singular=Trittbrettfahrer\n'
             '|Nominativ Plural=Trittbrettfahrer\n'
             '|Genitiv Singular=Trittbrettfahrers\n'
             '|Genitiv Plural=Trittbrettfahrer\n'
             '|Dativ Singular=Trittbrettfahrer\n'
             '|Dativ Plural=Trittbrettfahrern\n'
             '|Akkusativ Singular=Trittbrettfahrer\n'
             '|Akkusativ Plural=Trittbrettfahrer\n'
             '}}\n'
             '\n'
             '{{Worttrennung}}\n'
             ':Tritt·brett·fah·rer, {{Pl.}} Tritt·brett·fah·rer\n'
             '\n'
             '{{Aussprache}}\n'
             ':{{IPA}} {{Lautschrift|ˈtʁɪtbʁɛtˌfaːʁɐ}}\n'
             ':{{Hörbeispiele}} {{Audio|}}\n'
             '\n'
             '{{Bedeutungen}}\n'
             ':[1] Person, die ohne [[Anstrengung]] an Vorteilen teilhaben '
             'will\n'
             '\n'
             '{{Herkunft}}\n'
             ':[[Determinativkompositum]] aus den Substantiven '
             "''[[Trittbrett]]'' und ''[[Fahrer]]''\n"
             '\n'
             '{{Weibliche Wortformen}}\n'
             ':[1] [[Trittbrettfahrerin]]\n'
             '\n'
             '{{Beispiele}}\n'
             ':[1] „Bleibt schließlich noch das Problem der '
             "''Trittbrettfahrer,'' die sich ohne Versicherung aus "
             'Nachlässigkeit in das soziale Netz abgleiten '
             'lassen.“<ref>{{Internetquelle|url=http://books.google.se/books?id=VjLq84xNpfMC&pg=PA446&dq=trittbrettfahrer&hl=de&sa=X&ei=8AztU4aVJYq_ygOd1oKIDA&ved=0CEEQ6AEwBjgK#v=onepage&q=trittbrettfahrer&f=false|titel=Öffentliche '
             'Finanzen in der Demokratie: Eine Einführung, Charles B. '
             'Blankart|zugriff=2014-08-14}}</ref>\n'
             '\n'
             '{{Wortbildungen}}\n'
             ':[1] [[Trittbrettfahrer-Problem]]\n'
             '\n'
             '==== {{Übersetzungen}} ====\n'
             '{{Ü-Tabelle|Ü-links=\n'
             '*{{en}}: [1] {{Ü|en|free rider}}\n'
             '*{{fi}}: [1] {{Ü|fi|siipeilijä}}, {{Ü|fi|vapaamatkustaja}}\n'
             '*{{fr}}: [1] {{Ü|fr|profiteur}}\n'
             '|Ü-rechts=\n'
             '*{{it}}: [1] {{Ü|it|scroccone}} {{m}}\n'
             '*{{es}}: [1] {{Ü|es|}}\n'
             '}}\n'
             '\n'
             '{{Referenzen}}\n'
             ':[1] {{Wikipedia|Trittbrettfahrer}}\n'
             ':[*] {{Ref-DWDS|Trittbrettfahrer}}\n'
             ':[*] {{Ref-Canoo|Trittbrettfahrer}}\n'
             ':[1] {{Ref-UniLeipzig|Trittbrettfahrer}}\n'
             ':[1] {{Ref-FreeDictionary|Trittbrettfahrer}}\n'
             '\n'
             '{{Quellen}}'}
```

## Development
This project uses [Poetry](https://python-poetry.org/).

1. Install [Poetry](https://python-poetry.org/).
2. Clone this repository
3. Run `poetry install` inside of the project folder to install dependencies.
4. Check out `run.py` and edit it.
5. Run `poetry run python wiktionary_de_parser/run.py` or `poetry run pytest` to run tests.

## License

[MIT](https://github.com/gambolputty/wiktionary-de-parser/blob/master/LICENSE.md) © Gregor Weichbrodt

# wiktionary_de_parser
`wiktionary_de_parser` is a Python module to extract data from German Wiktionary XML files. It allows you to add your own extraction methods.

## Requirements
- Python 3+ (tested with 3.7)
- [pyphen](https://pyphen.org)

## Features

- comes with preset extraction methods for:
  - flexion tables, genus, IPA, language, lemma, part of speech, syllables, raw Wikitext
- allows you to add your own extraction methods (pass them as argument)
- data values are normalized and cleaned from obsolete Wikitext markup
- yields per entry, not per page (a word can have multiple meanings, which is why some Wiktionary pages have multiple entries, called 'sections')

## Usage

Clone this repository to your project and import `wiktionary_de_parser` like this:

```python
from bz2file import BZ2File
from wiktionary_de_parser import Parser

bzfile_path = 'C:/Users/Gregor/Downloads/dewiktionary-latest-pages-articles-multistream.xml.bz2'
bz = BZ2File(bzfile_path)

for record in Parser(bz):
    if record['language'] != 'de':
      continue
    # do stuff with 'record'
```
Note: in this example we use [BZ2File](https://pypi.org/project/bz2file/) to read a compressed Wiktionary dump file.
The dump file is obtained from [here](https://dumps.wikimedia.org/dewiktionary/).

### Adding new extraction methods

All extraction methods must return a `Dict()` and accept the following arguments:
- `title` (_string_): The title of the current Wiktionary page
- `text` (_string_): The [Wikitext](https://en.wikipedia.org/wiki/Wiki#Editing) of the current word entry/section
- `current_record` (_Dict_): A dictionary with all values of the current iteration (e. g. `current_record['language']`)

```python
# Create a new extraction method
def my_method(title, text, current_record):
  # do stuff
  return {'my_field': my_data}

# Pass a list with all extraction methods to the class constructor:
for record in Parser(bz, custom_methods=[my_method]):
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
             'Nominativ Plural': 'Trittbrettfahrer',
             'Nominativ Singular': 'Trittbrettfahrer'},
 'genus': 'm',
 'ipa': 'ˈtʁɪtbʁɛtˌfaːʁɐ',
 'language': 'de',
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

## License
[MIT](https://github.com/gambolputty/wiktionary_de_parser/blob/master/LICENSE.md) © Gregor Weichbrodt

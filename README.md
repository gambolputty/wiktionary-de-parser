# wiktionary_de_parser
wiktionary_de_parser is a Python module to parse and extract data from German Wiktionary XML files. 

## Requirements
- Python 3+ (tested with 3.7)
- [pyphen](https://pyphen.org)

## Features

A word can have multiple meanings, which is why some Wiktionary entries have multiple definitions. wiktionary_de_parser takes this into account.

Values are normalized and cleaned from obsolete Wikitext markup

At the moment the following data is extracted per entry: 
**flexion info, IPA, language, lemma, part of speech, syllables, raw Wikitext**

The methods to extract the data can be found in the `methods` folder:
```
/methods
  flexion.py
  ipa.py
  language.py
  lemma.py
  pos.py
  syllables.py
```

## Usage

Clone this repository into you project and import `wiktionary_de_parser` like this:

```python
from bz2file import BZ2File
from wiktionary_de_parser import Parser

bzfile_path = 'C:/Users/Gregor/Downloads/dewiktionary-latest-pages-articles-multistream.xml.bz2'
bz = BZ2File(bzfile_path)
for record in Parser(bz):
    # do stuff with 'record'
```
Note: in this example we use [BZ2File](https://pypi.org/project/bz2file/) to read a compressed Wiktionary dump file.
The file is obtained from ([here](https://dumps.wikimedia.org/dewiktionary/))

### Adding new parsing methods
To add a new method, create a Python file inside the `methods` folder and add the filename to the variable `method_names` inside the class constructor of `Parser` in the `__init__.py` file inside the root folder. Make sure the method file has an `init()` method like this:

```python
def init(title, text, current_record):
  pass
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

# wiktionary-de-parser

This is a Python module to extract data from German Wiktionary XML files (for Python 3.11+). It allows you to add your own extraction methods.

## Installation

`pip install wiktionary-de-parser`

## Features

- Extracts flexion tables, genus, IPA, language, lemma, part of speech (basic) and syllables
- Allows you to add your own extraction methods (pass them as argument)
- Yields per entry, not per page (a page can have multiple entries/ words can have different meanings)

## Usage

```python
from bz2 import BZ2File
from wiktionary_de_parser import Parser

bzfile_path = '/tmp/dewiktionary-latest-pages-articles-multistream.xml.bz2'
bz_file = BZ2File(bzfile_path)

for record in Parser(bz_file):
    if record.lang_code != 'de':
      continue
    # do stuff with 'record'
```

Note: In this example we load a compressed Wiktionary dump file that was [obtained from here](https://dumps.wikimedia.org/dewiktionary/latest).


## Output
Example output for the page "Abend":
```python
Record(lemma='Abend',
       inflected=False,
       syllables=['Abend'],
       ipa=['ˈaːbn̩t', 'ˈaːbm̩t'],
       rhymes=['aːbn̩t'],
       pos={'Substantiv': []},
       lang='Deutsch',
       lang_code='de',
       flexion={'Akkusativ Plural': 'Abende',
                'Akkusativ Singular': 'Abend',
                'Dativ Plural': 'Abenden',
                'Dativ Singular': 'Abend',
                'Genitiv Plural': 'Abende',
                'Genitiv Singular': 'Abends',
                'Genus': 'm',
                'Nominativ Plural': 'Abende',
                'Nominativ Singular': 'Abend'},
       page_id=5719,
       index=0,
       title='Abend',
       wikitext=None)

Record(lemma='Abend',
       inflected=False,
       syllables=['Abend'],
       ipa=['ˈaːbn̩t'],
       rhymes=['aːbn̩t'],
       pos={'Substantiv': ['Nachname']},
       lang='Deutsch',
       lang_code='de',
       flexion=None,
       page_id=5719,
       index=1,
       title='Abend',
       wikitext=None)

Record(lemma='Abend',
       inflected=False,
       syllables=['Abend'],
       ipa=['ˈaːbn̩t', 'ˈaːbm̩t'],
       rhymes=['aːbn̩t'],
       pos={'Substantiv': ['Toponym']},
       lang='Deutsch',
       lang_code='de',
       flexion=None,
       page_id=5719,
       index=2,
       title='Abend',
       wikitext=None)
```

## Development
This project uses [Poetry](https://python-poetry.org/).

1. Install [Poetry](https://python-poetry.org/).
2. Clone this repository
3. Run `poetry install` inside of the project folder to install dependencies.
4. Change `wiktionary_de_parser/run.py` to your needs.
5. Run `poetry run python wiktionary_de_parser/run.py` to run the parser. Or `poetry run pytest` to run tests.

## License

[MIT](https://github.com/gambolputty/wiktionary-de-parser/blob/master/LICENSE.md) © Gregor Weichbrodt

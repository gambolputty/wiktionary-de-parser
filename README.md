# wiktionary_de_parser
wiktionary_de_parser is a Python module to parse German Wiktionary XML files. It is equipped with predefined methods to extract data from a Wiktionary entry. 

## Features

A word can have multiple meanings, which is why some Wiktionary entries have multiple definitions. wiktionary_de_parser takes this into account.

### Extracting data
At the moment the following data is extracted per entry:

**flexion info, IPA, language, lemma, part of speech, syllables, raw Wikitext**

The methods to extract the data can be found as files in the Methods folder:
```
/methods
  flexion.py
  ipa.py
  language.py
  lemma.py
  pos.py
  syllables.py
```

## Requirements
- Python 3+ (tested with 3.7)
- [pyphen](https://pyphen.org)


## License
[MIT](https://github.com/gambolputty/wiktionary_de_parser/blob/master/LICENSE.md) © Gregor Weichbrodt

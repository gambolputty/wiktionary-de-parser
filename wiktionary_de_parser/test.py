import os
from os import name as os_name
import sys
from bz2 import BZ2File
from pdb import set_trace as bp
from pprint import pprint
from __init__ import Parser

# add parent dir to PATH
sys.path.insert(1, os.path.join(sys.path[0], '..'))

bzfile_path = '/mnt/c/Users/gregor/Downloads/dewiktionary-latest-pages-articles-multistream.xml.bz2'
bz = BZ2File(bzfile_path)
collection = set()
for record in Parser(bz):

    # German entries missig IPA:
    # if record['title'] not in collection and \
    #     'langCode' in record and record['langCode'] == 'de' and \
    #     'pos' in record and 'Abkürzung' not in record['pos'] and \
    #     'ipa' not in record:
    #     print(record['title'])

    # if 'langCode' in record:
    #     print(record['langCode'])

    if record['title'] == 'Drittes Reich':
        pprint(record)
    # if 'syllables' in record:
    #     print(record['title'])
    #     print(record['syllables'])
    #     print()

    # # German entries missig syls:
    # if record['title'] not in collection and \
    #     'langCode' in record and record['langCode'] == 'de' and \
    #     'pos' in record and 'Abkürzung' not in record['pos'] and \
    #     'syllables' not in record:
    #     print(record['title'])

    collection.add(record['title'])

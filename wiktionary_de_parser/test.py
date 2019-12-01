import os
from os import name as os_name
import sys
from bz2file import BZ2File
from pdb import set_trace as bp
from pprint import pprint
from __init__ import Parser

# add parent dir to PATH
sys.path.insert(1, os.path.join(sys.path[0], '..'))

if os_name == 'nt':
    bzfile_path = 'C:/Users/Gregor/Downloads/dewiktionary-latest-pages-articles-multistream.xml.bz2'
else:
    bzfile_path = '/Users/gregor/Downloads/dewiktionary-latest-pages-articles-multistream.xml.bz2'
bz = BZ2File(bzfile_path)
collection = set()
for record in Parser(bz):
    if 'lang' in record and record['lang'] == 'Deutsch' and 'ipa' not in record:
        print(record['title'])

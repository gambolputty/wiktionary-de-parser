import os
import sys
from bz2file import BZ2File
from __init__ import Parser

# add parent dir to PATH
sys.path.insert(1, os.path.join(sys.path[0], '..'))

bzfile_path = 'C:/Users/Gregor/Downloads/dewiktionary-latest-pages-articles-multistream.xml.bz2'
bz = BZ2File(bzfile_path)
collection = set()
for record in Parser(bz):
    pass

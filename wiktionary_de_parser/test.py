from bz2 import BZ2File
from pprint import pprint

from __init__ import Parser

bzfile_path = "tmp/dewiktionary-latest-pages-articles-multistream.xml.bz2"
bz = BZ2File(bzfile_path)

for record in Parser(bz):
    pass

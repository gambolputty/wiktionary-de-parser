from bz2file import BZ2File
from __init__ import Parser


bzfile_path = 'C:/Users/Gregor/Downloads/dewiktionary-latest-pages-articles-multistream.xml.bz2'
bz = BZ2File(bzfile_path)
prefixes = set()
for record in Parser(bz):
    if ':' in record['title']:
        title = record['title']
        colon_index = title.index(':')
        prefix = title[0:colon_index]
        if prefix not in prefixes:
            prefixes.add(prefix)
            print(prefix)

from bz2file import BZ2File
from __init__ import Parser


bzfile_path = 'C:/Users/Gregor/Downloads/dewiktionary-latest-pages-articles-multistream.xml.bz2'
bz = BZ2File(bzfile_path)
collection = set()
for record in Parser(bz):
    if not record['part_of_speech']:
        continue
    pos = [x for x in record['part_of_speech'] if x not in collection]
    if pos:
        collection.update(pos)
        for p in pos:
            print(p)

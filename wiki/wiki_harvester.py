import wikipedia
import sys
import datetime
import argparse
import string
import collections
from multiprocessing import Process, Queue

verbose_output = False

# Lädt rekursiv alle verlinkten Artikel bis die maximale Tiefe erreicht ist
def load_recursive(page, queue, depth=2, scanned=set()):
    if depth <= 0 or (page in scanned and depth == 1):
        #print('skipping %s because it already exists and no further depths are being analyzed anyway'%(page))
        return scanned
    print(f"Start recursive loading from page {page}")
    scanned.add(page)

    try:
        loaded_page = wikipedia.page(page)

        for sub_page in loaded_page.links:
            scanned = load_recursive(sub_page, queue, depth - 1,  scanned)

        content = loaded_page.content
        if content:
            queue.put({"depth":depth, "page":page, "content":loaded_page.content}, block=True, timeout=None)

    except wikipedia.DisambiguationError:
        scanned = load_recursive_by_search(page, queue, depth - 1,  scanned)
    except wikipedia.PageError:
        return scanned

    #sys.stdout.write("\r%i pages scanned" % (len(scanned)))
    return scanned


# Sucht nach dem übergebenen Begriff und führt die rekursive auf jedes der Ergebnisse aus
def load_recursive_by_search(search, process_all_results, queue, depth=1, scanned = set()):
    search_result = wikipedia.search(search)
    if not process_all_results:
        search_result = search_result[:1]
    for result in search_result:
        scanned = load_recursive(result, queue, depth,  scanned)
    return scanned

def search_process(search_list, process_all_results, queue, depth):
    scanned = set()
    print("pages found: %s"%(scanned))
    for search in search_list:
        print("starting with %s"%(search))
        scanned = load_recursive_by_search(search, process_all_results, queue, depth, scanned)
        print("%i sites have been scanned"%(len(scanned)))
    queue.put(None, block=True, timeout=None)


def main(args):
    wikipedia.set_lang(args.language)
    wikipedia.set_rate_limiting(True, min_wait=datetime.timedelta(0, 0, 50000))
    max_queue_size = 100
    page_queue = Queue(maxsize=max_queue_size)

    page_queue = Queue(maxsize=max_queue_size)
    p = Process(target=search_process, args=([args.query],args.all,page_queue,args.depth,))
    p.start()

    counter = collections.Counter()
    for document in iter(page_queue.get, None):
        # print(f"depth {document['depth']} loaded page {document['page']} with length {len(document['content'])}")
        if args.c:
            counter.update(map(lambda s: s.translate(str.maketrans('', '', string.punctuation)) ,document['content'].split()))
        else:
            counter.update(document['content'].split())

    if args.s:
        for line in counter.most_common(1000):
            word, _ =  line
            args.o.write("%s\n" % word)
    else:
        for line in counter.most_common():
            word, _ =  line
            args.o.write("%s\n" % word)



if __name__ == "__main__":
    parser = argparse.ArgumentParser('''Query data from wikipedia by supplying a query, depth and source language''')
    parser.add_argument('-d', '--depth', default=2, type=int, help='Query depth. Runtime and output size increase exponentially with it.')
    parser.add_argument('-l', '--language', default='de', type=str, help='Languages to query e.g. en')
    parser.add_argument('-a', '--all', default=False, action='store_true', help='Process all search result instead of only the first one')
    parser.add_argument('-s', '--size', type=int, help='Output the n most common words')
    parser.add_argument('-c', default=True, action='store_true', help='Cleanup punctation in output')
    parser.add_argument('-v', default=False, action='store_true', help='Verbose output, polutes stdout')
    parser.add_argument('-o', type=argparse.FileType('w',encoding="utf-8"), default=sys.stdout, help='Output file')
    parser.add_argument('query', nargs=1, help='Query to run')

    args = parser.parse_args()
    verbose_output = args.v
    main(args)

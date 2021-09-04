import wikipediaapi
import sys
import datetime
import argparse
import string
import collections
from multiprocessing import Process, Queue

verbose_output = False

# Recursively loads all sub pages until the depth is 0 (basecase)
def load_recursive(page, queue, depth=2, scanned=set()):
    page_title = page.title
    if isinstance(page_title, list):
        page_title = page_title[0]

    if depth <= 0 or (page_title in scanned and depth == 1):
        return scanned
    # if verbose_output:
    print(f"Start recursive loading from page {page_title}")
    scanned.add(page_title)

    links = page.links
    for title in sorted(links.keys()):
        scanned = load_recursive(links[title], queue, depth - 1,  scanned)

    content = page.text
    if content:
        queue.put({"depth":depth, "page":page_title, "content":content}, block=True, timeout=None)

    return scanned

# Starts the scraping at the supplied pages
def scraping_process(pages, queue, depth):
    if verbose_output:
        print(f"start scriping {pages}")
    scanned = set()
    for page in pages:
        if verbose_output:
            print("starting with %s"%(page.title))
        scanned = load_recursive(page, queue, depth, scanned)
        if verbose_output:
            print("%i sites have been scanned"%(len(scanned)))
    queue.put(None, block=True, timeout=None)


def main(args):
    wikipedia = wikipediaapi.Wikipedia(language = args.language,
        extract_format = wikipediaapi.ExtractFormat.WIKI, timeout=args.timeout)
    page = wikipedia.page(args.page)
    if verbose_output and not page.exists():
        print(f"page {args.page} does not exist")
        quit()

    # wikipedia.set_rate_limiting(True, min_wait=datetime.timedelta(0, 0, 50000))
    max_queue_size = 100
    page_queue = Queue(maxsize=max_queue_size)

    page_queue = Queue(maxsize=max_queue_size)
    p = Process(target=scraping_process, args=([page],page_queue,args.depth,))
    p.start()

    counter = collections.Counter()
    for document in iter(page_queue.get, None):
        # print(f"depth {document['depth']} loaded page {document['page']} with length {len(document['content'])}")
        if args.c:
            counter.update(map(lambda s: s.translate(str.maketrans('', '', string.punctuation)) ,document['content'].split()))
        else:
            counter.update(document['content'].split())

    if hasattr(args, 'size'):
        for line in counter.most_common(args.size):
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
    parser.add_argument('-s', '--size', type=int, help='Output the n most common words')
    parser.add_argument('-c', default=True, action='store_true', help='Cleanup punctation in output')
    parser.add_argument('-v', action='store_true', help='Verbose output, polutes stdout')
    parser.add_argument('-t', '--timeout', default=30, type=int, help='Timeout of the requests to wikipedia')
    parser.add_argument('-o', type=argparse.FileType('w',encoding="utf-8"), default=sys.stdout, help='Output file')
    parser.add_argument('page', nargs=1, help='Page to start processing from')

    args = parser.parse_args()
    verbose_output = args.v
    main(args)

from bs4 import BeautifulSoup
import pandas as pd
import queue
import threading
import time
import os
import random
import math
import requests
import argparse

URL = "https://www.abebooks.co.uk/servlet/SearchResults?bi=0&bx=off&cm_sp=SearchF-_-Advtab1-_-Results&ds=30&isbn={isbn}&n=200000169&recentlyadded=all&sortby=17&sts=t"
OUTPUTFILE = "out.csv"
ISBN_FILE = "./isbn.xlsx"
ISBN_LIST = []
FAILED_ISBN = set([])
MAX_RETRIES = 0
NUM_THREADS = 4
DEBUG = False
SLEEP_TIMER = 0.5

# PROXY LIST FROM PROXYSTORM
# PROXY_LIST = [
# '173.208.208.42:19018',
# '142.54.179.98:19016',
# '204.12.211.114:19011',
# '69.30.217.114:19006',
# '208.110.86.178:19012'
# ]

PROXY_LIST = set([])


def rebuild_proxylist():
    global PROXY_LIST
    if len(PROXY_LIST) < 4:
        os.system("curl 'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=200&country=all&ssl=all&anonymity=all&simplified=true' > http_proxies.txt")
        with open("http_proxies.txt") as fp:
            PROXY_LIST = set([x.strip() for x in fp.readlines()])
        print("Proxy List Rebuilt.")
        if DEBUG:
            print(PROXY_LIST)


def get_next_proxy():
    return random.sample(PROXY_LIST, 1)[0]


def remove_dead_proxy(ip):
    global PROXY_LIST
    if ip in PROXY_LIST:
        PROXY_LIST.remove(ip)
    rebuild_proxylist()


def get_isbns():
    return list(set(pd.read_excel(ISBN_FILE)["ISBN"]))


def worker():
    global FAILED_ISBN
    _p = get_next_proxy()
    proxies = {
        "http": _p,
        "https": _p
    }
    counter = 0
    session = requests.Session()
    while True:
        isbn, fp, _attempt = q.get()
        if counter % 30 == 0:
            session = requests.Session()
        counter += 1
        try:
            response = session.get(URL.format(isbn=isbn), proxies=proxies)
            # print(response.status_code, proxies['http'])
            if response.status_code == 429:
                q.put((isbn, fp, _attempt+1))
                _p = get_next_proxy()
                proxies = {
                    "http": _p,
                    "https": _p
                }
            elif response.status_code == 403:
                remove_dead_proxy(_p)
                q.put((isbn, fp, _attempt+1))
                _p = get_next_proxy()
                proxies = {
                    "http": _p,
                    "https": _p
                }
                # time.sleep(3 + math.floor(random.random() * 5))
            markup = response.text
            if DEBUG:
                f_name = f"./scrapes/{isbn}.html"
                os.makedirs(os.path.dirname(f_name), exist_ok=True)
                with open(f_name, "w") as _fp:
                    _fp.write(markup)
            bs_data = BeautifulSoup(markup, "html.parser")
            try:
                _cost = bs_data.find(
                    "div", attrs={"id": "srp-item-price-1"}).text.split(" ")[1]
                if DEBUG:
                    print(
                        f"{response.status_code}, {proxies['http']} | Writing {isbn} => {_cost}")
                fp.write(",".join([isbn, _cost]) + "\n")
            except AttributeError as e:
                if DEBUG:
                    print(f"ISBN FAILURE: {isbn}")
                # -1 Represents Unable to find the file.
                if _attempt < MAX_RETRIES:
                    q.put((isbn, fp, _attempt + 1))
                else:
                    fp.write(",".join([isbn, '-1']) + "\n")
                    FAILED_ISBN.add(isbn)
        except OSError as e:
            if DEBUG:
                print("Possible Proxy dead. ", _p)
            remove_dead_proxy(_p)
            _p = get_next_proxy()
            proxies = {
                "http": _p,
                "https": _p
            }
            if _attempt < MAX_RETRIES:
                q.put((isbn, fp, _attempt + 1))
            else:
                fp.write(",".join([isbn, '-2']) + "\n")
        except Exception as e:
            if DEBUG:
                print("Failed to get file. ", e)
            _p = get_next_proxy()
            proxies = {
                "http": _p,
                "https": _p
            }
            if _attempt < MAX_RETRIES:
                q.put((isbn, fp, _attemp + 1))
            else:
                fp.write(",".join([isbn, '-2']) + "\n")
        q.task_done()

        if SLEEP_TIMER is not None and SLEEP_TIMER > 0:
            time.sleep(SLEEP_TIMER)


def main():
    global q
    global ISBN_LIST
    q = queue.Queue()
    fp = open(OUTPUTFILE, "w+")
    count = 0
    ISBN_LIST = get_isbns()
    for isbn in ISBN_LIST:
        q.put((isbn, fp, 0))
    if DEBUG:
        print(f"Size: {len(ISBN_LIST)}")

    for i in range(NUM_THREADS):
        x = threading.Thread(target=worker)
        x.daemon = True
        x.start()
    q.join()
    fp.close()
    with open("failed_isbn.csv", "w+") as fp:
        fp.writelines([str(x)+'\n' for x in FAILED_ISBN])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-o', '--outfile', help=f'File output.  Default: {OUTPUTFILE}', default=OUTPUTFILE)
    parser.add_argument(
        'input', help=f"ABS path to Input xlsx ISBN file. Default: '{ISBN_FILE}''", default=ISBN_FILE)
    parser.add_argument('--retries', help="Max Retries",
                        type=int, default=MAX_RETRIES)
    parser.add_argument(
        '-t', '--threads', help="Number of Threads", type=int, default=NUM_THREADS)
    parser.add_argument(
        '--sleep', help=f"Sleep Timer.  Default: {SLEEP_TIMER} seconds", type=float, default=SLEEP_TIMER)

    args = parser.parse_args()
    if args.outfile:
        OUTPUTFILE = args.outfile
    if args.input:
        ISBN_FILE = args.input
    if args.retries:
        MAX_RETRIES = args.retries
    if args.threads:
        NUM_THREADS = args.threads
    if args.sleep:
        SLEEP_TIMER = args.sleep

    print("Starting.")
    rebuild_proxylist()
    START = time.time()
    main()
    END = time.time()
    _overall = END - START
    print(
        f"Application Completed Running.\nNumber of ISBN Checked: {len(ISBN_LIST)}\nFailed Items: {len(FAILED_ISBN)}\n Time to Completion: {_overall}")

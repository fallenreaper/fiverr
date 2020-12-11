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
from typing import List

URL = "https://www.bookfinder.com/search/?isbn={isbn}&new_used=*&st=sr&ac=qr"
OUTPUTFILE = "out.csv"
ISBN_FILE = "./isbn.xlsx"
ISBN_LIST = []
THREAD_LIST: List[threading.Thread] = []
FAILED_ISBN = set([])
MAX_RETRIES = 0
NUM_THREADS = 4
DEBUG = False
SLEEP_TIMER = 0.5
MAX_PROXY_LATENCY = 200
PROXY_FILE = None
__RESULTS = []
__counter = 0

time_between_proxy_rebuilds = None
PROXY_LIST = set([])

def rebuild_proxylist():
    global PROXY_LIST
    global time_between_proxy_rebuilds
    if time_between_proxy_rebuilds is None:
        time_between_proxy_rebuilds = time.time()
    else:
        _under_3_minutes = 3*60
        if (PROXY_FILE is not None or len(PROXY_LIST) < 4) and (time.time() - time_between_proxy_rebuilds) < _under_3_minutes:
            print("[WARNING] Rebuilding Proxy List too Frequently.  Cause:  Too Many Dead or Offline Proxies. This can drastically slow down Data processing.")

    if PROXY_FILE is not None:
        with open(PROXY_FILE) as fp:
            PROXY_LIST = set([x.strip() for x in fp.readlines()])
        print("Proxy List Rebuilt.")
        if DEBUG:
            print(PROXY_LIST)
    elif len(PROXY_LIST) < 4:
        _url = f"https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout={MAX_PROXY_LATENCY}&country=all&ssl=all&anonymity=all&simplified=true"
        proxydata = requests.get(_url).text.split("\n")
        PROXY_LIST = set([x.strip() for x in proxydata if x.strip() != ''])
        print("Proxy List Rebuilt.")
        if DEBUG:
            print(PROXY_LIST)


def get_next_proxy():
    if len(PROXY_LIST) == 0:
        rebuild_proxylist()
    _p = random.choice(tuple(PROXY_LIST))
    return {
        'http': f"http://{_p}",
        'https': f"https://{_p}"
    }


def remove_dead_proxy(url):
    global PROXY_LIST
    _l = url.split("//")
    ip = _l[-1] if len(_l) > 0 else url
    if ip in PROXY_LIST:
        PROXY_LIST.remove(ip)
    rebuild_proxylist()


def get_isbns_set():
    return set(pd.read_excel(ISBN_FILE, header=None)[0])


def add_item(item, old_cost: str, new_cost: str):
    global __RESULTS
    global __counter
    __counter += 1
    if (__counter % 100) == 0:
        print(f"Number Processed: {__counter}")
        write_part()
    __RESULTS.append((item, old_cost, new_cost))


def thread_monitoring():
    global THREAD_LIST
    if DEBUG:
        print("Started Thread Monitor")
    while True:
        try:
            for t in THREAD_LIST:
                if t.is_alive is False:
                    if DEBUG:
                        print("Found Failed Thread.")
                    newthread = threading.Thread(target=worker)
                    newthread.daemon = True
                    THREAD_LIST.remove(t)
                    THREAD_LIST.append(newthread)
                    newthread.start()
            time.sleep(15)
        except Exception as e:
            print("Error Watching Threads", e)


def worker():
    global FAILED_ISBN
    try:
        proxies = get_next_proxy()
        while True:
            isbn, _attempt = q.get()
            try:
                response = requests.get(URL.format(isbn=isbn), proxies=proxies)
                if response.status_code == 429:
                    q.put((isbn, _attempt+1))
                    proxies = get_next_proxy()
                elif response.status_code == 403:
                    remove_dead_proxy(proxies['http'])
                    q.put((isbn, _attempt+1))
                    proxies = get_next_proxy()
                markup = response.text
                bs_data = BeautifulSoup(markup, "html.parser")
                try:
                    _d = bs_data.select(
                        "table.results-table-Logo tr.results-table-first-LogoRow.has-data")
                    if DEBUG:
                        print(f"Size of BS4 Select. {len(_d)}")
                    if len(_d) == 0:
                        if DEBUG:
                            print(
                                f"bs_data: {bs_data.select('table.results-table-Logo')}")
                    _oldcost = _d[0]['data-price'] if len(_d) > 0 else '-1'
                    _newcost = _d[1]['data-price'] if len(_d) > 1 else '-1'
                    if DEBUG:
                        print(
                            f"{response.status_code}, {proxies['http']} | Writing {isbn} => {_oldcost}, {_newcost}")
                    add_item(isbn, _oldcost, _newcost)
                except (AttributeError, IndexError) as e:
                    if DEBUG:
                        print(f"ISBN FAILURE: {isbn}", e)
                    # -1 Represents Unable to find the file.
                    if _attempt < MAX_RETRIES:
                        q.put((isbn, _attempt + 1))
                    else:
                        add_item(isbn, '-1', '-1')
                        FAILED_ISBN.add(isbn)
            except OSError as e:
                if DEBUG:
                    print("Possible Proxy dead. ", proxies['http'])
                remove_dead_proxy(proxies['http'])
                proxies = get_next_proxy()
                q.put((isbn, _attempt))
            except Exception as e:
                if DEBUG:
                    print("Failed to get file. ", e)
                proxies = get_next_proxy()
                if _attempt < MAX_RETRIES:
                    q.put((isbn, _attempt + 1))
                else:
                    add_item(isbn, '-2', '-2')
            q.task_done()

            if SLEEP_TIMER is not None and SLEEP_TIMER > 0:
                time.sleep(SLEEP_TIMER)
    except Exception as threadE:
        print(f"Exception Not Expected: {threadE}")


def main():
    global q
    global ISBN_LIST
    global THREAD_LIST
    q = queue.Queue()
    count = 0
    print("Building ISBN List")
    ISBN_LIST = get_isbns_set()
    try:
        _recovered_df = pd.read_csv(f"DUMP-{OUTPUTFILE}", header=None)
        for _idx in _recovered_df.index:
            try:
                _isbn = str(int(_recovered_df[0][_idx]))
                _oldCost = _recovered_df[1][_idx]
                _newCost = _recovered_df[2][_idx]
            except:
                continue
            add_item(_isbn, _oldCost, _newCost)
            if _isbn in ISBN_LIST:
                ISBN_LIST.remove(_isbn)
        __recovered_out = pd.read_csv(OUTPUTFILE, header=None)
        # OUTFILE is written in chunks, so we want to load the file, and remove duplicates from the pending list.
        for _idx in __recovered_out.index:
            try:
                _isbn = str(int(__recovered_out[0][_idx]))
            except:
                continue
            if _isbn in ISBN_LIST:
                ISBN_LIST.remove(_isbn)

        print("Recovered Position...")
    except Exception as e:
        print("Failed to Recover Position: ", e)
    print("Finished Building ISBN List.")
    for isbn in sorted(ISBN_LIST):
        q.put((isbn, 0))
    if DEBUG:
        print(f"Number of ISBN to Process: {len(ISBN_LIST)}.")

    for i in range(NUM_THREADS):
        x = threading.Thread(target=worker)
        x.daemon = True
        THREAD_LIST.append(x)
        x.start()

    monitor = threading.Thread(target=thread_monitoring)
    monitor.daemon = True
    monitor.start()

    q.join()
    monitor._delete()
    # with open(OUTPUTFILE, "w+") as fp:
    #   fp.writelines([",".join(str(isbn), str(price))+'\n' for isbn, price in sorted(__RESULTS, key=lambda row: row[0])])
    with open("failed_isbn.csv", "w+") as fp:
        fp.writelines([str(x)+'\n' for x in FAILED_ISBN])


def crash_dump():
    print(f"Dumping Data: {__RESULTS}")
    with open(f"DUMP-{OUTPUTFILE}", "w+") as dp:
        dp.writelines([",".join([str(isbn), str(_old), str(_new)]) + '\n' for isbn,
                       _old, _new in sorted(__RESULTS, key=lambda row: row[0])])
    print("Dump Complete.")


def write_part():
    global __RESULTS
    with open(OUTPUTFILE, "a") as fp:
        _tmp = __RESULTS
        fp.writelines([",".join([str(isbn), str(_old), str(_new)]) + '\n' for isbn,
                       _old, _new in sorted(_tmp, key=lambda row: row[0])])
        for i, c in _tmp:
            for row in __RESULTS:
                x, y = row
                if i == x:
                    __RESULTS.remove(row)


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
    parser.add_argument('--max-proxy-latency',
                        help=f"Max Latency for Free Proxies.  Default: '{MAX_PROXY_LATENCY}'", type=int, default=MAX_PROXY_LATENCY)
    parser.add_argument('--debug', help="Turns On Debugger",
                        action="store_true")
    parser.add_argument(
        '-p', '--proxy', help="ABS path to file representing proxy ip addresses", default=None)
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
    if args.max_proxy_latency:
        MAX_PROXY_LATENCY = args.max_proxy_latency
    if args.debug:
        DEBUG = True
    if args.proxy:
        PROXY_FILE = args.proxy

    print("Starting....")
    rebuild_proxylist()
    START = time.time()
    try:
        main()
    except KeyboardInterrupt as e:
        print("\nInteruption!")
        crash_dump()
    END = time.time()
    _overall = END - START
    print(
        f"...Application Completed Running.\nNumber of ISBN in Memory: {len(ISBN_LIST)}\nFailed Items: {len(FAILED_ISBN)}\n Time to Completion: {_overall}")

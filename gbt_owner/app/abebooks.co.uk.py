from bs4 import BeautifulSoup
import pandas as pd
import queue
import threading
import time
import os
import requests
import argparse
import globals
from typing import List
from utils.proxy import rebuild_proxylist,remove_dead_proxy,get_next_proxy
from utils import thread_monitoring, get_isbns_set
from utils.fileutils import write_part, crash_dump

def add_item(item, cost):
  globals.__counter += 1
  if (globals.__counter % 100) == 0:
    print(f"Number Processed: {globals.__counter}")
    write_part()
  globals.__RESULTS.append((item, cost))

def worker():
  try:
    proxies = get_next_proxy()
    while True:
      isbn, _attempt = globals.q.get()
      try:
        response = requests.get(globals.URL.format(isbn=isbn), proxies=proxies)
        if response.status_code == 429:
          globals.q.put((isbn, _attempt+1))
          proxies = get_next_proxy()
        elif response.status_code == 403:
          remove_dead_proxy(proxies['http'])
          globals.q.put((isbn, _attempt+1))
          proxies = get_next_proxy()
        markup = response.text
        if globals.DEBUG:
          f_name = f"./scrapes/{isbn}.html"
          os.makedirs(os.path.dirname(f_name), exist_ok=True)
          with open(f_name, "w") as _fp:
            _fp.write(markup)
        bs_data = BeautifulSoup(markup, "html.parser")
        try:
          # 3 Different ways to do approximately the same thing.
          #
          # _cost = bs_data.find(
          #     "div", attrs={"id": "srp-item-price-1"}).text.split(" ")[1]
          #
          # _book = bs_data.find("div", attrs={"id": "book-1"})
          # _h2 = _book.find("h2")
          #
          # _cost = _h2.find("meta", attrs={"itemprop": "price"})['content']
          _d = bs_data.select("div#book-1 h2 > meta[itemprop='price']")
          if len(_d) == 0:
            raise Exception("Did not find html tag")
          _cost = _d[0]['content']
          if globals.DEBUG:
            print(f"{response.status_code}, {proxies['http']} | Writing {isbn} => {_cost}")
          add_item(isbn, _cost)
        except (AttributeError, IndexError) as e:
          if globals.DEBUG:
            print(f"ISBN FAILURE: {isbn}", e)
          # -1 Represents Unable to find the file.
          if _attempt < globals.MAX_RETRIES:
            globals.q.put((isbn, _attempt + 1))
          else:
            add_item(isbn, '-1')
            globals.FAILED_ISBN.add(isbn)
      except OSError as e:
        if globals.DEBUG:
          print("Possible Proxy dead. ", proxies['http'])
        remove_dead_proxy(proxies['http'])
        proxies = get_next_proxy()
        globals.q.put((isbn, _attempt))
      except Exception as e:
        if globals.DEBUG:
          print("Failed to get file. ", e)
        proxies = get_next_proxy()
        if _attempt < globals.MAX_RETRIES:
          globals.q.put((isbn, _attempt + 1))
        else:
          add_item(isbn, '-2')
      globals.q.task_done()

      if globals.SLEEP_TIMER is not None and globals.SLEEP_TIMER > 0:
          time.sleep(globals.SLEEP_TIMER)
  except Exception as threadE:
    print(f"Exception Not Expected: {threadE}")

def main():
  globals.q = queue.Queue()
  count = 0
  print("Building ISBN List")
  globals.ISBN_LIST = get_isbns_set()
  try:
    _recovered_df = pd.read_csv(f"DUMP-{globals.OUTPUTFILE}", header=None)
    for _idx in _recovered_df.index:
      try:
        _isbn = str(int(_recovered_df[0][_idx]))
        _cost = _recovered_df[1][_idx]
      except:
        continue
      globals.__RESULTS.append((_isbn, float(_cost)))
      if _isbn in globals.ISBN_LIST:
        globals.ISBN_LIST.remove(_isbn)
    __recovered_out = pd.read_csv(globals.OUTPUTFILE, header=None)
    for _idx in __recovered_out.index:
      try:
        _isbn = str(int(__recovered_out[0][_idx]))
        _cost = __recovered_out[1][_idx]
      except:
        continue
      if _isbn in globals.ISBN_LIST:
        globals.ISBN_LIST.remove(_isbn)

    print("Recovered Position...")
  except Exception as e:
    print("Failed to Recover Position: ", e)
  print("Finished Building ISBN List.")
  for isbn in sorted(globals.ISBN_LIST):
    globals.q.put((isbn, 0))
  if globals.DEBUG:
    print(f"Number of ISBN to Process: {len(globals.ISBN_LIST)}.")

  for i in range(globals.NUM_THREADS):
    x = threading.Thread(target=worker)
    x.daemon = True
    globals.THREAD_LIST.append(x)
    x.start()

  monitor = threading.Thread(target=thread_monitoring)
  monitor.daemon = True
  monitor.start()

  globals.q.join()
  monitor._delete()
  # with open(OUTPUTFILE, "w+") as fp:
  #   fp.writelines([",".join(str(isbn), str(price))+'\n' for isbn, price in sorted(__RESULTS, key=lambda row: row[0])])
  with open("failed_isbn.csv", "w+") as fp:
    fp.writelines([str(x)+'\n' for x in globals.FAILED_ISBN])

if __name__ == '__main__':
  globals.initialize()
  globals.URL = "https://www.abebooks.co.uk/servlet/SearchResults?bi=0&bx=off&ds=30&isbn={isbn}&n=200000169&recentlyadded=all&sortby=17&sts=t"
  globals.OUTPUTFILE = "out.csv"
  globals.ISBN_FILE = "./isbn.xlsx"
  globals.ISBN_LIST = []
  globals.THREAD_LIST : List[threading.Thread] = []
  globals.FAILED_ISBN = set([])
  globals.MAX_RETRIES = 0
  globals.NUM_THREADS = 4
  globals.DEBUG = False
  globals.SLEEP_TIMER = 0.5
  globals.MAX_PROXY_LATENCY = 200
  globals.PROXY_FILE = None
  globals.__RESULTS = []
  globals.__counter = 0
  globals.time_between_proxy_rebuilds = None
  globals.PROXY_LIST = set([])

  parser=argparse.ArgumentParser()
  parser.add_argument(
      '-o', '--outfile', help=f'File output.  Default: {globals.OUTPUTFILE}', default=globals.OUTPUTFILE)
  parser.add_argument(
      'input', help=f"ABS path to Input xlsx ISBN file. Default: '{globals.ISBN_FILE}''", default=globals.ISBN_FILE)
  parser.add_argument('--retries', help="Max Retries",
                      type=int, default=globals.MAX_RETRIES)
  parser.add_argument(
      '-t', '--threads', help="Number of Threads", type=int, default=globals.NUM_THREADS)
  parser.add_argument(
      '--sleep', help=f"Sleep Timer.  Default: {globals.SLEEP_TIMER} seconds", type=float, default=globals.SLEEP_TIMER)
  parser.add_argument('--max-proxy-latency',
                      help=f"Max Latency for Free Proxies.  Default: '{globals.MAX_PROXY_LATENCY}'", type=int, default=globals.MAX_PROXY_LATENCY)
  parser.add_argument('--debug', help="Turns On Debugger",
                      action="store_true")
  parser.add_argument('-p', '--proxy', help="ABS path to file representing proxy ip addresses", default=None)
  args=parser.parse_args()
  if args.outfile:
    globals.OUTPUTFILE=args.outfile
  if args.input:
    globals.ISBN_FILE=args.input
  if args.retries:
    globals.MAX_RETRIES=args.retries
  if args.threads:
    globals.NUM_THREADS=args.threads
  if args.sleep:
    globals.SLEEP_TIMER=args.sleep
  if args.max_proxy_latency:
    globals.MAX_PROXY_LATENCY=args.max_proxy_latency
  if args.debug:
    globals.DEBUG=True
  if args.proxy:
    Pglobals.ROXY_FILE = args.proxy

  print("Starting....")
  rebuild_proxylist()
  START=time.time()
  try:
    main()
  except KeyboardInterrupt as e:
    print("\nInteruption!")
    crash_dump()
  END=time.time()
  _overall=END - START
  print(
      f"...Application Completed Running.\nNumber of ISBN in Memory: {len(globals.ISBN_LIST)}\nFailed Items: {len(globals.FAILED_ISBN)}\n Time to Completion: {_overall}")

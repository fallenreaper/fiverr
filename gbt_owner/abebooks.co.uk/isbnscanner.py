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

URL = "https://www.abebooks.co.uk/servlet/SearchResults?bi=0&bx=off&ds=30&isbn={isbn}&n=200000169&recentlyadded=all&sortby=17&sts=t"
OUTPUTFILE = "out.csv"
ISBN_FILE = "./isbn.xlsx"
ISBN_LIST = []
THREAD_LIST : List[threading.Thread] = []
FAILED_ISBN = set([])
MAX_RETRIES = 0
NUM_THREADS = 4
DEBUG = False
SLEEP_TIMER = 0.5
MAX_PROXY_LATENCY = 200
PROXY_FILE = None
__RESULTS = []
__counter = 0

# PROXY LIST FROM PROXYSTORM
# PROXY_LIST = [
# '173.208.208.42:19018',
# '142.54.179.98:19016',
# '204.12.211.114:19011',
# '69.30.217.114:19006',
# '208.110.86.178:19012'
# ]

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
    os.system(
        f"curl 'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout={MAX_PROXY_LATENCY}&country=all&ssl=all&anonymity=all&simplified=true' > http_proxies.txt")
    with open("http_proxies.txt") as fp:
      PROXY_LIST = set([x.strip() for x in fp.readlines()])
    print("Proxy List Rebuilt.")
    if DEBUG:
      print(PROXY_LIST)


def get_next_proxy():
  _p = random.sample(PROXY_LIST, 1)[0]
  return { 
    'http': _p,
    'https': _p
    }


def remove_dead_proxy(ip):
  global PROXY_LIST
  if ip in PROXY_LIST:
    PROXY_LIST.remove(ip)
  rebuild_proxylist()

def get_isbns_set():
  return set(pd.read_excel(ISBN_FILE, header=None)[0])

def add_item(item, cost):
  global __RESULTS
  global __counter
  __counter += 1
  if (__counter % 100) == 0:
    print(f"Number Processed: {__counter}")
    write_part()
  __RESULTS.append((item, cost))

def thread_monitoring():
  global THREAD_LIST
  try:
    while True:
      for t in THREAD_LIST:
        if t.is_alive is False:
          newthread = threading.Thread(target=worker)
          newthread.daemon = True
          THREAD_LIST.remove(t)
          THREAD_LIST.append(newthread)
          newthread.start()
      time.sleep(2)
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
        if DEBUG:
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
          _cost = bs_data.select("div#book-1 h2 > meta[itemprop='price']")[0]['content']
          if DEBUG:
            print(f"{response.status_code}, {proxies['http']} | Writing {isbn} => {_cost}")
          add_item(isbn, _cost)
        except (AttributeError, IndexError) as e:
          if DEBUG:
            print(f"ISBN FAILURE: {isbn}", e)
          # -1 Represents Unable to find the file.
          if _attempt < MAX_RETRIES:
            q.put((isbn, _attempt + 1))
          else:
            add_item(isbn, '-1')
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
          add_item(isbn, '-2')
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
    print(_recovered_df)
    for _idx in _recovered_df.index:
      try:
        _isbn = str(int(_recovered_df[0][_idx]))
        _cost = _recovered_df[1][_idx]
      except:
        continue
      __RESULTS.append((_isbn, float(_cost)))
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
  # with open(OUTPUTFILE, "w+") as fp:
  #   fp.writelines([",".join(str(isbn), str(price))+'\n' for isbn, price in sorted(__RESULTS, key=lambda row: row[0])])
  with open("failed_isbn.csv", "w+") as fp:
    fp.writelines([str(x)+'\n' for x in FAILED_ISBN])

def crash_dump():
  print(f"Dumping Data: {__RESULTS}")
  with open(f"DUMP-{OUTPUTFILE}", "w+") as dp:
    dp.writelines([",".join([str(isbn), str(cost)]) + '\n' for isbn, cost in sorted(__RESULTS, key=lambda row: row[0])])
  print("Dump Complete.")

def write_part():
  global __RESULTS
  with open(OUTPUTFILE, "a") as fp:
    _tmp = __RESULTS
    fp.writelines([",".join([str(isbn), str(cost)]) + '\n' for isbn, cost in sorted(_tmp, key=lambda row: row[0])])
    for i,c in _tmp:
      for row in __RESULTS:
        x,y = row
        if i == x:
          __RESULTS.remove(row)


if __name__ == '__main__':
  parser=argparse.ArgumentParser()
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
  parser.add_argument('-p', '--proxy', help="ABS path to file representing proxy ip addresses", default=None)
  args=parser.parse_args()
  if args.outfile:
    OUTPUTFILE=args.outfile
  if args.input:
    ISBN_FILE=args.input
  if args.retries:
    MAX_RETRIES=args.retries
  if args.threads:
    NUM_THREADS=args.threads
  if args.sleep:
    SLEEP_TIMER=args.sleep
  if args.max_proxy_latency:
    MAX_PROXY_LATENCY=args.max_proxy_latency
  if args.debug:
    DEBUG=True
  if args.proxy:
    PROXY_FILE = args.proxy

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
      f"...Application Completed Running.\nNumber of ISBN in Memory: {len(ISBN_LIST)}\nFailed Items: {len(FAILED_ISBN)}\n Time to Completion: {_overall}")

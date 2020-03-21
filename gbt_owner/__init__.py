
import requests
import pandas as pd
from bs4 import BeautifulSoup
import threading
import queue
import time

DEBUG = False
ISBN_FILE = "./isbn.xlsx"
BOOKKEEPER = "https://www.bookfinder.com/search/?isbn={isbn}&new_used=*&st=sr&ac=qr"
# BOOKKEEPER = "https://www.bookfinder.com/search/?lang=en&isbn={isbn}&new_used=*&destination=us&currency=USD&mode=basic&st=sr&ac=qr"
OUTPUT_CSV = "./out.csv"
NUM_THREADS = 50

COUNT = 0
START = None
END = None

def process_isbn(isbn: str):
    try:
        html = requests.get(BOOKKEEPER.format(isbn=isbn)).text
        data = BeautifulSoup(html, "html.parser")
    except:
        # -2 CONNECTION ERROR
        if DEBUG: print(f"Connection Error for {isbn}")
        new_book_price = old_book_price = -2
    try:
        rows = data.find_all("div",attrs={"id": "buyback_and_rentals"})[0].findNextSibling().findNextSibling().findNextSibling().findNextSibling().contents[3].find_all("tr")
        new_book_price = None
        for row in rows:
            try:
                value = float(row.find_all("a")[-1].contents[0])
            except:
                try:
                    value = float(row.find_all("a")[-1].contents[0][1:])
                except:
                    continue
            if new_book_price is None:
                new_book_price = value
            else:
                new_book_price = min(new_book_price, value)
    except:
        new_book_price = -1

    try:
        rows = data.find_all("div",attrs={"id": "buyback_and_rentals"})[0].findNextSibling().findNextSibling().findNextSibling().findNextSibling().contents[-1].find_all("tr")
        old_book_price = None
        for row in rows:
            try:
                value = float(row.find_all("a")[-1].contents[0])
            except:
                try:
                    value = float(row.find_all("a")[-1].contents[0][1:])
                except:
                    continue
            if old_book_price is None:
                old_book_price = value
            else:
                old_book_price = min(old_book_price, value)
    except:
        old_book_price = -1
    return (isbn, str(new_book_price), str(old_book_price))

def process(isbn, fp):
    global COUNT
    COUNT = (COUNT + 1) % 10000
    t = process_isbn(isbn)
    print(t)
    if COUNT == 0 and DEBUG:
        print("10K Passed.")
    fp.write(",".join(t) + "\n")

def worker():
    while True:
        isbn, fp = q.get()
        if DEBUG: print(f"ISBN: {isbn}")
        process(isbn, fp)
        q.task_done()

def main():
    global q
    if DEBUG: print("In Main")
    isbn_items = pd.read_excel(ISBN_FILE)["ISBN"]
    try:
        fp = open(OUTPUT_CSV, "w")
    except:
        print("Failed to Open file to write")
        return
    if DEBUG: print("About to start looping")
    q = queue.Queue()
    for i in range(NUM_THREADS):
        if DEBUG: print(f"Starting Thread {i}")
        x = threading.Thread(target=worker)
        x.daemon = True
        x.start()

    for isbn in isbn_items:
        q.put((isbn, fp))
    q.join()
    fp.close()
    print("DONE!")

if __name__ == "__main__":
    START = time.time()
    main()
    END = time.time()
    overall = END - START
    print(f"Seconds Elapsed: {overall}")
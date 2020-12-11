import globals
import pandas as pd
import time
def thread_monitoring():
    if globals.DEBUG:
        print("Started Thread Monitor")
    while True:
        try:
            for t in globals.THREAD_LIST:
                if t.is_alive is False:
                    if globals.DEBUG:
                        print("Found Failed Thread.")
                    newthread = threading.Thread(target=worker)
                    newthread.daemon = True
                    globals.THREAD_LIST.remove(t)
                    globals.THREAD_LIST.append(newthread)
                    newthread.start()
            time.sleep(15)
        except Exception as e:
            print("Error Watching Threads", e)

def get_isbns_set():
    return set(pd.read_excel(globals.ISBN_FILE, header=None)[0])
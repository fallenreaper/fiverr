
def initialize():
    global URL
    global OUTPUTFILE
    global ISBN_FILE
    global ISBN_LIST
    global THREAD_LIST
    global FAILED_ISBN
    global MAX_RETRIES
    global NUM_THREADS
    global DEBUG
    global SLEEP_TIMER
    global MAX_PROXY_LATENCY
    global PROXY_FILE
    global __RESULTS
    global __counter
    global time_between_proxy_rebuilds
    global PROXY_LIST
    URL = ''
    OUTPUTFILE = "out.csv"
    ISBN_FILE = "./isbn.xlsx"
    ISBN_LIST = []
    THREAD_LIST= []  # Type List[threading.Thread]
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

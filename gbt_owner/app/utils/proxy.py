import globals
import time
import requests
import random

def rebuild_proxylist():
    if globals.time_between_proxy_rebuilds is None:
        globals.time_between_proxy_rebuilds = time.time()
    else:
        _under_3_minutes = 3*60
        if (globals.PROXY_FILE is not None or len(globals.PROXY_LIST) < 4) and (time.time() - globals.time_between_proxy_rebuilds) < _under_3_minutes:
            print("[WARNING] Rebuilding Proxy List too Frequently.  Cause:  Too Many Dead or Offline Proxies. This can drastically slow down Data processing.")

    if globals.PROXY_FILE is not None:
        with open(globals.PROXY_FILE) as fp:
            globals.PROXY_LIST = set([x.strip() for x in fp.readlines()])
        print("Proxy List Rebuilt.")
        if globals.DEBUG:
            print(globals.PROXY_LIST)
    elif len(globals.PROXY_LIST) < 4:
        _url = f"https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout={globals.MAX_PROXY_LATENCY}&country=all&ssl=all&anonymity=all&simplified=true"
        proxydata = requests.get(_url).text.split("\n")
        globals.PROXY_LIST = set([x.strip() for x in proxydata if x.strip() != ''])
        print("Proxy List Rebuilt.")
        if globals.DEBUG:
            print(globals.PROXY_LIST)


def get_next_proxy():
    if len(globals.PROXY_LIST) == 0:
        rebuild_proxylist()
    _p = random.choice(tuple(globals.PROXY_LIST))
    return {
        'http': f"http://{_p}",
        'https': f"https://{_p}"
    }


def remove_dead_proxy(url):
    _l = url.split("//")
    ip = _l[-1] if len(_l) > 0 else url
    if ip in globals.PROXY_LIST:
        globals.PROXY_LIST.remove(ip)
    rebuild_proxylist()
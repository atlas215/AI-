#!/usr/bin/env python3

import time
import urllib.request
import urllib.error

TARGET_URL = 'http://127.0.0.1:8000/health'
INTERVAL_SECONDS = 300


def ping_target():
    request = urllib.request.Request(TARGET_URL, headers={'User-Agent': 'ATLAS-Heartbeat/1.0'})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            status = response.getcode()
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Heartbeat OK: {status}")
    except urllib.error.HTTPError as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Heartbeat HTTP error: {e.code}")
    except urllib.error.URLError as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Heartbeat failed: {e}")
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Heartbeat exception: {e}")


if __name__ == '__main__':
    print('Starting ATLAS heartbeat keep-alive loop...')
    while True:
        ping_target()
        time.sleep(INTERVAL_SECONDS)

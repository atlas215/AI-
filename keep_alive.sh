#!/usr/bin/env bash

set -e

TARGET_URL="http://127.0.0.1:8000/health"
INTERVAL_SECONDS=300

while true; do
  if command -v curl >/dev/null 2>&1; then
    if curl --fail -sS "$TARGET_URL" >/dev/null; then
      echo "$(date -u +'%Y-%m-%d %H:%M:%S') - Keep-alive heartbeat success"
    else
      echo "$(date -u +'%Y-%m-%d %H:%M:%S') - Keep-alive heartbeat failed"
    fi
  else
    python - <<'PY'
import urllib.request, urllib.error, time
url = 'http://127.0.0.1:8000/health'
try:
    with urllib.request.urlopen(url, timeout=15) as response:
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Keep-alive heartbeat success: {response.getcode()}")
except Exception as e:
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Keep-alive heartbeat failed: {e}")
PY
  fi
  sleep "$INTERVAL_SECONDS"
done

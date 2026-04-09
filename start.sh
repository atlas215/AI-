#!/usr/bin/env bash
set -e

# Ensure the app runs on the bound port in cloud environments.
PORT=${PORT:-8000}

cd "$(dirname "$0")"
exec uvicorn COMM_LINK:app --host 0.0.0.0 --port "$PORT" --workers 1 --reload false

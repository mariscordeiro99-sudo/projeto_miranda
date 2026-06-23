#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

export PYTHONUNBUFFERED=1
PORT="${PORT:-8000}"
WORKERS="${WEB_CONCURRENCY:-1}"
TIMEOUT="${GUNICORN_TIMEOUT:-120}"

echo "=== Starting Django web server ==="
echo "Port: ${PORT}"
echo "Workers: ${WORKERS}"
echo "Timeout: ${TIMEOUT}s"

exec gunicorn core.wsgi:application \
  --bind "0.0.0.0:${PORT}" \
  --workers "${WORKERS}" \
  --timeout "${TIMEOUT}" \
  --access-logfile - \
  --error-logfile - \
  --capture-output

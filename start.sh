#!/usr/bin/env sh
set -eu

APP_MODE="${APP_MODE:-bot}"

case "$APP_MODE" in
  bot)
    exec python -m app.main
    ;;
  api)
    exec uvicorn app.api.app:app --host "${API_HOST:-0.0.0.0}" --port "${PORT:-${API_PORT:-8000}}"
    ;;
  *)
    echo "Noto'g'ri APP_MODE: $APP_MODE. 'bot' yoki 'api' qiymatini tanlang." >&2
    exit 1
    ;;
esac

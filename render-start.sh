#!/usr/bin/env bash
set -o errexit

echo "=== Finz: Starting Application Services ==="

# 1. Start FastAPI backend in background on port 8000
echo "Starting FastAPI backend on 127.0.0.1:8000..."
(cd backend && uvicorn main:app --host 127.0.0.1 --port 8000) &

# Brief pause to ensure FastAPI server initializes
sleep 2

# 2. Start Django frontend with Gunicorn on the Render-assigned PORT (fallback 8080)
RENDER_PORT="${PORT:-8080}"
echo "Starting Django frontend on port $RENDER_PORT..."
cd frontend
exec gunicorn config.wsgi:application --bind "0.0.0.0:$RENDER_PORT" --workers 2 --timeout 120

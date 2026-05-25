#!/bin/bash
set -e

echo "Waiting for MySQL to be ready..."
until python check_db.py; do
  echo "MySQL not ready yet, retrying in 2s..."
  sleep 2
done

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

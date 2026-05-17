#!/bin/bash
set -e

echo "Waiting for MySQL to be ready..."
until python -c "
import pymysql, os, sys
try:
    pymysql.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        user=os.getenv('MYSQL_USER', 'appuser'),
        password=os.getenv('MYSQL_PASSWORD', 'apppassword'),
        database=os.getenv('MYSQL_DB', 'appdb'),
    )
    sys.exit(0)
except Exception:
    sys.exit(1)
"; do
  echo "MySQL not ready yet, retrying in 2s..."
  sleep 2
done

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

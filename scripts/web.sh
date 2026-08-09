#!/bin/sh
until python check_db.py; do echo "Waiting for MySQL..."; sleep 2; done

# Migrate here rather than on app startup: uvicorn --reload restarts the app
# process on every code change, and migrations should run once per container.
alembic upgrade head

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

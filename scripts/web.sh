#!/bin/sh
until python check_db.py; do echo "Waiting for MySQL..."; sleep 2; done
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

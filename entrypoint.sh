#!/bin/bash
set -e

echo "Waiting for MySQL to be ready..."
until python -c "
import asyncio, sys, os
from sqlalchemy.ext.asyncio import create_async_engine

async def check():
    url = (
        f\"mysql+aiomysql://{os.getenv('MYSQL_USER','appuser')}:{os.getenv('MYSQL_PASSWORD','apppassword')}\"
        f\"@{os.getenv('MYSQL_HOST','localhost')}:{os.getenv('MYSQL_PORT','3306')}/{os.getenv('MYSQL_DB','appdb')}\"
    )
    engine = create_async_engine(url)
    try:
        async with engine.connect():
            pass
        await engine.dispose()
        sys.exit(0)
    except Exception:
        await engine.dispose()
        sys.exit(1)

asyncio.run(check())
"; do
  echo "MySQL not ready yet, retrying in 2s..."
  sleep 2
done

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

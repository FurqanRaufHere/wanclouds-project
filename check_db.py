import asyncio, sys
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import DATABASE_URL


async def check():
    url = DATABASE_URL.replace("mysql+pymysql", "mysql+aiomysql")
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

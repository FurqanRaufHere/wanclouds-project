from contextlib import contextmanager
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.core.config import DATABASE_URL

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Declare a route's session as `db: DbSession` instead of repeating
# `Depends(get_db_session)` in every signature.
DbSession = Annotated[Session, Depends(get_db_session)]


@contextmanager
def get_db():
    """Session for code outside the request cycle (Celery tasks), where
    FastAPI's dependency injection isn't available."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

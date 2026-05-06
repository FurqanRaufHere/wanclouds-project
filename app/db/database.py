# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, 
#     connect_args={"check_same_thread": False}
# )

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


#  Database connection (now MySQL)
#  We now import DATABASE_URL from config.py instead of
#  defining it here. The URL now points to MySQL instead
#  of a local SQLite file.
#
#  ALSO REMOVED:
#  connect_args={"check_same_thread": False}
#  That was SQLite-specific. MySQL doesn't need it.
#
#  Everything else (SessionLocal, Base, get_db) stays
#  exactly the same — SQLAlchemy abstracts the difference.

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL

# Create engine using the MySQL URL from config
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
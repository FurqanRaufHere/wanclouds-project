#  alembic/env.py — Alembic environment configuration
#  This file is the bridge between Alembic and your app.
#  It tells Alembic:
#  1. Which database to connect to (our DATABASE_URL)
#  2. Which models to look at (our Base metadata)

#  HOW AUTOGENERATE WORKS:
#  When you run "alembic revision --autogenerate", Alembic:
#  1. Connects to the database, reads current table structure
#  2. Reads your SQLAlchemy models (via target_metadata)
#  3. COMPARES the two
#  4. Generates a migration file with the differences

#  So if you add a column to User model and run autogenerate,
#  Alembic will detect it and write:
#    op.add_column('users', sa.Column('phone', sa.String()))
#  automatically!
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os

# Add the project root to Python path so we can import
# from "app.*" modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.db.database import Base
from app.models.user import User  # noqa: F401 — must import to register
from app.core.config import DATABASE_URL

config = context.config

# Set up logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override the sqlalchemy.url from alembic.ini with our
# dynamic DATABASE_URL from config.py (reads env vars)
config.set_main_option("sqlalchemy.url", DATABASE_URL)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
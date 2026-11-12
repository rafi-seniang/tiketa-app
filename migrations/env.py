"""Runs the migrations on the service's own async engine."""

import asyncio

from alembic import context
from sqlalchemy import Connection

import app.models  # noqa: F401  registers every table on Base.metadata
from app.core.database import Base, connect_database
from app.settings import get_settings

target_metadata = Base.metadata


def database_url() -> str:
    return context.config.get_main_option("sqlalchemy.url") or get_settings().database_url.get_secret_value()


def run_on(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,  # SQLite changes a column by copying the table
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_online() -> None:
    engine, _ = connect_database(database_url())
    async with engine.connect() as connection:
        await connection.run_sync(run_on)
    await engine.dispose()


asyncio.run(run_online(), loop_factory=asyncio.SelectorEventLoop)  # psycopg's async mode needs a selector loop

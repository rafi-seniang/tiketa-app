import asyncio
import os
import sys
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import httpx
import pytest
from fastmcp import Client, FastMCP
from pydantic import SecretStr

from app.core.application import create_app
from app.core.database import Base, Sessions, connect_database
from app.core.dependencies import get_now, get_resources
from app.core.lifespan import Resources, build_resources
from app.core.signing import Signer
from app.mcp.server import build_mcp_server
from app.middleware.rate_limit import InMemoryRateLimiter, key_id
from app.repositories.cinema import CinemaStore
from app.schemas.cinema import Showtime
from app.services.weekly_schedule import publish_week
from app.settings import Settings

CINEMA_TIMEZONE = ZoneInfo("Asia/Jakarta")
NOW = datetime(2026, 11, 8, 3, 0, tzinfo=UTC)  # Sunday 10:00 in Jakarta, the last day of the week of 2 November
TODAY = NOW.astimezone(CINEMA_TIMEZONE).date()
OWNER = key_id("test-key-0001")  # the caller the test client's API key stands for
DUNE = 9  # the film id of Dune: Part Two, shown at 12:30, 15:15, 18:00 and 20:45


def pytest_asyncio_loop_factories(config: pytest.Config, item: pytest.Item) -> dict[str, Any]:
    """psycopg's async mode needs a selector loop, which is not the default on Windows."""
    return {"selector": asyncio.SelectorEventLoop} if sys.platform == "win32" else {"default": asyncio.new_event_loop}


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    """A test module can override this fixture to change a setting.

    SQLite in a temporary file by default. TEST_DATABASE_URL runs the same tests on that database instead, an empty
    PostgreSQL one in CI, because the rule that a seat is sold once is kept by the database.
    """
    return Settings(  # type: ignore[call-arg]
        _env_file=None,
        environment="test",
        api_keys="test-key-0001,other-key-0002",
        database_url=os.environ.get("TEST_DATABASE_URL")
        or f"sqlite+aiosqlite:///{(tmp_path / 'tiketa.db').as_posix()}",
    )


@pytest.fixture
async def sessions(settings: Settings) -> AsyncIterator[Sessions]:
    engine, session_factory = connect_database(settings.database_url.get_secret_value())
    async with engine.begin() as connection:  # migrations are tested on their own in test_migrations.py
        await connection.run_sync(Base.metadata.create_all)
    await publish_week(session_factory, TODAY, CINEMA_TIMEZONE)
    yield session_factory
    async with engine.begin() as connection:  # a shared test database starts empty for the next test
        await connection.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def resources(sessions: Sessions, settings: Settings) -> Resources:
    return build_resources(sessions, InMemoryRateLimiter(), Signer("test-secret"), settings)


@pytest.fixture
def store(resources: Resources) -> CinemaStore:
    return resources.store


@pytest.fixture
async def dune_today(store: CinemaStore) -> list[Showtime]:
    return await store.showtimes_on(TODAY, NOW, DUNE)


@pytest.fixture
async def client(settings: Settings, resources: Resources) -> AsyncIterator[httpx.AsyncClient]:
    app = create_app(settings)
    app.dependency_overrides[get_resources] = lambda: resources
    app.dependency_overrides[get_now] = lambda: NOW
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://test", headers={"X-API-Key": "test-key-0001"}
    ) as http:
        yield http


def keyless(settings: Settings) -> Settings:
    """The settings of a local run without API keys, where every MCP call is the local caller."""
    return settings.model_copy(update={"api_keys": SecretStr("")})


@pytest.fixture
def mcp_server(resources: Resources, settings: Settings) -> FastMCP:
    return build_mcp_server(lambda: resources, lambda: NOW, keyless(settings))


@pytest.fixture
async def mcp(mcp_server: FastMCP) -> AsyncIterator[Client]:
    async with Client(mcp_server) as mcp_client:
        yield mcp_client

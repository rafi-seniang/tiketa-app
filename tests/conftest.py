from collections.abc import AsyncIterator
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx
import pytest

from app.core.application import create_app
from app.core.database import Base, Sessions, connect_database
from app.core.dependencies import get_now, get_resources
from app.core.lifespan import Resources, build_resources
from app.core.signing import Signer
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


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    """A test module can override this fixture to change a setting."""
    return Settings(  # type: ignore[call-arg]
        _env_file=None,
        environment="test",
        api_keys="test-key-0001,other-key-0002",
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'tiketa.db').as_posix()}",
    )


@pytest.fixture
async def sessions(settings: Settings) -> AsyncIterator[Sessions]:
    engine, session_factory = connect_database(settings.database_url.get_secret_value())
    async with engine.begin() as connection:  # migrations are tested on their own in test_migrations.py
        await connection.run_sync(Base.metadata.create_all)
    await publish_week(session_factory, TODAY, CINEMA_TIMEZONE)
    yield session_factory
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

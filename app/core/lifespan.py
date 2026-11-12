"""Everything long-lived, built once at startup and closed on shutdown: database, Redis, the controllers."""

import secrets
from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, AsyncExitStack, asynccontextmanager
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from fastapi import FastAPI

from app.controllers.bookings import BookingController
from app.controllers.catalog import CatalogController
from app.core.database import Sessions, connect_database
from app.core.migrations import check_schema
from app.core.redis import connect_redis
from app.core.signing import Signer
from app.middleware.rate_limit import InMemoryRateLimiter, RateLimiter, RedisRateLimiter
from app.repositories.cinema import CinemaStore
from app.services.booking_quotes import BookingQuotes
from app.settings import Settings


@dataclass
class Resources:
    store: CinemaStore
    catalog: CatalogController
    bookings: BookingController
    rate_limiter: RateLimiter


def build_signer(settings: Settings) -> Signer:
    """Without SESSION_SECRET (local only, refused in production) signed values end when the process does."""
    return Signer(settings.session_secret.get_secret_value() or secrets.token_urlsafe(32))


def build_resources(sessions: Sessions, rate_limiter: RateLimiter, signer: Signer, settings: Settings) -> Resources:
    cinema_timezone = ZoneInfo(settings.cinema_timezone)
    store = CinemaStore(sessions, cinema_timezone)
    quotes = BookingQuotes(signer, settings.booking_confirmation_minutes, cinema_timezone)
    return Resources(
        store=store,
        catalog=CatalogController(store, settings.cinema_name, cinema_timezone, settings.max_seats_per_booking),
        bookings=BookingController(store, quotes, settings.max_seats_per_booking),
        rate_limiter=rate_limiter,
    )


@asynccontextmanager
async def open_resources(settings: Settings, signer: Signer) -> AsyncIterator[Resources]:
    async with AsyncExitStack() as stack:  # closes in reverse order, also when startup fails half way
        engine, sessions = connect_database(settings.database_url.get_secret_value())
        stack.push_async_callback(engine.dispose)
        await check_schema(engine)  # migrations run before the service, not inside it
        redis = await connect_redis(settings)
        if redis is not None:
            stack.push_async_callback(redis.aclose)
        rate_limiter: RateLimiter = RedisRateLimiter(redis) if redis is not None else InMemoryRateLimiter()
        resources = build_resources(sessions, rate_limiter, signer, settings)
        if not await resources.store.list_movies():
            raise RuntimeError("The cinema has no films yet: run `python scripts/publish_week.py` first")
        yield resources


def lifespan(settings: Settings, signer: Signer) -> Callable[[FastAPI], AbstractAsyncContextManager[None]]:
    @asynccontextmanager
    async def run(app: FastAPI) -> AsyncIterator[None]:
        async with open_resources(settings, signer) as resources:  # everything loads here, before any request
            app.state.resources = resources
            yield

    return run

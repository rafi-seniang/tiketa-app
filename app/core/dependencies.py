"""Dependency providers for the routes. Everything they hand out was built once at startup.
Tests swap any of them with app.dependency_overrides."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, Request

from app.controllers.bookings import BookingController
from app.controllers.catalog import CatalogController
from app.core.errors import RateLimited
from app.core.lifespan import Resources
from app.middleware.rate_limit import caller_of
from app.settings import Settings


def get_resources(request: Request) -> Resources:
    resources: Resources = request.app.state.resources
    return resources


def get_settings(request: Request) -> Settings:
    """The settings this app instance was built with (not a global), so tests and workers can differ."""
    settings: Settings = request.app.state.settings
    return settings


def get_now() -> datetime:
    """The clock, as a dependency, so tests can fix the time a booking is made."""
    return datetime.now(UTC)


async def enforce_rate_limit(
    request: Request,
    resources: Annotated[Resources, Depends(get_resources)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    retry_after = await resources.rate_limiter.hit(caller_of(request), settings.rate_limit_per_minute)
    if retry_after is not None:
        raise RateLimited(f"Over {settings.rate_limit_per_minute} requests a minute.", retry_after)


def get_catalog_controller(resources: Annotated[Resources, Depends(get_resources)]) -> CatalogController:
    return resources.catalog


def get_booking_controller(resources: Annotated[Resources, Depends(get_resources)]) -> BookingController:
    return resources.bookings

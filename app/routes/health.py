"""Liveness touches nothing. /meta says what this service is."""

from fastapi import APIRouter

from app import VERSION
from app.schemas.health import ServiceMeta

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/meta")
async def meta() -> ServiceMeta:
    return ServiceMeta(
        id="tiketa",
        name="Tiketa",
        summary="Cinema booking: films, a week of showtimes, seats and bookings, for the web app and a chat agent.",
        version=VERSION,
        docs_path="/docs",
    )

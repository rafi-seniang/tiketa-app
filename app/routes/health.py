"""Liveness touches nothing. /meta says what this service is and whether its MCP server is on."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app import VERSION
from app.core.dependencies import get_settings
from app.schemas.health import ServiceMeta
from app.settings import Settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/meta")
async def meta(settings: Annotated[Settings, Depends(get_settings)]) -> ServiceMeta:
    return ServiceMeta(
        id="tiketa",
        name="Tiketa",
        summary="Cinema booking: films, a week of showtimes, seats and bookings, for the web, a chat agent and MCP.",
        version=VERSION,
        docs_path="/docs",
        mcp_path="/mcp" if settings.mcp_enabled else None,
    )

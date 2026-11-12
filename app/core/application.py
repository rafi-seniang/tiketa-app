"""The app factory: settings, logging, middleware, error handlers, the routes, then the MCP server at /mcp."""

from typing import Any

from fastapi import APIRouter, Depends, FastAPI
from fastmcp.utilities.lifespan import combine_lifespans

from app import VERSION
from app.core.dependencies import enforce_rate_limit, get_now
from app.core.errors import register_error_handlers
from app.core.lifespan import build_signer, lifespan
from app.core.logging import configure_logging
from app.mcp.server import build_mcp_server
from app.middleware.auth import GuestSessions, authenticate
from app.middleware.cors import add_cors
from app.middleware.request_log import register_middleware
from app.middleware.security_headers import add_security_headers
from app.routes import auth, bookings, catalog, health
from app.settings import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level)
    signer = build_signer(settings)
    # Any: FastAPI and Starlette name different app types for the same kind of lifespan
    lifespans: list[Any] = [lifespan(settings, signer)]
    mcp_app = None
    if settings.mcp_enabled:
        mcp_server = build_mcp_server(lambda: app.state.resources, get_now, settings)
        # Plain JSON answers and no sessions: any worker can take any call, as the 2026-07-28 protocol expects
        mcp_app = mcp_server.http_app(path="/", json_response=True, stateless_http=True)
        lifespans.append(mcp_app.lifespan)
    app = FastAPI(
        title="Tiketa",
        version=VERSION,
        lifespan=combine_lifespans(*lifespans),
        docs_url=None if settings.environment == "production" else "/docs",
    )
    app.state.settings = settings
    app.state.guest_sessions = GuestSessions(signer, settings.guest_session_days)
    register_middleware(app)
    add_security_headers(app, https_only=settings.environment == "production")
    register_error_handlers(app)
    add_cors(app, settings.cors_origins)

    # Who is calling first, then the rate limit, so an unknown caller never spends a known caller's budget
    api = APIRouter(prefix="/v1", dependencies=[Depends(authenticate), Depends(enforce_rate_limit)])
    api.include_router(catalog.router)
    api.include_router(bookings.router)
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(api)
    if mcp_app is not None:
        app.mount("/mcp", mcp_app)
    return app

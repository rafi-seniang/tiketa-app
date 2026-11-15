"""The booking tools for MCP clients (Claude, Cursor and other assistants), served at /mcp.

The tools call the same controllers as the HTTP API, so every booking rule holds here too. The client's own model
is the agent: no model runs on this side. Booking takes two calls, so a person can read the price first:
prepare_booking returns the summary and a confirmation id, confirm_booking books it.
"""

from collections.abc import Awaitable, Callable
from datetime import date, datetime
from functools import wraps
from typing import Annotated, Any
from zoneinfo import ZoneInfo

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from fastmcp.exceptions import ToolError
from fastmcp.server.auth.providers.jwt import StaticTokenVerifier
from fastmcp.server.dependencies import get_access_token
from fastmcp.tools import ToolResult
from fastmcp.utilities.types import Image
from pydantic import Field

from app.core.errors import AppError
from app.core.lifespan import Resources
from app.middleware.rate_limit import key_id
from app.schemas.cinema import Booking, BookingForm, Cinema, CustomerName, Movie, SeatIds, Showtime
from app.settings import Settings
from app.utils.seat_image import render_seat_map_png
from app.utils.seat_layout import SEAT_MAP_LEGEND, seat_map_text

INSTRUCTIONS = """Tiketa books cinema seats. Call get_cinema first: it gives the cinema's current date and time \
and the week on sale (Monday to Sunday), so dates such as "tomorrow" or "besok" can be worked out in cinema time.
To book: find_showtimes, get_seat_map, then prepare_booking. Show the person the summary and its total, and call \
confirm_booking only after they agree. Ids are for tools: name the film, day, time and studio to the person.
Prices are per seat in rupiah. Payment is made at the cinema's counter with the booking code. Give the person \
that code: get_booking finds the booking again only by it."""

ANONYMOUS_CALLER = "mcp:anonymous"  # every caller without a key: a public server, or a local run with no keys
READ_ONLY = {"readOnlyHint": True, "openWorldHint": False}
BOOKS_ONCE = {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}


def token_verifier(api_keys: list[str]) -> StaticTokenVerifier | None:
    """MCP clients send an API key as a bearer token. The caller is named by a hash of it, as on the HTTP API."""
    if not api_keys:
        return None
    return StaticTokenVerifier({key: {"client_id": key_id(key), "scopes": []} for key in api_keys})


def refusals_as_tool_errors[**Arguments, Result](
    tool: Callable[Arguments, Awaitable[Result]],
) -> Callable[Arguments, Awaitable[Result]]:
    """A refused request (a taken seat, an expired confirmation) reaches the model as its reason, not as a failure."""

    @wraps(tool)
    async def run(*args: Arguments.args, **kwargs: Arguments.kwargs) -> Result:
        try:
            return await tool(*args, **kwargs)
        except AppError as refusal:
            raise ToolError(refusal.detail) from None

    return run


def build_mcp_server(
    get_resources: Callable[[], Resources], get_now: Callable[[], datetime], settings: Settings
) -> FastMCP:
    # A public server asks for no key. Otherwise the API's keys are the bearer tokens
    verifier = None if settings.mcp_public else token_verifier(settings.api_key_list)
    cinema_timezone = ZoneInfo(settings.cinema_timezone)

    def clock_time(moment: datetime) -> str:
        local = moment.astimezone(cinema_timezone)
        return f"{local:%H:%M} {local.tzname()}"

    mcp = FastMCP(
        "Tiketa",
        instructions=INSTRUCTIONS,
        auth=verifier,
        mask_error_details=True,  # an unexpected error is logged here and not described to the client
    )

    def tool(annotations: dict[str, Any]) -> Callable[[Callable[..., Awaitable[Any]]], Any]:
        return lambda function: mcp.tool(annotations=annotations)(refusals_as_tool_errors(function))

    async def caller() -> str:
        """Who is calling, counted against the same per-minute limit as the HTTP API."""
        token = get_access_token()
        name = token.client_id if token is not None else ANONYMOUS_CALLER
        # Anonymous callers share one name, so they share one larger limit
        limit = settings.rate_limit_per_minute if token is not None else settings.mcp_public_rate_limit_per_minute
        retry_after = await get_resources().rate_limiter.hit(name, limit)
        if retry_after is not None:
            raise ToolError(f"Over {limit} calls a minute. Try again in {retry_after} seconds")
        return name

    Caller = Annotated[str, Depends(caller)]

    @tool(READ_ONLY)
    async def get_cinema(_: Caller) -> Cinema:
        """The cinema's name, its current date and time, the seat limit per booking and the week on sale."""
        return await get_resources().catalog.cinema(get_now())

    @tool(READ_ONLY)
    async def list_films(_: Caller) -> list[Movie]:
        """Every film showing, with its id, year, genres, synopsis and studio."""
        return await get_resources().catalog.movies()

    @tool(READ_ONLY)
    async def find_showtimes(
        _: Caller,
        day: Annotated[date, Field(description="The day in cinema time, as YYYY-MM-DD, within the week on sale")],
        film_id: Annotated[int | None, Field(description="Only this film. Leave it out for every film")] = None,
    ) -> list[Showtime]:
        """Showtimes on one day that have not started yet, with the price per seat and the seats left."""
        return await get_resources().catalog.showtimes(day, get_now(), film_id)

    @tool(READ_ONLY)
    async def get_seat_map(_: Caller, showtime_id: int) -> ToolResult:
        """The seat map of a showtime as text and a visual PNG image. Read it before choosing seats."""
        seat_map = await get_resources().catalog.seat_map(showtime_id)
        taken = {seat.id for row in seat_map.rows for seat in row.seats if seat.is_taken}
        showtime = seat_map.showtime
        heading = f"{showtime.movie_title}, {showtime.starts_at_local}, studio {showtime.studio_number}"
        text = f"{heading}\n{SEAT_MAP_LEGEND}\n{seat_map_text(taken)}"
        png = render_seat_map_png(
            taken,
            title=showtime.movie_title,
            subtitle=f"{showtime.starts_at_local} - Studio {showtime.studio_number}",
            as_of=clock_time(get_now()),
        )
        return ToolResult(content=[text, Image(data=png, format="png")])

    @tool(READ_ONLY)
    async def prepare_booking(
        owner: Caller,
        showtime_id: int,
        seats: Annotated[SeatIds, Field(description="Every seat of the booking, ids as in the seat map")],
        customer_name: Annotated[CustomerName, Field(description="The name the booking is under")],
    ) -> ToolResult:
        """Checks a booking and returns its summary, confirmation id, and visual seat preview. Nothing is held yet."""
        form = BookingForm(showtime_id=showtime_id, seats=seats, customer_name=customer_name, channel="mcp")
        quote = await get_resources().bookings.prepare(form, owner, get_now())
        seat_map = await get_resources().catalog.seat_map(showtime_id)
        taken = {seat.id for row in seat_map.rows for seat in row.seats if seat.is_taken}
        png = render_seat_map_png(
            taken,
            set(quote.summary.seats),
            title=quote.summary.movie_title,
            subtitle=f"{quote.summary.starts_at_local} - Studio {quote.summary.studio_number}",
            as_of=clock_time(get_now()),
        )
        return ToolResult(content=[quote.model_dump_json(), Image(data=png, format="png")], structured_content=quote)

    @tool(BOOKS_ONCE)
    async def confirm_booking(
        owner: Caller,
        confirmation_id: Annotated[str, Field(description="From prepare_booking, after the person agreed")],
    ) -> Booking:
        """Books a prepared booking and returns its booking code. Call it only after the person agreed to it."""
        return await get_resources().bookings.confirm(confirmation_id, owner, get_now())

    @tool(READ_ONLY)
    async def get_booking(
        owner: Caller,
        booking_code: Annotated[str, Field(description="The code confirm_booking returned, such as TK1A2B3C4D")],
    ) -> Booking:
        """One booking, found by its booking code."""
        return await get_resources().bookings.by_code(booking_code, owner)

    if verifier is None:
        return mcp  # callers without a key are one caller: a list would show them each other's names and codes

    @tool(READ_ONLY)
    async def list_my_bookings(owner: Caller) -> list[Booking]:
        """The caller's latest bookings, newest first."""
        return await get_resources().bookings.recent(owner)

    return mcp

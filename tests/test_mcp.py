"""An MCP client books through the same rules as the form: a prepared booking first, then its confirmation."""

from datetime import timedelta
from typing import Any

import httpx
import httpx2
import pytest
from fastapi import FastAPI
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.exceptions import ToolError
from fastmcp.utilities.asgi_transport import StreamingASGITransport, run_asgi_lifespan
from mcp.shared.exceptions import MCPError

from app.core.application import create_app
from app.core.lifespan import Resources
from app.mcp.server import build_mcp_server
from app.repositories.cinema import CinemaStore
from app.schemas.cinema import Showtime
from app.settings import Settings

from conftest import NOW, TODAY, keyless


async def prepare(mcp: Client[Any], showtime: Showtime, seats: list[str]) -> dict[str, Any]:
    arguments = {"showtime_id": showtime.id, "seats": seats, "customer_name": "Rafi"}
    quote: dict[str, Any] = (await mcp.call_tool("prepare_booking", arguments)).structured_content
    return quote


async def test_the_tools_say_which_ones_only_read(mcp: Client[Any]) -> None:
    tools = {tool.name: tool for tool in await mcp.list_tools()}
    assert set(tools) == {
        "get_cinema",
        "list_films",
        "find_showtimes",
        "get_seat_map",
        "prepare_booking",
        "confirm_booking",
        "get_booking",
    }  # no list without keys: every such caller is the same caller
    assert tools["prepare_booking"].annotations.read_only_hint is True
    assert tools["confirm_booking"].annotations.read_only_hint is False
    assert "owner" not in tools["prepare_booking"].input_schema["properties"]  # the caller is never an argument


async def test_a_client_finds_the_week_a_showtime_and_its_seats(mcp: Client[Any], dune_today: list[Showtime]) -> None:
    cinema = (await mcp.call_tool("get_cinema", {})).structured_content
    assert cinema["now_local"] == "Sunday 08 November 2026, 10:00 WIB"
    assert cinema["week"]["days"][0] == "2026-11-02" and cinema["week"]["is_published"] is True
    found = await mcp.call_tool("find_showtimes", {"day": TODAY.isoformat(), "film_id": 9})
    assert [showtime["id"] for showtime in found.structured_content["result"]] == [s.id for s in dune_today]
    seat_map = (await mcp.call_tool("get_seat_map", {"showtime_id": dune_today[2].id})).content[0].text
    assert "18:00 WIB" in seat_map and "A9 | A10" in seat_map


async def test_nothing_is_booked_until_the_prepared_booking_is_confirmed(
    mcp: Client[Any], store: CinemaStore, dune_today: list[Showtime]
) -> None:
    evening = dune_today[2]
    quote = await prepare(mcp, evening, ["D9", "D10"])
    assert quote["summary"]["total_price_idr"] == 2 * evening.price_idr  # priced from the database
    assert await store.taken_seat_ids(evening.id) == set()

    confirmation = {"confirmation_id": quote["confirmation_id"]}
    booking = (await mcp.call_tool("confirm_booking", confirmation)).structured_content
    assert booking["channel"] == "mcp" and booking["seats"] == ["D9", "D10"]
    again = (await mcp.call_tool("confirm_booking", confirmation)).structured_content
    assert again["code"] == booking["code"]  # confirming twice books once
    found = (await mcp.call_tool("get_booking", {"booking_code": booking["code"]})).structured_content
    assert found["seats"] == ["D9", "D10"] and found["customer_name"] == "Rafi"
    with pytest.raises(ToolError, match="no booking with this code"):
        await mcp.call_tool("get_booking", {"booking_code": "TK00000000"})


async def test_a_seat_sold_while_the_person_decides_is_refused_at_confirmation(
    mcp: Client[Any], client: httpx.AsyncClient, dune_today: list[Showtime]
) -> None:
    quote = await prepare(mcp, dune_today[2], ["D9"])
    form = {"showtime_id": dune_today[2].id, "seats": ["D9"], "customer_name": "Sari"}
    assert (await client.post("/v1/bookings", json=form, headers={"Idempotency-Key": "form-key-1"})).status_code == 201
    with pytest.raises(ToolError, match="D9"):
        await mcp.call_tool("confirm_booking", {"confirmation_id": quote["confirmation_id"]})


async def test_a_changed_or_expired_confirmation_id_books_nothing(
    mcp: Client[Any], resources: Resources, settings: Settings, dune_today: list[Showtime]
) -> None:
    confirmation_id = (await prepare(mcp, dune_today[2], ["D9"]))["confirmation_id"]
    with pytest.raises(ToolError, match="not valid"):
        await mcp.call_tool("confirm_booking", {"confirmation_id": f"x{confirmation_id}"})
    later = build_mcp_server(lambda: resources, lambda: NOW + timedelta(minutes=11), keyless(settings))
    async with Client(later) as eleven_minutes_later:
        with pytest.raises(ToolError, match="expired"):
            await eleven_minutes_later.call_tool("confirm_booking", {"confirmation_id": confirmation_id})


@pytest.mark.parametrize(
    ("change", "reason"),
    [
        ({"seats": ["Z1"]}, "not a seat"),
        ({"seats": [f"G{number}" for number in range(1, 10)]}, "At most 8"),
        ({"showtime_id": 999_999}, "no showtime"),
    ],
)
async def test_a_booking_the_form_would_refuse_is_refused_here_with_the_reason(
    mcp: Client[Any], dune_today: list[Showtime], change: dict[str, Any], reason: str
) -> None:
    booking = {"showtime_id": dune_today[2].id, "seats": ["D9"], "customer_name": "Rafi", **change}
    with pytest.raises(ToolError, match=reason):
        await mcp.call_tool("prepare_booking", booking)


async def test_over_http_a_client_needs_an_api_key_and_books_as_that_caller(
    settings: Settings, resources: Resources, client: httpx.AsyncClient, dune_today: list[Showtime]
) -> None:
    mcp_app = build_mcp_server(lambda: resources, lambda: NOW, settings).http_app(
        path="/", json_response=True, stateless_http=True
    )
    host = FastAPI(lifespan=mcp_app.lifespan)
    host.mount("/mcp", mcp_app)

    def connect(api_key: str) -> Client[Any]:
        def in_process(**kwargs: Any) -> httpx2.AsyncClient:
            return httpx2.AsyncClient(transport=StreamingASGITransport(host), **kwargs)

        return Client(StreamableHttpTransport("http://test/mcp/", auth=api_key, httpx_client_factory=in_process))

    async with run_asgi_lifespan(host):
        with pytest.raises(MCPError):
            async with connect("not-a-key") as stranger:
                await stranger.list_tools()
        async with connect("test-key-0001") as known:
            quote = await prepare(known, dune_today[2], ["E5"])
            booked = await known.call_tool("confirm_booking", {"confirmation_id": quote["confirmation_id"]})
            mine = (await known.call_tool("list_my_bookings", {})).structured_content["result"]
            assert [item["code"] for item in mine] == [booked.structured_content["code"]]
        async with connect("other-key-0002") as someone_else:  # a code alone does not open another caller's booking
            with pytest.raises(ToolError, match="no booking with this code"):
                await someone_else.call_tool("get_booking", {"booking_code": booked.structured_content["code"]})
    bookings = (await client.get("/v1/bookings")).json()  # the same key on the HTTP API is the same caller
    assert [booking["channel"] for booking in bookings] == ["mcp"]


async def test_a_public_server_takes_callers_without_a_key_and_lists_nobodys_bookings(
    settings: Settings, resources: Resources, client: httpx.AsyncClient, dune_today: list[Showtime]
) -> None:
    public = settings.model_copy(update={"mcp_public": True})  # API keys stay set for the HTTP API
    async with Client(build_mcp_server(lambda: resources, lambda: NOW, public)) as visitor:
        assert "list_my_bookings" not in {tool.name for tool in await visitor.list_tools()}
        quote = await prepare(visitor, dune_today[2], ["F5"])
        booking = (await visitor.call_tool("confirm_booking", {"confirmation_id": quote["confirmation_id"]})).data
        assert (await visitor.call_tool("get_booking", {"booking_code": booking.code})).data.seats == ["F5"]
    assert (await client.get("/v1/bookings")).json() == []  # a key's own list does not hold the visitor's booking


async def test_the_mcp_server_can_be_turned_off(settings: Settings, client: httpx.AsyncClient) -> None:
    assert (await client.get("/meta")).json()["mcp_path"] == "/mcp"
    without_mcp = create_app(settings.model_copy(update={"mcp_enabled": False}))
    assert "/mcp" not in [getattr(route, "path", None) for route in without_mcp.routes]
    assert "/mcp" in [getattr(route, "path", None) for route in create_app(settings).routes]

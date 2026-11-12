from typing import Any

import httpx

from app.schemas.cinema import Showtime


def form_booking(showtime: Showtime, seats: list[str], **more: Any) -> dict[str, Any]:
    return {"showtime_id": showtime.id, "seats": seats, "customer_name": "Sari", **more}


async def book(
    client: httpx.AsyncClient, body: dict[str, Any], key: str = "form-key-0001", **headers: str
) -> httpx.Response:
    return await client.post("/v1/bookings", json=body, headers={"Idempotency-Key": key, **headers})


async def test_the_form_books_seats_priced_from_the_database(
    client: httpx.AsyncClient, dune_today: list[Showtime]
) -> None:
    evening = dune_today[2]
    response = await book(client, form_booking(evening, ["F7", "F8"]))
    assert response.status_code == 201
    booking = response.json()
    assert booking["channel"] == "web" and booking["seats"] == ["F7", "F8"]
    assert booking["total_price_idr"] == 2 * evening.price_idr
    seats = (await client.get(f"/v1/showtimes/{evening.id}/seats")).json()
    taken = {seat["id"] for row in seats["rows"] for seat in row["seats"] if seat["is_taken"]}
    assert taken == {"F7", "F8"}


async def test_a_retried_request_gets_the_same_booking(client: httpx.AsyncClient, dune_today: list[Showtime]) -> None:
    first = await book(client, form_booking(dune_today[2], ["F7"]))
    again = await book(client, form_booking(dune_today[2], ["F7"]))
    assert first.json()["code"] == again.json()["code"]
    assert len((await client.get("/v1/bookings")).json()) == 1


async def test_a_seat_one_channel_booked_is_refused_on_another(
    client: httpx.AsyncClient, dune_today: list[Showtime]
) -> None:
    evening = dune_today[2]
    from_the_agent = form_booking(evening, ["D9"], channel="chat", session_id="a" * 32)
    assert (await book(client, from_the_agent, key="call_book_tickets_1")).status_code == 201

    response = await book(client, form_booking(evening, ["D9", "D10"]))
    assert response.status_code == 409 and "D9" in response.json()["detail"]
    bookings = (await client.get("/v1/bookings")).json()
    assert [booking["channel"] for booking in bookings] == ["chat"]  # D10 was not taken on its own either


async def test_the_list_holds_every_channel_and_only_the_callers_own(
    client: httpx.AsyncClient, dune_today: list[Showtime]
) -> None:
    conversation = "c" * 32
    await book(client, form_booking(dune_today[2], ["A1"]), key="form-key-0001")
    await book(client, form_booking(dune_today[2], ["A2"], channel="chat", session_id=conversation), key="call-0002")
    other = await book(
        client, form_booking(dune_today[2], ["A3"]), key="form-key-0001", **{"X-API-Key": "other-key-0002"}
    )
    assert other.status_code == 201  # the same key from another caller is another booking
    mine = (await client.get("/v1/bookings")).json()
    assert [booking["seats"] for booking in mine] == [["A2"], ["A1"]]  # newest first
    of_the_conversation = (await client.get("/v1/bookings", params={"session_id": conversation})).json()
    assert [booking["seats"] for booking in of_the_conversation] == [["A2"]]
    not_the_owner = await client.get(
        "/v1/bookings", params={"session_id": conversation}, headers={"X-API-Key": "other-key-0002"}
    )
    assert not_the_owner.json() == []  # knowing a conversation's id shows nothing of it


async def test_the_seat_limit_holds_and_a_key_is_required(
    client: httpx.AsyncClient, dune_today: list[Showtime]
) -> None:
    nine = [f"G{number}" for number in range(1, 10)]
    assert (await book(client, form_booking(dune_today[2], nine))).status_code == 409
    missing_key = await client.post("/v1/bookings", json=form_booking(dune_today[2], ["G1"]))
    assert missing_key.status_code == 422

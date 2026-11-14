import asyncio
from datetime import timedelta

import pytest
from pydantic import ValidationError

from app.core.errors import Conflict
from app.repositories.cinema import CinemaStore
from app.schemas.cinema import BookingRequest, Showtime
from app.utils.seat_layout import SEATS_PER_SHOWTIME, seat_map_text

from conftest import CINEMA_TIMEZONE, DUNE, NOW


def request(showtime_id: int, seats: list[str], key: str = "call-1", session_id: str = "s1") -> BookingRequest:
    return BookingRequest(
        idempotency_key=key,
        owner="key:key-0001",
        channel="chat",
        session_id=session_id,
        showtime_id=showtime_id,
        seats=seats,
        customer_name="Rafi",
    )


async def test_a_booking_takes_its_seats_and_charges_per_seat(store: CinemaStore, dune_today: list[Showtime]) -> None:
    evening = dune_today[2]
    booking = await store.book(request(evening.id, ["D9", "D10"]), NOW)
    assert booking.seats == ["D9", "D10"]
    assert booking.total_price_idr == 2 * evening.price_idr
    assert await store.taken_seat_ids(evening.id) == {"D9", "D10"}
    assert (await store.get_showtime(evening.id)).seats_left == SEATS_PER_SHOWTIME - 2


async def test_a_seat_is_sold_once_and_a_failed_booking_takes_nothing(
    store: CinemaStore, dune_today: list[Showtime]
) -> None:
    evening = dune_today[2]
    await store.book(request(evening.id, ["D9"], key="first"), NOW)
    with pytest.raises(Conflict, match="D9"):
        await store.book(request(evening.id, ["D10", "D9"], key="second", session_id="s2"), NOW)
    assert await store.taken_seat_ids(evening.id) == {"D9"}  # D10 was not kept from the refused booking


async def test_people_booking_one_seat_at_the_same_moment_get_it_once(
    store: CinemaStore, dune_today: list[Showtime]
) -> None:
    evening = dune_today[2]
    attempts = [store.book(request(evening.id, ["D9"], key=f"person-{n}", session_id=f"s{n}"), NOW) for n in range(12)]
    outcomes = await asyncio.gather(*attempts, return_exceptions=True)
    refused = [outcome for outcome in outcomes if isinstance(outcome, Conflict)]
    assert len(refused) == len(outcomes) - 1 == 11
    assert await store.taken_seat_ids(evening.id) == {"D9"}
    assert (await store.get_showtime(evening.id)).seats_left == SEATS_PER_SHOWTIME - 1


async def test_one_request_sent_twice_at_the_same_moment_books_once(
    store: CinemaStore, dune_today: list[Showtime]
) -> None:
    sent_twice = [store.book(request(dune_today[2].id, ["E5", "E6"]), NOW) for _ in range(2)]
    first, second = await asyncio.gather(*sent_twice)
    assert first.code == second.code
    assert len(await store.bookings_for_owner("key:key-0001", 20)) == 1


async def test_the_same_tool_call_books_once(store: CinemaStore, dune_today: list[Showtime]) -> None:
    first = await store.book(request(dune_today[2].id, ["E5"]), NOW)
    again = await store.book(request(dune_today[2].id, ["E5"]), NOW)
    assert again.code == first.code
    assert len(await store.bookings_for_owner("key:key-0001", 20, session_id="s1")) == 1


async def test_a_started_showtime_cannot_be_booked(store: CinemaStore, dune_today: list[Showtime]) -> None:
    lunchtime = dune_today[0]
    with pytest.raises(Conflict, match="started"):
        await store.book(request(lunchtime.id, ["A1"]), lunchtime.starts_at + timedelta(minutes=5))


async def test_a_days_showtimes_leave_out_the_ones_already_started(store: CinemaStore) -> None:
    afternoon = NOW + timedelta(hours=6)  # 16:00 in Jakarta
    showtimes = await store.showtimes_on(afternoon.astimezone(CINEMA_TIMEZONE).date(), afternoon, DUNE)
    assert [showtime.starts_at.astimezone(CINEMA_TIMEZONE).strftime("%H:%M") for showtime in showtimes] == [
        "18:00",
        "20:45",
    ]


async def test_a_callers_bookings_come_newest_first_each_with_its_own_seats(
    store: CinemaStore, dune_today: list[Showtime]
) -> None:
    await store.book(request(dune_today[2].id, ["A1", "A2"], key="first"), NOW)
    await store.book(request(dune_today[3].id, ["B5"], key="second", session_id="s2"), NOW + timedelta(minutes=1))
    bookings = await store.bookings_for_owner("key:key-0001", 20)
    assert [booking.seats for booking in bookings] == [["B5"], ["A1", "A2"]]
    assert [booking.showtime.id for booking in bookings] == [dune_today[3].id, dune_today[2].id]
    assert [b.seats for b in await store.bookings_for_owner("key:key-0001", 20, session_id="s2")] == [["B5"]]
    assert await store.bookings_for_owner("key:someone-else", 20) == []


@pytest.mark.parametrize("seats", [["Z1"], ["d5"], ["K3"], ["D5", "D5"], []])
def test_seats_outside_the_layout_or_repeated_are_refused_where_they_enter(seats: list[str]) -> None:
    with pytest.raises(ValidationError):
        request(1, seats)


def test_the_seat_map_shows_taken_seats_the_aisle_and_the_walkway() -> None:
    lines = seat_map_text({"A9", "M18"}).splitlines()
    assert lines[0] == "SCREEN (front)"
    assert lines[1].startswith("A1 A2") and "A8 -- | A10" in lines[1]
    assert lines[11] == "(walkway)"
    assert lines[-2].endswith("M17 --")

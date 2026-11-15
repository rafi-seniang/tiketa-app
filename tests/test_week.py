"""The schedule is published one week at a time, Monday to Sunday in cinema time, and old weeks are kept."""

from datetime import date, timedelta

import httpx
from sqlalchemy import func, select

from app.core.database import Sessions
from app.models.cinema import MovieRow, ShowtimeRow
from app.repositories.cinema import CinemaStore
from app.schemas.cinema import BookingRequest, Showtime
from app.services.weekly_schedule import publish_week
from app.utils.clock import week_days

from conftest import CINEMA_TIMEZONE, DUNE, NOW, TODAY

FILMS = 21
SHOWTIMES_A_DAY = 4
NEXT_MONDAY = date(2026, 11, 9)


async def showtime_count(sessions: Sessions) -> int:
    async with sessions() as db:
        return int(await db.scalar(select(func.count()).select_from(ShowtimeRow)) or 0)


def test_a_week_runs_from_monday_to_sunday() -> None:
    assert week_days(date(2026, 11, 8)) == [date(2026, 11, day) for day in range(2, 9)]  # asked on the Sunday
    assert week_days(NEXT_MONDAY)[0] == NEXT_MONDAY and week_days(NEXT_MONDAY)[-1] == date(2026, 11, 15)


async def test_a_published_week_has_every_film_on_each_of_its_seven_days(
    sessions: Sessions, store: CinemaStore
) -> None:
    assert await showtime_count(sessions) == FILMS * SHOWTIMES_A_DAY * 7
    monday = week_days(TODAY)[0]
    midnight = NOW - timedelta(days=7)  # before the week began, so no showtime has started
    assert len(await store.showtimes_on(monday, midnight, DUNE)) == SHOWTIMES_A_DAY
    assert await store.showtimes_on(monday - timedelta(days=1), midnight, DUNE) == []  # the Sunday before


async def test_publishing_a_week_again_adds_nothing(sessions: Sessions) -> None:
    assert await publish_week(sessions, TODAY, CINEMA_TIMEZONE) == (0, 0)
    assert await publish_week(sessions, week_days(TODAY)[0], CINEMA_TIMEZONE) == (0, 0)  # any day of the same week


async def test_a_film_already_published_takes_the_catalogue_again(sessions: Sessions) -> None:
    async with sessions.begin() as db:
        film = await db.scalar(select(MovieRow).where(MovieRow.id == DUNE))
        assert film is not None
        film.synopsis, film.backdrop_url = "an old story", None  # as published before the catalogue changed
    await publish_week(sessions, TODAY, CINEMA_TIMEZONE)
    async with sessions() as db:
        film = await db.scalar(select(MovieRow).where(MovieRow.id == DUNE))
    assert film is not None and film.synopsis.startswith("Paul Atreides joins Chani")
    assert film.backdrop_url and film.backdrop_url.endswith(".jpg")


async def test_the_next_week_is_added_and_the_old_week_stays_with_its_bookings(
    sessions: Sessions, store: CinemaStore, dune_today: list[Showtime]
) -> None:
    old = BookingRequest(
        idempotency_key="k1",
        owner="key:a",
        channel="web",
        showtime_id=dune_today[2].id,
        seats=["A1"],
        customer_name="R",
    )
    booked = await store.book(old, NOW)
    assert await publish_week(sessions, NEXT_MONDAY, CINEMA_TIMEZONE) == (0, FILMS * SHOWTIMES_A_DAY * 7)
    assert await showtime_count(sessions) == 2 * FILMS * SHOWTIMES_A_DAY * 7
    kept = await store.bookings_for_owner("key:a", 20)
    assert [booking.code for booking in kept] == [booked.code] and kept[0].showtime.id == dune_today[2].id


async def test_the_cinema_names_its_week_and_whether_it_is_published(
    client: httpx.AsyncClient, store: CinemaStore
) -> None:
    cinema = (await client.get("/v1/cinema")).json()
    assert cinema["week"]["days"] == [f"2026-11-0{day}" for day in range(2, 9)]
    assert cinema["week"]["today"] == "2026-11-08" and cinema["week"]["is_published"] is True
    assert cinema["now_local"] == "Sunday 08 November 2026, 10:00 WIB" and cinema["max_seats_per_booking"] == 8
    assert await store.is_week_published(NEXT_MONDAY) is False  # until Monday's publishing run

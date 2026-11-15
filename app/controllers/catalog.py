"""Films, the week on sale, a day's showtimes and a seat map, read by the web app, the agent and MCP clients."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

from app.repositories.cinema import CinemaStore
from app.schemas.cinema import Cinema, Movie, SeatMap, Showtime, Week
from app.utils.clock import local_text, week_days


class CatalogController:
    def __init__(self, store: CinemaStore, cinema_name: str, cinema_timezone: ZoneInfo, max_seats: int) -> None:
        self._store = store
        self._cinema_name = cinema_name
        self._cinema_timezone = cinema_timezone
        self._max_seats = max_seats

    async def cinema(self, now: datetime) -> Cinema:
        today = now.astimezone(self._cinema_timezone).date()
        week = Week(days=week_days(today), today=today, is_published=await self._store.is_week_published(today))
        return Cinema(
            name=self._cinema_name,
            timezone=self._cinema_timezone.key,
            now=now,
            now_local=local_text(now, self._cinema_timezone),
            max_seats_per_booking=self._max_seats,
            week=week,
        )

    async def movies(self) -> list[Movie]:
        return await self._store.list_movies()

    async def movie(self, movie_id: int) -> Movie:
        return await self._store.get_movie(movie_id)

    async def showtimes(self, day: date, now: datetime, movie_id: int | None) -> list[Showtime]:
        return await self._store.showtimes_on(day, now, movie_id)

    async def showtime(self, showtime_id: int) -> Showtime:
        return await self._store.get_showtime(showtime_id)

    async def seat_map(self, showtime_id: int) -> SeatMap:
        return await self._store.seat_map(showtime_id)

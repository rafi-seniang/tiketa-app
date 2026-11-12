"""The week on sale. Each Monday a new week of showtimes is added, Monday to Sunday in cinema time.

Publishing is its own step (scripts/publish_week.py, by hand or from cron), never a side effect of a request.
Nothing is removed: past weeks stay in the database with their bookings.
"""

from datetime import UTC, date, datetime, time
from itertools import product
from zoneinfo import ZoneInfo

from sqlalchemy import select

from app.core.database import Sessions
from app.models.cinema import MovieRow, ShowtimeRow
from app.repositories.sample_films import SAMPLE_MOVIES
from app.utils.clock import local_week_window, week_days

# Odd studios start on the half hour, even ones half an hour later, so films do not all start together
ODD_STUDIO_START_TIMES = (time(12, 30), time(15, 15), time(18, 0), time(20, 45))
EVEN_STUDIO_START_TIMES = (time(13, 0), time(15, 45), time(18, 30), time(21, 15))
# Ticket price by weekday (Monday is 0): Monday to Thursday, Friday, then the weekend
PRICE_IDR_BY_WEEKDAY = (45_000, 45_000, 45_000, 45_000, 50_000, 60_000, 60_000)


def start_times_of(studio_number: int) -> tuple[time, ...]:
    return ODD_STUDIO_START_TIMES if studio_number % 2 else EVEN_STUDIO_START_TIMES


async def publish_week(sessions: Sessions, day: date, cinema_timezone: ZoneInfo) -> tuple[int, int]:
    """Adds the films and the showtimes still missing from the week `day` falls in. Returns how many of each."""
    async with sessions.begin() as db:
        known_titles = set(await db.scalars(select(MovieRow.title)))
        new_movies = [MovieRow(**movie) for movie in SAMPLE_MOVIES if movie["title"] not in known_titles]
        db.add_all(new_movies)
        await db.flush()
        movies = (await db.scalars(select(MovieRow))).all()

        week_starts, week_ends = local_week_window(day, cinema_timezone)
        published = await db.execute(
            select(ShowtimeRow.movie_id, ShowtimeRow.starts_at).where(
                ShowtimeRow.starts_at >= week_starts, ShowtimeRow.starts_at < week_ends
            )
        )
        published_slots = {(movie_id, starts_at) for movie_id, starts_at in published}
        week_slots = [
            (movie.id, datetime.combine(show_day, start_time, cinema_timezone).astimezone(UTC), show_day.weekday())
            for show_day, movie in product(week_days(day), movies)
            for start_time in start_times_of(movie.studio_number)
        ]
        new_showtimes = [
            ShowtimeRow(movie_id=movie_id, starts_at=starts_at, price_idr=PRICE_IDR_BY_WEEKDAY[weekday])
            for movie_id, starts_at, weekday in week_slots
            if (movie_id, starts_at) not in published_slots
        ]
        db.add_all(new_showtimes)
    return len(new_movies), len(new_showtimes)

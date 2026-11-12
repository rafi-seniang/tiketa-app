"""Add this week's showtimes (Monday to Sunday, cinema time) and any film not yet in the database. Safe to run again.

Run it once after the first `alembic upgrade head`, then every Monday: by hand, or from cron
(scripts/cron/publish_week.cron). Past weeks and their bookings are kept.

Usage: python scripts/publish_week.py [--day YYYY-MM-DD]
"""

import argparse
import asyncio
from datetime import date, datetime
from zoneinfo import ZoneInfo

from app.core.database import connect_database
from app.core.migrations import check_schema
from app.services.weekly_schedule import publish_week
from app.settings import get_settings
from app.utils.clock import week_days


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--day", type=date.fromisoformat, help="Any day of the week to publish. Default: today")
    args = parser.parse_args()
    settings = get_settings()
    cinema_timezone = ZoneInfo(settings.cinema_timezone)
    day: date = args.day or datetime.now(cinema_timezone).date()
    engine, sessions = connect_database(settings.database_url.get_secret_value())
    await check_schema(engine)
    new_movies, new_showtimes = await publish_week(sessions, day, cinema_timezone)
    await engine.dispose()
    days = week_days(day)
    print(f"week {days[0]} to {days[-1]}: added {new_movies} films and {new_showtimes} showtimes")


if __name__ == "__main__":
    asyncio.run(main(), loop_factory=asyncio.SelectorEventLoop)  # psycopg's async mode needs a selector loop

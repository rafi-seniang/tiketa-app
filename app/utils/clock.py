"""Cinema-local time: one local day or week as a UTC window, and a moment written out as people read it."""

from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

DAYS_IN_WEEK = 7


def local_day_window(day: date, cinema_timezone: ZoneInfo) -> tuple[datetime, datetime]:
    """From local midnight of `day` to the next local midnight, in UTC."""
    starts = datetime.combine(day, time(0), cinema_timezone).astimezone(UTC)
    ends = datetime.combine(day + timedelta(days=1), time(0), cinema_timezone).astimezone(UTC)
    return starts, ends


def week_days(day: date) -> list[date]:
    """The seven days, Monday to Sunday, of the week `day` falls in."""
    monday = day - timedelta(days=day.weekday())
    return [monday + timedelta(days=offset) for offset in range(DAYS_IN_WEEK)]


def local_week_window(day: date, cinema_timezone: ZoneInfo) -> tuple[datetime, datetime]:
    """From local midnight on Monday to the next Monday's, in UTC, for the week `day` falls in."""
    days = week_days(day)
    starts, _ = local_day_window(days[0], cinema_timezone)
    _, ends = local_day_window(days[-1], cinema_timezone)
    return starts, ends


def local_text(moment: datetime, cinema_timezone: ZoneInfo) -> str:
    """For example "Sunday 09 November 2026, 19:00 WIB"."""
    local = moment.astimezone(cinema_timezone)
    return f"{local:%A %d %B %Y, %H:%M} {local.tzname()}"

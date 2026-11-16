"""What the cinema hands out and takes in. Seat ids are checked here, once, where they enter."""

from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, Field

from app.utils.seat_layout import AISLE_AFTER_SEAT, ALL_SEAT_IDS, WALKWAY_BEFORE_ROW


def known_seat_id(seat_id: str) -> str:
    if seat_id not in ALL_SEAT_IDS:
        raise ValueError(
            f"{seat_id!r} is not a seat in this studio. Seat ids look like D7: a row letter, then a number"
        )
    return seat_id


def no_repeated_seats(seat_ids: list[str]) -> list[str]:
    if len(set(seat_ids)) != len(seat_ids):
        raise ValueError("a seat is listed twice")
    return seat_ids


SeatId = Annotated[str, AfterValidator(known_seat_id)]
SeatIds = Annotated[list[SeatId], Field(min_length=1), AfterValidator(no_repeated_seats)]
CustomerName = Annotated[str, Field(min_length=1, max_length=80)]


class Movie(BaseModel):
    id: int
    title: str
    synopsis: str
    release_year: int
    genres: list[str]
    studio_number: int
    poster_url: str | None
    backdrop_url: str | None
    trailer_youtube_id: str | None


class Showtime(BaseModel):
    id: int
    movie_id: int
    movie_title: str
    studio_number: int
    starts_at: datetime
    starts_at_local: str  # as people read it, in cinema time
    price_idr: int
    seats_left: int


Channel = Literal["web", "chat", "mcp"]
SessionId = Annotated[str, Field(min_length=1, max_length=40)]


class Booking(BaseModel):
    code: str
    channel: Channel
    showtime: Showtime
    seats: list[str]
    customer_name: str
    total_price_idr: int
    created_at: datetime


class BookingRequest(BaseModel):
    idempotency_key: str
    owner: str
    channel: Channel
    session_id: SessionId | None = None
    showtime_id: int
    seats: SeatIds
    customer_name: CustomerName


class SeatView(BaseModel):
    id: str
    is_taken: bool
    booked_by: str | None = None  # the first letter of the booking's name, for a taken seat


class SeatRowView(BaseModel):
    row: str
    seats: list[SeatView]


class SeatMap(BaseModel):
    """For a UI: rows front to back, and where the aisle and the walkway fall, so a UI draws the real room."""

    showtime: Showtime
    rows: list[SeatRowView]
    aisle_after_seat: int = AISLE_AFTER_SEAT
    walkway_before_row: str = WALKWAY_BEFORE_ROW


class BookingForm(BaseModel):
    """What a client sends to book. The owner comes from the server, never from the body."""

    showtime_id: int
    seats: SeatIds
    customer_name: CustomerName
    channel: Channel = "web"
    session_id: SessionId | None = Field(default=None, description="The chat agent's conversation, if it books")


class BookingSummary(BaseModel):
    """A booking as it would be made, priced from the database, for a person to read before saying yes."""

    showtime_id: int
    movie_title: str
    starts_at: datetime
    starts_at_local: str
    studio_number: int
    seats: list[str]
    customer_name: str
    price_per_seat_idr: int
    total_price_idr: int


class BookingQuote(BaseModel):
    """A prepared booking. Nothing is held: the seats are checked again when the confirmation comes."""

    summary: BookingSummary
    confirmation_id: str
    expires_at: datetime


class Week(BaseModel):
    """The week on sale, Monday to Sunday in cinema time."""

    days: list[date]
    today: date
    is_published: bool  # False until this week's showtimes have been added (scripts/publish_week.py)


class Cinema(BaseModel):
    name: str
    timezone: str
    now: datetime
    now_local: str
    max_seats_per_booking: int
    week: Week


class CallerView(BaseModel):
    caller: str  # how the service names whoever sent the request: guest:..., key:... or ip:...

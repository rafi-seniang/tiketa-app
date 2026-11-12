"""Booking seats, in one request (the form, the chat agent) or in two (MCP: prepare, then confirm)."""

from datetime import datetime

from app.core.errors import Conflict
from app.repositories.cinema import CinemaStore
from app.schemas.cinema import Booking, BookingForm, BookingQuote, BookingRequest
from app.services.booking_quotes import BookingQuotes

RECENT_BOOKINGS = 20


class BookingController:
    def __init__(self, store: CinemaStore, quotes: BookingQuotes, max_seats: int) -> None:
        self._store = store
        self._quotes = quotes
        self._max_seats = max_seats

    async def book(self, form: BookingForm, caller: str, idempotency_key: str, now: datetime) -> Booking:
        """Books every seat or none. A retried request with the same key gets the first booking back."""
        self._refuse_too_many_seats(form)
        request = BookingRequest(
            # A key is unique per caller and channel, not across them
            idempotency_key=f"{form.channel}:{caller}:{idempotency_key}",
            owner=caller,
            **form.model_dump(),
        )
        return await self._store.book(request, now)

    async def prepare(self, form: BookingForm, caller: str, now: datetime) -> BookingQuote:
        """Checks the booking as it stands now and returns it priced, with the id that confirms it."""
        self._refuse_too_many_seats(form)
        showtime = await self._store.get_showtime(form.showtime_id)
        if showtime.starts_at <= now:
            raise Conflict("This showtime has already started")
        taken = await self._store.taken_seat_ids(form.showtime_id)
        taken_now = [seat_id for seat_id in form.seats if seat_id in taken]
        if taken_now:
            raise Conflict(f"Already taken: {', '.join(taken_now)}. Read the seat map again")
        return self._quotes.issue(form, caller, showtime, now)

    async def confirm(self, confirmation_id: str, caller: str, now: datetime) -> Booking:
        """Books a prepared booking. Confirming the same id again returns the same booking."""
        prepared = self._quotes.read(confirmation_id, caller, now)
        return await self.book(prepared.form, caller, prepared.reference, now)

    async def recent(self, caller: str, session_id: str | None = None) -> list[Booking]:
        """The caller's latest bookings from every channel, newest first, or only one conversation's."""
        return await self._store.bookings_for_owner(caller, RECENT_BOOKINGS, session_id)

    def _refuse_too_many_seats(self, form: BookingForm) -> None:
        if len(form.seats) > self._max_seats:
            raise Conflict(f"At most {self._max_seats} seats per booking")

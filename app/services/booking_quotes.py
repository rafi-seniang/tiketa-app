"""A booking in two steps: prepare it, show it to a person, then confirm it with the id the first step returned.

The id is the prepared booking itself, signed by this service. Nothing is stored and no seat is held, so any worker
can confirm it, and the seats are checked again at that moment.
"""

import base64
import secrets
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ValidationError

from app.core.errors import Conflict
from app.core.signing import Signer
from app.schemas.cinema import BookingForm, BookingQuote, BookingSummary, Showtime
from app.utils.clock import local_text


class PreparedBooking(BaseModel):
    reference: str  # random, and the idempotency key of the booking: confirming twice books once
    owner: str
    form: BookingForm
    expires_at: datetime


def summary_of(form: BookingForm, showtime: Showtime, cinema_timezone: ZoneInfo) -> BookingSummary:
    return BookingSummary(
        showtime_id=showtime.id,
        movie_title=showtime.movie_title,
        starts_at=showtime.starts_at,
        starts_at_local=local_text(showtime.starts_at, cinema_timezone),
        studio_number=showtime.studio_number,
        seats=form.seats,
        customer_name=form.customer_name,
        price_per_seat_idr=showtime.price_idr,
        total_price_idr=showtime.price_idr * len(form.seats),
    )


class BookingQuotes:
    def __init__(self, signer: Signer, minutes: int, cinema_timezone: ZoneInfo) -> None:
        self._signer = signer
        self._lifetime = timedelta(minutes=minutes)
        self._cinema_timezone = cinema_timezone

    def issue(self, form: BookingForm, owner: str, showtime: Showtime, now: datetime) -> BookingQuote:
        prepared = PreparedBooking(
            reference=secrets.token_urlsafe(12), owner=owner, form=form, expires_at=now + self._lifetime
        )
        payload = base64.urlsafe_b64encode(prepared.model_dump_json().encode()).decode()
        return BookingQuote(
            summary=summary_of(form, showtime, self._cinema_timezone),
            confirmation_id=f"{payload}.{self._signer.signature(payload)}",
            expires_at=prepared.expires_at,
        )

    def read(self, confirmation_id: str, owner: str, now: datetime) -> PreparedBooking:
        """The prepared booking behind an id this service signed for this caller, while it has not expired."""
        refusal = Conflict("This confirmation id is not valid or has expired. Prepare the booking again")
        payload, _, signature = confirmation_id.partition(".")
        if not self._signer.has_signed(payload, signature):
            raise refusal
        try:
            prepared = PreparedBooking.model_validate_json(base64.urlsafe_b64decode(payload))
        except (ValueError, ValidationError):
            raise refusal from None
        if prepared.owner != owner or prepared.expires_at <= now:
            raise refusal
        return prepared

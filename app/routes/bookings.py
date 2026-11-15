"""Book seats, and list the caller's bookings from the form, the chat agent and MCP clients together."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header

from app.controllers.bookings import BookingController
from app.core.dependencies import get_booking_controller, get_now
from app.middleware.auth import authenticate
from app.schemas.cinema import Booking, BookingForm, SessionId

router = APIRouter(prefix="/bookings", tags=["bookings"])
Controller = Annotated[BookingController, Depends(get_booking_controller)]
Caller = Annotated[str, Depends(authenticate)]


@router.post("", status_code=201)
async def book(
    body: BookingForm,
    controller: Controller,
    caller: Caller,
    now: Annotated[datetime, Depends(get_now)],
    idempotency_key: Annotated[str, Header(min_length=8, max_length=64)],
) -> Booking:
    """Books every seat or none. A retried request with the same Idempotency-Key gets the first booking back."""
    return await controller.book(body, caller, idempotency_key, now)


@router.get("")
async def my_bookings(controller: Controller, caller: Caller, session_id: SessionId | None = None) -> list[Booking]:
    """The caller's latest bookings, newest first. `session_id` keeps those of one chat conversation."""
    return await controller.recent(caller, session_id)

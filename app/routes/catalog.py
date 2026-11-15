"""What every client reads: the cinema and its week, films, a day's showtimes, a seat map."""

from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends

from app.controllers.catalog import CatalogController
from app.core.dependencies import get_catalog_controller, get_now
from app.middleware.auth import authenticate
from app.schemas.cinema import CallerView, Cinema, Movie, SeatMap, Showtime

router = APIRouter(tags=["catalog"])
Controller = Annotated[CatalogController, Depends(get_catalog_controller)]
Now = Annotated[datetime, Depends(get_now)]


@router.get("/cinema")
async def cinema(controller: Controller, now: Now) -> Cinema:
    """The cinema's name, clock and rules, and the week on sale (Monday to Sunday)."""
    return await controller.cinema(now)


@router.get("/me")
async def me(caller: Annotated[str, Depends(authenticate)]) -> CallerView:
    """How the service names the caller. The chat agent asks this to know whose conversation it holds."""
    return CallerView(caller=caller)


@router.get("/movies")
async def list_movies(controller: Controller) -> list[Movie]:
    return await controller.movies()


@router.get("/movies/{movie_id}")
async def get_movie(movie_id: int, controller: Controller) -> Movie:
    return await controller.movie(movie_id)


@router.get("/showtimes")
async def list_showtimes(day: date, controller: Controller, now: Now, movie_id: int | None = None) -> list[Showtime]:
    """Showtimes on a cinema-local day that have not started yet."""
    return await controller.showtimes(day, now, movie_id)


@router.get("/showtimes/{showtime_id}")
async def get_showtime(showtime_id: int, controller: Controller) -> Showtime:
    return await controller.showtime(showtime_id)


@router.get("/showtimes/{showtime_id}/seats")
async def seat_map(showtime_id: int, controller: Controller) -> SeatMap:
    return await controller.seat_map(showtime_id)

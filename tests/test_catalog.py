import httpx

from app.utils.seat_layout import ROWS_FRONT_TO_BACK

from conftest import OWNER


async def test_the_catalog_lists_films_showtimes_and_seats(client: httpx.AsyncClient) -> None:
    movies = (await client.get("/v1/movies")).json()
    assert len(movies) == 21
    assert (await client.get("/v1/movies/9")).json()["title"] == "Dune: Part Two"
    showtimes = (await client.get("/v1/showtimes", params={"day": "2026-11-08", "movie_id": 9})).json()
    assert showtimes[0]["starts_at"] == "2026-11-08T05:30:00Z"
    assert showtimes[0]["starts_at_local"] == "Sunday 08 November 2026, 12:30 WIB"
    assert (await client.get(f"/v1/showtimes/{showtimes[0]['id']}")).json() == showtimes[0]
    seats = (await client.get(f"/v1/showtimes/{showtimes[0]['id']}/seats")).json()
    assert [row["row"] for row in seats["rows"]] == list(ROWS_FRONT_TO_BACK)


async def test_a_film_or_showtime_that_does_not_exist_is_a_404_with_the_reason(client: httpx.AsyncClient) -> None:
    missing = await client.get("/v1/showtimes/999999/seats")
    assert missing.status_code == 404 and missing.headers["content-type"] == "application/problem+json"
    assert (await client.get("/v1/movies/999")).status_code == 404


async def test_requests_without_a_valid_key_are_refused(client: httpx.AsyncClient) -> None:
    assert (await client.get("/v1/movies", headers={"X-API-Key": "wrong"})).status_code == 401
    assert (await client.get("/health", headers={"X-API-Key": "wrong"})).status_code == 200


async def test_the_service_tells_a_caller_its_name(client: httpx.AsyncClient) -> None:
    assert (await client.get("/v1/me")).json() == {"caller": OWNER}

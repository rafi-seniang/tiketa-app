# Tiketa

Cinema booking for a Jakarta cinema: a booking API that owns films, a week of showtimes, seats and bookings, a web
app with a seat map, and an MCP server so assistants such as Claude can book too. A LangGraph chat agent plugs in as
a separate service.

The booking service is the product. The two AI entry points are add-ons on the same API and the same rules, and
either can be off without anything else noticing. On rafilab.com it is a demo: prices show what a ticket would cost,
and every ticket is free.

    web app (React)  ─────────────►  booking API (FastAPI)  ──►  PostgreSQL
                                        ▲          ▲              films, showtimes, seats, bookings
    chat agent (LangGraph, add-on) ─────┘          │
      github.com/rafi-seniang/tiketa-booking-agent │
    MCP clients (Claude, Cursor) ──► /mcp (FastMCP, add-on, same process)

| Piece | Where | Off means |
|---|---|---|
| Booking API | this repository, `app/` | nothing works: it must be up |
| Web app | this repository, `web/` | the API and the add-ons still work |
| MCP server | this repository, `app/mcp/`, at `/mcp` | `MCP_ENABLED=false`. The API and web app are unchanged |
| Chat agent | [tiketa-booking-agent](https://github.com/rafi-seniang/tiketa-booking-agent) | the web app shows the chat as Off. The seat map books as before |

v1 (tag `v1.0`, 2025) was a Flask app with server-rendered pages. This is v2.

Live at [rafilab.com/tiketa](https://rafilab.com/tiketa/), with the MCP server at
`https://rafilab.com/tiketa/api/mcp/`. How it is deployed: [lab-deploy](https://github.com/rafi-seniang/lab-deploy).
The web app is served under a path there (`VITE_BASE_PATH=/tiketa/` at build time). Its screens have their own
addresses (`/tiketa/film/9`, `/tiketa/showtime/117`, `/tiketa/tickets`); nginx answers every path with the app.

## What holds, whoever books

| Rule | How |
|---|---|
| A seat is sold once per showtime | `UNIQUE (showtime_id, seat_id)` in PostgreSQL. The database refuses a second row, not the code. A test sends twelve bookings for one seat at the same moment and one gets it, on SQLite and on PostgreSQL |
| A booking is all its seats or none | One transaction per booking |
| A retried request books once | An `Idempotency-Key` per request, unique per caller and channel |
| The price is the service's | Totals come from the showtime's price in the database, never from a client or a model |
| A started showtime cannot be booked | Checked against the service's clock |
| At most 8 seats per booking | `MAX_SEATS_PER_BOOKING`, enforced in the controller every channel goes through |
| A booking belongs to its caller | Browsers get a signed `HttpOnly` guest cookie, servers and MCP clients an API key. A caller sees only its own |
| Every channel is recorded | Each booking says `web`, `chat` or `mcp` |

## The week on sale

Showtimes are published one week at a time, Monday to Sunday in cinema time (Asia/Jakarta). The web app shows that
week, with the days already past closed.

    python scripts/publish_week.py              # this week. Safe to run again: it adds only what is missing
    python scripts/publish_week.py --day 2026-11-16

Run it every Monday, by hand or from cron (`scripts/cron/publish_week.cron`, which nothing installs for you).
Publishing is its own step and never a side effect of a request.

Nothing is deleted. A new week adds showtimes, and past weeks stay in the database with their bookings, each with
its time, channel and owner, for later study.

## The MCP server

A [FastMCP](https://gofastmcp.com) 4 server mounted in the API at `/mcp`, on the stateless MCP protocol of
28 July 2026 with plain JSON answers, so any worker can take any call. The tools are written for a model, not
generated from the REST routes, and call the same controllers as the HTTP API. The client's own model is the agent:
no model runs on this side.

| Tool | What |
|---|---|
| `get_cinema` | The cinema's current date and time, the seat limit and the week on sale |
| `list_films` | Every film showing |
| `find_showtimes` | One day's showtimes that have not started, with price and seats left |
| `get_seat_map` | A showtime's seats as text and a picture, taken ones marked |
| `prepare_booking` | Checks a booking and returns its summary, total, a confirmation id and a seat picture. Nothing is booked or held |
| `confirm_booking` | Books a prepared booking. Calling it twice with the same id books once |
| `get_booking` | One booking, by its booking code |
| `list_my_bookings` | The caller's latest bookings. Only for callers with a key |

Booking takes two calls so a person can read the price before anything is booked. The confirmation id is the
prepared booking itself, signed by the service and valid for 10 minutes: nothing is stored, and the seats are checked
again at confirmation. Read tools carry `readOnlyHint`, so a client can ask before `confirm_booking` only.

Try it with the API running:

    claude mcp add --transport http tiketa http://127.0.0.1:8070/mcp/     # Claude Code
    npx @modelcontextprotocol/inspector                                    # then connect to the same URL

With `API_KEYS` set, clients send a key as a bearer token and are limited per minute like any other caller. OAuth for
MCP clients is not implemented.

`MCP_PUBLIC=true` opens `/mcp` to callers without a key, so a visitor's own chatbot (Claude, ChatGPT, an editor) can
book. Those callers are one anonymous caller with one shared limit (`MCP_PUBLIC_RATE_LIMIT_PER_MINUTE`), so
`list_my_bookings` is not offered to them: it would show each visitor the others' names and codes. A booking is read
back with `get_booking` and its code.

The web app's home page has a "Try it" band under the top bar: the server's URL, a button that copies one set of
instructions to paste into any chatbot, and the steps to add the server in each app. The band shows only while `/meta`
reports the MCP server on. Behind Cloudflare, Browser Integrity Check must be off for the MCP path, or clients that
send an unusual User-Agent (Python's, for one) are refused with error 1010.

## Run

Needs Python 3.12, Node 24 and Docker.

    python -m venv .venv && .venv/Scripts/pip install -e ".[dev]"     # .venv/bin on Linux and macOS
    cp .env.example .env
    docker compose up -d                          # Postgres :5434, Redis :6384, on 127.0.0.1 only
    alembic upgrade head                          # the schema. The service refuses to start on an older one
    PYTHONPATH=. python scripts/publish_week.py   # 21 films and this week's showtimes
    python main.py                                # http://127.0.0.1:8070/docs

    cd web && npm ci && npm run dev               # http://localhost:5174

Without Docker, set `DATABASE_URL=sqlite+aiosqlite:///./tiketa.db` and an empty `REDIS_URL`. On Windows, use
`127.0.0.1` rather than `localhost` in the service's own URLs (`localhost` tries IPv6 first and stalls). Open the web
app on `localhost`, the host its API addresses use, so the guest cookie reaches the API and the chat agent alike.

    make check                    # ruff, mypy strict, 50 tests on SQLite with no services, 90% coverage floor
    make test-postgres            # the same tests on PostgreSQL, as CI also runs them
    cd web && npm run lint && npm test && npm run build

## API

| Method and path | What |
|---|---|
| `GET /v1/cinema` | Name, clock, seat limit, and the week on sale with whether it is published |
| `GET /v1/movies`, `GET /v1/movies/{id}` | Films |
| `GET /v1/showtimes?day=&movie_id=`, `GET /v1/showtimes/{id}` | Showtimes that have not started, with seats left |
| `GET /v1/showtimes/{id}/seats` | The seat map: rows, taken seats (with the first letter of the booker's name), the aisle and the walkway |
| `POST /v1/bookings` | Book `showtime_id`, `seats`, `customer_name` with an `Idempotency-Key` header |
| `GET /v1/bookings` | The caller's latest bookings, newest first, each with its channel |
| `GET /v1/me` | How the service names the caller. The chat agent asks this |
| `POST /auth/guest` | Sets the guest session cookie, for browsers, which never get an API key |
| `/mcp` | The MCP server |
| `GET /health`, `GET /meta` | Liveness, and what the service is |

Errors are RFC 9457 problem details with a request id. `/v1` needs `X-API-Key` or the guest cookie once `API_KEYS`
is set. Threats and answers are in [SECURITY.md](SECURITY.md), decisions in
[docs/adr/0001-booking-core-with-add-ons.md](docs/adr/0001-booking-core-with-add-ons.md).

## Layout

    main.py                     entry point: uvicorn on the app from app/core/application.py
    app/settings.py             every environment value, typed (pydantic-settings)
    app/core/                   app factory, lifespan (everything built once at startup), database, Redis, signing,
                                errors, logging, dependencies
    app/middleware/             request id and access log, CORS, guest sessions and API keys, the Redis rate limit
    app/routes/                 one APIRouter per area: catalog, bookings, auth, health
    app/controllers/            what every channel goes through: catalog and bookings
    app/services/               the weekly schedule, and a booking prepared now and confirmed later
    app/mcp/                    the MCP server and its tools
    app/repositories/           every query (the cinema store) and the film list
    app/models/                 SQLAlchemy tables
    app/schemas/                Pydantic models
    app/utils/                  pure helpers: the cinema clock and week, the seat layout
    scripts/                    publish_week.py and its cron line
    migrations/                 Alembic
    tests/                      the store, the API, the week, the MCP server over memory and HTTP, the migrations
    web/                        the React web app: films now showing, a film's week, the seat map and checkout, my
                                tickets, and the agent as a floating chat on every screen

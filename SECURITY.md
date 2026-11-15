# Security

Report a vulnerability privately to rafiseniangwangsa@gmail.com, not in a public issue.

## What is protected

| Asset | Why it matters |
|---|---|
| Seats | A seat sold twice, or held by a fake booking, is a real loss |
| Bookings | They hold people's names and what they booked |
| Secrets | API keys, the session secret, the database password |

## Threats and what answers them

| Threat | Answer | Where |
|---|---|---|
| An API key read from the web app's JavaScript | Browsers never get one. They get a guest session: a random id with an expiry, signed with HMAC-SHA256, in an `HttpOnly`, `SameSite=Strict` cookie, `Secure` once deployed | `app/middleware/auth.py`, `app/routes/auth.py` |
| A forged or edited guest cookie | The signature is checked in constant time and the expiry with it. A wrong one is a 401 | `GuestSessions.read`, `app/core/signing.py` |
| Another site making the browser book (CSRF) | `SameSite=Strict` keeps the cookie off cross-site requests, and CORS allows only the listed origins | `app/middleware/cors.py` |
| Double booking, a retried request booking twice | `UNIQUE (showtime_id, seat_id)`, one transaction per booking, an idempotency key per request | `app/repositories/cinema.py` |
| A client or a model setting the price or the owner | Totals come from the database. The owner comes from the caller's credentials, never from a request body or a tool argument | `app/controllers/bookings.py`, `app/mcp/server.py` |
| An AI agent booking without a person's yes | Over MCP a booking takes two calls: the summary first, then a confirmation with a signed id that expires in 10 minutes and is bound to the caller. Read tools are marked read-only so a client can gate the one that books. The chat agent has its own confirmation step | `app/services/booking_quotes.py`, `app/mcp/server.py` |
| A forged confirmation id, or one prepared by someone else | It is signed by the service and carries its owner. A changed, expired or foreign one books nothing | `BookingQuotes.read` |
| The chat agent doing more than its user may | The agent has no key that can book. It forwards the user's own cookie or key, so the API sees the user | tiketa-booking-agent |
| Reading someone else's bookings | Each belongs to its caller, also when filtered by a conversation id | `app/repositories/cinema.py` |
| Visitors' assistants seeing each other's bookings on a public MCP server | Callers without a key are one caller, so they get no list. A booking is read back only with its code, and a code opens only the caller's own | `app/mcp/server.py` |
| One caller flooding the service | 60 requests a minute per caller on `/v1` and `/mcp`, counted in Redis across workers | `app/middleware/rate_limit.py` |
| API keys in logs or Redis | Callers are named by a SHA-256 prefix of their key. Keys are compared in constant time and several can be active, for rotation | `app/middleware/rate_limit.py` |
| Internals in error messages | HTTP errors are problem+json with a short detail and a request id. MCP tools return a refusal's reason and mask anything unexpected. Stack traces go to the logs only | `app/core/errors.py`, `app/mcp/server.py` |
| Private answers kept by a cache or framed by a page | `Cache-Control: no-store` on `/v1`, `/auth` and `/mcp`, `nosniff`, `X-Frame-Options: DENY`, HSTS in production. The web app's nginx sends a Content-Security-Policy | `app/middleware/security_headers.py`, `web/nginx.conf` |
| A secret committed by mistake | Secrets live outside the repository. gitleaks runs before each commit and on every push | `.pre-commit-config.yaml`, `.github/workflows/ci.yml` |
| A vulnerable or compromised dependency | pip-audit and npm audit fail the build on a known vulnerability. FastMCP is pinned exactly. Dependabot proposes updates only for releases 14 days old | `.github/workflows/ci.yml`, `.github/dependabot.yml` |
| Running a misconfigured production | The service refuses to start in production without `API_KEYS` and `SESSION_SECRET`, and refuses an unmigrated database | `app/settings.py`, `app/core/migrations.py` |
| A compromised container | Both images run as a non-root user with only the app's files | `Dockerfile`, `web/Dockerfile` |

## Accepted for now

- A prepared booking holds no seat. Two people can prepare the same seat, and the second confirmation is refused.
  Seat holds that expire are not built.
- A guest session proves a browser, not a person. A determined caller can start many and fill a showtime with fake
  bookings, each still paid at the counter. A CAPTCHA on `/auth/guest` would raise the bar.
- MCP clients authenticate with an API key as a bearer token. OAuth, which the MCP specification describes for
  remote servers, is not implemented, so a key is given to a person by hand.
- With `MCP_PUBLIC=true` anyone can book over MCP without a key, as anyone can with a guest session on the web. A
  booking code is 32 random bits. At the shared limit, finding one given booking by guessing takes about seven
  million minutes on average, and hitting any one of a thousand takes about five days, so codes should grow
  longer before real use. Fake bookings
  that fill a showtime are possible, as on the web, and are each still paid at the counter.
- FastMCP is at 4.1.4. Newer patch releases exist and are taken once they are 14 days old.
- Names on bookings are stored as typed. There is no retention period: nothing is deleted, by design, so the data
  can be studied later. A public deployment needs a notice that it is a demonstration.

## Out of scope

Payment (bookings are paid at the counter with the code), user accounts and passwords, and cancelling a booking.

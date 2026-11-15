# 0001. A booking core, with the chat agent and MCP as add-ons

Date: 12 November 2026. Status: accepted. Replaces Tiketa v1 in this repository (a Flask app, tag `v1.0`) and takes
over the booking half of tiketa-booking-agent v0.1.0, where the agent and the booking API were one service.

## Context

Tiketa had grown an AI agent that also owned the cinema's data. A cinema sells seats with or without a chat. Two AI
entry points were wanted, a LangGraph chat agent and an MCP server for assistants such as Claude, and neither may
become a second place that decides whether a seat is free or what it costs.

## Decision

- **One owner of the cinema.** This service owns films, showtimes, seats, bookings, prices and guest sessions in
  one PostgreSQL database. The web app, the chat agent and MCP clients all book through the same controller, so a
  rule is written once: the unique seat constraint, the idempotency key, the seat limit, the price.
- **Add-ons can be off.** The chat agent is a separate service and repository. The web app checks its health and
  shows the chat as Off when it does not answer. The MCP server is mounted in this process and turned off with one
  setting. Booking on the seat map never depends on either.
- **The schedule is a week, published on purpose.** Showtimes are added for one week, Monday to Sunday in cinema
  time, by a script run by hand or from cron. Publishing is never a side effect of a request, and running it again
  adds nothing.
- **Nothing is deleted.** A new week adds rows. Past showtimes and bookings stay, with their time, channel and
  owner, so they can be studied later. The API shows what has not started yet.
- **MCP tools are written for a model.** Seven tools on FastMCP 4, mounted at `/mcp` on the stateless protocol of
  28 July 2026 with JSON answers. They call the controllers in process. The client's model is the agent.
- **Booking over MCP takes two calls.** `prepare_booking` returns the priced summary and a confirmation id,
  `confirm_booking` books it. The id is the prepared booking, signed by the service, bound to the caller and valid
  for 10 minutes. It is the kind of server-minted handle the stateless protocol asks for in place of sessions:
  nothing is stored, any worker can confirm, and confirming twice books once.
- **The agent books as the user.** The API names a caller from a guest cookie or an API key (`GET /v1/me`). The chat
  agent forwards the user's own credentials and holds no key that can book.

## Set aside

- **Generating the MCP server from the OpenAPI schema** (`FastMCP.from_fastapi`). One line of code, and FastMCP's
  own documentation advises against it beyond prototypes: models do better with a few tools shaped for them than
  with every REST route. It would also expose `POST /v1/bookings` as a single unconfirmed call.
- **Wrapping the LangGraph agent in one MCP tool.** A model calling a model: twice the cost and delay, and this
  side would pay for the tokens.
- **Elicitation for the confirmation.** The protocol lets a tool ask the user a question, but the way to do it
  differs between protocol versions and not every client supports it. Two plain tools work with every client.
- **Seat holds on `prepare_booking`.** Kinder to the user, and it needs expiry, clean-up and a rule for abandoned
  holds. The confirmation checks the seats again instead.
- **The MCP server as its own process over the HTTP API.** Cleaner separation, one more thing to deploy. Mounted,
  it shares the controllers, the rate limit and the lifespan.
- **Soft-delete columns.** Nothing deletes a row, so there is nothing to mark.

## Consequences

- On Sunday night the week has few showtimes left, until Monday's publishing run.
- A prepared booking holds no seat, so a confirmation can be refused when someone else was faster.
- The chat agent reads the films once at its startup and needs a restart after a change of programme.
- Remote MCP clients need an API key given by hand. OAuth is not implemented.

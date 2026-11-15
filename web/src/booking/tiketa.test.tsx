import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, test, vi } from "vitest";
import { TiketaBooking } from "./TiketaBooking";

const AGENT_PORT = "8060";
const WEEK = {
  days: ["2026-11-09", "2026-11-10", "2026-11-11", "2026-11-12", "2026-11-13", "2026-11-14", "2026-11-15"],
  today: "2026-11-11",
  is_published: true,
};
const CINEMA = {
  name: "Tiketa Cinema",
  timezone: "Asia/Jakarta",
  now: "2026-11-11T03:00:00Z",
  now_local: "Wednesday 11 November 2026, 10:00 WIB",
  max_seats_per_booking: 8,
  week: WEEK,
};
const META = {
  id: "tiketa",
  name: "Tiketa",
  summary: "Cinema booking",
  version: "2.0.0",
  docs_path: "/docs",
  mcp_path: "/mcp",
};
const SHOWTIME = {
  id: 117,
  movie_id: 9,
  movie_title: "Dune: Part Two",
  studio_number: 9,
  starts_at: "2026-11-12T11:00:00Z",
  starts_at_local: "Thursday 12 November 2026, 18:00 WIB",
  price_idr: 45000,
  seats_left: 7,
};
const MOVIE = {
  id: 9,
  title: "Dune: Part Two",
  synopsis: "Paul Atreides joins the Fremen.",
  release_year: 2024,
  genres: ["Science fiction"],
  studio_number: 9,
  poster_url: null,
  trailer_youtube_id: null,
};
const SEATS = {
  showtime: SHOWTIME,
  rows: [
    { row: "A", seats: ["A1", "A2", "A3", "A4"].map((id) => ({ id, is_taken: id === "A4" })) },
    { row: "B", seats: ["B1", "B2", "B3", "B4"].map((id) => ({ id, is_taken: false })) },
  ],
  aisle_after_seat: 2,
  walkway_before_row: "B",
};
const SUMMARY = {
  showtime_id: 117,
  movie_title: "Dune: Part Two",
  starts_at: SHOWTIME.starts_at,
  starts_at_local: SHOWTIME.starts_at_local,
  studio_number: 9,
  seats: ["B1", "B2"],
  customer_name: "Rafi",
  price_per_seat_idr: 45000,
  total_price_idr: 90000,
};
const booking = (code: string, channel: "chat" | "web", seats: string[]) => ({
  code,
  channel,
  showtime: SHOWTIME,
  seats,
  customer_name: "Rafi",
  total_price_idr: 45000 * seats.length,
  created_at: "2026-11-11T03:00:00Z",
});

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
const events = (...items: unknown[]) =>
  new Response(items.map((item) => `data: ${JSON.stringify(item)}\n\n`).join(""), {
    headers: { "Content-Type": "text/event-stream" },
  });

interface Sent {
  service: "core" | "agent";
  method: string;
  path: string;
  body: unknown;
  headers: Headers;
  credentials: RequestCredentials;
}

/** Stands in for both services: the booking API, and the chat agent on its own port, which can be off. */
function serve(handle: (call: Sent) => Response | undefined, agentIsOn = true) {
  const sent: Sent[] = [];
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const request = input instanceof Request ? input : new Request(String(input), init);
      const url = new URL(request.url);
      const text = await request.clone().text();
      const call: Sent = {
        service: url.port === AGENT_PORT ? "agent" : "core",
        method: request.method,
        path: url.pathname,
        body: text ? JSON.parse(text) : undefined,
        headers: request.headers,
        credentials: request.credentials,
      };
      sent.push(call);
      if (call.service === "agent") {
        if (!agentIsOn) throw new TypeError("Failed to fetch");
        if (call.path === "/health") return json({ status: "ok" });
        if (call.path === "/v1/usage") return json({ used_tokens: 0, daily_tokens: 400000, resets_in_seconds: 3600 });
        if (call.path === "/v1/sessions" && call.method === "POST") return json({ session_id: "s1" }, 201);
      } else {
        if (call.path === "/auth/guest") return new Response(null, { status: 204 });
        if (call.path === "/v1/cinema") return json(CINEMA);
        if (call.path === "/meta") return json(META);
        if (call.path === "/v1/movies") return json([MOVIE]);
        if (call.path === "/v1/showtimes") return json([SHOWTIME]);
        if (call.path === "/v1/showtimes/117/seats") return json(SEATS);
      }
      return handle(call) ?? new Response("not found", { status: 404 });
    }),
  );
  return sent;
}

function renderScreen() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(
    <QueryClientProvider client={queryClient}>
      <TiketaBooking />
    </QueryClientProvider>,
  );
}

async function openSeatStep() {
  expect(screen.queryByRole("button", { name: "A1, free" })).not.toBeInTheDocument();
  await userEvent.click(await screen.findByRole("button", { name: /Dune: Part Two/ }));
  await userEvent.click(await screen.findByRole("button", { name: /18:00/ }));
}

beforeEach(() => {
  vi.stubGlobal(
    "ResizeObserver",
    class {
      observe() {}
      disconnect() {}
    },
  );
  window.localStorage.clear();
});

test("the form books the chosen seats once, with an idempotency key", async () => {
  let booked: string[] = [];
  const sent = serve((call) => {
    if (call.path === "/v1/bookings" && call.method === "GET")
      return json(booked.length ? [booking("TKFORM0001", "web", booked)] : []);
    if (call.path === "/v1/bookings" && call.method === "POST") {
      booked = (call.body as { seats: string[] }).seats;
      return json(booking("TKFORM0001", "web", booked), 201);
    }
    return undefined;
  });
  renderScreen();

  await openSeatStep();
  await userEvent.click(await screen.findByRole("button", { name: "A1, free" }));
  await userEvent.click(screen.getByRole("button", { name: "A2, free" }));
  expect(screen.getByRole("button", { name: "A4, taken" })).toBeDisabled();
  await userEvent.type(screen.getByLabelText("Name on the booking"), "Rafi");
  await userEvent.click(screen.getByRole("button", { name: "Book 2 seats" }));

  expect(await screen.findByText(/Booked/)).toHaveTextContent("Booked TKFORM0001: A1, A2 for Dune: Part Two");
  const post = sent.find((call) => call.path === "/v1/bookings" && call.method === "POST");
  expect(post?.body).toEqual({ showtime_id: 117, seats: ["A1", "A2"], customer_name: "Rafi", channel: "web" });
  expect(post?.headers.get("idempotency-key")).toMatch(/^[0-9a-f-]{36}$/);
  const toCore = sent.filter((call) => call.service === "core");
  expect(toCore[0]?.path).toBe("/auth/guest"); // the cookie comes before any call that needs it
  expect(toCore.filter((call) => call.path.startsWith("/v1")).every((call) => call.credentials === "include")).toBe(
    true,
  );
  const table = await screen.findByRole("table");
  expect(await within(table).findByText("Form")).toBeInTheDocument();
});

test("the week runs Monday to Sunday, and its days already past cannot be chosen", async () => {
  const sent = serve((call) => (call.path === "/v1/bookings" ? json([]) : undefined));
  renderScreen();

  await userEvent.click(await screen.findByRole("button", { name: /Dune: Part Two/ }));
  const today = await screen.findByRole("button", { name: /Today/ });
  expect(today).toHaveAttribute("aria-pressed", "true");
  expect(screen.getByRole("button", { name: /Mon.*9 Nov/ })).toBeDisabled();
  expect(screen.getByRole("button", { name: /Tue.*10 Nov/ })).toBeDisabled();
  const sunday = screen.getByRole("button", { name: /Sun.*15 Nov/ });
  expect(sunday).toBeEnabled();
  await userEvent.click(sunday);
  expect(sunday).toHaveAttribute("aria-pressed", "true");
  const days = sent.filter((call) => call.path === "/v1/showtimes");
  expect(days.length).toBeGreaterThan(0);
});

test("the chat's summary shows on the map and books only after Confirm", async () => {
  const sent = serve((call) => {
    if (call.path === "/v1/bookings") return json([]);
    if (call.path === "/v1/sessions/s1/messages") {
      return events(
        { type: "tool", name: "find_showtimes" },
        { type: "confirmation", data: SUMMARY },
        { type: "end", data: { model_calls: 2, input_tokens: 900, output_tokens: 40 } },
      );
    }
    if (call.path === "/v1/sessions/s1/confirmation") {
      return events(
        { type: "booking", data: booking("TKCHAT0001", "chat", ["B1", "B2"]) },
        { type: "message", text: "Sudah dipesan, kodenya TKCHAT0001." },
        { type: "end", data: { model_calls: 1, input_tokens: 300, output_tokens: 20 } },
      );
    }
    return undefined;
  });
  renderScreen();

  const message = await screen.findByLabelText("Message to the agent");
  await screen.findByText("Dune besok malam, 2 kursi tengah sebelahan"); // the conversation has started
  await userEvent.type(message, "dune besok jam 6, B1 B2, Rafi{Enter}");
  const summary = await screen.findByRole("region", { name: "Booking waiting for your answer" });
  expect(within(summary).getByText("B1, B2")).toBeInTheDocument();
  expect(within(summary).getByRole("img", { name: /Seat map preview for B1, B2/ })).toBeInTheDocument();
  expect(await screen.findByRole("button", { name: "B1, in the chat's summary" })).toBeInTheDocument();
  expect(sent.some((call) => call.path === "/v1/sessions/s1/confirmation")).toBe(false);

  await userEvent.click(within(summary).getByRole("button", { name: "Confirm booking" }));
  expect(await screen.findByText("TKCHAT0001")).toBeInTheDocument();
  expect(screen.getByText("Sudah dipesan, kodenya TKCHAT0001.")).toBeInTheDocument();
  const confirmation = sent.find((call) => call.path === "/v1/sessions/s1/confirmation");
  expect(confirmation?.service).toBe("agent");
  expect(confirmation?.body).toEqual({ approved: true });
});

test("with the agent off the chat says so and the form still books", async () => {
  const sent = serve((call) => {
    if (call.path === "/v1/bookings" && call.method === "GET") return json([]);
    if (call.path === "/v1/bookings" && call.method === "POST") return json(booking("TKFORM0002", "web", ["A1"]), 201);
    return undefined;
  }, false);
  renderScreen();

  expect(await screen.findByText(/The booking agent is off right now/)).toBeInTheDocument();
  expect(screen.getByLabelText("Message to the agent")).toBeDisabled();
  await openSeatStep();
  await userEvent.click(await screen.findByRole("button", { name: "A1, free" }));
  await userEvent.type(screen.getByLabelText("Name on the booking"), "Rafi");
  await userEvent.click(screen.getByRole("button", { name: "Book 1 seat" }));
  expect(await screen.findByText(/Booked/)).toHaveTextContent("Booked TKFORM0002");
  expect(sent.some((call) => call.service === "agent" && call.path.startsWith("/v1"))).toBe(false);
});

test("a visitor copies the instructions that connect their own assistant to the MCP server", async () => {
  serve((call) => (call.path === "/v1/bookings" ? json([]) : undefined));
  const user = userEvent.setup(); // gives the page a clipboard
  renderScreen();

  await user.click(await screen.findByRole("button", { name: "Copy instructions" }));
  expect(await screen.findByRole("button", { name: "Copied" })).toBeInTheDocument();
  const copied = await navigator.clipboard.readText();
  expect(copied).toContain("MCP server URL: http://localhost:8070/mcp/");
  expect(copied).toContain("claude mcp add --transport http tiketa http://localhost:8070/mcp/");
  expect(copied).toContain("this address is on my own computer");
});

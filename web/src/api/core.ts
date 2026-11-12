import createClient from "openapi-fetch";
import type { components, paths } from "./generated/core";

/** Where the booking API answers. Public, never a secret. An empty build argument means unset. */
export const CORE_URL = (
  (import.meta.env.VITE_TIKETA_API_URL as string | undefined) || "http://localhost:8070"
).replace(/\/$/, "");

let guestSession: Promise<void> | null = null;

/**
 * The browser's guest session: a signed HttpOnly cookie the booking API sets, which scripts here never see. It stands
 * in for an API key, which a browser must never hold. Started once, and again if the API no longer accepts it.
 */
function ensureGuest(): Promise<void> {
  guestSession ??= globalThis
    .fetch(`${CORE_URL}/auth/guest`, { method: "POST", credentials: "include" })
    .then((response) => {
      if (!response.ok) throw new Error(`Tiketa refused a guest session (${response.status})`);
    })
    .catch((error: unknown) => {
      guestSession = null; // the next request tries again
      throw error;
    });
  return guestSession;
}

/**
 * Sends a request with the guest cookie, starting the session first and once more if it has expired. The chat agent
 * accepts the same cookie, so its client sends through here too.
 */
export async function withGuest(send: () => Promise<Response>): Promise<Response> {
  await ensureGuest();
  const response = await send();
  if (response.status !== 401) return response;
  guestSession = null;
  await ensureGuest();
  return send();
}

/** Typed client for the booking API. Paths, bodies and responses come from its OpenAPI schema. */
export const core = createClient<paths>({
  baseUrl: CORE_URL,
  credentials: "include",
  fetch: (request) => withGuest(() => globalThis.fetch(request.clone())),
});

export type Movie = components["schemas"]["Movie"];
export type Showtime = components["schemas"]["Showtime"];
export type SeatMap = components["schemas"]["SeatMap"];
export type Booking = components["schemas"]["Booking"];
export type Cinema = components["schemas"]["Cinema"];

/** An answer a service refused, with its own words. */
export class TiketaError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

/** Raises with the service's own detail when it gave one, so a screen can say what failed. */
export function unwrap<T>(result: { data?: T; error?: unknown; response: Response }): T {
  if (result.data !== undefined) return result.data;
  throw new TiketaError(detailOf(result.error, result.response.status), result.response.status);
}

export function detailOf(body: unknown, status: number): string {
  const detail = (body as { detail?: unknown } | undefined)?.detail;
  if (typeof detail === "string") return detail;
  return status === 429 ? "Too many requests. Try again in a minute." : `Tiketa answered ${status}`;
}

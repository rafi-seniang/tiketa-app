import createClient from "openapi-fetch";
import { detailOf, TiketaError, withGuest } from "./core";
import type { components, paths } from "./generated/agent";

/**
 * Where the chat agent answers. It is a separate service that books through the booking API: when it is off, the
 * chat is off and everything else works. Public, never a secret.
 */
export const AGENT_URL = (
  (import.meta.env.VITE_TIKETA_AGENT_URL as string | undefined) || "http://localhost:8060"
).replace(/\/$/, "");

const HEALTH_TIMEOUT_MILLISECONDS = 2_500;

/** Whether the agent answers its health check. An agent that is off is an expected state, not an error. */
export async function isAgentAnswering(): Promise<boolean> {
  try {
    const response = await globalThis.fetch(`${AGENT_URL}/health`, {
      signal: AbortSignal.timeout(HEALTH_TIMEOUT_MILLISECONDS),
    });
    return response.ok;
  } catch {
    return false;
  }
}

/** Typed client for the chat agent. It reads the same guest cookie the booking API set. */
export const agent = createClient<paths>({
  baseUrl: AGENT_URL,
  credentials: "include",
  fetch: (request) => withGuest(() => globalThis.fetch(request.clone())),
});

export type BookingSummary = components["schemas"]["BookingSummary"];
export type TokenUsage = components["schemas"]["TokenUsageView"];
/** One server-sent event of a chat turn, as the agent's ChatEvent writes it. */
export interface ChatEvent {
  type: "token" | "tool" | "confirmation" | "booking" | "message" | "error" | "end";
  text?: string;
  name?: string;
  data?: Record<string, unknown>;
}

/**
 * Posts to a chat endpoint and hands each server-sent event to `onEvent` as it arrives. A refusal before the stream
 * starts (another turn running, the day's tokens used up) raises a TiketaError with the agent's detail.
 */
export async function streamTurn(
  path: string,
  body: Record<string, unknown>,
  onEvent: (event: ChatEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const response = await withGuest(() =>
    globalThis.fetch(`${AGENT_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
      body: JSON.stringify(body),
      credentials: "include",
      signal,
    }),
  );
  if (!response.ok || !response.body) {
    const error = await response.json().catch(() => undefined);
    throw new TiketaError(detailOf(error, response.status), response.status);
  }
  const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
  let buffer = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += value;
    let boundary = buffer.indexOf("\n\n");
    while (boundary !== -1) {
      const frame = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);
      const data = frame
        .split("\n")
        .filter((line) => line.startsWith("data:"))
        .map((line) => line.slice(5).trimStart())
        .join("\n");
      if (data) onEvent(JSON.parse(data) as ChatEvent);
      boundary = buffer.indexOf("\n\n");
    }
  }
}

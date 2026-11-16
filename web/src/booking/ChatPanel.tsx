import { type FormEvent, type KeyboardEvent, useEffect, useRef, useState } from "react";
import type { BookingSummary, TokenUsage } from "../api/agent";
import { freePrice, rupiah, whenLabel } from "./format";
import type { ChatLine } from "./useChat";

const STARTERS = [
  "Dune besok malam, 2 kursi tengah sebelahan",
  "Film apa aja yang main hari ini?",
  "Interstellar lusa, 3 kursi paling belakang dekat lorong",
];

/** on: the agent answers. off: it does not, and the seat map books as usual. checking: the first check is pending. */
export type AgentStatus = "on" | "off" | "checking";

const STATUS_WORDS: Record<AgentStatus, string> = { on: "On", off: "Off", checking: "Checking" };

interface SeatMapPreview {
  rows: ReadonlyArray<{ row: string; seats: ReadonlyArray<{ id: string; is_taken: boolean }> }>;
  aisle_after_seat: number;
  walkway_before_row: string;
}

// Drawn only from the showtime's real seat map, so a seat shown free is free
function SeatMiniMap({ seats, seatMap }: { seats: string[]; seatMap: SeatMapPreview }) {
  const chosen = new Set(seats);
  const rows = seatMap.rows;
  const aisleAfter = seatMap.aisle_after_seat;
  const walkwayBefore = seatMap.walkway_before_row;
  let y = 22;

  return (
    <svg
      className="tk-mini-map"
      viewBox="0 0 244 164"
      role="img"
      aria-label={`Seat map preview for ${seats.join(", ")}`}
    >
      <rect x={44} y={6} width={166} height={4} rx={2} fill="var(--seat-taken)" />
      <text x={127} y={17} textAnchor="middle" fontSize={7} fill="var(--muted)">
        SCREEN
      </text>
      {rows.map((row) => {
        if (row.row === walkwayBefore) y += 6;
        const rowY = y;
        y += 10;
        let x = 20;
        return (
          <g key={row.row}>
            <text x={9} y={rowY + 6.5} textAnchor="middle" fontSize={7} fill="var(--muted)">
              {row.row}
            </text>
            {row.seats.map((seat, index) => {
              const seatX = x;
              x += 11;
              if (index + 1 === aisleAfter) x += 10;
              const isMine = chosen.has(seat.id);
              const fill = isMine ? "var(--seat-mine)" : seat.is_taken ? "var(--seat-taken)" : "var(--surface)";
              const stroke = isMine || seat.is_taken ? "none" : "var(--control)";
              return (
                <rect
                  key={seat.id}
                  x={seatX}
                  y={rowY}
                  width={9}
                  height={8}
                  rx={1.5}
                  fill={fill}
                  stroke={stroke}
                  strokeWidth={0.8}
                />
              );
            })}
          </g>
        );
      })}
    </svg>
  );
}

interface ChatPanelProps {
  status: AgentStatus;
  lines: ChatLine[];
  pending: BookingSummary | null;
  pendingSeatMap?: SeatMapPreview;
  activity: string | null;
  busy: boolean;
  ready: boolean;
  startError: string | null;
  usage: TokenUsage | undefined;
  onSend: (text: string) => void;
  onAnswer: (approved: boolean) => void;
  onShowOnMap: (summary: BookingSummary) => void;
  onRestart: () => void;
  onClose: () => void;
}

const tokens = new Intl.NumberFormat("en-US");

export function ChatPanel(props: ChatPanelProps) {
  const { status, lines, pending, activity, busy, ready, startError, usage } = props;
  const [draft, setDraft] = useState("");
  const log = useRef<HTMLDivElement>(null);
  const lastText = lines.at(-1)?.text;

  // biome-ignore lint/correctness/useExhaustiveDependencies: follows the newest line and every streamed token
  useEffect(() => {
    log.current?.scrollTo?.({ top: log.current.scrollHeight });
  }, [lines.length, lastText, pending, activity]);

  const submit = (event?: FormEvent) => {
    event?.preventDefault();
    const text = draft.trim();
    if (!text || busy || !ready) return;
    props.onSend(text);
    setDraft("");
  };
  const onKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) submit(event);
  };

  return (
    <section className="tk-chat" aria-labelledby="tk-chat-title">
      <header className="tk-chat-head">
        <div>
          <h2 id="tk-chat-title">
            Ask the agent <span className={`pill${status === "on" ? " pos" : ""}`}>{STATUS_WORDS[status]}</span>
          </h2>
          <p className="tk-usage num">
            {status === "off"
              ? "The seat map books as usual"
              : usage
                ? `${tokens.format(usage.used_tokens)} of ${tokens.format(usage.daily_tokens)} tokens today`
                : "Tokens today -"}
          </p>
          <p className="tk-chat-demo">Demo: every ticket is free</p>
        </div>
        <div className="tk-chat-actions">
          <button type="button" className="btn ghost" onClick={props.onRestart} disabled={busy || status !== "on"}>
            New chat
          </button>
          <button type="button" className="btn ghost" onClick={props.onClose}>
            Close
          </button>
        </div>
      </header>

      <div className="tk-log" ref={log} aria-live="polite">
        {status === "off" && (
          <div className="tk-intro">
            <p>The booking agent is off right now. It is a separate service, and the cinema runs without it.</p>
            <p>Choose a film, a time and your seats on the seat map. The chat comes back when the agent does.</p>
          </div>
        )}
        {status === "on" && startError && (
          <div className="error">
            <p>The chat could not start: {startError}</p>
            <button type="button" className="btn" onClick={props.onRestart}>
              Retry
            </button>
          </div>
        )}
        {status === "on" && !startError && lines.length === 0 && (
          <div className="tk-starters">
            <div className="tk-intro">
              <p>
                Ask in Indonesian or English, all at once or one step at a time. The agent reads the same showtimes and
                seat map as the site, and works out dates like besok or malam minggu from today in Jakarta.
              </p>
              <p>
                Nothing is booked until you confirm the summary it shows. This is a demo cinema: the prices are what a
                ticket would cost, and nothing is ever paid.
              </p>
            </div>
            {STARTERS.map((starter) => (
              <button
                key={starter}
                type="button"
                className="tk-starter"
                disabled={!ready}
                onClick={() => props.onSend(starter)}
              >
                {starter}
              </button>
            ))}
          </div>
        )}
        {lines.map((item) => {
          if (item.role === "booking" && item.booking) {
            const { booking } = item;
            return (
              <div key={item.id} className="tk-ticket" data-channel="chat">
                <strong className="tk-code">{booking.code}</strong>
                <span>
                  {booking.showtime.movie_title}, {whenLabel(booking.showtime.starts_at)}
                </span>
                <span className="num">
                  {booking.seats.join(", ")} · {freePrice(booking.total_price_idr)}
                </span>
              </div>
            );
          }
          return (
            <p key={item.id} className="tk-line" data-role={item.role}>
              {item.text}
            </p>
          );
        })}
        {activity && (
          <p className="tk-activity" role="status">
            {activity}
          </p>
        )}
      </div>

      {pending && (
        <section className="tk-summary" aria-label="Booking waiting for your answer">
          <div className="tk-summary-body">
            <div className="tk-summary-top">
              <strong>{pending.movie_title}</strong>
              {pending.showtime_id != null && (
                <button type="button" className="tk-link" onClick={() => props.onShowOnMap(pending)}>
                  Show on the seat map
                </button>
              )}
            </div>
            <dl>
              <div>
                <dt>When</dt>
                <dd>{whenLabel(pending.starts_at)}</dd>
              </div>
              <div>
                <dt>Studio</dt>
                <dd className="num">{pending.studio_number}</dd>
              </div>
              <div>
                <dt>Seats</dt>
                <dd className="num">{pending.seats.join(", ")}</dd>
              </div>
              <div>
                <dt>Name</dt>
                <dd>{pending.customer_name}</dd>
              </div>
              <div>
                <dt>Total</dt>
                <dd className="num">
                  {pending.seats.length} x {rupiah(pending.price_per_seat_idr)} ={" "}
                  <b>{freePrice(pending.total_price_idr)}</b>
                </dd>
              </div>
            </dl>
            {props.pendingSeatMap && <SeatMiniMap seats={pending.seats} seatMap={props.pendingSeatMap} />}
          </div>
          <div className="tk-summary-actions">
            <button type="button" className="btn primary" disabled={busy} onClick={() => props.onAnswer(true)}>
              Confirm booking
            </button>
            <button type="button" className="btn" disabled={busy} onClick={() => props.onAnswer(false)}>
              Cancel
            </button>
          </div>
        </section>
      )}

      <form className="tk-composer" onSubmit={submit}>
        <label className="visually-hidden" htmlFor="tk-message">
          Message to the agent
        </label>
        <textarea
          id="tk-message"
          rows={2}
          maxLength={2000}
          placeholder={pending ? "Or type a change, for example: ganti ke E7 dan E8" : "Mau nonton apa?"}
          disabled={status !== "on"}
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={onKeyDown}
        />
        <button type="submit" className="btn" disabled={!ready || busy || draft.trim() === ""}>
          Send
        </button>
      </form>
    </section>
  );
}

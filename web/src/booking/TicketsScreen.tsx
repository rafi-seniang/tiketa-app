import type { Booking } from "../api/core";
import { rupiah, whenLabel } from "./format";
import { useBookings } from "./queries";
import { Link } from "./router";

const CHANNEL_WORDS: Record<Booking["channel"], string> = { web: "Seat map", chat: "Chat agent", mcp: "Own AI (MCP)" };

/** Every booking this visitor made, from the seat map, the chat agent or their own assistant, with its code. */
export function TicketsScreen() {
  const bookings = useBookings();
  const list = bookings.data ?? [];
  const total = list.reduce((sum, booking) => sum + booking.total_price_idr, 0);

  return (
    <div className="tk-tickets-page">
      <header className="tk-page-head">
        <h1>My tickets</h1>
        <p className="num">
          {bookings.isPending
            ? "Loading your bookings."
            : list.length === 0
              ? "No bookings yet."
              : `${list.length} ${list.length === 1 ? "booking" : "bookings"}, ${rupiah(total)} to pay at the counter with each code.`}
        </p>
      </header>
      {bookings.isError ? (
        <p className="error">The bookings could not load: {bookings.error.message}</p>
      ) : bookings.isPending ? (
        <div className="tk-ticket-list-loading" aria-hidden="true" />
      ) : list.length === 0 ? (
        <p className="empty">
          Bookings from the seat map, the chat agent and your own AI all land here, each with its code.{" "}
          <Link to={{ name: "home" }}>Choose a film</Link>
        </p>
      ) : (
        <ul className="tk-ticket-list" aria-label="Bookings">
          {list.map((booking) => (
            <li key={booking.code} className="tk-stub">
              <strong className="tk-code">{booking.code}</strong>
              <div className="tk-stub-film">
                <span>{booking.showtime.movie_title}</span>
                <span>
                  {whenLabel(booking.showtime.starts_at)}, studio {booking.showtime.studio_number}
                </span>
              </div>
              <div className="tk-stub-seats num">
                <span>{booking.seats.join(", ")}</span>
                <span>{booking.customer_name}</span>
              </div>
              <div className="tk-stub-pay num">
                <span>{rupiah(booking.total_price_idr)}</span>
                <span>{CHANNEL_WORDS[booking.channel]}</span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

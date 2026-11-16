import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type FormEvent, useEffect, useRef, useState } from "react";
import { type Booking, core, type SeatMap as SeatMapData, TiketaError, unwrap } from "../api/core";
import { cinemaDay, freePrice, rupiah, whenLabel } from "./format";
import { fetchSeats, keys, useCinema } from "./queries";
import { Link } from "./router";
import { SeatMap, SeatMapPlaceholder } from "./SeatMap";

const MAX_SEATS_UNTIL_KNOWN = 8; // the API's own limit arrives with /v1/cinema, and it refuses more either way
const SEAT_REFRESH_MS = 10_000;
const NAME_KEY = "tiketa.name";

function storedName(): string {
  try {
    return window.localStorage.getItem(NAME_KEY) ?? "";
  } catch {
    return "";
  }
}

function rememberName(name: string) {
  try {
    window.localStorage.setItem(NAME_KEY, name);
  } catch {
    // private window: the name is asked again next time
  }
}

type Notice = { kind: "booked"; booking: Booking } | { kind: "refused"; text: string };

const takenIn = (map: SeatMapData) =>
  new Set(map.rows.flatMap((row) => row.seats.filter((seat) => seat.is_taken).map((seat) => seat.id)));

/** One showtime's room: choose seats on the map, name the booking, book. Seats refresh every 10 seconds. */
export function SeatsScreen({ id, heldByChat }: { id: number; heldByChat: string[] }) {
  const queryClient = useQueryClient();
  const cinema = useCinema();
  const maxSeats = cinema.data?.max_seats_per_booking ?? MAX_SEATS_UNTIL_KNOWN;
  const seats = useQuery({
    queryKey: keys.seats(id),
    queryFn: () => fetchSeats(id),
    staleTime: 5_000,
    refetchInterval: SEAT_REFRESH_MS,
  });
  const map = seats.data;
  const [selected, setSelected] = useState<string[]>([]);
  const [name, setName] = useState(storedName);
  const [notice, setNotice] = useState<Notice | null>(null);
  const [zoomed, setZoomed] = useState(false); // phones only: seats at thumb size, the room scrolls sideways
  const attempt = useRef({ signature: "", key: "" });

  // Seats someone else took while they were selected here leave the selection, with a word about it
  useEffect(() => {
    if (!map || selected.length === 0) return;
    const taken = takenIn(map);
    const lost = selected.filter((seatId) => taken.has(seatId));
    if (lost.length === 0) return;
    setSelected(selected.filter((seatId) => !taken.has(seatId)));
    setNotice({ kind: "refused", text: `${lost.join(", ")} just went to someone else.` });
  }, [map, selected]);

  const book = useMutation({
    mutationFn: async (key: string) =>
      unwrap(
        await core.POST("/v1/bookings", {
          body: { showtime_id: id, seats: selected, customer_name: name.trim(), channel: "web" },
          params: { header: { "idempotency-key": key } },
        }),
      ),
    onSuccess: (booking) => {
      setNotice({ kind: "booked", booking });
      setSelected([]);
      rememberName(name.trim());
      queryClient.setQueryData<SeatMapData>(keys.seats(id), (old) =>
        old
          ? {
              ...old,
              rows: old.rows.map((row) => ({
                ...row,
                seats: row.seats.map((seat) => (booking.seats.includes(seat.id) ? { ...seat, is_taken: true } : seat)),
              })),
            }
          : old,
      );
      void queryClient.invalidateQueries({ queryKey: keys.seats(id) });
      void queryClient.invalidateQueries({ queryKey: keys.showtimes(cinemaDay(booking.showtime.starts_at)) });
      void queryClient.invalidateQueries({ queryKey: keys.bookings });
    },
    onError: (error) => {
      setNotice({ kind: "refused", text: error instanceof TiketaError ? error.message : "Tiketa did not answer." });
      void queryClient.invalidateQueries({ queryKey: keys.seats(id) });
    },
  });

  const toggle = (seatId: string) => {
    setNotice(null);
    setSelected((current) =>
      current.includes(seatId)
        ? current.filter((seat) => seat !== seatId)
        : current.length >= maxSeats
          ? current
          : [...current, seatId],
    );
  };

  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (selected.length === 0 || name.trim() === "" || book.isPending) return;
    // A retry of the same choice reuses its key, so a lost response can never book twice
    const signature = `${id}|${selected.join(",")}|${name.trim()}`;
    if (attempt.current.signature !== signature) attempt.current = { signature, key: crypto.randomUUID() };
    book.mutate(attempt.current.key);
  };

  if (seats.isError) {
    return (
      <div className="error">
        <p>The seats could not load: {seats.error.message}</p>
        <button type="button" className="btn" onClick={() => void seats.refetch()}>
          Retry
        </button>
      </div>
    );
  }

  const showtime = map?.showtime;
  const total = map ? map.rows.reduce((sum, row) => sum + row.seats.length, 0) : 0;
  const free = map ? total - takenIn(map).size : 0;
  const price = showtime?.price_idr ?? 0;

  return (
    <div className="tk-seats-page">
      {showtime ? (
        <Link to={{ name: "film", id: showtime.movie_id }} className="tk-back">
          {showtime.movie_title}, other times
        </Link>
      ) : (
        <Link to={{ name: "home" }} className="tk-back">
          All films
        </Link>
      )}
      <header className="tk-page-head">
        <h1>{showtime ? showtime.movie_title : "Choose your seats"}</h1>
        <p className="num">
          {showtime
            ? `${whenLabel(showtime.starts_at)}, studio ${showtime.studio_number}. ${free} of ${total} seats free.`
            : "Loading the room."}
        </p>
      </header>

      <div className="tk-seats-layout">
        <section className="tk-seats" aria-labelledby="tk-seats-title">
          <header className="tk-section-head">
            <h2 id="tk-seats-title">Choose seats</h2>
            <ul className="tk-legend">
              <li data-state="free">Free</li>
              <li data-state="taken">Taken (point at it for the initial)</li>
              <li data-state="mine">Yours</li>
              {heldByChat.length > 0 && <li data-state="held">In the chat's summary</li>}
            </ul>
            <button type="button" className="btn tk-zoom" aria-pressed={zoomed} onClick={() => setZoomed(!zoomed)}>
              {zoomed ? "Fit to screen" : "Zoom in"}
            </button>
          </header>
          {map ? (
            <SeatMap
              zoomed={zoomed}
              map={map}
              selected={selected}
              heldByChat={heldByChat}
              full={selected.length >= maxSeats}
              onToggle={toggle}
            />
          ) : (
            <SeatMapPlaceholder />
          )}
        </section>

        <aside className="tk-checkout-col" aria-label="Your booking">
          <form className="tk-checkout" data-active={selected.length > 0} onSubmit={submit}>
            <div className="tk-choice">
              <span className="tk-choice-seats num">
                {selected.length === 0 ? "No seats chosen" : selected.join(", ")}
              </span>
              <span className="tk-choice-total num">
                {selected.length === 0
                  ? `Up to ${maxSeats} seats, ${price ? freePrice(price) : "-"} each`
                  : `${selected.length} x ${rupiah(price)} = `}
                {selected.length > 0 && <b>{freePrice(selected.length * price)}</b>}
              </span>
            </div>
            <div className="field tk-name">
              <label htmlFor="tk-name">Name on the booking</label>
              <input
                id="tk-name"
                className="input"
                value={name}
                maxLength={80}
                autoComplete="name"
                onChange={(event) => setName(event.target.value)}
              />
            </div>
            <button
              type="submit"
              className="btn primary tk-book"
              disabled={selected.length === 0 || name.trim() === "" || book.isPending}
            >
              {book.isPending
                ? "Booking"
                : selected.length > 0
                  ? `Book ${selected.length} ${selected.length === 1 ? "seat" : "seats"}`
                  : "Book"}
            </button>
          </form>
          {notice?.kind === "booked" && (
            <p className="tk-notice" data-kind="booked" role="status">
              Booked <strong className="tk-code">{notice.booking.code}</strong>: {notice.booking.seats.join(", ")} for{" "}
              {notice.booking.showtime.movie_title}, {whenLabel(notice.booking.showtime.starts_at)}. Free in this demo:
              show the code at the counter. <Link to={{ name: "tickets" }}>See my tickets</Link>
            </p>
          )}
          {notice?.kind === "refused" && (
            <p className="tk-notice" data-kind="refused" role="alert">
              {notice.text}
            </p>
          )}
        </aside>
      </div>
    </div>
  );
}

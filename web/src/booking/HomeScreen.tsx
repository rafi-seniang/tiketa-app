import { type FormEvent, useState } from "react";
import type { Showtime } from "../api/core";
import type { AgentStatus } from "./ChatPanel";
import { FeaturedFilm } from "./FeaturedFilm";
import { clockTime, weekDays } from "./format";
import { Poster } from "./Poster";
import { useCinema, useMovies, useShowtimes } from "./queries";
import { Link } from "./router";

const NEXT_SHOWN = 3;

/** Now showing: every film with today's next showings, and the agent's one-sentence way in above them. */
export function HomeScreen({
  agentStatus,
  ready,
  onAsk,
}: {
  agentStatus: AgentStatus;
  ready: boolean;
  onAsk: (text: string) => void;
}) {
  const cinema = useCinema();
  const movies = useMovies();
  const today = cinema.data?.week.today ?? "";
  const showtimes = useShowtimes(today);
  const [draft, setDraft] = useState("");
  const days = cinema.data ? weekDays(cinema.data.week) : [];
  const todayLabel = days.find((day) => day.isToday)?.date;

  const byFilm = new Map<number, Showtime[]>();
  for (const showtime of showtimes.data ?? []) {
    byFilm.set(showtime.movie_id, [...(byFilm.get(showtime.movie_id) ?? []), showtime]);
  }
  // Films still showing today come first, the soonest first; the rest keep the catalogue's order
  const films = [...(movies.data ?? [])].sort((a, b) => {
    const nextA = byFilm.get(a.id)?.[0]?.starts_at ?? "~";
    const nextB = byFilm.get(b.id)?.[0]?.starts_at ?? "~";
    return nextA < nextB ? -1 : nextA > nextB ? 1 : 0;
  });
  const showingsToday = showtimes.data?.length ?? 0;
  // The featured film changes with the day, among the films that still show today and have a wide still
  const candidates = films.filter((movie) => movie.backdrop_url && byFilm.has(movie.id));
  const featured = candidates.length > 0 ? candidates[Number(today.slice(-2)) % candidates.length] : undefined;

  const ask = (event: FormEvent) => {
    event.preventDefault();
    const text = draft.trim();
    if (!text || !ready) return;
    onAsk(text);
    setDraft("");
  };

  return (
    <div className="tk-home">
      <header className="tk-page-head">
        <h1>Now showing</h1>
        <p>
          {cinema.data
            ? `${cinema.data.name}, Jakarta. This week runs ${days[0]?.date} to ${days.at(-1)?.date}, times in WIB.`
            : "Tiketa Cinema, Jakarta. Times in WIB."}
        </p>
        <p className="tk-demo-note">
          A demo cinema. Prices show what a ticket would cost, and every ticket is free: nothing is ever paid.
        </p>
      </header>

      {featured && <FeaturedFilm movie={featured} times={byFilm.get(featured.id) ?? []} />}

      <form className="tk-ask" onSubmit={ask} aria-labelledby="tk-ask-title">
        <h2 id="tk-ask-title">Book in one sentence</h2>
        <p>
          {agentStatus === "off"
            ? "The booking agent is off right now. Choose a film below and book on the seat map."
            : "Tell the agent the film, the day and the seats, in Indonesian or English. It shows a summary before anything is booked."}
        </p>
        <div className="tk-ask-row">
          <label className="visually-hidden" htmlFor="tk-ask-input">
            What to book
          </label>
          <input
            id="tk-ask-input"
            className="input"
            maxLength={2000}
            placeholder="Dune besok malam, 2 kursi tengah sebelahan"
            value={draft}
            disabled={agentStatus === "off"}
            onChange={(event) => setDraft(event.target.value)}
          />
          <button type="submit" className="btn primary" disabled={!ready || draft.trim() === ""}>
            Ask the agent
          </button>
        </div>
      </form>

      <section className="tk-films" aria-labelledby="tk-films-title">
        <header className="tk-section-head">
          <h2 id="tk-films-title">Today{todayLabel ? `, ${todayLabel}` : ""}</h2>
          <span className="num">
            {movies.data ? `${movies.data.length} films, ${showingsToday} showings left today` : ""}
          </span>
        </header>
        {movies.isError ? (
          <p className="error">The films could not load: {movies.error.message}</p>
        ) : movies.isPending ? (
          <div className="tk-posters-loading" aria-hidden="true" />
        ) : (
          <ul className="tk-posters">
            {films.map((movie) => {
              const next = byFilm.get(movie.id) ?? [];
              return (
                <li key={movie.id} className="tk-film">
                  <Link to={{ name: "film", id: movie.id }} className="tk-film-link">
                    <Poster movie={movie} width={185} />
                    <span className="tk-film-title">{movie.title}</span>
                    <span className="tk-film-meta">
                      {movie.release_year} · {movie.genres.slice(0, 2).join(", ")}
                    </span>
                  </Link>
                  {next.length > 0 ? (
                    <ul className="tk-film-times" aria-label={`Next showings of ${movie.title}`}>
                      {next.slice(0, NEXT_SHOWN).map((showtime) => (
                        <li key={showtime.id}>
                          <Link to={{ name: "seats", id: showtime.id }} className="tk-time-chip num">
                            {clockTime(showtime.starts_at)}
                          </Link>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="tk-film-none">No more showings today</p>
                  )}
                </li>
              );
            })}
          </ul>
        )}
      </section>
    </div>
  );
}

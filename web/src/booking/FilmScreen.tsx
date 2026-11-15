import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { clockTime, rupiah, weekDays } from "./format";
import { Poster } from "./Poster";
import { fetchShowtimes, keys, useCinema, useMovies, useShowtimes } from "./queries";
import { Link } from "./router";

/** One film: its poster, story and trailer, and its showtimes across the week on sale. */
export function FilmScreen({ id }: { id: number }) {
  const queryClient = useQueryClient();
  const cinema = useCinema();
  const movies = useMovies();
  const movie = movies.data?.find((candidate) => candidate.id === id);
  const days = cinema.data ? weekDays(cinema.data.week) : [];
  const [chosenDay, setDay] = useState<string | null>(null);
  const day = chosenDay ?? cinema.data?.week.today ?? "";
  const showtimes = useShowtimes(day);
  const times = showtimes.data?.filter((showtime) => showtime.movie_id === id) ?? [];
  const nextDay = days.find((option) => option.day > day);

  // The other days load in the background, so switching days is instant
  useEffect(() => {
    for (const { day: other } of days.filter((option) => !option.isPast && !option.isToday)) {
      void queryClient.prefetchQuery({
        queryKey: keys.showtimes(other),
        queryFn: () => fetchShowtimes(other),
        staleTime: 30_000,
      });
    }
  }, [days, queryClient]);

  if (movies.isError) return <p className="error">The film could not load: {movies.error.message}</p>;
  if (movies.isPending) return <div className="tk-film-head tk-film-head-loading" aria-hidden="true" />;
  if (!movie) {
    return (
      <div className="tk-page-head">
        <h1>No such film</h1>
        <p>
          It is not showing here. <Link to={{ name: "home" }}>See the films now showing</Link>
        </p>
      </div>
    );
  }

  return (
    <div className="tk-film-page">
      <Link to={{ name: "home" }} className="tk-back">
        All films
      </Link>
      <article className="tk-film-head">
        <Poster movie={movie} width={342} />
        <div className="tk-film-main">
          <div className="tk-film-about">
            <h1>{movie.title}</h1>
            <p className="tk-film-facts">
              {movie.release_year} · {movie.genres.join(", ")} · Studio {movie.studio_number}
            </p>
            <p className="tk-synopsis">{movie.synopsis}</p>
            {movie.trailer_youtube_id && (
              <a
                className="btn"
                href={`https://www.youtube.com/watch?v=${movie.trailer_youtube_id}`}
                target="_blank"
                rel="noreferrer"
              >
                Watch the trailer
              </a>
            )}
          </div>

          <section className="tk-showtimes" aria-labelledby="tk-showtimes-title">
            <header className="tk-section-head">
              <h2 id="tk-showtimes-title">Showtimes</h2>
              <span>Studio {movie.studio_number}, times in WIB</span>
            </header>
            <fieldset className="tk-days">
              <legend className="visually-hidden">Day</legend>
              {days.map((option) => (
                <button
                  key={option.day}
                  type="button"
                  disabled={option.isPast}
                  aria-pressed={option.day === day}
                  onClick={() => setDay(option.day)}
                >
                  <span>{option.weekday}</span>
                  <span className="num">{option.date}</span>
                </button>
              ))}
            </fieldset>
            {showtimes.isError ? (
              <p className="error">The showtimes could not load: {showtimes.error.message}</p>
            ) : showtimes.isPending ? (
              <div className="tk-times tk-times-loading" aria-hidden="true" />
            ) : times.length === 0 ? (
              <p className="empty">
                No more showings of {movie.title} on this day.{" "}
                {nextDay ? (
                  <button type="button" className="tk-link" onClick={() => setDay(nextDay.day)}>
                    See {nextDay.weekday} {nextDay.date}
                  </button>
                ) : (
                  "Next week's showtimes open on Monday."
                )}
              </p>
            ) : (
              <ul className="tk-times">
                {times.map((showtime) => (
                  <li key={showtime.id}>
                    <Link to={{ name: "seats", id: showtime.id }} className="tk-time">
                      <strong className="num">{clockTime(showtime.starts_at)}</strong>
                      <span className="num">{rupiah(showtime.price_idr)}</span>
                      <span className="num" data-low={showtime.seats_left <= 20 || undefined}>
                        {showtime.seats_left} seats left
                      </span>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>
      </article>
    </div>
  );
}

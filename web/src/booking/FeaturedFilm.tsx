import type { Movie, Showtime } from "../api/core";
import { backdropAt, clockTime, freePrice } from "./format";
import { Link } from "./router";

/** Today's featured film: its wide still, its story and every showing still to come today, one click from the seats. */
export function FeaturedFilm({ movie, times }: { movie: Movie; times: Showtime[] }) {
  const backdrop = backdropAt(movie);
  return (
    <section className="tk-feature" aria-labelledby="tk-feature-title">
      {backdrop && (
        <Link to={{ name: "film", id: movie.id }} className="tk-feature-still" tabIndex={-1} aria-hidden="true">
          <img src={backdrop} alt="" width={1280} height={720} decoding="async" fetchPriority="high" />
        </Link>
      )}
      <div className="tk-feature-about">
        <p className="tk-feature-when">Featured today, studio {movie.studio_number}</p>
        <h2 id="tk-feature-title">{movie.title}</h2>
        <p className="tk-film-facts">
          {movie.release_year} · {movie.genres.join(", ")}
          {times[0] ? ` · ${freePrice(times[0].price_idr)}` : ""}
        </p>
        <p className="tk-feature-story">{movie.synopsis}</p>
        <ul className="tk-film-times" aria-label={`Showings of ${movie.title} today`}>
          {times.map((showtime) => (
            <li key={showtime.id}>
              <Link to={{ name: "seats", id: showtime.id }} className="tk-time-chip num">
                {clockTime(showtime.starts_at)}
              </Link>
            </li>
          ))}
        </ul>
        <Link to={{ name: "film", id: movie.id }} className="btn">
          Showtimes this week
        </Link>
      </div>
    </section>
  );
}

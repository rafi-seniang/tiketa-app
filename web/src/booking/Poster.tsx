import { useState } from "react";
import type { Movie } from "../api/core";
import { posterAt } from "./format";

/** The film's poster at the width it is shown, or its title set as type when there is none. */
export function Poster({ movie, width }: { movie: Movie; width: number }) {
  const [failed, setFailed] = useState(false);
  const source = posterAt(movie, width);
  if (!source || failed) {
    return (
      <span className="tk-poster tk-poster-type" aria-hidden="true">
        {movie.title}
      </span>
    );
  }
  return (
    <img
      className="tk-poster"
      src={source}
      alt=""
      width={width}
      height={Math.round(width * 1.5)}
      decoding="async"
      loading="lazy"
      onError={() => setFailed(true)}
    />
  );
}

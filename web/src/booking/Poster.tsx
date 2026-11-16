import { useState } from "react";
import type { Movie } from "../api/core";
import { posterAt } from "./format";

/**
 * The film's poster at the width it is shown, or its title set as type when there is none. The poster column can
 * run a little wider than `width`, and most screens have two pixels to a point, so the browser picks from 1.5x and 2x.
 */
export function Poster({ movie, width }: { movie: Movie; width: number }) {
  const [failed, setFailed] = useState(false);
  const source = posterAt(movie, Math.round(width * 1.5));
  const sharp = posterAt(movie, width * 2);
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
      srcSet={sharp && sharp !== source ? `${source} 1x, ${sharp} 2x` : undefined}
      alt=""
      width={width}
      height={Math.round(width * 1.5)}
      decoding="async"
      loading="lazy"
      onError={() => setFailed(true)}
    />
  );
}

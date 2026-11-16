import type { Cinema, Movie } from "../api/core";

/** The cinema's clock. Showtimes come in UTC and are shown, and grouped into days, in Jakarta time. */
export const CINEMA_TIMEZONE = "Asia/Jakarta";

const rupiahFormat = new Intl.NumberFormat("id-ID");
const timeFormat = new Intl.DateTimeFormat("en-GB", { timeZone: CINEMA_TIMEZONE, hour: "2-digit", minute: "2-digit" });
const dayFormat = new Intl.DateTimeFormat("en-GB", {
  timeZone: CINEMA_TIMEZONE,
  weekday: "short",
  day: "numeric",
  month: "short",
});
const isoDayFormat = new Intl.DateTimeFormat("en-CA", { timeZone: CINEMA_TIMEZONE });

export const rupiah = (amount: number) => `Rp${rupiahFormat.format(amount)}`;
/** Every price on the demo site: what a ticket would cost, and that it costs nothing here. */
export const freePrice = (amount: number) => `${rupiah(amount)} (free)`;
export const clockTime = (iso: string) => timeFormat.format(new Date(iso));
export const dayLabel = (iso: string) => dayFormat.format(new Date(iso));
export const whenLabel = (iso: string) => `${dayLabel(iso)}, ${clockTime(iso)} WIB`;
/** The cinema day (YYYY-MM-DD in Jakarta) a moment falls on. */
export const cinemaDay = (iso: string) => isoDayFormat.format(new Date(iso));

export interface WeekDay {
  day: string;
  weekday: string;
  date: string;
  isToday: boolean;
  isPast: boolean;
}

/** The week on sale as the booking API gives it, Monday to Sunday, each day with a short label. */
export function weekDays(week: Cinema["week"]): WeekDay[] {
  return week.days.map((day) => {
    const noon = new Date(`${day}T12:00:00+07:00`); // any moment of that day in Jakarta
    const parts = Object.fromEntries(dayFormat.formatToParts(noon).map((part) => [part.type, part.value]));
    return {
      day,
      weekday: day === week.today ? "Today" : (parts.weekday ?? ""),
      date: `${parts.day} ${parts.month}`,
      isToday: day === week.today,
      isPast: day < week.today, // YYYY-MM-DD compares as text
    };
  });
}

// The widths TMDB serves a poster at, short of the original (1 to 3 MB each)
const TMDB_POSTER_WIDTHS = [185, 342, 500, 780];

/** A poster file at least `pixels` wide, the smallest that is, so it stays sharp without the full original. */
export function posterAt(movie: Movie, pixels: number): string | null {
  const url = movie.poster_url;
  if (!url) return null;
  if (url.includes("image.tmdb.org")) {
    const size = TMDB_POSTER_WIDTHS.find((width) => width >= pixels) ?? 780;
    return url.replace("/original/", `/w${size}/`);
  }
  if (url.includes("images.weserv.nl")) return `${url}&w=${pixels}&h=${Math.round(pixels * 1.5)}&fit=cover&output=webp`;
  return url;
}

/** A film's wide still for the banner, at 1280px wide (TMDB's originals run to several megabytes). */
export function backdropAt(movie: Movie): string | null {
  const url = movie.backdrop_url;
  if (!url) return null;
  return url.includes("image.tmdb.org") ? url.replace("/original/", "/w1280/") : url;
}

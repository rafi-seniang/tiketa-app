import { useQuery } from "@tanstack/react-query";
import { core, unwrap } from "../api/core";

/** Every screen reads the cinema through these, so a booking anywhere refreshes the same cached data. */
export const keys = {
  cinema: ["tiketa", "cinema"] as const,
  meta: ["tiketa", "meta"] as const,
  agent: ["tiketa", "agent"] as const,
  movies: ["tiketa", "movies"] as const,
  showtimes: (day: string) => ["tiketa", "showtimes", day] as const,
  seats: (showtimeId: number) => ["tiketa", "seats", showtimeId] as const,
  bookings: ["tiketa", "bookings"] as const,
  usage: ["tiketa", "usage"] as const,
};

export const fetchShowtimes = async (day: string) =>
  unwrap(await core.GET("/v1/showtimes", { params: { query: { day } } }));
export const fetchSeats = async (showtimeId: number) =>
  unwrap(await core.GET("/v1/showtimes/{showtime_id}/seats", { params: { path: { showtime_id: showtimeId } } }));

export const useCinema = () =>
  useQuery({ queryKey: keys.cinema, queryFn: async () => unwrap(await core.GET("/v1/cinema")) });

export const useMovies = () =>
  useQuery({
    queryKey: keys.movies,
    queryFn: async () => unwrap(await core.GET("/v1/movies")),
    staleTime: Number.POSITIVE_INFINITY,
  });

export const useShowtimes = (day: string) =>
  useQuery({
    queryKey: keys.showtimes(day),
    queryFn: () => fetchShowtimes(day),
    enabled: day !== "",
    staleTime: 30_000,
  });

export const useBookings = () =>
  useQuery({ queryKey: keys.bookings, queryFn: async () => unwrap(await core.GET("/v1/bookings")) });

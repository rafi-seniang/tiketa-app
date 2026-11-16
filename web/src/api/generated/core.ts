/** Generated from the service's OpenAPI schema by scripts/generate-api-types.mjs. Do not edit. */
export interface paths {
  "/health": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Health */
    get: operations["health_health_get"];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/meta": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Meta */
    get: operations["meta_meta_get"];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/auth/guest": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /**
     * Start Guest Session
     * @description Sets a signed guest session cookie, or keeps the one the browser already has while it is valid.
     */
    post: operations["start_guest_session_auth_guest_post"];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/v1/cinema": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /**
     * Cinema
     * @description The cinema's name, clock and rules, and the week on sale (Monday to Sunday).
     */
    get: operations["cinema_v1_cinema_get"];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/v1/me": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /**
     * Me
     * @description How the service names the caller. The chat agent asks this to know whose conversation it holds.
     */
    get: operations["me_v1_me_get"];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/v1/movies": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** List Movies */
    get: operations["list_movies_v1_movies_get"];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/v1/movies/{movie_id}": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Get Movie */
    get: operations["get_movie_v1_movies__movie_id__get"];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/v1/showtimes": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /**
     * List Showtimes
     * @description Showtimes on a cinema-local day that have not started yet.
     */
    get: operations["list_showtimes_v1_showtimes_get"];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/v1/showtimes/{showtime_id}": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Get Showtime */
    get: operations["get_showtime_v1_showtimes__showtime_id__get"];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/v1/showtimes/{showtime_id}/seats": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Seat Map */
    get: operations["seat_map_v1_showtimes__showtime_id__seats_get"];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/v1/bookings": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /**
     * My Bookings
     * @description The caller's latest bookings, newest first. `session_id` keeps those of one chat conversation.
     */
    get: operations["my_bookings_v1_bookings_get"];
    put?: never;
    /**
     * Book
     * @description Books every seat or none. A retried request with the same Idempotency-Key gets the first booking back.
     */
    post: operations["book_v1_bookings_post"];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
}
export type webhooks = Record<string, never>;
export interface components {
  schemas: {
    /** Booking */
    Booking: {
      /** Code */
      code: string;
      /**
       * Channel
       * @enum {string}
       */
      channel: "web" | "chat" | "mcp";
      showtime: components["schemas"]["Showtime"];
      /** Seats */
      seats: string[];
      /** Customer Name */
      customer_name: string;
      /** Total Price Idr */
      total_price_idr: number;
      /**
       * Created At
       * Format: date-time
       */
      created_at: string;
    };
    /**
     * BookingForm
     * @description What a client sends to book. The owner comes from the server, never from the body.
     */
    BookingForm: {
      /** Showtime Id */
      showtime_id: number;
      /** Seats */
      seats: string[];
      /** Customer Name */
      customer_name: string;
      /**
       * Channel
       * @default web
       * @enum {string}
       */
      channel: "web" | "chat" | "mcp";
      /**
       * Session Id
       * @description The chat agent's conversation, if it books
       */
      session_id?: string | null;
    };
    /** CallerView */
    CallerView: {
      /** Caller */
      caller: string;
    };
    /** Cinema */
    Cinema: {
      /** Name */
      name: string;
      /** Timezone */
      timezone: string;
      /**
       * Now
       * Format: date-time
       */
      now: string;
      /** Now Local */
      now_local: string;
      /** Max Seats Per Booking */
      max_seats_per_booking: number;
      week: components["schemas"]["Week"];
    };
    /** HTTPValidationError */
    HTTPValidationError: {
      /** Detail */
      detail?: components["schemas"]["ValidationError"][];
    };
    /** Movie */
    Movie: {
      /** Id */
      id: number;
      /** Title */
      title: string;
      /** Synopsis */
      synopsis: string;
      /** Release Year */
      release_year: number;
      /** Genres */
      genres: string[];
      /** Studio Number */
      studio_number: number;
      /** Poster Url */
      poster_url: string | null;
      /** Backdrop Url */
      backdrop_url: string | null;
      /** Trailer Youtube Id */
      trailer_youtube_id: string | null;
    };
    /**
     * SeatMap
     * @description For a UI: rows front to back, and where the aisle and the walkway fall, so a UI draws the real room.
     */
    SeatMap: {
      showtime: components["schemas"]["Showtime"];
      /** Rows */
      rows: components["schemas"]["SeatRowView"][];
      /**
       * Aisle After Seat
       * @default 9
       */
      aisle_after_seat: number;
      /**
       * Walkway Before Row
       * @default L
       */
      walkway_before_row: string;
    };
    /** SeatRowView */
    SeatRowView: {
      /** Row */
      row: string;
      /** Seats */
      seats: components["schemas"]["SeatView"][];
    };
    /** SeatView */
    SeatView: {
      /** Id */
      id: string;
      /** Is Taken */
      is_taken: boolean;
      /** Booked By */
      booked_by?: string | null;
    };
    /** ServiceMeta */
    ServiceMeta: {
      /** Id */
      id: string;
      /** Name */
      name: string;
      /** Summary */
      summary: string;
      /** Version */
      version: string;
      /** Docs Path */
      docs_path: string;
      /** Mcp Path */
      mcp_path: string | null;
    };
    /** Showtime */
    Showtime: {
      /** Id */
      id: number;
      /** Movie Id */
      movie_id: number;
      /** Movie Title */
      movie_title: string;
      /** Studio Number */
      studio_number: number;
      /**
       * Starts At
       * Format: date-time
       */
      starts_at: string;
      /** Starts At Local */
      starts_at_local: string;
      /** Price Idr */
      price_idr: number;
      /** Seats Left */
      seats_left: number;
    };
    /** ValidationError */
    ValidationError: {
      /** Location */
      loc: (string | number)[];
      /** Message */
      msg: string;
      /** Error Type */
      type: string;
      /** Input */
      input?: unknown;
      /** Context */
      ctx?: Record<string, never>;
    };
    /**
     * Week
     * @description The week on sale, Monday to Sunday in cinema time.
     */
    Week: {
      /** Days */
      days: string[];
      /**
       * Today
       * Format: date
       */
      today: string;
      /** Is Published */
      is_published: boolean;
    };
  };
  responses: never;
  parameters: never;
  requestBodies: never;
  headers: never;
  pathItems: never;
}
export type $defs = Record<string, never>;
export interface operations {
  health_health_get: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": {
            [key: string]: string;
          };
        };
      };
    };
  };
  meta_meta_get: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["ServiceMeta"];
        };
      };
    };
  };
  start_guest_session_auth_guest_post: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      204: {
        headers: {
          [name: string]: unknown;
        };
        content?: never;
      };
    };
  };
  cinema_v1_cinema_get: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["Cinema"];
        };
      };
    };
  };
  me_v1_me_get: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["CallerView"];
        };
      };
    };
  };
  list_movies_v1_movies_get: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["Movie"][];
        };
      };
    };
  };
  get_movie_v1_movies__movie_id__get: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        movie_id: number;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["Movie"];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  list_showtimes_v1_showtimes_get: {
    parameters: {
      query: {
        day: string;
        movie_id?: number | null;
      };
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["Showtime"][];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  get_showtime_v1_showtimes__showtime_id__get: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        showtime_id: number;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["Showtime"];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  seat_map_v1_showtimes__showtime_id__seats_get: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        showtime_id: number;
      };
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["SeatMap"];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  my_bookings_v1_bookings_get: {
    parameters: {
      query?: {
        session_id?: string | null;
      };
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["Booking"][];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  book_v1_bookings_post: {
    parameters: {
      query?: never;
      header: {
        "idempotency-key": string;
      };
      path?: never;
      cookie?: never;
    };
    requestBody: {
      content: {
        "application/json": components["schemas"]["BookingForm"];
      };
    };
    responses: {
      /** @description Successful Response */
      201: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["Booking"];
        };
      };
      /** @description Validation Error */
      422: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
}

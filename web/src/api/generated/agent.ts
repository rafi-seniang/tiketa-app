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
  "/v1/sessions": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /** Start Session */
    post: operations["start_session_v1_sessions_post"];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/v1/sessions/{session_id}": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Get Session */
    get: operations["get_session_v1_sessions__session_id__get"];
    put?: never;
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/v1/sessions/{session_id}/messages": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /** Send Message */
    post: operations["send_message_v1_sessions__session_id__messages_post"];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/v1/sessions/{session_id}/confirmation": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    /** Answer Confirmation */
    post: operations["answer_confirmation_v1_sessions__session_id__confirmation_post"];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/v1/usage": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /**
     * Token Usage
     * @description The caller's model tokens today against the daily budget.
     */
    get: operations["token_usage_v1_usage_get"];
    put?: never;
    post?: never;
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
     * BookingSummary
     * @description Built in code from the database and shown to the user before anything is booked.
     */
    BookingSummary: {
      /** Showtime Id */
      showtime_id?: number | null;
      /** Movie Title */
      movie_title: string;
      /**
       * Starts At
       * Format: date-time
       */
      starts_at: string;
      /** Starts At Local */
      starts_at_local: string;
      /** Studio Number */
      studio_number: number;
      /** Seats */
      seats: string[];
      /** Customer Name */
      customer_name: string;
      /** Price Per Seat Idr */
      price_per_seat_idr: number;
      /** Total Price Idr */
      total_price_idr: number;
    };
    /** ConfirmationIn */
    ConfirmationIn: {
      /**
       * Approved
       * @description The user pressed Confirm (true) or Cancel (false)
       */
      approved: boolean;
    };
    /** HTTPValidationError */
    HTTPValidationError: {
      /** Detail */
      detail?: components["schemas"]["ValidationError"][];
    };
    /** MessageIn */
    MessageIn: {
      /**
       * Message
       * @description What the user typed
       */
      message: string;
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
      /** Engine */
      engine: string;
      /** Own Ui Path */
      own_ui_path: string;
      /** Docs Path */
      docs_path: string;
    };
    /** SessionCreated */
    SessionCreated: {
      /** Session Id */
      session_id: string;
    };
    /** SessionView */
    SessionView: {
      /** Session Id */
      session_id: string;
      /** Turns */
      turns: components["schemas"]["Turn"][];
      /** Draft */
      draft: {
        [key: string]: unknown;
      };
      pending_confirmation: components["schemas"]["BookingSummary"] | null;
      /** Bookings */
      bookings: components["schemas"]["Booking"][];
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
    /** TokenUsageView */
    TokenUsageView: {
      /** Used Tokens */
      used_tokens: number;
      /** Daily Tokens */
      daily_tokens: number;
      /** Resets In Seconds */
      resets_in_seconds: number;
    };
    /** Turn */
    Turn: {
      /**
       * Role
       * @enum {string}
       */
      role: "user" | "assistant";
      /** Text */
      text: string;
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
  start_session_v1_sessions_post: {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody?: never;
    responses: {
      /** @description Successful Response */
      201: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "application/json": components["schemas"]["SessionCreated"];
        };
      };
    };
  };
  get_session_v1_sessions__session_id__get: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        session_id: string;
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
          "application/json": components["schemas"]["SessionView"];
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
  send_message_v1_sessions__session_id__messages_post: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        session_id: string;
      };
      cookie?: never;
    };
    requestBody: {
      content: {
        "application/json": components["schemas"]["MessageIn"];
      };
    };
    responses: {
      /** @description ChatEvent objects, one per data: line */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "text/event-stream": unknown;
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
  answer_confirmation_v1_sessions__session_id__confirmation_post: {
    parameters: {
      query?: never;
      header?: never;
      path: {
        session_id: string;
      };
      cookie?: never;
    };
    requestBody: {
      content: {
        "application/json": components["schemas"]["ConfirmationIn"];
      };
    };
    responses: {
      /** @description ChatEvent objects, one per data: line */
      200: {
        headers: {
          [name: string]: unknown;
        };
        content: {
          "text/event-stream": unknown;
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
  token_usage_v1_usage_get: {
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
          "application/json": components["schemas"]["TokenUsageView"];
        };
      };
    };
  };
}

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useState } from "react";
import { agent, isAgentAnswering } from "../api/agent";
import { type Booking, CORE_URL, core, unwrap } from "../api/core";
import { AssistantSetup } from "./AssistantSetup";
import { type AgentStatus, ChatPanel } from "./ChatPanel";
import { FilmScreen } from "./FilmScreen";
import { cinemaDay } from "./format";
import { HomeScreen } from "./HomeScreen";
import { fetchSeats, keys, useCinema } from "./queries";
import { Link, navigate, useRoute } from "./router";
import { SeatsScreen } from "./SeatsScreen";
import { TicketsScreen } from "./TicketsScreen";
import { useChat } from "./useChat";
import "./tiketa.css";

const AGENT_CHECK_MS = 10_000;
// The Lab sits at the site's root once deployed; locally it runs on its own port
const LAB_URL =
  (import.meta.env.VITE_LAB_URL as string | undefined) ||
  (import.meta.env.BASE_URL === "/" ? "http://localhost:5173/" : "/");

function Mark() {
  return (
    <svg width={22} height={22} viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
      <path d="M3 4h14v4a2 2 0 0 0 0 4v4H3v-4a2 2 0 0 0 0-4V4Z" />
      <path d="M8 7h4v1.5H8zM8 11.5h4V13H8z" fill="var(--ground)" />
    </svg>
  );
}

/** Tiketa's site: films, a film's showtimes, a room's seats and the visitor's tickets, with the agent on every screen. */
export function TiketaApp() {
  const queryClient = useQueryClient();
  const route = useRoute();
  const cinema = useCinema();
  const meta = useQuery({
    queryKey: keys.meta,
    queryFn: async () => unwrap(await core.GET("/meta")),
    staleTime: Number.POSITIVE_INFINITY,
  });
  const mcpPath = meta.data?.mcp_path; // null while the API runs with its MCP server off
  // The chat agent is its own service: asked every 10 seconds, so the chat turns on and off with it
  const agentAnswering = useQuery({
    queryKey: keys.agent,
    queryFn: isAgentAnswering,
    refetchInterval: AGENT_CHECK_MS,
    retry: false,
  });
  const agentStatus: AgentStatus = agentAnswering.data === undefined ? "checking" : agentAnswering.data ? "on" : "off";
  const usage = useQuery({
    queryKey: keys.usage,
    queryFn: async () => unwrap(await agent.GET("/v1/usage")),
    enabled: agentStatus === "on",
  });
  const [chatOpen, setChatOpen] = useState(false);

  const refreshAfterBooking = useCallback(
    (booking: Booking) => {
      void queryClient.invalidateQueries({ queryKey: keys.seats(booking.showtime.id) });
      void queryClient.invalidateQueries({ queryKey: keys.showtimes(cinemaDay(booking.showtime.starts_at)) });
      void queryClient.invalidateQueries({ queryKey: keys.bookings });
    },
    [queryClient],
  );
  const chat = useChat({
    enabled: agentStatus === "on",
    onBooked: refreshAfterBooking,
    onTurnEnd: () => void queryClient.invalidateQueries({ queryKey: keys.usage }),
  });

  const pendingShowtimeId = chat.pending?.showtime_id ?? null;
  const pendingSeats = useQuery({
    queryKey: keys.seats(pendingShowtimeId ?? 0),
    queryFn: () => fetchSeats(pendingShowtimeId ?? 0),
    enabled: pendingShowtimeId !== null,
    staleTime: 5_000,
  });
  const heldByChat =
    route.name === "seats" && chat.pending?.showtime_id === route.id ? chat.pending.seats : ([] as string[]);

  const ask = (text: string) => {
    setChatOpen(true);
    void chat.send(text);
  };

  return (
    <div className="tk-site" data-route={route.name}>
      <header className="tk-top">
        <Link to={{ name: "home" }} className="tk-brand">
          <Mark />
          Tiketa
        </Link>
        <nav aria-label="Tiketa">
          <Link to={{ name: "home" }} aria-current={route.name !== "tickets" ? "page" : undefined}>
            Now showing
          </Link>
          <Link to={{ name: "tickets" }} aria-current={route.name === "tickets" ? "page" : undefined}>
            My tickets
          </Link>
        </nav>
        <a className="tk-lab-link" href={LAB_URL}>
          Back to the AI Lab
        </a>
      </header>

      <main className="tk-main">
        {route.name === "home" && <HomeScreen agentStatus={agentStatus} ready={chat.ready} onAsk={ask} />}
        {route.name === "film" && <FilmScreen id={route.id} />}
        {route.name === "seats" && <SeatsScreen key={route.id} id={route.id} heldByChat={heldByChat} />}
        {route.name === "tickets" && <TicketsScreen />}
      </main>

      <footer className="tk-foot">
        <div className="tk-foot-cinema">
          <strong>{cinema.data?.name ?? "Tiketa Cinema"}</strong>
          <span>Jakarta, times in WIB. Pay at the counter with your booking code.</span>
          <span>
            Chat agent {agentStatus === "on" ? "on" : agentStatus === "off" ? "off" : "checking"}, MCP server{" "}
            {meta.data ? (mcpPath ? "on" : "off") : "checking"}
          </span>
        </div>
        {mcpPath && <AssistantSetup mcpUrl={`${CORE_URL}${mcpPath}/`} />}
      </footer>

      <div className="tk-chat-dock" data-open={chatOpen}>
        {chatOpen ? (
          <ChatPanel
            status={agentStatus}
            lines={chat.lines}
            pending={chat.pending}
            pendingSeatMap={pendingSeats.data?.showtime.id === pendingShowtimeId ? pendingSeats.data : undefined}
            activity={chat.activity}
            busy={chat.busy}
            ready={chat.ready}
            startError={chat.startError}
            usage={usage.data}
            onSend={(text) => void chat.send(text)}
            onAnswer={(approved) => void chat.answer(approved)}
            onShowOnMap={(summary) => {
              if (summary.showtime_id != null) navigate({ name: "seats", id: summary.showtime_id });
            }}
            onRestart={() => void chat.restart()}
            onClose={() => setChatOpen(false)}
          />
        ) : (
          <button type="button" className="btn primary tk-chat-open" onClick={() => setChatOpen(true)}>
            {chat.pending ? "1 booking to confirm" : "Chat with the agent"}
          </button>
        )}
      </div>
    </div>
  );
}

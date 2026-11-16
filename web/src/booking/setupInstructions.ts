const THIS_COMPUTER = ["localhost", "127.0.0.1"];

/** Where a person adds a remote MCP server, per app. Shown on the page for the person, not pasted to the assistant. */
export const ADD_SERVER_STEPS: { app: string; steps: string }[] = [
  {
    app: "Claude (web or desktop)",
    steps:
      'Customize, Connectors, Add custom connector. Paste the URL, choose "No sign in", then switch it on in the chat.',
  },
  {
    app: "ChatGPT",
    steps: "Settings, Apps, Advanced, turn on Developer mode, then create an app with the URL and no authentication.",
  },
  {
    app: "Claude Code",
    steps: "Run claude mcp add --transport http tiketa <URL>, then start a new session.",
  },
  {
    app: "Cursor, VS Code, Windsurf and others",
    steps: 'Add a server named "tiketa" with the URL and the HTTP transport to the MCP settings, then reload.',
  },
];

/**
 * What a visitor pastes into their own assistant once Tiketa's MCP server is added there. One text for every app:
 * how to add the server is on the page, so the assistant never has to guess which app it is in.
 */
export function assistantSetupText(mcpUrl: string): string {
  const lines = [
    "Help me book cinema seats at Tiketa through its MCP server.",
    "",
    `MCP server: ${mcpUrl} (Streamable HTTP, no sign in)`,
    "Its tools: get_cinema, list_films, find_showtimes, get_seat_map, prepare_booking, confirm_booking, get_booking.",
    "",
    "1. Check that the Tiketa tools are available to you in this chat. If they are not, tell me so and stop: I will " +
      "add the server and come back. Do not call the URL some other way unless I say you may.",
    "2. Call get_cinema first for the cinema's date and time, so words like tomorrow or besok mean the right day.",
    "3. Ask me which film, day, time and seats I want and the name for the booking. Show me the seat map.",
    "4. Call prepare_booking and show me the summary and its total. Call confirm_booking only after I say yes to " +
      "that summary. A yes given before I saw it does not count.",
    "5. Give me the booking code. Confirming the same confirmation id twice returns the same booking.",
    "",
    "This is a demo cinema: the prices are what a ticket would cost, and nothing is paid.",
  ];
  if (THIS_COMPUTER.includes(new URL(mcpUrl).hostname)) {
    lines.push(
      "",
      "Note: this address is on my own computer, so only an assistant running on this computer can reach it.",
    );
  }
  return lines.join("\n");
}

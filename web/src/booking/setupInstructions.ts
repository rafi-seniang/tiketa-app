const THIS_COMPUTER = ["localhost", "127.0.0.1"];

/**
 * What a visitor pastes into their own assistant (Claude, ChatGPT, an editor's agent) so it adds Tiketa's MCP server,
 * or walks them through adding it. Written to the assistant, in English. How to book is not repeated here: the
 * server sends its own instructions once it is connected.
 */
export function assistantSetupText(mcpUrl: string): string {
  const lines = [
    "Please connect to Tiketa, a cinema booking service, through its MCP server, and then help me book seats.",
    "",
    `MCP server URL: ${mcpUrl}`,
    "Transport: Streamable HTTP. No sign in is needed.",
    "It has tools to read films, showtimes and seat maps, and to book in two steps: prepare, then confirm.",
    "",
    "How to add it, depending on what you are:",
    `- You can run commands on my computer (Claude Code): run "claude mcp add --transport http tiketa ${mcpUrl}".`,
    '- You read an MCP configuration file (Cursor, VS Code and similar): add a server named "tiketa" with this URL ' +
      "and the HTTP transport.",
    "- You are Claude on the web, desktop or phone: you cannot add it yourself, so walk me through it. " +
      'Customize, then Connectors, then Add, then Add custom connector. Name it Tiketa, paste the URL, choose "No ' +
      'sign in" and add it. Then switch it on for this chat from the + button under Connectors.',
    "- You are ChatGPT: you cannot add it yourself, so walk me through it on the web. Plugins, then the plus button, " +
      'then Add custom MCP server. Name it Tiketa, paste the URL as the Server URL, choose "No authentication", accept ' +
      "the warning and create it. Then install it and pick it in the chat with @. This needs a paid plan.",
    "If a step does not match my screen, the menus have changed: ask me what I see and guide me from there.",
  ];
  if (THIS_COMPUTER.includes(new URL(mcpUrl).hostname)) {
    lines.push(
      "",
      "Note: this address is on my own computer. Claude and ChatGPT connect from their own servers and cannot reach " +
        "it, so only an assistant running on this computer can use it (Claude Code, Cursor, VS Code).",
    );
  }
  lines.push(
    "",
    "Once you are connected, call get_cinema first for the cinema's date and time. Ask me which film, day, time and " +
      "seats I want and the name for the booking. Show me the summary and its total, and confirm the booking only " +
      "after I say yes. I pay at the cinema's counter with the booking code.",
  );
  return lines.join("\n");
}

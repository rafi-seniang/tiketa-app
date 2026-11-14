import { useState } from "react";
import { assistantSetupText } from "./setupInstructions";

/** Lets a visitor copy the instructions that connect their own assistant to the MCP server, and read them first. */
export function AssistantSetup({ mcpUrl }: { mcpUrl: string }) {
  const [copying, setCopying] = useState<"idle" | "copied" | "blocked">("idle");
  const text = assistantSetupText(mcpUrl);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopying("copied");
    } catch {
      setCopying("blocked"); // no clipboard permission, or a page not served over HTTPS
    }
  };

  return (
    <section className="tk-assistant" aria-labelledby="tk-assistant-title">
      <h2 id="tk-assistant-title">Book from your own assistant</h2>
      <p>Claude, ChatGPT and coding agents can book here over MCP. Paste these instructions into yours.</p>
      <button type="button" className="btn" onClick={() => void copy()}>
        {copying === "copied" ? "Copied" : "Copy setup instructions"}
      </button>
      <p className="tk-assistant-status" role="status">
        {copying === "copied" && "Now paste it into your assistant."}
        {copying === "blocked" && "The browser blocked copying. Select the text below."}
      </p>
      <details open={copying === "blocked" || undefined}>
        <summary>Read what is copied</summary>
        <pre>{text}</pre>
      </details>
    </section>
  );
}

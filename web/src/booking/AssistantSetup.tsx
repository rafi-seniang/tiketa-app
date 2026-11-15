import { useState } from "react";
import { assistantSetupText } from "./setupInstructions";

/** One sentence and one button: a visitor copies the instructions that connect their own assistant to the MCP server. */
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
      <h2 id="tk-assistant-title">Book with your own AI chatbot</h2>
      <p>Copy the instructions and paste them into Claude or ChatGPT.</p>
      <button type="button" className="btn" onClick={() => void copy()}>
        {copying === "copied" ? "Copied" : "Copy instructions"}
      </button>
      <p className="tk-assistant-status" role="status">
        {copying === "copied" && "Now paste it into your chatbot."}
        {copying === "blocked" && "The browser blocked copying. Select the text below."}
      </p>
      {copying === "blocked" && <pre>{text}</pre>}
    </section>
  );
}

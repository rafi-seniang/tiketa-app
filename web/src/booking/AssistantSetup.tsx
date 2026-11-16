import { useState } from "react";
import { ADD_SERVER_STEPS, assistantSetupText } from "./setupInstructions";

type CopyState = "idle" | "copied" | "blocked";

function useCopy(text: string) {
  const [state, setState] = useState<CopyState>("idle");
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setState("copied");
    } catch {
      setState("blocked"); // no clipboard permission, or a page not served over HTTPS
    }
  };
  return { state, copy };
}

/** The band under the top bar: add Tiketa's MCP server to any assistant, then paste one set of instructions. */
export function AssistantSetup({ mcpUrl }: { mcpUrl: string }) {
  const text = assistantSetupText(mcpUrl);
  const prompt = useCopy(text);
  const url = useCopy(mcpUrl);

  return (
    <section className="tk-try" aria-labelledby="tk-try-title">
      <div className="tk-try-about">
        <span className="tk-try-label">Try it</span>
        <h2 id="tk-try-title">Book with your own AI chatbot</h2>
        <p>
          Tiketa has an MCP server. Add it to Claude, ChatGPT, Cursor or any app that takes a remote MCP server, then
          paste the instructions into a new chat.
        </p>
      </div>
      <div className="tk-try-actions">
        <div className="tk-try-url">
          <code>{mcpUrl}</code>
          <button type="button" className="btn" onClick={() => void url.copy()}>
            {url.state === "copied" ? "Copied" : "Copy URL"}
          </button>
        </div>
        <button type="button" className="btn primary" onClick={() => void prompt.copy()}>
          {prompt.state === "copied" ? "Copied, now paste it" : "Copy instructions"}
        </button>
        <details className="tk-try-steps">
          <summary>How to add the server in your app</summary>
          <dl>
            {ADD_SERVER_STEPS.map((entry) => (
              <div key={entry.app}>
                <dt>{entry.app}</dt>
                <dd>{entry.steps.replace("<URL>", mcpUrl)}</dd>
              </div>
            ))}
          </dl>
          <p>Menus change often. If yours look different, look for connectors, apps or MCP servers in the settings.</p>
        </details>
        {(prompt.state === "blocked" || url.state === "blocked") && (
          <>
            <p role="status">The browser blocked copying. Select the text below.</p>
            <pre>{prompt.state === "blocked" ? text : mcpUrl}</pre>
          </>
        )}
      </div>
    </section>
  );
}

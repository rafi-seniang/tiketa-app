import { type ReactNode, useState } from "react";
import "./app-shell.css";

interface AppShellProps {
  product: string;
  mark: ReactNode;
  scope: { line: string; detail: string };
  sidebar?: ReactNode;
  sidebarFooter?: ReactNode;
  className?: string;
  children: ReactNode;
}

/** The frame the booking screen sits in: the tinted L of sidebar and top bar, and the white sheet. */
export function AppShell({ product, mark, scope, sidebar, sidebarFooter, className, children }: AppShellProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  return (
    <div className={`app-shell${className ? ` ${className}` : ""}`}>
      <div className="app">
        <aside className={`sidebar${menuOpen ? " open" : ""}`} aria-label="About this cinema">
          <div className="brand">
            {mark}
            {product}
            <button
              className="btn ghost menu-close"
              type="button"
              onClick={() => setMenuOpen(false)}
              aria-label="Close the side panel"
            >
              Close
            </button>
          </div>
          <span className="scope">
            <strong>{scope.line}</strong>
            <span>{scope.detail}</span>
          </span>
          {sidebar}
          {sidebarFooter && <div className="bottom">{sidebarFooter}</div>}
        </aside>

        <header className="topbar">
          <button
            className="btn ghost menu-toggle"
            type="button"
            onClick={() => setMenuOpen(true)}
            aria-expanded={menuOpen}
            aria-label="Open the side panel"
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              aria-hidden="true"
            >
              <path d="M2 4h12M2 8h12M2 12h12" />
            </svg>
          </button>
          <span className="brand-short">
            {mark}
            {product}
          </span>
        </header>

        <main className="sheet">{children}</main>
      </div>
    </div>
  );
}

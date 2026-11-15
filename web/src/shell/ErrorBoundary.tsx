import { Component, type ErrorInfo, type ReactNode } from "react";

/** A screen that fails while rendering shows this, not an empty page. The cause goes to the console. */
export class ErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };

  static getDerivedStateFromError() {
    return { failed: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("The screen failed to render", error, info.componentStack);
  }

  render() {
    if (!this.state.failed) return this.props.children;
    return (
      <main className="app-failed" role="alert">
        <h1>This page stopped working</h1>
        <p>Nothing was booked by this error. Reload the page to carry on.</p>
        <button type="button" className="btn" onClick={() => window.location.reload()}>
          Reload
        </button>
      </main>
    );
  }
}

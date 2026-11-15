import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { TiketaApp } from "./booking/TiketaApp";
import { ErrorBoundary } from "./shell/ErrorBoundary";

const queryClient = new QueryClient({ defaultOptions: { queries: { refetchOnWindowFocus: false } } });

const root = document.getElementById("root");
if (!root) throw new Error("index.html has no #root element");

createRoot(root).render(
  <StrictMode>
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <TiketaApp />
      </QueryClientProvider>
    </ErrorBoundary>
  </StrictMode>,
);

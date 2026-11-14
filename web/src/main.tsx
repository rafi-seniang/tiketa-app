import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { TiketaBooking } from "./booking/TiketaBooking";
import { ErrorBoundary } from "./shell/ErrorBoundary";
import "./styles/brand.css";

const queryClient = new QueryClient({ defaultOptions: { queries: { refetchOnWindowFocus: false } } });

const root = document.getElementById("root");
if (!root) throw new Error("index.html has no #root element");

createRoot(root).render(
  <StrictMode>
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <TiketaBooking />
      </QueryClientProvider>
    </ErrorBoundary>
  </StrictMode>,
);

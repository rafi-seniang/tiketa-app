import react from "@vitejs/plugin-react";
import { loadEnv } from "vite";
import { defineConfig } from "vitest/config";

export default defineConfig(({ mode }) => ({
  // Where the site is served: "/" on its own host, or a path such as "/tiketa/" behind a shared one
  base: loadEnv(mode, ".", "VITE_").VITE_BASE_PATH || "/",
  plugins: [react()],
  server: { port: 5174, strictPort: true }, // the API's CORS list names this port
  preview: { port: 4174, strictPort: true },
  test: { environment: "jsdom", setupFiles: ["./src/test-setup.ts"] },
}));

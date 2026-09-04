import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

/**
 * Nothing is aliased here on purpose: the point of this demo is to consume the
 * *published* `@vitreajs/vitrea-react@0.6.0` exactly as an outside app would,
 * so the resolution goes through `node_modules` and nowhere else.
 */
export default defineConfig({
  base: "./",
  plugins: [react()],
  server: { port: 5180 },
});

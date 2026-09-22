/** The ordinary demo suite on an unoccupied port; no test or launch policy changes (§5.173). */
import { resolve } from "node:path";
import { defineConfig } from "@playwright/test";
import base from "../../../../apps/demo/playwright.config";

const demo = resolve(import.meta.dirname, "../../../../apps/demo");
export default defineConfig({
  ...base,
  testDir: resolve(demo, "e2e"),
  use: { ...base.use, baseURL: "http://localhost:5197" },
  webServer: {
    command: "npx vite --port 5197 --strictPort",
    cwd: demo,
    url: "http://localhost:5197/",
    reuseExistingServer: false,
    timeout: 60_000,
  },
});

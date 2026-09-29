/**
 * The ordinary React suite on an unoccupied port, used only when 5176 is held at launch.
 * Same tests, projects and launch policy; the same demo app served; no server reuse.
 */
import { resolve } from "node:path";
import { defineConfig } from "@playwright/test";
import base from "../../../../packages/react/playwright.config";

const react = resolve(import.meta.dirname, "../../../../packages/react");
const demo = resolve(import.meta.dirname, "../../../../apps/demo");
export default defineConfig({
  ...base,
  testDir: resolve(react, "e2e"),
  outputDir: resolve(react, "test-results"),
  use: { ...base.use, baseURL: "http://localhost:5196" },
  webServer: {
    command: "npx vite --port 5196 --strictPort",
    cwd: demo,
    url: "http://localhost:5196/",
    reuseExistingServer: false,
    timeout: 60_000,
  },
});

/**
 * The ordinary demo suite on an unoccupied port, used only when 5177 is held at launch.
 * Same tests, projects and launch policy; no server reuse (W33/W36 G2's demo-isolated config).
 */
import { resolve } from "node:path";
import { defineConfig } from "@playwright/test";
import base from "../../../../apps/demo/playwright.config";

const demo = resolve(import.meta.dirname, "../../../../apps/demo");
export default defineConfig({
  ...base,
  testDir: resolve(demo, "e2e"),
  outputDir: resolve(demo, "test-results"),
  use: { ...base.use, baseURL: "http://localhost:5197" },
  webServer: {
    command: "npx vite --port 5197 --strictPort",
    cwd: demo,
    url: "http://localhost:5197/",
    reuseExistingServer: false,
    timeout: 60_000,
  },
});

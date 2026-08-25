import { fileURLToPath } from "node:url";

import { defineConfig, devices } from "@playwright/test";

/**
 * C8's acceptance suite, run against the playground.
 *
 * **Every project runs every spec.** C5's split — pixel assertions on Chromium
 * only — exists because S1 proved automation cannot observe `backdrop-filter`
 * output on Gecko and WebKit. Nothing here is a pixel assertion: the four
 * behaviors this child owns are observable as DOM semantics (#1), as channel
 * values (#3), as measured geometry and hit-testing (#4), and as resolved policy
 * (#6). That is not a workaround for the capture blindness — it is what those
 * acceptances actually claim, and asserting them structurally makes them true on
 * all three engines instead of one.
 *
 * The two engine-specific cases are marked in the specs themselves, not here:
 * `forced-colors` emulation is Chromium-only in Playwright, and
 * `prefers-contrast` is not emulable everywhere either. Both skip with a reason
 * rather than being quietly excluded from a project list.
 */
const demoRoot = fileURLToPath(new URL("../../apps/demo", import.meta.url));

export default defineConfig({
  testDir: "e2e",
  fullyParallel: true,
  forbidOnly: process.env.CI !== undefined,
  retries: process.env.CI !== undefined ? 1 : 0,
  reporter: [["list"]],
  use: {
    baseURL: "http://localhost:5176",
    trace: "on-first-retry",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
    { name: "webkit", use: { ...devices["Desktop Safari"] } },
  ],
  webServer: {
    command: "npx vite --port 5176 --strictPort",
    cwd: demoRoot,
    url: "http://localhost:5176/",
    reuseExistingServer: process.env.CI === undefined,
    timeout: 60_000,
  },
});

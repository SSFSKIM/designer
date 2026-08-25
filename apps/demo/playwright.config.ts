import { fileURLToPath } from "node:url";

import { defineConfig, devices } from "@playwright/test";

/**
 * The public site's own suite.
 *
 * It belongs to the app rather than to `vitrea-react` because what it asserts is
 * the *page*: that its layout satisfies the placement law in `DESIGN.md` §9 (zero
 * dev-mode findings, on a build with the checks on), that the reference pair really
 * does place both sides from the shared geometry contract, and that the
 * accessibility floor the library claims for its users holds for the library's own
 * front page. `vitrea-react`'s suite drives `/playground/`, which is the
 * acceptance harness and a different question.
 *
 * One project. These are structural and geometric assertions, not pixel ones, and
 * the engines' disagreements about `backdrop-filter` capture (S1) are irrelevant to
 * them; the cross-engine surface is already covered by the two package suites.
 * `forced-colors` emulation is Chromium-only in Playwright, which is the other
 * reason this runs there.
 */
const root = fileURLToPath(new URL(".", import.meta.url));

export default defineConfig({
  testDir: "e2e",
  fullyParallel: true,
  forbidOnly: process.env.CI !== undefined,
  retries: process.env.CI !== undefined ? 1 : 0,
  reporter: [["list"]],
  use: {
    baseURL: "http://localhost:5177",
    trace: "on-first-retry",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    command: "npx vite --port 5177 --strictPort",
    cwd: root,
    url: "http://localhost:5177/",
    reuseExistingServer: process.env.CI === undefined,
    timeout: 60_000,
  },
});

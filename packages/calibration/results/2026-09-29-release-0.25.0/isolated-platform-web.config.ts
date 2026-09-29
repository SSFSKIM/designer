/**
 * The ordinary platform-web suite on an unoccupied port, used only when 5188 is held at launch.
 * Same tests, projects and launch policy; each project's testDir made absolute; no server reuse.
 * Vite's `--port` on the command line takes precedence over the fixture config's 5188.
 */
import { resolve } from "node:path";
import { defineConfig } from "@playwright/test";
import base from "../../../../packages/platform-web/playwright.config";

const web = resolve(import.meta.dirname, "../../../../packages/platform-web");
export default defineConfig({
  ...base,
  testDir: resolve(web, "e2e"),
  outputDir: resolve(web, "test-results"),
  projects: (base.projects ?? []).map((project) => ({
    ...project,
    ...(project.testDir === undefined ? {} : { testDir: resolve(web, project.testDir) }),
  })),
  use: { ...base.use, baseURL: "http://localhost:5198" },
  webServer: {
    command: "npx vite --config e2e/vite.config.ts --port 5198 --strictPort",
    cwd: web,
    url: "http://localhost:5198/e2e/fixtures/index.html",
    reuseExistingServer: false,
    timeout: 60_000,
  },
});

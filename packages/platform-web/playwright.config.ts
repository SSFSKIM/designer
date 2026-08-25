import { defineConfig, devices } from "@playwright/test";

/** Dawn needs these to reach the real backend; see the `chromium-gpu` note below. */
const GPU_ARGS = ["--enable-unsafe-webgpu", "--enable-features=Vulkan,WebGPU"];

/**
 * C5's acceptance suite, split exactly where S1's evidence puts the line
 * (Decision Log #18, human-approved).
 *
 * **Pixel assertions run on Chromium only.** S1 measured Gecko and WebKit
 * rendering `backdrop-filter` as a complete no-op in every automatable capture
 * path — Playwright headless and headed, retail `--screenshot`, WebDriver BiDi,
 * WKWebView `takeSnapshot` — while rendering it live, and while CSS `filter`,
 * `mix-blend-mode` and `opacity` render correctly in the same images. A pixel
 * assertion about the dom tier there would not be measuring the dom tier: it
 * would be permanently red, or vacuously green against an unfiltered scene.
 *
 * **Everything else runs on all three engines**, because everything else is
 * genuinely observable there: registration, teardown, hit-testing through the
 * inert canvases, focus, the probe battery, the overlap dev-error, the read
 * meter, the probe-demotion path, and unit promotion. S1 verified that whole
 * surface in all three engines itself.
 *
 * The remaining gap — how the dom tier actually *looks* on Gecko and WebKit — is
 * closed by a human at release time with
 * `spikes/s1-proxy-topology/pages/manual-check.html` (C9 owns running it).
 *
 * **`e2e/gpu` needs a real adapter, so it gets its own project.** C6 measured
 * that Playwright's bundled headless shell hands back a *software* adapter while
 * `channel: "chromium"` — the full browser binary — hands back the real one, and
 * a GPU tier verified on a CPU rasteriser is not the thing acceptance #2 asks
 * about. That directory is therefore excluded from the stock `chromium` project
 * and run by `chromium-gpu`, which fails rather than skips when no hardware
 * adapter answers. It is left out of CI for the same reason C6's suite is: the
 * hardware answer is machine-specific, and a suite that silently passes on a
 * machine with no GPU is worse than one that is not run.
 */
export default defineConfig({
  testDir: "e2e",
  fullyParallel: true,
  forbidOnly: process.env.CI !== undefined,
  retries: process.env.CI !== undefined ? 1 : 0,
  reporter: [["list"]],
  use: {
    baseURL: "http://localhost:5188",
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
      testDir: "e2e",
      testIgnore: "**/gpu/**",
    },
    { name: "firefox", use: { ...devices["Desktop Firefox"] }, testDir: "e2e/shared" },
    { name: "webkit", use: { ...devices["Desktop Safari"] }, testDir: "e2e/shared" },
    {
      name: "chromium-gpu",
      testDir: "e2e/gpu",
      // C6's launch recipe, unchanged: the channel is what produces a hardware
      // adapter rather than SwiftShader, and the flags are what let Dawn use it.
      use: { channel: "chromium", launchOptions: { args: GPU_ARGS } },
    },
  ],
  webServer: {
    command: "npx vite --config e2e/vite.config.ts",
    url: "http://localhost:5188/e2e/fixtures/index.html",
    reuseExistingServer: process.env.CI === undefined,
    timeout: 60_000,
  },
});

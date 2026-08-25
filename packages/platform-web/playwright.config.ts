import { defineConfig, devices } from "@playwright/test";

/** Dawn needs these to reach the real backend; see the `chromium-gpu` note below. */
const GPU_ARGS = ["--enable-unsafe-webgpu", "--enable-features=Vulkan,WebGPU"];

/**
 * The software recipe: SwiftShader for Dawn *and* for Skia, so that GPU
 * compositing stays on. See the `chromium-gpu` note below for what each half
 * buys and what happens without it.
 */
const SOFTWARE_GPU_ARGS = [
  "--enable-unsafe-webgpu",
  "--use-webgpu-adapter=swiftshader",
  "--enable-unsafe-swiftshader",
  "--enable-features=Vulkan",
  "--use-vulkan=swiftshader",
  "--disable-vulkan-fallback-to-gl-for-testing",
  "--enable-gpu-rasterization",
];

/** "Measure the software path deliberately" — the repo-wide flag for it. */
const SOFTWARE_GPU = process.env.VITREA_ALLOW_FALLBACK_ADAPTER === "1";

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
 * **`e2e/gpu` needs an adapter, so it gets its own project.** C6 measured that
 * Playwright's bundled headless shell hands back a *software* adapter while
 * `channel: "chromium"` — the full browser binary — hands back the real one, and
 * a GPU tier verified on a CPU rasteriser is not the thing acceptance #2 asks
 * about. That directory is therefore excluded from the stock `chromium` project
 * and run by `chromium-gpu`, which fails rather than skips when no adapter
 * answers, and fails rather than quietly accept a software one.
 *
 * **On a GPU-less runner the software path is opted into explicitly**, with
 * `VITREA_ALLOW_FALLBACK_ADAPTER=1` — the flag this repo already uses to mean
 * "measure the software path deliberately". Three facts, measured on
 * `ubuntu-latest` on 2026-08-25, are what the recipe above is made of:
 *
 *  - Dawn *computes* on SwiftShader there in every launch mode tried: a render
 *    pass into an offscreen texture reads back correctly through
 *    `copyTextureToBuffer`.
 *  - A WebGPU *canvas* gets no pixels at all in headless mode, under every flag
 *    combination tried — the full Chromium binary, Chrome stable, the headless
 *    shell, `--use-angle=swiftshader`, Graphite, `--in-process-gpu`,
 *    `--headless=old`. The GPU process says why:
 *    `Could not find SharedImageBackingFactory` for `WebGPUSwapBufferProvider`.
 *    With GPU compositing off there is no backing a swap chain can use, so every
 *    readback path returns transparent while the adapter, the device, the draws
 *    and the tier's own health all look fine — which is exactly how the four
 *    painting tests failed the first time this job ever ran.
 *  - Putting Skia on the same SwiftShader Vulkan driver keeps GPU compositing
 *    on, and then a **headed** browser under a virtual display paints. Headless
 *    under that same display still does not, so the window is load-bearing
 *    rather than incidental: CI runs this suite under `xvfb-run`.
 *
 * So what CI verifies is the tier's *behaviour* on a CPU rasteriser: the canvas
 * carries the surface, losing the device swaps tiers, recovery draws again, the
 * label holds its contrast floor. What it cannot verify is how real glass looks
 * on real hardware — that stays a developer-machine and release-time job, and the
 * gate in `e2e/support.ts` names the software adapter out loud on every run that
 * takes this path, so no report can imply otherwise.
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
      use: SOFTWARE_GPU
        ? { channel: "chromium", headless: false, launchOptions: { args: SOFTWARE_GPU_ARGS } }
        : { channel: "chromium", launchOptions: { args: GPU_ARGS } },
    },
  ],
  webServer: {
    command: "npx vite --config e2e/vite.config.ts",
    url: "http://localhost:5188/e2e/fixtures/index.html",
    reuseExistingServer: process.env.CI === undefined,
    timeout: 60_000,
  },
});

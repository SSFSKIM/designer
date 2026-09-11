import { defineConfig } from "@playwright/test";

/**
 * The GPU suite.
 *
 * **One project, and the launch mode is the whole reason.** S2's benchmark
 * harness measured, and this package's own probe re-measured on 2026-08-25, that
 * this machine hands out three different WebGPU answers depending on how Chromium
 * is launched:
 *
 * | launch | adapter |
 * | --- | --- |
 * | Playwright's default headless shell | `google / swiftshader` — a **software** adapter |
 * | `channel: "chromium"`, headless | `apple / metal-3` — real hardware, `timestamp-query` |
 * | `channel: "chromium"`, headed | the same |
 *
 * So the project below asks for the full Chromium binary. The default headless
 * shell would run every test green against a CPU rasteriser, which would make the
 * benchmark meaningless and the goldens a record of SwiftShader's rounding.
 *
 * Two further requirements are not optional either:
 *
 *  - **A secure context.** `navigator.gpu` is undefined on `file://` and on
 *    `data:` URLs, which reads exactly like "no WebGPU on this machine". The Vite
 *    server serves `http://localhost`, which is a secure context.
 *  - **`--disable-dawn-features=timestamp_quantization`.** Chrome quantises
 *    timestamp-query results to 100 µs by default, and every pass here is shorter
 *    than that, so without it the benchmark reads every pass as 0.
 *
 * Firefox is absent because it returns no adapter here at all, and WebKit because
 * one hardware adapter is what the acceptance needs — a second engine would add
 * a second set of goldens without adding a second verdict.
 */

const GPU_ARGS = [
  "--enable-unsafe-webgpu",
  "--enable-features=Vulkan,WebGPU",
  "--disable-dawn-features=timestamp_quantization",
];

/**
 * Kept in step with `e2e/vite.config.ts`, which reads the same variable: the
 * config that starts the server and the config that points the browser at it
 * must agree, and two hard-coded copies of one number is how a golden run came
 * to be served a sibling worktree's calibration page.
 */
const GOLDEN_SERVER_ORIGIN = `http://localhost:${process.env["VITREA_GOLDEN_SERVER_PORT"] ?? 5189}`;

export default defineConfig({
  testDir: "e2e",
  fullyParallel: false,
  // The benchmark is a measurement: two of them contending for one GPU produce
  // numbers that are about the contention. S2 lost a whole run to exactly that.
  workers: 1,
  forbidOnly: process.env.CI !== undefined,
  retries: 0,
  reporter: [["list"]],
  timeout: 120_000,
  use: {
    baseURL: GOLDEN_SERVER_ORIGIN,
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "chromium-gpu",
      use: {
        channel: "chromium",
        launchOptions: { args: GPU_ARGS },
      },
    },
  ],
  webServer: {
    command: "npx vite --config e2e/vite.config.ts",
    url: `${GOLDEN_SERVER_ORIGIN}/e2e/fixtures/index.html`,
    reuseExistingServer: process.env.CI === undefined,
    timeout: 60_000,
  },
});

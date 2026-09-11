import { fileURLToPath } from "node:url";

import { defineConfig } from "vite";

/**
 * The W27e G0 composite probe's own dev server.
 *
 * Aliased to package SOURCE exactly as `platform-web/e2e/vite.config.ts` and
 * `calibration/web/vite.config.ts` are, for the same reason: the question is
 * what today's plane sandwich composites like, not last build's.
 *
 * The port is deliberately NOT one of the repo's fixed constants (5188, 5189,
 * 5197, 5198, 5213 are all already spoken for by a suite or a concurrent
 * worker); it is verified free before the run and `strictPort` refuses to slide
 * onto somebody else's server.
 */
const here = fileURLToPath(new URL(".", import.meta.url));
const packages = fileURLToPath(new URL("../../../../", import.meta.url));
const repoRoot = fileURLToPath(new URL("../../../../../", import.meta.url));

export const PROBE_PORT = 5231;

export default defineConfig({
  root: here,
  resolve: {
    alias: {
      "@vitreajs/vitrea": `${packages}core/src/index.ts`,
      "@vitreajs/vitrea-web": `${packages}platform-web/src/index.ts`,
      "@vitrea/geometry": `${packages}geometry/src/index.ts`,
      "@vitrea/motion": `${packages}motion/src/index.ts`,
      "@vitrea/renderer-webgpu": `${packages}renderer-webgpu/src/index.ts`,
    },
  },
  server: {
    port: PROBE_PORT,
    strictPort: true,
    fs: { allow: [repoRoot] },
  },
});

import { fileURLToPath } from "node:url";

import { defineConfig } from "vite";

/**
 * The e2e fixture server.
 *
 * Aliased to **source**, not to each package's `dist`: an integration suite that
 * silently tests a stale build is worse than no suite, and this way the e2e run
 * needs no build step of its own.
 */
const packageRoot = fileURLToPath(new URL("..", import.meta.url));
const packages = fileURLToPath(new URL("../..", import.meta.url));

export default defineConfig({
  root: packageRoot,
  resolve: {
    alias: {
      "@vitrea/core": `${packages}core/src/index.ts`,
      "@vitrea/geometry": `${packages}geometry/src/index.ts`,
      "@vitrea/motion": `${packages}motion/src/index.ts`,
      "@vitrea/renderer-webgpu": `${packages}renderer-webgpu/src/index.ts`,
    },
  },
  server: { port: 5188, strictPort: true },
});

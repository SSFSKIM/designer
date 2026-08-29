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
      "@vitreajs/vitrea": `${packages}core/src/index.ts`,
      // `fixtures/vanilla.ts` imports this package the way a consumer does — by
      // its published name, not by a relative path — so the specifier and the
      // public surface behind it are both under test. Aliased to source like
      // everything else here; `test/publish-shape.test.ts` covers the artifact.
      "@vitreajs/vitrea-web": `${packageRoot}src/index.ts`,
      "@vitrea/geometry": `${packages}geometry/src/index.ts`,
      "@vitrea/motion": `${packages}motion/src/index.ts`,
      "@vitrea/renderer-webgpu": `${packages}renderer-webgpu/src/index.ts`,
    },
  },
  server: { port: 5188, strictPort: true },
});

import { fileURLToPath } from "node:url";

import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

/**
 * Aliased to **source**, not to each package's `dist`, for the same reason
 * platform-web's e2e server is: a playground that silently runs a stale build is
 * worse than no playground, and this way `pnpm dev` needs no build step. The
 * published artifact is asserted separately, on `dist`, by
 * `packages/react/test/publish-shape.test.ts`.
 */
const packages = fileURLToPath(new URL("../../packages/", import.meta.url));

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@vitrea/core": `${packages}core/src/index.ts`,
      "@vitrea/geometry": `${packages}geometry/src/index.ts`,
      "@vitrea/motion": `${packages}motion/src/index.ts`,
      "@vitrea/platform-web": `${packages}platform-web/src/index.ts`,
      "@vitrea/react": `${packages}react/src/index.ts`,
    },
  },
  server: { port: 5173 },
});

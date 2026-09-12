import { fileURLToPath } from "node:url";

import { defineConfig } from "vite";

/**
 * The GPU-suite fixture server.
 *
 * Two things about it are load-bearing rather than convenient:
 *
 *  - **It serves over `http://localhost`.** WebGPU requires a secure context, and
 *    `localhost` is one; a `file://` or `data:` page has no `navigator.gpu` at
 *    all, which reads exactly like "this machine has no WebGPU" and is not.
 *  - **It aliases to source, not to `dist`.** A suite that silently tested a stale
 *    build is worse than no suite, and this way the run needs no build step of its
 *    own. Same choice `platform-web`'s e2e server makes, for the same reason.
 */
const packageRoot = fileURLToPath(new URL("..", import.meta.url));
const packages = fileURLToPath(new URL("../..", import.meta.url));

export default defineConfig({
  root: packageRoot,
  resolve: {
    alias: {
      "@vitrea/geometry": `${packages}geometry/src/index.ts`,
      "@vitrea/motion": `${packages}motion/src/index.ts`,
    },
  },
  // Overridable for the same reason the calibration scene server's port is:
  // both bind 5189 with `strictPort`, and on a machine running several
  // worktrees a golden run has been handed the calibration page instead of
  // these fixtures (tech-debt-tracker, "Calibration and renderer tests share a
  // fixed port"). `playwright.config.ts` reads the same variable, so the two
  // halves cannot disagree.
  server: { port: Number(process.env["VITREA_GOLDEN_SERVER_PORT"] ?? 5189), strictPort: true },
});

import { defineConfig } from "vitest/config";

/**
 * A Node-only unit suite, deliberately separate from `test:e2e`'s Playwright
 * run: these assertions are about the data `scenes.ts` resolves — what actually
 * ends up in `REFERENCE_SCENES` — not about a rendered page, so they need no
 * browser and no dev server.
 */
export default defineConfig({
  test: {
    include: ["test/**/*.test.ts"],
  },
});

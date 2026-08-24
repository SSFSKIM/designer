import { defineConfig } from "vitest/config";

/**
 * jsdom, not node: most of this package's unit-testable surface is DOM-shaped
 * even where the logic is pure — the layer sandwich, host registration and the
 * backdrop-root audit all reason about elements. What jsdom cannot do is
 * *layout* (`getBoundingClientRect` returns zeros) or `backdrop-filter`, so
 * everything that depends on a measured rect or a filtered pixel lives in the
 * Playwright suite (`playwright.config.ts`) instead. The split is deliberate:
 * a jsdom test that stubs layout would be asserting the stub.
 */
export default defineConfig({
  test: {
    environment: "jsdom",
    include: ["test/**/*.test.ts"],
  },
});

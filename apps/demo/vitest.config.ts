import { defineConfig } from "vitest/config";

import { shippedDocuments } from "./shipped-documents.ts";

/**
 * A Node-only unit suite, deliberately separate from `test:e2e`'s Playwright
 * run: these assertions are about the data `scenes.ts` resolves — what actually
 * ends up in `REFERENCE_SCENES` — not about a rendered page, so they need no
 * browser and no dev server.
 *
 * It carries `shippedDocuments()` for the same reason `vite.config.ts` does:
 * `calibration.ts` resolves which generation of a cell ships from the profile
 * documents' own bytes, and a suite that resolved that module differently from the
 * page would be asserting over a fixture rather than over the page's own reading.
 */
export default defineConfig({
  plugins: [shippedDocuments()],
  test: {
    include: ["test/**/*.test.ts"],
  },
});

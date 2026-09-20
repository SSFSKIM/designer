import { defineConfig } from "vitest/config";

import { matrixReduction } from "./matrix-reduction.ts";
import { shippedDocuments } from "./shipped-documents.ts";

/**
 * A Node-only unit suite, deliberately separate from `test:e2e`'s Playwright
 * run: these assertions are about the data `scenes.ts` resolves — what actually
 * ends up in `REFERENCE_SCENES` — not about a rendered page, so they need no
 * browser and no dev server.
 *
 * It carries `shippedDocuments()` and `matrixReduction()` for the same reason
 * `vite.config.ts` does: `calibration.ts` resolves which generation of a cell ships
 * from the profile documents' own bytes and reads its rows out of a build-time
 * projection of the matrix, and a suite that resolved either module differently from
 * the page would be asserting over a fixture rather than over the page's own reading.
 * The reduction is also what lets this suite LOAD at all — the whole matrix is past
 * the size the test loader's JSON bridge converts (claims §5.159 §6b).
 */
export default defineConfig({
  plugins: [shippedDocuments(), matrixReduction()],
  test: {
    include: ["test/**/*.test.ts"],
  },
});

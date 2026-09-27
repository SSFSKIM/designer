/**
 * The gallery, asserted the way the site is.
 *
 * Eight pages in two registers built under the materialist skill
 * (`docs/doperpowers/specs/2026-09-27-materialist-spatial-register.md`, C). Each page exposes
 * `window.__vitrea`, the runtime root, for the initiative's audit; this suite reads the
 * same handle and makes one claim per page, in both colour schemes: after the first
 * frame, neither diagnostics channel carries an authoring finding. Environment findings
 * (no adapter, no device, a preference the engine cannot query) are the honesty core
 * working and are not asserted away; everything else is a finding about the page's
 * own composition, which the skill's finish condition says is zero.
 *
 * Structural, not pixel: it runs on the default headless shell and does not need the
 * GPU project.
 */

import { expect, test, type Page } from "@playwright/test";

const SLUGS = [
  "music-player",
  "transit-ops",
  "photo-review",
  "film-festival",
  "park-trails",
  "product-launch",
  "exhibition",
  "start-page",
] as const;

/**
 * Codes a machine can produce that say nothing about the page. The list is the
 * complement of the authoring codes rather than a copy of `site.spec.ts`'s list, so a
 * code added to either channel later fails here until someone decides which it is.
 */
const ENVIRONMENT_CODES = new Set([
  "webgpu-unavailable",
  "webgpu-canvas-unavailable",
  "webgpu-device-lost",
  "webgpu-renderer-load-failed",
  "backdrop-filter-unsupported",
  "engine-known-defect",
  "engine-unrecognised",
  "reduced-transparency-undetectable",
]);

interface Reported {
  readonly code: string;
  readonly message: string;
}

async function authoringFindings(page: Page): Promise<string[]> {
  await page.waitForFunction(() => {
    const root = (window as unknown as { __vitrea?: { ready?: () => Promise<void> } }).__vitrea;
    return root !== undefined && root !== null;
  });
  // Two frames, so a finding raised on the first read phase has been reported.
  await page.evaluate(
    () => new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve))),
  );
  const reported = await page.evaluate(() => {
    const root = (
      window as unknown as {
        __vitrea: {
          diagnostics: { reported: readonly { code: string; message?: string }[] };
          scene: { diagnostics: { reported: readonly { code: string; message?: string }[] } };
        };
      }
    ).__vitrea;
    return [...root.diagnostics.reported, ...root.scene.diagnostics.reported].map(
      (entry): { code: string; message: string } => ({
        code: entry.code,
        message: entry.message ?? "",
      }),
    );
  });
  return (reported as Reported[])
    .filter((entry) => !ENVIRONMENT_CODES.has(entry.code))
    .map((entry) => `${entry.code}: ${entry.message}`);
}

for (const slug of SLUGS) {
  test.describe(`/gallery/${slug}/`, () => {
    for (const scheme of ["light", "dark"] as const) {
      test(`reports no authoring finding in the ${scheme} scheme`, async ({ page }) => {
        const errors: string[] = [];
        page.on("pageerror", (error) => errors.push(error.message));
        await page.emulateMedia({ colorScheme: scheme });
        await page.goto(`/gallery/${slug}/`);
        await page.waitForSelector("[data-vitrea-root]", { state: "attached" });
        expect(await authoringFindings(page)).toEqual([]);
        expect(errors).toEqual([]);
      });
    }
  });
}

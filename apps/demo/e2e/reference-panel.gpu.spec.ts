/**
 * The demo shows what was measured (claims §5.47).
 *
 * The reference pair's left panel is this browser rendering
 * `checkerboard__capsule-button__rest` — the same scene, the same raster and the
 * same material the calibration harness captures under
 * `packages/calibration/web-captures/`. Until §5.47 nothing checked that the two
 * renders were the same picture, and they were not: the harness hands the GPU a
 * raster the size of its stage, the site hands it a 320 px raster on a 1440 px
 * page, and the renderer mapped every texture over the whole viewport. The
 * panel showed a flat slab over one stretched checker cell while the harness
 * capture beside it in the matrix was translucent with the squares through it.
 *
 * So this compares the live panel against the harness capture, pixel for pixel,
 * on a real adapter. The two are produced by the same renderer over the same
 * bytes; what differs is the page around them, which the 320×200 crop excludes,
 * and the analysis readback's timing, which the warm-up absorbs. Measured over
 * the capsule's own box rather than the whole panel: the checkerboard outside
 * the surface is the same raster on both sides and would dilute any difference
 * to nothing. The tolerance is set from what was measured — the stretched
 * render sat 0.088 from the harness capture over that box in encoded luma (max
 * 0.19), the placed one 0.000 — so 0.02 (five code values) is a quarter of the
 * gap the fit opened, and the interior structure floor is the checkerboard
 * showing through at all.
 *
 * The capture lives beside this spec because `packages/calibration/web-captures/`
 * is not committed: `e2e/fixtures/checkerboard__capsule-button__rest__webgpu.png`
 * is a byte copy of the harness's own capture, and the `.cell.json` next to it is
 * the cell record it was taken under (engine, adapter, and the profile document's
 * digest). A recalibration that moves this scene's GPU capture moves this fixture
 * with it — copy both files again — or this test fails for the right reason: the
 * demo would no longer be showing what was measured.
 *
 * That is what happened at W29 G4, and the pair was re-copied: the runtime's
 * default material moved to macOS 27's document, the site draws the default, and
 * the committed macOS 26.5 copy became a picture of a material this page no
 * longer renders. That copy came from a scratch run,
 * `packages/calibration/results/2026-09-20-w29-g4-landing/harness-captures.sh`,
 * at `sha256:f42ddec1cf5a`.
 *
 * **And it then went stale silently, as the tracker's W22 entry says a hand-kept
 * copy does.** W30 to W36 moved the 0.5 documents' bytes at every seal and
 * nobody re-copied it; it stayed within the tolerance (a mean of 0.0003 from the
 * capture at the current documents, max 3 codes) and so nothing failed. W43 G3
 * (iii) re-copied both files byte for byte from the canonical
 * `web-captures/apple-macos-27.0-1x-light-standard-glass0.5/` tree, whose cell
 * names `sha256:85ad7f7e3e0d` and the receded `sha256:30fbe05986ae`
 * (png `16cd9de4…`, cell `9b5958b8…`), and added the first case below, which
 * fails when a committed capture's cell names a document whose bytes have since
 * moved, so the next seal that moves either document has to re-copy its pair.
 *
 * **The site draws a second position since W43 G3 (iii)** (charter clauses 13
 * and 14; claims §5.201): `?glass=0.25` builds the root with macOS 27's
 * clearer-glass document. Its capture is copied from the same canonical tree's
 * `-glass0.25` directory, into a directory of the same name here (png
 * `4adba9e6…`, cell `5292497…`, at `sha256:6d18c059eb42` / `4d5f23d9d312`), and
 * the comparison runs at both positions. Each panel must also be nearer its own
 * position's capture than the other position's: the two captures sit only 0.023
 * apart over this box, barely past the tolerance, so passing the tolerance alone
 * would not say which material drew.
 */
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { expect, test, type Page } from "@playwright/test";
import { PNG } from "pngjs";

const here = dirname(fileURLToPath(import.meta.url));
const repository = resolve(here, "../../..");
const SCENE = "checkerboard__capsule-button__rest";

/** Each glass position the site draws, the query that selects it, and its harness capture. */
const POSITIONS = [
  { glass: "0.5", query: "", directory: "fixtures" },
  {
    glass: "0.25",
    query: "?glass=0.25",
    directory: "fixtures/apple-macos-27.0-1x-light-standard-glass0.25",
  },
].map((position) => ({
  ...position,
  capture: resolve(here, position.directory, `${SCENE}__webgpu.png`),
  cell: resolve(here, position.directory, `${SCENE}__webgpu.cell.json`),
}));

const CANVAS = { width: 320, height: 200 };
/** The capsule's own box — scenes.json's 120×44, centred — in canvas px. */
const CAPSULE_BOX = { x: 100, y: 78, width: 120, height: 44 };
/** The capsule's interior, inside the rim and the lens band, in canvas px. */
const INTERIOR = { x: 130, y: 88, width: 60, height: 24 };

const MAX_MEAN_LUMA_DELTA = 0.02;
const MIN_INTERIOR_STD = 0.05;

async function gotoSite(page: Page, query: string): Promise<void> {
  await page.goto(`/${query}`);
  await page.waitForSelector("[data-vitrea-root]", { state: "attached" });
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
}

async function showSection(page: Page, id: string): Promise<void> {
  await page.evaluate((target) => {
    document.getElementById(target)?.scrollIntoView({ block: "center", behavior: "instant" });
  }, id);
  await expect(page.locator(`#${id}`)).toHaveAttribute("data-current", "");
}

const luma = (png: PNG, x: number, y: number): number => {
  const i = (y * png.width + x) * 4;
  const r = (png.data[i] ?? 0) / 255;
  const g = (png.data[i + 1] ?? 0) / 255;
  const b = (png.data[i + 2] ?? 0) / 255;
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
};

/** Mean |Δ encoded luma| between two 320×200 rasters over the capsule's own box. */
const boxDelta = (a: PNG, b: PNG): number => {
  let sum = 0;
  for (let y = CAPSULE_BOX.y; y < CAPSULE_BOX.y + CAPSULE_BOX.height; y += 1) {
    for (let x = CAPSULE_BOX.x; x < CAPSULE_BOX.x + CAPSULE_BOX.width; x += 1) {
      sum += Math.abs(luma(a, x, y) - luma(b, x, y));
    }
  }
  return sum / (CAPSULE_BOX.width * CAPSULE_BOX.height);
};

/** Every profile document a cell's `capturePath` names, with the twelve hex it recorded. */
const DOCUMENT_CLAUSE = /(?:materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})/g;

test.describe("the reference panel renders the harness capture", () => {
  test("each committed capture was taken at the documents on disk, at its own position", () => {
    for (const position of POSITIONS) {
      const cell = JSON.parse(readFileSync(position.cell, "utf8")) as {
        readonly sceneId: string;
        readonly renderer: string;
        readonly capturePath: string;
      };
      expect(cell.sceneId).toBe(SCENE);
      expect(cell.renderer).toBe("webgpu");
      const named = [...cell.capturePath.matchAll(DOCUMENT_CLAUSE)];
      expect(named.length, position.cell).toBeGreaterThan(0);
      expect(named[0]?.[1], position.cell).toBe(
        `packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass${position.glass}.json`,
      );
      for (const [, document = "", recorded] of named) {
        const onDisk = createHash("sha256")
          .update(readFileSync(resolve(repository, document)))
          .digest("hex")
          .slice(0, 12);
        expect(onDisk, `${document} has moved since ${position.cell} was copied`).toBe(recorded);
      }
    }
  });

  for (const position of POSITIONS) {
    const title = "the live panel matches the calibration harness's render of the same scene, "
      + `glass ${position.glass}`;
    test(title, async ({ page }) => {
      await gotoSite(page, position.query);
      await showSection(page, "reference");

      // A machine with no adapter renders the CSS tier, whose blur is the
      // engine's and not the renderer's; there is nothing to compare there.
      const tier = await page.evaluate(() => {
        const text = document.body.innerText;
        return text.includes("webgpu-unavailable") ? "css" : "webgpu";
      });
      test.skip(tier === "css", "no WebGPU adapter: the panel is on the CSS tier");

      // The picker opens on the capsule scene; say so rather than assume it.
      const picker = page.getByLabel("Scene");
      await picker.selectOption(SCENE);
      await expect(page.getByTestId("native-profile")).toContainText(
        `apple-macos-27.0-1x-light-standard-glass${position.glass}`,
      );
      // The raster is decoded and registered on load, the pyramid rebuilds on the
      // next frame, and the tone readback settles over a few more.
      await page.waitForTimeout(1200);

      const box = await page.locator('[data-cell="live"] .pair__raster').first().boundingBox();
      if (box === null) throw new Error("the live panel has no box");
      expect(Math.round(box.width)).toBe(CANVAS.width);
      expect(Math.round(box.height)).toBe(CANVAS.height);

      const live = PNG.sync.read(
        await page.screenshot({
          clip: { x: box.x, y: box.y, width: CANVAS.width, height: CANVAS.height },
        }),
      );
      const harness = PNG.sync.read(readFileSync(position.capture));
      const others = POSITIONS.filter((other) => other !== position)
        .map((other) => PNG.sync.read(readFileSync(other.capture)));
      expect([live.width, live.height]).toEqual([harness.width, harness.height]);

      const meanDelta = boxDelta(live, harness);
      const nearestOther = Math.min(...others.map((other) => boxDelta(live, other)));

      let interiorSum = 0;
      let interiorSq = 0;
      for (let y = INTERIOR.y; y < INTERIOR.y + INTERIOR.height; y += 1) {
        for (let x = INTERIOR.x; x < INTERIOR.x + INTERIOR.width; x += 1) {
          const value = luma(live, x, y);
          interiorSum += value;
          interiorSq += value * value;
        }
      }
      const n = INTERIOR.width * INTERIOR.height;
      const interiorMean = interiorSum / n;
      const interiorStd = Math.sqrt(Math.max(interiorSq / n - interiorMean * interiorMean, 0));

      test.info().annotations.push({
        type: "measurement",
        description:
          `glass ${position.glass}: mean |Δluma| ${meanDelta.toFixed(4)} from its own capture, `
          + `${nearestOther.toFixed(4)} from the other position's, `
          + `interior std ${interiorStd.toFixed(4)}`,
      });

      expect(
        meanDelta,
        `the live panel differs from the harness capture by a mean of ${meanDelta.toFixed(4)} in encoded luma`,
      ).toBeLessThan(MAX_MEAN_LUMA_DELTA);
      expect(
        meanDelta,
        "the live panel is nearer the other glass position's capture than its own",
      ).toBeLessThan(nearestOther);
      expect(
        interiorStd,
        `the checkerboard does not show through the capsule (interior std ${interiorStd.toFixed(4)})`,
      ).toBeGreaterThan(MIN_INTERIOR_STD);
    });
  }
});

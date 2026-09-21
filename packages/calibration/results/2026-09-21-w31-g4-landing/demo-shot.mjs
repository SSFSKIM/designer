/**
 * The demo's material stage, photographed at 2x in both schemes (W31 G4, claims §5.165 §4).
 *
 * W30 G4's `demo-shot.mjs` (`results/2026-09-20-w30-g4-landing/demo-shot.mjs`),
 * copied on that directory's convention with the shot unchanged and the reason
 * for it different.
 *
 * That gate photographed the material stage because the stage is the one place
 * on the site where three SPANS of one authored thickness sit side by side, and
 * its operator was the shadow's blur as a function of the span. This wave's
 * operator is the body's chroma, and the same stage is the right shot for a
 * second reason it already had: its backdrop is a saturated multi-lobe bloom
 * painted in `oklch` (`StageBackdrop.tsx`), so the three plates sit over
 * genuinely chromatic light rather than over the achromatic gradient the page
 * stage carries. A chroma retention over a grey backdrop is the identity, so a
 * shot of a grey stage would be a shot of nothing.
 *
 * Captured through the site's own renderer pin so the band is the WebGPU tier —
 * the fidelity target and the only tier that carries this operator at all — and
 * at `deviceScaleFactor: 2`.
 *
 *     node packages/calibration/results/2026-09-21-w31-g4-landing/demo-shot.mjs \
 *       --out ~/vitrea-w31-g4-scratch/demo
 *
 * Run against `pnpm --filter demo dev` on its usual port. Nothing is asserted
 * here; the reading is the picture.
 */
import { mkdirSync } from "node:fs";
import { chromium } from "@playwright/test";

const BASE = process.env.VITREA_DEMO_URL ?? "http://localhost:5173";
const outIndex = process.argv.indexOf("--out");
const OUT = outIndex === -1 ? "/tmp/w31-g4-demo" : process.argv[outIndex + 1];
mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch({ channel: "chromium" });

for (const scheme of ["light", "dark"]) {
  const page = await browser.newPage({
    viewport: { width: 1280, height: 900 },
    deviceScaleFactor: 2,
    colorScheme: scheme,
  });
  await page.goto(`${BASE}/?renderer=webgpu`);
  await page.waitForSelector("[data-vitrea-root]", { state: "attached" });
  // The site's scheme is a control on the page, not a query parameter: the root
  // is built at `"light"` and the switch moves it. Driving the control rather
  // than emulating `prefers-color-scheme` is also what a reader does, and the
  // page deliberately does NOT wire that media query to the material.
  await page.getByTestId("color-scheme-select").selectOption(scheme);
  // The stage the sweep lives on. `material` is the site's first mode and the
  // one whose three plates are the size sweep.
  await page.evaluate(() => {
    document.getElementById("material")?.scrollIntoView({ block: "center", behavior: "instant" });
  });
  await page.locator("#material").waitFor();
  // Past the material's own transition and one full frame of the ticker.
  await page.waitForTimeout(1200);
  const stage = page.locator(".stage").first();
  await stage.screenshot({ path: `${OUT}/demo-${scheme}.png` });
  const resolved = await page.evaluate(() => ({
    scheme: document.documentElement.dataset["colorScheme"] ?? "unknown",
  }));
  process.stdout.write(`${scheme}: ${JSON.stringify(resolved)} -> demo-${scheme}.png\n`);
  await page.close();
}

await browser.close();

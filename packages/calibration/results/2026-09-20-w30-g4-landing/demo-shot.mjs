/**
 * The demo's size sweep, photographed at 2x in both schemes (W30 G4, claims §5.160).
 *
 * The wave's operator is the outer shadow's blur as a function of the casting
 * span, and the demo has exactly one place where three spans of one authored
 * thickness sit side by side over one backdrop: the material stage's sweep, at
 * 40, 68 and 112 CSS px. Under 0.19.0 those three cast shadows of one width;
 * under 0.20.0 they cast 2.13, 4.75 and 11.06 CSS px of σ. That is the whole of
 * the operator on a real page, and it is what makes the harness bands beside it
 * evidence about the demo rather than about the harness.
 *
 * Captured through the site's own renderer pin so the band is the WebGPU tier —
 * the fidelity target — rather than whichever tier this machine happened to
 * resolve, and at `deviceScaleFactor: 2` so the shadow's edge is not a rounding
 * of itself.
 *
 *     node packages/calibration/results/2026-09-20-w30-g4-landing/demo-shot.mjs \
 *       --out ~/vitrea-w30-g4-scratch/demo
 *
 * Run against `pnpm --filter demo dev` on its usual port. Nothing is asserted
 * here; the reading is the picture.
 */
import { mkdirSync } from "node:fs";
import { chromium } from "@playwright/test";

const BASE = process.env.VITREA_DEMO_URL ?? "http://localhost:5173";
const outIndex = process.argv.indexOf("--out");
const OUT = outIndex === -1 ? "/tmp/w30-g4-demo" : process.argv[outIndex + 1];
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

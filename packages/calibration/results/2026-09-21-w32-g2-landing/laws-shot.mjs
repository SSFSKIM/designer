/**
 * The `/laws/` shadow stage, photographed at two spans in both poses (W32 G2;
 * Decision Log 1 (d) as ruled; claims §5.169 §4).
 *
 * W31 G4's `demo-shot.mjs` in shape and for the same purpose — a stage a wave
 * built is looked at rather than only asserted — with the stage changed. The
 * four shots are the two ends of what the section shows: the casting span at 96
 * and at 160, each focused and receded, so the σ law's grading and Decision Log
 * 2's stand-down are both in the picture rather than only in the readout.
 *
 * On the WebGPU tier, which is the fidelity target and the tier the exterior was
 * fitted on, at `deviceScaleFactor: 2`. The page's own control pins the pose, so
 * what the shot records is the pose the RUNTIME resolved and not one emulated
 * around it; the readout's endpoint line is printed beside each file for the
 * same reason.
 *
 *     node packages/calibration/results/2026-09-21-w32-g2-landing/laws-shot.mjs \
 *       --out ~/vitrea-w32-g2-scratch/laws
 *
 * Run against `pnpm --filter demo dev` on its usual port. Nothing is asserted
 * here; `e2e/laws.spec.ts` is where the readout is pinned to what the tier drew.
 */
import { mkdirSync } from "node:fs";
import { chromium } from "@playwright/test";

const BASE = process.env.VITREA_DEMO_URL ?? "http://localhost:5173";
const outIndex = process.argv.indexOf("--out");
const OUT = outIndex === -1 ? "/tmp/w32-g2-laws" : process.argv[outIndex + 1];
mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch({ channel: "chromium" });
const page = await browser.newPage({
  viewport: { width: 1280, height: 900 },
  deviceScaleFactor: 2,
});
await page.goto(`${BASE}/laws/?renderer=webgpu`);
await page.waitForSelector("[data-vitrea-root]", { state: "attached" });
await page.evaluate(() => {
  document.getElementById("shadow")?.scrollIntoView({ block: "center", behavior: "instant" });
});
await page.locator(".stage[data-mode='shadow']").first().waitFor();

for (const pose of ["active", "receded"]) {
  await page.getByTestId("shadow-pose").selectOption(pose);
  for (const span of ["96", "160"]) {
    await page.getByTestId("shadow-span").fill(span);
    // Past the material's own transition and a full frame of the ticker.
    await page.waitForTimeout(1200);
    const name = `laws-shadow-${pose}-${span}.png`;
    await page.locator(".stage").first().screenshot({ path: `${OUT}/${name}` });
    const read = await page.evaluate(() =>
      Object.fromEntries(
        ["shadow-endpoint", "shadow-sigma", "shadow-outset", "shadow-offset",
         "shadow-depth-3", "shadow-depth-12", "shadow-depth-24"].map((id) => [
          id,
          document.querySelector(`[data-testid="${id}"]`)?.textContent ?? "",
        ]),
      ),
    );
    process.stdout.write(`${name}\n  ${JSON.stringify(read)}\n`);
  }
}

await browser.close();

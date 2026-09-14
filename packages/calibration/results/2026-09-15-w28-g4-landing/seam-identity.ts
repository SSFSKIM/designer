/**
 * W28 G4, step 1: the calibration seam moved to the runtime pose, and the proof
 * that it moved no pixel (claims §5.148).
 *
 * Through G2 the calibration page merged the receded document itself and pinned the
 * root active; G4 hands the pose to the runtime. The two paths have to be the same
 * material or the matrix rows this wave publishes would describe a renderer nobody
 * ships. This script is the comparison, and it is deliberately not a metric: it
 * re-captures G2's own inactive cells through the NEW seam and compares the PNG's
 * SHA-256 with the one G2's frozen matrix recorded for that cell.
 *
 *   tsx results/2026-09-15-w28-g4-landing/seam-identity.ts --out /tmp/w28-g4-identity
 *
 * Three rules this file holds.
 *
 * **No native pixel is opened.** The comparison is web-against-web. Six of the 180
 * WebGPU rows are W28's spent holdout cells; re-capturing the WEB side of a cell
 * spends nothing, because a holdout is a native reading and no native fixture,
 * manifest entry or body-ΔE is touched here. Nothing in this file can produce a
 * fidelity number.
 *
 * **The capture is G2's, term for term.** Viewport, backing scale, context colour
 * scheme, accessibility overrides, the injected active document, the page URL, the
 * frame count and the `#stage` element screenshot are read from, or reproduced
 * exactly as, `2026-09-14-w28-g1-silhouette/frozen-read.ts`. The ONE difference is
 * the seam: `__vitreaRecededMaterialProfile` is not injected, so the page pins the
 * root `windowActivation: "inactive"` and the runtime merges the shipped receded
 * document. A byte that moves is then attributable to the seam and to nothing else.
 *
 * **A difference stops the wave, and a repeat cannot hide one.** A mismatching cell
 * is captured a second time: two loads that agree with each other and disagree with
 * G2 is a real difference in the material, while two loads that disagree with each
 * other is a non-deterministic page, and the report says which. Neither is a pass.
 */
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { chromium } from "@playwright/test";
import { createServer } from "vite";

const here = dirname(fileURLToPath(import.meta.url));
const pkg = resolve(here, "../..");
const repo = resolve(pkg, "../..");

const arg = (name: string, fallback?: string): string => {
  const index = process.argv.indexOf(`--${name}`);
  const value = index < 0 ? fallback : process.argv[index + 1];
  if (value === undefined) throw new Error(`Missing --${name}`);
  return value;
};
const json = (file: string): any => JSON.parse(readFileSync(file, "utf8"));
const sha = (data: Buffer | string): string => createHash("sha256").update(data).digest("hex");

const out = resolve(arg("out"));
if (!out.startsWith("/tmp/") && !out.startsWith("/private/tmp/")) {
  throw new Error(`--out must be scratch: ${out}`);
}
mkdirSync(out, { recursive: true });

const g2 = resolve(pkg, "results/2026-09-14-w28-g2-read");
const matrix = json(resolve(repo, "apps/reference-apple/scenes.json"));
const profileDoc = {
  light: json(resolve(pkg, "profiles/apple-macos-26.5-1x-light-standard.json")),
  dark: json(resolve(pkg, "profiles/apple-macos-26.5-1x-dark-standard.json")),
};

interface Row {
  readonly profile: string;
  readonly scene: string;
  readonly scale: number;
  readonly scheme: string;
  readonly a11yMode: string;
  readonly state: string;
  readonly isHoldout: boolean;
  readonly captureSha256: string;
}

/** Every inactive cell G2 read, on both tiers, in the order its matrices hold them. */
const planned: { readonly renderer: "webgpu" | "css"; readonly row: Row }[] = [
  ...(json(resolve(g2, "frozen-checking-matrix.json")).rows as Row[])
    .filter((row) => row.state === "inactive")
    .map((row) => ({ renderer: "webgpu" as const, row })),
  ...(json(resolve(g2, "css-matrix.json")).rows as Row[])
    .filter((row) => row.state === "inactive")
    .map((row) => ({ renderer: "css" as const, row })),
];
if (planned.length === 0) throw new Error("no inactive rows found in the G2 matrices");

const port = Number(arg("port", "5211"));
const server = await createServer({
  configFile: resolve(pkg, "web/vite.config.ts"),
  server: { port, strictPort: true },
});
await server.listen();
// The G2 recipe: the full Chromium binary, headed, on the hardware adapter.
const browser = await chromium.launch({
  channel: "chromium",
  headless: false,
  args: ["--enable-unsafe-webgpu", "--enable-features=Vulkan,WebGPU"],
});

interface Outcome {
  readonly renderer: string;
  readonly profile: string;
  readonly scene: string;
  readonly isHoldout: boolean;
  readonly expected: string;
  readonly observed: readonly string[];
  readonly identical: boolean;
  readonly windowActivation: string;
  readonly colorScheme: string;
  readonly recededApplied: boolean;
  readonly adapter: string;
}
const outcomes: Outcome[] = [];

try {
  for (const { renderer, row } of planned) {
    const scheme = row.scheme === "dark" ? "dark" : "light";
    const accessibility = {
      reducedTransparency: row.a11yMode !== "standard",
      increasedContrast: row.a11yMode === "increased-contrast",
      reducedMotion: false,
    };
    const context = await browser.newContext({
      viewport: { width: matrix.canvas.width, height: matrix.canvas.height },
      deviceScaleFactor: row.scale,
      colorScheme: scheme,
    });
    await context.addInitScript(
      ({ active, a11y }) => {
        window.__vitreaMaterialProfile = active;
        window.__vitreaAccessibilityOverrides = a11y;
      },
      { active: profileDoc[scheme].patch, a11y: accessibility },
    );

    const observed: string[] = [];
    let report: any;
    // One load, and a second only where the first disagrees: the page's determinism
    // is G2's own finding (`repeats: 2`, byte-identical), so a second load buys
    // nothing on an agreeing cell and is the only way to classify a disagreeing one.
    for (let attempt = 0; attempt < 2; attempt++) {
      const page = await context.newPage();
      await page.goto(
        `http://localhost:${port}/index.html?scene=${row.scene}&renderer=${renderer}` +
          `&scale=${row.scale}&frames=8`,
      );
      await page.waitForSelector("html[data-scene-ready='1'], html[data-scene-error]", {
        state: "attached",
      });
      const failure = await page.getAttribute("html", "data-scene-error");
      if (failure !== null) throw new Error(`${row.profile}/${row.scene}: ${failure}`);
      report = await page.evaluate(() => window.__vitreaCalibration.report);
      const png = await page.locator("#stage").screenshot({ animations: "disabled" });
      observed.push(sha(png));
      if (attempt === 0) {
        writeFileSync(
          resolve(out, `${renderer}__${row.profile}__${row.scene}.png`),
          png,
        );
      }
      await page.close();
      if (observed[0] === row.captureSha256) break;
    }
    await context.close();

    // The pose is asserted from the RESOLVED readout, not from the option: a cell
    // whose bytes matched because the recede never applied would be the one failure
    // a byte comparison alone cannot see.
    if (report.windowActivation !== "inactive") {
      throw new Error(
        `${row.profile}/${row.scene}: the root resolved windowActivation ` +
          `"${report.windowActivation}" on an inactive scene`,
      );
    }
    if (report.colorScheme !== scheme) {
      throw new Error(
        `${row.profile}/${row.scene}: the root resolved colorScheme ` +
          `"${report.colorScheme}" where the capture is ${scheme}`,
      );
    }
    if (report.recededMaterialProfile === null) {
      throw new Error(`${row.profile}/${row.scene}: no receded document reported`);
    }

    const identical = observed[0] === row.captureSha256;
    outcomes.push({
      renderer,
      profile: row.profile,
      scene: row.scene,
      isHoldout: row.isHoldout,
      expected: row.captureSha256,
      observed,
      identical,
      windowActivation: report.windowActivation,
      colorScheme: report.colorScheme,
      recededApplied: report.recededMaterialProfile !== null,
      adapter: `${report.adapter.vendor}/${report.adapter.architecture}`,
    });
    process.stderr.write(
      `${identical ? "=" : "!"} ${renderer} ${row.profile} ${row.scene}\n`,
    );
  }
} finally {
  await browser.close();
  await server.close();
}

const differing = outcomes.filter((outcome) => !outcome.identical);
const report = {
  gate: "W28 G4 — the calibration seam",
  claims: "§5.148",
  comparedAgainst: "packages/calibration/results/2026-09-14-w28-g2-read",
  seam: "windowActivation:'inactive' + explicit colorScheme; no candidate receded document",
  nativeFixturesOpened: 0,
  cells: outcomes.length,
  webgpuCells: outcomes.filter((outcome) => outcome.renderer === "webgpu").length,
  cssCells: outcomes.filter((outcome) => outcome.renderer === "css").length,
  holdoutCellsRecaptured: outcomes.filter((outcome) => outcome.isHoldout).length,
  identical: outcomes.length - differing.length,
  differing: differing.map((outcome) => ({
    renderer: outcome.renderer,
    profile: outcome.profile,
    scene: outcome.scene,
    expected: outcome.expected,
    observed: outcome.observed,
    classification:
      outcome.observed.length === 2 && outcome.observed[0] !== outcome.observed[1]
        ? "non-deterministic page"
        : "a real difference between the two seams",
  })),
  outcomes,
};
const reportPath = resolve(here, "seam-identity.json");
if (existsSync(reportPath)) throw new Error(`${reportPath} exists; refusing to overwrite evidence`);
writeFileSync(reportPath, `${JSON.stringify(report, undefined, 2)}\n`);

process.stderr.write(
  `\n${report.identical} / ${report.cells} byte-identical ` +
    `(${report.webgpuCells} webgpu, ${report.cssCells} css)\n`,
);
if (differing.length > 0) {
  process.stderr.write("A CELL DIFFERS. Do not publish a row.\n");
  process.exit(1);
}

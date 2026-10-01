/**
 * The scene page's own refusals, in the browser (W43 G0 (f)).
 *
 *   cd packages/calibration && npx tsx results/2026-10-01-w43-g0-declaration/seam/page-refusals.ts
 *
 * The drivers refuse first, and the unit suite pins those refusals; this checks the page,
 * which is what draws, by loading it with each injected state the drivers would never send
 * and reading its `data-scene-error`. Two green controls load a strict 0.5 read and the
 * scratch candidate, and report the drawn material's readout. Writes `page-refusals.txt`.
 */

import { writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { chromium } from "@playwright/test";
import { createServer } from "vite";

import { readCandidateDocument } from "../../../scripts/candidate-document";
import { readMaterialProfileFile } from "../../../scripts/material-profile-file";

const HERE = dirname(fileURLToPath(import.meta.url));
const PACKAGE = resolve(HERE, "../../..");
const GPU_ARGS = ["--enable-unsafe-webgpu", "--enable-features=Vulkan,WebGPU"];

const candidate = readCandidateDocument(join(HERE, "scratch-candidate/candidate.json"));
const light05 = readMaterialProfileFile(
  join(PACKAGE, "profiles/apple-macos-27.0-1x-light-standard-glass0.5.json"));
const stamp = { mode: "candidate", declaration: "scratch", declarationSha256: candidate.declarationSha256,
  cssTierMappingSha256: candidate.cssTierMappingSha256 };
const doc = candidate.document;
const { dark: _dark, ...recededLightOnly } = doc.receded;
void _dark;

type Injected = Record<string, unknown>;
const cases: { name: string; inject: Injected; expect: RegExp | "ready" }[] = [
  { name: "green: strict, the 0.5 key", expect: "ready",
    inject: { __vitreaMaterialProfileKey: light05.profileKey, __vitreaMaterialProfile: light05.patch } },
  { name: "green: candidate, the scratch 0.25 document", expect: "ready",
    inject: { __vitreaCandidateDocument: { stamp, document: doc } } },
  { name: "red: strict, a 0.25 key (unshipped pair)", expect: /ships no material at that pair/,
    inject: { __vitreaMaterialProfileKey: "apple-macos-27.0-1x-light-standard-glass0.25" } },
  { name: "red: strict, a macOS 27 key with no glass token", expect: /ships no material at that pair/,
    inject: { __vitreaMaterialProfileKey: "apple-macos-27.0-1x-light-standard" } },
  { name: "red: candidate beside an injected patch", expect: /refuses __vitreaMaterialProfile beside/,
    inject: { __vitreaCandidateDocument: { stamp, document: doc }, __vitreaMaterialProfile: light05.patch } },
  { name: "red: candidate beside an injected key", expect: /refuses __vitreaMaterialProfileKey beside/,
    inject: { __vitreaCandidateDocument: { stamp, document: doc },
      __vitreaMaterialProfileKey: light05.profileKey } },
  { name: "red: candidate beside a receded difference", expect: /refuses __vitreaRecededMaterialProfile/,
    inject: { __vitreaCandidateDocument: { stamp, document: doc },
      __vitreaRecededMaterialProfile: doc.receded.light.patch } },
  { name: "red: candidate beside a CSS mapping", expect: /refuses __vitreaCssTierMapping beside/,
    inject: { __vitreaCandidateDocument: { stamp, document: doc }, __vitreaCssTierMapping: {} } },
  { name: "red: partial candidate (no receded.dark)", expect: /partial: no receded\.dark endpoint/,
    inject: { __vitreaCandidateDocument: { stamp, document: { ...doc, receded: recededLightOnly } } } },
  { name: "red: candidate whose keys' glass token differs", expect: /glass token: /,
    inject: { __vitreaCandidateDocument: { stamp, document: { ...doc, glassTintAmount: 0.5 } } } },
  { name: "red: candidate naming the shipped document", expect: /names a shipped document/,
    inject: { __vitreaCandidateDocument: { stamp, document: { ...doc, name: "apple-macos-27.0-glass0.5" } } } },
];

const server = await createServer({ configFile: join(PACKAGE, "web/vite.config.ts") });
await server.listen();
const base = server.resolvedUrls!.local[0]!.replace(/\/$/, "");
const browser = await chromium.launch({ channel: "chromium", args: GPU_ARGS });
const lines = [`W43 G0 (f) page refusals, ${new Date().toISOString()}, chromium ${browser.version()}`];
let wrong = 0;
try {
  for (const c of cases) {
    const context = await browser.newContext({ viewport: { width: 320, height: 200 }, colorScheme: "light" });
    await context.addInitScript((injected: Injected) => {
      for (const [name, value] of Object.entries(injected)) (window as unknown as Injected)[name] = value;
    }, c.inject);
    const page = await context.newPage();
    await page.goto(`${base}/index.html?scene=photo__rrect-md__inactive&renderer=webgpu&scale=1&frames=8`);
    await page.waitForSelector("html[data-scene-ready='1'], html[data-scene-error]", { state: "attached" });
    const error = await page.getAttribute("html", "data-scene-error");
    let got: string;
    let ok: boolean;
    if (c.expect === "ready") {
      const report = await page.evaluate(() => window.__vitreaCalibration.report);
      got = error ?? `ready: mode=${report?.materialMode} material=${JSON.stringify(report?.material)} ` +
        `windowActivation=${report?.windowActivation}`;
      ok = error === null;
    } else {
      got = error ?? "ready (no refusal)";
      ok = error !== null && c.expect.test(error);
    }
    if (!ok) wrong += 1;
    lines.push(`${ok ? "ok   " : "WRONG"} ${c.name}\n        ${got}`);
    await context.close();
  }
} finally {
  await browser.close();
  await server.close();
}
lines.push(`wrong verdicts: ${wrong}`);
writeFileSync(join(HERE, "page-refusals.txt"), `${lines.join("\n")}\n`);
console.log(lines.join("\n"));
process.exitCode = wrong === 0 ? 0 : 1;

/** Propose response rows on supplying native cells; only GPU reads may select one. */
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { backdropToneResponse, DEFAULT_MATERIAL_PROFILE, withMaterialOverrides } from "../../../renderer-webgpu/src/material";
import { componentRegion } from "../../src/component-region";
import { decodePng, linearLuminance } from "../../src/image";
import { recededMaterialProfile } from "../../../platform-web/src/receded-profile";
import { admitFitRows } from "./admission";

const here = dirname(fileURLToPath(import.meta.url));
const repo = resolve(here, "../../../..");
const pkg = resolve(here, "../..");
const json = (path: string): any => JSON.parse(readFileSync(path, "utf8"));
const sha = (bytes: Buffer): string => createHash("sha256").update(bytes).digest("hex");
const partition = json(resolve(here, "partition.json"));
const plan = json(resolve(here, "sweep-plan.json"));
if (json(resolve(here, "mechanism-table.json")).passes !== true) throw new Error("Input check refused the fit");
const cells = partition.rows.filter((r: any) => r.role === "fit");
admitFitRows(cells, new Set(partition.holdout));
const baseline = json(resolve(here, "../2026-09-14-w27c-g1d/fitted-endpoint.json"));
const baseRows = new Map<string, any>(json(resolve(here,
  "../2026-09-14-w27c-g1d/frozen-checking-matrix.json")).rows.map((r: any) => [`${r.profile}/${r.scene}`, r]));
const matrix = json(resolve(repo, "apps/reference-apple/scenes.json"));
const targets: any[] = [];
for (const cell of cells) {
  const base = baseRows.get(cell.cell);
  const nativePath = base?.nativePath ?? resolve(repo, "apps/reference-apple/fixtures", cell.nativeFile);
  const bytes = readFileSync(nativePath);
  if (base !== undefined && sha(bytes) !== base.nativeSha256) throw new Error(`${cell.cell}: native bytes moved`);
  const image = decodePng(bytes);
  const scene = matrix.scenes.find((s: any) => s.id === cell.scene);
  const background = decodePng(readFileSync(resolve(repo, "apps/reference-apple/fixtures/backgrounds",
    `${scene.background}@${cell.scale}x.png`)));
  const region = componentRegion(matrix.components[scene.component], { canvas: matrix.canvas,
    scale: cell.scale, width: image.width, height: image.height });
  const luminance = linearLuminance(image);
  let n = 0, nativeY = 0, encoded = 0;
  for (let i = 0; i < luminance.length; i++) {
    if (region.signedDistancePx[i]! <= -6 * cell.scale) { n++; nativeY += luminance[i]!; }
    if (region.silhouette.mask[i] !== 0) encoded +=
      (0.2126 * background.data[i * 4]! + 0.7152 * background.data[i * 4 + 1]! +
        0.0722 * background.data[i * 4 + 2]!) / 255;
  }
  const span = Math.min(...region.placed.flatMap((s) => [s.width, s.height]));
  const t = Math.max(0, Math.min(1, (span - 32) / 64));
  targets.push({ cell: cell.cell, scheme: cell.scheme, source: nativePath,
    nativeSha256: sha(bytes), nativeY: nativeY / n, encoded: encoded / region.areaPx,
    thickness: t * t * (3 - 2 * t), span });
}
const out = resolve(here, "sweeps");
if (existsSync(out)) throw new Error("Refusing to replace proposed sweeps");
mkdirSync(out);
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value));
const write = (name: string, patch: any) => writeFileSync(resolve(out, `${name}.json`),
  `${JSON.stringify(patch, null, 2)}\n`);
write("baseline-source", baseline.patch);
write("baseline-silhouette", recededMaterialProfile);
const proposals: any[] = [];
for (const scheme of ["light", "dark"] as const) {
  const active = json(resolve(pkg, "profiles", `apple-macos-26.5-1x-${scheme}-standard.json`));
  const points = targets.filter((r) => r.scheme === scheme);
  const templates: any[] = [];
  if (scheme === "light") templates.push({ name: "light-three", xs: [0.1104, 0.2706, 0.9505] });
  const positions = scheme === "light" ? plan.light.thirdPositionsForFour : plan.dark.thirdPositions;
  for (const x of positions) {
    for (const middle of scheme === "light" ? [undefined] : plan.dark.middleRows) {
      templates.push({ name: `${scheme}-four-x${x}${middle ? `-m${middle[0]}` : ""}`,
        xs: [0.1104, 0.2706, x, 0.9505], middle });
    }
  }
  for (const template of templates) {
    const patch: any = clone(recededMaterialProfile);
    const row = patch[scheme];
    row.backdropToneAnchorX = template.xs;
    if (template.xs.length === 3) {
      row.backdropToneResponseThin = [plan.light.heldLow[0], 0.4, 0.929];
      row.backdropToneResponseThick = [plan.light.heldLow[1], 0.518, 0.9];
    } else if (scheme === "light") {
      row.backdropToneResponseThin = [plan.light.heldLow[0], 0.4, 0.65, 0.929];
      row.backdropToneResponseThick = [plan.light.heldLow[1], 0.518, 0.65, 0.9];
    } else {
      row.backdropToneResponseThin = [plan.dark.heldLow[0], template.middle[0], 0.12, plan.dark.initialFar[0]];
      row.backdropToneResponseThick = [plan.dark.heldLow[1], template.middle[1], 0.06, plan.dark.initialFar[1]];
    }
    const objective = () => {
      const material = withMaterialOverrides(withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, active.patch), row);
      return points.reduce((sum, p) => sum + Math.abs(Math.cbrt(Math.max(0,
        backdropToneResponse(p.encoded, p.thickness, material))) - Math.cbrt(p.nativeY)), 0) / points.length;
    };
    let best = objective();
    const trace: any[] = [];
    for (const step of plan.proposalSearch.coordinateStepLadder) {
      for (let pass = 0; pass < plan.proposalSearch.maximumPassesPerStep; pass++) {
        let improved = false;
        for (const key of ["backdropToneResponseThin", "backdropToneResponseThick"]) {
          for (let i = scheme === "dark" ? 2 : 1; i < template.xs.length; i++) {
            const original = row[key][i];
            let selected = original;
            for (const delta of [-step, step]) {
              row[key][i] = Math.min(1, Math.max(0, original + delta));
              const value = objective();
              if (value < best - 1e-12) { best = value; selected = row[key][i]; improved = true; }
            }
            row[key][i] = selected;
          }
        }
        if (!improved) break;
      }
      trace.push({ step, surrogateObjective: best });
    }
    for (const key of ["backdropToneResponseThin", "backdropToneResponseThick"]) {
      row[key] = row[key].map((n: number) => Number(n.toFixed(7)));
    }
    write(template.name, patch);
    proposals.push({ name: template.name, scheme, surrogateObjective: best, trace,
      anchors: row.backdropToneAnchorX, thin: row.backdropToneResponseThin, thick: row.backdropToneResponseThick });
  }
}
writeFileSync(resolve(here, "fit-model-proposals.json"), `${JSON.stringify({
  role: "Candidate generation only; no candidate selected by this surrogate", targets, proposals,
}, null, 2)}\n`);
console.log(`${proposals.length} response candidates proposed; GPU selection remains unread`);

/** W33 G0: FINISHED capture alpha, not the proposed stroke's alpha (§5.170).
 * Arrays are counterfactual composites over committed captures, never rendered
 * evidence. All measured gates use the calibration package's actual functions.
 */
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";
import {
  decodePng, componentRegion, extractSilhouette, silhouetteArea, silhouetteBodyCount,
  silhouetteIoU, contourDistance, type CalibrationImage, type DeclaredComponent,
} from "../../src/index";
import {
  DRAWN_ALPHA_THRESHOLD, DEFAULT_SILHOUETTE_THRESHOLD, DEFAULT_SILHOUETTE_CHROMA_THRESHOLD,
} from "../../cli/measure";
const here = import.meta.dirname;
const root = resolve(here, "../../../..");
const captures = process.env["VITREA_WEB_CAPTURES"] ?? resolve(root, "packages/calibration/web-captures");
const spec = JSON.parse(readFileSync(resolve(root, "apps/reference-apple/scenes.json"), "utf8"));
const matrix = JSON.parse(readFileSync(resolve(here, "../matrix.json"), "utf8"));
const holdout = new Set(spec.split.holdout);
const image = (p: string) => decodePng(readFileSync(p));
const all = matrix.cells.filter((c: any) => c.key.profileKey.startsWith("apple-macos-27.0-") &&
  c.tier === "texture" && c.shape?.declaredContourMaxWeb !== undefined);
const selected = all.filter((c: any) => c.fixtureSet !== "probe" && c.state !== "inactive");
const inventory = { all: all.length, atOne: all.filter((c: any) => c.shape.declaredContourMaxWeb.value === 1).length,
  selected: selected.length, selectedAtOne: selected.filter((c: any) => c.shape.declaredContourMaxWeb.value === 1).length };
const m2 = JSON.parse(readFileSync(resolve(here,
  "../2026-09-21-w32-g2-landing/chroma-cut.json"), "utf8")).cells;
const result: any[] = [];
const skipped: any[] = [];
for (const cell of all) {
  const p = cell.key.profileKey, s = cell.key.sceneId;
  if (holdout.has(s) || cell.fixtureSet === "recorded") continue;
  const scene = spec.scenes.find((v: any) => v.id === s);
  const base = resolve(captures, p, s, `${s}__webgpu`);
  if (!existsSync(`${base}__alpha.png`)) { skipped.push({ p, s, reason: "no alpha capture" }); continue; }
  const n = image(resolve(root, "apps/reference-apple/fixtures", p, `${s}.png`));
  const w = image(`${base}.png`), a = image(`${base}__alpha.png`);
  const scale = n.width / spec.canvas.width;
  const b = image(resolve(root, "apps/reference-apple/fixtures/backgrounds", `${scene.background}@${scale}x.png`));
  const region = componentRegion(spec.components[scene.component] as DeclaredComponent,
    { canvas: spec.canvas, scale, width: n.width, height: n.height });
  const extractor = { kind: "luminance-delta" as const, background: b,
    threshold: DEFAULT_SILHOUETTE_THRESHOLD, chromaThreshold: DEFAULT_SILHOUETTE_CHROMA_THRESHOLD,
    region: region.silhouette };
  const nativeSil = extractSilhouette(n, extractor);
  const nArea = silhouetteArea(nativeSil), nBodies = silhouetteBodyCount(nativeSil);
  const rBodies = silhouetteBodyCount(region.silhouette);
  const well = (area: number, bodies: number) => nArea >= .95 * region.areaPx &&
    area >= .95 * region.areaPx && nBodies <= rBodies && bodies <= rBodies;
  const outside: number[] = [], inside: number[] = [];
  for (let i = 0; i < region.signedDistancePx.length; i++) {
    const d = region.signedDistancePx[i]!;
    if (d >= 0 && d < 1) outside.push(i);
    if (d >= -1 && d < 0) inside.push(i);
  }
  // A one-parameter neutral source-over depth measured independently per cell.
  // This is the most favourable scalar black stroke in encoded least squares,
  // not an assertion that its colour family reproduces Apple's three channels.
  let xy = 0, xx = 0;
  for (const i of outside) for (let c = 0; c < 3; c++) {
    xy += n.data[4*i+c]! * w.data[4*i+c]!;
    xx += w.data[4*i+c]! ** 2;
  }
  const depth = Math.max(0, Math.min(1, 1 - xy / xx));
  const metrics = (colour: CalibrationImage, alpha: CalibrationImage) => {
    const drawn = extractSilhouette(alpha, { kind: "alpha", threshold: DRAWN_ALPHA_THRESHOLD });
    const silhouette = extractSilhouette(colour, extractor);
    const area = silhouetteArea(silhouette), bodies = silhouetteBodyCount(silhouette);
    return { declaredContourMaxWeb: contourDistance(drawn, region.silhouette).maxPx,
      declaredIoUWeb: silhouetteIoU(drawn, region.silhouette), drawnArea: silhouetteArea(drawn),
      silhouetteAreaWeb: area, silhouetteBodiesWeb: bodies, wellConditioned: well(area, bodies) };
  };
  const original = metrics(w, a);
  // The original metric is a guard against a stale capture generation or an
  // incorrect reconstruction. A capture tree matching only the document name
  // does not prove that its pixels are the row's pixels.
  for (const key of ["declaredContourMaxWeb", "declaredIoUWeb", "silhouetteAreaWeb", "silhouetteBodiesWeb"] as const) {
    if (Math.abs(original[key] - cell.shape[key].value) > 1e-9) {
      throw new Error(`${p}/${s}: ${key} ${original[key]} != matrix ${cell.shape[key].value}`);
    }
  }
  // Even an independently coloured stroke at every pixel cannot need LESS
  // source-over alpha than this. This oracle is a feasibility lower bound,
  // not a material candidate and not a fit.
  const oracleAlpha = { ...a, data: new Uint8Array(a.data) };
  let oracleCrossings = 0, oracleOverHalf = 0;
  for (const i of outside) {
    let needed = 0;
    for (let c=0;c<3;c++) {
      const W=w.data[4*i+c]!, N=n.data[4*i+c]!;
      needed=Math.max(needed,N<W ? (W-N)/W : N>W ? (N-W)/(255-W) : 0);
    }
    const A=a.data[4*i+3]!/255;
    const next=needed+A*(1-needed);
    oracleAlpha.data[4*i+3]=Math.round(next*255);
    if (needed>=.5) oracleOverHalf++;
    if (A<.5 && oracleAlpha.data[4*i+3]!/255>=.5) oracleCrossings++;
  }
  const oracle={...metrics(w,oracleAlpha), crossings:oracleCrossings, strokeAtLeastHalf:oracleOverHalf};
  const forms: any[] = [];
  for (const name of ["i-outside-measured", "ii-inside-measured", "iii-outside-0.49", "iv-held-coverage"]) {
    const colour = { ...w, data: new Uint8Array(w.data) };
    const alpha = { ...a, data: new Uint8Array(a.data) };
    const pixels = name.startsWith("ii-") ? inside : outside;
    const opacity = name.startsWith("iii-") ? .49 : depth;
    let infeasiblePixels = 0, infeasibleBeyondOne = 0, changedInteriorPixels = 0;
    let minAlpha = 1, maxAlpha = 0;
    let rgbError = 0;
    for (const i of pixels) {
      const A = a.data[4*i+3]! / 255;
      let feasible = true, withinOne = true, changed = false;
      for (let c = 0; c < 3; c++) {
        const W = w.data[4*i+c]!, N = n.data[4*i+c]!, B = b.data[4*i+c]!;
        let C: number;
        if (name === "iv-held-coverage") {
          // To hit the native composite at held A, premultiplied source must
          // be N-(1-A)*B, between 0 and 255*A in EVERY channel.
          const P = N - (1-A)*B;
          if (P < -1e-9 || P > 255*A+1e-9) feasible = false;
          if (P < -1 || P > 255*A+1) withinOne = false;
          C = Math.max(0, Math.min(255*A, P)) + (1-A)*B;
          alpha.data[4*i+c] = A === 0 ? 0 : Math.round(Math.max(0,Math.min(255*A,P))/A);
        } else {
          C = W * (1-opacity);
          const nextA = opacity + A*(1-opacity);
          // PNG stores unassociated RGB; composite in premultiplied form then
          // unassociate for the final counterfactual RGBA8 capture.
          alpha.data[4*i+c] = nextA === 0 ? 0 : Math.round(a.data[4*i+c]! * A*(1-opacity)/nextA);
          alpha.data[4*i+3] = Math.round(nextA*255);
        }
        colour.data[4*i+c] = Math.round(C);
        changed ||= colour.data[4*i+c] !== W;
        rgbError += Math.abs(N-colour.data[4*i+c]!);
      }
      if (!feasible) infeasiblePixels++;
      if (!withinOne) infeasibleBeyondOne++;
      if (changed && nativeSil.mask[i]) changedInteriorPixels++;
      minAlpha = Math.min(minAlpha,alpha.data[4*i+3]!/255);
      maxAlpha = Math.max(maxAlpha,alpha.data[4*i+3]!/255);
    }
    const after = metrics(colour, alpha);
    forms.push({ name, opacity: name === "iv-held-coverage" ? null : opacity,
      ringPixels: pixels.length, infeasiblePixels, infeasibleBeyondOne, changedInteriorPixels, minAlpha, maxAlpha,
      ringMAE: rgbError/(3*pixels.length), newlyThresholded: after.drawnArea-original.drawnArea,
      ...after });
  }
  result.push({ profile: p, scene: s, role: cell.fixtureSet, pose: cell.state,
    oracle,
    ringAlpha: [Math.min(...outside.map(i=>a.data[4*i+3]!/255)), Math.max(...outside.map(i=>a.data[4*i+3]!/255))],
    m2: m2.some((r: any)=>r.profile===p && r.scene===s),
    nativeInteriorRingPixels: inside.filter(i=>nativeSil.mask[i]).length, original, forms });
}
const summary = ["i-outside-measured", "ii-inside-measured", "iii-outside-0.49", "iv-held-coverage"].map(name => {
  const fs = result.map(r=>r.forms.find((f: any)=>f.name===name));
  return { name, cells: fs.length, contourFailures: fs.filter(f=>f.declaredContourMaxWeb>1).length,
    iouFailures: fs.filter(f=>f.declaredIoUWeb<.99).length,
    maxContour: Math.max(...fs.map(f=>f.declaredContourMaxWeb)), minIoU: Math.min(...fs.map(f=>f.declaredIoUWeb)),
    newlyThresholded: fs.reduce((sum,f)=>sum+f.newlyThresholded,0),
    selectedContourFailures: result.filter((r,i)=>r.role!=="probe" && r.pose!=="inactive" && fs[i].declaredContourMaxWeb>1).length,
    selectedIoUFailures: result.filter((r,i)=>r.role!=="probe" && r.pose!=="inactive" && fs[i].declaredIoUWeb<.99).length,
    selectedPredicateChanges: result.filter((r,i)=>r.role!=="probe" && r.pose!=="inactive" &&
      r.original.wellConditioned!==fs[i].wellConditioned).map((r)=>({profile:r.profile,scene:r.scene,
        before:r.original.wellConditioned,after:r.forms.find((f:any)=>f.name===name).wellConditioned})),
    predicateChanges: result.filter((r,i)=>r.original.wellConditioned!==fs[i].wellConditioned).map(r=>`${r.profile}/${r.scene}`),
    changedInteriorPixels: fs.reduce((sum,f)=>sum+f.changedInteriorPixels,0),
    infeasibleBeyondOneCells: fs.filter(f=>f.infeasibleBeyondOne>0).length,
    infeasibleCells: fs.filter(f=>f.infeasiblePixels>0).length,
    infeasiblePixels: fs.reduce((sum,f)=>sum+f.infeasiblePixels,0) };
});
const oracleSummary={cells:result.length,contourFailures:result.filter(r=>r.oracle.declaredContourMaxWeb>1).length,
  iouFailures:result.filter(r=>r.oracle.declaredIoUWeb<.99).length,
  crossings:result.reduce((sum,r)=>sum+r.oracle.crossings,0),
  selectedContourFailures:result.filter(r=>r.role!=="probe"&&r.pose!=="inactive"&&r.oracle.declaredContourMaxWeb>1).length,
  selectedIoUFailures:result.filter(r=>r.role!=="probe"&&r.pose!=="inactive"&&r.oracle.declaredIoUWeb<.99).length};
const output = { oracleSummary, threshold: DRAWN_ALPHA_THRESHOLD, inventory, includeHoldout: false, summary, skipped, rows: result };
writeFileSync(resolve(here, "forms.json"), `${JSON.stringify(output,null,2)}\n`);
console.log(JSON.stringify({ inventory, summary, oracleSummary, skipped },null,2));

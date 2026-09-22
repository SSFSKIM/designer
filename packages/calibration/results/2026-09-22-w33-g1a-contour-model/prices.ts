/** W33 G1a: FINISHED capture alpha, not the proposed stroke's alpha (§5.171).
 * Arrays are counterfactual composites over committed captures, never rendered
 * evidence. All measured gates use the calibration package's actual functions.
 */
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";
import {
  decodePng, componentRegion, linearLuminance, extractSilhouette, silhouetteArea, silhouetteBodyCount,
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
const eligible = all.filter((c: any) => !holdout.has(c.key.sceneId) && c.fixtureSet !== "recorded");
const selected = eligible.filter((c: any) => c.fixtureSet !== "probe" && c.state !== "inactive");
const inventory = { all: eligible.length, atOne: eligible.filter((c: any) => c.shape.declaredContourMaxWeb.value === 1).length,
  selected: selected.length, selectedAtOne: selected.filter((c: any) => c.shape.declaredContourMaxWeb.value === 1).length };
const m2 = JSON.parse(readFileSync(resolve(here,
  "../2026-09-21-w32-g2-landing/chroma-cut.json"), "utf8")).cells;
const targets = JSON.parse(readFileSync(resolve(here, "targets.json"), "utf8"));
if (targets.includeHoldout) throw new Error("G1a prices refuse holdout targets");
const targetMap = new Map(targets.rows.map((r: any) => [`${r.profile}/${r.scene}`, r]));
const result: any[] = [];
const skipped: any[] = [];
for (const cell of matrix.cells.filter((c: any) => all.includes(c) ||
  (c.tier === "texture" && targetMap.has(`${c.key.profileKey}/${c.key.sceneId}`)))) {
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
  const metrics = (colour: CalibrationImage, alpha: CalibrationImage) => {
    const drawn = extractSilhouette(alpha, { kind: "alpha", threshold: DRAWN_ALPHA_THRESHOLD });
    const silhouette = extractSilhouette(colour, extractor);
    const area = silhouetteArea(silhouette), bodies = silhouetteBodyCount(silhouette);
    return { declaredContourMaxWeb: cell.shape?.declaredContourMaxWeb ? contourDistance(drawn, region.silhouette).maxPx : null,
      declaredIoUWeb: cell.shape?.declaredIoUWeb ? silhouetteIoU(drawn, region.silhouette) : null, drawnArea: silhouetteArea(drawn),
      silhouetteAreaWeb: area, silhouetteBodiesWeb: bodies, wellConditioned: well(area, bodies) };
  };
  const original = metrics(w, a);
  // The original metric is a guard against a stale capture generation or an
  // incorrect reconstruction. A capture tree matching only the document name
  // does not prove that its pixels are the row's pixels.
  for (const key of ["declaredContourMaxWeb", "declaredIoUWeb", "silhouetteAreaWeb", "silhouetteBodiesWeb"] as const) {
    if (cell.shape?.[key] && Math.abs(original[key]! - cell.shape[key].value) > 1e-9) {
      throw new Error(`${p}/${s}: ${key} ${original[key]} != matrix ${cell.shape[key].value}`);
    }
  }
  const target: any = targetMap.get(`${p}/${s}`);
  if (target && JSON.stringify(target.indices) !== JSON.stringify(outside)) {
    throw new Error(`${p}/${s}: Python and production SDF shells differ`);
  }
  const webLum = linearLuminance(w), nativeLum = linearLuminance(n), bgLum = linearLuminance(b);
  let exteriorCount = 0, oldDeparture = 0, nativeDeparture = 0;
  for (let i=0; i<webLum.length; i++) if (!region.silhouette.mask[i]) {
    exteriorCount++;
    oldDeparture += bgLum[i]! - webLum[i]!;
    nativeDeparture += bgLum[i]! - nativeLum[i]!;
  }
  oldDeparture /= exteriorCount; nativeDeparture /= exteriorCount;
  if (Math.abs(oldDeparture-cell.shadow.meanDepartureWeb.value)>1e-10 ||
      Math.abs(nativeDeparture-cell.shadow.meanDepartureNative.value)>1e-10) {
    throw new Error(`${p}/${s}: departure does not reproduce the matrix`);
  }
  const forms: any[] = [];
  for (const name of ["candidate-exact", "candidate-capped", "oracle-exact", "oracle-capped"]) {
    if (name.startsWith("candidate") && !target) continue;
    const colour = { ...w, data: new Uint8Array(w.data) };
    const alpha = { ...a, data: new Uint8Array(a.data) };
    let infeasiblePixels = 0, changedInteriorPixels = 0;
    const error = [0,0,0], loss = [0,0,0];
    for (let j=0; j<outside.length; j++) {
      const i = outside[j]!;
      const T = name.startsWith("candidate") ? target.rgb[j] :
        [n.data[4*i]!,n.data[4*i+1]!,n.data[4*i+2]!];
      let needed = 0;
      for (let c=0; c<3; c++) {
        const B=b.data[4*i+c]!, N=T[c]!;
        needed=Math.max(needed, N<B ? (B-N)/B : N>B ? (N-B)/(255-B) : 0);
      }
      const oldA=a.data[4*i+3]!/255;
      let usedA=Math.max(oldA,Math.ceil(needed*255-1e-10)/255);
      if (name.endsWith("capped") && oldA<.5) usedA=Math.min(127/255,usedA);
      alpha.data[4*i+3]=Math.round(usedA*255);
      let feasible=true, changed=false;
      for (let c=0; c<3; c++) {
        const B=b.data[4*i+c]!, P=T[c]!-(1-usedA)*B;
        if (P < -1e-9 || P > 255*usedA+1e-9) feasible=false;
        // Solve a valid premultiplied replacement layer, then quantise its
        // stored unassociated RGBA8 BEFORE source-over onto the backdrop.
        const source=usedA===0 ? 0 : Math.round(Math.max(0,Math.min(255*usedA,P))/usedA);
        alpha.data[4*i+c]=source;
        const C=Math.round(source*usedA+(1-usedA)*B);
        colour.data[4*i+c]=C;
        error[c]! += Math.abs(n.data[4*i+c]!-C);
        loss[c]! += Math.abs(T[c]!-C);
        changed ||= C!==w.data[4*i+c];
      }
      if (!feasible) infeasiblePixels++;
      if (changed && nativeSil.mask[i]) changedInteriorPixels++;
    }
    const lum=linearLuminance(colour);
    let delta=0;
    for (const i of outside) if (!region.silhouette.mask[i]) delta+=webLum[i]!-lum[i]!;
    const offsets=[];
    for (let offset=1;offset<=6;offset++) {
      let pixels=0; const rgb=[0,0,0];
      for(let i=0;i<region.signedDistancePx.length;i++) {
        const d=region.signedDistancePx[i]!;
        if(d<offset-1 || d>=offset) continue;
        pixels++;
        for(let c=0;c<3;c++) rgb[c]!+=Math.abs(n.data[4*i+c]!-colour.data[4*i+c]!);
      }
      offsets.push({offset,pixels,maeRGB:rgb.map(v=>v/pixels)});
    }
    const after=metrics(colour,alpha);
    forms.push({name,ringPixels:outside.length,infeasiblePixels,changedInteriorPixels,
      ringMAE:error.reduce((a,b)=>a+b,0)/(3*outside.length),
      maeRGB:error.map(v=>v/outside.length),lossRGB:loss.map(v=>v/outside.length),
      newlyThresholded:after.drawnArea-original.drawnArea,
      departure:oldDeparture+delta/exteriorCount, offsets,...after});
  }
  result.push({profile:p,scene:s,role:cell.fixtureSet,pose:cell.state,
    hasCandidate:!!target,m2:m2.some((r:any)=>r.profile===p&&r.scene===s),
    nativeDeparture,oldDeparture,original,forms});
}
const summary=["candidate-exact","candidate-capped","oracle-exact","oracle-capped"].map(name=>{
  const rs=result.filter(r=>r.forms.some((f:any)=>f.name===name));
  const fs=rs.map(r=>r.forms.find((f:any)=>f.name===name));
  const selected=(r:any)=>r.role!=="probe"&&r.pose!=="inactive";
  return {name,cells:rs.length,conformanceCells:fs.filter(f=>f.declaredIoUWeb!==null).length,
    contourFailures:fs.filter(f=>f.declaredContourMaxWeb>1).length,
    iouFailures:fs.filter(f=>f.declaredIoUWeb!==null&&f.declaredIoUWeb<.99).length,
    uniqueRedCells:fs.filter(f=>f.declaredContourMaxWeb>1||f.declaredIoUWeb!==null&&f.declaredIoUWeb<.99).length,
    selectedCells:rs.filter(selected).length,
    selectedContourFailures:rs.filter((r,i)=>selected(r)&&fs[i].declaredContourMaxWeb>1).length,
    selectedIoUFailures:rs.filter((r,i)=>selected(r)&&(fs[i].declaredIoUWeb!==null&&fs[i].declaredIoUWeb<.99)).length,
    selectedUniqueRedCells:rs.filter((r,i)=>selected(r)&&
      (fs[i].declaredContourMaxWeb>1||(fs[i].declaredIoUWeb!==null&&fs[i].declaredIoUWeb<.99))).length,
    maxContour:Math.max(...fs.map(f=>f.declaredContourMaxWeb)),
    minIoU:Math.min(...fs.filter(f=>f.declaredIoUWeb!==null).map(f=>f.declaredIoUWeb)),
    newlyThresholded:fs.reduce((s,f)=>s+f.newlyThresholded,0),
    predicateChanges:rs.filter((r,i)=>r.original.wellConditioned!==fs[i].wellConditioned).length,
    areaChanges:rs.filter((r,i)=>r.original.silhouetteAreaWeb!==fs[i].silhouetteAreaWeb).length,
    bodiesChanges:rs.filter((r,i)=>r.original.silhouetteBodiesWeb!==fs[i].silhouetteBodiesWeb).length,
    nativeMaskPixelsTouched:fs.reduce((s,f)=>s+f.changedInteriorPixels,0),
    infeasibleCells:fs.filter(f=>f.infeasiblePixels>0).length,
    pooledMAE:fs.reduce((s,f)=>s+f.ringMAE*f.ringPixels,0)/fs.reduce((s,f)=>s+f.ringPixels,0),
    lossRGB:[0,1,2].map(c=>fs.reduce((s,f)=>s+f.lossRGB[c]*f.ringPixels,0)/fs.reduce((s,f)=>s+f.ringPixels,0))};
});
// The forecast keeps every member of the declared 166-row stop population.
// For cells outside the candidate's measured domain it assumes NO change,
// explicitly, rather than extrapolating a fitted single-shape law to a union.
const stopRows=JSON.parse(readFileSync(resolve(here,"../2026-09-21-w32-g2-landing/exterior-cut.json"),"utf8"))
  .rows.filter((r:any)=>r.tier==="webgpu"&&["calibration","validation"].includes(r.set)&&
    r.departure.native!==null&&r.departure.window.native!==null);
const forecasts=["candidate-exact","candidate-capped","oracle-exact","oracle-capped"].map(name=>{
  const readings=stopRows.map((stop:any)=>{
    const row=result.find(r=>r.profile===stop.profile&&r.scene===stop.scene);
    if(!row) return {profile:stop.profile,scene:stop.scene,pose:stop.state,changedDomain:false,
      before:Math.abs(stop.departure.web-stop.departure.native),
      after:Math.abs(stop.departure.web-stop.departure.native)};
    const f=row.forms.find((f:any)=>f.name===name);
    return {profile:row.profile,scene:row.scene,pose:row.pose,changedDomain:!!f,
      before:Math.abs(row.oldDeparture-row.nativeDeparture),
      after:Math.abs((f?.departure??row.oldDeparture)-row.nativeDeparture)};
  });
  const avg=(rs:any[],key:string)=>rs.reduce((s,r)=>s+r[key],0)/rs.length;
  const inactive=readings.filter((r:any)=>r.pose==="inactive");
  return {name,cells:readings.length,changedDomain:readings.filter((r:any)=>r.changedDomain).length,
    before:avg(readings,"before"),after:avg(readings,"after"),inactiveCells:inactive.length,
    inactiveBefore:avg(inactive,"before"),inactiveAfter:avg(inactive,"after"),rows:readings};
});
writeFileSync(resolve(here,"prices.json"),JSON.stringify({includeHoldout:false,threshold:DRAWN_ALPHA_THRESHOLD,
  inventory,summary,forecasts,skipped,rows:result})+"\n");
console.log(JSON.stringify({summary,forecasts:forecasts.map(({rows,...r})=>r),skipped},null,2));

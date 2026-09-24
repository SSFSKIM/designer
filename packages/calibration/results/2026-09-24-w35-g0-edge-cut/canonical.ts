/** Replay the actual W29 estimator and M2 mask; pixels enter only through guarded Python. */
import { spawnSync } from "node:child_process";
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";
import { componentRegion, decodePng, extractSilhouette, rimIntensity, interiorLevel,
  distanceToSeeds, type DeclaredComponent, type CanvasSize } from "../../src/index";
import { DEFAULT_SILHOUETTE_THRESHOLD, DEFAULT_SILHOUETTE_CHROMA_THRESHOLD } from "../../cli/measure";
const here=import.meta.dirname;
const root=resolve(here,"../../../..");
const spec=JSON.parse(readFileSync(resolve(root,"apps/reference-apple/scenes.json"),"utf8"));
const matrix=JSON.parse(readFileSync(resolve(here,"../matrix.json"),"utf8"));
const rows: unknown[]=[];
const requests=new Map<string,string>();
for (const row of matrix.cells) {
  const key=row.key;
  if (!key.profileKey.includes("27.0") || !key.profileKey.includes("standard") || row.tier!=="texture") continue;
  const sid=key.sceneId;
  if (![...spec.split.calibration,...spec.split.validation,...spec.split.probe].includes(sid)) continue;
  requests.set(key.profileKey+"/"+sid,"canonical");
}
const split=JSON.parse(readFileSync(resolve(here,"../2026-09-23-w34-g0-contour-bed/split.json"),"utf8"));
for (const scale of [1,2]) for (const scheme of ["light","dark"]) {
  const profile=`apple-macos-27.0-${scale}x-${scheme}-standard-glass0.5`;
  for (const sid of [...split.calibration,...split.validation]) {
    if (/^grey-\d+__circular-120__rest$/.test(sid)) requests.set(profile+"/"+sid,"w34");
  }
}
for (const [cell,source] of requests) {
  const p=spawnSync("python3.12",[resolve(here,"export-cell.py"),source,cell],
    {encoding:"utf8",maxBuffer:20*1024*1024});
  if(p.status!==0) throw new Error(`${cell}: ${p.stderr}`);
  const input=JSON.parse(p.stdout);
  const native=decodePng(Buffer.from(input.native,"base64"));
  const web=decodePng(Buffer.from(input.web,"base64"));
  const background=decodePng(Buffer.from(input.background,"base64"));
  const region=componentRegion(input.component as DeclaredComponent,{canvas:input.canvas as CanvasSize,
    scale:input.scale,width:native.width,height:native.height});
  const silhouette=extractSilhouette(native,{kind:"luminance-delta",background,
    threshold:DEFAULT_SILHOUETTE_THRESHOLD,chromaThreshold:DEFAULT_SILHOUETTE_CHROMA_THRESHOLD,
    region:region.silhouette});
  if(!silhouette.mask.some(Boolean)) { rows.push({cell,source,role:input.role,status:"empty native mask"});continue; }
  const complement=Uint8Array.from(silhouette.mask,v=>v?0:1);
  const distance=distanceToSeeds(complement,native.width,native.height);
  const erosion=[0,1,2,3].map(px=> {
    const interior={...silhouette,mask:Uint8Array.from(silhouette.mask,(v,i)=>v && distance[i]!>px?1:0)};
    return interior.mask.some(Boolean)
      ? {devicePx:px,native:interiorLevel(native,{interior}),web:interiorLevel(web,{interior})}
      : {devicePx:px,native:null,web:null};
  });
  const rimNative=rimIntensity(native,silhouette);const rimWeb=rimIntensity(web,silhouette);
  const profile=cell.split('/')[0];const sid=cell.split('/')[1];
  const stored=matrix.cells.find((r: any)=>r.key.profileKey===profile&&r.key.sceneId===sid&&r.tier==='texture');
  rows.push({cell,source,role:input.role,scale:input.scale,component:input.component,
    erosion,varianceRingFraction:erosion.slice(1).map(r=>r.web ? 1-r.web.stdDev**2/Math.max(erosion[0]!.web!.stdDev**2,1e-30) : null),
    nativeRim:rimNative,webRim:rimWeb,
    storedMaterial:stored?.material??null});
  console.log(cell,erosion.map(r=>r.web?.stdDev));
}
const target=resolve(here,"canonical-metrics.json");
if(existsSync(target)) throw new Error("Refuse to overwrite recorded metrics");
writeFileSync(target,JSON.stringify({threshold:DEFAULT_SILHOUETTE_THRESHOLD,
  chromaThreshold:DEFAULT_SILHOUETTE_CHROMA_THRESHOLD,erosionRule:"native mask & Euclidean distance to its complement > devicePx",
  missing:["mid-light-solid__rrect-md__rest: no canonical scene"],rows},null,2)+"\n");

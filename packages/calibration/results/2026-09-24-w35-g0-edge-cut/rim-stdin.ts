/** Existing rim estimator, receiving guarded bytes rather than opening an image path. */
import { readFileSync } from "node:fs";
import { componentRegion, decodePng, extractSilhouette, rimIntensity } from "../../src/index";
import { DEFAULT_SILHOUETTE_THRESHOLD, DEFAULT_SILHOUETTE_CHROMA_THRESHOLD } from "../../cli/measure";
const input=JSON.parse(readFileSync(0,"utf8"));
const n=decodePng(Buffer.from(input.native,"base64"));
const bg=decodePng(Buffer.from(input.background,"base64"));
const region=componentRegion(input.component,{canvas:input.canvas,scale:input.scale,width:n.width,height:n.height});
const mask=extractSilhouette(n,{kind:"luminance-delta",background:bg,
  threshold:DEFAULT_SILHOUETTE_THRESHOLD,chromaThreshold:DEFAULT_SILHOUETTE_CHROMA_THRESHOLD,
  region:region.silhouette});
console.log(JSON.stringify(rimIntensity(n,mask)));

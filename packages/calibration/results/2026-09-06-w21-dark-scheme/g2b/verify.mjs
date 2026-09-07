// The shipped chain with root.ts's gate, so the emitted numbers are the runtime's.
import { readFileSync } from "node:fs";
import {
  sourceOptics, sourceSize, sourceInteriorLight, resolvedBackdropTone, resolvedBackdropToneResponse,
  sizeThickness, sizeOcclusionAlphaAt, backdropToneAdaptation, toneRespondedSourceOptics,
  adaptedSourceOptics, innerShadowedSourceOptics, interiorShadowKeep, interiorBandLight,
  cssTierOptics, cssOpticsFromSource, CSS_TIER_MAPPING, cssTintFormAt, cssTierCompositeLevel,
} from "/Users/new/Developer/GitHub/designer/packages/platform-web/dist/index.js";
const R = "/Users/new/Developer/GitHub/designer/";
const E = (l) => { l = Math.min(1, Math.max(0, l)); return l <= 0.0031308 ? l*12.92 : 1.055*Math.pow(l,1/2.4)-0.055; };
const D = (e) => { e = Math.min(1, Math.max(0, e)); return e <= 0.04045 ? e/12.92 : Math.pow((e+0.055)/1.055,2.4); };
const lum = (c) => 0.2126*c[0]+0.7152*c[1]+0.0722*c[2];
const bd = JSON.parse(readFileSync("./backdrops.json","utf8"));
const scenes = JSON.parse(readFileSync(R+"apps/reference-apple/scenes.json","utf8")).components;
const geomOf = (c) => c === "capsule-button" ? {width:120,height:44,radius:22}
  : {width:scenes[c].size[0],height:scenes[c].size[1],radius:scenes[c].radius};
const cases = [["dark-solid","rrect-md"],["checkerboard","rrect-md"],["photo","rrect-md"],["photo","rrect-lg"],
  ["dark-solid","capsule-button"],["checkerboard","capsule-button"],["photo","capsule-button"],
  ["mid-dark-solid","capsule-button"],["impulse","capsule-button"],["light-solid","rrect-md"],
  ["hc-text","capsule-button"],["light-solid","capsule-button"]];
for (const [prof,scale] of [["apple-macos-26.5-1x-dark-standard","1x"],["apple-macos-26.5-1x-light-standard","1x"]]) {
  const patch = JSON.parse(readFileSync(R+"packages/calibration/profiles/"+prof+".json","utf8")).patch;
  const gpu = sourceOptics(patch), size = sourceSize(patch), il = sourceInteriorLight(patch);
  const tone = resolvedBackdropTone(patch), resp = resolvedBackdropToneResponse(patch);
  const base = cssTierOptics(patch, CSS_TIER_MAPPING);
  console.log(`\n== ${prof}`);
  console.log("scene".padEnd(32),"gated  gpuBody  cssBody  ratio   cssAlpha tint");
  for (const [bg,c] of cases) {
    const s = bd[`${bg}@${scale}`], g = geomOf(c);
    const thick = sizeThickness(Math.min(g.width,g.height), size);
    const k = backdropToneAdaptation(s.luminance, thick, tone);
    const occ = {...gpu.regular, tintAlpha: sizeOcclusionAlphaAt(gpu.regular.tintAlpha, thick, size)};
    const responded = toneRespondedSourceOptics(occ, s, thick, k, Math.min(1,Math.max(0,tone.max)), resp);
    const adapted = adaptedSourceOptics(responded, s.rgb, k);
    const ig = {widthCssPx:g.width,heightCssPx:g.height,radiusCssPx:g.radius,thicknessCssPx:8};
    const present = 1-k;
    const src = innerShadowedSourceOptics(adapted, interiorShadowKeep(gpu.regular, ig, thick, present, il));
    const X = interiorBandLight(gpu.regular, ig, present, il);
    const interior = { tintAlpha: src.tintAlpha, tint: src.tint, addedLight: X };
    const level = cssTierCompositeLevel(interior, s.luminance);
    const gated = cssTintFormAt(level) === "encoded";
    const anchor = gated ? { linearMean: s.linearLuminance, toneLevel: s.luminance } : undefined;
    const css = cssOpticsFromSource(base, src, CSS_TIER_MAPPING, anchor);
    const gpuBody = (1-src.tintAlpha)*s.linearLuminance + src.tintAlpha*lum(src.tint) + X;
    const cssBody = D((1-css.tintAlpha)*E(s.luminance) + css.tintAlpha*lum(css.tint.map(v=>v/255)));
    console.log(`${bg}__${c}`.padEnd(32), (gated?"YES  ":"no   "), gpuBody.toFixed(4).padStart(7),
      cssBody.toFixed(4).padStart(8), (gpuBody/cssBody).toFixed(3).padStart(7),
      css.tintAlpha.toFixed(4).padStart(8), String(css.tint[0]).padStart(4));
  }
}

import { readFileSync } from "node:fs";
import {
  sourceOptics, sourceSize, sourceInteriorLight, resolvedBackdropTone, resolvedBackdropToneResponse,
  sizeThickness, sizeOcclusionAlphaAt, backdropToneAdaptation, toneRespondedSourceOptics,
  adaptedSourceOptics, innerShadowedSourceOptics, interiorShadowKeep, interiorBandLight,
  backdropToneResponseLevel, cssTierOptics, cssOpticsFromSource, CSS_TIER_MAPPING, cssTintFormAt,
} from "/Users/new/Developer/GitHub/designer/packages/platform-web/dist/index.js";
const R = "/Users/new/Developer/GitHub/designer/";
const E = (l) => { l = Math.min(1, Math.max(0, l)); return l <= 0.0031308 ? l * 12.92 : 1.055 * Math.pow(l, 1/2.4) - 0.055; };
const D = (e) => { e = Math.min(1, Math.max(0, e)); return e <= 0.04045 ? e/12.92 : Math.pow((e+0.055)/1.055, 2.4); };
const lum = (c) => 0.2126*c[0] + 0.7152*c[1] + 0.0722*c[2];
const bd = JSON.parse(readFileSync("./backdrops.json", "utf8"));
const scenes = JSON.parse(readFileSync(R + "apps/reference-apple/scenes.json", "utf8"));
const comp = scenes.components;
const geomOf = (c) => c === "capsule-button" ? { width: 120, height: 44, radius: 22 }
  : { width: comp[c].size[0], height: comp[c].size[1], radius: comp[c].radius };

// The proposed conversion, written out so the table can show it beside the shipped one.
function solveAlpha(source, anchor) {
  const eb = E(anchor.toneLevel);
  const t = lum(source.tint);
  const span = E(t) - eb;
  if (Math.abs(span) < CSS_TIER_MAPPING.minimumTintContrast) return { alpha: Math.min(1, Math.max(0, source.tintAlpha)), degenerate: true, span };
  const composited = anchor.linearMean * (1 - source.tintAlpha) + t * source.tintAlpha;
  return { alpha: Math.min(1, Math.max(0, (E(composited) - eb) / span)), degenerate: false, span };
}

export function run(profilePath, scale, cases) {
  const patch = JSON.parse(readFileSync(profilePath, "utf8")).patch;
  const gpu = sourceOptics(patch), size = sourceSize(patch), il = sourceInteriorLight(patch);
  const tone = resolvedBackdropTone(patch), resp = resolvedBackdropToneResponse(patch);
  const base = cssTierOptics(patch, CSS_TIER_MAPPING);
  const rows = [];
  for (const [bg, c] of cases) {
    const s = bd[`${bg}@${scale}`], g = geomOf(c);
    const thick = sizeThickness(Math.min(g.width, g.height), size);
    const k = backdropToneAdaptation(s.luminance, thick, tone);
    const occ = { ...gpu.regular, tintAlpha: sizeOcclusionAlphaAt(gpu.regular.tintAlpha, thick, size) };
    const target = backdropToneResponseLevel(E(s.luminance), thick, resp);
    const nominal = (1 - occ.tintAlpha) * s.linearLuminance + occ.tintAlpha * lum(occ.tint);
    const responded = toneRespondedSourceOptics(occ, s, thick, k, Math.min(1, Math.max(0, tone.max)), resp);
    const adapted = adaptedSourceOptics(responded, s.rgb, k);
    const ig = { widthCssPx: g.width, heightCssPx: g.height, radiusCssPx: g.radius, thicknessCssPx: 8 };
    const present = 1 - k;
    const src = innerShadowedSourceOptics(adapted, interiorShadowKeep(gpu.regular, ig, thick, present, il));
    const X = interiorBandLight(gpu.regular, ig, present, il);
    const gpuBody = (1 - src.tintAlpha) * s.linearLuminance + src.tintAlpha * lum(src.tint) + X;
    const shipped = cssOpticsFromSource(base, src, CSS_TIER_MAPPING);
    const cssNow = D((1 - shipped.tintAlpha) * E(s.luminance) + shipped.tintAlpha * lum(shipped.tint.map((v) => v / 255)));
    const anchor = { linearMean: s.linearLuminance, toneLevel: s.luminance };
    const fixed = solveAlpha(src, anchor);
    const eb = E(anchor.toneLevel);
    const cssTintFixed = fixed.alpha <= CSS_TIER_MAPPING.minimumTintContrast ? src.tint.map(E)
      : [0,1,2].map((i) => Math.min(1, Math.max(0, (E(anchor.linearMean*(1-src.tintAlpha) + src.tint[i]*src.tintAlpha) - eb*(1-fixed.alpha))/fixed.alpha)));
    const cssFixed = D((1 - fixed.alpha) * eb + fixed.alpha * lum(cssTintFixed.map((v) => Math.round(v*255)/255)));
    const now = solveAlpha(src, { linearMean: CSS_TIER_MAPPING.referenceBackdropLuminance, toneLevel: CSS_TIER_MAPPING.referenceBackdropLuminance });
    rows.push({ scene: `${bg}__${c}`, bgLin: s.linearLuminance, bgEnc: E(s.luminance), thick, k,
      target, nominal, alpha: src.tintAlpha, tint: lum(src.tint), clamped: lum(src.tint) <= 1e-9,
      X, gpuBody, form: cssTintFormAt(gpuBody), degenerate: now.degenerate, spanNow: now.span,
      cssAlphaNow: shipped.tintAlpha, cssTintNow: shipped.tint[0], cssNow,
      cssAlphaFixed: fixed.alpha, cssTintFixed: Math.round(cssTintFixed[0]*255), cssFixed });
  }
  return rows;
}

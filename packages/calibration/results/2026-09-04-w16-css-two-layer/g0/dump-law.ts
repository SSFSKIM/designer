/**
 * W16 G0 — the law's own numbers, read out of `packages/platform-web/src/optics.ts`
 * rather than transcribed, so that every probe page and every prediction in
 * `g0-two-layer.md` is the shared profile's arithmetic and not a second opinion.
 *
 *   pnpm --filter @vitrea/calibration exec tsx \
 *     ../../packages/calibration/results/2026-09-04-w16-css-two-layer/g0/dump-law.ts
 */
import {
  MATERIAL_SOURCE_OPTICS,
  MATERIAL_SOURCE_SIZE,
  scatterDeepThickness,
  scatterGainAt,
  scatterRampReachDevicePx,
  scatterRampStart,
  scatterSharpShare,
  scatterThickness,
  sizeScatterSigmaAt,
} from "../../../../platform-web/src/optics";

const SPANS = [32, 44, 96, 128, 160] as const;
const EXTENTS: Record<number, readonly [number, number]> = {
  32: [64, 32], 44: [120, 44], 96: [160, 96], 128: [224, 128], 160: [280, 160],
};
const base = MATERIAL_SOURCE_OPTICS.regular.blurSigma;

const out: Record<string, unknown> = { blurSigma: base, size: MATERIAL_SOURCE_SIZE, spans: {} };
for (const dpr of [1, 2]) {
  for (const span of SPANS) {
    const gain = scatterGainAt(span, MATERIAL_SOURCE_SIZE, dpr);
    const kDeep = scatterDeepThickness(span, MATERIAL_SOURCE_SIZE, dpr);
    const start = scatterRampStart(dpr, MATERIAL_SOURCE_SIZE, span);
    const reach = scatterRampReachDevicePx(dpr, MATERIAL_SOURCE_SIZE);
    // The GPU tier's own widths at this ratio: the sharp σ is a DEVICE-pixel
    // quantity (W15 G1), so in CSS px it is `blurSigma / dpr`.
    const sharpCss = base / dpr;
    const heavyCss = sharpCss * gain;
    const areaMix = scatterThickness(span, 1, MATERIAL_SOURCE_SIZE, dpr, EXTENTS[span]);
    const ramp: Array<{ u: number; k: number }> = [];
    for (let u = 0; u <= 120; u += 1) {
      ramp.push({ u, k: 1 - scatterSharpShare(u, dpr, MATERIAL_SOURCE_SIZE, span) });
    }
    (out["spans"] as Record<string, unknown>)[`${span}@${dpr}x`] = {
      span, dpr, gain, kDeep, start, reachDevicePx: reach,
      sharpCss, heavyCss,
      heavyLayerCss: sharpCss * Math.sqrt(gain * gain - 1),
      areaMix,
      // what the tier writes today: one blur at the 1x law's projection
      cssTierSigmaToday: sizeScatterSigmaAt(
        base, scatterThickness(span, 1, MATERIAL_SOURCE_SIZE, 1, EXTENTS[span]),
        MATERIAL_SOURCE_SIZE, 1, span),
      ramp,
    };
  }
}
process.stdout.write(JSON.stringify(out, null, 1));

/**
 * W42 G0 rehearsal (charter clause 3): the shipped WebGPU body's constants, resolved from THIS
 * worktree's own material code for the four macOS 27 endpoints, both scales, and every surface
 * shape the canonical non-holdout bed draws.
 *
 * Grounding memo B's scratch resolver (`~/vitrea-w42/grounding/kernel/code-map/resolve.ts`,
 * hashed in `2026-09-29-w42-grounding/scratch-sha256.txt`) imported the same functions from the
 * main checkout by absolute path and covered five shapes. This copy imports them relative to the
 * worktree, adds rrect-lg (the probe bed's span 160) and the lens law's leaves the swap needs
 * (`shipped.py` displaces the body difference the way the optics pass displaces the body), and
 * drops the CSS-tier fields, which the rehearsal does not read. Every number is the code's.
 *
 *   pnpm exec tsx results/2026-09-29-w42-g0-declaration/gate/rehearsal/resolve.ts > resolved.json
 */
import {
  DEFAULT_MATERIAL_PROFILE,
  withMaterialOverrides,
  scatterGainAtScale,
  scatterGainFarAtScale,
  scatterFloorAtScale,
  scatterSpanMaxAtScale,
  scatterRampStart,
  scatterRampReachDevicePx,
  scatterHeavyShareThickAtScale,
  heavyTapSigmaAtScale,
  heavySecondTapSigmaAtScale,
  collapseTransmissionAtScale,
  type MaterialProfile,
} from "../../../../../renderer-webgpu/src/material.ts";
import {
  planPyramid,
  bodyBlurPlan,
  heavyTapPlan,
  chainLodForSigma,
  chainLevelSigma,
} from "../../../../../renderer-webgpu/src/pyramid-plan.ts";
import {
  macos27LightMaterialProfile,
  macos27DarkMaterialProfile,
  macos27RecededMaterialProfile,
} from "../../../../../platform-web/src/macos27-profile.ts";

type Endpoint = { name: string; material: MaterialProfile };
const lightActive = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, macos27LightMaterialProfile as never);
const darkActive = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, macos27DarkMaterialProfile as never);
const endpoints: Endpoint[] = [
  { name: "light-active", material: lightActive },
  {
    name: "light-receded",
    material: withMaterialOverrides(lightActive, macos27RecededMaterialProfile.light as never),
  },
  { name: "dark-active", material: darkActive },
  {
    name: "dark-receded",
    material: withMaterialOverrides(darkActive, macos27RecededMaterialProfile.dark as never),
  },
];

// [name, width, height, radius] in CSS px; toolbar-member is one capsule of toolbar-group.
const components = [
  ["capsule", 120, 44, 22],
  ["rrect-sm", 64, 32, 8],
  ["rrect-md", 160, 96, 20],
  ["rrect-ml", 224, 128, 27],
  ["rrect-lg", 280, 160, 34],
  ["toolbar-member", 44, 44, 22],
] as const;

const clamp01 = (x: number) => Math.min(1, Math.max(0, x));
const out: Record<string, unknown> = { endpoints: {} };

for (const e of endpoints) {
  const m = e.material;
  const reg = m.optics.regular;
  const fold = m.refractionScale["true"];
  const rec: Record<string, unknown> & { perScale: Record<string, unknown> } = {
    blurSigma: reg.blurSigma, tint: reg.tint, tintAlpha: reg.tintAlpha,
    sizeSpanMin: m.sizeSpanMin, sizeSpanMax: m.sizeSpanMax, sizeOcclusionGain: m.sizeOcclusionGain,
    sizeHeavyTapSigma: [m.sizeHeavyTapSigma, m.sizeHeavyTapSigma2x],
    heavySecond: [m.sizeHeavySecondSigma, m.sizeHeavySecondSigma2x, m.sizeHeavySecondShare],
    scaleCond: [m.sizeScatterScaleGain, m.sizeScatterScaleRef],
    bodyChromaRetention: m.bodyChromaRetention, bodyE3Strength: m.bodyE3Strength,
    backdropToneLow: m.backdropToneLow, backdropToneHigh: m.backdropToneHigh,
    backdropToneSizeBias: m.backdropToneSizeBias, backdropToneMax: m.backdropToneMax,
    anchorX: m.backdropToneAnchorX, thin: m.backdropToneResponseThin, thick: m.backdropToneResponseThick,
    responseStrength: m.backdropToneResponseStrength, sizeToneLevelFar: m.sizeToneLevelFar,
    black: [m.backdropToneBlackStrength, m.backdropToneBlackThin, m.backdropToneBlackThick],
    abscissa: m.backdropToneAbscissa ?? "source(default)",
    collapse: [m.collapseTransmission, m.collapseTransmission2x],
    fold,
    lensLaw: {
      refractionGain: m.lensRefractionGain, heightPerSpan: m.lensHeightPerSpan,
      heightMax: m.lensHeightMax, amountPerSpan: m.lensAmountPerSpan, amountMax: m.lensAmountMax,
      thicknessReference: m.lensThicknessReference, extentGain: m.lensExtentGain,
      profileExponent: m.lensProfileExponent, ovalization: m.lensOvalization,
      ovalizationSpanMin: m.lensOvalizationSpanMin, ovalizationSpanMax: m.lensOvalizationSpanMax,
    },
    perScale: {},
  };

  for (const dpr of [1, 2]) {
    const W = 320 * dpr, H = 200 * dpr;
    const plan = planPyramid(W, H, { scale: 1, maxDimension: 2048 });
    const bodySigmaTexels = (reg.blurSigma / dpr) * dpr;
    const bodyPlan = bodyBlurPlan(bodySigmaTexels, plan);
    const bodyChainLod = chainLodForSigma(bodySigmaTexels);
    const heavyDev = heavyTapSigmaAtScale(m, dpr);
    const heavySigmaCss = reg.blurSigma > 0 ? heavyDev / dpr : 0;
    const heavyPlan = heavySigmaCss > 0 ? heavyTapPlan(heavySigmaCss * dpr, plan) : undefined;
    const floor = scatterFloorAtScale(m, dpr);
    const spanTop = scatterSpanMaxAtScale(m, dpr);
    const startThin = scatterRampStart(dpr, m, 0);
    const startThick = scatterRampStart(dpr, m, m.sizeSpanMax);
    const startFar = scatterRampStart(dpr, m, spanTop);
    const reachDev = scatterRampReachDevicePx(dpr, m);
    const thickLift = scatterHeavyShareThickAtScale(m, dpr);
    const gainNear = scatterGainAtScale(m, dpr);
    const gainFar = scatterGainFarAtScale(m, dpr);
    const sc: Record<string, unknown> & { components: Record<string, unknown> } = {
      plan: { levels: plan.levels.map((l) => [l.width, l.height]), maxLod: plan.maxLod },
      bodySigmaTexels, bodyPlan, bodyChainLod, bodyLevelMeasuredSigma: chainLevelSigma(bodyPlan.level),
      heavyDevicePx: heavyDev, heavyPlan: heavyPlan ?? null,
      heavy2: heavySecondTapSigmaAtScale(m, dpr),
      gainNear, gainFar, floor, spanTop, startThin, startThick, startFar, reachDev,
      reachCss: reachDev / dpr, thickLift, collapseTransmission: collapseTransmissionAtScale(m, dpr),
      components: {},
    };
    for (const [name, w, h] of components) {
      const span = Math.min(w, h);
      const thickT = clamp01((span - m.sizeSpanMin) / Math.max(m.sizeSpanMax - m.sizeSpanMin, 1e-6));
      const sizeThick = thickT * thickT * (3 - 2 * thickT);
      const sizeK = clamp01(sizeThick * fold);
      const deepT = clamp01((span - m.sizeSpanMin) / Math.max(spanTop - m.sizeSpanMin, 1e-6));
      const kDeep = clamp01(floor + (1 - floor) * deepT * deepT * (3 - 2 * deepT) + thickLift * sizeThick);
      const farT = clamp01((span - m.sizeSpanMax) / Math.max(spanTop - m.sizeSpanMax, 1e-6));
      const farS = farT * farT * (3 - 2 * farT);
      const rampStart = startThin + (startThick - startThin) * sizeThick + (startFar - startThick) * farS;
      const gainEff = gainNear + (gainFar - gainNear) * farS;
      const scatterLod = Math.min(Math.max(bodyChainLod + Math.log2(Math.max(gainEff, 1e-4)), 0), plan.maxLod);
      sc.components[name] = {
        span, sizeThick, sizeK, kDeep, sDeep: 1 - kDeep, farS, rampStart, gainEff, scatterLod,
        sizedAlpha: reg.tintAlpha + m.sizeOcclusionGain * sizeK * (1 - reg.tintAlpha),
      };
    }
    rec.perScale[`${dpr}x`] = sc;
  }
  (out.endpoints as Record<string, unknown>)[e.name] = rec;
}
process.stdout.write(`${JSON.stringify(out, null, 1)}\n`);

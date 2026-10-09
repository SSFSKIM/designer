/**
 * W50 G1 pre-fit numericalRehearsal: replay G0's full synthetic rehearsal (§5.217 §6) through
 * the sealed producer `audit/numerical.ts`, in its authorised (post-seal) runtime mode.
 *
 * The profile is the explicit synthetic test profile of `audit/numerical.test.ts`, placed in all
 * four dark endpoint slots. It is not a shipped, fitted or native material, and no measured
 * structured argument is supplied, so the producer must return UNMEASURED: a synthetic rehearsal
 * can never stand in for a candidate's numericalReferee. What it does establish is that the
 * composed CPU uniform response over the FULL declared domain (inputs 0-64 at 1/64 code, every
 * integer span 32-224, both scales, positions and poses) has zero running drawdown, a fixed64
 * join, intact stand-downs and no negative pre-clamp neutral request, with the numbers G0
 * recorded in `evidence/synthetic-rehearsal.json`.
 */
import { evaluateNumerical, FULL_DOMAIN, loadRuntime, type NumericalEndpoint } from
  "../../2026-10-08-w50-g0-declaration/audit/numerical.ts";

await loadRuntime({ discovery: false });

const profile = {
  lowEndStrength: 1,
  lowEnd44: [20 / 255, 28 / 255, 50 / 255, 64 / 255] as const,
  lowEnd96: [24 / 255, 32 / 255, 54 / 255, 68 / 255] as const,
  lowEnd160: [28 / 255, 36 / 255, 58 / 255, 72 / 255] as const,
  backdropToneAnchorX: [0.004, 0.11, 0.425, 0.95] as const,
  backdropToneResponseThin: [0.08, 0.15, 0.2, 0.35] as const,
  backdropToneResponseThick: [0.1, 0.17, 0.25, 0.4] as const,
  backdropToneSizeBias: 1, backdropToneLow: 0, backdropToneHigh: 0.001,
  optics: { regular: { tint: [0.08, 0.08, 0.08] as const, tintAlpha: 0.8 } },
  sizeOcclusionGain: 0,
};
const endpoints: NumericalEndpoint[] = [0.25, 0.5].flatMap((position) =>
  (["active", "receded"] as const).map((pose) => ({ position, pose, profile })));

const started = performance.now();
const report = await evaluateNumerical(endpoints, [], FULL_DOMAIN);
const { structuredArguments: _a, structuredArgumentIds: _b, ...summary } = report;
console.log(JSON.stringify({ ...summary, wallSeconds: (performance.now() - started) / 1000 }, null, 1));

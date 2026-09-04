/**
 * W18 G0 (b) — the instrument's scratch profile documents, W17 G0's with one term added.
 *
 * The per-term attribution reads both tiers' captures under a profile that declines one of the
 * renderer's per-pixel terms at a time. Two properties make that a separation rather than a sweep.
 * The decline is a data change through the `--material-profile` seam, which is the same
 * `withMaterialOverrides` seam the renderer's isolation proof uses, so no shader, no committed
 * profile and no canonical capture is touched. And the CSS tier derives its own material from the
 * SAME profile document (`optics.ts`), so a declined term is declined on both tiers — which is
 * exactly what makes the CSS-minus-GPU difference under each decline a statement about that term's
 * share of the residual rather than about the term itself.
 *
 * `resolvedMaterialSha256` is dropped rather than recomputed, for W17 G0's reason: it is a
 * fingerprint over a COMMITTED profile's fully resolved material, nothing in `cli/` or `scripts/`
 * verifies it, and a stale hash in a scratch document would be a number that looks checked.
 *
 * The five terms, and the field that stands each one down:
 *
 *  - **the lens** — `lensRefractionGain` (the shader's `ou.lens.y`, the factor on the whole
 *    displacement magnitude) and `lensAmountMax` (the cap on the amount law that magnitude is built
 *    from). Both, as W17 G0 declined them, so the decline does not depend on where a span sits on
 *    the law.
 *  - **the rim's ambient term** — `optics.<variant>.rimAlpha`, `ou.rim.y`, the unlit edge
 *    brightness added as `rw * (rimAlpha + spec)`.
 *  - **the highlight** — `optics.<variant>.specularGain`, `ou.rim.w`, the lit half of that same
 *    added band.
 *  - **the outer shadow's lift** — `outerShadow.liftAmplitude`, added as
 *    `liftEncoded * (1 - coverage)` and therefore predicted to read zero inside the silhouette.
 *  - **the whole outer shadow** — every occlusion anchor and the lift at zero. Not one of the
 *    charter's five, and added because the separation in (a) puts a term on the NEIGHBOURS that the
 *    renderer does not carry: the tier draws a real shadow element per host, and a sibling's shadow
 *    is part of what a host's own `backdrop-filter` samples, where the renderer composites the
 *    group's shadow after it samples. Declining the shadow entirely is the measurement that tells
 *    that mechanism from every other thing a neighbour could be doing.
 *  - **the inner shadow** — `optics.<variant>.shadowAlpha`, the amplitude of the term the tier
 *    mirrors as `interiorShadowKeep`'s `1 - P̄·shadowDepth·shadowAlpha`. The AMPLITUDE and not
 *    `shadowDepth`: the depth also feeds `shadowDepthPx`, so zeroing it would decline a second
 *    quantity at the same time, and this wave's whole question is which term owns which share.
 *    The inner shadow is W18's addition to W17 G0's four, because it is the one term the tier
 *    carries through a co-area integral over the surface's own box — M1's leading candidate.
 *
 * Both variants are declined, not only `regular`: the bed draws `regular` throughout, so declining
 * `clear` changes no pixel, and declining both means the document states the term rather than the
 * bed's use of it.
 *
 * Usage: `node make-profiles.mjs <outDir>`.
 */

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const PROFILES = resolve(import.meta.dirname, "..", "..", "..", "profiles");

/** The declines, by configuration name. `optics` is applied to every variant. */
const DECLINES = {
  "no-lens": { lensRefractionGain: 0, lensAmountMax: 0 },
  "no-rim": { optics: { rimAlpha: 0 } },
  "no-highlight": { optics: { specularGain: 0 } },
  "no-lift": { outerShadow: { liftAmplitude: 0 } },
  "no-inner-shadow": { optics: { shadowAlpha: 0 } },
  "no-outer-shadow": {
    outerShadow: {
      thinOcclusionDark: 0,
      thinOcclusionMid: 0,
      thinOcclusionBright: 0,
      thickOcclusionAt96: 0,
      thickOcclusionAt128: 0,
      thickOcclusionAt160: 0,
      liftAmplitude: 0,
      reducedTransparencyOcclusion: 0,
    },
  },
  "all-declined": {
    lensRefractionGain: 0,
    lensAmountMax: 0,
    optics: { rimAlpha: 0, specularGain: 0, shadowAlpha: 0 },
    outerShadow: { liftAmplitude: 0 },
  },
};

const VARIANTS = ["regular", "clear"];

function decline(document, fields) {
  const patch = structuredClone(document.patch ?? {});
  for (const [key, value] of Object.entries(fields)) {
    if (key === "optics") {
      patch.optics ??= {};
      for (const variant of VARIANTS) patch.optics[variant] = { ...patch.optics[variant], ...value };
    } else if (key === "outerShadow") {
      patch.outerShadow = { ...patch.outerShadow, ...value };
    } else {
      patch[key] = value;
    }
  }
  const out = { ...document, patch };
  delete out.resolvedMaterialSha256;
  return out;
}

const outDir = process.argv[2];
if (outDir === undefined) throw new Error("usage: node make-profiles.mjs <outDir>");
mkdirSync(outDir, { recursive: true });

// The light document only: W18's separation is the standard LIGHT profile's, at both scales, and
// a dark document nothing reads would be an artefact with no run behind it.
const path = resolve(PROFILES, "apple-macos-26.5-1x-light-standard.json");
const document = JSON.parse(readFileSync(path, "utf8"));
for (const [name, fields] of Object.entries(DECLINES)) {
  const written = decline(document, fields);
  written["$comment-w18-g0"] = [
    `W18 G0's instrument: ${path} with the "${name}" decline written into its patch.`,
    "Scratch only — never committed under packages/calibration/profiles/, never used for a",
    "canonical capture. resolvedMaterialSha256 is dropped rather than recomputed; see",
    "make-profiles.mjs for why.",
  ];
  const file = resolve(outDir, `w18-g0-${name}-light.json`);
  writeFileSync(file, `${JSON.stringify(written, null, 2)}\n`);
  process.stdout.write(`${file}\n`);
}

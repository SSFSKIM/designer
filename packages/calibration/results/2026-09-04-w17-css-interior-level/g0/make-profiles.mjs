/**
 * W17 G0 — the instrument's scratch profile documents.
 *
 * The attribution reads the renderer's own captures under a profile that declines one term at a
 * time, on the precedent of the isolation proof (`packages/renderer-webgpu/e2e/golden/
 * isolation.spec.ts`), which renders a golden scene under an old profile injected through the
 * `materialProfile` seam and attributes the whole visual delta to the constants the patch names.
 * The same seam is what `--material-profile` drives, so a decline is a data change and no shader,
 * no committed profile and no canonical capture is touched.
 *
 * Each document is the committed profile document with the declined fields written into its
 * `patch`, so a declined render differs from the default render in exactly those fields and in
 * nothing else. `capture-web.ts` hashes the FILE, so every configuration lands under its own cell
 * key in the scratch matrix and no two rows can be confused. `resolvedMaterialSha256` is dropped
 * rather than recomputed: it is a fingerprint over the fully resolved material of a COMMITTED
 * profile, only `packages/calibration/test/tuned-profiles.test.ts` reads it, and that test resolves
 * `profiles/apple-macos-26.5-1x-{light,dark}-standard.json` by name — nothing in `cli/`, `src/` or
 * `scripts/` verifies it at all, so leaving a stale hash in a scratch document would be a number
 * that looks checked and is not.
 *
 * The four terms, and why each field is the one that stands the term down:
 *
 *  - **the lens** — `lensRefractionGain` is the shader's `ou.lens.y`, the factor on the whole
 *    displacement magnitude, and `lensAmountMax` caps the amount law that magnitude is built from.
 *    Either alone would zero the displacement; the charter names both, and naming both makes the
 *    decline independent of which end of the law a span happens to sit on.
 *  - **the rim's ambient term** — `optics.<variant>.rimAlpha` is `ou.rim.y`, the unlit edge
 *    brightness added as `rw * (rimAlpha + spec)`.
 *  - **the highlight** — `optics.<variant>.specularGain` is `ou.rim.w`, the lit half of the same
 *    added term. (The highlight PASS — the travelling sweep and the press glow — is a separate
 *    plane and is not drawn on a bed cell at rest; §2 of the findings records the check.)
 *  - **the outer shadow's lift** — `outerShadow.liftAmplitude`, the second term of W14 G1's
 *    shadow, which the shader adds as `liftEncoded * (1 - coverage)` and which should therefore
 *    read zero everywhere the coverage is full.
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
  "all-declined": {
    lensRefractionGain: 0,
    lensAmountMax: 0,
    optics: { rimAlpha: 0, specularGain: 0 },
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

for (const scheme of ["light", "dark"]) {
  const path = resolve(PROFILES, `apple-macos-26.5-1x-${scheme}-standard.json`);
  const document = JSON.parse(readFileSync(path, "utf8"));
  for (const [name, fields] of Object.entries(DECLINES)) {
    const written = decline(document, fields);
    written["$comment-w17-g0"] = [
      `W17 G0's instrument: ${path} with the "${name}" decline written into its patch.`,
      "Scratch only — never committed under packages/calibration/profiles/, never used for a",
      "canonical capture. resolvedMaterialSha256 is dropped rather than recomputed; see",
      "make-profiles.mjs for why.",
    ];
    const file = resolve(outDir, `w17-g0-${name}-${scheme}.json`);
    writeFileSync(file, `${JSON.stringify(written, null, 2)}\n`);
    process.stdout.write(`${file}\n`);
  }
}

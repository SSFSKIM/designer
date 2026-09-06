/**
 * W21 G0 — the two scratch material-profile documents vitrea's diagnostic renders use.
 *
 * Both are the SHIPPED dark document with one thing changed each, written to scratch and never to
 * `packages/calibration/profiles/`: G0 is a spike and re-records nothing. The endpoint document
 * turns the response law on at the LIGHT reference's anchors, which is the far end of the mix's
 * reachable span and not a proposal; the candidate document turns it on at the anchors the dark
 * probe measured, which is where G1 starts.
 *
 * `resolvedMaterialSha256` is deliberately left as the shipped document's value and marked in the
 * copy's own comment: these documents are diagnostics that never enter `profiles/`, the fingerprint
 * test does not read them, and a fabricated hash beside a changed patch would be worse than an
 * honest stale one that says so.
 *
 * Usage: node make-candidate-profiles.mjs <darkProfileDoc> <outDir> <anchorsJson>
 *
 * `anchorsJson` is `{ "thin": [a,b,c], "thick": [a,b,c], "anchorX": [a,b,c] }` — the six anchors and
 * their inputs as `read.py` measured them on the probe. Omit it and only the endpoint document is
 * written.
 */

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const [, , docPath, outDir, anchorsPath] = process.argv;
if (docPath === undefined || outDir === undefined) {
  throw new Error("usage: make-candidate-profiles.mjs <darkProfileDoc> <outDir> [anchorsJson]");
}
mkdirSync(outDir, { recursive: true });
const doc = JSON.parse(readFileSync(docPath, "utf8"));

function write(name, note, mutate) {
  const copy = JSON.parse(JSON.stringify(doc));
  copy["$comment-w21-g0"] = note;
  mutate(copy.patch);
  const path = join(outDir, name);
  writeFileSync(path, `${JSON.stringify(copy, null, 2)}\n`);
  process.stdout.write(`${path}\n`);
}

write(
  "endpoint-strength1-light-anchors.json",
  [
    "W21 G0 DIAGNOSTIC — scratch only, never committed to profiles/.",
    "The shipped dark document with backdropToneResponseStrength moved 0 -> 1 and nothing else.",
    "The response law therefore runs on the LIGHT reference's anchors, which is the far end of",
    "the reachable span, not a candidate. web0 (the shipped document) and web1 (this one) bracket",
    "what the law can reach per cell; the required strength is (native - web0) / (web1 - web0),",
    "claims 5.33's endpoint table in the dark scheme.",
    "resolvedMaterialSha256 is the shipped document's and is STALE here on purpose.",
  ],
  (patch) => {
    patch.backdropToneResponseStrength = 1;
  },
);

if (anchorsPath !== undefined) {
  const anchors = JSON.parse(readFileSync(anchorsPath, "utf8"));
  write(
    "candidate-measured-anchors.json",
    [
      "W21 G0 DIAGNOSTIC — scratch only, never committed to profiles/.",
      "The shipped dark document with backdropToneResponseStrength 1 and the response rows",
      "replaced by the anchors the DARK probe measured under the declared geometry",
      "(results/2026-09-06-w21-dark-scheme/g0/anchors.txt). Nothing else moves: the alpha, the",
      "rim and the tint are the shipped document's, so this is the law's contribution alone.",
      "A first read, not a fit. G1 fits, on the probe's calibration split.",
      "resolvedMaterialSha256 is the shipped document's and is STALE here on purpose.",
    ],
    (patch) => {
      patch.backdropToneResponseStrength = 1;
      patch.backdropToneAnchorX = anchors.anchorX;
      patch.backdropToneResponseThin = anchors.thin;
      patch.backdropToneResponseThick = anchors.thick;
    },
  );
}

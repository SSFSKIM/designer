/**
 * W21 G0 — the scratch material-profile documents vitrea's diagnostic renders use.
 *
 * Each is the SHIPPED dark document with one thing changed, written to scratch and never to
 * `packages/calibration/profiles/`: G0 is a spike and re-records nothing. The endpoint document
 * turns the response law on at the LIGHT reference's anchors, which is the far end of the mix's
 * reachable span and not a proposal; a candidate document turns it on at anchors the dark probe
 * measured, which is where G1 starts.
 *
 * `resolvedMaterialSha256` is deliberately left as the shipped document's value and marked in the
 * copy's own comment: these documents are diagnostics that never enter `profiles/`, the fingerprint
 * test does not read them, and a fabricated hash beside a changed patch would be worse than an
 * honest stale one that says so.
 *
 * Usage:
 *   node make-candidate-profiles.mjs <darkProfileDoc> <outDir> [<name>=<anchorsJson> ...]
 *
 * An anchors file is `{ "anchorX": [a,b,c], "thin": [a,b,c], "thick": [a,b,c], "note": "…" }`. More
 * than one may be given because the dark probe's thin row admits more than one honest reading of
 * its top anchor, and the way to choose between them is to render both and look.
 */

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const [, , docPath, outDir, ...candidates] = process.argv;
if (docPath === undefined || outDir === undefined) {
  throw new Error("usage: make-candidate-profiles.mjs <darkProfileDoc> <outDir> [name=anchors.json]");
}
mkdirSync(outDir, { recursive: true });
const doc = JSON.parse(readFileSync(docPath, "utf8"));

function write(name, note, mutate) {
  const copy = JSON.parse(JSON.stringify(doc));
  copy["$comment-w21-g0"] = note;
  mutate(copy.patch);
  const path = join(outDir, `${name}.json`);
  writeFileSync(path, `${JSON.stringify(copy, null, 2)}\n`);
  process.stdout.write(`${path}\n`);
}

write(
  "endpoint-strength1-light-anchors",
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

for (const entry of candidates) {
  const [name, path] = entry.split("=");
  if (name === undefined || path === undefined) throw new Error(`bad candidate spec: ${entry}`);
  const anchors = JSON.parse(readFileSync(path, "utf8"));
  write(
    name,
    [
      "W21 G0 DIAGNOSTIC — scratch only, never committed to profiles/.",
      "The shipped dark document with backdropToneResponseStrength 1 and the response rows",
      "replaced by anchors the DARK probe measured under the declared geometry",
      "(results/2026-09-06-w21-dark-scheme/g0/anchors.txt). Nothing else moves: the alpha, the",
      "rim and the tint are the shipped document's, so this is the law's contribution alone.",
      "A first read, not a fit. G1 fits, on the probe's calibration split.",
      ...(anchors.note === undefined ? [] : ["", anchors.note]),
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

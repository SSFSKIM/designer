/**
 * W21 G1 — the scratch material-profile documents the fits render at.
 *
 * G0's `make-candidate-profiles.mjs` wrote one diagnostic shape (the law turned on at a given set
 * of anchors). G1 fits two constants on top of that shape, so what it needs is a generic override
 * writer: the shipped dark document, with the wave's BOUND form applied (Decision Log 2 (a) and
 * (b) — the measured anchors, `backdropToneResponseStrength` 1, `specularGain` 0), and then one or
 * more leaf overrides given on the command line. Nothing here is committed to `profiles/`: the
 * fits are rendered to scratch and only their winner is re-recorded, by hand, into the document.
 *
 * `resolvedMaterialSha256` is deliberately left as the shipped document's and said so in the copy's
 * own comment, for G0's reason: a fabricated hash beside a changed patch is worse than an honest
 * stale one that names itself.
 *
 * Usage:
 *   node make-fit-profiles.mjs <darkProfileDoc> <anchorsJson> <outDir> <name>:<path>=<value> ...
 *
 * A leaf path is dotted into the patch (`optics.regular.rimAlpha`), a value is JSON, and several
 * leaves may share one name by repeating it — `rim0.02:optics.regular.rimAlpha=0.02` and
 * `rim0.02:optics.regular.tintAlpha=0.9` write one document called `rim0.02`.
 */

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const [, , docPath, anchorsPath, outDir, ...specs] = process.argv;
if (docPath === undefined || anchorsPath === undefined || outDir === undefined) {
  throw new Error("usage: make-fit-profiles.mjs <doc> <anchors.json> <outDir> <name>:<path>=<v> ...");
}
mkdirSync(outDir, { recursive: true });
const doc = JSON.parse(readFileSync(docPath, "utf8"));
const anchors = JSON.parse(readFileSync(anchorsPath, "utf8"));

/** The wave's bound form, applied to every document this writes before any fit override. */
function bindForm(patch) {
  patch.backdropToneResponseStrength = 1;
  patch.backdropToneAnchorX = anchors.anchorX;
  patch.backdropToneResponseThin = anchors.thin;
  patch.backdropToneResponseThick = anchors.thick;
  patch.optics.regular.specularGain = 0;
}

function setLeaf(patch, path, value) {
  const keys = path.split(".");
  let node = patch;
  for (const key of keys.slice(0, -1)) {
    node[key] ??= {};
    node = node[key];
  }
  node[keys[keys.length - 1]] = value;
}

const grouped = new Map();
for (const spec of specs) {
  const colon = spec.indexOf(":");
  const equals = spec.indexOf("=");
  if (colon < 0 || equals < colon) throw new Error(`bad spec: ${spec}`);
  const name = spec.slice(0, colon);
  const path = spec.slice(colon + 1, equals);
  const value = JSON.parse(spec.slice(equals + 1));
  if (!grouped.has(name)) grouped.set(name, []);
  grouped.get(name).push([path, value]);
}

for (const [name, leaves] of grouped) {
  const copy = JSON.parse(JSON.stringify(doc));
  bindForm(copy.patch);
  for (const [path, value] of leaves) setLeaf(copy.patch, path, value);
  copy["$comment-w21-g1"] = [
    "W21 G1 FIT CANDIDATE — scratch only, never committed to profiles/.",
    "The shipped dark document under the wave's bound form (W21 Decision Log 2 (a) and (b)): the",
    "anchors the dark probe measured, backdropToneResponseStrength 1, specularGain 0. On top of",
    "that, this document's own fit overrides:",
    ...leaves.map(([path, value]) => `    ${path} = ${JSON.stringify(value)}`),
    "resolvedMaterialSha256 is the shipped document's and is STALE here on purpose.",
  ];
  const path = join(outDir, `${name}.json`);
  writeFileSync(path, `${JSON.stringify(copy, null, 2)}\n`);
  process.stdout.write(`${path}\n`);
}

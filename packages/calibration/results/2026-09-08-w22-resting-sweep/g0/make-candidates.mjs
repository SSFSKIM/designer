/**
 * W22 G0 — the scratch material-profile documents this gate's fits and predictions render at.
 *
 * A generic leaf-override writer over a SHIPPED document, with no bound form of its own: unlike
 * W21 G1, this wave changes no law before it fits, so a candidate is the shipped document plus the
 * named leaves and nothing else. That is what makes each rendered point attributable to the leaf
 * whose name it carries.
 *
 * `resolvedMaterialSha256` is left as the shipped document's and is STALE in every copy, on W21's
 * rule: a fabricated hash beside a changed patch is worse than an honest stale one that says so.
 * Nothing here is ever committed to `profiles/` — the candidates live in scratch and only a
 * winner's NUMBER is carried forward, by hand, into G1's document.
 *
 * Usage:
 *   node make-candidates.mjs <shippedDoc> <outDir> <name>:<dotted.path>=<jsonValue> ...
 *
 * Several leaves may share one name by repeating it, so one document can carry a pair of
 * constants that only mean anything together.
 */

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const [, , docPath, outDir, ...specs] = process.argv;
if (docPath === undefined || outDir === undefined) {
  throw new Error("usage: make-candidates.mjs <doc> <outDir> <name>:<path>=<value> ...");
}
mkdirSync(outDir, { recursive: true });
const doc = JSON.parse(readFileSync(docPath, "utf8"));

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
  for (const [path, value] of leaves) setLeaf(copy.patch, path, value);
  copy["$comment-w22-g0"] = [
    "W22 G0 CANDIDATE — scratch only, never committed to profiles/.",
    `The shipped ${doc.profileKey} document with these leaves overridden and nothing else:`,
    ...leaves.map(([path, value]) => `    ${path} = ${JSON.stringify(value)}`),
    "resolvedMaterialSha256 is the shipped document's and is STALE here on purpose.",
  ];
  const path = join(outDir, `${name}.json`);
  writeFileSync(path, `${JSON.stringify(copy, null, 2)}\n`);
  process.stdout.write(`${path}\n`);
}

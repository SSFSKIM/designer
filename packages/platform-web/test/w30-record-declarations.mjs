/**
 * Record `w30-css-declarations-pre-leaves.json` from the tree as it stands.
 *
 *   npx tsx test/w30-record-declarations.mjs
 *
 * Run ONCE, on the tree before W30 G2's leaves exist, and never again: the file
 * it writes is the "nothing moved" half of acceptance clause 1, and a fixture
 * re-recorded on the tree it is meant to judge says nothing at all. It is kept
 * beside the bed so a reader can see exactly what produced the bytes, on the
 * precedent of W19 G1's own pre-fold recording.
 */
import { writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

import { sweep } from "./w30-css-declaration-bed.ts";

const here = dirname(fileURLToPath(import.meta.url));
const data = sweep();
writeFileSync(join(here, "w30-css-declarations-pre-leaves.json"), `${JSON.stringify(data, null, 2)}\n`);
const first = Object.values(data)[0];
process.stdout.write(
  `cases ${String(Object.keys(data).length)}; properties per case ${String(Object.keys(first ?? {}).length)}\n`,
);

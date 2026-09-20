/**
 * Record a pre-leaf declaration fixture from the tree as it stands.
 *
 *   npx tsx test/w30-record-declarations.mjs              # the nominal sweep
 *   npx tsx test/w30-record-declarations.mjs --policies   # the two a11y regimes
 *
 * Run ONCE per fixture, on the tree before W30 G2's leaves exist, and never
 * again: the file it writes is the "nothing moved" half of acceptance clause 1,
 * and a fixture re-recorded on the tree it is meant to judge says nothing at all.
 * It is kept beside the bed so a reader can see exactly what produced the bytes,
 * on the precedent of W19 G1's own pre-fold recording.
 *
 * The nominal fixture was recorded on the tree at the commit before the leaves.
 * The policy fixture was added by the review closure (claims §5.158 §8, finding
 * 6) and recorded the only way that keeps it honest after the fact: by checking
 * `packages/platform-web/src` out at `01347a2c` — the pre-leaf tree — running
 * this with `--policies` there, and restoring the working tree. The bed itself is
 * the current one, because the bed is what asks the question; the code it asks is
 * the pre-leaf code.
 */
import { writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

import { policySweep, sweep } from "./w30-css-declaration-bed.ts";

const policies = process.argv.includes("--policies");
const here = dirname(fileURLToPath(import.meta.url));
const name = policies
  ? "w30-css-declarations-policies-pre-leaves.json"
  : "w30-css-declarations-pre-leaves.json";
const data = policies ? policySweep() : sweep();
writeFileSync(join(here, name), `${JSON.stringify(data, null, 2)}\n`);
const first = Object.values(data)[0];
process.stdout.write(
  `${name}: cases ${String(Object.keys(data).length)}; properties per case ${String(Object.keys(first ?? {}).length)}\n`,
);

/** Record the numerical producer's exercised Node closure before the assembled G0 seal.
 * This imports runtime code only: no cohort, argument record, pixel or numerical sweep is read.
 */
import { existsSync, realpathSync, writeFileSync } from "node:fs";
import { dirname, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { loadRuntime, verifyPins } from "./numerical.ts";

const here = dirname(fileURLToPath(import.meta.url));
const root = realpathSync(resolve(here, "../../../../../"));
if (["declaration.sha256", "fit-declaration.sha256"].some((name) => existsSync(resolve(here, "..", name)))) {
  throw new Error("Root is already sealed; no runtime-closure replacement is admitted");
}
const runtime = await loadRuntime({ discovery: true });
const sources = [...runtime.sources].map(([path, sha256]) => ({ path: relative(root, path), sha256 }))
  .sort((a, b) => a.path.localeCompare(b.path));
verifyPins(root, sources);
const out = resolve(here, "runtime-closure.json");
writeFileSync(out, `${JSON.stringify({ schema: "w50-numerical-runtime-closure-1", sources,
  environment: { node: process.version, executable: process.execPath },
  scope: "CPU-only runtime imports; no numerical candidate or pixel measured" }, null, 2)}\n`, { flag: "wx" });
console.log(`Recorded ${sources.length} exercised numerical source pins; root remains unsealed`);

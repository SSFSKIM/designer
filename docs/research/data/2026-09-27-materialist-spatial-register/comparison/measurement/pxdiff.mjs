import { createRequire } from "node:module";
import { readdirSync, readFileSync } from "node:fs";
const require = createRequire("/Users/new/Developer/GitHub/designer/apps/demo/package.json");
const { PNG } = require("pngjs");
const [A, B] = process.argv.slice(2);
for (const f of readdirSync(A).filter((f) => f.endsWith(".png")).sort()) {
  let b; try { b = PNG.sync.read(readFileSync(`${B}/${f}`)); } catch { continue; }
  const a = PNG.sync.read(readFileSync(`${A}/${f}`));
  let n = 0, max = 0, box = [1e9, 1e9, -1, -1];
  for (let i = 0; i < a.data.length; i += 4) { const d = Math.max(Math.abs(a.data[i]-b.data[i]), Math.abs(a.data[i+1]-b.data[i+1]), Math.abs(a.data[i+2]-b.data[i+2])); if (d) { n++; max = Math.max(max, d); const p = i/4, x = p % a.width, y = Math.floor(p / a.width); box = [Math.min(box[0],x),Math.min(box[1],y),Math.max(box[2],x),Math.max(box[3],y)]; } }
  console.log(f.padEnd(34), "differing px", String(n).padStart(7), "max", String(max).padStart(3), n ? "bbox " + box.join(",") : "");
}

import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
const require = createRequire("/Users/new/Developer/GitHub/designer/apps/demo/package.json");
const { PNG } = require("pngjs");
const R = JSON.parse(readFileSync("/tmp/sp-clear/recapture.json", "utf8"));
const cells = ["webgpu-dark-day-platter", "webgpu-dark-night-platter", "css-dark-dawn-platter", "webgpu-dark-day-rest", "webgpu-light-day-rest", "webgpu-light-day-platter"];
for (const c of cells) {
  const a = PNG.sync.read(readFileSync(`/tmp/sp-clear/clear-shots/${c}.png`)), b = PNG.sync.read(readFileSync(`/tmp/sp-clear/clear-shots-2/${c}.png`));
  const [tier, scheme, phase, state] = c.split("-");
  const m = R.matrix.find((x) => x.tier === tier && x.scheme === scheme && x.phase === phase && x.state === state);
  const rects = Object.values(m.fp.groups).map((g) => g.rect);
  const inside = (x, y) => rects.some(([rx, ry, rw, rh]) => x >= rx - 20 && x < rx + rw + 20 && y >= ry - 20 && y < ry + rh + 20);
  let n1 = 0, n2 = 0, nOut1 = 0, nOut2 = 0, max = 0, maxOut = 0, bx = [1e9, 1e9, -1, -1];
  for (let y = 0; y < a.height; y++) for (let x = 0; x < a.width; x++) {
    const i = (y * a.width + x) * 4; let d = 0;
    for (let k = 0; k < 3; k++) d = Math.max(d, Math.abs(a.data[i + k] - b.data[i + k]));
    if (!d) continue;
    const out = !inside(x, y);
    if (d >= 1) { n1++; if (out) nOut1++; } if (d >= 2) { n2++; if (out) nOut2++; if (out) { bx[0] = Math.min(bx[0], x); bx[1] = Math.min(bx[1], y); bx[2] = Math.max(bx[2], x); bx[3] = Math.max(bx[3], y); } }
    max = Math.max(max, d); if (out) maxOut = Math.max(maxOut, d);
  }
  console.log(`${c}: differing px ≥1: ${n1} (outside hosts+20px: ${nOut1}), ≥2: ${n2} (outside: ${nOut2}), max ${max} (outside ${maxOut}); outside ≥2 bbox ${bx[2] < 0 ? "-" : bx.join(",")}`);
}

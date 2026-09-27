import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
const require = createRequire("/Users/new/Developer/GitHub/designer/apps/demo/package.json");
const { PNG } = require("pngjs");
const R = JSON.parse(readFileSync("/tmp/sp-clear/recapture.json", "utf8"));
const F = JSON.parse(readFileSync("/tmp/sp-clear/final.json", "utf8"));
for (const c of ["webgpu-dark-day-platter", "css-dark-dawn-platter", "webgpu-dark-night-platter", "webgpu-light-day-platter"]) {
  const a = PNG.sync.read(readFileSync(`/tmp/sp-clear/clear-shots/${c}.png`)), b = PNG.sync.read(readFileSync(`/tmp/sp-clear/clear-shots-2/${c}.png`));
  const [tier, scheme, phase, state] = c.split("-");
  const m = R.matrix.find((x) => x.tier === tier && x.scheme === scheme && x.phase === phase && x.state === state);
  const f = F.matrix.find((x) => x.glass === "clear" && x.tier === tier && x.scheme === scheme && x.phase === phase && x.state === state);
  const [rx, ry, rw, rh] = m.fp.groups.photograph.rect;
  const count = (dx, dy, inner) => { let n = 0; for (let y = ry + 4; y < ry + rh - 4; y++) for (let x = rx + 4; x < rx + rw - 4; x++) { const i = (y * a.width + x) * 4, j = ((y + dy) * a.width + (x + dx)) * 4; let d = 0; for (let k = 0; k < 3; k++) d = Math.max(d, Math.abs(a.data[i + k] - b.data[j + k])); if (d >= 2) n++; } return n; };
  const shifts = []; for (const dy of [-1, 0, 1]) for (const dx of [-1, 0, 1]) shifts.push(`(${dx},${dy}):${count(dx, dy)}`);
  // the feather ring: 20 px outside the platter rect, excluding the rect
  let ring = 0, ringMax = 0; for (let y = ry - 20; y < ry + rh + 20; y++) for (let x = rx - 20; x < rx + rw + 20; x++) { if (x >= rx && x < rx + rw && y >= ry && y < ry + rh) continue; const i = (y * a.width + x) * 4; let d = 0; for (let k = 0; k < 3; k++) d = Math.max(d, Math.abs(a.data[i + k] - b.data[i + k])); }
  for (let y = ry - 20; y < ry + rh + 20; y++) for (let x = rx - 20; x < rx + rw + 20; x++) { if (x >= rx && x < rx + rw && y >= ry && y < ry + rh) continue; const i = (y * a.width + x) * 4; let d = 0; for (let k = 0; k < 3; k++) d = Math.max(d, Math.abs(a.data[i + k] - b.data[i + k])); if (d >= 1) { ring++; ringMax = Math.max(ringMax, d); } }
  console.log(`${c}: inner diffs ≥2 by shift ${shifts.join(" ")} | feather ring ≥1: ${ring} max ${ringMax} | photograph hint run1 ${f.fp.groups.photograph.backdrop?.luminance} run2 ${m.fp.groups.photograph.backdrop?.luminance} canvasLum ${f.fp.groups.photograph.canvasLum} -> ${m.fp.groups.photograph.canvasLum}`);
}

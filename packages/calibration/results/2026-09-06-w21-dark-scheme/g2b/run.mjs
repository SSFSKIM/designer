import { readFileSync } from "node:fs";
import { derive, E, D } from "./model.mjs";
const R = "/Users/new/Developer/GitHub/designer/";
const bd = JSON.parse(readFileSync("./backdrops.json", "utf8"));
const scenes = JSON.parse(readFileSync(R + "apps/reference-apple/scenes.json", "utf8"));
const comp = scenes.components;
const geomOf = (c) => c === "capsule-button"
  ? { width: 120, height: 44, radius: 22 }
  : { width: comp[c].size[0], height: comp[c].size[1], radius: comp[c].radius };

const cases = [
  ["dark-solid", "rrect-md"], ["checkerboard", "rrect-md"], ["photo", "rrect-md"],
  ["photo", "rrect-lg"], ["dark-solid", "capsule-button"], ["checkerboard", "capsule-button"],
  ["photo", "capsule-button"], ["mid-dark-solid", "capsule-button"], ["impulse", "capsule-button"],
];
const profiles = {
  dark: JSON.parse(readFileSync(R + "packages/calibration/profiles/apple-macos-26.5-1x-dark-standard.json", "utf8")),
  light: JSON.parse(readFileSync(R + "packages/calibration/profiles/apple-macos-26.5-1x-light-standard.json", "utf8")),
};
const patchOf = (p) => p.patch ?? p.profile ?? p;
for (const key of ["dark", "light"]) {
  const patch = patchOf(profiles[key]);
  console.log(`\n== ${key} profile`);
  console.log("scene".padEnd(34), "thk    k      alpha  tint    X       cssA   cssTint gpuBody cssBody form");
  for (const [bg, c] of cases) {
    const s = bd[`${bg}@1x`];
    const r = derive(patch, geomOf(c), { rgb: s.rgb, luminance: s.luminance, linearLuminance: s.linearLuminance });
    const f = (x, n = 4) => x.toFixed(n);
    console.log(
      `${bg}__${c}`.padEnd(34),
      f(r.thickness, 3), f(r.adaptation, 3), f(r.alpha), f(r.tint[0]), f(r.addedLight),
      f(r.cssAlpha), String(r.cssTint[0]).padStart(3), "    ", f(r.gpuBody), " ", f(r.cssBody), " ", r.form,
    );
  }
}

/** W27c G1's spatial reread before fitting width: measured line profiles, not SD-to-sigma. */
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { decodePng, linearLuminance } from "../src/image";
import { componentRegion } from "../src/component-region";

const run = JSON.parse(readFileSync(process.argv[2]!, "utf8"));
const matrix = JSON.parse(readFileSync(resolve("../../apps/reference-apple/scenes.json"), "utf8"));
const rows = run.rows.filter((r: any) => r.set === "calibration" &&
  (r.sourceScene === "checkerboard__capsule-button__rest" ||
   r.sourceScene === "checkerboard__rrect-md__rest" || r.sourceScene === "photo__rrect-md__rest"));
const result = rows.map((r: any) => {
  const scene = matrix.scenes.find((s: any) => s.id === r.sourceScene);
  const native = decodePng(readFileSync(resolve("../../apps/reference-apple/fixtures", r.profile, `${r.scene}.png`)));
  const web = decodePng(readFileSync(r.capture));
  const region = componentRegion(matrix.components[scene.component], {
    canvas: matrix.canvas, width: native.width, height: native.height, scale: r.scale,
  });
  const profiles = [native, web].map((image) => {
    const y = linearLuminance(image);
    const scan = (axis: "horizontal" | "vertical"): number[][] => {
      const samples: number[][] = [];
      const length = axis === "horizontal" ? image.width : image.height;
      for (let i = 0; i < length; i++) {
        let sum = 0, n = 0;
        for (let j = -2 * r.scale; j <= 2 * r.scale; j++) {
          const x = axis === "horizontal" ? i : Math.floor(region.centreX) + j;
          const v = axis === "horizontal" ? Math.floor(region.centreY) + j : i;
          const k = v * image.width + x;
          if (region.signedDistancePx[k]! > -6 * r.scale) continue;
          sum += y[k]!; n++;
        }
        if (n > 0) samples.push([i / r.scale, sum / n]);
      }
      return samples;
    };
    return { horizontal: scan("horizontal"), vertical: scan("vertical") };
  });
  return { profile: r.profile, scene: r.scene, scale: r.scale,
    native: profiles[0], web: profiles[1] };
});
writeFileSync(process.argv[3]!, JSON.stringify({
  definition: "Linear Rec.709 Y averaged across a 4-CSS-px central stripe, restricted to the declared body's 6-CSS-px erosion. Position is CSS px; each scale remains separate.",
  source: process.argv[2], rows: result,
}, null, 2) + "\n", { flag: "wx" });
console.log(`${result.length} paired spatial profiles recorded`);

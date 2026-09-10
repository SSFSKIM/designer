/** W27c G1: reuse G0's declared-mask facet readers on a completed frozen run. */
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { decodePng } from "../src/image";
import { componentRegion } from "../src/component-region";
import { readInterior, difference } from "../scripts/recede";

const run = JSON.parse(readFileSync(process.argv[2]!, "utf8"));
const matrix = JSON.parse(readFileSync(resolve("../../apps/reference-apple/scenes.json"), "utf8"));
const rows = run.rows.map((r: any) => {
  const scene = matrix.scenes.find((s: any) => s.id === r.sourceScene);
  const native = decodePng(readFileSync(resolve("../../apps/reference-apple/fixtures", r.profile, `${r.scene}.png`)));
  const background = decodePng(readFileSync(resolve("../../apps/reference-apple/fixtures/backgrounds",
    `${scene.background}@${r.scale}x.png`)));
  const web = decodePng(readFileSync(r.capture));
  const region = componentRegion(matrix.components[scene.component], {
    canvas: matrix.canvas, width: native.width, height: native.height, scale: r.scale,
  });
  const mask = { ...region.silhouette, mask: Uint8Array.from(region.signedDistancePx,
    (d) => d <= -6 * r.scale ? 1 : 0) };
  const read = (image: typeof web) => {
    const delta = difference(image, background, region.silhouette);
    const { changed, ...counts } = delta;
    return { footprint: readInterior(image, background, region.silhouette),
      body: readInterior(image, background, mask), exterior: { ...counts,
        exteriorBeyondOneCodePast2CssPx: changed.filter((i) => region.signedDistancePx[i]! > 2 * r.scale).length },
    };
  };
  return { profile: r.profile, scene: r.scene, scale: r.scale, set: r.set,
    native: read(native), web: read(web) };
});
writeFileSync(process.argv[3]!, JSON.stringify({
  definition: "G0 readInterior/difference unchanged; footprint is declared union, body eroded 6 CSS px. Exterior >1-code counts are device pixels, beyond 2 CSS px separately, not fitted shadow amplitudes.",
  source: process.argv[2], rows,
}, null, 2) + "\n", { flag: "wx" });
console.log(`${rows.length} native/WebGPU facet pairs recorded`);

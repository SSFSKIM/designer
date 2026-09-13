/**
 * W27c G1c: the reference's own dark thin response curve, read NATIVE-ONLY
 * (claims §5.141 §2).
 *
 * This produces no vitrea-against-native distance for any cell and therefore
 * spends nothing — the same standing as §5.139 §4's native-against-native
 * attestation. What it produces is the abscissa/ordinate pair the response law
 * is a function of: for each dark inactive cell over a uniform or structured
 * backdrop, the backdrop's ENCODED-space mean (which is what
 * `backdropToneAnchorX` is: 69/255 = 0.2706 is `mid-dark-solid`'s, exactly) and
 * the reference's settled interior level in linear Rec.709 Y over the declared
 * union eroded 6 CSS px.
 *
 * It is run before the fit, because whether a one-parameter move of
 * `backdropToneResponseThin[2]` can carry the bed at all is decided by the curve
 * these points describe and not by a sweep's residual.
 *
 * Usage:
 *   pnpm --filter @vitrea/calibration --fail-if-no-match exec tsx \
 *     results/2026-09-13-w27c-g1c-fit/native-response.ts
 */
import { readFileSync, writeFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { decodePng, linearLuminance } from "../../src/image";
import { componentRegion, type DeclaredComponent } from "../../src/component-region";

const here = dirname(fileURLToPath(import.meta.url));
const pkg = resolve(here, "../..");
const repo = resolve(pkg, "../..");
const json = (file: string): any => JSON.parse(readFileSync(file, "utf8"));

const matrix = json(resolve(repo, "apps/reference-apple/scenes.json"));
const manifest = json(resolve(repo, "apps/reference-apple/fixtures/manifest.json"));
const fixtures = resolve(repo, "apps/reference-apple/fixtures");

/** `backdropToneAnchorX`'s own axis: the raster's Rec.709 luma mean in ENCODED bytes. */
function encodedMean(file: string): number {
  const png = decodePng(readFileSync(file));
  let sum = 0;
  for (let i = 0; i < png.width * png.height; i++) {
    const j = i * 4;
    sum += (0.2126 * png.data[j]! + 0.7152 * png.data[j + 1]! + 0.0722 * png.data[j + 2]!) / 255;
  }
  return sum / (png.width * png.height);
}

/** The declared union eroded 6 CSS px, the body of every reading in this ledger. */
function body(file: string, scene: any, scale: number): { y: number; sd: number; n: number } {
  const png = decodePng(readFileSync(file));
  const region = componentRegion(matrix.components[scene.component] as DeclaredComponent, {
    canvas: matrix.canvas, scale, width: png.width, height: png.height,
  });
  const y = linearLuminance(png);
  let n = 0, s = 0, s2 = 0;
  for (let i = 0; i < y.length; i++) {
    if (region.signedDistancePx[i]! > -6 * scale) continue;
    n++; s += y[i]!; s2 += y[i]! ** 2;
  }
  return { y: s / n, sd: Math.sqrt(Math.max(0, s2 / n - (s / n) ** 2)), n };
}

const backgrounds = new Map<string, { at1x: number; at2x: number }>();
for (const name of Object.keys(matrix.backgrounds)) {
  backgrounds.set(name, {
    at1x: encodedMean(resolve(fixtures, "backgrounds", `${name}@1x.png`)),
    at2x: encodedMean(resolve(fixtures, "backgrounds", `${name}@2x.png`)),
  });
}

const rows: any[] = [];
for (const profile of manifest.profiles) {
  const key: string = profile.profileKey;
  const scale = key.includes("-2x-") ? 2 : 1;
  for (const fixture of profile.fixtures) {
    const scene = matrix.scenes.find((s: any) => s.id === fixture.sceneId);
    if (scene === undefined || scene.state !== "inactive") continue;
    if (scene.tint !== undefined || scene.interaction !== undefined) continue;
    const component = matrix.components[scene.component];
    if (component?.kind !== "rrect" && component?.kind !== "capsule") continue;
    const span = Math.min(component.size?.[0] ?? 0, component.size?.[1] ?? 0);
    const b = body(resolve(fixtures, fixture.file), scene, scale);
    rows.push({
      profile: key,
      scene: scene.id,
      scheme: profile.colorScheme ?? (key.includes("-dark-") ? "dark" : "light"),
      a11y: key.includes("increased-contrast") ? "increased-contrast"
        : key.includes("reduced-transparency") ? "reduced-transparency" : "standard",
      scale,
      background: scene.background,
      span,
      /* The two coordinates the response law is a function of. */
      encodedBackdropMean: scale === 2
        ? backgrounds.get(scene.background)!.at2x : backgrounds.get(scene.background)!.at1x,
      sizeThickness: Math.max(0, Math.min(1, (span - 32) / 64)) ** 2 *
        (3 - 2 * Math.max(0, Math.min(1, (span - 32) / 64))),
      nativeBodyY: b.y,
      nativeBodySd: b.sd,
      bodyPixels: b.n,
      fixtureSet: fixture.fixtureSet,
      file: fixture.file,
    });
  }
}
rows.sort((a, b) => `${a.profile}/${a.scene}`.localeCompare(`${b.profile}/${b.scene}`));

writeFileSync(
  resolve(here, "native-response.json"),
  `${JSON.stringify({
    gate: "W27c G1c / claims §5.141",
    kind: "native-only reading — no vitrea capture, no comparison, nothing spent",
    definitions: {
      encodedBackdropMean:
        "the background raster's Rec.709 luma mean over its ENCODED bytes — `backdropToneAnchorX`'s own axis. mid-dark-solid reads 69/255 = 0.27059 and light-solid 0.9505, which are two of the three declared anchors exactly.",
      nativeBodyY: "the reference's settled interior level, linear Rec.709 Y over the declared union eroded 6 CSS px",
      sizeThickness: "smoothstep(sizeSpanMin 32, sizeSpanMax 96, span) — the row mixture the response evaluates at",
    },
    rows,
  }, null, 2)}\n`,
);
console.log(`${rows.length} native rows`);

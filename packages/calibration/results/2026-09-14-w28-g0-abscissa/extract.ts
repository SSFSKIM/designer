/**
 * W28 G0's only pixel-reading boundary. The geometry and native ordinate use the
 * calibration instrument, not a second implementation. Raw arrays go to scratch;
 * the compact results and hashes are committed by read.py. Never opens a D fixture.
 */
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { resolve, dirname, basename } from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { decodePng, linearLuminance } from "../../src/image";
import { componentRegion, type DeclaredComponent } from "../../src/component-region";

const here = dirname(fileURLToPath(import.meta.url));
const repo = resolve(here, "../../../..");
const json = (file: string): any => JSON.parse(readFileSync(resolve(repo, file), "utf8"));
const relativeHere = "packages/calibration/results/2026-09-14-w28-g0-abscissa";
const populationPath = `${relativeHere}/population.json`;
const population = json(populationPath);
const authority = json(population.checkingAuthority);
const denied = new Set<string>(authority.groups.find((g: any) => g.id === "D").scenes
  .map((id: string) => id.slice(0, id.lastIndexOf("__"))));
function admit(scene: string): void {
  if (denied.has(scene.slice(0, scene.lastIndexOf("__")))) {
    throw new Error(`X10 refused checking cell: ${scene}`);
  }
}

if (process.argv.includes("--check-scene")) {
  admit(process.argv[process.argv.indexOf("--check-scene") + 1]!);
} else {
  const committed = execFileSync("git", ["show", `HEAD:${populationPath}`], { cwd: repo });
  if (!committed.equals(readFileSync(resolve(repo, populationPath)))) {
    throw new Error("Population must be committed unchanged before any pixel read");
  }
  for (const row of population.rows) {
    admit(row.scene);
    admit(basename(row.fixture, ".png"));
    if (basename(row.fixture, ".png") !== row.scene) throw new Error("Fixture/id mismatch");
  }
  const scratch = process.argv[process.argv.indexOf("--scratch") + 1];
  if (!process.argv.includes("--scratch") || !scratch) throw new Error("--scratch is required");
  mkdirSync(scratch, { recursive: true });
  const hashes: Record<string, string> = {};
  function png(file: string): ReturnType<typeof decodePng> {
    const bytes = readFileSync(resolve(repo, file));
    hashes[file] = createHash("sha256").update(bytes).digest("hex");
    return decodePng(bytes);
  }
  const fields = new Map<string, any>();
  const regions = new Map<string, any>();
  function background(file: string): any {
    if (fields.has(file)) return fields.get(file);
    const image = png(file);
    const encoded = new Float64Array(image.width * image.height);
    for (let i = 0; i < encoded.length; i++) {
      const j = i * 4;
      if (image.data[j + 3] !== 255) throw new Error("Expected opaque committed backdrop");
      encoded[i] = (0.2126 * image.data[j]! + 0.7152 * image.data[j + 1]! +
        0.0722 * image.data[j + 2]!) / 255;
    }
    const fileName = `background-${fields.size}.f64`;
    writeFileSync(resolve(scratch!, fileName), Buffer.from(encoded.buffer));
    const field = { width: image.width, height: image.height, encoded, fileName };
    fields.set(file, field);
    return field;
  }
  function region(specPath: string, component: string, scale: number, width: number, height: number): any {
    const key = `${specPath}/${component}/${scale}`;
    if (regions.has(key)) return regions.get(key);
    const spec = json(specPath);
    const declaration = spec.components[component] as DeclaredComponent;
    const r = componentRegion(declaration, { canvas: spec.canvas, scale, width, height });
    const span = Math.min(...r.placed.map((s) => Math.min(s.width, s.height)));
    const t = Math.max(0, Math.min(1, (span - 32) / 64));
    const fileName = `region-${regions.size}.f64`;
    writeFileSync(resolve(scratch!, fileName), Buffer.from(r.signedDistancePx.buffer));
    const value = { ...r, span, sizeThickness: t * t * (3 - 2 * t), fileName };
    regions.set(key, value);
    return value;
  }
  // These two controls use ONLY hc-text's BACKGROUND, never the forbidden square fixture.
  const checks = [];
  const bg = background("apps/reference-apple/fixtures/backgrounds/hc-text@1x.png");
  for (const component of ["rrect-sm", "capsule-button"]) {
    const r = region("apps/reference-apple/scenes.json", component, 1, bg.width, bg.height);
    const means: Record<string, number> = {};
    for (const [name, erosion] of [["silhouette", 0], ["body", -6]] as const) {
      let sum = 0, n = 0;
      for (let i = 0; i < bg.encoded.length; i++) {
        if (r.signedDistancePx[i]! <= erosion) { sum += bg.encoded[i]!; n++; }
      }
      means[name] = sum / n;
    }
    checks.push({ component, ...means });
  }
  const expected = [[0.5110, 0.6988], [0.6026, 0.5293]];
  checks.forEach((c, i) => {
    if (Math.abs(c.silhouette! - expected[i]![0]!) > 0.00005 ||
        Math.abs(c.body! - expected[i]![1]!) > 0.00005) throw new Error("hc-text region control failed");
  });
  console.log("Background-only hc-text region checks", checks);
  const rows = [];
  for (const row of population.rows) {
    const spec = json(row.sceneSpec);
    const scene = spec.scenes.find((s: any) => s.id === row.scene);
    const bg = background(row.background);
    const r = region(row.sceneSpec, scene.component, row.scale, bg.width, bg.height);
    admit(row.scene);
    const image = png(row.fixture);
    if (image.width !== bg.width || image.height !== bg.height) throw new Error("Dimension mismatch");
    const luminance = linearLuminance(image);
    let sum = 0, sum2 = 0, n = 0;
    for (let i = 0; i < luminance.length; i++) {
      if (r.signedDistancePx[i]! > -6 * row.scale) continue;
      const y = luminance[i]!;
      n++; sum += y; sum2 += y * y;
    }
    if (!n) throw new Error("Empty eroded body");
    const flags = [];
    if (scene.tint) flags.push("tinted");
    if (scene.interaction || scene.state === "pressed") flags.push("interaction");
    if (["group", "stack"].includes(spec.components[scene.component].kind)) flags.push("composite");
    if (r.sizeThickness > 0 && r.sizeThickness < 1) flags.push("intermediate-thickness");
    rows.push({ ...row, component: scene.component, backgroundName: scene.background,
      backgroundSpec: spec.backgrounds[scene.background], width: bg.width, height: bg.height,
      backgroundArray: bg.fileName, regionArray: r.fileName, span: r.span,
      sizeThickness: r.sizeThickness, thickness: r.sizeThickness < 1 ? "thin" : "thick", flags,
      nativeBodyY: sum / n, nativeBodySd: Math.sqrt(Math.max(0, sum2 / n - (sum / n) ** 2)), bodyPixels: n });
  }
  writeFileSync(resolve(scratch, "extracted.json"), JSON.stringify({ rows, hashes, regionChecks: checks }));
  console.log(`${rows.length} admitted native fixtures read; ${fields.size} background rasters`);
}

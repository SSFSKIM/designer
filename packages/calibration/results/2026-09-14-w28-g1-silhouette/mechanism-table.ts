/** Reduce actual input readouts; native material outputs are never consumed. */
import { readFileSync, writeFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const tierFiles = process.argv.slice(2);
if (tierFiles.length !== 2) throw new Error("Pass GPU and CSS mechanism JSON files");
const json = (path: string): any => JSON.parse(readFileSync(path, "utf8"));
const inputs = tierFiles.map((path) => json(resolve(path)));
if (new Set(inputs.map((input) => input.tier)).size !== 2) throw new Error("Need both tiers");
const g0 = json(resolve(here, "../2026-09-14-w28-g0-abscissa/per-cell.json")).rows;
const canonicalIds = g0.filter((r: any) => r.bed === "canonical").map((r: any) => r.id).sort();
const tolerance = 1 / 255;
const table: any[] = [];
for (const input of inputs) {
  const ids = input.rows.map((r: any) => r.id).sort();
  if (JSON.stringify(ids) !== JSON.stringify(canonicalIds)) {
    throw new Error(`${input.tier}: incomplete or duplicate canonical population`);
  }
  for (const row of input.rows) {
    const textureGroups = row.groups.filter((g: any) => g.configuredSource === "texture");
    const readouts = textureGroups.flatMap((g: any) => g.state?.backdropToneAbscissae ?? []);
    const relevant = row.component === "glass-over-glass"
      ? readouts.filter((r: any) => row.surfaces.find((s: any) => s.nodeId === r.surfaceId)?.plane === "base")
      : readouts;
    const pixels = relevant.reduce((sum: number, r: any) => sum + r.sampleCount, 0);
    const actual = pixels > 0 ? relevant.reduce((sum: number, r: any) =>
      sum + r.encodedLuminance * r.sampleCount, 0) / pixels : null;
    const delta = actual === null ? null : actual - row.expectedEncoded;
    const pressed = row.flags.includes("interaction");
    const perSurface = relevant.map((reading: any) => {
      const expected = row.expectedSurfaces.find((s: any) => s.surfaceId === reading.surfaceId);
      if (expected === undefined) throw new Error(`${row.id}: unexpected surface ${reading.surfaceId}`);
      const difference = reading.encodedLuminance - expected.encodedLuminance;
      return { surfaceId: reading.surfaceId, expectedEncoded: expected.encodedLuminance,
        actualEncoded: reading.encodedLuminance, deltaEncoded: difference,
        expectedPixels: expected.sampleCount, sampledPixels: reading.sampleCount,
        withinCode: reading.kind === "silhouette" && Number.isFinite(difference) &&
          Math.abs(difference) <= tolerance };
    });
    const expectedTextureCount = row.surfaces.filter((s: any) =>
      textureGroups.some((g: any) => g.id === s.groupId)).length;
    const withinCode = delta !== null && Number.isFinite(delta) && Math.abs(delta) <= tolerance &&
      relevant.length === expectedTextureCount && perSurface.every((s: any) => s.withinCode);
    table.push({ id: row.id, tier: input.tier, profile: row.profile, scene: row.scene,
      expectedEncoded: row.expectedEncoded, actualEncoded: actual, deltaEncoded: delta,
      deltaCodes: delta === null ? null : delta * 255, withinCode,
      gated: !pressed, passes: pressed || withinCode,
      reason: pressed ? "Interaction geometry differs from G0's unpressed predictor; recorded, not a raw-sampling gate."
        : actual === null ? "No sampled silhouette input readout was published" : null,
      aggregation: row.component === "glass-over-glass"
        ? "The raw-raster union is the containing base silhouette; the DOM overlay samples already-rendered glass."
        : relevant.length > 1
          ? "Area-weighted per-surface means reproduce G0's disjoint silhouette union; each member is checked separately too."
          : "One per-surface silhouette input.",
      perSurface, readouts: relevant, flags: row.flags,
      geometryDifferences: row.geometryDifferences });
  }
}
const aliases = g0.filter((r: any) => r.bed === "w9").map((r: any) => {
  const canonicalId = `canonical/${r.profile}/${r.scene}`;
  const twin = g0.find((c: any) => c.id === canonicalId);
  if (twin === undefined || twin.background !== r.background || twin.width !== r.width ||
    twin.height !== r.height || twin.component !== r.component ||
    Math.abs(twin.predictors.encoded.silhouette - r.predictors.encoded.silhouette) > 1e-12) {
    throw new Error(`${r.id}: W9 input cannot alias its canonical counterpart`);
  }
  return { id: r.id, canonicalId, reason: "Same committed raster, geometry, dimensions and G0 input; native output is not read." };
});
const crossTier = table.filter((r) => r.tier === "webgpu").map((gpu) => {
  const css = table.find((r) => r.tier === "css" && r.id === gpu.id)!;
  const delta = gpu.actualEncoded === null || css.actualEncoded === null ? null
    : gpu.actualEncoded - css.actualEncoded;
  return { id: gpu.id, gpu: gpu.actualEncoded, css: css.actualEncoded, delta, gated: gpu.gated,
    passes: !gpu.gated || (delta !== null && Number.isFinite(delta) && Math.abs(delta) <= tolerance) };
});
const summary = Object.fromEntries(inputs.map((input) => {
  const rows = table.filter((r) => r.tier === input.tier);
  const gated = rows.filter((r) => r.gated);
  return [input.tier, { cells: rows.length, gated: gated.length,
    interactionRecorded: rows.length - gated.length,
    pass: gated.filter((r) => r.passes).length, fail: gated.filter((r) => !r.passes).length,
    maximumAbsoluteDeltaCodes: Math.max(...gated.filter((r) => r.deltaCodes !== null)
      .map((r) => Math.abs(r.deltaCodes))) }];
}));
const passes = table.every((r) => r.passes) && crossTier.every((r) => r.passes);
writeFileSync(resolve(here, "mechanism-table.json"), `${JSON.stringify({
  toleranceEncoded: tolerance, passes, summary, aliases, crossTier, rows: table,
}, null, 2)}\n`);
writeFileSync(resolve(here, "mechanism-table.csv"), [
  "tier,profile,scene,expectedEncoded,actualEncoded,deltaCodes,gated,withinCode",
  ...table.map((r) => [r.tier, r.profile, r.scene, r.expectedEncoded, r.actualEncoded,
    r.deltaCodes, r.gated, r.withinCode].join(",")),
].join("\n") + "\n");
console.log(JSON.stringify(summary, null, 2));
if (!passes) process.exitCode = 1;

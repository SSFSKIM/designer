import { loadRuntime } from "../../2026-10-08-w50-g0-declaration/audit/numerical.ts";
import type { MaterialProfile } from "../../../../renderer-webgpu/src/material.ts";

/** This adapter calls the sealed production CPU law; it does not duplicate its solve. */
const nominal = {
  glass: "material", colorSource: "material", frost: "nominal", refraction: "nominal",
  occlusion: "nominal", border: "nominal", ambientTint: "nominal", foreground: "adaptive",
} as const;
const decode = (v: number): number => v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
const encode = (v: number): number => v <= 0.0031308 ? v * 12.92 : 1.055 * v ** (1 / 2.4) - 0.055;
type Rows = readonly (readonly number[])[];

function tuple(row: readonly number[]): [number, number, number, number] {
  if (row.length !== 4 || row.some((v, i) => !Number.isFinite(v) || v < 0 || v > 1 ||
    (i > 0 && v < row[i - 1]!))) throw new Error("Invalid declared chart row");
  return [row[0]!, row[1]!, row[2]!, row[3]!];
}
function domain(input: number, span: number, dpr: number): void {
  if (!Number.isFinite(input) || input < 0 || input > 64 ||
    !Number.isFinite(span) || span < 32 || span > 224 || ![1, 2].includes(dpr)) {
    throw new Error("Outside the declared low-end oracle domain");
  }
}
export async function currentEndpoint(position: 0.25 | 0.5, pose: "active" | "receded") {
  if (![0.25, 0.5].includes(position) || !["active", "receded"].includes(pose)) {
    throw new Error("Only four dark endpoints are declared");
  }
  const { renderer, documents } = await loadRuntime();
  const doc = position === 0.25 ? documents.macos27Glass025MaterialProfileDocument
    : documents.macos27MaterialProfileDocument;
  const active = renderer.withMaterialOverrides(renderer.DEFAULT_MATERIAL_PROFILE, doc.active.dark.patch ?? {});
  return pose === "active" ? active : renderer.withMaterialOverrides(active, doc.receded.dark.patch ?? {});
}

export function chartCodes(rows: Rows, input: number, span: number): number {
  domain(input, span, 1);
  if (input > 40 || rows.length !== 3) throw new Error("Only measured chart input0–40 has free ordinates");
  const checked = rows.map(tuple);
  const row = span < 96 ? 0 : 1;
  const st = Math.min(1, Math.max(0, row === 0 ? (span - 44) / 52 : (span - 96) / 64));
  const index = input <= 8 ? 0 : input <= 28 ? 1 : 2;
  const xs = [0, 8, 28, 40];
  const xt = (input - xs[index]!) / (xs[index + 1]! - xs[index]!);
  const a = checked[row]![index]! + (checked[row]![index + 1]! - checked[row]![index]!) * xt;
  const b = checked[row + 1]![index]! + (checked[row + 1]![index + 1]! - checked[row + 1]![index]!) * xt;
  return (a + (b - a) * st) * 255;
}

export async function composedUniformCode(profile: MaterialProfile, rows: Rows,
  input: number, span: number, dpr: number): Promise<number> {
  domain(input, span, dpr);
  if (rows.length !== 3) throw new Error("Three declared span rows required");
  const { renderer, css } = await loadRuntime();
  const chart = renderer.withMaterialOverrides(profile, {
    lowEndStrength: 1, lowEnd44: tuple(rows[0]!), lowEnd96: tuple(rows[1]!), lowEnd160: tuple(rows[2]!),
  });
  const level = decode(input / 255);
  const material = css.materialAtBackdrop(chart, "regular",
    { luminance: level, linearLuminance: level, rgb: [level, level, level] }, span, nominal, dpr);
  return encode(material.level) * 255;
}

export async function fixedJoins(profile: MaterialProfile): Promise<{
  span: number; dpr: number; value: number;
}[]> {
  const { css } = await loadRuntime();
  const off = { ...profile, lowEndStrength: 0 };
  const size = css.sourceSize(off);
  const response = css.resolvedBackdropToneResponse(off);
  const result = [];
  for (const dpr of [1, 2]) for (let span = 32; span <= 224; span++) {
    const level = css.backdropToneResponseLevel(64 / 255, css.sizeThickness(span, size),
      response, css.sizeToneLevelFar(span, size, dpr), span);
    result.push({ span, dpr, value: encode(level) * 255 });
  }
  return result;
}

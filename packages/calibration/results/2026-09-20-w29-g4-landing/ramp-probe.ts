/**
 * The response curve's own values across the browser suite's twelve-step ramp,
 * per shipped material document (W29 G4, claims §5.155).
 *
 * `platform-web/e2e/pixel/backdrop-tone-pixels.spec.ts` sweeps twelve flat
 * backdrops from black to a mid grey and asserts that the small surface's
 * RENDERED level never moves the wrong way. That assertion moved at this landing,
 * and this is the reading it moved against: the curve's target level and the
 * collapse amount at each step, for macOS 26.5 and macOS 27 side by side, so the
 * difference is a document's and not an opinion.
 *
 *     npx tsx results/2026-09-20-w29-g4-landing/ramp-probe.ts
 */
import {
  colorSchemeMaterialProfile,
  DEFAULT_MATERIAL_PROFILE_DOCUMENT,
  macos26MaterialProfileDocument,
  backdropToneAdaptation,
  backdropToneResponseLevel,
  resolvedBackdropTone,
  resolvedBackdropToneResponse,
  sizeThickness,
  sourceSize,
  type GlassMaterialProfileDocument,
} from "@vitreajs/vitrea-web";

const decode = (value: number): number =>
  value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;

const STEPS = 12;
const SPANS = [44, 140];

for (const [name, document] of [
  ["macOS 27 (the default)", DEFAULT_MATERIAL_PROFILE_DOCUMENT],
  ["macOS 26.5", macos26MaterialProfileDocument],
] as const satisfies readonly (readonly [string, GlassMaterialProfileDocument])[]) {
  const patch = colorSchemeMaterialProfile("light", document);
  const size = sourceSize(patch);
  const tone = resolvedBackdropTone(patch);
  const response = resolvedBackdropToneResponse(patch);
  process.stdout.write(`\n${name}\n`);
  process.stdout.write(
    `  adaptation band ${tone.low} … ${tone.high}, size bias ${tone.sizeBias}, ` +
      `anchors ${response.anchorX.join(", ")}\n`,
  );
  for (const span of SPANS) {
    const thickness = sizeThickness(span, size);
    const row: string[] = [];
    for (let i = 0; i < STEPS; i += 1) {
      const grey = Math.round((i / (STEPS - 1)) * 140);
      const linear = decode(grey / 255);
      const target = backdropToneResponseLevel(grey / 255, thickness, response);
      const collapse = backdropToneAdaptation(linear, thickness, tone);
      row.push(`${String(grey).padStart(3)}:${target.toFixed(4)}/k${collapse.toFixed(2)}`);
    }
    process.stdout.write(`  span ${span} (thickness ${thickness.toFixed(4)})\n`);
    process.stdout.write(`    ${row.join("  ")}\n`);
  }
}

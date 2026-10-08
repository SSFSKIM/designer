/** W50's compact response is one target/authority law; these are synthetic, not fitted rows. */
import type { ResolvedMaterialPolicy } from "@vitreajs/vitrea";
import { describe, expect, it } from "vitest";
import {
  MATERIAL_SOURCE_OPTICS,
  backdropToneResponseLevel,
  materialAtBackdrop,
  lowEndNeutralRequest,
  resolvedBackdropToneResponse,
  sizeThickness,
  sourceSize,
  toneRespondedSourceOptics,
  type MaterialSourceOptics,
} from "../src/optics";
import type { RendererMaterialProfile } from "../src/renderer-bridge";

const decode = (x: number): number =>
  x <= 0.04045 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4;
const encode = (x: number): number =>
  x <= 0.0031308 ? x * 12.92 : 1.055 * x ** (1 / 2.4) - 0.055;
const chart = {
  lowEndStrength: 1,
  lowEnd44: [20 / 255, 28 / 255, 50 / 255, 64 / 255] as const,
  lowEnd96: [24 / 255, 32 / 255, 54 / 255, 68 / 255] as const,
  lowEnd160: [28 / 255, 36 / 255, 58 / 255, 72 / 255] as const,
};
const patch: RendererMaterialProfile = {
  ...chart,
  backdropToneAnchorX: [0.004, 0.11, 0.425, 0.95],
  backdropToneResponseThin: [0.08, 0.15, 0.2, 0.35],
  backdropToneResponseThick: [0.10, 0.17, 0.25, 0.4],
  backdropToneBlackStrength: 1,
  backdropToneBlackThin: 0.02,
  backdropToneBlackThick: 0.03,
};
const source = { ...MATERIAL_SOURCE_OPTICS.regular, tint: [0.08, 0.08, 0.08] as const,
  tintAlpha: 0.8 };
const policy: ResolvedMaterialPolicy = {
  glass: "material", colorSource: "material", frost: "nominal", refraction: "nominal",
  occlusion: "nominal", border: "nominal", ambientTint: "nominal", foreground: "adaptive",
};
const tone = (code: number) => {
  const level = decode(code / 255);
  return { rgb: [level, level, level] as const, luminance: level, linearLuminance: level };
};
const composite = (result: MaterialSourceOptics, linear: number): number =>
  (1 - result.tintAlpha) * linear + result.tintAlpha * result.tint[0];

describe("W50 CSS low-end response", () => {
  it("interpolates encoded output in input and span, holding only the measured outer rows", () => {
    const response = resolvedBackdropToneResponse(patch);
    // Expected codes are hand-derived from the two linear axes, before decoding the target.
    for (const [span, input, output] of [
      [44, 0, 20], [44, 1, 21], [44, 4, 24], [44, 8, 28], [44, 18, 39],
      [44, 28, 50], [44, 34, 57], [44, 40, 64],
      [96, 0, 24], [96, 8, 32], [96, 28, 54], [96, 40, 68],
      [160, 0, 28], [160, 8, 36], [160, 28, 58], [160, 40, 72],
      [70, 18, 41], [128, 34, 63], [32, 40, 64], [224, 40, 72],
    ]) {
      expect(backdropToneResponseLevel(input! / 255, 0.5, response, 0, span!),
        `span ${span}, input ${input}`).toBeCloseTo(decode(output! / 255), 14);
    }
    // Appending the span parameter preserves the historical caller's default span 44.
    expect(backdropToneResponseLevel(8 / 255, 0.5, response)).toBeCloseTo(decode(28 / 255), 14);
  });

  it("joins at 64 to the old response at actual thickness and far level, not a held span row", () => {
    const on = resolvedBackdropToneResponse(patch);
    const off = resolvedBackdropToneResponse({ ...patch, lowEndStrength: 0 });
    for (const [span, thickness, far, code40] of [
      [32, 0, 0, 64], [70, 0.3, 0, 66], [128, 1, 0.015, 70], [224, 1, 0.07, 72],
    ]) {
      const old64 = backdropToneResponseLevel(64 / 255, thickness!, off, far!, span!);
      const midpoint = decode((code40! / 255 + encode(old64)) / 2);
      expect(backdropToneResponseLevel(52 / 255, thickness!, on, far!, span!))
        .toBeCloseTo(midpoint, 14);
      for (const input of [64 / 255, 64 / 255 + 1e-10, 69 / 255, 0.425, 0.95, 1]) {
        expect(backdropToneResponseLevel(input, thickness!, on, far!, span!))
          .toBe(backdropToneResponseLevel(input, thickness!, off, far!, span!));
      }
      expect(backdropToneResponseLevel(64 / 255 - 1e-10, thickness!, on, far!, span!))
        .toBeCloseTo(old64, 8);
    }
  });

  it("gives the enabled solve full low-end authority without changing the protected old domain", () => {
    const on = resolvedBackdropToneResponse(patch);
    const off = resolvedBackdropToneResponse({ ...patch, lowEndStrength: 0 });
    for (const [code, output] of [[0, 20], [0.25, 20.25], [0.8, 20.8], [1, 21],
      [4, 24], [8, 28], [18, 39], [28, 50], [40, 64]]) {
      const sample = tone(code!);
      const solved = toneRespondedSourceOptics(source, sample, 0, 0, 1, on, 0, 44);
      expect(encode(composite(solved, sample.linearLuminance)) * 255,
        `input ${code}`).toBeCloseTo(output!, 10);
    }
    for (const code of [64, 69, 128, 255]) {
      expect(toneRespondedSourceOptics(source, tone(code), 0.7, 0, 1, on, 0.01, 128))
        .toEqual(toneRespondedSourceOptics(source, tone(code), 0.7, 0, 1, off, 0.01, 128));
    }
  });

  it("blends target and authority independently for fractional chart strength", () => {
    const on = resolvedBackdropToneResponse({ ...patch, lowEndStrength: 0.4 });
    const off = resolvedBackdropToneResponse({ ...patch, lowEndStrength: 0 });
    const encoded = 0.0035;
    const sample = { luminance: decode(encoded), linearLuminance: decode(encoded) };
    const oldTarget = backdropToneResponseLevel(encoded, 0, off);
    const chartTarget = decode((20 + encoded * 255) / 255);
    const target = oldTarget + (chartTarget - oldTarget) * 0.4;
    const oldAuthority = 0.75 ** 2 * (3 - 2 * 0.75);
    const authority = oldAuthority + (1 - oldAuthority) * 0.4;
    const nominal = composite(source, sample.linearLuminance);
    const expected = nominal + (target - nominal) * authority;
    expect(backdropToneResponseLevel(encoded, 0, on)).toBeCloseTo(target, 14);
    const solved = toneRespondedSourceOptics(source, sample, 0, 0, 1, on);
    expect(composite(solved, sample.linearLuminance)).toBeCloseTo(expected, 14);
  });

  it("leaves gate-zero rows unread and preserves old response and solve arithmetic exactly", () => {
    const inert = { ...patch, lowEndStrength: 0 };
    Object.defineProperty(inert, "lowEnd44", { get: () => { throw new Error("read inert chart"); } });
    const response = resolvedBackdropToneResponse(inert);
    const old = resolvedBackdropToneResponse({ ...patch, lowEndStrength: 0 });
    for (const span of [32, 44, 96, 128, 160, 224]) {
      for (const code of [0, 0.2, 0.7, 1, 8, 28, 40, 64, 69, 128, 255]) {
        expect(backdropToneResponseLevel(code / 255, 0.4, response, 0.02, span))
          .toBe(backdropToneResponseLevel(code / 255, 0.4, old, 0.02, span));
        expect(toneRespondedSourceOptics(source, tone(code), 0.4, 0, 1, response, 0.02, span))
          .toEqual(toneRespondedSourceOptics(source, tone(code), 0.4, 0, 1, old, 0.02, span));
      }
    }
  });

  it("validates the finite unit gate always, and enabled rows as ordered four-knot output tuples", () => {
    for (const gate of [NaN, Infinity, -0.01, 1.01]) {
      expect(() => resolvedBackdropToneResponse({ ...patch, lowEndStrength: gate }))
        .toThrow(/lowEndStrength/);
    }
    for (const row of [null, "bad", [0, 0.1, 0.2], [0, 0.1, 0.2, 0.3, 0.4],
      [NaN, 0.1, 0.2, 0.3], [0, 0.1, Infinity, 1], [-0.1, 0.1, 0.2, 0.3],
      [0, 0.1, 0.2, 1.1], [0, 0.2, 0.1, 0.3]]) {
      for (const key of ["lowEnd44", "lowEnd96", "lowEnd160"]) {
        expect(() => resolvedBackdropToneResponse({ ...patch, [key]: row } as RendererMaterialProfile))
          .toThrow(new RegExp(key));
      }
    }
    expect(() => resolvedBackdropToneResponse({ ...patch, lowEnd44: [0, 0, 1, 1] })).not.toThrow();
    expect(() => resolvedBackdropToneResponse({ ...patch, lowEndStrength: 0,
      lowEnd44: [NaN] } as unknown as RendererMaterialProfile)).not.toThrow();
  });

  it("keeps the alpha, collapse, profile-strength and caller-strength stand-down thresholds", () => {
    const response = resolvedBackdropToneResponse(patch);
    for (const [alpha, k, strength] of [[0, 0, 1], [0.001, 0, 1], [0.8, 0.995, 1],
      [0.8, 1, 1], [0.8, 0, 0]]) {
      const input = { ...source, tintAlpha: alpha! };
      expect(toneRespondedSourceOptics(input, tone(0), 0, k!, strength!, response))
        .toBe(input);
    }
    expect(toneRespondedSourceOptics(source, tone(0), 0, 0, 1, { ...response, strength: 0 }))
      .toBe(source);
    for (const [alpha, k] of [[0.00101, 0], [0.8, 0.99499]]) {
      const input = { ...source, tintAlpha: alpha! };
      expect(toneRespondedSourceOptics(input, tone(0), 0, k!, 1, response)).not.toBe(input);
    }
    const half = toneRespondedSourceOptics(source, tone(0), 0, 0, 0.5,
      { ...response, strength: 0.6 });
    const nominal = composite(source, 0);
    expect(composite(half, 0)).toBeCloseTo(
      nominal + (decode(20 / 255) - nominal) * 0.6 * 0.5 * 0.5, 14,
    );
  });

  it("referees cumulative drawdown on the composed uniform response, not merely ordered rows", () => {
    const response = resolvedBackdropToneResponse(patch);
    const size = sourceSize(patch);
    let worstDrawdown = 0;
    for (let span = 32; span <= 224; span++) {
      let runningMax = -Infinity;
      for (let step = 0; step <= 64 * 64; step++) {
        const sample = tone(step / 64);
        const solved = toneRespondedSourceOptics(source, sample, sizeThickness(span, size),
          0, 1, response, 0, span);
        const output = encode(composite(solved, sample.linearLuminance)) * 255;
        worstDrawdown = Math.max(worstDrawdown, runningMax - output);
        runningMax = Math.max(runningMax, output);
      }
    }
    expect(worstDrawdown).toBeLessThanOrEqual(1e-4);
    // Ordered measured rows are insufficient: the fixed join can still lie below T40.
    const bad = resolvedBackdropToneResponse({ ...patch,
      lowEnd44: [0.1, 0.2, 0.5, 0.8],
      lowEnd96: [0.1, 0.2, 0.5, 0.8],
      lowEnd160: [0.1, 0.2, 0.5, 0.8],
    });
    let runningMax = -Infinity;
    let drawdown = 0;
    for (let step = 0; step <= 64 * 64; step++) {
      const sample = tone(step / 64);
      const solved = toneRespondedSourceOptics(source, sample, 0, 0, 1, bad);
      const output = encode(composite(solved, sample.linearLuminance)) * 255;
      drawdown = Math.max(drawdown, runningMax - output);
      runningMax = Math.max(runningMax, output);
    }
    expect(drawdown).toBeGreaterThan(1);
  }, 15_000);

  it("reports the actual pre-clamp neutral request and preserves the distinct linear mean", () => {
    const response = resolvedBackdropToneResponse(patch);
    const structured = { luminance: decode(4 / 255), linearLuminance: 0.1 };
    const requested = lowEndNeutralRequest(source, structured, 0, 0, 1, response);
    // Transmitting 20% of a 0.1 linear mean already exceeds the 24-code target.
    const expected = (decode(24 / 255) - 0.2 * 0.1) / 0.8;
    expect(requested).toEqual([expect.closeTo(expected, 14), expect.closeTo(expected, 14),
      expect.closeTo(expected, 14)]);
    expect(requested!.every((channel) => channel < 0)).toBe(true);
    const result = toneRespondedSourceOptics(source, structured, 0, 0, 1, response);
    expect(result.tint).toEqual([0, 0, 0]);
    expect(lowEndNeutralRequest(source, tone(4), 0, 0, 1, response)![0]).toBeGreaterThan(0);
    for (const [alpha, k, strength] of [[0.001, 0, 1], [0.8, 0.995, 1], [0.8, 1, 1],
      [0.8, 0, 0]]) {
      expect(lowEndNeutralRequest({ ...source, tintAlpha: alpha! }, structured,
        0, k!, strength!, response)).toBeUndefined();
    }
    expect(lowEndNeutralRequest(source, structured, 0, 0, 1, { ...response, strength: 0 }))
      .toBeUndefined();
    expect(lowEndNeutralRequest(source, structured, 0, 0, 1, { ...response, lowEndStrength: 0 }))
      .toBeUndefined();
    expect(lowEndNeutralRequest(source, tone(64), 0, 0, 1, response)).toBeUndefined();
  });

  it("passes the actual surface span and preserves unknown-tone and policy stand-downs", () => {
    const profile: RendererMaterialProfile = {
      ...patch,
      optics: { regular: { tint: source.tint, tintAlpha: source.tintAlpha } },
      backdropToneSizeBias: 1,
      backdropToneLow: 0,
      backdropToneHigh: 0.001,
      sizeOcclusionGain: 0,
    };
    for (const [span, code] of [[44, 20], [70, 22], [96, 24], [128, 26], [160, 28], [224, 28]]) {
      const result = materialAtBackdrop(profile, "regular", tone(0), span!, policy);
      expect(result.adaptation).toBe(0);
      expect(encode(result.level) * 255, `span ${span}`).toBeCloseTo(code!, 10);
    }
    const off = { ...profile, lowEndStrength: 0 };
    expect(materialAtBackdrop(profile, "regular", undefined, 160, policy))
      .toEqual(materialAtBackdrop(off, "regular", undefined, 160, policy));
    for (const folded of [
      { ...policy, refraction: "none", frost: "increased", occlusion: "increased" },
      { ...policy, ambientTint: "reduced" },
    ] as ResolvedMaterialPolicy[]) {
      expect(materialAtBackdrop(profile, "regular", tone(0), 160, folded))
        .toEqual(materialAtBackdrop(off, "regular", tone(0), 160, folded));
    }
    // Full collapse keeps ownership even when a chart requests a visible positive floor.
    expect(materialAtBackdrop(profile, "regular", tone(0), 32, policy).responded)
      .toEqual(materialAtBackdrop(off, "regular", tone(0), 32, policy).responded);
  });
});

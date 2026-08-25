import { describe, expect, it } from "vitest";

import { CalibrationError } from "../src/errors";
import {
  alphaChannel,
  assertComparable,
  clampRect,
  createImage,
  decodePng,
  encodedLuma,
  linearLuminance,
  toLinearRgb,
} from "../src/image";
import { alphaMaskImage, encodePng, fromLinearLuminance, solidLuminance } from "./synthesise";

describe("image decoding", () => {
  it("round-trips an RGBA image through a PNG buffer byte for byte", () => {
    const original = alphaMaskImage(9, 7, (x, y) => x > y);
    const decoded = decodePng(encodePng(original));

    expect(decoded.width).toBe(9);
    expect(decoded.height).toBe(7);
    expect([...decoded.data]).toEqual([...original.data]);
  });

  it("refuses a buffer that is not the size it claims", () => {
    expect(() => createImage(4, 4, new Uint8Array(60))).toThrowError(CalibrationError);
    expect(() => createImage(0, 4, new Uint8Array(0))).toThrowError(/positive integer size/);
  });
});

describe("comparison guard", () => {
  it("refuses two differently sized captures instead of resizing one", () => {
    const a = solidLuminance(16, 16, 0.5);
    const b = solidLuminance(16, 15, 0.5);

    let caught: unknown;
    try {
      assertComparable(a, b, "unit test");
    } catch (error) {
      caught = error;
    }

    expect(caught).toBeInstanceOf(CalibrationError);
    expect((caught as CalibrationError).code).toBe("dimension-mismatch");
    // The message has to be actionable: in practice the cause is a DPR mistake.
    expect((caught as CalibrationError).message).toMatch(/16x16 and 16x15/);
    expect((caught as CalibrationError).message).toMatch(/never resizes/);
  });

  it("passes two captures of the same size", () => {
    expect(() => assertComparable(solidLuminance(8, 8, 0), solidLuminance(8, 8, 1))).not.toThrow();
  });
});

describe("channel extraction", () => {
  it("recovers the linear-light luminance a grey was built from", () => {
    const image = fromLinearLuminance(4, 4, (x) => 0.1 + 0.2 * x);
    const luminance = linearLuminance(image);

    for (let y = 0; y < 4; y += 1) {
      for (let x = 0; x < 4; x += 1) {
        // 8-bit quantisation is the only loss; it is worst in the bright half.
        expect(luminance[y * 4 + x]).toBeCloseTo(Math.min(1, 0.1 + 0.2 * x), 2);
      }
    }
  });

  it("keeps linear RGB and encoded luma in different domains", () => {
    const image = solidLuminance(2, 2, 0.2);
    const linear = toLinearRgb(image);
    const encoded = encodedLuma(image);

    expect(linear[0]).toBeCloseTo(0.2, 2);
    // Encoded luma lives on 0..255 and is far above 0.2 * 255 — the two are not
    // interchangeable, which is the whole reason both exist.
    expect(encoded[0]).toBeGreaterThan(0.4 * 255);
  });

  it("reads alpha as its own channel", () => {
    const image = alphaMaskImage(4, 1, (x) => x < 2);
    expect([...alphaChannel(image)]).toEqual([255, 255, 0, 0]);
  });
});

describe("regions", () => {
  it("defaults to the whole image and clamps an oversized rect", () => {
    const image = solidLuminance(10, 10, 0.5);
    expect(clampRect(image, undefined)).toEqual({ x: 0, y: 0, width: 10, height: 10 });
    expect(clampRect(image, { x: 5, y: 5, width: 100, height: 100 })).toEqual({ x: 5, y: 5, width: 5, height: 5 });
  });

  it("refuses a rect that misses the image entirely", () => {
    const image = solidLuminance(10, 10, 0.5);
    expect(() => clampRect(image, { x: 40, y: 40, width: 4, height: 4 })).toThrowError(CalibrationError);
  });
});

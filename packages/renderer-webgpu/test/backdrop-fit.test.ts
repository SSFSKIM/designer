/**
 * `backdrop-fit.ts` — the map from a source's placement to the uv transform the
 * optics pass samples through, and to the density a CSS-px σ is converted with.
 *
 * The properties pinned here are the ones claims §5.47 rests on: a texture the
 * size of the viewport at its origin fits identically under both rules (which is
 * why no golden and no calibration capture moved), a placed texture maps the
 * viewport pixel under it to the texel under it, and the density follows the
 * placed box rather than the viewport.
 */
import { describe, expect, it } from "vitest";
import {
  backdropFit,
  coverFit,
  isUsablePlacement,
  placementFit,
  samePlacement,
  texelsPerCssPx,
} from "../src/backdrop-fit";

const close = (actual: readonly number[], expected: readonly number[]): void => {
  expect(actual).toHaveLength(expected.length);
  for (let i = 0; i < expected.length; i += 1) {
    expect(actual[i]).toBeCloseTo(expected[i] as number, 9);
  }
};

describe("the placed fit", () => {
  it("is the identity when the texture is the whole viewport", () => {
    // The calibration stage: a 320×200 raster at the origin of a 320×200 viewport.
    close(placementFit({ x: 0, y: 0, width: 320, height: 200 }, 320, 200), [1, 1, 0, 0]);
    close(backdropFit(320, 200, { x: 0, y: 0, width: 320, height: 200 }, 320, 200), [1, 1, 0, 0]);
  });

  it("maps the viewport pixel under a placed texture to the texel under it", () => {
    // The demo's reference panel: a 320×200 raster at (681, 48) on a 1440×900 page.
    const placement = { x: 681, y: 48, width: 320, height: 200 };
    const [sx, sy, ox, oy] = placementFit(placement, 1440, 900);
    const uvOf = (xCss: number, yCss: number): readonly [number, number] => [
      (xCss / 1440) * sx + ox,
      (yCss / 900) * sy + oy,
    ];
    close(uvOf(681, 48), [0, 0]);
    close(uvOf(681 + 320, 48 + 200), [1, 1]);
    close(uvOf(681 + 160, 48 + 100), [0.5, 0.5]);
    // A pixel left of the box lands below 0, where the sampler clamps.
    expect(uvOf(600, 100)[0]).toBeLessThan(0);
  });

  it("keeps a displacement in CSS px as the same distance in texels", () => {
    // The lens displaces in CSS px and divides by the viewport before the fit;
    // through a placed fit that is displacement / placement.width in uv, so a
    // 33 px displacement over a 320 px box is 33/320 of the texture.
    const [sx] = placementFit({ x: 100, y: 100, width: 320, height: 200 }, 1440, 900);
    expect((33 / 1440) * sx).toBeCloseTo(33 / 320, 12);
  });

  it("falls back to cover for a placement with no area, and reports it unusable", () => {
    expect(isUsablePlacement(undefined)).toBe(false);
    expect(isUsablePlacement({ x: 0, y: 0, width: 0, height: 100 })).toBe(false);
    expect(isUsablePlacement({ x: 0, y: 0, width: 100, height: 0 })).toBe(false);
    expect(isUsablePlacement({ x: Number.NaN, y: 0, width: 100, height: 100 })).toBe(false);
    expect(isUsablePlacement({ x: 0, y: 0, width: 100, height: 100 })).toBe(true);
    close(
      backdropFit(256, 256, { x: 0, y: 0, width: 0, height: 0 }, 200, 120),
      coverFit(256, 256, 200, 120),
    );
  });
});

describe("the cover fit", () => {
  it("fills the viewport and crops the overflow symmetrically", () => {
    // A square source on a wide viewport keeps the width and crops the height.
    const [sx, sy, ox, oy] = coverFit(256, 256, 200, 120);
    expect(sx).toBe(1);
    expect(sy).toBeCloseTo(0.6, 12);
    expect(ox).toBe(0);
    expect(oy).toBeCloseTo(0.2, 12);
    // A wide source on a squarer viewport keeps the height and crops the width.
    const [tx, ty, px, py] = coverFit(400, 100, 200, 100);
    expect(tx).toBeCloseTo(0.5, 12);
    expect(ty).toBe(1);
    expect(px).toBeCloseTo(0.25, 12);
    expect(py).toBe(0);
  });

  it("is the identity when the source has the viewport's aspect", () => {
    close(coverFit(320, 200, 320, 200), [1, 1, 0, 0]);
    close(coverFit(640, 400, 320, 200), [1, 1, 0, 0]);
  });
});

describe("texels per CSS px", () => {
  it("is 1 for a 1:1 raster placed at its own size, whatever the viewport", () => {
    expect(texelsPerCssPx(320, 200, { x: 681, y: 48, width: 320, height: 200 }, 1440, 900)).toBe(1);
  });

  it("is 2 for a @2x raster shown at half its size, as it is for the 2x stage", () => {
    expect(texelsPerCssPx(640, 400, { x: 10, y: 10, width: 320, height: 200 }, 1440, 900)).toBe(2);
    // The calibration stage at DPR 2: a 640×400 raster covering a 320×200 viewport.
    expect(texelsPerCssPx(640, 400, undefined, 320, 200)).toBe(2);
  });

  it("agrees with the cover ratio where the placement is the viewport", () => {
    expect(texelsPerCssPx(320, 200, { x: 0, y: 0, width: 320, height: 200 }, 320, 200)).toBe(
      texelsPerCssPx(320, 200, undefined, 320, 200),
    );
  });

  it("follows the placed width, not the height, when the box distorts the source", () => {
    expect(texelsPerCssPx(200, 200, { x: 0, y: 0, width: 100, height: 400 }, 800, 600)).toBe(2);
  });

  it("keeps the cover rule's larger ratio without a placement", () => {
    // Cover keeps the axis the crop preserves: 0.22 texels per CSS px here, one
    // texel every 4.5 CSS px — the stretch the demo's reference panel was
    // sampling through before §5.47.
    expect(texelsPerCssPx(320, 200, undefined, 1440, 900)).toBeCloseTo(320 / 1440, 12);
    expect(texelsPerCssPx(3840, 2160, undefined, 390, 844)).toBeCloseTo(3840 / 390, 12);
  });
});

describe("placement identity", () => {
  it("compares by value, and treats absent as equal only to absent", () => {
    const a = { x: 1, y: 2, width: 3, height: 4 };
    expect(samePlacement(a, { ...a })).toBe(true);
    expect(samePlacement(a, { ...a, x: 2 })).toBe(false);
    expect(samePlacement(undefined, undefined)).toBe(true);
    expect(samePlacement(a, undefined)).toBe(false);
  });
});

/**
 * Instance packing — where X8 rider 2 is either honoured or not.
 *
 * The rider (tightened at C3's landing, Decision Log #22b) binds the renderer to
 * draw a concentric child as a **level set of the parent's field**. The test that
 * matters is not "does it look right" but the arithmetic one: the packed instance
 * must carry the PARENT's half-extents, reach and coefficients, plus the child's
 * inset. If it carried the child's own resolved shape instead, the offset
 * approximation would enter — 0.326 px at 8 px inset, past the field's declared
 * 0.170 px bound and dominant past about 4 px.
 */

import { describe, expect, it } from "vitest";
import { DEFAULT_GROUP_UNION, fieldParams, resolveShape } from "@vitrea/geometry";
import { DEFAULT_MOTION_PROFILE } from "@vitrea/motion";

import { RendererError } from "../src/errors";
import {
  clipFieldRectToCanvas,
  groupFieldRect,
  INSTANCE_FLOATS,
  packInstances,
  resolveSurfaces,
  snapRectToDevicePixels,
} from "../src/instances";
import { LENS_HEIGHT_MAX } from "../src/material";
import type { GroupRenderInput, SurfaceInput } from "../src/render-model";

const surface = (over: Partial<SurfaceInput> = {}): SurfaceInput => ({
  nodeId: "s1",
  family: "fixed-rounded-rect",
  shape: {
    center: [100, 60],
    size: [120, 40],
    radii: [20, 20, 20, 20],
    smoothing: 0,
    thickness: 8,
  },
  reference: "figma-smoothing",
  ...over,
});

const group = (surfaces: readonly SurfaceInput[]): GroupRenderInput => ({
  groupId: "g1",
  surfaces,
  refraction: "true",
  analysisExact: true,
});

describe("the packed layout", () => {
  it("is eighteen floats: X8's geometry, the six derived floats, the channels and the two per-pixel scalars", () => {
    // Sixteen until W2 and W3 each needed a per-surface scalar that the fragment
    // stage reads per pixel — the size law's thickness factor and the author
    // tint's strength. Seventeen is not a legal stride (`vec2f` aligns the struct
    // to 8 bytes), so the eighteenth float is padding; `wgsl-contract.test.ts`
    // pins that rule against the WGSL declaration itself.
    expect(INSTANCE_FLOATS).toBe(18);

    const resolved = resolveSurfaces(group([surface()]), "rsupn");
    const { data, count } = packInstances(resolved, [0, 0]);

    expect(count).toBe(1);
    expect(data.length).toBeGreaterThanOrEqual(INSTANCE_FLOATS);
  });

  it("writes the six derived floats the instance buffer widens by", () => {
    const resolved = resolveSurfaces(group([surface()]), "rsupn");
    const { data } = packInstances(resolved, [0, 0]);
    const expected = fieldParams(
      resolveShape({
        family: "fixed-rounded-rect",
        center: [100, 60],
        size: [120, 40],
        radii: 20,
        profile: 0,
        thickness: 8,
      }),
    );

    expect(data[2]).toBeCloseTo(expected.halfW, 10);
    expect(data[3]).toBeCloseTo(expected.halfH, 10);
    expect(data[4]).toBeCloseTo(expected.reach, 10);
    for (let i = 0; i < 5; i += 1) {
      expect(data[5 + i]).toBeCloseTo(expected.k[i] as number, 10);
    }
  });

  it("makes centres relative to the group's rect", () => {
    // f32 loses resolution at large magnitudes, so a field evaluated at y = 40000
    // would quantise its own corner.
    const resolved = resolveSurfaces(group([surface()]), "rsupn");
    const { data } = packInstances(resolved, [90, 40]);
    expect(data[0]).toBeCloseTo(10, 10);
    expect(data[1]).toBeCloseTo(20, 10);
  });

  it("reuses a caller's buffer when it is large enough", () => {
    const resolved = resolveSurfaces(group([surface()]), "rsupn");
    const scratch = new Float32Array(INSTANCE_FLOATS * 4);
    const { data } = packInstances(resolved, [0, 0], scratch);
    expect(data).toBe(scratch);
  });

  it("allocates when the caller's buffer is too small", () => {
    const resolved = resolveSurfaces(group([surface(), surface({ nodeId: "s2" })]), "rsupn");
    const tiny = new Float32Array(4);
    const { data } = packInstances(resolved, [0, 0], tiny);
    expect(data).not.toBe(tiny);
    expect(data.length).toBeGreaterThanOrEqual(2 * INSTANCE_FLOATS);
  });
});

describe("X8 rider 2 — concentric renders as a level set", () => {
  const parent = surface({ nodeId: "parent" });
  const child = surface({
    nodeId: "child",
    family: "concentric-rounded-rect",
    concentricOf: { nodeId: "parent", inset: 8 },
  });

  it("packs the PARENT's field parameters and the child's inset", () => {
    const resolved = resolveSurfaces(group([parent, child]), "rsupn");
    const { data } = packInstances(resolved, [0, 0]);

    const parentSlice = [...data.slice(0, 10)];
    const childSlice = [...data.slice(INSTANCE_FLOATS, INSTANCE_FLOATS + 10)];

    // Same centre, same half-extents, same reach, same coefficients — the child IS
    // the parent's field. Only the inset differs.
    expect(childSlice).toEqual(parentSlice);
    expect(data[INSTANCE_FLOATS + 10]).toBeCloseTo(8, 10);
    expect(data[10]).toBe(0);
  });

  it("never packs the child's own resolved half-extents", () => {
    // This is the instantiated-shape path the rider rules out. The child's own
    // shape IS resolved — for bounds and hit-testing — but it must not reach the
    // field.
    const resolved = resolveSurfaces(group([parent, child]), "rsupn");
    const packedChild = resolved[1];
    expect(packedChild).toBeDefined();

    const ownHalfW = (packedChild?.shape.channels.size[0] ?? 0) / 2;
    expect(ownHalfW).toBeCloseTo(120 / 2 - 8, 10);
    expect(packedChild?.field.halfW).toBeCloseTo(120 / 2, 10);
    expect(packedChild?.field.halfW).not.toBeCloseTo(ownHalfW, 3);
  });

  it("still resolves the child's own shape, because bounds need it", () => {
    const resolved = resolveSurfaces(group([parent, child]), "rsupn");
    expect(resolved[1]?.shape.family).toBe("concentric-rounded-rect");
    expect(resolved[1]?.shape.channels.size).toEqual([104, 24]);
  });

  it("refuses a parent outside the group, because a level set needs its field", () => {
    const orphan = surface({
      nodeId: "orphan",
      concentricOf: { nodeId: "elsewhere", inset: 4 },
    });
    expect(() => resolveSurfaces(group([orphan]), "rsupn")).toThrowError(RendererError);
    try {
      resolveSurfaces(group([orphan]), "rsupn");
    } catch (error) {
      expect((error as RendererError).code).toBe("pass-input");
      expect((error as RendererError).message).toContain("rider 2");
    }
  });

  it("refuses a concentric cycle instead of recursing forever", () => {
    const a = surface({ nodeId: "a", concentricOf: { nodeId: "b", inset: 2 } });
    const b = surface({ nodeId: "b", concentricOf: { nodeId: "a", inset: 2 } });
    expect(() => resolveSurfaces(group([a, b]), "rsupn")).toThrowError(/cycle/);
  });

  it("chains: a level set of a level set still resolves to the root's field", () => {
    const middle = surface({
      nodeId: "middle",
      concentricOf: { nodeId: "parent", inset: 4 },
    });
    const inner = surface({
      nodeId: "inner",
      concentricOf: { nodeId: "middle", inset: 4 },
    });
    const resolved = resolveSurfaces(group([parent, middle, inner]), "rsupn");
    // `inner` is a level set of `middle`'s own resolved shape, which is the honest
    // reading: `middle` is an instance of the group, so its field is what `inner`
    // offsets from.
    expect(resolved[2]?.inset).toBe(4);
    expect(resolved[2]?.field.halfW).toBeCloseTo(resolved[1]?.shape.channels.size[0] as number / 2, 10);
  });
});

describe("press compression", () => {
  it("scales the size by motion's own constant, and re-derives the corner", () => {
    // §Motion: "this is what 1 means, so the renderer needs no constant of its
    // own." And the corner budget is a function of size, so a compressed surface
    // must re-derive rather than scale a corner derived at rest.
    const pressed = resolveSurfaces(
      group([surface({ channels: { press: 1 } })]),
      "rsupn",
    );
    const scale = 1 - DEFAULT_MOTION_PROFILE.pressCompressionScale;
    expect(pressed[0]?.shape.channels.size[0]).toBeCloseTo(120 * scale, 10);
    expect(pressed[0]?.shape.channels.size[1]).toBeCloseTo(40 * scale, 10);
  });

  it("leaves an unpressed surface untouched", () => {
    const idle = resolveSurfaces(group([surface()]), "rsupn");
    expect(idle[0]?.shape.channels.size).toEqual([120, 40]);
  });
});

describe("the size-parameterised lens", () => {
  it("gives a larger surface a deeper lens at the same thickness", () => {
    // Parent acceptance #2's mechanism, as arithmetic.
    const small = resolveSurfaces(
      group([surface({ shape: { ...surface().shape, size: [40, 24] } })]),
      "rsupn",
    );
    // Span 500 is past the height law's clamp, so the depth has saturated at the
    // reference's 20 (W12 G2): the size term stops growing instead of running
    // away on a full-width platter.
    const large = resolveSurfaces(
      group([surface({ shape: { ...surface().shape, size: [600, 500] } })]),
      "rsupn",
    );

    expect(large[0]?.lensDepthPx).toBeGreaterThan(small[0]?.lensDepthPx as number);
    expect(large[0]?.lensDepthPx).toBeCloseTo(LENS_HEIGHT_MAX, 6);
  });

  it("clamps a small control so it cannot be all lens", () => {
    const tiny = resolveSurfaces(
      group([
        surface({
          shape: { ...surface().shape, size: [40, 16], thickness: 40 },
        }),
      ]),
      "rsupn",
    );
    // Half the shorter extent, never more.
    expect(tiny[0]?.lensDepthPx).toBeCloseTo(8, 6);
  });

  it("packs the thickness scaled by the lensStrength channel, for both depths (W12 G2)", () => {
    // The slot carries the authored thickness times the strength; the shader
    // evaluates the lens's depth and the inner shadow's from it and the span.
    const resolved = resolveSurfaces(
      group([surface({ channels: { lensStrength: 0.5 } })]),
      "rsupn",
    );
    const { data } = packInstances(resolved, [0, 0]);
    expect(data[14]).toBeCloseTo((resolved[0]?.shape.channels.thickness as number) * 0.5, 6);
  });
});

describe("the field pass's rect", () => {
  it("covers every member plus what can reach past a contour", () => {
    const resolved = resolveSurfaces(group([surface()]), "rsupn");
    const rect = groupFieldRect(resolved, DEFAULT_GROUP_UNION, 2);

    // Members span x 40..160, y 40..80. Padding is rim + bulge cap + one pixel.
    const pad = 2 + DEFAULT_GROUP_UNION.maxBulge + 1;
    expect(rect.x).toBeCloseTo(40 - pad, 10);
    expect(rect.width).toBeCloseTo(120 + 2 * pad, 10);
    expect(rect.y).toBeCloseTo(40 - pad, 10);
    expect(rect.height).toBeCloseTo(40 + 2 * pad, 10);
  });

  it("is not padded by the lens depth, which displaces sampling and not drawing", () => {
    const thin = resolveSurfaces(
      group([surface({ shape: { ...surface().shape, thickness: 1 } })]),
      "rsupn",
    );
    const thick = resolveSurfaces(
      group([surface({ shape: { ...surface().shape, thickness: 40 } })]),
      "rsupn",
    );
    expect(groupFieldRect(thin)).toEqual(groupFieldRect(thick));
  });

  it("unions members, so a group's rect covers all of them", () => {
    const resolved = resolveSurfaces(
      group([
        surface({ nodeId: "a", shape: { ...surface().shape, center: [50, 60] } }),
        surface({ nodeId: "b", shape: { ...surface().shape, center: [300, 60] } }),
      ]),
      "rsupn",
    );
    const rect = groupFieldRect(resolved);
    expect(rect.x).toBeLessThan(50 - 60);
    expect(rect.x + rect.width).toBeGreaterThan(300 + 60);
  });

  it("returns an empty rect for an empty group rather than infinities", () => {
    expect(groupFieldRect([])).toEqual({ x: 0, y: 0, width: 0, height: 0 });
  });

  it("snaps outward to whole device pixels, so no edge falls between texels", () => {
    const snapped = snapRectToDevicePixels({ x: 10.3, y: 20.7, width: 30.4, height: 5.1 }, 2);
    expect(snapped.x * 2).toBe(Math.floor(10.3 * 2));
    expect((snapped.x + snapped.width) * 2).toBe(Math.ceil((10.3 + 30.4) * 2));
    expect(snapped.x).toBeLessThanOrEqual(10.3);
    expect(snapped.x + snapped.width).toBeGreaterThanOrEqual(10.3 + 30.4);
  });
});

describe("family C, the governor's step", () => {
  it("packs family C's own coefficients, not family D's", () => {
    // The two families share a zero level set but not a fit, so taking family C
    // means taking family C's coefficients too.
    // Radius well inside the corner budget, so the budget clamp leaves the
    // authored smoothing alone — at radius == budget the clamp drives effective
    // smoothing to 0 and both families fit the same circular corner, which would
    // make this test vacuous.
    const smoothed = surface({
      reference: "figma-smoothing",
      shape: {
        ...surface().shape,
        size: [200, 200],
        radii: [30, 30, 30, 30],
        smoothing: 0.6,
      },
    });
    const d = resolveSurfaces(group([smoothed]), "rsupn");
    const c = resolveSurfaces(group([smoothed]), "rsup");

    expect(d[0]?.field.reach).toBeCloseTo(c[0]?.field.reach as number, 10);
    expect([...(d[0]?.field.k ?? [])]).not.toEqual([...(c[0]?.field.k ?? [])]);
  });
});

describe("duplicate surfaces", () => {
  it("refuses two surfaces with the same id", () => {
    expect(() => resolveSurfaces(group([surface(), surface()]), "rsupn")).toThrowError(
      /twice/,
    );
  });
});

describe("clipping the field rect to the canvas", () => {
  const CANVAS: readonly [number, number] = [1440, 900];

  it("leaves a rect that is entirely on the canvas exactly where it was", () => {
    // The regression that matters most: every existing golden draws a group that
    // is fully on screen, and clipping must not move any of them by a pixel.
    const snapped = snapRectToDevicePixels({ x: 100, y: 200, width: 320, height: 180 }, 2);
    const clipped = clipFieldRectToCanvas(snapped, 2, [2880, 1800]);

    expect(clipped).toEqual({ x: 200, y: 400, width: 640, height: 360 });
  });

  it("clips a rect that reaches past the top-left origin, rather than going negative", () => {
    // `groupFieldRect` pads by the rim and bulge margin, so a surface at the
    // viewport edge lands here with a negative origin. `setScissorRect` takes
    // unsigned values, so this is the difference between a clipped draw and a
    // RangeError.
    const clipped = clipFieldRectToCanvas({ x: -5, y: -5, width: 130, height: 54 }, 1, CANVAS);

    expect(clipped).toEqual({ x: 0, y: 0, width: 125, height: 49 });
  });

  it("clips a rect that reaches past the far edge", () => {
    const clipped = clipFieldRectToCanvas({ x: 1400, y: 880, width: 100, height: 100 }, 1, CANVAS);

    expect(clipped).toEqual({ x: 1400, y: 880, width: 40, height: 20 });
  });

  it("returns nothing at all for a rect entirely off the canvas", () => {
    expect(clipFieldRectToCanvas({ x: -200, y: 10, width: 100, height: 10 }, 1, CANVAS)).toBe(
      undefined,
    );
    expect(clipFieldRectToCanvas({ x: 10, y: 1000, width: 100, height: 10 }, 1, CANVAS)).toBe(
      undefined,
    );
  });

  it("clips in device pixels, so the device-pixel ratio scales the clip", () => {
    const clipped = clipFieldRectToCanvas({ x: -4, y: -4, width: 100, height: 100 }, 2, [200, 200]);

    // -8 device px clipped to 0, and the far edge at (-4 + 100) * 2 = 192 kept.
    expect(clipped).toEqual({ x: 0, y: 0, width: 192, height: 192 });
  });
});

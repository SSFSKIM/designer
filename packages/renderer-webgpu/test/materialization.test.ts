/**
 * W27d — presence, not alpha: the `materialization` channel on the WebGPU tier.
 *
 * Apple states the rule twice — "prefer setting the effect property over the
 * alpha", and a surface materializes "by gradually modulating the light bending
 * and lensing" — and the runtime states it a third time from the other side: any
 * `opacity < 1` on a host or one of its ancestors forms a Backdrop Root and kills
 * the group's proxy sampling (W27 §Where each feature lives, binding; contract
 * X6). So a surface's presence is a scalar on the MATERIAL's optical terms and
 * never a scalar on the element.
 *
 * What this file pins is the CPU half — the channel as a per-surface number with
 * an idle of 1, riding the instance buffer's one free float (the padding the
 * `vec2f` alignment already required), bounded on its way in, and touching
 * nothing else in the buffer at any value the surface is drawn at. A value that
 * is not a number is the undriven case and not a surface asked to disappear,
 * which is the same distinction `lensStrength` draws.
 *
 * And the endpoint, which is a CPU fact rather than a shader one: exactly 0
 * drops the member before the field pass, so it owns no coverage and joins no
 * union. That is what makes `Glass.identity` exact — the group's rect, its
 * instance buffer and therefore its pixels become the ones it would have had
 * without the member — and it is why the continuum of scaled optical terms lives
 * strictly above zero.
 *
 * What the material DOES with it is behaviour, and behaviour is measured on
 * pixels: `e2e/gpu/materialization.spec.ts` renders one scene at two presences on
 * a real adapter, proves the endpoint carries no material by rendering it under a
 * material it cannot tell from the shipped one, and proves that at 1 the bytes
 * are the bytes of a scene nobody drove. Nothing here restates the shaders.
 */

import { describe, expect, it } from "vitest";

import {
  groupFieldRect,
  INSTANCE_FLOATS,
  packInstances,
  resolveSurfaces,
} from "../src/instances";
import { IDLE_CHANNELS, type GroupRenderInput, type SurfaceInput } from "../src/render-model";
import { createWebGPURenderer } from "../src/renderer";

import { createFakeGpu, type FakeGpu } from "./harness/fake-gpu";

/**
 * The tint seed as the optics pass is handed it: `d[20..22]` of the uniform
 * (`passes.ts`), read off the fake device rather than inferred.
 */
function seedWrites(gpu: FakeGpu): Float32Array[] {
  const writes: Float32Array[] = [];
  const queue = gpu.device.queue as unknown as { writeBuffer: (...args: unknown[]) => void };
  queue.writeBuffer = (buffer, _offset, data, dataOffset, size) => {
    if (!String((buffer as { label?: string }).label ?? "").includes("uniform:optics")) return;
    const view = new Float32Array(
      data as ArrayBuffer,
      Number(dataOffset ?? 0),
      Number(size ?? (data as ArrayBuffer).byteLength) / 4,
    );
    writes.push(Float32Array.from(view.subarray(20, 23)));
  };
  return writes;
}

const surface = (
  over: Partial<SurfaceInput> & { readonly center?: readonly [number, number] } = {},
): SurfaceInput => {
  const { center, ...rest } = over;
  return {
    nodeId: "s1",
    family: "fixed-rounded-rect",
    shape: {
      center: center === undefined ? [100, 60] : [center[0], center[1]],
      size: [120, 40],
      radii: [20, 20, 20, 20],
      smoothing: 0,
      thickness: 8,
    },
    reference: "figma-smoothing",
    ...rest,
  };
};

const group = (surfaces: readonly SurfaceInput[]): GroupRenderInput => ({
  groupId: "g1",
  surfaces,
  refraction: "true",
  analysisExact: true,
});

/** The instance slot the channel rides: the last float of the struct. */
const MATERIALIZATION_SLOT = INSTANCE_FLOATS - 1;

const packed = (channels?: Partial<SurfaceInput["channels"]>): Float32Array =>
  packInstances(
    resolveSurfaces(group([surface(channels === undefined ? {} : { channels })]), "rsupn"),
    [0, 0],
  ).data;

describe("W27d the channel and its idle", () => {
  it("names an idle of 1, so an undriven surface is a present one", () => {
    // Zero and "nobody is driving this" are different claims, exactly as they are
    // for `lensStrength`: 0 is a surface asked to be absent, which a driver may
    // legitimately ask for, and 1 is a surface nobody asked anything of.
    expect(IDLE_CHANNELS.materialization).toBe(1);
  });

  it("packs the idle into the slot the stride already paid for", () => {
    expect(packed()[MATERIALIZATION_SLOT]).toBe(1);
  });

  it("packs a driven value verbatim", () => {
    expect(packed({ materialization: 0.35 })[MATERIALIZATION_SLOT]).toBeCloseTo(0.35, 6);
    // Small but present is still packed; exactly 0 has no instance to pack into
    // at all, which the endpoint cases below are about.
    expect(packed({ materialization: 1e-6 })[MATERIALIZATION_SLOT]).toBeCloseTo(1e-6, 9);
  });

  it("clamps into 0..1 and answers NaN with the idle, not with an end of the clamp", () => {
    // A clamp does not catch NaN — it compares false against everything — and a
    // non-finite value packed into a `Float32Array` reaches the shader as a
    // non-finite per-pixel scalar, which does not draw a strange material: it
    // blanks the passes that read it.
    expect(packed({ materialization: 4 })[MATERIALIZATION_SLOT]).toBe(1);
    // Below zero is zero, which is the absent case: no instance is packed, so the
    // buffer is the empty one rather than a surface at a negative presence.
    expect(
      packInstances(
        resolveSurfaces(group([surface({ channels: { materialization: -2 } })]), "rsupn"),
        [0, 0],
      ).count,
    ).toBe(0);
    expect(packed({ materialization: Number.POSITIVE_INFINITY })[MATERIALIZATION_SLOT]).toBe(1);
    expect(packed({ materialization: Number.NaN })[MATERIALIZATION_SLOT]).toBe(
      IDLE_CHANNELS.materialization,
    );
  });

  it("moves no other float in the buffer, at any value the surface is drawn at", () => {
    // The byte-identity claim, stated where it can be checked without a GPU: the
    // channel took the slot that was already being written as zero, and nothing
    // else in the instance is a function of it. The geometry a presence of 0.35
    // packs is the geometry a presence of 1 packs, so nothing about the surface
    // moves, shrinks or softens — only the material the shader draws over it.
    const rest = (data: Float32Array): number[] => [...data.slice(0, MATERIALIZATION_SLOT)];
    expect(rest(packed({ materialization: 0.35 }))).toEqual(rest(packed()));
    expect(rest(packed({ materialization: 1e-6 }))).toEqual(rest(packed()));
  });

  it("resolves per surface, so one member of a group may be dim and another present", () => {
    const resolved = resolveSurfaces(
      group([
        surface({ nodeId: "a", channels: { materialization: 0.25 } }),
        surface({ nodeId: "b" }),
      ]),
      "rsupn",
    );
    expect(resolved.map((s) => s.materialization)).toEqual([0.25, 1]);
  });
});

describe("W27d exactly 0 is the absence of the surface, not the bottom of the ramp", () => {
  it("draws no instance for a member at 0, and every instance for one just above it", () => {
    // `Glass.identity`: the glass animated to nothing in place. A member with no
    // glass on it has no silhouette either, so it leaves the field pass entirely
    // rather than arriving with every term multiplied by zero.
    const absent = resolveSurfaces(
      group([surface({ nodeId: "a", channels: { materialization: 0 } }), surface({ nodeId: "b" })]),
      "rsupn",
    );
    expect(absent.map((s) => s.nodeId)).toEqual(["b"]);

    const dim = resolveSurfaces(
      group([
        surface({ nodeId: "a", channels: { materialization: 1e-6 } }),
        surface({ nodeId: "b" }),
      ]),
      "rsupn",
    );
    expect(dim.map((s) => s.nodeId)).toEqual(["a", "b"]);
  });

  it("hands a group of nothing but absent members no instances at all", () => {
    // What the renderer reads as "skip this group": an empty surface list makes
    // `groupFieldRect` a zero rect, which `clipFieldRectToCanvas` answers with
    // `undefined`, and no pass is encoded for the group at all.
    const none = resolveSurfaces(
      group([
        surface({ nodeId: "a", channels: { materialization: 0 } }),
        surface({ nodeId: "b", channels: { materialization: 0 } }),
      ]),
      "rsupn",
    );
    expect(none).toEqual([]);
    expect(groupFieldRect(none)).toEqual({ x: 0, y: 0, width: 0, height: 0 });
  });

  it("leaves an absent member's neighbours exactly the group they would have alone", () => {
    // The endpoint stated where it can be stated exactly: the instance buffer and
    // the field rect of a group whose member is at 0 are the buffer and the rect
    // of the same group without that member. Nothing downstream can then tell the
    // two apart — which is what makes an absent member unable to bend a present
    // neighbour's union.
    const withAbsent = resolveSurfaces(
      group([
        surface({ nodeId: "a", center: [40, 60], channels: { materialization: 0 } }),
        surface({ nodeId: "b", center: [120, 60] }),
      ]),
      "rsupn",
    );
    const alone = resolveSurfaces(group([surface({ nodeId: "b", center: [120, 60] })]), "rsupn");

    expect(groupFieldRect(withAbsent)).toEqual(groupFieldRect(alone));
    expect([...packInstances(withAbsent, [0, 0]).data]).toEqual([
      ...packInstances(alone, [0, 0]).data,
    ]);
  });

  it("still resolves an absent surface as a concentric child's parent field", () => {
    // The shapes are resolved before the drop, so X8 rider 2 survives it: a child
    // is its parent's field plus an inset whether or not the parent is drawn.
    const parentPresent = resolveSurfaces(
      group([
        surface({ nodeId: "parent" }),
        surface({
          nodeId: "child",
          family: "concentric-rounded-rect",
          concentricOf: { nodeId: "parent", inset: 8 },
        }),
      ]),
      "rsupn",
    );
    const parentAbsent = resolveSurfaces(
      group([
        surface({ nodeId: "parent", channels: { materialization: 0 } }),
        surface({
          nodeId: "child",
          family: "concentric-rounded-rect",
          concentricOf: { nodeId: "parent", inset: 8 },
        }),
      ]),
      "rsupn",
    );

    expect(parentAbsent.map((s) => s.nodeId)).toEqual(["child"]);
    const childOf = (resolved: readonly { nodeId: string }[]) =>
      resolved.find((s) => s.nodeId === "child");
    expect(childOf(parentAbsent)).toEqual(childOf(parentPresent));
  });

  it("takes the group's tint seed from a member that is still there", () => {
    /*
     * The group's uniforms have to agree with the drop, and this is the one that
     * can disagree: the seed is per group ("the first tinted DRAWN member wins")
     * while the strength is per pixel, so a group whose emphasised control has
     * dematerialized while a second tinted control is still up would otherwise
     * paint the survivor in the absent control's hue.
     */
    const orange = { color: [1, 0.4, 0] as const, strength: 1 };
    const blue = { color: [0, 0.3, 1] as const, strength: 1 };
    const gpu = createFakeGpu();
    const seeds = seedWrites(gpu);
    const renderer = createWebGPURenderer({
      viewport: { widthCss: 320, heightCss: 200, devicePixelRatio: 1 },
    });
    renderer.attachDevice(gpu.device, "vitrea");
    renderer.setGroup({
      groupId: "g",
      refraction: "true",
      analysisExact: true,
      surfaces: [
        surface({
          nodeId: "gone",
          center: [80, 100],
          tint: orange,
          channels: { materialization: 0 },
        }),
        surface({ nodeId: "here", center: [220, 100], tint: blue }),
      ],
    });
    renderer.drawFrame({
      frame: { id: 1, timeMs: 16.7 },
      optics: {} as GPUTextureView,
      highlight: {} as GPUTextureView,
    });

    const seed = seeds.at(-1);
    expect(seed).toBeDefined();
    // Channel by channel: the seed crosses the seam as f32, so the blue's 0.3
    // arrives as 0.30000001 and an exact comparison would be a comparison of
    // float widths rather than of which control the colour came from.
    for (let channel = 0; channel < 3; channel += 1) {
      expect((seed as Float32Array)[channel]).toBeCloseTo(blue.color[channel] as number, 6);
    }
  });
});

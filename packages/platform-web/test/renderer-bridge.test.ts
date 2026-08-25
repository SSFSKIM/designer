/**
 * The frame conversion: `renderInput()` → renderer groups.
 *
 * This is the half of the bridge with no device in it, and it carries the
 * decisions worth pinning — which groups the GPU draws at all, which of them
 * bind a backdrop, how a measured rect becomes X8's channel vector, and which
 * plane a surface lands on. The GPU half is exercised in the Playwright suite,
 * against a real adapter, because nothing short of one proves it.
 *
 * The renderer's own input types are reached through its public interface in
 * `renderer-bridge.ts`, so a signature change in C6 fails this file's *build*
 * rather than one of its assertions.
 */

import { NOMINAL_ACCESSIBILITY_POLICY, type GlassGroupState } from "@vitreajs/vitrea";
import { DEFAULT_GROUP_UNION, groupUnionFromMergeDistance } from "@vitrea/geometry";
import { describe, expect, it } from "vitest";

import { IDLE_CHANNELS } from "../src/channels";
import { MATERIAL_OPTICS } from "../src/optics";
import { toRendererGroups, toRendererResolution } from "../src/renderer-bridge";
import type {
  GlassFrameRenderInput,
  GlassGroupRenderInput,
  GlassNodeRenderInput,
  GlassPlaneRenderInput,
} from "../src/root";

const WEBGPU_TEXTURE_STATE: GlassGroupState = {
  configuredSource: "texture",
  activeRenderer: "webgpu",
  samplingBackend: "gpu-texture",
  refraction: "true",
  analysis: "exact",
  health: "ok",
};

const WEBGPU_DOM_STATE: GlassGroupState = {
  configuredSource: "dom",
  activeRenderer: "webgpu",
  samplingBackend: "css-backdrop",
  refraction: "approximate",
  analysis: "hint",
  health: "ok",
};

const CSS_STATE: GlassGroupState = {
  configuredSource: "dom",
  activeRenderer: "css",
  samplingBackend: "css-backdrop",
  refraction: "none",
  analysis: "none",
  health: "demoted",
  demotionReason: "no-webgpu",
};

const node = (overrides: Partial<GlassNodeRenderInput> = {}): GlassNodeRenderInput => ({
  nodeId: "n1",
  groupId: "g1",
  plane: "base",
  order: 0,
  bounds: { x: 100, y: 50, width: 200, height: 80 },
  shapeFamily: "fixed-rounded-rect",
  radii: [22, 22, 22, 22],
  smoothing: 0.6,
  thickness: 10,
  channels: IDLE_CHANNELS,
  material: { variant: "regular", adaptation: "adaptive" },
  foreground: { adaptation: { mode: "fixed" } },
  optics: MATERIAL_OPTICS.regular,
  refraction: { state: "true", accessibilityCap: "true", effective: "true" },
  ownedTransform: undefined,
  ...overrides,
});

const group = (overrides: Partial<GlassGroupRenderInput> = {}): GlassGroupRenderInput => ({
  groupId: "g1",
  state: WEBGPU_TEXTURE_STATE,
  probe: { groupId: "g1", verdict: "pass", breaks: [], reach: "verified" },
  backdropSourceId: "src",
  variant: "regular",
  samplingPadding: 24,
  mergeDistance: 24,
  declaredMergeDistance: undefined,
  blurRadius: 8,
  ...overrides,
});

const frame = (
  groups: readonly GlassGroupRenderInput[],
  planes: readonly { plane: GlassPlaneRenderInput["plane"]; nodes: readonly GlassNodeRenderInput[] }[],
): GlassFrameRenderInput => ({
  frame: { id: 1, timeMs: 16 },
  accessibility: NOMINAL_ACCESSIBILITY_POLICY,
  planes: planes.map((entry) => ({
    plane: entry.plane,
    // The layer DOM is never read by the conversion; it travels for the bridge's
    // own use, and a cast keeps this fixture from building a document.
    layers: undefined as unknown as GlassPlaneRenderInput["layers"],
    nodes: entry.nodes,
  })),
  groups,
  viewport: { width: 1280, height: 720, devicePixelRatio: 2 },
  device: undefined,
});

const always = (): boolean => true;
const never = (): boolean => false;

describe("toRendererGroups", () => {
  it("turns a measured rect into X8's channel vector", () => {
    const [base] = toRendererGroups(frame([group()], [{ plane: "base", nodes: [node()] }]), always);
    const surface = base?.groups[0]?.surfaces[0];

    // `bounds` is a top-left rect; the shape channels are centre-and-extent.
    expect(surface?.shape.center).toEqual([200, 90]);
    expect(surface?.shape.size).toEqual([200, 80]);
    expect(surface?.shape.radii).toEqual([22, 22, 22, 22]);
    expect(surface?.shape.smoothing).toBe(0.6);
    expect(surface?.shape.thickness).toBe(10);
    expect(surface?.family).toBe("fixed-rounded-rect");
    expect(surface?.variant).toBe("regular");
  });

  it("carries the channel values straight through", () => {
    const channels = { press: 0.3, glow: 0.9, sweep: 0.1, lensStrength: 1.2, pressPoint: [150, 70] as const };
    const [base] = toRendererGroups(
      frame([group()], [{ plane: "base", nodes: [node({ channels })] }]),
      always,
    );

    expect(base?.groups[0]?.surfaces[0]?.channels).toEqual(channels);
  });

  it("binds a backdrop only where the state sampled one and pixels were supplied", () => {
    const bound = toRendererGroups(
      frame([group()], [{ plane: "base", nodes: [node()] }]),
      always,
    )[0]?.groups[0];
    expect(bound?.backdropSourceId).toBe("src");

    // Declared as a texture, but nobody ever called `setBackdropTexture`. Binding
    // the id anyway would ask the renderer to sample a source it has no provider
    // for, which is a skipped group rather than an honest state.
    const unsupplied = toRendererGroups(
      frame([group()], [{ plane: "base", nodes: [node()] }]),
      never,
    )[0]?.groups[0];
    expect(unsupplied?.backdropSourceId).toBeUndefined();
  });

  it("gives a dom-mode group no source at all, so it builds no pyramid", () => {
    // §honesty core: in dom-backdrop mode the browser compositor does the blur
    // and the GPU renders rim, tint and glow. An unbound source is what makes
    // "the GPU builds no pyramid at all" true rather than described.
    const [base] = toRendererGroups(
      frame(
        [group({ state: WEBGPU_DOM_STATE, backdropSourceId: "vitrea.dom" })],
        [{ plane: "base", nodes: [node()] }],
      ),
      always,
    );

    expect(base?.groups[0]?.backdropSourceId).toBeUndefined();
    expect(base?.groups[0]?.refraction).toBe("approximate");
    expect(base?.groups[0]?.analysisExact).toBe(false);
  });

  it("omits a group core resolved to the CSS tier", () => {
    // The CSS tier is painting this group's host in the same frame. Drawing it
    // here too would put two materials on one surface.
    const [base] = toRendererGroups(
      frame([group({ state: CSS_STATE })], [{ plane: "base", nodes: [node()] }]),
      always,
    );

    expect(base?.groups).toHaveLength(0);
  });

  it("reports analysisExact only where X2 resolved exact analysis", () => {
    const exact = toRendererGroups(
      frame([group()], [{ plane: "base", nodes: [node()] }]),
      always,
    )[0]?.groups[0];
    expect(exact?.analysisExact).toBe(true);
  });

  it("splits surfaces by plane and keeps the group on both", () => {
    // A group whose members straddle a promotion draws on each plane's canvas
    // pair. It keeps its entry on both — with an empty surface list where it has
    // nothing — because removing and re-adding it would discard the renderer's
    // cached field target twice a frame.
    const planes = toRendererGroups(
      frame(
        [group()],
        [
          { plane: "base", nodes: [node({ nodeId: "a" })] },
          { plane: "overlay", nodes: [node({ nodeId: "b", plane: "overlay" })] },
        ],
      ),
      always,
    );

    expect(planes.map((entry) => entry.plane)).toEqual(["base", "overlay"]);
    expect(planes[0]?.groups[0]?.surfaces.map((surface) => surface.nodeId)).toEqual(["a"]);
    expect(planes[1]?.groups[0]?.surfaces.map((surface) => surface.nodeId)).toEqual(["b"]);
  });

  it("forwards DEFAULT_GROUP_UNION when the group declared no mergeDistance", () => {
    // K3: before this wiring, the renderer's DEFAULT_GROUP_UNION was reached by
    // omission (the `union` field was simply absent). Now it is forwarded
    // explicitly, but the values — and the no-declaration case — must be
    // identical to what the renderer already defaulted to.
    const [base] = toRendererGroups(
      frame([group({ declaredMergeDistance: undefined })], [{ plane: "base", nodes: [node()] }]),
      always,
    );

    expect(base?.groups[0]?.union).toEqual(DEFAULT_GROUP_UNION);
  });

  it("derives the union params from a declared mergeDistance", () => {
    const [base] = toRendererGroups(
      frame([group({ declaredMergeDistance: 40 })], [{ plane: "base", nodes: [node()] }]),
      always,
    );

    expect(base?.groups[0]?.union).toEqual(groupUnionFromMergeDistance(40));
    expect(base?.groups[0]?.union).toEqual({
      neckWidth: 20,
      maxBulge: 5,
      separationThreshold: 40,
    });
  });

  it("leaves a plane's group empty rather than dropping it", () => {
    const planes = toRendererGroups(
      frame(
        [group()],
        [
          { plane: "base", nodes: [node()] },
          { plane: "overlay", nodes: [] },
        ],
      ),
      always,
    );

    expect(planes[1]?.groups).toHaveLength(1);
    expect(planes[1]?.groups[0]?.surfaces).toEqual([]);
  });
});

describe("toRendererResolution", () => {
  it("hands core's resolved state through as the renderer's authority", () => {
    const resolution = toRendererResolution(
      frame(
        [group(), group({ groupId: "g2", state: WEBGPU_DOM_STATE })],
        [{ plane: "base", nodes: [node()] }],
      ),
    );

    expect(resolution.groups).toEqual([
      { groupId: "g1", state: { refraction: "true", analysis: "exact", samplingBackend: "gpu-texture" } },
      {
        groupId: "g2",
        state: { refraction: "approximate", analysis: "hint", samplingBackend: "css-backdrop" },
      },
    ]);
  });

  it("carries the accessibility policy, which is the other half of the dual cap", () => {
    // Decision Log #19: the renderer honours the lower of the accessibility cap
    // and the state's refraction. Handing it a pre-collapsed number would take
    // that fold away from the side that owns it.
    const resolution = toRendererResolution(frame([group()], [{ plane: "base", nodes: [node()] }]));

    expect(resolution.accessibility.material).toBe(NOMINAL_ACCESSIBILITY_POLICY.material);
  });

  it("includes a CSS-tier group, so the renderer sees the whole frame's state", () => {
    const resolution = toRendererResolution(
      frame([group({ state: CSS_STATE })], [{ plane: "base", nodes: [] }]),
    );

    expect(resolution.groups).toHaveLength(1);
  });
});

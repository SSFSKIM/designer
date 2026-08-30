import { describe, expect, it } from "vitest";

import { DEFAULT_GROUP_SAMPLING } from "@vitreajs/vitrea";

import { MATERIAL_OPTICS, requiredSamplingPadding, SAMPLING_PADDING_SIGMA_MULTIPLE } from "../src/optics";
import {
  resolveProxyGeometry,
  resolveSamplingGeometry,
  roundedRectPath,
  type ProxyGeometry,
  type ProxyGeometryInput,
  type ProxyMember,
} from "../src/proxy-geometry";

const member = (x: number, y: number, width = 120, height = 44, radius = 22): ProxyMember => ({
  nodeId: `n${x}-${y}`,
  bounds: { x, y, width, height },
  radii: [radius, radius, radius, radius],
});

const base: ProxyGeometryInput = {
  members: [member(100, 100)],
  samplingPadding: 24,
  mergeDistance: 24,
  blurRadius: 8,
  devicePixelRatio: 1,
  maxProxyAreaDevicePx: Number.POSITIVE_INFINITY,
};

/** Narrow the optional result without a non-null assertion. */
function resolved(input: ProxyGeometryInput): ProxyGeometry {
  const geometry = resolveProxyGeometry(input);
  if (geometry === undefined) throw new Error("expected a proxy geometry for these members");
  return geometry;
}

const codes = (geometry: ProxyGeometry): readonly string[] =>
  geometry.findings.map((finding) => finding.code);

describe("proxy geometry (X1, as S1 measured it)", () => {
  it("pads the border box and masks the shape union — the box/mask split is normative", () => {
    const geometry = resolved({ ...base, samplingPadding: 30, blurRadius: 10 });

    // Box: the member union inflated by the padding. Filter Effects 2 clips the
    // filter *input* to the filtered element's own border box, so an unpadded
    // box starves its own blur at the shape edge.
    expect(geometry.box).toEqual({ x: 70, y: 70, width: 180, height: 104 });
    // Mask: the shape union only. Masking to box+padding instead leaves a
    // full-strength blurred rectangle standing proud of the glass — S1 measured
    // that halo at mean 102.92/255.
    expect(geometry.clipPath.startsWith("path(")).toBe(true);
    expect(geometry.maskBounds).toEqual([{ x: 30, y: 30, width: 120, height: 44 }]);
    // The same union in viewport coordinates: what this proxy *paints*, as
    // against the box it *samples*. The cross-group overlap check needs the two
    // told apart, because the padding between them is a region nothing draws in.
    expect(geometry.clipUnion).toEqual({ x: 100, y: 100, width: 120, height: 44 });
  });

  it("raises a padding below 3σ to 3σ, and says so", () => {
    const geometry = resolved({ ...base, samplingPadding: 8, blurRadius: 20 });

    expect(requiredSamplingPadding(20)).toBe(60);
    expect(geometry.effectivePadding).toBe(60);
    expect(codes(geometry)).toContain("sampling-padding-below-3-sigma");
  });

  it("leaves a padding already at or above 3σ alone", () => {
    const geometry = resolved({ ...base, samplingPadding: 64, blurRadius: 20, mergeDistance: 64 });

    expect(geometry.effectivePadding).toBe(64);
    expect(geometry.findings).toEqual([]);
  });

  it("puts the 3σ floor where the blur radius lives, which core cannot see", () => {
    expect(SAMPLING_PADDING_SIGMA_MULTIPLE).toBe(3);
    // Verified byte-exact at three radii spanning 5× (S1 Q1).
    expect([8, 20, 40].map(requiredSamplingPadding)).toEqual([24, 60, 120]);
    // And at the shipped material's own σ, whatever it is. This used to read
    // `toBe(24)` because core's advisory was 3σ at the σ = 8 the material then
    // had; the cascade refitted σ to 3 (2026-08-31) and the relationship, not the
    // number, is what this line was ever asserting.
    expect(requiredSamplingPadding(MATERIAL_OPTICS.regular.blurRadius)).toBe(
      MATERIAL_OPTICS.regular.blurRadius * SAMPLING_PADDING_SIGMA_MULTIPLE,
    );
  });

  it("reports when enforcement pushes the padding past the group's mergeDistance", () => {
    // core checks mergeDistance >= samplingPadding against the *authored*
    // padding; raising the padding to 3σ here can break the relation core
    // already cleared, so the DOM consequence is checked where it is created.
    const geometry = resolved({ ...base, samplingPadding: 24, mergeDistance: 24, blurRadius: 20 });

    expect(geometry.effectivePadding).toBe(60);
    expect(codes(geometry)).toContain("merge-distance-below-effective-padding");
  });

  it("unions every member into one box and one multi-subpath mask", () => {
    const geometry = resolved({ ...base, members: [member(100, 100), member(260, 100)] });

    expect(geometry.box).toEqual({ x: 76, y: 76, width: 328, height: 92 });
    // Every member, not just the first: the painted rect is the whole union.
    expect(geometry.clipUnion).toEqual({ x: 100, y: 100, width: 280, height: 44 });
    expect(geometry.maskBounds).toHaveLength(2);
    // One proxy per sampling group, never one per member.
    expect(geometry.clipPath.match(/M/g)).toHaveLength(2);
  });

  it("emits the mask in proxy-local coordinates, so the element can be positioned by its box", () => {
    const geometry = resolved({ ...base, members: [member(400, 300)] });

    expect(geometry.box.x).toBe(376);
    expect(geometry.maskBounds[0]).toMatchObject({ x: 24, y: 24 });
  });

  it("trims the padding back toward 3σ when the proxy would exceed the area cap", () => {
    // S1: headless Chromium silently drops backdrop-filter above roughly
    // 1.75–3.0 Mpx of device-pixel proxy area; retail Chrome never does, so a
    // page cannot tell which rasteriser it is on — hence a cap, not a probe.
    const geometry = resolved({
      ...base,
      members: [member(0, 0, 600, 400)],
      samplingPadding: 300,
      mergeDistance: 300,
      blurRadius: 8,
      devicePixelRatio: 2,
      maxProxyAreaDevicePx: 1_750_000,
    });

    expect(codes(geometry)).toContain("proxy-area-over-cap");
    expect(geometry.effectivePadding).toBeLessThan(300);
    expect(geometry.effectivePadding).toBeGreaterThanOrEqual(requiredSamplingPadding(8));
    expect(geometry.box.width * geometry.box.height * 4).toBeLessThanOrEqual(1_750_000);
  });

  it("never trims below 3σ to satisfy the cap — a starved blur is the worse failure", () => {
    const geometry = resolved({
      ...base,
      members: [member(0, 0, 1400, 900)],
      samplingPadding: 100,
      mergeDistance: 100,
      blurRadius: 8,
      devicePixelRatio: 2,
      maxProxyAreaDevicePx: 1_750_000,
    });

    expect(geometry.effectivePadding).toBe(requiredSamplingPadding(8));
    const overCap = geometry.findings.find((finding) => finding.code === "proxy-area-over-cap");
    expect(overCap?.severity).toBe("error");
  });

  it("never builds a proxy for a group with no measured members", () => {
    expect(resolveProxyGeometry({ ...base, members: [] })).toBeUndefined();
  });

  it("ignores a member whose rect has not been measured yet", () => {
    const geometry = resolved({
      ...base,
      members: [
        member(100, 100),
        { nodeId: "unmeasured", bounds: { x: 0, y: 0, width: 0, height: 0 }, radii: [0, 0, 0, 0] },
      ],
    });

    expect(geometry.maskBounds).toHaveLength(1);
  });
});

describe("the mask path builder", () => {
  it("clamps a corner radius to half the shorter side, so a mask path never self-crosses", () => {
    const capsule = roundedRectPath({ x: 0, y: 0, width: 120, height: 44 }, [99, 99, 99, 99]);

    expect(capsule).toContain("22");
    expect(capsule).not.toContain("99");
  });

  it("emits a closed subpath with one arc per corner", () => {
    const path = roundedRectPath({ x: 10, y: 20, width: 100, height: 50 }, [8, 8, 8, 8]);

    expect(path.match(/A/g)).toHaveLength(4);
    expect(path.trimEnd().endsWith("Z")).toBe(true);
  });

  it("takes each corner's own radius", () => {
    const path = roundedRectPath({ x: 0, y: 0, width: 100, height: 100 }, [4, 8, 12, 16]);

    for (const radius of [4, 8, 12, 16]) expect(path).toContain(`A ${radius} ${radius}`);
  });

  it("degenerates to a plain rectangle at radius zero", () => {
    const path = roundedRectPath({ x: 0, y: 0, width: 10, height: 10 }, [0, 0, 0, 0]);

    expect(path).not.toContain("A");
    expect(path.trimEnd().endsWith("Z")).toBe(true);
  });
});

/*
 * The default padding, derived rather than constant.
 *
 * core defaults `samplingPadding` to 24, and 24 is 3σ at the regular material's
 * nominal σ of 8 — the same floor this module enforces, because one number was
 * written from the other. They part company the moment an accessibility
 * preference moves σ: `reducedTransparency` frosts at 1.75×, so σ becomes 14,
 * the floor becomes 42, and a group that never declared a padding is below a
 * floor it was written to sit exactly on. A 0.1.1 consumer flipped one prop and
 * got seven warnings about geometry they had never authored.
 */
describe("the default sampling geometry, derived from the blur the material draws with", () => {
  it("is exactly 3σ of the shipped blur, and no longer core's constant", () => {
    /*
     * W6's neutrality argument was that the derivation reproduced core's 24
     * exactly, because 24 is 3σ at σ = 8. The recalibration cascade refitted σ to
     * 3 against the active-pose bed (2026-08-31), so the derivation now yields 9
     * and the two numbers have parted company — which is the derivation working
     * rather than failing. The invariant was never the 24; it was the multiple.
     *
     * core's advisory stays at 24 deliberately. Its only stated requirement is to
     * be at least 3σ of the group's blur, and at the refitted σ it clears that
     * with room to spare. Lowering a public default for tidiness rather than for
     * a measurement would change behaviour for every consumer that never reaches
     * this derivation, and this is the path that actually ships.
     */
    const blurRadius = MATERIAL_OPTICS.regular.blurRadius;
    expect(
      resolveSamplingGeometry({ samplingPadding: undefined, mergeDistance: undefined, blurRadius }),
    ).toEqual({
      samplingPadding: requiredSamplingPadding(blurRadius),
      mergeDistance: requiredSamplingPadding(blurRadius),
    });
    expect(requiredSamplingPadding(blurRadius)).toBeLessThanOrEqual(
      DEFAULT_GROUP_SAMPLING.samplingPadding,
    );
  });

  it("follows the blur up when an accessibility policy raises it", () => {
    // σ = 8 × 1.75 under reduced transparency.
    expect(
      resolveSamplingGeometry({ samplingPadding: undefined, mergeDistance: undefined, blurRadius: 14 }),
    ).toEqual({ samplingPadding: 42, mergeDistance: 42 });
  });

  it("lands exactly on the floor it used to fall under", () => {
    for (const blurRadius of [8, 14, 20, 40]) {
      const { samplingPadding } = resolveSamplingGeometry({
        samplingPadding: undefined,
        mergeDistance: undefined,
        blurRadius,
      });
      expect(samplingPadding).toBe(requiredSamplingPadding(blurRadius));
      // And therefore raises nothing and warns about nothing, at any blur.
      expect(
        codes(resolved({ ...base, samplingPadding, mergeDistance: samplingPadding, blurRadius })),
      ).toEqual([]);
    }
  });

  it("leaves an authored padding alone, and its warning with it", () => {
    // An authored number is a statement about that app's geometry. Deriving over
    // the top of it would be the runtime overruling an author, which is a worse
    // defect than the one this fixes.
    expect(
      resolveSamplingGeometry({ samplingPadding: 24, mergeDistance: undefined, blurRadius: 14 }),
    ).toEqual({ samplingPadding: 24, mergeDistance: 24 });
    expect(codes(resolved({ ...base, samplingPadding: 24, mergeDistance: 24, blurRadius: 14 }))).toEqual([
      "sampling-padding-below-3-sigma",
      "merge-distance-below-effective-padding",
    ]);
  });

  it("keeps core's rule that mergeDistance defaults to the resolved padding", () => {
    // Not to `DEFAULT_GROUP_SAMPLING.mergeDistance`: core resolves `{ padding: 60 }`
    // alone to `{ 60, 60 }`, and the derived default has to inherit that rule
    // rather than invent a second one.
    expect(
      resolveSamplingGeometry({ samplingPadding: 60, mergeDistance: undefined, blurRadius: 14 }),
    ).toEqual({ samplingPadding: 60, mergeDistance: 60 });
    expect(
      resolveSamplingGeometry({ samplingPadding: undefined, mergeDistance: 100, blurRadius: 14 }),
    ).toEqual({ samplingPadding: 42, mergeDistance: 100 });
  });

  it("derives nothing to pad where the policy removed the blur entirely", () => {
    // forced-colors resolves `frost: "none"`, so there is no sampling region to
    // reserve and 3 × 0 is the honest answer rather than a floor to defend.
    expect(
      resolveSamplingGeometry({ samplingPadding: undefined, mergeDistance: undefined, blurRadius: 0 }),
    ).toEqual({ samplingPadding: 0, mergeDistance: 0 });
  });
});

/**
 * The ancestor clip chain, folded into the proxy (Decision Log #41(k)).
 *
 * A proxy sits in the plane layer, not inside whatever is cropping its members,
 * so nothing narrows it on the browser's behalf. Every number below therefore
 * comes from the *visible* extent rather than the border box — and the
 * `clipUnion` in particular, because `backdrop-proxy.ts`'s cross-group overlap
 * predicate rests on the sentence "a proxy paints only inside its own clip
 * union", which a union of unclipped boxes made false.
 */
describe("members their ancestors clip", () => {
  const clipped = (clip: readonly { x: number; y: number; width: number; height: number }[]) =>
    resolved({ ...base, members: [{ ...member(100, 100), clip }] });

  it("shrinks the painted region to what the clip lets through", () => {
    // 44 tall, the bottom 24 cropped away by a window ending at y = 120.
    const geometry = clipped([{ x: 0, y: 0, width: 1000, height: 120 }]);

    expect(geometry.clipUnion).toEqual({ x: 100, y: 100, width: 120, height: 20 });
    // And the sampled box follows it: padding is measured from the visible
    // region, not from a box the ancestor is hiding.
    expect(geometry.box).toEqual({ x: 76, y: 76, width: 168, height: 68 });
  });

  it("squares the corners the clip cut, and leaves the others alone", () => {
    const arcs = (geometry: ProxyGeometry): number =>
      (geometry.clipPath.match(/A /g) ?? []).length;

    // A rectangular crop of a rounded rect has a straight cut edge. Keeping the
    // radii would put a rounded corner in the middle of a scroller, which reads
    // as a rendering fault rather than as a crop.
    expect(arcs(resolved(base))).toBe(4);
    expect(arcs(clipped([{ x: 0, y: 0, width: 1000, height: 120 }]))).toBe(2); // bottom cut
    expect(arcs(clipped([{ x: 0, y: 110, width: 1000, height: 1000 }]))).toBe(2); // top cut
    expect(arcs(clipped([{ x: 110, y: 0, width: 1000, height: 1000 }]))).toBe(2); // left cut
    // Cut on two adjacent sides: only the far corner survives.
    expect(arcs(clipped([{ x: 110, y: 110, width: 1000, height: 1000 }]))).toBe(1);
  });

  it("drops a member its ancestors hide completely", () => {
    const geometry = resolveProxyGeometry({
      ...base,
      members: [{ ...member(100, 100), clip: [{ x: 0, y: 500, width: 100, height: 100 }] }],
    });

    // The same answer as an unmeasured member, and deliberately so: neither can
    // be painted, so "not there" is one state rather than two.
    expect(geometry).toBeUndefined();
  });

  it("keeps a group alive on the members that are still visible", () => {
    const geometry = resolved({
      ...base,
      members: [
        { ...member(100, 100), clip: [{ x: 0, y: 500, width: 100, height: 100 }] },
        member(400, 100),
      ],
    });

    expect(geometry.clipUnion).toEqual({ x: 400, y: 100, width: 120, height: 44 });
  });

  it("intersects every window in the chain", () => {
    const geometry = clipped([
      { x: 0, y: 0, width: 1000, height: 120 },
      { x: 140, y: 0, width: 1000, height: 1000 },
    ]);

    expect(geometry.clipUnion).toEqual({ x: 140, y: 100, width: 80, height: 20 });
  });

  it("changes nothing for a member with no clipping ancestor", () => {
    expect(resolved(base)).toEqual(resolved({ ...base, members: [{ ...member(100, 100) }] }));
  });
});

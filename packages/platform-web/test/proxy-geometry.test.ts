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
    // core's 24px advisory default is exactly 3σ at the regular variant's σ.
    expect(requiredSamplingPadding(MATERIAL_OPTICS.regular.blurRadius)).toBe(24);
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
  it("is byte-identical to the constant it replaces at the nominal blur", () => {
    // The whole neutrality argument. Not "close to" 24 — 24, so every committed
    // box, golden and pixel assertion stands unchanged.
    expect(resolveSamplingGeometry({ samplingPadding: undefined, mergeDistance: undefined, blurRadius: MATERIAL_OPTICS.regular.blurRadius })).toEqual({
      samplingPadding: DEFAULT_GROUP_SAMPLING.samplingPadding,
      mergeDistance: DEFAULT_GROUP_SAMPLING.mergeDistance,
    });
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

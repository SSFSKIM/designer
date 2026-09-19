/**
 * The native-delta instrument: the two ported rim readers, the pair reader, and
 * the rule that pairs a 27 cell with its 26.5 counterpart.
 *
 * The pairing is tested against `scenes.json` itself rather than against a list
 * written here. A silently mispaired cell would be the one failure this
 * instrument could not survive — every row would be a measurement of two
 * different scenes — and it is exactly the failure a hand-written expectation
 * cannot catch, because the hand that wrote it made the same assumption.
 */

import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

import {
  angularRead,
  contourRimRead,
  declaredBox,
  rasterOf,
  wrapDegrees,
  ANGULAR_BINS,
  COMPASS,
  RIM_SIDES,
} from "../cli/native-delta-readers";
import {
  activeTwinOf,
  cellGeometry,
  counterpartKey,
  pairMetrics,
  poseOf,
  readCapture,
  NATIVE_DELTA_METRICS,
} from "../cli/native-delta-metrics";
import { srgbByteToLinear } from "../src/color";
import { componentRegion, type DeclaredComponent } from "../src/component-region";
import { encodeByte, fromLinearLuminance, solidLuminance } from "./synthesise";

const REFERENCE = resolve(import.meta.dirname, "..", "..", "..", "apps", "reference-apple");

interface SceneSpec {
  readonly canvas: { readonly width: number; readonly height: number };
  readonly components: Readonly<Record<string, DeclaredComponent>>;
  readonly scenes: readonly { readonly id: string; readonly background: string; readonly component: string }[];
  readonly profiles: readonly { readonly key: string }[];
}

const spec = JSON.parse(readFileSync(resolve(REFERENCE, "scenes.json"), "utf8")) as SceneSpec;

describe("the pairing of a 27 cell with its 26.5 counterpart", () => {
  it("maps every declared 27 profile key onto a declared 26.5 one", () => {
    const declared = new Set(spec.profiles.map((profile) => profile.key));
    const keys27 = spec.profiles.map((profile) => profile.key).filter((key) => key.startsWith("apple-macos-27.0-"));
    expect(keys27).toHaveLength(6);
    for (const key of keys27) {
      const counterpart = counterpartKey(key);
      expect(counterpart.startsWith("apple-macos-26.5-")).toBe(true);
      expect(counterpart).not.toContain("glass");
      expect(declared.has(counterpart)).toBe(true);
    }
  });

  it("reads the pose off the scene's own state token, on every declared scene", () => {
    for (const scene of spec.scenes) {
      const state = scene.id.split("__")[2] ?? "";
      expect(poseOf(scene.id)).toBe(state.startsWith("inactive") ? "inactive" : "active");
    }
  });

  it("names a declared active scene for every receded scene that has one", () => {
    const declared = new Set(spec.scenes.map((scene) => scene.id));
    let paired = 0;
    for (const scene of spec.scenes) {
      const twin = activeTwinOf(scene.id);
      if (poseOf(scene.id) === "active") {
        expect(twin).toBeNull();
        continue;
      }
      expect(twin).not.toBeNull();
      // The twin must be the SAME backdrop and the SAME component, or the
      // recede would be a difference between two scenes rather than two poses.
      const parts = scene.id.split("__");
      expect(twin).toMatch(new RegExp(`^${parts[0] ?? ""}__${parts[1] ?? ""}__`));
      if (declared.has(twin as string)) paired += 1;
    }
    // Most receded scenes have an active twin in the declaration; the recede
    // read is only taken where one exists, and this pins that it is not a
    // handful of cells.
    expect(paired).toBeGreaterThan(40);
  });

  it("carries the tint and the press through to the active id", () => {
    expect(activeTwinOf("photo__capsule-button__inactive")).toBe("photo__capsule-button__rest");
    expect(activeTwinOf("photo__capsule-button__inactive-pressed")).toBe("photo__capsule-button__pressed");
    expect(activeTwinOf("photo__capsule-button__inactive-tint-orange")).toBe(
      "photo__capsule-button__rest-tint-orange",
    );
    expect(activeTwinOf("photo__capsule-button__inactive-tint-orange-half")).toBe(
      "photo__capsule-button__rest-tint-orange-half",
    );
  });
});

/**
 * A synthetic cell: a flat body inside a rounded box over a flat backdrop, with
 * an optional one-pixel rim of known amplitude painted **all the way around**
 * the contour with the profile `A·|cos(θ − φ)|`, θ being the outward normal's
 * compass angle.
 *
 * The rim is painted from the shape's own signed distance field rather than
 * side by side, which is what makes the corner arcs carry the profile too. That
 * matters: a rim painted on the straight spans alone would make each compass
 * bin's mean depend on how much unpainted arc that bin catches, and the reading
 * would be a fact about the synthetic instead of about the reader.
 */
function syntheticCell(options: {
  readonly canvas: { readonly width: number; readonly height: number };
  readonly box: readonly [number, number, number, number];
  readonly radius: number;
  readonly backdrop: number;
  readonly body: number;
  readonly rimAmplitude?: number;
  readonly rimAxisDeg?: number;
}) {
  const [x0, y0, x1, y1] = options.box;
  const r = options.radius;
  const amplitude = options.rimAmplitude ?? 0;
  const axis = ((options.rimAxisDeg ?? 0) * Math.PI) / 180;
  const cx = (x0 + x1) / 2;
  const cy = (y0 + y1) / 2;
  const hx = (x1 - x0) / 2;
  const hy = (y1 - y0) / 2;
  return fromLinearLuminance(options.canvas.width, options.canvas.height, (x, y) => {
    const px = x + 0.5 - cx;
    const py = y + 0.5 - cy;
    const qx = Math.abs(px) - (hx - r);
    const qy = Math.abs(py) - (hy - r);
    const distance =
      Math.hypot(Math.max(qx, 0), Math.max(qy, 0)) - r + Math.min(Math.max(qx, qy), 0);
    if (distance >= 0) return options.backdrop;
    if (amplitude === 0 || distance < -1) return options.body;
    const corner = qx > 0 && qy > 0;
    const norm = Math.max(Math.hypot(qx, qy), 1e-9);
    const nx = corner ? (Math.sign(px) * qx) / norm : qx > qy ? Math.sign(px) : 0;
    const ny = corner ? (Math.sign(py) * qy) / norm : qx > qy ? 0 : Math.sign(py);
    // No axis declared means a rim of uniform amplitude all the way round —
    // the isotropic case the contour reader's per-side recovery is stated on.
    const theta = Math.atan2(nx, -ny);
    const modulation = options.rimAxisDeg === undefined ? 1 : Math.abs(Math.cos(theta - axis));
    return options.body + amplitude * modulation;
  });
}

/** What an 8-bit capture of a linear-light value actually carries (X5). */
const quantised = (linear: number): number => srgbByteToLinear(encodeByte(linear));

describe("the W23 contour reader, ported", () => {
  const canvas = { width: 320, height: 200 };
  // A 160x96 rounded rectangle centred on the declared canvas, which is what
  // `rrect-md` is: the box the reader derives is x 80..240, y 52..148.
  const component: DeclaredComponent = { kind: "rrect", size: [160, 96], radius: 20 };
  const box = declaredBox(component, canvas, 1);

  it("places the declared box where the declaration puts it", () => {
    expect(box).not.toBeNull();
    expect(box).toMatchObject({ x0: 80, y0: 52, x1: 240, y1: 148, radiusPx: 20 });
  });

  it("reads a flat body as the body and a flat rim as nothing", () => {
    const image = syntheticCell({ canvas, box: [80, 52, 240, 148], radius: 20, backdrop: 0.1, body: 0.5 });
    const read = contourRimRead(rasterOf(image), box as NonNullable<typeof box>, 1);
    expect(read.body).toBeCloseTo(quantised(0.5), 12);
    for (const side of RIM_SIDES) {
      expect(read.sides[side].rim).toBeCloseTo(0, 12);
      expect(read.sides[side].row0).toBeCloseTo(0, 12);
    }
  });

  it("recovers a one-pixel line of known amplitude on every straight span", () => {
    const image = syntheticCell({
      canvas,
      box: [80, 52, 240, 148],
      radius: 20,
      backdrop: 0.1,
      body: 0.5,
      rimAmplitude: 0.05,
    });
    const read = contourRimRead(rasterOf(image), box as NonNullable<typeof box>, 1);
    // `rim` sums the excess over two CSS px and divides by the scale, so a
    // one-pixel line of amplitude a on a scale-1 raster reads exactly a — which
    // is the property that makes the 1x and 2x rows comparable at all. The
    // amplitude the raster can carry is the 8-bit one, not the declared one.
    // To four decimals, not exactly: the eroded body the excess is taken
    // against is six CSS px in from the declared box, and on a 20 px corner the
    // painted band reaches just inside that on the diagonal, which lifts the
    // body by about 1e-5. A real fixture's rim is not a step and W21 chose the
    // erosion against one; the synthetic is the harsher case.
    const expected = quantised(0.55) - quantised(0.5);
    for (const side of RIM_SIDES) {
      expect(read.sides[side].rim).toBeCloseTo(expected, 4);
      expect(read.sides[side].row0).toBeCloseTo(expected, 4);
    }
  });

  it("refuses the straight span of a capsule's short axis rather than reading across the arc", () => {
    const capsule: DeclaredComponent = { kind: "capsule", size: [120, 44] };
    const capsuleBox = declaredBox(capsule, canvas, 1);
    const image = syntheticCell({ canvas, box: [100, 78, 220, 122], radius: 22, backdrop: 0.1, body: 0.5 });
    const read = contourRimRead(rasterOf(image), capsuleBox as NonNullable<typeof capsuleBox>, 1);
    expect(Number.isNaN(read.sides.left.rim)).toBe(true);
    expect(Number.isNaN(read.sides.right.rim)).toBe(true);
    expect(Number.isFinite(read.sides.top.rim)).toBe(true);
  });
});

describe("the W24 angular reader, ported", () => {
  const canvas = { width: 320, height: 200 };
  const component: DeclaredComponent = { kind: "rrect", size: [160, 96], radius: 20 };
  const box = declaredBox(component, canvas, 1) as NonNullable<ReturnType<typeof declaredBox>>;

  it("bins the whole boundary and populates every compass direction", () => {
    const image = syntheticCell({ canvas, box: [80, 52, 240, 148], radius: 20, backdrop: 0.1, body: 0.5 });
    const read = angularRead(rasterOf(image), box, 1);
    expect(read.counts).toHaveLength(ANGULAR_BINS);
    expect(read.counts.every((count) => count > 0)).toBe(true);
    // Each straight side is wholly inside one compass bin, which is what the
    // centred binning exists for: N, E, S and W carry hundreds of samples each
    // while the sixteenths of the corner arcs carry tens.
    for (const k of [0, 4, 8, 12]) expect(read.counts[k] as number).toBeGreaterThan(100);
  });

  it("finds a rim painted on one axis only on that axis's sides", () => {
    // Painted about the N–S axis: the top and bottom straight spans carry the
    // full amplitude and the left and right carry |cos 90°| = 0.
    const image = syntheticCell({
      canvas,
      box: [80, 52, 240, 148],
      radius: 20,
      backdrop: 0.1,
      body: 0.5,
      rimAmplitude: 0.08,
      rimAxisDeg: 0,
    });
    const read = angularRead(rasterOf(image), box, 1);
    const expected = quantised(0.58) - quantised(0.5);
    expect(["N", "S"]).toContain(COMPASS[read.brightestBin]);
    expect(read.bins[0] as number).toBeCloseTo(expected, 3);
    expect(read.bins[8] as number).toBeCloseTo(expected, 3);
    // Not zero, and the residual is the instrument being right: the E and W
    // bins are 22.5° wide, so they catch the first degrees of the corner arcs
    // where |cos θ| has left zero. Two orders of magnitude under the sides is
    // the statement.
    expect(read.bins[4] as number).toBeLessThan(expected / 50);
    expect(read.bins[12] as number).toBeLessThan(expected / 50);
    expect(read.ratio).toBeGreaterThan(1);
  });

  it("reads a rim on the diagonal as equal on all four sides — the W24 finding", () => {
    const image = syntheticCell({
      canvas,
      box: [80, 52, 240, 148],
      radius: 20,
      backdrop: 0.1,
      body: 0.5,
      rimAmplitude: 0.08,
      rimAxisDeg: 45,
    });
    const read = angularRead(rasterOf(image), box, 1);
    // |cos(θ − 45°)| is the same on all four straight sides, so a per-side
    // reader sees no variation at all here while the light is plainly on the
    // diagonal. That is the blindness W24 was chartered on, restated as a
    // property of this instrument's own input.
    const sideBins = [0, 4, 8, 12].map((k) => read.bins[k] as number);
    expect(Math.max(...sideBins) / Math.min(...sideBins)).toBeLessThan(1.05);
  });
});

describe("wrapDegrees", () => {
  it("wraps to (-180, 180]", () => {
    expect(wrapDegrees(0)).toBe(0);
    expect(wrapDegrees(350)).toBe(-10);
    expect(wrapDegrees(-350)).toBe(10);
    expect(wrapDegrees(180)).toBe(180);
    expect(wrapDegrees(-180)).toBe(180);
  });
});

describe("the pair reader", () => {
  const canvas = { width: 320, height: 200 };
  const component: DeclaredComponent = { kind: "rrect", size: [160, 96], radius: 20 };
  const region = componentRegion(component, { canvas, scale: 1, width: 320, height: 200 });
  const geometry = cellGeometry(region, component, canvas, 1);
  const background = solidLuminance(320, 200, 0.1);

  it("reports every measurable distance as exactly zero for a capture against itself", () => {
    const image = syntheticCell({
      canvas,
      box: [80, 52, 240, 148],
      radius: 20,
      backdrop: 0.1,
      body: 0.5,
      rimAmplitude: 0.05,
    });
    const reading = readCapture(image, background, geometry);
    const result = pairMetrics(reading, reading, background, geometry);
    for (const metric of NATIVE_DELTA_METRICS) {
      const value = result.metrics[metric];
      if (value === null) continue;
      expect(`${metric}=${String(value)}`).toBe(`${metric}=0`);
    }
  });

  it("moves the interior level, the body and nothing else when only the body changes", () => {
    const base = syntheticCell({ canvas, box: [80, 52, 240, 148], radius: 20, backdrop: 0.1, body: 0.5 });
    const lifted = syntheticCell({ canvas, box: [80, 52, 240, 148], radius: 20, backdrop: 0.1, body: 0.55 });
    const result = pairMetrics(
      readCapture(base, background, geometry),
      readCapture(lifted, background, geometry),
      background,
      geometry,
    );
    expect(result.metrics.interiorMeanDelta).toBeGreaterThan(0.04);
    expect(result.metrics.bodyLevelDelta).toBeGreaterThan(0.04);
    // The shape did not change, so the silhouette rows must not have.
    expect(result.metrics.silhouetteIoUComplement).toBe(0);
    expect(result.metrics.contourDistanceMeanPx).toBe(0);
  });

  it("is absent rather than zero where a composite has no declared box", () => {
    const stack: DeclaredComponent = {
      kind: "stack",
      base: { kind: "rrect", size: [220, 130], radius: 24 },
      over: { kind: "rrect", size: [120, 56], radius: 16 },
    };
    const stackRegion = componentRegion(stack, { canvas, scale: 1, width: 320, height: 200 });
    const stackGeometry = cellGeometry(stackRegion, stack, canvas, 1);
    const image = syntheticCell({ canvas, box: [80, 52, 240, 148], radius: 20, backdrop: 0.1, body: 0.5 });
    const reading = readCapture(image, background, stackGeometry);
    const result = pairMetrics(reading, reading, background, stackGeometry);
    expect(result.metrics.rimContourDeltaMax).toBeNull();
    expect(result.metrics.highlightBinDeltaMax).toBeNull();
    expect(result.notes.join(" ")).toContain("no single declared box");
  });
});

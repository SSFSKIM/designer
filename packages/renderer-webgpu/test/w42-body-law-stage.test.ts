/**
 * W42 G2 step 3, U3 — the stage's SCHEDULE held to the measured storage graph and to the exact
 * Gaussian (`implementation-design.md` §2.3–§2.6 as revised in §11–§12).
 *
 * `body-law-pass.ts` runs what `bodyLawSchedule` says: which widths are stored, at which
 * decimation, on which grid with how much padding, and where the composite reads them back. The
 * WGSL is only a transcription of that, and it runs on a real adapter in U7. What can be settled
 * here is the schedule itself, and one claim in particular: that the widths of one q may share a
 * grid padded by the largest padding any of them needs. `u2_mirror.py` measured the realisation
 * with each width padded by its own amount, so this file emulates the runtime's passes in f64 —
 * the capture, the floor, the direct and decimated separable pairs, the weight channel of the
 * normalised mode, the composite's return coordinate and its interpolation — and compares with the
 * mirror's graph (to 1e-6 code) and with the exact per-pixel Gaussian, band-weighted, on
 * `fixtures/stage.json` (`implementation-design/u3_fixtures.py`).
 *
 * Since the perf wave (§17) the stage computes each width only where it is read
 * (`bodyLawRegions`). The last block here runs the same passes over those regions alone, with every
 * other texel a NaN, and holds each value the composite reads to the whole-footprint value.
 */

import { readFileSync } from "node:fs";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import {
  bodyLawComposite,
  bodyLawInterpolateLevels,
  bodyLawNarrowSigmaDevicePx,
  bodyLawSurfacePlan,
} from "../src/body-law";
import {
  bodyLawDecimatedSigma,
  bodyLawDecimationPad,
  bodyLawGaussianWeights,
  bodyLawPackShelves,
  bodyLawRegions,
  bodyLawSchedule,
  bodyLawSourceExtent,
  type BodyLawRect,
} from "../src/body-law-pass";
import { DEFAULT_MATERIAL_PROFILE, type MaterialProfile } from "../src/material";

const FIXTURES = join(
  __dirname,
  "../../calibration/results/2026-09-30-w42-g2-identification/implementation-design/fixtures/",
);

interface StageCell {
  readonly comp: string;
  readonly scale: number;
  readonly scheme: "light" | "dark";
  readonly pose: "active" | "receded";
  readonly unit: number;
  readonly k: number;
  readonly lam: number;
  readonly hinge: number;
  readonly canvas: readonly [number, number];
  readonly centre: readonly [number, number];
  readonly size: readonly [number, number];
  readonly window: { x0: number; y0: number; x1: number; y1: number };
  readonly levels: readonly number[];
  readonly interpolation: "single" | "linear" | "cubic";
  readonly wide: number;
  readonly mode: "clamp" | "norm";
  readonly samples: {
    readonly y: readonly number[];
    readonly x: readonly number[];
    readonly depth: readonly number[];
    readonly sigma: readonly number[];
    readonly mirrorC: readonly (readonly number[])[];
    readonly mirrorW: readonly (readonly number[])[];
    readonly exactC: readonly (readonly number[])[];
    readonly exactW: readonly (readonly number[])[];
    readonly argument: readonly (readonly number[])[];
    readonly wideLuma: readonly number[];
  };
}

const doc = JSON.parse(readFileSync(join(FIXTURES, "stage.json"), "utf8")) as {
  readonly normal: number;
  readonly cells: readonly StageCell[];
};

/** The fixture's integer backdrop (`u3_fixtures.py` `backdrop`), codes. */
function backdropCode(x: number, y: number, c: number): number {
  const checker = ((x >> 3) + (y >> 3)) & 1;
  const v = (x * 37 + y * 101 + c * 59 + ((x * y) % 29) * 13) % 41;
  return Math.min(255, Math.max(0, (checker === 1 ? 200 : 40) + v - 20 + c * 7));
}

interface Tile {
  readonly w: number;
  readonly h: number;
  readonly data: Float64Array;
}

const at = (tile: Tile, x: number, y: number, c: number): number =>
  tile.data[(y * tile.w + x) * 4 + c]!;

/**
 * `cs_blur` on one job: taps clamped to the tile, or zero outside it, written over `rect` (the
 * whole tile unless given) into `into` (zeros unless given).
 */
function blur(tile: Tile, axis: 0 | 1, weights: Float64Array, zero: boolean,
  rect: BodyLawRect = { x0: 0, y0: 0, x1: tile.w, y1: tile.h },
  into: Tile = { w: tile.w, h: tile.h, data: new Float64Array(tile.data.length) }): Tile {
  const r = (weights.length - 1) / 2;
  const out = into.data;
  for (let y = rect.y0; y < rect.y1; y++) {
    for (let x = rect.x0; x < rect.x1; x++) {
      const dst = (y * tile.w + x) * 4;
      for (let c = 0; c < 4; c++) out[dst + c] = 0;
      for (let k = -r; k <= r; k++) {
        let tx = axis === 0 ? x + k : x;
        let ty = axis === 1 ? y + k : y;
        if (zero && (tx < 0 || ty < 0 || tx >= tile.w || ty >= tile.h)) continue;
        tx = Math.min(tile.w - 1, Math.max(0, tx));
        ty = Math.min(tile.h - 1, Math.max(0, ty));
        const w = weights[k + r]!;
        const src = (ty * tile.w + tx) * 4;
        for (let c = 0; c < 4; c++) out[dst + c]! += w * tile.data[src + c]!;
      }
    }
  }
  return into;
}

/** `cs_decimate`: the q × q block means of the tile padded by `pad`, edge or zero. */
function decimate(tile: Tile, q: number, pad: number, zero: boolean, w: number, h: number): Tile {
  const out = new Float64Array(w * h * 4);
  for (let gy = 0; gy < h; gy++) {
    for (let gx = 0; gx < w; gx++) {
      for (let sy = 0; sy < q; sy++) {
        for (let sx = 0; sx < q; sx++) {
          let tx = gx * q + sx - pad;
          let ty = gy * q + sy - pad;
          if (zero && (tx < 0 || ty < 0 || tx >= tile.w || ty >= tile.h)) continue;
          tx = Math.min(tile.w - 1, Math.max(0, tx));
          ty = Math.min(tile.h - 1, Math.max(0, ty));
          for (let c = 0; c < 4; c++) out[(gy * w + gx) * 4 + c]! += at(tile, tx, ty, c) / (q * q);
        }
      }
    }
  }
  return { w, h, data: out };
}

/** `tile_value`: the pixel's own texel at q = 1, else the decimated grid's return coordinate. */
function tileValue(tile: Tile, q: number, pad: number, i: number, j: number): number[] {
  const load = (x: number, y: number, c: number) =>
    at(tile, Math.min(tile.w - 1, Math.max(0, x)), Math.min(tile.h - 1, Math.max(0, y)), c);
  let v: number[];
  if (q < 1.5) v = [0, 1, 2, 3].map((c) => load(i, j, c));
  else {
    const ax = (pad + i + 0.5) / q - 0.5;
    const ay = (pad + j + 0.5) / q - 0.5;
    const bx = Math.floor(ax), by = Math.floor(ay);
    const fx = ax - bx, fy = ay - by;
    v = [0, 1, 2, 3].map((c) => {
      const top = load(bx, by, c) * (1 - fx) + load(bx + 1, by, c) * fx;
      const bottom = load(bx, by + 1, c) * (1 - fx) + load(bx + 1, by + 1, c) * fx;
      return top * (1 - fy) + bottom * fy;
    });
  }
  const weight = Math.max(v[3]!, 1e-9);
  return [v[0]! / weight, v[1]! / weight, v[2]! / weight];
}

const materialOf = (cell: StageCell): MaterialProfile => ({
  ...DEFAULT_MATERIAL_PROFILE,
  bodyLawStrength: 1,
  bodyLawK: [cell.k, cell.k],
  bodyLawLambda: cell.lam,
  bodyLawHinge: cell.hinge,
  bodyLawNormal: doc.normal,
  bodyLawPose: cell.pose === "receded" ? 1 : 0,
  bodyLawWidthUnit: cell.unit,
  bodyLawEncodedAveraging: 1,
});

/** The runtime's passes for one cell, in f64, read at the fixture's samples. */
function emulate(cell: StageCell) {
  const material = materialOf(cell);
  const [W, H] = cell.canvas;
  const extent = bodyLawSourceExtent([W, H], [1, 1, 0, 0]);
  const plan = bodyLawSurfacePlan({ centre: cell.centre, size: cell.size }, cell.scale, material, extent);
  const schedule = bodyLawSchedule(plan);
  const fw = plan.footprint.x1 - plan.footprint.x0;
  const fh = plan.footprint.y1 - plan.footprint.y0;
  const capture: Tile = { w: fw, h: fh, data: new Float64Array(fw * fh * 4) };
  for (let j = 0; j < fh; j++) {
    for (let i = 0; i < fw; i++) {
      for (let c = 0; c < 3; c++) {
        capture.data[(j * fw + i) * 4 + c] =
          backdropCode(plan.footprint.x0 + i, plan.footprint.y0 + j, c) / 255;
      }
      capture.data[(j * fw + i) * 4 + 3] = 1;
    }
  }
  const floorWeights = bodyLawGaussianWeights(plan.floorSigmaDevicePx);
  const floored = blur(blur(capture, 0, floorWeights, false), 1, floorWeights, false);
  const zero = plan.edge === "normalised";
  const tiles = new Map<number | "wide", { tile: Tile; q: number; pad: number }>();
  for (const width of schedule.widths) {
    if (width.q === 0) tiles.set(width.role, { tile: floored, q: 1, pad: 0 });
  }
  const inputs = new Map<number, Tile>();
  for (const grid of schedule.grids) {
    const input = grid.q === 1 ? floored : decimate(floored, grid.q, grid.pad, zero, grid.width, grid.height);
    inputs.set(grid.q, input);
    for (const width of grid.members) {
      const sigma = grid.q === 1 ? width.sigma : bodyLawDecimatedSigma(width.sigma, grid.q);
      const weights = bodyLawGaussianWeights(sigma);
      const gridZero = grid.q === 1 && zero;
      tiles.set(width.role, {
        tile: blur(blur(input, 0, weights, gridZero), 1, weights, gridZero), q: grid.q, pad: grid.pad,
      });
    }
  }
  const s = cell.samples;
  const C: number[][] = [];
  const Wv: number[][] = [];
  s.y.forEach((y, n) => {
    const i = s.x[n]! + cell.window.x0 - plan.footprint.x0;
    const j = y + cell.window.y0 - plan.footprint.y0;
    const values = plan.narrowSigmaDevicePx.map((_, k) => {
      const entry = tiles.get(k)!;
      return tileValue(entry.tile, entry.q, entry.pad, i, j);
    });
    // The fixture's depth is positive inside; the plan's d is negative inside.
    const sigma = bodyLawNarrowSigmaDevicePx(-s.depth[n]!, plan, material);
    C.push([0, 1, 2].map((c) =>
      bodyLawInterpolateLevels(sigma, plan.narrowSigmaDevicePx, values.map((v) => v[c]!),
        plan.interpolation)));
    const wide = tiles.get("wide")!;
    Wv.push(tileValue(wide.tile, wide.q, wide.pad, i, j));
  });
  return { plan, schedule, material, C, W: Wv, tiles, inputs, floored };
}

const smoothstep = (a: number, b: number, x: number): number => {
  const t = Math.min(1, Math.max(0, (x - a) / (b - a)));
  return t * t * (3 - 2 * t);
};

describe("W42 U3: the stage's kernel, padding and grid arithmetic", () => {
  it("builds ndimage's truncated, normalised Gaussian", () => {
    const w = bodyLawGaussianWeights(1);
    expect(w).toHaveLength(9);
    const raw = [-4, -3, -2, -1, 0, 1, 2, 3, 4].map((x) => Math.exp(-0.5 * x * x));
    const sum = raw.reduce((a, b) => a + b, 0);
    raw.forEach((v, i) => expect(w[i]).toBeCloseTo(v / sum, 15));
    // int(4 σ + 0.5): σ 1.6 has radius 6, σ 0.8 radius 3.
    expect(bodyLawGaussianWeights(1.6)).toHaveLength(13);
    expect(bodyLawGaussianWeights(0.8)).toHaveLength(7);
  });

  it("pads and narrows a decimated width as forward.py's _blur_decimated does", () => {
    expect(bodyLawDecimationPad(15.864, 2)).toBe(Math.ceil((4 * 15.864) / 2 + 2) * 2);
    expect(bodyLawDecimationPad(67, 4) % 4).toBe(0);
    expect(bodyLawDecimatedSigma(16, 2)).toBeCloseTo(Math.sqrt(256 - 3 / 12 - 4 / 6) / 2, 12);
  });

  it("takes R_fp's clip from the fit's image of the source", () => {
    expect(bodyLawSourceExtent([320, 200], [1, 1, 0, 0])).toEqual({ x0: 0, y0: 0, x1: 320, y1: 200 });
    // A cover fit that crops half the source's width: uv = 0.5 p/W + 0.25, so the source spans
    // [−W/2, 3W/2) of the plane.
    expect(bodyLawSourceExtent([320, 200], [0.5, 1, 0.25, 0])).toEqual(
      { x0: -160, y0: 0, x1: 480, y1: 200 });
  });
});

describe.each(doc.cells.map((cell) => [`${cell.comp} ${cell.scale}x ${cell.scheme} ${cell.pose} unit ${cell.unit}`, cell] as const))(
  "W42 U3 stage, %s",
  (_name, cell) => {
    const run = emulate(cell);

    it("plans the fixture's footprint, levels and wide width", () => {
      expect(run.plan.footprint).toEqual(cell.window);
      expect(run.plan.interpolation).toBe(cell.interpolation);
      expect(run.plan.edge).toBe(cell.mode === "norm" ? "normalised" : "clamp");
      expect(run.plan.narrowSigmaDevicePx).toHaveLength(cell.levels.length);
      run.plan.narrowSigmaDevicePx.forEach((v, k) => expect(v).toBeCloseTo(cell.levels[k]!, 12));
      expect(run.plan.wideSigmaDevicePx).toBeCloseTo(cell.wide, 12);
      cell.samples.depth.forEach((depth, n) => expect(
        bodyLawNarrowSigmaDevicePx(-depth, run.plan, run.material),
      ).toBeCloseTo(cell.samples.sigma[n]!, 10));
    });

    it("schedules every width once, one grid per decimation factor", () => {
      const { schedule } = run;
      const scheduled = schedule.grids.flatMap((grid) => grid.members);
      const stored = schedule.widths.filter((width) => width.q !== 0);
      expect(scheduled).toHaveLength(stored.length);
      expect(new Set(schedule.grids.map((grid) => grid.q)).size).toBe(schedule.grids.length);
      for (const grid of schedule.grids) {
        expect(grid.members.every((width) => width.q === grid.q)).toBe(true);
        if (grid.q > 1) {
          // The shared padding is the widest member's, a multiple of q, and covers every member.
          expect(grid.pad % grid.q).toBe(0);
          for (const width of grid.members) {
            expect(grid.pad).toBeGreaterThanOrEqual(bodyLawDecimationPad(width.sigma, grid.q));
          }
        }
      }
    });

    it("is the mirror's storage graph in exact arithmetic (shared padding included)", () => {
      let worst = 0;
      cell.samples.y.forEach((_, n) => {
        for (let c = 0; c < 3; c++) {
          worst = Math.max(worst, Math.abs(run.C[n]![c]! - cell.samples.mirrorC[n]![c]!) * 255,
            Math.abs(run.W[n]![c]! - cell.samples.mirrorW[n]![c]!) * 255);
        }
      });
      expect(worst).toBeLessThan(1e-6);
    });

    it("is within the realisation's budget of the exact Gaussian, band-weighted", () => {
      // The budget of §11.1 (0.15 code) is on the OUTPUT; C and W here are the argument's terms.
      // Measured on this fixture: 0.022 code at worst band-weighted (rrect-80 at 2x, C), 0.0015 for
      // W. Unweighted, rrect-80's cubic across the gap between its top interior level (2.8 device
      // px) and the contour level (10.5) misses by 5.0 codes inside the last point of depth, where
      // the band weight is below 0.008: real, and outside what reaches the render.
      let worst = 0;
      cell.samples.y.forEach((_, n) => {
        const depth = cell.samples.depth[n]!;
        const band = cell.pose === "receded" ? 1 : smoothstep(0, 20, depth);
        for (let c = 0; c < 3; c++) {
          worst = Math.max(worst,
            band * Math.abs(run.C[n]![c]! - cell.samples.exactC[n]![c]!) * 255,
            band * Math.abs(run.W[n]![c]! - cell.samples.exactW[n]![c]!) * 255);
        }
      });
      expect(worst).toBeLessThan(0.05);
    });

    it("composes the argument the mirror composes", () => {
      const material = run.material;
      cell.samples.y.forEach((_, n) => {
        const out = bodyLawComposite(run.C[n] as never, run.W[n] as never, material);
        for (let c = 0; c < 3; c++) {
          expect(Math.abs(out.argument[c]! - cell.samples.argument[n]![c]!) * 255).toBeLessThan(1e-6);
        }
        expect(Math.abs(out.wideLuma - cell.samples.wideLuma[n]!) * 255).toBeLessThan(1e-6);
      });
    });
  },
);

/**
 * The stage computes a width only where it is read (`bodyLawRegions`, §17). Run every pass over
 * its region alone, with NaN in every texel it does not write, and read each width back at every
 * pixel of the composite as the composite reads it: each value is the whole-footprint pass's value
 * to the bit, and none is a NaN. That is the claim the regions make — every tap of the vertical
 * pass lands in what the horizontal pass wrote, and every read of the composite in what the
 * vertical pass wrote — checked rather than argued.
 */
describe.each(doc.cells.map((cell) => [`${cell.comp} ${cell.scale}x ${cell.scheme} ${cell.pose} unit ${cell.unit}`, cell] as const))(
  "W42 perf wave: the stage's regions, %s",
  (_name, cell) => {
    const run = emulate(cell);
    const { plan, schedule, tiles, inputs } = run;
    const fw = plan.footprint.x1 - plan.footprint.x0;
    const fh = plan.footprint.y1 - plan.footprint.y0;
    const nan = (tile: Tile): Tile => ({ w: tile.w, h: tile.h, data: new Float64Array(tile.data.length).fill(NaN) });
    const box = {
      x0: plan.box.x0 - plan.footprint.x0, y0: plan.box.y0 - plan.footprint.y0,
      x1: plan.box.x1 - plan.footprint.x0, y1: plan.box.y1 - plan.footprint.y0,
    };
    const clip = (r: BodyLawRect): BodyLawRect => ({
      x0: Math.max(0, r.x0), y0: Math.max(0, r.y0), x1: Math.min(fw, r.x1), y1: Math.min(fh, r.y1),
    });
    it.each([
      ["the whole footprint", { x0: 0, y0: 0, x1: fw, y1: fh }],
      // A's rect cutting the footprint unevenly, as a group rect a few points past the box does.
      ["a rect cutting the footprint", clip({ x0: box.x0 - 5, y0: box.y0 - 2, x1: box.x1 + 7, y1: box.y1 + 4 })],
      ["a corner of it", clip({ x0: 0, y0: 0, x1: box.x0 + 9, y1: box.y0 + 6 })],
    ] as const)("reads every width back exactly over %s", (_label, composite) => {
      for (const region of bodyLawRegions(schedule, composite)) {
        const input = inputs.get(region.grid.q)!;
        const weights = bodyLawGaussianWeights(region.sigma);
        expect(weights.length).toBe(2 * region.radius + 1);
        const h = blur(input, 0, weights, region.zero, region.horizontal, nan(input));
        const v = blur(h, 1, weights, region.zero, region.written, nan(input));
        const whole = tiles.get(region.width.role)!;
        for (let j = composite.y0; j < composite.y1; j++) {
          for (let i = composite.x0; i < composite.x1; i++) {
            const bounded = tileValue(v, whole.q, whole.pad, i, j);
            const full = tileValue(whole.tile, whole.q, whole.pad, i, j);
            for (let c = 0; c < 3; c++) {
              if (!Object.is(bounded[c], full[c])) {
                expect.fail(`${String(region.width.role)} at (${i}, ${j}): ${bounded[c]} against ${full[c]}`);
              }
            }
          }
        }
      }
    });
  },
);

describe("W42 perf wave: the atlas packing", () => {
  it("places every tile inside the atlas, none overlapping, and declines what cannot fit", () => {
    const sizes: [number, number][] = [[300, 40], [120, 90], [500, 12], [64, 64], [80, 90], [1, 1]];
    const packed = bodyLawPackShelves(sizes, 600)!;
    expect(packed.width).toBeLessThanOrEqual(600);
    const rects = sizes.map(([w, h], i) => {
      const [x, y] = packed.places[i]!;
      expect(x + w).toBeLessThanOrEqual(packed.width);
      expect(y + h).toBeLessThanOrEqual(packed.height);
      return { x, y, w, h };
    });
    for (let a = 0; a < rects.length; a++) {
      for (let b = a + 1; b < rects.length; b++) {
        const p = rects[a]!, q = rects[b]!;
        const apart = p.x + p.w <= q.x || q.x + q.w <= p.x || p.y + p.h <= q.y || q.y + q.h <= p.y;
        expect(apart, `${a} and ${b}`).toBe(true);
      }
    }
    expect(bodyLawPackShelves([[601, 1]], 600)).toBeUndefined();
    expect(bodyLawPackShelves([[400, 400], [400, 400]], 600)).toBeUndefined();
    expect(bodyLawPackShelves([], 600)).toEqual({ places: [], width: 1, height: 1 });
  });
});

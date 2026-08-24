/**
 * Error measurement in the optical band.
 *
 * Two quantities matter, because the optics read two different things:
 *   - field VALUE error, in px  -> where the rim sits, how wide it reads
 *   - field GRADIENT DIRECTION error, in degrees -> which way refraction bends
 *
 * Both are measured inside |d| <= halfBand of the true contour, with sub-bands
 * reported separately because rim lighting reads a much thinner band than
 * refraction does.
 *
 * Ground truth comes from the normal-offset construction (see truth.ts), so the
 * reference distance and reference gradient are exact, not solver estimates.
 *
 * The reported max is then locally refined by pattern search over (contour
 * parameter, offset), so "max" means the true worst case of the continuous
 * field, not just the worst grid sample.
 */

import {
  buildContour,
  segCurvature,
  segNormal,
  segPoint,
  type Contour,
  type ShapeSpec,
} from './contour.js';
import { angleDeg, inwardReach, sampleBand, type BandOptions, DEFAULT_BAND } from './truth.js';
import { fieldGradient, type Candidate, type Prepared } from './candidates.js';

export interface BandStats {
  /** band half-width this row covers */
  half: number;
  n: number;
  valueMax: number;
  valueP95: number;
  valueRms: number;
  gradMaxDeg: number;
  gradP95Deg: number;
  /** fraction of samples sitting on a C1 kink of the candidate field */
  kinkFraction: number;
  /** max |grad| deviation from 1 (eikonal defect) */
  eikonalMax: number;
  /** where the worst value error was found */
  worstAt: { x: number; y: number; d: number };
}

export interface ConfigResult {
  spec: ShapeSpec;
  sEff: number;
  r: number;
  reach: number;
  bands: BandStats[];
}

const SUB_BANDS = [1, 4, 8];

function percentile(sorted: number[], q: number): number {
  if (sorted.length === 0) return 0;
  const i = Math.min(sorted.length - 1, Math.max(0, Math.ceil(q * sorted.length) - 1));
  return sorted[i];
}

export interface MeasureOptions {
  band?: BandOptions;
  /** finite-difference step for the candidate gradient, as a fraction of r */
  gradStepFrac?: number;
  /** how many worst samples to locally refine */
  refineTop?: number;
}

export function measure(
  cand: Candidate,
  spec: ShapeSpec,
  coeff: number[],
  opts: MeasureOptions = {}
): ConfigResult {
  const band = opts.band ?? DEFAULT_BAND;
  const contour = buildContour(spec);
  const prep = cand.prepare(spec, coeff);
  const r = contour.params.r;
  const h = Math.max(1e-6, (opts.gradStepFrac ?? 1e-3) * Math.max(r, 1));

  const samples = sampleBand(contour, band);

  interface Rec {
    absd: number;
    ve: number;
    ge: number;
    kink: boolean;
    eik: number;
    x: number;
    y: number;
    d: number;
  }
  const recs: Rec[] = [];

  for (const s of samples) {
    const fv = cand.evalAt(prep, s.P.x, s.P.y);
    const g = fieldGradient(cand, prep, s.P.x, s.P.y, h);
    const ve = Math.abs(fv - s.d);
    const ge = g.mag > 0 ? angleDeg({ x: g.gx, y: g.gy }, s.grad) : 90;
    recs.push({
      absd: Math.abs(s.d),
      ve,
      ge,
      kink: g.kink,
      eik: Math.abs(g.mag - 1),
      x: s.P.x,
      y: s.P.y,
      d: s.d,
    });
  }

  const bands: BandStats[] = [];
  for (const half of SUB_BANDS) {
    if (half > band.halfBand) continue;
    const inBand = recs.filter((rr) => rr.absd <= half + 1e-12);
    const vals = inBand.map((rr) => rr.ve).sort((a, b) => a - b);
    const nonKink = inBand.filter((rr) => !rr.kink);
    const grads = nonKink.map((rr) => rr.ge).sort((a, b) => a - b);
    let worst = inBand[0];
    for (const rr of inBand) if (rr.ve > (worst?.ve ?? -1)) worst = rr;

    // local refinement of the max value error
    const refined = refineMaxValueError(cand, prep, contour, half, opts.refineTop ?? 24);

    const valueMax = Math.max(vals.length ? vals[vals.length - 1] : 0, refined.value);
    const gradMax = grads.length ? grads[grads.length - 1] : 0;

    bands.push({
      half,
      n: inBand.length,
      valueMax,
      valueP95: percentile(vals, 0.95),
      valueRms: Math.sqrt(inBand.reduce((a, rr) => a + rr.ve * rr.ve, 0) / Math.max(1, inBand.length)),
      gradMaxDeg: gradMax,
      gradP95Deg: percentile(grads, 0.95),
      kinkFraction: inBand.length ? (inBand.length - nonKink.length) / inBand.length : 0,
      eikonalMax: nonKink.reduce((a, rr) => Math.max(a, rr.eik), 0),
      worstAt: refined.value > (worst?.ve ?? 0)
        ? refined.at
        : { x: worst?.x ?? 0, y: worst?.y ?? 0, d: worst?.d ?? 0 },
    });
  }

  return { spec, sEff: contour.params.smoothingEff, r, reach: contour.params.p, bands };
}

/**
 * Pattern search in (segment, t, offset) space from the worst grid samples, so
 * the reported max is the field's real worst case rather than a sampling artifact.
 */
function refineMaxValueError(
  cand: Candidate,
  prep: Prepared,
  contour: Contour,
  half: number,
  topN: number
): { value: number; at: { x: number; y: number; d: number } } {
  const segs = contour.segments;
  type Seed = { i: number; t: number; delta: number; err: number };
  const seeds: Seed[] = [];

  /** inward offsets past the medial axis break the "distance == offset"
   * identity, so they are excluded from the search domain, exactly as the band
   * sampler excludes them. */
  const inLimit = (i: number, t: number) => {
    const s = segs[i];
    const b = segPoint(s, t);
    return Math.min(half, 0.98 * inwardReach(contour, b, segCurvature(s, t)));
  };

  const evalAt = (i: number, t: number, delta: number) => {
    const s = segs[i];
    const b = segPoint(s, t);
    const n = segNormal(s, t);
    const x = b.x + n.x * delta;
    const y = b.y + n.y * delta;
    const fv = cand.evalAt(prep, x, y);
    return { err: Math.abs(fv - delta), x, y };
  };

  for (let i = 0; i < segs.length; i++) {
    const s = segs[i];
    if (s.kind === 'line') continue; // straight edges are exact for every family
    const n = 96;
    for (let k = 0; k <= n; k++) {
      const t = k / n;
      const lim = inLimit(i, t);
      for (const d of [-lim, -lim * 0.5, 0, half * 0.5, half]) {
        seeds.push({ i, t, delta: d, err: evalAt(i, t, d).err });
      }
    }
  }
  seeds.sort((a, b) => b.err - a.err);

  let best = { value: 0, at: { x: 0, y: 0, d: 0 } };
  for (const s of seeds.slice(0, topN)) {
    let t = s.t;
    let delta = s.delta;
    let cur = evalAt(s.i, t, delta);
    let stepT = 1 / 96;
    let stepD = half / 4;
    for (let it = 0; it < 300; it++) {
      let improved = false;
      for (const dt of [stepT, -stepT]) {
        const nt = Math.min(1, Math.max(0, t + dt));
        const c = evalAt(s.i, nt, Math.max(-inLimit(s.i, nt), delta));
        if (c.err > cur.err) {
          t = nt;
          delta = Math.max(-inLimit(s.i, nt), delta);
          cur = c;
          improved = true;
        }
      }
      for (const dd of [stepD, -stepD]) {
        const nd = Math.min(half, Math.max(-inLimit(s.i, t), delta + dd));
        const c = evalAt(s.i, t, nd);
        if (c.err > cur.err) {
          delta = nd;
          cur = c;
          improved = true;
        }
      }
      if (!improved) {
        stepT *= 0.5;
        stepD *= 0.5;
        if (stepT < 1e-10 && stepD < 1e-10) break;
      }
    }
    if (cur.err > best.value) {
      best = { value: cur.err, at: { x: cur.x, y: cur.y, d: delta } };
    }
  }
  return best;
}

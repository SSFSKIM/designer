/**
 * W31 G2 — the standing readback guard: an ENCLOSED region of zero alpha
 * (claims §5.163 §3, §8 finding N1; the tracker's WGSL range class, fix shape
 * 3).
 *
 * ## What it is for
 *
 * A NaN that reaches a colour target does not announce itself. Written to an
 * `rgba8unorm` attachment it becomes zero, and zero alpha inside a surface is a
 * hole where the material should be — which is exactly what §5.159 §6 measured
 * as an undrawn strip and spent a whole child diagnosing. The renderer's
 * readback already refuses a raster when WebGPU reported a validation error,
 * because a blank target with no message is worse than a failure. This is the
 * same idea for the same reason, one class along: the signature is in the bytes
 * the harness already has in hand, and finding it costs one pass over them.
 *
 * ## What it adds over a sweep
 *
 * `e2e/gpu/w30-thin-sigma-coverage.spec.ts` and `w31-range-sweeps.spec.ts` are
 * the shape that CAUGHT the W30 strip: name a material axis and a scene axis,
 * sweep both, assert an invariant that does not depend on either. A sweep is the
 * stronger instrument and it is also the narrower one — it only ever sees the
 * scenes and the leaves somebody thought to name, and §5.159b's own defect had
 * been reachable for six waves because nobody had thought to name a thin σ. This
 * guard sees every scene any spec renders, including the ones nobody wrote a
 * sweep for, at the cost of one pass over bytes that are already decoded. **The
 * sweep is the exposure; the guard is the standing watch.**
 *
 * It is a TEST-TIME watch and not a runtime property (review closure
 * 2026-09-21; claims §5.163 §8, finding N7): it is wired into
 * `e2e/fixtures/harness.ts`'s `renderScene` and `renderAtGovernorLevel`, which
 * are the in-page harness's own entry points. Nothing under `src/` runs it, so
 * "every scene" means every scene an e2e spec renders and not every scene an
 * application draws.
 *
 * ## The predicate, and its two stand-downs
 *
 * The guard is given the scene's **declared regions** — the surfaces the scene
 * says it draws, in device px — and reads each one on its own terms:
 *
 * - A pixel is a **candidate** when its alpha is exactly zero.
 * - A pixel is a **wall** when its alpha is at or above half the peak alpha
 *   **inside the declared region being read**, floored at one code. That is the
 *   drawn silhouette, read at the threshold W20's declaration conformance reads
 *   it at (`declared-coverage.ts`, `declared-conformance.test.ts`).
 * - A candidate is **enclosed** when it cannot reach the raster's border by a
 *   4-connected walk through non-wall pixels.
 * - The guard fires on an enclosed candidate component that has at least one
 *   pixel inside a declared region.
 *
 * **The wall is read per region, and that is finding N1's correction.** The
 * first shipped form took one cutoff for the whole raster, half of the WHOLE
 * raster's peak — and the review measured what that costs: a bright surface at
 * alpha 255 elsewhere in the scene lifts the cutoff to 128, a dim surface at
 * alpha 100 is then not a wall at all, and a 4×4 hole punched through the dim
 * one reads as ZERO holes. The same dim surface alone reads one. A guard whose
 * sensitivity on a surface depends on what else is in the frame is a guard that
 * is silent on exactly the scene that has more than one thing in it, and
 * `glass-over-glass` — the scene the bed's own residual sits on — is a
 * two-surface scene. Reading the cutoff from the region's own peak makes each
 * surface's silhouette its own.
 *
 * **Bounding candidates to the declared regions is the other half**, and it is
 * the charter's own wording ("an enclosed region of zero alpha inside a declared
 * silhouette") taken literally rather than approximated by the raster. It is
 * what stands the guard down on the outer shadow's quantisation tail: on
 * `page-material.spec.ts`'s scalar scene the composited alpha 170 CSS px out
 * reads 1 and 2 of 255, one pixel of it rounds to 0 with 1s and 2s all round it,
 * and the first form fired on two of forty-two `@gpu` cases for it
 * (`guard-first-form.txt`). That pixel is nowhere near a declared surface. It is
 * a rounding event in a facet, not a hole in a silhouette.
 *
 * Both stand-downs then fall out of the definition rather than being exceptions
 * to it, which is the reason it is worded this way:
 *
 *  1. **The unsampled layer path.** It writes `bodyAlpha = presentAlpha` — a
 *     deliberately translucent interior, sometimes only a few codes of alpha
 *     over a large area. The predicate reads *exactly zero* and never a
 *     threshold, so a translucent interior is not a candidate at all. A guard
 *     phrased as "low alpha" would refuse that path's every frame.
 *  2. **Presence 0.** `dom_material_alpha` is legitimately 0 where a surface is
 *     not there, so the surface's whole footprint is zero — and a declared
 *     region whose own peak is zero drew nothing, so there is no silhouette for
 *     anything to be a hole in and the region is not read at all. That is the
 *     per-region form of what the one-code floor used to do for the whole
 *     raster, and it is exact rather than incidental: it no longer depends on
 *     the transparent page around the surface reaching the border.
 */

export interface AlphaHole {
  /** Number of zero-alpha pixels in the enclosed component. */
  readonly area: number;
  /** Inclusive pixel bounds of the component. */
  readonly x0: number;
  readonly y0: number;
  readonly x1: number;
  readonly y1: number;
}

export interface Raster {
  readonly width: number;
  readonly height: number;
  /** RGBA8, row-major, `width * height * 4` bytes. */
  readonly data: Uint8Array;
}

/**
 * A surface the scene declared it would draw, in **device px** — the raster's
 * own units, because that is what the guard reads.
 *
 * The same five numbers `declared-coverage.ts` reads a conformance clause from,
 * and deliberately the same shape: the guard and the sweep are reading the same
 * declaration, one for coverage and one for holes.
 */
export interface DeclaredRegion {
  readonly cx: number;
  readonly cy: number;
  readonly w: number;
  readonly h: number;
  readonly r: number;
}

/** The signed distance to a rounded rectangle, device px, negative inside. */
const roundedRectDistance = (x: number, y: number, region: DeclaredRegion): number => {
  const dx = Math.abs(x - region.cx) - (region.w / 2 - region.r);
  const dy = Math.abs(y - region.cy) - (region.h / 2 - region.r);
  const ox = Math.max(dx, 0);
  const oy = Math.max(dy, 0);
  return Math.min(Math.max(dx, dy), 0) + Math.hypot(ox, oy) - region.r;
};

/**
 * The region's pixels: centre at least half a pixel inside the contour.
 *
 * `declared-coverage.ts`'s rule, for `declared-coverage.ts`'s reason — a
 * partially covered pixel is evidence about the contour, not about coverage —
 * and here it also keeps the antialiased ring out of the peak the cutoff is
 * read from.
 */
const maskOf = (region: DeclaredRegion, width: number, height: number): number[] => {
  const out: number[] = [];
  const x0 = Math.max(0, Math.floor(region.cx - region.w / 2) - 1);
  const x1 = Math.min(width - 1, Math.ceil(region.cx + region.w / 2) + 1);
  const y0 = Math.max(0, Math.floor(region.cy - region.h / 2) - 1);
  const y1 = Math.min(height - 1, Math.ceil(region.cy + region.h / 2) + 1);
  for (let y = y0; y <= y1; y += 1) {
    for (let x = x0; x <= x1; x += 1) {
      if (roundedRectDistance(x + 0.5, y + 0.5, region) <= -0.5) out.push(y * width + x);
    }
  }
  return out;
};

interface Labelled {
  readonly holes: readonly AlphaHole[];
  /** Component index per pixel, `-1` where the pixel is in none. */
  readonly label: Int32Array;
}

/**
 * Every enclosed zero-alpha component at one wall cutoff, with a per-pixel
 * label so a caller can ask which components a region touches.
 *
 * One pass to mark everything the border can reach without crossing drawn
 * material, one pass to label the zero-alpha pixels it could not. Both are
 * iterative — a recursive flood fill overflows the stack on a full-target
 * region, which is a failure mode a guard must not have.
 */
function componentsAtCutoff(raster: Raster, cutoff: number): Labelled {
  const { width, height, data } = raster;
  const count = width * height;

  // 0 = free (below the cutoff, and not zero), 1 = zero-alpha candidate,
  // 2 = reached from the border, 4 = wall (drawn material).
  const state = new Uint8Array(count);
  for (let i = 0; i < count; i += 1) {
    const alpha = data[i * 4 + 3] ?? 0;
    state[i] = alpha === 0 ? 1 : alpha >= cutoff ? 4 : 0;
  }

  const queue = new Int32Array(count);
  let head = 0;
  let tail = 0;
  /**
   * Walk out from the border through everything that is NOT drawn material: a
   * free pixel or a zero-alpha one. A candidate the walk reaches is open to the
   * exterior through a facet — the shadow's tail, the antialiased ring — and is
   * not a hole in anything.
   */
  const push = (index: number): void => {
    if (state[index] !== 1 && state[index] !== 0) return;
    state[index] = 2;
    queue[tail] = index;
    tail += 1;
  };

  for (let x = 0; x < width; x += 1) {
    push(x);
    push((height - 1) * width + x);
  }
  for (let y = 0; y < height; y += 1) {
    push(y * width);
    push(y * width + width - 1);
  }
  while (head < tail) {
    const index = queue[head] as number;
    head += 1;
    const x = index % width;
    const y = (index - x) / width;
    if (x > 0) push(index - 1);
    if (x + 1 < width) push(index + 1);
    if (y > 0) push(index - width);
    if (y + 1 < height) push(index + width);
  }

  const label = new Int32Array(count).fill(-1);
  const holes: AlphaHole[] = [];
  for (let seed = 0; seed < count; seed += 1) {
    if (state[seed] !== 1) continue;
    const component = holes.length;
    let area = 0;
    let x0 = width;
    let y0 = height;
    let x1 = -1;
    let y1 = -1;
    head = 0;
    tail = 0;
    state[seed] = 3;
    label[seed] = component;
    queue[tail] = seed;
    tail += 1;
    const visit = (index: number): void => {
      if (state[index] !== 1) return;
      state[index] = 3;
      label[index] = component;
      queue[tail] = index;
      tail += 1;
    };
    while (head < tail) {
      const index = queue[head] as number;
      head += 1;
      const x = index % width;
      const y = (index - x) / width;
      area += 1;
      if (x < x0) x0 = x;
      if (x > x1) x1 = x;
      if (y < y0) y0 = y;
      if (y > y1) y1 = y;
      if (x > 0) visit(index - 1);
      if (x + 1 < width) visit(index + 1);
      if (y > 0) visit(index - width);
      if (y + 1 < height) visit(index + width);
    }
    holes.push({ area, x0, y0, x1, y1 });
  }
  return { holes, label };
}

/**
 * Every enclosed zero-alpha region inside a declared silhouette, largest first.
 *
 * One flood per distinct cutoff rather than one per region: several surfaces of
 * the same scene usually composite at the same alpha, and the walk is over the
 * whole raster either way.
 */
export function enclosedZeroAlphaRegions(
  raster: Raster,
  declared: readonly DeclaredRegion[],
): AlphaHole[] {
  const { width, height, data } = raster;
  if (width <= 0 || height <= 0) return [];

  /*
   * Each region's own cutoff: half the peak alpha INSIDE it, floored at one
   * code. Half the peak rather than half of 255 because a group over a
   * transparent page emits the material's own alpha, which is well under one on
   * the layer path; the region's peak rather than the raster's because a
   * surface's silhouette is its own (finding N1). A region whose peak is zero
   * drew nothing at all and is not read: there is no silhouette there for
   * anything to be a hole in.
   */
  const masks = new Map<number, number[]>();
  for (const region of declared) {
    const mask = maskOf(region, width, height);
    let peak = 0;
    for (const index of mask) peak = Math.max(peak, data[index * 4 + 3] ?? 0);
    if (peak === 0) continue;
    const cutoff = Math.max(1, peak / 2);
    const together = masks.get(cutoff);
    // Appended one at a time rather than with a spread: `push(...mask)` is an
    // apply, and a 340 px caster's mask is 115,432 arguments, which overflows
    // the stack. A guard that crashes on a large surface is worse than one that
    // is silent, and this is the second form of that failure mode the module
    // has had to avoid (the first is the iterative flood below).
    if (together === undefined) masks.set(cutoff, mask);
    else for (const index of mask) together.push(index);
  }

  const found = new Map<string, AlphaHole>();
  for (const [cutoff, mask] of masks) {
    const { holes, label } = componentsAtCutoff(raster, cutoff);
    if (holes.length === 0) continue;
    const touched = new Set<number>();
    for (const index of mask) {
      const component = label[index] ?? -1;
      if (component >= 0) touched.add(component);
    }
    for (const component of touched) {
      const hole = holes[component] as AlphaHole;
      found.set(`${hole.x0},${hole.y0},${hole.x1},${hole.y1},${hole.area}`, hole);
    }
  }
  return [...found.values()].sort((a, b) => b.area - a.area);
}

/**
 * The refusal a guarded readback raises, or `undefined` when the raster is
 * sound.
 *
 * A message rather than a boolean: the whole value of catching this at the
 * readback is that it can say WHERE, and a hole's bounds are what a reader needs
 * to decide whether they are looking at §5.159b's strip again or at something
 * new.
 */
export function alphaHoleRefusal(
  raster: Raster,
  label: string,
  declared: readonly DeclaredRegion[],
): string | undefined {
  const holes = enclosedZeroAlphaRegions(raster, declared);
  if (holes.length === 0) return undefined;
  const worst = holes[0] as AlphaHole;
  const total = holes.reduce((sum, hole) => sum + hole.area, 0);
  return (
    `${label}: the raster has ${holes.length} enclosed region(s) of ZERO alpha inside the drawn ` +
    `silhouette, ${total} px in all. The largest is ${worst.area} px spanning ` +
    `(${worst.x0}, ${worst.y0})–(${worst.x1}, ${worst.y1}). That is the signature a NaN leaves ` +
    `when it reaches a colour target: written to rgba8unorm it becomes zero, and zero alpha ` +
    `inside a DECLARED surface, walled in by material at half that surface's own peak or more, ` +
    `is a hole where the surface declared itself. It is what left a 44 px capsule with a strip ` +
    `undrawn in W30 (claims §5.159b). Three things are deliberately NOT this: a translucent ` +
    `interior, because the predicate reads alpha exactly 0; a surface that drew nothing at all, ` +
    `whose declared region has no peak to be walled by; and a rounding event in the outer ` +
    `shadow's tail, which is outside every declared silhouette.`
  );
}

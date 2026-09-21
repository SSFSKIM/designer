/**
 * W31 G2 — the standing readback guard: an ENCLOSED region of zero alpha
 * (claims §5.163 §3; the tracker's WGSL range class, fix shape 3).
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
 * ## The predicate, and its two stand-downs
 *
 * A pixel is a **candidate** when its alpha is exactly zero. A pixel is a
 * **wall** when its alpha is at or above half the raster's own peak — which is
 * the drawn silhouette, read by exactly the extractor W20's declaration
 * conformance reads (`declared-coverage.ts`, `declared-conformance.test.ts`). A
 * candidate is **enclosed** when it cannot reach the raster's border by a
 * 4-connected walk through non-wall pixels. The guard fires on any enclosed
 * candidate component.
 *
 * Both clauses are load-bearing and each was measured to be. Take the wall out
 * and the guard fires on the outer shadow's own quantisation tail: on
 * `page-material.spec.ts`'s scalar scene the composited alpha 170 CSS px out
 * reads 1 and 2 of 255, and one pixel of it rounds to 0 with 1s and 2s all
 * round it — an isolated zero surrounded by *something*, and by nothing drawn.
 * That is a rounding event in a facet, not a hole in a silhouette, and it is
 * what "inside a declared silhouette" means as a clause rather than as a
 * synonym for "enclosed" (W31 G2; claims §5.163 §3).
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
 *     not there, so the surface's whole footprint is zero — and so is the page
 *     around it, which means the region reaches the border and is not enclosed.
 *     Enclosure, not emptiness, is what distinguishes a hole from an absence.
 *     A raster that is zero everywhere has no peak and therefore no wall, so it
 *     has nothing to be enclosed by.
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
 * Every enclosed zero-alpha component, largest first.
 *
 * One pass to mark everything the border can reach without crossing drawn
 * material, one pass to label the zero-alpha pixels it could not. Both are
 * iterative — a recursive flood fill overflows the stack on a full-target
 * region, which is a failure mode a guard must not have.
 */
export function enclosedZeroAlphaRegions(raster: Raster): AlphaHole[] {
  const { width, height, data } = raster;
  if (width <= 0 || height <= 0) return [];
  const count = width * height;

  /*
   * The drawn silhouette's cutoff: half the raster's own peak alpha, floored at
   * one code. The peak rather than 255 because a group over a transparent page
   * emits the material's own alpha, which is well under one on the layer path;
   * the floor because a raster that drew nothing has a peak of zero, and a
   * cutoff of zero would make every pixel a wall and the empty render a solid
   * one.
   */
  let peak = 0;
  for (let i = 3; i < data.length; i += 4) peak = Math.max(peak, data[i] ?? 0);
  const cutoff = Math.max(1, peak / 2);

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

  const holes: AlphaHole[] = [];
  for (let seed = 0; seed < count; seed += 1) {
    if (state[seed] !== 1) continue;
    let area = 0;
    let x0 = width;
    let y0 = height;
    let x1 = -1;
    let y1 = -1;
    head = 0;
    tail = 0;
    state[seed] = 3;
    queue[tail] = seed;
    tail += 1;
    const visit = (index: number): void => {
      if (state[index] !== 1) return;
      state[index] = 3;
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
  return holes.sort((a, b) => b.area - a.area);
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
export function alphaHoleRefusal(raster: Raster, label: string): string | undefined {
  const holes = enclosedZeroAlphaRegions(raster);
  if (holes.length === 0) return undefined;
  const worst = holes[0] as AlphaHole;
  const total = holes.reduce((sum, hole) => sum + hole.area, 0);
  return (
    `${label}: the raster has ${holes.length} enclosed region(s) of ZERO alpha inside the drawn ` +
    `silhouette, ${total} px in all. The largest is ${worst.area} px spanning ` +
    `(${worst.x0}, ${worst.y0})–(${worst.x1}, ${worst.y1}). That is the signature a NaN leaves ` +
    `when it reaches a colour target: written to rgba8unorm it becomes zero, and zero alpha ` +
    `walled in by material at half the raster's peak or more is a hole where the surface ` +
    `declared itself. It is what left a 44 px capsule with a strip undrawn in W30 (claims ` +
    `§5.159b). Three things are deliberately NOT this: a translucent interior, because the ` +
    `predicate reads alpha exactly 0; a surface at presence 0, whose zero region reaches the ` +
    `border; and a rounding event in the outer shadow's tail, which is walled in by nothing ` +
    `drawn.`
  );
}

/**
 * Materialising one reference bed out of several capture runs.
 *
 * The doctrine this replaces took three runs of the same cell and kept whichever
 * bytes at least two of them shared. That is the right rule for noise — a stray
 * bit, a compositor hiccup, a frame caught mid-flush — because noise is a wrong
 * answer scattered around a right one, and a majority finds the right one.
 *
 * It is the wrong rule for a *state*. On 2026-08-31 one cell returned the
 * committed bytes on the first run and a materially different appearance on the
 * second and third, twenty seconds apart, with nothing changed between them: the
 * body about 32 codes brighter and the outer shadow weaker (claims §5.18). Two
 * of three agreed, so the majority rule named a winner and recorded nothing —
 * and the whole point of a reference bed is that it is not a coin flip that came
 * up heads.
 *
 * So this module distinguishes the two cases before it decides anything, and it
 * has one piece of evidence the old rule did not use: **the harness already
 * attests each cell byte-stable inside its own run**, by capturing it twice and
 * comparing (`deterministic` in the manifest). A variant that is settled within
 * its run is a value the machine returns on purpose, not a value it stumbled
 * into. When two settled variants disagree *structurally*, the cell has two
 * states, and the bed cannot say which one it is without a ruling.
 */

/** One distinct byte-image, and which runs returned it. */
export interface CaptureVariant {
  readonly sha256: string;
  /** Run labels that produced exactly these bytes, in run order. */
  readonly runs: readonly string[];
  /**
   * Whether *every* run that produced it attested the cell byte-stable within
   * that run. Absent attestation counts as unsettled: this asks the record for
   * a positive claim rather than reading silence as one.
   */
  readonly settled: boolean;
}

/** How one variant differs from the variant it is being weighed against. */
export interface VariantDifference {
  /** Largest absolute 8-bit channel difference over the whole image. */
  readonly maxDelta: number;
  /** Pixels differing in any channel. */
  readonly changedPx: number;
  /**
   * Of the changed pixels, the fraction with at least one 4-neighbour that also
   * changed — 0 for isolated speckle, near 1 for any contiguous region.
   */
  readonly coherence: number;
}

/**
 * One 8-bit code: the raster's own quantisation step, and the smallest
 * difference it can represent.
 *
 * A difference that fits inside it is not a description of a material — there is
 * no appearance a renderer could hold that is half a code away from another one.
 * This is a floor rather than a tolerance: it is not "close enough to ignore",
 * it is "below what the image can say".
 */
export const RASTER_QUANTISATION_DELTA = 1;

/**
 * Half the changed pixels must touch another changed pixel for a difference to
 * count as structured.
 *
 * The two populations sit at the ends rather than around this value, which is
 * why the exact number does not carry weight. Isolated speckle scores 0 by
 * construction — no changed pixel has a changed neighbour. Any contiguous region
 * larger than about 4×4 px scores above 0.8, because a region's interior grows
 * as its area while its boundary grows as its perimeter. The midpoint between
 * two poles is the honest place to cut, and every classification this module
 * makes reports its measured coherence so the separation stays checkable rather
 * than assumed.
 */
export const STRUCTURE_COHERENCE = 0.5;

/**
 * Is this difference a description of a different appearance, or the raster
 * being imprecise about the same one?
 */
export function classifyDifference(
  difference: VariantDifference,
): "incidental" | "structured" {
  if (difference.changedPx === 0) return "incidental";
  if (difference.maxDelta <= RASTER_QUANTISATION_DELTA) return "incidental";
  return difference.coherence >= STRUCTURE_COHERENCE ? "structured" : "incidental";
}

export type CellResolution =
  | {
      readonly kind: "agreed";
      readonly chosen: CaptureVariant;
    }
  | {
      readonly kind: "voted";
      readonly chosen: CaptureVariant;
      readonly outvoted: readonly CaptureVariant[];
      readonly reason: string;
    }
  | {
      readonly kind: "refused";
      /** Why no single variant may be published as the cell's value. */
      readonly reason: string;
      readonly stateAmbiguous: boolean;
      readonly variants: readonly CaptureVariant[];
    };

/**
 * Decide one cell's published bytes from the runs that produced it.
 *
 * `differenceTo` is asked for the difference between the leading variant and
 * each other one, so the caller owns pixel decoding and this stays a decision
 * over summaries.
 */
export function resolveCell(
  variants: readonly CaptureVariant[],
  differenceTo: (majority: CaptureVariant, other: CaptureVariant) => VariantDifference,
): CellResolution {
  if (variants.length === 0) {
    throw new Error("resolveCell: a cell with no capture runs has nothing to resolve.");
  }
  if (variants.length === 1) return { kind: "agreed", chosen: variants[0] as CaptureVariant };

  const ranked = [...variants].sort((a, b) => b.runs.length - a.runs.length);
  const leader = ranked[0] as CaptureVariant;
  const rest = ranked.slice(1);

  // Structure first, and before the count. A cell that holds two settled
  // appearances is state-ambiguous however the runs happened to split, so
  // asking "who won" before asking "is this even a vote" would let a 2–1 split
  // publish a state the machine picks between at random.
  const structured = rest.filter(
    (other) =>
      other.settled &&
      leader.settled &&
      classifyDifference(differenceTo(leader, other)) === "structured",
  );
  if (structured.length > 0) {
    const named = [leader, ...structured].map((v) => {
      if (v === leader) return `${v.sha256.slice(0, 12)} (${v.runs.join("")})`;
      const d = differenceTo(leader, v);
      return (
        `${v.sha256.slice(0, 12)} (${v.runs.join("")}) at maxDelta ${d.maxDelta}, ` +
        `${d.changedPx} px changed, coherence ${d.coherence.toFixed(3)}`
      );
    });
    return {
      kind: "refused",
      stateAmbiguous: true,
      variants: [leader, ...structured],
      reason:
        `the runs returned ${1 + structured.length} settled appearances that differ structurally, ` +
        `not one appearance and some noise — ${named.join(" vs ")}. A majority would publish ` +
        `whichever state happened to win two runs, which is a coin flip wearing a reference's name.`,
    };
  }

  const tied = ranked.filter((v) => v.runs.length === leader.runs.length);
  if (tied.length > 1) {
    return {
      kind: "refused",
      stateAmbiguous: false,
      variants: ranked,
      reason:
        `no variant holds a plurality (${ranked.map((v) => `${v.runs.join("")}=${v.runs.length}`).join(", ")}), ` +
        `and the differences are within the raster's own precision, so the cell is genuinely noisy.`,
    };
  }

  return {
    kind: "voted",
    chosen: leader,
    outvoted: rest,
    reason:
      `${leader.runs.join("")} agree and the ${rest.length} other reading(s) differ only incidentally ` +
      `— at or below one 8-bit code, or scattered rather than in a region.`,
  };
}

/**
 * Summarise how two same-sized RGBA rasters differ.
 *
 * Alpha is deliberately out of the comparison: these fixtures are opaque window
 * captures, and an alpha channel that never varies would only dilute the
 * coherence figure with pixels that cannot change.
 */
export function differenceSummary(
  a: Uint8Array,
  b: Uint8Array,
  width: number,
  height: number,
): VariantDifference {
  if (a.length !== b.length || a.length !== width * height * 4) {
    throw new Error(
      `differenceSummary: ${a.length} and ${b.length} bytes cannot both be a ${width}x${height} RGBA raster.`,
    );
  }
  const changed = new Uint8Array(width * height);
  let maxDelta = 0;
  let changedPx = 0;
  for (let p = 0; p < width * height; p += 1) {
    const i = p * 4;
    let worst = 0;
    for (let c = 0; c < 3; c += 1) {
      const d = Math.abs((a[i + c] ?? 0) - (b[i + c] ?? 0));
      if (d > worst) worst = d;
    }
    if (worst > 0) {
      changed[p] = 1;
      changedPx += 1;
      if (worst > maxDelta) maxDelta = worst;
    }
  }
  if (changedPx === 0) return { maxDelta: 0, changedPx: 0, coherence: 0 };

  let neighboured = 0;
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const p = y * width + x;
      if (changed[p] !== 1) continue;
      const touching =
        (x > 0 && changed[p - 1] === 1) ||
        (x + 1 < width && changed[p + 1] === 1) ||
        (y > 0 && changed[p - width] === 1) ||
        (y + 1 < height && changed[p + width] === 1);
      if (touching) neighboured += 1;
    }
  }
  return { maxDelta, changedPx, coherence: neighboured / changedPx };
}

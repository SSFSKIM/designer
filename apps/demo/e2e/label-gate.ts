/**
 * The all-label gate's verdicts, and the scheduling arithmetic behind its phases.
 *
 * Nothing here touches a browser, and that is deliberate rather than tidy. The
 * gate measures the whole inventory first, writes every measured row to disk, and
 * only then asks whether the rows pass — so a floor that fails leaves a complete,
 * auditable record instead of a record truncated at the first bad label. Keeping
 * the judging half pure is what makes that ordering possible, and it lets the
 * rules be held to a unit suite that needs neither a page nor an adapter.
 */

/**
 * WCAG's two readings of "large text", as numbers this gate can check.
 *
 * The success criterion is 18pt, or 14pt **at bold** — 24px at any weight, or
 * 18.66px bold. Both are admitted here, because refusing the second would hold the
 * page to a size the criterion does not ask for. What is not admitted is a weight
 * that merely looks heavy: "bold" is a judgement about a face, and at 650 in the
 * system UI face it is arguable either way, so the lower threshold is granted only
 * to type whose computed weight is numerically at least 700. That is the one point
 * where the CSS keyword `bold` and the criterion's word agree without argument.
 */
export const LARGE_LABEL_MIN_PX = 24;
export const LARGE_LABEL_BOLD_MIN_PX = 18.66;
export const LARGE_LABEL_BOLD_WEIGHT = 700;

/**
 * Whether type at this size and weight is large text under either reading.
 *
 * Both comparisons are written so that a value which did not resolve to a number
 * — a computed weight some engine reported as a keyword, a size that failed to
 * parse — answers `false`. A size check that guesses in the page's favour is the
 * same failure as a contrast check that does, one step earlier.
 */
export function qualifiesAsLargeText(fontSizePx: number, fontWeight: number): boolean {
  if (fontSizePx >= LARGE_LABEL_MIN_PX) return true;
  return fontWeight >= LARGE_LABEL_BOLD_WEIGHT && fontSizePx >= LARGE_LABEL_BOLD_MIN_PX;
}

/** Apple's four ink levels, strongest first. */
export const INK_LADDER = ["primary", "secondary", "tertiary", "quaternary"] as const;

/** One measured label, reduced to what a floor and a size verdict need. */
export interface GateRow {
  /** Route, state, family and text: enough to find the label in the record. */
  readonly where: string;
  readonly floorName: string;
  /** `null` where the level is read and recorded but promises no ratio. */
  readonly floor: number | null;
  readonly ratio: number;
  readonly fontSizePx: number;
  /** The computed weight as a number; CSS keywords resolve to one before this. */
  readonly fontWeight: number;
}

/** One measured specimen on one plate, reduced to what the ladder needs. */
export interface LadderRow {
  /** One ladder: one plate in one state. */
  readonly where: string;
  readonly level: string;
  readonly ratio: number;
}

/**
 * Every row that misses the floor it was given, named.
 *
 * The comparison is written as a refused `>=` rather than a `<` so that a ratio
 * that came back as `NaN` — a family that matched nothing measurable — fails
 * instead of slipping through the one direction a contrast gate must never be
 * wrong in.
 */
export function floorFailures(rows: readonly GateRow[]): readonly string[] {
  const failures: string[] = [];
  for (const row of rows) {
    if (row.floor === null || row.ratio >= row.floor) continue;
    failures.push(
      `${row.where}: ${row.ratio.toFixed(3)} misses the ${row.floorName} floor of ${String(row.floor)}`,
    );
  }
  return failures;
}

/**
 * Every row claiming the large-label floor whose rendered type is not large.
 *
 * Without this the 3:1 floor is a promise about a size nobody checks: a later type
 * change could quietly take a plate label under either threshold — by shrinking it,
 * or by dropping its weight below bold while it sits under 24px — and the gate
 * would go on passing it at a floor it no longer qualifies for.
 */
export function largeLabelSizeFailures(rows: readonly GateRow[]): readonly string[] {
  const failures: string[] = [];
  for (const row of rows) {
    if (row.floorName !== "large-label-pixel") continue;
    if (qualifiesAsLargeText(row.fontSizePx, row.fontWeight)) continue;
    failures.push(
      `${row.where}: rendered at ${String(row.fontSizePx)}px weight ${String(row.fontWeight)}, ` +
        `which is neither ${String(LARGE_LABEL_MIN_PX)}px at any weight nor ` +
        `${String(LARGE_LABEL_BOLD_MIN_PX)}px at weight ${String(LARGE_LABEL_BOLD_WEIGHT)}, so this ` +
        `row is not large text and may not claim WCAG's 3:1 floor`,
    );
  }
  return failures;
}

/**
 * Every plate whose four ink levels do not descend, and every plate missing one.
 *
 * An incomplete ladder is a failure rather than a subset to order: two of the
 * four levels carry no contrast floor at all, so the only thing holding them
 * honest is that each reads weaker than the one above it. A ladder judged on
 * whichever levels happened to be measured would drop that guarantee silently.
 */
export function ladderFailures(rows: readonly LadderRow[]): readonly string[] {
  const ladders = new Map<string, Map<string, number>>();
  for (const row of rows) {
    const ladder = ladders.get(row.where) ?? new Map<string, number>();
    ladder.set(row.level, row.ratio);
    ladders.set(row.where, ladder);
  }

  const failures: string[] = [];
  for (const [where, ladder] of ladders) {
    const missing = INK_LADDER.filter((level) => !ladder.has(level));
    if (missing.length > 0) {
      failures.push(`${where}: the ink ladder is incomplete — ${missing.join(", ")} not measured`);
      continue;
    }
    for (let step = 1; step < INK_LADDER.length; step += 1) {
      const stronger = INK_LADDER[step - 1] ?? "";
      const weaker = INK_LADDER[step] ?? "";
      const above = ladder.get(stronger) ?? Number.NaN;
      const below = ladder.get(weaker) ?? Number.NaN;
      if (below <= above) continue;
      failures.push(
        `${where}: ${weaker} reads ${below.toFixed(3)}, above ${stronger}'s ${above.toFixed(3)}`,
      );
    }
  }
  return failures;
}

/**
 * How long is left to wait to reach `offsetMs` after a scenario started.
 *
 * The phases name offsets into a backdrop's drift, and measuring is not free: a
 * family that takes two seconds to read pushes every later phase that far past
 * the moment it was chosen to land on, until the four samples are no longer four
 * points of one period. Each sample therefore waits only the remainder to its own
 * offset from the scenario's start.
 */
export function remainingWait(startedAtMs: number, nowMs: number, offsetMs: number): number {
  return Math.max(0, offsetMs - (nowMs - startedAtMs));
}

/**
 * Where one cell's raw readings are written.
 *
 * A tag lands beside the plain name rather than replacing it, so a corrective run
 * adds a record next to the one already committed instead of standing in for it.
 */
export function evidenceFileName(tier: string, scheme: string, tag: string | undefined): string {
  const suffix = tag === undefined || tag === "" ? "" : `-${tag}`;
  return `contrast-${tier}-${scheme}${suffix}.json`;
}

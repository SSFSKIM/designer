/**
 * The all-label gate's verdicts, held to tests that need no browser.
 *
 * The gate measures in Chromium and then judges what it measured, and the two
 * halves are deliberately separable: the measured rows are written to disk before
 * any verdict runs, so a failing floor leaves a complete record rather than a
 * truncated one. Everything asserted here is the second half — the arithmetic that
 * turns rows into failures — which is exactly the part that would otherwise only
 * ever be exercised by a ten-minute browser run.
 */

import { describe, expect, it } from "vitest";

import {
  INK_LADDER,
  LARGE_LABEL_BOLD_MIN_PX,
  LARGE_LABEL_BOLD_WEIGHT,
  LARGE_LABEL_MIN_PX,
  evidenceFileName,
  floorFailures,
  ladderFailures,
  largeLabelSizeFailures,
  qualifiesAsLargeText,
  remainingWait,
  type GateRow,
  type LadderRow,
} from "../e2e/label-gate";

const row = (overrides: Partial<GateRow> = {}): GateRow => ({
  where: "/ material: 112px",
  floorName: "large-label-pixel",
  floor: 3,
  ratio: 10,
  fontSizePx: 20,
  fontWeight: 700,
  ...overrides,
});

const ladder = (where: string, ratios: readonly number[]): LadderRow[] =>
  INK_LADDER.map((level, index) => ({ where, level, ratio: ratios[index] ?? Number.NaN }));

describe("floor verdicts", () => {
  it("passes a row that meets its floor exactly", () => {
    expect(floorFailures([row({ floor: 4.5, ratio: 4.5 })])).toEqual([]);
  });

  it("names the row, the reading and the floor it missed", () => {
    const failures = floorFailures([row({ where: "/ toolbar: Publish", floorName: "body-pixel", floor: 4.5, ratio: 4.463 })]);
    expect(failures).toHaveLength(1);
    expect(failures[0]).toContain("/ toolbar: Publish");
    expect(failures[0]).toContain("4.463");
    expect(failures[0]).toContain("body-pixel");
  });

  it("reports every failing row rather than stopping at the first", () => {
    expect(
      floorFailures([
        row({ where: "first", floor: 4.5, ratio: 1.2 }),
        row({ where: "second", floor: 3, ratio: 9 }),
        row({ where: "third", floor: 4.5, ratio: 2.1 }),
      ]),
    ).toHaveLength(2);
  });

  it("lets a read-only row through, because a null floor is a measurement and not a promise", () => {
    expect(floorFailures([row({ floorName: "read-only", floor: null, ratio: 1.203 })])).toEqual([]);
  });

  it("fails a row whose ratio is not a number, rather than comparing NaN away", () => {
    expect(floorFailures([row({ floor: 4.5, ratio: Number.NaN })])).toHaveLength(1);
  });
});

describe("what WCAG calls large text", () => {
  it("accepts the plain threshold at any weight, bold or not", () => {
    expect(qualifiesAsLargeText(LARGE_LABEL_MIN_PX, 400)).toBe(true);
  });

  it("accepts the lower threshold once the weight is numerically bold", () => {
    expect(qualifiesAsLargeText(LARGE_LABEL_BOLD_MIN_PX, LARGE_LABEL_BOLD_WEIGHT)).toBe(true);
    expect(qualifiesAsLargeText(20, 700)).toBe(true);
  });

  it("refuses the lower threshold below bold, however heavy it looks", () => {
    expect(qualifiesAsLargeText(20, 650)).toBe(false);
  });

  it("refuses type below the lower threshold even at bold", () => {
    expect(qualifiesAsLargeText(18, 700)).toBe(false);
    expect(qualifiesAsLargeText(17, 900)).toBe(false);
  });

  it("refuses a weight that did not resolve to a number, rather than assuming bold", () => {
    expect(qualifiesAsLargeText(20, Number.NaN)).toBe(false);
  });
});

describe("the large-text size check", () => {
  it("accepts a row the page draws as large text", () => {
    expect(largeLabelSizeFailures([row({ fontSizePx: 20, fontWeight: 700 })])).toEqual([]);
  });

  it("refuses a 3.0 row that qualifies under neither reading", () => {
    const failures = largeLabelSizeFailures([
      row({ where: "/ tone: 68px", fontSizePx: 17, fontWeight: 650 }),
    ]);
    expect(failures).toHaveLength(1);
    expect(failures[0]).toContain("/ tone: 68px");
    expect(failures[0]).toContain("17");
    expect(failures[0]).toContain("650");
  });

  it("refuses a row that lost its bold weight without gaining the plain size", () => {
    expect(largeLabelSizeFailures([row({ fontSizePx: 20, fontWeight: 400 })])).toHaveLength(1);
  });

  it("says nothing about body rows, which carry the 4.5 floor whatever their size", () => {
    expect(
      largeLabelSizeFailures([
        row({ floorName: "body-pixel", floor: 4.5, fontSizePx: 13, fontWeight: 400 }),
      ]),
    ).toEqual([]);
  });
});

describe("the ink ladder", () => {
  it("accepts a ladder that descends", () => {
    expect(ladderFailures(ladder("light plate", [5.642, 4.463, 1.675, 1.206]))).toEqual([]);
  });

  it("accepts equal neighbours, which are an ordering and not an inversion", () => {
    expect(ladderFailures(ladder("light plate", [5, 5, 5, 5]))).toEqual([]);
  });

  it("names an inverted pair", () => {
    const failures = ladderFailures(ladder("dark plate", [5.642, 4.463, 4.9, 1.206]));
    expect(failures).toHaveLength(1);
    expect(failures[0]).toContain("dark plate");
    expect(failures[0]).toContain("tertiary");
    expect(failures[0]).toContain("secondary");
  });

  it("judges each plate's ladder on its own", () => {
    expect(
      ladderFailures([
        ...ladder("light plate", [5, 4, 3, 2]),
        ...ladder("dark plate", [5, 4, 4.5, 2]),
      ]),
    ).toHaveLength(1);
  });

  it("fails an incomplete ladder instead of silently ordering what it has", () => {
    const failures = ladderFailures([
      { where: "light plate", level: "primary", ratio: 5 },
      { where: "light plate", level: "secondary", ratio: 4 },
    ]);
    expect(failures).toHaveLength(1);
    expect(failures[0]).toContain("incomplete");
  });
});

describe("phase scheduling", () => {
  it("waits the whole offset when the scenario has just started", () => {
    expect(remainingWait(1_000, 1_000, 2_200)).toBe(2_200);
  });

  it("subtracts the time measurement already spent, so the offsets stay absolute", () => {
    expect(remainingWait(1_000, 2_500, 2_200)).toBe(700);
  });

  it("does not wait at all once the offset has passed", () => {
    expect(remainingWait(1_000, 9_000, 2_200)).toBe(0);
  });
});

describe("evidence filenames", () => {
  it("keeps the untagged name a successful run already wrote", () => {
    expect(evidenceFileName("css", "light", undefined)).toBe("contrast-css-light.json");
  });

  it("puts a tag beside that name rather than in place of it", () => {
    expect(evidenceFileName("webgpu", "dark", "review-fix")).toBe("contrast-webgpu-dark-review-fix.json");
  });
});

# W32 G0 — the declarations: C1's three forms, every stop with today's reading, and what the bed can identify

**Committed before G1 renders a round** (W32 X2, X4; charter acceptance clause 2). Claims §5.166.
Every figure is a cut of committed evidence and of the shipped documents; no capture was taken, no
constant was fitted, no document, bound, floor or row of `results/matrix.json` moves, and nothing
under a macOS 26.5-keyed path is touched (X1, X5). `freeze.py verify` reads **26.5 freeze intact:
1818 entries** at this gate's opening and at its close.

The evidence this file summarises is beside it: `exterior-cut.txt`/`.json` (the reader),
`clearance.txt` (the clearance against the reach), `directions.md` (what the directions say),
`model-fit.txt`/`.json` (the falloff model on both sides), `c1-forms.txt`/`.json` (the three forms),
`stops.txt`/`.json` (every stop today), `shadow-law-at-shipped.txt` (B1's windows at the shipped
bytes), `departure-stat.txt` (B3), `reach.txt` (the runtime's own reach).

---

## 1. The admitted-band rule, which every figure below is read under

A band is read on a cell in a direction only where its **outer edge in CSS px lies inside that
cell's own clearance in that direction** — `clearance{Above,Below,Left,Right}` divided by the row's
scale, and for `all` the minimum of the four. The rule is geometric, so the set is a property of the
component and the scale and every cell at a span carries the same one:

| span | component | clearance CSS px (a/b, l/r) | shipped reach light / dark | admitted (all) | eaten |
| ---: | --- | --- | ---: | --- | --- |
| 32 | `rrect-sm` | 83.50 / 127.50 | 13.39 / 12.76 | `3-6 / 6-12 / 12-24 / 24-48` | none |
| 44 | `capsule-button`, `toolbar-group` | 77.50 / 99.50 | 13.41 / 12.83 | `3-6 / 6-12 / 12-24 / 24-48` | none |
| 96 | `rrect-md` | 51.50 / 79.50 | 23.74 / 24.54 | `3-6 / 6-12 / 12-24 / 24-48` | none |
| 128 | `rrect-ml` | 35.50 / 47.50 | 32.89 / 34.60 | `3-6 / 6-12 / 12-24` | `24-48` |
| 160 | `rrect-lg` | 19.50 / 19.50 | 42.93 / 45.69 | `3-6 / 6-12` | `12-24`, `24-48` |

**The charter expected `3-6 / 6-12 / 12-24` at span 160 and the rows say `3-6 / 6-12`.** The
`12-24` band's outer edge is 24 CSS px against 19.50 of clearance on every side, so it is outside
the frame in every direction; and at span 128 the `24-48` band is outside on the left and right too
(47.50 against 48.00, by half a pixel) and not only above and below. Both are corrections to the
charter, recorded in its Surprises.

An order statistic is taken only over cells whose identified band set EQUALS their span's admitted
set. The cells with a shorter set are counted and reported apart: 0 at span 32, 76 of 276 at span
44, 32 of 166 at 96, 4 of 42 at 128, 0 at 160 (every row of the generation, both tiers, both poses).

**What the rule moves, against W31 G1's own renormalisation** (`exterior-cut.txt` §3c). The two are
the same number to five decimals at spans 32, 44 and 96 on every bed. At span 128 the admitted-band
`T` is **worse** by +0.00251 to +0.00357 and at span 160 it moves by −0.00289 to +0.00064 — the
`24-48` band the frame ate carried 53 % of the weight and was where the two exteriors agreed most.
Nothing §5.162 recorded is withdrawn; the reading is printed beside it.

---

## 2. C1, in its three forms, with the bound of each

**The bound rule is the charter's** (clause 2): for the two non-declared forms, *the bound at every
span is the worst standard bed's span-96 order statistic of that form on the current generation,
rounded up to two significant figures*. It is computed by `c1-forms.py` and this gate cannot choose
it.

### Form (i) — `T` as W31 G1 declared it, one bound across the thick spans, ≤ 0.0045

| bed | 96 | 128 | 160 |
| --- | ---: | ---: | ---: |
| 1x light | 0.00408 PASS | **0.00843 FAIL** | **0.00796 FAIL** |
| 2x light | 0.00413 PASS | **0.00889 FAIL** | **0.00797 FAIL** |
| 1x dark | 0.00399 PASS | **0.00782 FAIL** | **0.00659 FAIL** |
| 2x dark | 0.00385 PASS | **0.00738 FAIL** | **0.00627 FAIL** |

Under W31 G1's renormalisation the same rows read 0.00502 / 0.00532 / 0.00511 / 0.00487 at span 128
and 0.00735 / 0.00733 / 0.00921 / 0.00916 at 160 (§5.162 §1, unchanged). The difference is the
admitted-band rule and nothing else.

### Form (ii) — the same statistic, bounded PER SPAN, ≤ **0.0042**

The four standard beds read 0.00385, 0.00399, 0.00408 and 0.00413 at span 96; the worst is 0.00413
and the rule's bound is **0.0042**. Today it passes at span 96 on all four beds with 1.7–8.3 % of
headroom and fails at 128 by 76–112 % and at 160 by 49–90 %.

### Form (iii) — the σ-normalised window: **WITHDRAWN on measurement**

σ-band edges at 0.35 / 0.7 / 1.4 / 2.8 × the bed-and-span's own median native σ, with the per-band
`|Δa|` read as the piecewise-constant profile it already is. The bound the rule produces is
**0.0085**. It is withdrawn because it cannot be stated where C1 exists to be stated:

| bed | span | native σ | clearance | clearance / σ | the fixed bands cover | σ-bands admitted |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| 1x light | 44 | 1.417 | 77.50 | 54.69 | 3–48 | **0** |
| 1x light | 96 | 8.796 | 51.50 | 5.85 | 3–48 | 3 |
| 1x light | 128 | 13.138 | 35.50 | 2.70 | 3–24 | 2 |
| 1x light | 160 | 17.317 | 19.50 | **1.13** | 3–12 | **0** |

At span 160 the admitted bands reach 12 CSS px and the FIRST σ-band ends at 0.7 σ = 12.1, so the
form reads nothing on any of the four beds — at the span whose residual is largest and where every
non-ladder cell is holdout. It reads nothing at span 44 on any bed either, so the thin regime this
wave admits to the fit would carry no shape clause at all. **And the choice of multiples is not the
cause**: the clearance measured in the bed's own native σ is 5.5–5.9 at span 96, 2.7 at 128 and 1.1
at 160, so "the same number of falloff lengths at every span" is not purchasable on a 320 × 200
canvas at any multiples. The form becomes available when the canvas does, which is this wave's first
Deferred item.

### What G0 recommends: **form (ii), at 0.0042**. The parent rules (Decision Log 1 (c)).

Form (ii) changes nothing about what is measured — it is form (i)'s own value read against a bound
stated per span, which is the minimum change that makes the promise "no worse at any span than at
span 96 today" true. It keeps the statistic, the exclusions, the population and the order statistic
exactly as §5.162 §3 declared them; it needs no re-binning and no assumption about the profile
between band edges; and the admitted-band rule makes form (i) worse rather than better as one
number, because the band SET now differs per span — four bands at 96, three at 128, two at 160 — so
one bound is a promise about three different statistics.

What adopting it costs, stated plainly: the bound is 0.0042 rather than 0.0045, so span 96 passes
with 1.7 % of headroom on 2x light where form (i) leaves 8 %. That thinness is the clause's own
statement that span 96 is not free either — a fit that buys span 128 by widening span 96 fails.

---

## 3. The candidate row, in `adopted-thresholds.test.ts`'s idiom

Written here as a block rather than as a skipped case, for the reason §5.162 §3 gives: that file's
convention is that every case in it is live and green, and a bound enters it in the commit that
adopts it. X11 does not give this gate that file.

**The conditions from §5.162 §9 finding B-1 are inside the block and are not optional.** The
adopting gate re-runs `exterior-cut.py` into ITS OWN evidence directory, against the matrix it read
its own bed at, and points `CUT` there; `CUT.atDocuments === "shipped"` and
`CUT.withHoldout === false` are asserted. **And this wave adds a third**: the case asserts the
ADMITTED BAND SET per span, because a cut whose band rule had changed would satisfy every other
guard and would not be the statistic C1 is stated over.

```ts
/**
 * **C1, adopted — the outer shadow's exterior SHAPE, per span** (declared
 * W31 G1 at claims §5.162 §3 as one bound across three spans; restated per
 * span and over the admitted bands at W32 G0, claims §5.166; fitted and met
 * at claims §5.NNN).
 *
 * **What it asserts.** The shadow axis fits an affine map of the backdrop,
 * `y = a·bg + c`, per band and per direction outside the declared contour.
 * `a` is the transmission the exterior applies at that distance, so the
 * sequence of `a` with distance is the falloff's SHAPE — read without
 * assuming the profile is a blurred edge, and strictly outside the contour,
 * so the interior cannot dilute it the way it diluted the two `ssimMean`
 * rows W30 claimed through this same lever and had refuted (§5.159 §7).
 *
 * **Per span, and over the admitted bands.** One bound across 96, 128 and
 * 160 is span-confounded (§5.162 §9, finding N-9) and the admitted-band rule
 * sharpens that rather than softening it: the band SET differs per span
 * because the capture's clearance does — four bands at 96, three at 128, two
 * at 160 on a 320x200 canvas — so one number would be a promise about three
 * different statistics. The bound is the worst standard bed's span-96
 * reading on the generation this clause was adopted against, rounded up to
 * two significant figures: "no worse at any span than at span 96 was".
 *
 * **Why not the fitted σ.** W31 G1 computed that candidate beside this one
 * and it reads the bed backwards: 0.000 and 0.027 on the two refuted rows,
 * against 5.4 and 6.2 on the two cells §5.160 §6's eye called RIGHT. Its
 * finding is recorded at §5.162 §5 and at §5.166 and is not gated.
 */
describe("W32 C1 — the shadow's exterior shape, per span (claims §5.NNN)", () => {
  const C1_TOLERANCE = 0.0042;
  const C1_SPANS = [96, 128, 160] as const;

  /** W30 G0's statistic, and B1's: the upper middle order statistic. */
  const upperMiddle = (values: readonly number[]): number =>
    [...values].sort((a, b) => a - b)[Math.floor(values.length / 2)] ?? Number.NaN;

  /**
   * The cut, RE-RUN by the adopting gate into its own directory against the
   * matrix it read its own bed at (§5.162 §9, finding B-1). Left pointing at
   * a predecessor's directory this case would assert a bound against a frozen
   * snapshot and could never fail — B1's own doc comment's "a number retyped
   * after a refit is a number that goes stale silently", one level up.
   */
  const CUT = readJson<{
    readonly atDocuments: string;
    readonly withHoldout: boolean;
    readonly candidateII: { readonly quantity: string };
    readonly admittedBandRule: { readonly rule: string };
    readonly rows: readonly {
      readonly bed: string; readonly tier: string; readonly set: string;
      readonly state: string; readonly span: number | null;
      readonly T: number | null;
      readonly admitted: readonly string[];
      readonly bandsUsed: readonly string[];
    }[];
  }>(resolve(PACKAGE_ROOT, "results", "<THE ADOPTING GATE'S OWN DIRECTORY>",
             "exterior-cut.json"));

  /**
   * The band set the clearance admits at each span, asserted rather than
   * trusted. A cut whose band rule had moved would satisfy every other guard
   * in this case and would not be the statistic C1 is stated over; and a
   * canvas change — the wave's first Deferred item — moves these sets, which
   * is exactly the kind of change that should turn this case red until
   * somebody re-reads the clause.
   */
  const ADMITTED_BANDS: Readonly<Record<number, readonly string[]>> = {
    96: ["3-6", "6-12", "12-24", "24-48"],
    128: ["3-6", "6-12", "12-24"],
    160: ["3-6", "6-12"],
  };

  /**
   * How many cells each standard bed contributes at each asserted span —
   * counted, not merely required to be non-zero, for the reason W30 G4's
   * review gave `CONTRIBUTING_BEDS` (§5.160 §9): a bed that stopped
   * contributing would leave the clause to the beds that remain instead of
   * failing. Span 160's cells are the pitch ladder's alone; span 128's are
   * two calibration cells and five probe on each light bed and five probe on
   * each dark one (§5.162 §9, finding N-6, re-counted at W32 G0).
   */
  const CONTRIBUTING_CELLS: Readonly<Record<string, Readonly<Record<number, number>>>> = {
    "1x light": { 96: 10, 128: 7, 160: 7 },
    "2x light": { 96: 10, 128: 7, 160: 7 },
    "1x dark": { 96: 9, 128: 5, 160: 7 },
    "2x dark": { 96: 9, 128: 5, 160: 7 },
  };

  const readingsAt = (bed: string, span: number) =>
    CUT.rows.filter((row) =>
      row.bed === bed && row.span === span && row.tier === "webgpu"
      && row.state !== "inactive" && row.set !== "holdout" && row.T !== null
      && row.bandsUsed.join("/") === row.admitted.join("/"));

  it("reads the cut at the declared quantity, band rule and provenance", () => {
    expect(CUT.candidateII.quantity).toContain("slopeAWeb");
    expect(CUT.admittedBandRule.rule).toContain("outer edge in CSS px");
    // A cut taken with `--with-holdout`, or at `--at-documents any` over a
    // superseded generation, satisfies every other guard here and is not the
    // bed C1 is stated on (§5.162 §9, finding B-1).
    expect(CUT.atDocuments).toBe("shipped");
    expect(CUT.withHoldout).toBe(false);
    for (const bed of Object.keys(CONTRIBUTING_CELLS)) {
      for (const span of C1_SPANS) {
        const rows = readingsAt(bed, span);
        expect(rows.length, `${bed} at span ${span}`)
          .toBe(CONTRIBUTING_CELLS[bed]![span]!);
        for (const row of rows) {
          expect(row.admitted.join("/"), `${bed} at span ${span}`)
            .toBe(ADMITTED_BANDS[span]!.join("/"));
        }
      }
    }
  });

  for (const bed of Object.keys(CONTRIBUTING_CELLS)) {
    for (const span of C1_SPANS) {
      it(`${bed}, span ${span}: the exterior's shape is within ${C1_TOLERANCE}`, () => {
        const readings = readingsAt(bed, span).map((row) => row.T!);
        const statistic = upperMiddle(readings);
        // min, max and count beside the number, for the reason §5.162 §9's
        // finding N-1 gives: the per-cell maxima at span 96 are above the
        // bound and the clause is stated over the order statistic.
        expect(
          statistic,
          `${bed} span ${span}: ${readings.length} cells, `
          + `${Math.min(...readings).toFixed(5)}–${Math.max(...readings).toFixed(5)}`,
        ).toBeLessThanOrEqual(C1_TOLERANCE);
      });
    }
  }
});
```

`CONTRIBUTING_CELLS` is counted from the bed, per bed per span, on the admitted-band population
(`c1-forms.txt` §4). The composition, which is what the guard protects:

| bed | span | cal | val | probe | total | gated scenes |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1x light | 96 | 2 | 1 | 7 | 10 | `checkerboard__rrect-md__rest`, `photo__rrect-md__rest`, `photo__rrect-md__rest-tint-orange` |
| 1x light | 128 | 2 | 0 | 5 | 7 | `checkerboard__rrect-ml__rest`, `photo__rrect-ml__rest` |
| 1x light | 160 | 0 | 0 | 7 | 7 | all probe — the pitch ladder's alone |
| 2x light | 96 / 128 / 160 | 2 / 2 / 0 | 1 / 0 / 0 | 7 / 5 / 7 | 10 / 7 / 7 | as 1x light |
| 1x dark | 96 | 2 | 0 | 7 | 9 | `checkerboard__rrect-md__rest`, `photo__rrect-md__rest` |
| 1x dark | 128 | 0 | 0 | 5 | 5 | all probe |
| 1x dark | 160 | 0 | 0 | 7 | 7 | all probe |
| 2x dark | 96 / 128 / 160 | 2 / 0 / 0 | 0 | 7 / 5 / 7 | 9 / 5 / 7 | as 1x dark |

The **inactive pose** (32 / 44 / 96 / 160 on the standard beds) and the **two accessibility beds**
(44 and 96 only) are recorded and not bounded; so is the **CSS tier**, and so is `L`.

---

## 4. The stops, with today's readings

### B1, at the shipped bytes — the σ leaves may move only inside these windows

`shadow-law-at-shipped.txt` beside this file. The joint window per document is the intersection of
the ±5 % windows of every bed that document serves.

| document | span 96 | span 128 | span 160 | the law today | position |
| --- | --- | --- | --- | --- | --- |
| light `49490eb9ff7a` | [8.8966, 9.0193] | [12.6397, 13.7947] | [16.7033, 17.8198] | 8.9600 / 13.1648 / 17.3696 | INSIDE all three |
| dark `b5714a866288` | [8.9084, 9.3180] | [12.7458, 13.8499] | [16.7931, 18.3237] | 9.0400 / 13.3280 / 17.6160 | INSIDE all three |

The span-96 light window is ±0.685 % about its centre and is the binding one. **These are the
windows G1's σ leaves are bounded by** (Decision Log 1 (a)); `sigmaSpanRefPx` is held at 96 and the
knee at 44 by re-deriving `sigmaThinOffsetPx`.

### Candidate (i) — the wave's headline number, read at the verdict

Declared as a one-wave reading with the bound **"inside B1's own ±5 % window of the native σ"**,
which is the sentence W31 G1 found false. WebGPU tier, active, non-holdout, upper middle order
statistic (`stops.txt` §1):

| bed | span | native σ | rendered σ | σ_web − σ_nat | (i) | ±5 % window | today |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1x light | 96 | 8.796 | 12.570 | **+3.773** | 0.414 | [8.357, 9.236] | OUTSIDE |
| 1x light | 128 | 13.138 | 16.176 | **+3.038** | 0.249 | [12.481, 13.795] | OUTSIDE |
| 2x light | 96 | 9.370 | 12.833 | **+3.463** | 0.354 | [8.902, 9.839] | OUTSIDE |
| 2x light | 128 | 13.305 | 16.360 | **+3.055** | 0.240 | [12.640, 13.970] | OUTSIDE |
| 1x dark | 96 | 8.874 | 12.443 | **+3.568** | 0.389 | [8.431, 9.318] | OUTSIDE |
| 1x dark | 128 | 13.190 | 16.415 | **+3.224** | 0.240 | [12.531, 13.850] | OUTSIDE |
| 2x dark | 96 | 9.377 | 12.485 | **+3.108** | 0.317 | [8.908, 9.846] | OUTSIDE |
| 2x dark | 128 | 13.417 | 16.493 | **+3.076** | 0.224 | [12.746, 14.087] | OUTSIDE |

**Today: OUTSIDE on all eight, on every bed at both spans.** Span 160 is read beside them and is
not a verdict (0.150–0.176, +2.658 to +2.947 CSS px, OUTSIDE on all four) because the bed cannot see a span-160 exterior.

### B3 — the departure residual over the whole exterior

| population | today | bound | verdict |
| --- | ---: | ---: | --- |
| WebGPU, calibration + validation, six profiles | **0.00034** | ≤ 0.00035 | MET, by 3 % |
| WebGPU, every non-holdout row, probe included | 0.00177 | — | recorded |

**The window-restricted departure beside it**, which is what W32 clause 3 re-solves the six anchors
on. It is a different objective and the difference is large (`stops.txt` §2, WebGPU, active,
non-holdout, 1x light):

| span | whole `|Δ|` | window `|Δ|` | ratio | whole native | window native | whole web | window web |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 32 | 0.00015 | 0.00098 | 6.35 | 0.00064 | 0.00027 | 0.00046 | 0.00126 |
| 44 | 0.00023 | 0.00128 | 5.52 | 0.00085 | 0.00037 | 0.00084 | 0.00164 |
| 96 | 0.00044 | 0.00176 | 3.98 | 0.00373 | 0.00237 | 0.00326 | 0.00413 |
| 128 | 0.00076 | 0.00433 | 5.70 | 0.01286 | 0.01622 | 0.01210 | 0.02056 |
| 160 | 0.00142 | 0.00463 | 3.27 | 0.04117 | 0.04415 | 0.03961 | 0.04897 |

The restricted difference is **3.3 to 6.4 times** the whole-exterior one, and it changes sign
structure as well as size: over the whole exterior vitrea's departure is BELOW Apple's at every
thick span on 1x light, and over the window it is ABOVE. An anchor solve on one is not an anchor
solve on the other, which is why the charter has G1 measure the difference at its first round rather
than assume it.

### The thin regime, per cell — the table G1 compares against

The bar is **0.002044**, the MAX of `shadowAffineSlopeDeltaMax` over the 432 cells of
`results/2026-09-19-w29-g3b-shadow-recede/noise-bar.json`. The stop: on every active non-holdout
WebGPU cell at spans 32 and 44, neither inner band's `|Δa|` worse than today's by more than the bar,
and the order statistic per bed no worse than today's. The per-cell table is `stops.txt` §3; the
order statistic:

| bed | span | n | median `3-6` | max `3-6` | median `6-12` | max `6-12` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1x light | 32 | 9 | 0.01754 | 0.03433 | 0.01229 | 0.01995 |
| 1x light | 44 | 18 | 0.01865 | 0.02931 | 0.01494 | 0.02554 |
| 2x light | 32 | 9 | 0.01726 | 0.03449 | 0.01217 | 0.01953 |
| 2x light | 44 | 18 | 0.01873 | 0.02873 | 0.01490 | 0.02558 |
| 1x dark | 32 | 7 | 0.01016 | 0.01147 | 0.00739 | 0.01182 |
| 1x dark | 44 | 13 | 0.01061 | 0.01647 | 0.00936 | 0.01562 |
| 2x dark | 32 | 7 | 0.00970 | 0.01096 | 0.00744 | 0.01200 |
| 2x dark | 44 | 13 | 0.01037 | 0.01648 | 0.00929 | 0.01561 |

The per-cell medians are 4.7 to 9.2 times the bar and the maxima 5.4 to 17 times it, so a cell that moves by the bar has moved by 7–20 %
of its own reading: the stop is a real constraint and not a noise allowance.

### M1 and M2, and the rows expected unmoved

From W31 G4's committed `chroma-cut.json`, the cut `adopted-thresholds.test.ts` points at and
re-derives from `results/matrix.json` cell by cell (`stops.txt` §4):

| bed | n | median `R` | min | max | M1 | M2 median | M2 max | M2 |
| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | --- |
| 1x light | 9 | 1.03869 | 0.89065 | 1.51552 | MET | 0.00093 | 0.01317 | MET |
| 2x light | 9 | 1.04662 | 0.88905 | 1.44690 | MET | 0.00062 | 0.00740 | MET |
| 1x dark | 4 | 0.92339 | 0.82132 | 1.12912 | MET | 0.00327 | 0.00632 | MET |
| 2x dark | 4 | 1.07526 | 0.87475 | 1.18664 | MET | 0.00234 | 0.00396 | MET |

The three cells outside [0.60, 1.40] are M1's three excused misses, all `photo__rrect-sm` at span
32 and all named in `MISSED_27_ROWS` at adoption.

**The structure, tint and rim readings expected unmoved** — today's VALUES, per bed, WebGPU tier,
active, non-holdout (`stops.txt` §5). The BOUNDS live in `adopted-thresholds.test.ts` and are
deliberately not copied here, for that file's own reason:

| bed | `interiorStdDevWeb` | `interiorStdDevNative` | `tintChromaDeltaWeb` | `tintHueShiftWeb` | `rimPeakLuminanceWeb` | `rimFwhmWeb` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1x light | 0.05021 | 0.05752 | 0.16412 | −27.22088 | 0.02114 | 2.24694 |
| 2x light | 0.03354 | 0.05893 | 0.16450 | −27.26898 | 0.02541 | 3.71327 |
| 1x dark | 0.02921 | 0.03612 | 0.17439 | −26.88537 | 0.07585 | 1.16017 |
| 2x dark | 0.02748 | 0.03876 | 0.17474 | −27.05601 | 0.08863 | 1.35102 |

The tint readings are over the TINTED scenes only, because `tintChromaDeltaWeb` is zero by
construction on an untinted surface and a median over the whole bed would report the untinted
majority.

---

## 5. What the bed can identify, before a round is rendered

### Apple's own outset — §5.162 §9's finding N-10, answered

`model-fit.py` fits the renderer's own falloff model to the NATIVE per-band per-direction slopes.
The spread is Apple's effective outset; the one-sigma interval is the profile likelihood's, with the
spread held and σ, the offset and the amplitude re-fitted (`model-fit.txt` §4 and §5):

| bed | span | Apple's spread | 1σ interval | vitrea's 3.10 | Apple's offset | vitrea's 7.95 |
| --- | ---: | ---: | --- | --- | ---: | --- |
| 1x light | 44 | −0.013 | [0.00, 1.00] | excluded | 8.213 | +0.26 |
| 1x light | 96 | 0.552 | [0.75, 1.00] | excluded | 7.753 | −0.20 |
| 1x light | 128 | 0.717 | [0.25, 2.00] | excluded | 8.054 | +0.10 |
| 2x light | 96 | 0.419 | [0.00, 1.00] | excluded | 7.946 | −0.00 |
| 2x light | 128 | 2.816 | [3.00, 3.10] | INSIDE | 7.668 | −0.28 |
| 1x dark | 96 | 0.582 | [0.25, 1.00] | excluded | 7.740 | −0.21 |
| 1x dark | 128 | 0.487 | [0.00, 1.00] | excluded | 8.181 | +0.23 |
| 2x dark | 96 | −0.149 | [0.00, 1.00] | excluded | 7.930 | −0.02 |

**At spans 32, 44 and 96 Apple's outset reads 0.0–1.0 CSS px on every standard bed and vitrea's
3.10 is outside the one-sigma interval on all of them.** At span 128 the beds disagree — three
exclude 3.10 and 2x light does not — and at span 160 the interval spans 0.0–5.0 and excludes
nothing. **Apple's offset reads 7.65–8.22 at every span**, which is vitrea's 7.95 to within a
quarter of a pixel. So the exterior's +5.00 CSS px of isotropic extent excess and its agreeing
displacement are one finding with one cause, and the cause is the outset.

### The instrument's model against the shader — the error before any prior is trusted

The same fit on VITREA's render must return the shipped triple. What it returns instead is the
model's own bias:

| span | web spread (shipped 3.10) | web offset (shipped 7.95) | web σ against the law |
| ---: | --- | --- | --- |
| 32 | 3.15 – 3.41 | 7.63 – 7.88 | −0.35 to −0.55 |
| 44 | 3.10 – 3.41 | 7.97 – 8.02 | −0.34 to −0.49 |
| 96 | 2.82 – 3.41 | 7.72 – 7.98 | +0.11 to +0.92 |
| 128 | −3.26 to +7.11 | 7.56 – 8.04 | −2.17 to +3.93 |
| 160 | −2.55 to +8.62 | 8.29 – 8.93 | −2.60 to +5.38 |

**G1 may trust a native-side prior at spans 32, 44 and 96 and may not at 128 and 160.** The encoded
form — `(1 − A·Ψ)^2.4`, the shape the shader actually composites, since its alpha lives in the
canvas's compositing space and the affine pair is fitted in linear light — moves the residual by
less than 3 × 10⁻⁶ and is recorded as a negative result: the linear form is adequate on this bed.

### One-sidedness, and what it means for a fit

`above` reads exactly 0.00000 on every band on both `Δa` and `Δc`, on every standard and
accessibility bed, **at spans 32 AND 44** — and not because the two renders agree but because
neither draws anything there: both transmissions are exactly 1.000000 from 3 CSS px outward and both
extents are 0. So at the thin spans the offset is identified from BELOW only, and `offsetY` is
degenerate rather than merely uncertain: it is `(below − above) / 2` with `above` zero on both sides.

With σ and the spread held at each cell's two-sided values, `below`'s own offset reads 7.75–8.25 at
every span while `above`'s runs to 8.5–15.0 with an amplitude that trades off to 0.95–1.00 at span
96. **`below` is the direction that identifies the offset at every span, not only at the thin ones.**
The fit still separates a shift from a widening on `below`'s three bands — a shift moves the whole
profile outward where a widening flattens it — but the CHECK on that separation, the opposite side
moving the other way, is unavailable below span 96 and unreliable above it.

---

## 6. `MISSED_27_ROWS`, decomposed

**The list is not §5.162 §4's seven.** Two of those seven —
`photo__rrect-lg__rest :: oklabDeltaEP95` on the WebGPU tier, 1x and 2x dark — cleared at W31 G3
(0.21531 → 0.14655 and 0.21341 → 0.14505) and M1's three chroma rows joined at W31 G4. Today it is
**five + three**, which is what the charter's Grounding says.

`share` is the fraction of the cell's SSIM windows outside the silhouette; `reach` is the most the
metric could move if the exterior became perfect (`stops.txt` §7):

| tier | scene | bed | metric | gap | share | reach | `T` | verdict |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| dom | `checkerboard__glass-over-glass__rest` | 1x light | ssimMean | 0.00469 | 0.384 | 0.01325 | 0.01156 | **reachable if** the exterior closes 35 % of its own residual |
| dom | `checkerboard__rrect-lg__rest` | 1x light | ssimMean | 0.01577 | 0.249 | 0.01518 | 0.01142 | **NOT through the shadow** — a perfect exterior moves it 0.01518 against a 0.01577 gap |
| dom | `photo__rrect-lg__rest` | 1x dark | oklabDeltaEP95 | 0.02095 | 0.250 | — | 0.01532 | undecidable from the committed fields |
| dom | `photo__rrect-lg__rest` | 1x RT | ssimOutside | 0.00305 | — | 0.17305 | **0.05669** | **reachable** — the metric IS the exterior; 2 % of its residual |
| dom | `photo__rrect-lg__rest` | 2x dark | oklabDeltaEP95 | 0.00474 | 0.276 | — | 0.01571 | undecidable from the committed fields |
| texture | `photo__rrect-sm__{inactive,rest}` ×3 | light | chromaStructureRatioR | — | — | — | — | **not through the shadow** — `R` is the BODY's chroma over its structure |

Two readings. The `ssimOutside` row is scored entirely outside the silhouette and carries the
largest `T` of the whole list (0.05669, five times the next) — the correspondence an exterior
statistic should show, and the one row of the five the shadow can close on its own arithmetic.
`checkerboard__rrect-lg__rest :: ssimMean` is the opposite and is the sharper finding: **even a
perfect exterior leaves it missed**, by 0.00059, so a wave that claimed it through the shadow would
be claiming something the decomposition forbids. The two ΔE rows cannot be decided from the
committed fields at all — the axis carries no exterior-restricted ΔE — and that is a tracker entry,
not a verdict. **Nothing is claimed through this wave.**

---

## 7. The recede's declared reading

The inactive pose is its own population and is never pooled with the active. `T_dir` today, WebGPU,
non-holdout, over the admitted bands (`stops.txt` §6):

| bed | span | n | `all` | `above` | `below` | `left` | `right` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1x light | 44 | 10 | 0.00424 | 0.00000 | 0.01006 | 0.00838 | 0.00177 |
| 1x light | 96 | 9 | 0.00968 | 0.00222 | 0.01896 | 0.00831 | 0.00755 |
| 1x light | 160 | 3 | **0.09785** | 0.06094 | **0.13926** | 0.09437 | 0.09499 |
| 1x dark | 96 | 8 | 0.01216 | 0.00276 | 0.02426 | 0.01002 | 0.00979 |
| 1x dark | 160 | 3 | **0.13717** | 0.08606 | **0.19065** | 0.13417 | 0.13765 |

**And the reading that governs the whole of clause 4, which no wave had written down: on EVERY
inactive cell of this bed, Apple's receded window removes no light at all from 3 CSS px outward.**
The native render equals its backdrop to the axis's six written decimals in every admitted band on
100 of 100 non-holdout inactive WebGPU rows at every span and on both schemes; where the affine pair
is identified there it reads `a` = 1.000000 with `c` = 0; and `falloffSigmaNative` resolves on 0 of
them, because fewer than three rings past the edge ring clear the occlusion threshold. The receded
exterior Apple draws lives entirely in the `0-3` band, where the native departure reads 0.024–0.128
(`exterior-cut.txt` §12c) — a contour hairline, which this wave's Deferred list already names as a
rim term and not a shadow one.

Vitrea draws a full receded shadow out to 48 CSS px on every one of those cells, with `a` running
0.887 → 0.980 across the bands, because **the receded documents carry their active document's
anchors leaf for leaf** (light 0.1158 / 0.1827 / 0.26, dark 0.133 / 0.2263 / 0.3409) and
`outerShadowReachPx` therefore returns exactly the active reach at every span (`reach.txt`).

**What the recede's anchor solve is judged on, declared:** the inactive departure ratio per regime —
and on this bed the denominator is **zero** at every span and on every bed, so the ratio is not a
small number but an absent one. G1 solves the receded anchors toward a window-restricted departure
whose native side is 0.000000 and whose web side is 0.00112 at span 44, 0.00413–0.00530 at 96 and
0.0487–0.0685 at 160. That is a solve toward zero amplitude in the 3–48 window, not toward a lower
alpha on the same falloff, and if the solve returns an amplitude the shipped material cannot express
the finding is recorded rather than forced.

**The nine scenes Decision Log 1 (b) widens the read to**, with their fixtures confirmed present:
`checkerboard`, `impulse`, `light-solid` and `photo` on `rrect-ml` (span 128) and `impulse`,
`dark-solid`, `mid-dark-solid`, `light-solid`, `hc-text` and `mid-chroma-solid` on `rrect-lg` (span
160). Each of the ten names above is `<backdrop>__<component>__inactive`; the charter counts nine
because `impulse__rrect-ml__inactive` has no shadow to read. The fixture directories are checked per
profile by G1's read, which is where a missing fixture becomes a red rather than a silently short
population.

---

## 8. The rows expected unmoved

- **Every macOS 26.5 row**, and the freeze at 1,818 entries (X1).
- **The 34 renderer goldens**, byte-identical: they render `DEFAULT_MATERIAL_PROFILE` with no
  document seam and the default does not move.
- **M1 and M2** at the readings in §4, and the structure, tint and rim readings beside them: the
  three lengths and the anchors act outside the silhouette and reach no interior statistic.
- **The 1,107 gated-row pin** and the 27 bed's 230 / 726 count (X10); the widened ladder adds probe
  rows and never gated cells.
- **B2** (the thin regime's σ against the bed), which the knee held at 44 by construction preserves.
- **`samplingPaddingFor`'s advisory constant** (X8), which is the backdrop blur's 3σ and not the
  shadow's reach.

A fit that moves any of these is a warning and not a result (X3).

---

## 9. What this declaration does not say

No bound is adopted here and nothing is claimed. C1's form is the parent's ruling and its number is
the charter's rule, not this gate's. Candidate (i) is a one-wave reading, as §5.162 §5 left it. The
CSS tier is recorded and not bounded, and so is the inactive pose, span 130, `L`, and the two
accessibility beds above span 96. Apple's outset is a MEASUREMENT with an interval, on an instrument
whose own error is calibrated in §5 and is large at spans 128 and 160; it is not a value to be
transcribed into a document. And the recede's reading is a reading of the bed the fixtures give,
which at span 128 and 160 is three and seven probe cells and no gated cell at all.

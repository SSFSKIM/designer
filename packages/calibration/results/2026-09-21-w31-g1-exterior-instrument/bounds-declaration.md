# W31 G1 — the exterior clause, declared

**Gate: W31 G1, acceptance clause 4; contracts X1, X7, X11; W30's Deferred-at-close items 1 and 9
and Decision Log 5 (d). Claims §5.162.**

**Nothing here is adopted and nothing is fitted.** This gate takes no capture, edits no profile
document, adds no leaf, moves no row of `results/matrix.json` and writes no case into
`test/adopted-thresholds.test.ts`. What it declares is the clause **the wave that next moves the
shadow** reads its fit against, with the statistic, the bed, the exclusions, the bound and the row
shape all stated before that wave's first constant exists — which is the order §5.156 §5 set and
X4 requires. Every figure below is reproduced by
`python3 exterior-instrument.py` and its `--with-holdout` run, both committed beside this file.

---

## 1. Why a clause at all, and why this one

W30 claimed three rows through the shadow and the sealed read **refuted** them (Decision Log 5 (d),
§5.159 §7): the lever moved — the CSS group clip at span 160 went 33.05 → 45.79 CSS px — and the
rows moved by 0.0002 where they needed 0.016. The wave's own verdict names the reason: "SSIM over a
whole cell does not read a shadow's width", and the biggest movers of the whole read were
`falloffSigmaWeb`, by up to 30 CSS px, **on an axis no gated bound is stated over**. W30's Deferred
item 1 is therefore a metric that reads the exterior, and its item 9 is a second thing the eye found
and no metric reads: below a span-160 panel the ×8 difference carries visible LEVEL CONTOURS rather
than a featureless haze (§5.160 §6).

Those are two different quantities, so this gate computed one candidate for each and let the bed
choose.

| | candidate (i) — the width | candidate (ii) — the shape |
| --- | --- | --- |
| quantity | `\|falloffSigmaWeb − falloffSigmaNative\| / falloffSigmaNative`, both sides in CSS px | `T`, the band-width-weighted mean of `\|a_web − a_native\|` over the affine bands 3–48 CSS px, linear luminance |
| rows it reads | 258 of 602 | 490 of 602 |
| agrees with the eye (§5.160 §6) | **no — it reads the two cells the opposite way round** | **yes** |
| reads the two refuted `ssimMean` rows | **no: 0.000 and 0.027** | yes: 0.00790 and 0.00712 |
| moved by the σ law's lever | yes, and it reverses sign at spans 128–130 | yes, monotonically below 128 |
| **fate** | **not the clause.** Recorded as a diagnostic that points at an unfitted leaf (§5) | **the clause, declared at §3** |

---

## 2. The two statistics, defined

**Candidate (i).** Per cell, `|σ_web − σ_native| / σ_native`, with both sides divided by the row's
own scale — §5.154 §4's correction verbatim, the arithmetic `shadow-cut.py` already applies.
Excluded by W30 G0's rule `σ_css > span`, applied to **both** sides rather than only the native one
(a web fit can run away for the same reason and does: four cells read a web σ of 268–270 CSS px
under a 44 px caster). Ten exclusions, every one a probe row over `checkerboard-64` or `hc-text-7`,
each named in §0 of the output; **no gated cell is excluded at any span**, as in G0's own cut.

**Candidate (ii).** The shadow axis already carries, per cell, an affine map of the backdrop
`y = a·bg + c` fitted per band and per direction in linear light (W14 X7, `ShadowAffineSample`).
`a` is the transmission the exterior applies to its backdrop at that distance; the sequence of `a`
with distance **is** the falloff's shape, measured without assuming the profile is a blurred edge at
all. The one-number summary:

```
T = Σ_b  w_b · |a_web,b − a_native,b|   /   Σ_b  w_b
        over b ∈ {3-6, 6-12, 12-24, 24-48},   w_b ∈ {3, 6, 12, 24} CSS px
```

**Why weighted by band width.** The weights make `T` the discrete integral of the transmission error
over distance — the mean vertical gap between vitrea's falloff curve and Apple's across 3–48 CSS px
outside the declared contour, in the same unit as the curves themselves. A mean over four bands of
unequal reach would let a 3 px band and a 24 px one count the same; weighting by pixel COUNT instead
would hand the statistic to the outer bands' area, which is the same dilution that made whole-cell
SSIM blind to a shadow in the first place. `T` reduces to the departure quantity B3 already reads
when the two profiles differ by a constant, and separates from it exactly when they differ in SHAPE,
which is the residual §5.160 §6 names. The unit case
`test/w31-exterior-instrument.test.ts` pins the arithmetic on a scratch matrix with a known answer
and asserts that an unweighted mean of the same four differences is not what the reader prints.

**`L`, beside it and never summed in.** The same weighted mean over `|c_web − c_native|` — the lift,
the light the exterior ADDS, which a transmission cannot express. A shadow that removes less light
and a shadow that adds some are different findings (W14 X7), so they stay two numbers.

**The exclusions, all of them the axis's own.**

- a band the axis left unidentifiable — a flat backdrop makes `a` and `c` collinear at any sample
  count, and a band the frame ran out of has too few pixels (`ShadowAffineAbsence`). 32 rows carry
  no identified band in the window;
- the `0-3` band, out of `T` by the axis's own caveat: it holds the body's own edge, and vitrea's
  GPU capsule over-fills its declared contour by 3.5–4 CSS px where Apple's does by ≤ 1 (§5.62).
  It is tabled beside `T`, never dropped from the record. `0-6` is never used: it overlaps the first
  two bands and exists in the axis only so §5.60's and §5.62's published lifts can be read unbinned;
- a cell whose `backdropSupport` is below the axis's own `DEFAULT_MIN_BACKDROP_SUPPORT` of 0.1.
  80 rows: 48 over `dark-solid` (support 0.000) and 32 over `impulse` (0.004). The affine pair is
  reported there by design — a lift is measured cleanly over black, which is exactly where a ratio
  has no denominator — but a TRANSMISSION error over a backdrop with no light to remove is
  arithmetic on no information, and both classes read `T` exactly 0.000000 on every band. Left in,
  they would have made the bed look better than it is by 80 rows of the backdrop's own floor.

---

## 3. The clause

> **C1 — the exterior's shape at the thick spans.** On each of the four standard macOS 27 beds, at
> every thick span the bed carries a fittable cell at (96, 128, 160), the **upper middle order
> statistic of `T` over that bed's ACTIVE, non-holdout, WebGPU-tier cells at that span is
> ≤ 0.0045**, with the per-cell minimum, maximum and count reported beside it and the two
> accessibility beds and the CSS tier **recorded, not bounded**.

**The statistic.** `sorted[n // 2]`, the upper middle order statistic — `law-tables.txt`'s
convention, W30 G0's, and therefore B1's. Per bed and per span, never pooled across either.

**The bed, and the count guard.** The four standard beds, active pose, WebGPU tier, macOS 27 rows at
the shipped documents (`atAShippedDocument`), holdout dropped by construction, with the three
exclusions of §2. The populations today:

| span | 1x light | 2x light | 1x dark | 2x dark | RT | IC-coupled | composition |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 96 | 10 | 10 | 9 | 9 | 2 | 2 | calibration + validation + probe |
| 128 | 7 | 7 | 5 | 5 | 0 | 0 | one calibration cell on the light beds; the rest probe |
| 160 | 7 | 7 | 7 | 7 | 0 | 0 | **probe only** — the ladder W30 Decision Log 2 (a) granted |

Two readings follow and both bind the clause. **Span 160 is read on the pitch ladder alone**: every
non-ladder span-160 cell on this bed is holdout, exactly as §5.156 §2 records for the σ law. And
**the two accessibility beds carry no fittable cell above span 96**, so the clause is silent about
them there and says so rather than passing over nothing. The next wave writes those counts into its
case the way W30 G4's `CONTRIBUTING_BEDS` had to be written after the review found that a bed which
stopped contributing would have left the clause to the beds that remained (§5.160 §9).

**The bound, justified.** 0.0045 is the span-96 column rounded up past its own maximum: the four
standard beds read 0.00385, 0.00399, 0.00408 and 0.00413 there. So the clause says, in one number,
**"the exterior's shape under a 160 px panel is no worse than it is under a 96 px one today"**.

- *It can fail, and it fails today.* At span 128 the four beds read 0.00487–0.00532 (8–18 % over)
  and at span 160 they read 0.00733–0.00921 (63–105 % over). A clause a fit could not miss would
  certify nothing; this one is missed by every standard bed at two of its three spans before the
  first constant moves, which is the position B1 was in at its own declaration (the shipped σ was
  0.64× the native at span 160 against a ±5 % promise).
- *It is not missed at every span either.* Span 96 passes with 9–17 % headroom on all four beds, so
  the clause is a statement about the shape's dependence on span rather than a restatement of a
  residual the material misses everywhere.
- *It is far clear of the instrument's own resolution.* W29 G3b's `noise-bar.json` puts the
  native-pair spread on the worst affine band at **p95 0.000229** and **max 0.002044**, over 432
  cells of seven runs each. 0.0045 is **20× the p95 bar** and 2.2× the worst pair the bed ever
  produced against itself, and the per-span medians sit 224–779× above the per-cell bar. Neither
  meeting nor missing this clause can be a reading of the capture.
- *The bed's own floor says the number is reachable in kind.* At spans 32 and 44 — where §5.160 §6's
  eye calls the exterior right — the same statistic reads 0.00168–0.00339 on the same beds with the
  same instrument, which is what this material's exterior looks like when it agrees with Apple's.

**Fate: a ONE-WAVE READING at this gate.** Nothing is adopted here. The clause is the candidate
adopted row for the wave that next moves the shadow; that wave fits against it, reads it on the bed
above, and the parent decides adoption at its landing on the same argument W30's parent decided B1
on. Written now, before that wave's first constant exists, because that is the only order in which a
bound is a bound (X4).

**What it deliberately does not say.** No bound on the inactive pose (the receded documents are a
difference over the active ones and the inactive span-160 cells read 0.04531–0.06412, six to nine times the
active — W30's Deferred item 8, reported and not claimed). No bound at span 130 (every cell there is
holdout, as it is for the σ law). No bound on the CSS tier, which is recorded (it reads
0.00776 and 0.00789 at span 160 on the two beds that carry it, 0.00720–0.00924 at 128, and its one
coupled-contrast bed reads 0.0199–0.0411 at span 44, the largest single reading anywhere on the bed). No bound on `L`, which
is recorded at 0.00000–0.00131 over the whole active non-holdout WebGPU bed and carries no residual
worth a clause. No floor.

### The row shape, in `adopted-thresholds.test.ts`'s idiom

That file's convention is that **every case in it is live and green**, and a bound enters it in the
commit that adopts it — B1's own case was written at W30 G4, after it passed, not before. There is
no `it.skip` and no commented case anywhere in `test/`, so putting one there would be this gate
introducing a convention rather than following one, and it would also touch a file this wave's X11
does not give G1. The case therefore lives here, ready to be moved:

```ts
/**
 * **C1, adopted — the outer shadow's exterior SHAPE against the bed's own
 * native falloff** (declared W31 G1, claims §5.162 §3; fitted and met at
 * claims §5.NNN).
 *
 * **What it asserts.** The shadow axis fits an affine map of the backdrop,
 * `y = a·bg + c`, per band outside the declared contour. `a` is the
 * transmission the exterior applies at that distance, so the sequence of `a`
 * with distance is the falloff's shape — read without assuming the profile is
 * a blurred edge, and read strictly outside the contour, so the interior
 * cannot dilute it the way it diluted the two `ssimMean` rows W30 claimed
 * through this same lever and had refuted (§5.159 §7).
 *
 * **Why not the fitted σ.** W31 G1 computed that candidate beside this one and
 * it reads the bed backwards: 0.000 and 0.027 on the two refuted rows, against
 * 5.4 and 6.2 on the two cells §5.160 §6's eye called RIGHT. It reads a total
 * exterior width that the law's σ is only one term of, and its finding is
 * recorded at §5.162 §5 rather than gated.
 */
describe("W31 C1 — the shadow's exterior shape, adopted (claims §5.NNN)", () => {
  const C1_TOLERANCE = 0.0045;
  const C1_SPANS = [96, 128, 160] as const;

  /** W30 G0's statistic, and B1's: the upper middle order statistic. */
  const upperMiddle = (values: readonly number[]): number =>
    [...values].sort((a, b) => a - b)[Math.floor(values.length / 2)] ?? Number.NaN;

  /**
   * W31 G1's cut: one `T` per row, with the three exclusions §5.162 §2 names
   * already applied and the statistic named in the file's own `candidateII`
   * block, so a cut that had been re-stated at another quantity cannot let
   * this clause pass over nothing.
   */
  const CUT = readJson<{
    readonly candidateII: { readonly quantity: string };
    readonly rows: readonly {
      readonly bed: string; readonly tier: string; readonly set: string;
      readonly state: string; readonly span: number | null; readonly T: number | null;
    }[];
  }>(resolve(PACKAGE_ROOT, "results", "2026-09-21-w31-g1-exterior-instrument",
             "exterior-instrument.json"));

  /**
   * How many cells each standard bed contributes at each asserted span —
   * counted, not merely required to be non-zero, for the reason W30 G4's
   * review gave `CONTRIBUTING_BEDS` (§5.160 §9): a bed that stopped
   * contributing would leave the clause to the beds that remain instead of
   * failing. Span 160's cells are the pitch ladder's alone.
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
      && row.state !== "inactive" && row.set !== "holdout" && row.T !== null);

  it("reads the cut at the quantity §5.162 §2 declared, over every standard bed", () => {
    expect(CUT.candidateII.quantity).toContain("slopeAWeb");
    for (const bed of Object.keys(CONTRIBUTING_CELLS)) {
      for (const span of C1_SPANS) {
        expect(readingsAt(bed, span).length, `${bed} at span ${span}`)
          .toBe(CONTRIBUTING_CELLS[bed]![span]!);
      }
    }
  });

  for (const bed of Object.keys(CONTRIBUTING_CELLS)) {
    it(`${bed}: the exterior's shape error is within ${C1_TOLERANCE} at spans 96, 128 and 160`, () => {
      for (const span of C1_SPANS) {
        const cells = readingsAt(bed, span);
        const T = upperMiddle(cells.map((row) => row.T!));
        expect(T, `${bed} at span ${span}: T = ${T.toFixed(5)} over ${cells.length} cells`)
          .toBeLessThanOrEqual(C1_TOLERANCE);
      }
    });
  }
});
```

---

## 4. Candidate (i) beside B1, and what the divergence means — stated before the clause

B1 is **green** on every bed at every one of its spans, and it is green by margins of 0.04–4.38 %
against a ±5 % promise whose joint window on the light document is ±0.685 %. On the same cells,
candidate (i) reads the rendered σ **15–41 % wider than the native** on the WebGPU tier at spans
96–160, and the sign is one-way: **123 of 150** rows that resolve both sides read the rendered σ
wider. Both statements are true of the same material on the same day, and the charter asks what the
divergence means before a clause is declared. It is not ambiguous:

**The two sides of B1 are not the same quantity.** B1's left-hand side is the DOCUMENT's blur leaf,
`σ(span) = sigmaPx + max(sigmaThinOffsetPx, sigmaSlopePerSpan · (span − sigmaSpanRefPx))`,
evaluated in closed form. Its right-hand side is the INSTRUMENT's fit of Apple's render, which
absorbs whatever else Apple's shadow is besides a blur. Candidate (i)'s two sides are the same
instrument applied to both renders. So B1 says "the law's blur agrees with a fit of Apple's shadow",
and candidate (i) says "a fit of vitrea's shadow does not". **The law is right and the law is not
the whole of what vitrea draws** — which is the first of the two readings the charter names, and the
bed says so with a number rather than by elimination:

| bed | tier | span | native σ | law σ | law err (B1) | rendered σ | **σ_web − σ_nat** |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1x light | webgpu | 96 | 8.796 | 8.960 | +1.86 % | 12.570 | **+3.77** |
| 1x light | webgpu | 128 | 13.138 | 13.165 | +0.21 % | 16.176 | **+3.04** |
| 1x light | webgpu | 160 | 17.317 | 17.370 | +0.30 % | 20.264 | **+2.95** |
| 1x dark | webgpu | 96 | 8.874 | 9.040 | +1.87 % | 12.443 | **+3.57** |
| 1x dark | webgpu | 128 | 13.190 | 13.328 | +1.04 % | 16.415 | **+3.22** |
| 1x dark | webgpu | 160 | 17.456 | 17.616 | +0.92 % | 20.208 | **+2.75** |

The gap is **additive and nearly constant** — +2.66 to +3.77 CSS px at every thick span on every
standard bed, where a proportional error would shrink with σ. The material's own model says what a
constant additive width is: `material.ts` describes the shadow as *"the component's OWN rounded
silhouette, outset by `spreadPx`, translated down by `offsetPx`, blurred by a Gaussian of standard
deviation `sigmaPx`"*, and the shipped `spreadPx` is **3.10 CSS px**. A blurred-edge fit pinned at
the declared contour reads an outset silhouette as extra σ, which is the size and the sign the bed
shows. **`spreadPx` has never been fitted on the macOS 27 bed**: it is inherited from the macOS 26.5
default and no wave has touched it, and B1 — which reads the blur leaf alone — is structurally
incapable of seeing it.

Below the knee the same arithmetic runs away: at span 44 the law asks for σ 2.13 and the instrument
reads 12.15–15.63 off the render, because `offsetPx` 7.95 and `spreadPx` 3.10 are then several times
the blur and an isotropic ring-mean profile pooled over four directions is mostly reading the
displacement. The web σ at span 44 is identical on a cell and its `-tint-orange` and `-tint-blue`
siblings to five decimals (12.849 on `checkerboard__capsule-button`), so the web fit is stable — it
is simply not measuring the law's σ there.

**Neither statement is withdrawn and neither is rewritten.** B1 stands as adopted; the reading
recorded beside it is that it bounds the document's blur leaf and not the exterior vitrea draws, and
that the next shadow wave should expect a green B1 and a wide exterior to be consistent.

---

## 5. What candidate (i) is kept for, since it is not the clause

It is the only statistic on the bed that points at `spreadPx` and `offsetPx` — two leaves the macOS
27 material inherited unfitted — and it does so with a number (+2.66 to +3.77 CSS px, one-way on 123
of 150 rows) rather than by inference. It is recorded at §5.162 §5 and carried into W31's Deferred
as the shape of a second piece of work: **a joint fit of the shadow's three lengths against the
exterior, instead of the blur alone.** It is not gated, for three reasons the bed produced:

1. **it anti-correlates with the eye.** On §5.160 §6's own four sheet cells it reads 5.37 and 6.22
   on the two the eye called RIGHT and 0.151 and 0.134 on the two it called WRONG — a factor of 40
   the wrong way;
2. **it is blind on the rows the clause exists for.** `checkerboard__rrect-lg__rest :: ssimMean`,
   the largest of W30's three refuted claims, reads **0.000** — σ native 17.30 against σ web 17.29
   — while the row misses its bound by 0.016;
3. **its own lever reverses.** Under the σ law it improved at spans 32–96 (6.25 → 4.40, 8.45 → 7.73,
   0.563 → 0.390) and got 2.5–3.8× WORSE at 128 and 130 (0.101 → 0.251, 0.059 → 0.226). A statistic
   that a wave's declared improvement moves in both directions at once is not one a later wave can
   be judged on until the quantity it reads is separated.

---

## 6. The verdicts this gate records, and where they go

- **§5.162 §1** — the two statistics, per span class, scheme, tier and scale, on the gated sets, the
  probe ladder and the holdout apart.
- **§5.162 §2** — candidate (i) beside B1, and the divergence of §4 above.
- **§5.162 §3** — the clause, this document's §3.
- **§5.162 §4** — the seven missed rows' readings under both statistics.
- **§5.162 §5** — candidate (i)'s finding, and the Deferred item it becomes.
- Charter Tracking Map row and a Revision Note; `freeze.py verify` **1,818 entries intact** at this
  gate's open and at its close.

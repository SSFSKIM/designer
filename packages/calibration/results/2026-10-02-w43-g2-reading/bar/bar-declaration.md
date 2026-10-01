# The bar, declared — W43 G2 stage one, before any 0.25-against-0.5 pair is read (2026-10-02)

Charter `docs/doperpowers/specs/2026-10-01-w43-glass-0-25-generation.md` v1.2, clause 7, Design "The
native delta and the refit", X3 and X43; claims §5.200. This file is hashed and its SHA-256 is
committed in `bar-declaration.sha256`, in a commit that precedes the first read of a 0.25 fixture
against a 0.5 one. **It is never edited.** A correction is a new file beside it, naming this one.

At the moment of hashing, no tool of this child has read a 0.25 cell against a 0.5 cell. The 0.25
pixels have been read twice, each against its own runs only: by the native delta's `bar` command
(§2) and by `raw-states.py`, by bytes. The 0.5 pixels have been read against themselves (§6 (c)) and
against the G1a bridge captures at 0.5 (§6 (b)). At the child's opening the 26.5 freeze reads
1,818 and the X41 manifest 911 (`opening-checks.txt`).

## 1. The instrument: W29 G2's driver, re-keyed to the pair

`packages/calibration/cli/slider-delta.ts` (new) reads one slider position against another. It
imports from the native delta everything that turns pixels into numbers: `readCapture` and
`pairMetrics` (the 49 metrics, W29 G2's 32 and W29 G3b's 17 shadow metrics), `captureReadings` (the
13 signed per-capture readings the recede is built from) and `contextFor` (declared region, declared
box, backdrop). So the bar and the delta are one function of a pair of captures, which is the
reason W29 G2's declaration gives for porting the rim readers. `cli/native-delta.ts` gains exports
and a run-as-script guard and nothing else; `cli/native-delta-metrics.ts` gains
`sliderCounterpartKey`, which moves the `-glass<amount>` token and refuses a key with none or at
the same position. `test/slider-delta.test.ts` checks the pairing against `scenes.json` (every
`-glass0.25` key onto a `-glass0.5` key with the identical scene list) and the bar's arithmetic.

- **The pair.** The `-glass0.5` fixture is the reference side: its silhouette masks the material
  rows and defines the SSIM windows, because it is the bed the shipped generation was fitted
  against. Every signed reading is `[0.5, 0.25]`, so subject − reference is Apple's change when
  the slider moves from 0.5 to 0.25.
- **The recede** is its own row set, `(0.25 inactive − 0.25 active) − (0.5 inactive − 0.5 active)`,
  so the slider's change and the recede are never read as each other.
- **The radial difference profile** is carried beside the metrics: where the two captures differ,
  by band of signed distance from the declared contour (deep body ≤ −6 CSS px, shoulder, edge
  (−2, 0], near exterior (0, 2], exterior (2, 12], far). It needs no silhouette and no reader. It is
  descriptive and never a verdict.

## 2. The 0.25 side's run-to-run distribution: degenerate at zero

`npx tsx cli/native-delta.ts bar --runs ~/vitrea-w43/g1a-run --passes
bed-0.25-1x-active,bed-0.25-1x-receded,bed-0.25-2x-active,bed-0.25-2x-receded` wrote
`noise-bar-0.25.json` (`bar-run.txt`): the native delta's own construction, per cell and per metric
the distribution over all 21 unordered pairs of the cell's seven admitted runs (never a quarantine).

- **562 cells, seven runs each, 21 run pairs each.** Over the 49 metrics that is **22,427
  cell-metric distributions**, and every one reads min = median = p95 = max = **0**. A metric is
  carried wherever it is measurable: 562 cells on the whole-cell rows, 548 on the silhouette and
  material rows, 540 on the two declared-box readers, fewer on the conditional ones (the transfer,
  the FWHM, the highlight ratio and the normalised shadow rows). The rest are composites or empty
  silhouettes: absent, never zero.
- **All 13 signed capture readings** (the recede's inputs) have a run-to-run spread of exactly 0 on
  every cell that carries them.
- **`bedMinimumNonZeroBar` is empty:** the bed resolves no non-zero spread on any metric.
- The run began at 07:46 local time, before `cli/native-delta.ts` gained its exports and guard
  (§1); the bar was computed by that file's unchanged logic.

**Said plainly: the 0.25 side's distribution is degenerate at zero.** Every one of the 562 cells
reproduced its frame byte for byte in all seven runs (`raw-states.txt`: 562 of 562 unanimous by file
SHA-256, each the published fixture), so every pairwise distance is exactly 0 on every metric, and
the bed resolves no non-zero spread from which a fallback could be taken: under the native delta's
own rule its bar is `bed-zero`, exactly 0, everywhere. This says the sitting's seven runs agreed. It
does not say the 0.25 material has no second state: seven runs miss a one-in-six minority state with
probability (5/6)^7 ≈ 0.28 per cell.

## 3. The 0.5 side's W29 bar, recorded beside it

The 0.5 fixtures were plurality-published from W29 G1's seven runs through the original bundle
(2026-09-18/19), whose bed carried two-state cells. Their run-to-run bar is committed: W29 G3b's
`results/2026-09-19-w29-g3b-shadow-recede/noise-bar.json` (SHA-256 `2f31bbf8…80f5`), all 49
metrics over 624 cells, the same construction from the same raw runs, which reproduces W29 G2's
32-metric bar reading for reading (its `bar-reproduction.txt`). It is read here on the 562 standard
cells the 0.25 bed mirrors, with its `bedMinimumNonZeroBar` as committed (over its whole 624-cell
bed: the bar W29's own verdicts were judged against).

On the 562 standard cells, **103 spread at all on the whole-cell rows and 459 are unanimous**. The
103 are exactly the cells that carry two raw states by bytes (`raw-states.txt`; no cell carried
three), as W29 G2's own two-constructions check found on its bed: 94 were voted and 9
frequency-settled at W29's publication (§5.150), and every published fixture is one of its cell's
own run states. On each law's primary metric (`bar-sides.txt` has all 49 and the 13 readings):

| metric | cells with their own spread | median own spread | max own spread | W29's bed minimum |
| --- | ---: | ---: | ---: | ---: |
| `silhouetteIoUComplement` | 12 / 548 | 2.28e-5 | 9.14e-5 | 5.79e-6 |
| `contourDistanceMeanPx` | 12 / 548 | 1.25e-3 px | 4.90e-3 px | 5.88e-4 px |
| `bodyLevelDelta` | 76 / 540 | 4.81e-7 | 1.15e-5 | 5.97e-10 |
| `transferSlopeDelta` | 74 / 376 | 2.61e-6 | 6.33e-5 | 4.31e-8 |
| `interiorStdDevDelta` | 96 / 548 | 2.47e-6 | 3.20e-5 | 3.02e-9 |
| `tintChromaDelta` | 96 / 548 | 1.59e-7 | 1.06e-5 | 5.56e-16 |
| `rimContourDeltaMax` | 78 / 540 | 1.12e-5 | 4.10e-3 | 9.24e-9 |
| `highlightBinDeltaMax` | 82 / 540 | 2.67e-4 | 5.28e-3 | 9.45e-9 |
| `shadowProfileRmsDelta` | 83 / 450 | 8.71e-6 | 2.64e-4 | 4.39e-8 |
| `tintDeltaLDelta` | 96 / 548 | 7.64e-7 | 3.09e-5 | 1.18e-8 |
| recede input `bodyLevel` (spread) | 76 / 540 | 4.81e-7 | 1.15e-5 | 5.97e-10 |

Ten metrics have no spread anywhere in W29's bed and take a bar of exactly zero on both sides:
`contourDistanceP95Px`, `oklabDeltaEP95`, `rimPeakDepthDeltaPx`, `shadowStrengthPeakDistanceDeltaPx`,
the four `shadowExtent…DeltaPx` and the two `shadowOffset…DeltaPx`. A "moved" there means non-zero.
Levels are linear luminance; the shadow and rim rows are in their own units (`bar-declaration.md` of
W29 G2 and G3b).

**Where the verdict bar comes from.** On every cell and metric that both sides carry, the 0.5 side
sets it (its own spread on the cells above, W29's bed minimum on the rest, zero on the ten), because
the 0.25 side is zero everywhere. The 0.25 side alone carries a reading on 51 cell-metrics
(`rimFwhmDeltaPx` 34, `highlightRatioDelta` 17), where no pair of the 0.5 cell's runs resolves it;
the pair's own metric needs the 0.5 fixture to resolve it, so none of those 51 can be judged.

## 4. The verdict bar, per metric: the larger of the two sides

> **Per cell c and metric m, the verdict bar is max(B₀.₂₅(c, m), B₀.₅(c, m)),** where each side's B is
> the native delta's three-level rule over that side's own bar file: the cell's own pairwise max over
> its seven runs, else that bed's smallest non-zero pairwise max, else exactly zero. **A cell MOVED on
> a metric when the pair's value exceeds it.** `barSource` names the side and the level.
>
> **The recede's readings** take, per side, the sum of its two cells' run-to-run spreads, each with
> that side's bed-minimum fallback (W29 G2's corrected rule, §5.151 §12), and the verdict bar is the
> larger side's.

**Why the larger of the two.** A 0.25-against-0.5 pair takes one capture from each side, and each
published fixture is one draw from its side's run states. A cross-position difference no larger
than one side's own run-to-run spread could be produced by recapturing that side alone, so it is not
evidence that the slider changed anything. The pair's noise is therefore at least the larger
side's. For two independent draws the bound would be the sum, and here the 0.25 side is identically
zero, so the larger and the sum are the same number: the clause's rule loses nothing on this bed.

**Why not the 0.25 side alone,** which is what the clause names first. Alone it would judge every
cell at a bar of exactly zero, the sharpest instrument there is, on pairs whose other side is known
to vary on 103 cells. The clause's own reasoning, "the pair's noise is the larger of its two sides",
is what this rule implements.

**What a "moved" means here.** On the 459 cells unanimous on both sides the bar is W29's bed minimum,
of order 10⁻¹⁶ to 10⁻⁵ on the level and material rows (§3), or exactly zero on the metrics W29's bed
never resolved. A "moved" there means "differs on that metric at all". So every verdict is printed
with its magnitudes, and the Decision Log 7 draft ranks the laws by magnitude, never by count.

**What the bar does not contain, stated once and carried on every reading:**
- **The bundle term.** The 0.25 bed came through the W39 side bundle and the 0.5 bed through the
  original. Clause 3's bridges measure that term on the cells they cover (G2 (a)), and §6 (b) reads
  what this bar would call "moved" on them.
- **The machine and night term** between 2026-09-18/19 and 2026-10-01: the same bridges.
- **A 0.25-side spread below seven runs' resolution** (§2).

## 5. The verdict per law: the rule, in `verdicts.py`

`verdicts.py` (pinned in §8) is the rule; this is its prose.

1. A law is read on a declared **primary** metric over a declared population, in each pose.
2. **Every `rrect-lg` cell is held out as its own stratum.** Memo F reads the rrect-lg backdrop
   capture scale at 0.5 for x = 0.25 against 0.25 for x = 0.5, in all four endpoints (§5.198 §4 and
   §7): a declared-tree step, which the native delta must read as such and not as a material
   change. The stratum's counts are printed beside each law and never set its verdict.
3. **MOVED** when the primary moved on at least half the measured cells in at least one pose.
   **NOT MOVED** when it moved on no cell in either pose: the bar separates nothing, and that is the
   finding (clause 7's stop: such a law is not refit). **MINORITY** otherwise: the law did not move as
   a law, and the cells that did are named.
4. Each verdict is printed with its magnitudes: moved / measured, the median and p90 |Δ|, the
   median signed change with up / down counts, the median Δ/bar.
5. A law's secondary metrics are printed beside it and never change its verdict.
6. **The bundle null beside each verdict** (§6 (b)): each law's primary is printed beside the
   largest value the canonical bridge null reached on it, and moved cells no larger are counted as
   "within the null". It never changes a verdict.
7. **Attribution reads, descriptive and never a verdict:**
   - *the geometry:* the healthy population (both silhouettes within 2× of each other, §5.151 §4),
     with its median magnitudes in pixels, the unhealthy cells by backdrop, and the implied corner
     radius per component on both sides;
   - *the rim and the highlight:* the uniform-backdrop subset, where the body's change is uniform,
     so a reading taken relative to the body (both readers subtract it) is the edge's own change;
   - *every law:* the radial difference profile's bands.

| law | primary | secondary | population |
| --- | --- | --- | --- |
| silhouette | `silhouetteIoUComplement` | `silhouetteAreaDeltaPx` | every cell |
| contour | `contourDistanceMeanPx` | `contourDistanceP95Px`, `cornerCurvatureDeltaPerPx` | every cell |
| interior level | `bodyLevelDelta` (mask-free) | `interiorMeanDelta` | every cell |
| tone by backdrop | `transferSlopeDelta` | `transferOffsetDelta` | cells whose backdrop identifies a transfer |
| scatter | `interiorStdDevDelta` | — | structured backdrops (`checkerboard*`, `hc-text*`, `photo`, `impulse`) |
| chroma | `tintChromaDelta` | — | untinted cells: the body's own chroma, which `bodyChromaRetention` carries |
| rim band | `rimContourDeltaMax` | `rimLocalDeltaMax`, `rimRow0DeltaMax`, `rimPeakDelta`, `rimPeakDepthDeltaPx`, `rimFwhmDeltaPx` | single-box cells |
| highlight | `highlightBinDeltaMax` | `highlightBinDeltaMean`, `highlightIntegralDeltaMax`, `highlightRatioDelta`, `highlightPeakAngleDeltaDeg` | single-box cells |
| exterior shadow | `shadowProfileRmsDelta` | the other sixteen shadow metrics | cells whose exterior was walked |
| tint shade | `tintDeltaLDelta` | `tintChromaDelta`, `tintHueShiftDeltaDeg` | tinted cells |
| the recede | recede `bodyLevel` | recede `rimContourMean`, `rimLocalMean`, `highlightPeak`, `highlightFloor`, `highlightRatio`, `interiorMean`, `interiorStdDev`, `tintDeltaL`, `tintChroma` | recede rows |

The whole-cell rows (SSIM, ΔE, edge-weighted) are printed as context and carry no verdict.

**Memo F's pointers, written before the read (X38).** At 0.25 against 0.5 the declared tree moves
w (0.5 → 0.25), λ (0.9 → 0.7875 in both schemes), the light face fill's alpha (0.2 → 0.1), the dark
MaxLuma cap at s ≥ 80, and the rrect-lg capture scale. It moves nothing else: not the shapes, the
SDF, the margin, the refraction, the bleed, the shadows, the ring shadow or the highlight (§5.198
§4). So the pointers say: interior level, tone by backdrop, scatter and chroma move; the geometry,
the exterior shadow and the highlight's own inputs do not. The rim and highlight readers read
relative to the body and so may move with it, which is what the uniform-backdrop read separates. The
tint shade and the recede have no pointer of their own. The pixels referee every one of these.

## 6. The rule and the bar, rehearsed before the hash

Every file below is under `rehearsal/`.

**(a) The rule on a delta whose verdicts are on record:** W29 G3b's 26.5-against-27 rows, standard
profiles (557 rows, 104 in the rrect-lg stratum), `verdicts-w29-g3b-standard.txt`. Every material
law reads MOVED, as §5.151 and §5.154 recorded. **Silhouette and contour read MOVED too**:
`silhouetteIoUComplement` moved on 181 of 265 active cells at a median of 3.1e-4, and the contour on
the same cells at a median of 0.011 px. W29 called the geometry unmoved, on magnitude (§5.151 §3). On
the healthy population the rule's attribution read reproduces W29's own numbers: a median IoU
complement of 3.3e-4 and the capsule's implied radius 17.92 → 17.95 px. So **a geometry verdict of
MOVED by the bar is expected wherever the level moves at the edge**. The shape question is answered by
the attribution read, never by the count, and G3 has no geometry leaf to refit in either case.

**(b) The bridge null, 144 pairs** (`rehearse.txt`, `verdicts-null.txt`): G1a's 0.5 captures through
the side bundle against their 0.5 fixtures. Their slider change is zero, so every "moved" here is the
bar misreading the bundle, the night or the protocol.
- **Canonical cells, the bed's own protocol: 72 pairs, 5 read moved, on 2 cells.**
  `1x-light/dark-solid__capsule-button__rest` (all three runs, on 15 metrics) is a side-bundle state
  that is not among W29's seven runs of that cell. `2x-dark/checkerboard__capsule-button__rest-tint-orange`
  (runs 2–3, on 29 metrics) is the same: a state the original bundle never produced at W29. The
  largest values are small: `bodyLevelDelta` 2.4e-9, `interiorMeanDelta` 8.1e-6, `rimContourDeltaMax`
  6.5e-5, `highlightBinDeltaMax` 1.9e-4, `shadowProfileRmsDelta` 4.5e-6, `tintDeltaLDelta` 5.9e-6 and
  `oklabDeltaEMean` 1.1e-6.
- **The W42 sentinels, long protocol against the normal-protocol fixtures: 72 pairs, 16 read moved,
  on 3 cells:** the checker-64 on rrect-lg at 1x in both schemes (an rrect-lg stratum cell) and the 2x
  light impulse on rrect-md. That is the protocol term §5.198 §6 recorded, at most `bodyLevelDelta`
  3.0e-6, `rimContourDeltaMax` 1.3e-3 and `highlightBinDeltaMax` 4.3e-3.
- **Under the law rule, no law reads MOVED on the null.** Silhouette and contour read NOT MOVED, and
  the rest read MINORITY, on those cells alone (the largest share is the chroma row's 9 of 30
  active pairs, 0.30, below the rule's one half).

So, declared from this: **the per-cell bar does not contain the bundle term and misreads it on a few
cells; the law rule cannot turn that into MOVED.** Every law's primary metric is printed beside the
canonical null's largest value on it, and moved cells no larger are counted as "within the null"
(`verdicts.py --null`, §5 item 6). A MINORITY verdict whose moved cells all sit within the null is
not separated from the bundle term, and is read that way.

**(c) The positive control, 103 pairs** (`rehearse.txt`, `verdicts-positive-control.txt`): each of
W29's minority states against its published fixture. None reads moved on any metric, and the
largest value/bar ratio is exactly 1.0, because each pair is its cell's own maximum. Every law reads
NOT MOVED. The bar holds where it must by construction.

## 7. What is read after the hash, in order

1. `slider-delta delta` over every canonical 0.25 cell with its 0.5 counterpart, both scales, both
   schemes, both poses: `delta/slider-delta.json` and `delta/slider-recede-delta.json`.
2. `verdicts.py` over them: the verdict per law.
3. The eye sheets per profile at both scales.
4. G2 (f), S1 on the perfect-endpoint null, which reads Apple's change in interior level from the
   same rows and the barring of §4, and the shipped 0.5 render's error from the current generation.
5. The Decision Log 7 draft.

Nothing in this file, in `verdicts.py` or in the instrument changes after the first of these.

## 8. Pins (SHA-256)

Paths relative to `packages/calibration/`.

```
0e953890268dde5e3c63a10f51913fbefa14d8b5052560e58d7231990898221e  cli/slider-delta.ts
c767c1af73d18d039ec0e135f7382a5f07499adef357632c6578614f7fec655d  cli/native-delta.ts
e8e511c8647c8c978559dd93859409604a1673e7d02838133df21fdd65082224  cli/native-delta-metrics.ts
6cc8b69182ea3c9014538fb3140f98c2f73d2f9af2aa8f2a9e8cd0294b022d46  cli/native-delta-readers.ts
74fb6ac73666eb01eeef5b52f2ddcca8dbadbd2262efa74cd4652122682e48c8  test/slider-delta.test.ts
1400aa0003bfdb757ead42e88f15ec6771ef7a5a9d26b5e425eb3d2818e1b795  results/2026-10-02-w43-g2-reading/bar/verdicts.py
7817cf7a4dd9d88aa15779ec87d111a726f4462064aa3c886c9c1d2b90761532  results/2026-10-02-w43-g2-reading/bar/raw-states.py
287cb463dfb0f96a4d261cc0b234545c3c785fb17b6757473baedfe50dad3779  results/2026-10-02-w43-g2-reading/bar/bar-sides.py
45ce79908c46eefcc63851244a07aa37b3a5442281b8d9b021fc149e4083f3e6  results/2026-10-02-w43-g2-reading/bar/null-pairs.py
a573a5ba1812622baa781cedabee884eb354f9a9834d8f78b031a0589b027333  results/2026-10-02-w43-g2-reading/bar/w29-state-pairs.py
544cc390d2599d753b1fbfa17ee5c08d74477bb19d2b1e248924d3c327a2deb8  results/2026-10-02-w43-g2-reading/bar/rehearse.py
f72de0b433f417249b07202affda97e3668ee3338f23eec6f0a333f3db13ede8  results/2026-10-02-w43-g2-reading/bar/noise-bar-0.25.json
2f31bbf82b09eef3843573fd588a8da97687f053d73ff94c0a8b11bcbe5e80f5  results/2026-09-19-w29-g3b-shadow-recede/noise-bar.json
f21eff9d97b6feebfb25acbe28a9d323f2c0cb80995a57df34f6a640fb12d838  results/2026-10-02-w43-g2-reading/bar/raw-states.json
1a659d8cd6daf357fd4c4802df625fa7e0de518072657ee597514b14f17bd2ac  results/2026-10-02-w43-g2-reading/bar/bar-sides.json
ca2f1fb438cace992a8f0b2997c675952f27bb2892fb4e8e320f61ab5dd46fac  results/2026-10-02-w43-g2-reading/bar/rehearsal/null-pairs.json
964688ae26f0e8b5f70fa5086a06cd019436ace39138036a7efb6d01fb4ede30  results/2026-10-02-w43-g2-reading/bar/rehearsal/null-pairs-measured.json
da6a44ab1c80de0025a2eeadeef67585758cef7f4db7fd67beb412809d304a7b  results/2026-10-02-w43-g2-reading/bar/rehearsal/w29-state-pairs.json
e7f7517a64a6d1a670ee8b6dd12c78230cc1d29ffb1eba448297800888278712  results/2026-10-02-w43-g2-reading/bar/rehearsal/w29-state-pairs-measured.json
bed39cddd24c47b4ecc05d147e034b9ae96e4a1ccdcd301c3a65173123fca539  results/2026-10-02-w43-g2-reading/bar/rehearsal/rehearse.txt
e3a167435b3fcce6d96c2dcdb10d1246a9451ebf8e7518cb621f8f9eeb9c86fe  results/2026-10-02-w43-g2-reading/bar/rehearsal/verdicts-null.txt
d19554236ac9fd57bc71e4d61542c40510c5fa79f29697f6e544319cf6f58a4f  results/2026-10-02-w43-g2-reading/bar/rehearsal/verdicts-positive-control.txt
d121a064fa88b820bbefc554edda2fc17e9aabf237d5b4621ef8da86bb3fabb8  results/2026-10-02-w43-g2-reading/bar/rehearsal/verdicts-w29-g3b-standard.txt
```

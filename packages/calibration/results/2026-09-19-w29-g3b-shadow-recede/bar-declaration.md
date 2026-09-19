# The shadow axis's noise bar, declared — W29 G3b, before any 26.5 pair is read

W29 Decision Log 6 (a), ruled by the user 2026-09-19; contracts X3 and X5; claims §5.154. This
file and `noise-bar.json` are committed **before** the commit that reads a single 26.5 fixture
against a 27 one on the shadow axis. Nothing in this gate has yet compared the two beds.

## What this declaration adds, and what it does not touch

G2 declared the bar for thirty-two metrics
(`results/2026-09-19-w29-g2-native-delta/bar-declaration.md`) and read them. It did **not** read
the shadow — §5.151 §2 lists the laws it read and the shadow is not among them — which is why X3
forbade G3 from following the shadow when its own read found it to be the cause of seven of the
fifteen missed rows (§5.153 §5). Decision Log 6 (a) rules that read now.

**The construction and the rule are G2's, unchanged and not restated as new.** This file names the
metrics that join the table and the two judgements behind them. Everything else — pairwise over all
21 unordered pairs of a cell's seven raw 27 runs; MOVED means beyond that cell's own pairwise MAX;
`bedMinimumNonZeroBar` where a cell's own spread is exactly zero; the bar being 27-against-27 and
therefore a floor on the evidence rather than a ceiling — is that file's, read as written.

The thirty-two metrics G2 barred are re-barred here from the same raw runs by the same code path,
and `noise-bar.json` therefore carries all forty-nine. That is a consequence of the bar being one
function of a pair of captures and not a choice: a bar file with the shadow in it is a bar file the
whole instrument produced. **Whether the thirty-two reproduce G2's figures is a check this gate
runs and records** (`bar-reproduction.txt`), not an assumption; G2's committed `noise-bar.json` is
untouched and stays the bar its verdicts were read against.

## The metrics

Every quantity `cli/measure.ts`'s shadow axis reports on one side, entered as a **non-negative
distance** between the two sides of a pair, exactly as every other metric in the table is.
`src/metrics/shadow.ts` is the reader and it is unchanged: the same `shadowField` call, the same
declared region, the same scale, the same absences.

| family | metrics |
| --- | --- |
| the absolute departure | `shadowMeanDepartureDelta` |
| the raw ring maximum | `shadowStrengthPeakDelta`, `shadowStrengthPeakDistanceDeltaPx` |
| the blurred-edge model | `shadowFalloffSigmaDeltaPx`, `shadowFalloffAmplitudeDelta` |
| its falsifier | `shadowFalloffLengthDeltaPx` (the exponential alternative) |
| the profile itself | `shadowProfileRmsDelta` |
| the reach | `shadowExtentAboveDeltaPx`, `…Below…`, `…Left…`, `…Right…` |
| the displacement | `shadowOffsetXDeltaPx`, `shadowOffsetYDeltaPx`, `shadowCentroidOffsetXDeltaPx`, `shadowCentroidOffsetYDeltaPx` |
| W14 X7's affine pair | `shadowAffineSlopeDeltaMax`, `shadowAffineInterceptDeltaMax` |

**Two of these are not one-to-one with a field of `ShadowAxisReport`, and they are the two a refit
most needs.**

`shadowProfileRmsDelta` is the ring profile itself, RMS over the rings both sides resolved, because
the summary figures can hide a change of shape: a shadow half as deep over twice the distance moves
the amplitude and σ in opposite directions and can leave the mean departure where it was. It is
absent, never zero, where the two profiles share no ring — which is the normalised block's own
absence over `dark-solid` and `impulse`, where there is no light to remove.

`shadowAffineSlopeDeltaMax` and `shadowAffineInterceptDeltaMax` are the worst band and direction the
two sides both identified, of W14 X7's `y = a·bg + c` in linear luminance. Worst rather than pooled
because the pair is per band and a pooled figure over thirty bands would average the shadow's own
structure away; both sides' identification required because a band where one side's backdrop is flat
identifies no pair on either side, and a `c` compared against an absent `c` is not a reading.

## The one thing the shadow axis does that the other laws do not

It is read **per capture** and not per pair — `readCapture` computes it once for each of a cell's
seven runs, as it already does for the radial rim and the two declared-geometry readers — so the
21 pairs of a cell share seven shadow fields rather than re-walking the exterior forty-two times.
That is an arrangement of the arithmetic and not of the measurement: the distance a pair reports is
still a function of exactly the two captures in it.

It also needs **no silhouette**, which is the property that makes this read possible at all on the
66 cells of §5.151 §4 where one bed's extracted silhouette is under half the other's. A material
inside the extractor's threshold of its own backdrop still casts a shadow, and the shadow axis is
measured outside the declared region rather than outside an extracted one.

## What the bar cannot say, carried unchanged from G2

It is a **27-against-27** bar. The 26.5 bed's own run-to-run variation is not in it and is not
derivable (§5.149 §6), so a verdict of "moved" understates the combined spread of a cross-bed pair
by whatever the 26.5 side's own spread was, and a cell that fails to move is the weaker of the two
statements.

## What this gate has not done at the moment this file is committed

It has not read one 26.5 fixture against one 27 one. No material has moved, no profile document,
no bound, no floor, no golden and no row of `results/matrix.json` (X3). No capture has been taken.

## The machine at the moment of declaration

Read on 2026-09-19 on the capture machine:

```
sw_vers                                                      27.0 / 26A428
defaults read com.apple.universalaccess reduceTransparency   0
defaults read com.apple.universalaccess increaseContrast     0
defaults read -g NSGlassTintAmount                           0.5
python3 results/2026-09-16-w29-freeze/freeze.py verify        26.5 freeze intact: 1818 entries
```

# The noise bar for the coupled bed, declared — W29 G1c, before any 26.5 pair is read

W29 Decision Log 4 (b) and acceptance clause 3; claims §5.152 §B. This file and
`delta/noise-bar.json` are committed **before** the commit that reads a single 26.5 fixture against
a coupled 27 one. Nothing in this child has yet compared the two beds.

## What is being barred, and against what it will be read

`apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5` — 32 cells, 10 active and 22
receded, captured 2026-09-19 with **Increase Contrast ON and Reduce transparency ON**, seven runs
per pose, every run attesting both toggles. It will be read against
`apple-macos-26.5-1x-light-increased-contrast`, which is the same 32 cells in the same state,
because macOS 26.5 force-coupled the two toggles and no other increased-contrast state existed
there. That pairing is the whole point of the second sitting: the 27 profile of nearly the same
name was captured with contrast alone, so every difference on it is confounded with the decoupling
and §5.151 §9 reads none of it as a statement about the material.

## The instrument, the construction and the rule

All three are **G2's, unchanged**: `cli/native-delta.ts` with `native-delta-metrics.ts` and
`native-delta-readers.ts`, as they stand on `main` after G2's review closure (which corrected the
recede rows' barring). `../2026-09-19-w29-g2-native-delta/bar-declaration.md` is the declaration in
full — the 21 unordered pairs of a cell's seven runs, the max as the bar, the metric table, the
recede's difference-of-differences and its own `readingSpread` bar, and the standing statement that
a 27-against-27 bar cannot carry the 26.5 side's own spread and therefore floors every verdict
rather than capping it. None of that is restated here, because a second reading that quietly
restated its instrument would be a second instrument.

Two things about applying it to one pass of 32 cells are **not** inherited, and they are declared
here because they are the only places a smaller bed changes what the rule means.

### 1. The zero-spread fallback is the BED's minimum, not this pass's

The rule gives a cell whose own seven runs agreed exactly the *bed's* smallest non-zero pairwise
max on that metric, so that a perfectly stable cell is not handed an infinitely sharp instrument.
Over one pass, "the bed" would mean 32 cells, and a minimum over a subset is never smaller than the
minimum over the whole — on this subset it is **undefined on twelve metrics**, including every
geometry metric, where the 624-cell bed resolves one. Read off the subset, those twelve would take
a bar of exactly zero: the sharpest instrument there is, on the thinnest possible evidence for it,
and a "moved" on this profile would then mean something different from a "moved" on every other 27
profile — which a reading that joins §5.151 cannot afford.

So the fallback is the minimum over **the 27 bed**, which is this pass's 32 cells together with the
624 the first sitting published: one machine, one build, one bundle, one slider position, one
seven-run bar. It is taken as the per-metric minimum of this run's own figure and the committed
`bedMinimumNonZeroBar` of `../2026-09-19-w29-g2-native-delta/noise-bar.json`, **read** rather than
re-derived, because those are committed numbers and re-deriving a recorded figure is how one gets
quietly rewritten. `--fallback-bar` is the flag; `fallbackBarsRead` in the file records it.

The result, which is the check that the choice did what it claims: on **32 of 32 metrics** the
fallback now equals the 624-cell bed's, and exactly the same **three** metrics are left with no
non-zero spread anywhere — `contourDistanceP95Px`, `oklabDeltaEP95` and `rimPeakDepthDeltaPx`,
G2's own three (its Surprise: a percentile over pixels and a rounded ring index are blind to the
handful of pixels a re-run moves). Those three keep G2's committed amendment: **the bar is exactly
zero and moved means a non-zero reading**, recorded per row as `barSource: "bed-zero"`.

Where this pass's own cells resolve a spread, that cell's own spread is its bar as always. Over the
32 cells × 32 metrics the split is **69 slots on the cell's own spread, 785 on the bed minimum, 96
on bed-zero, and 74 absent** (a metric a cell cannot measure — no declared box, no luminance
transfer to fit, an empty silhouette inside the declared region — is absent with its reason and
never zero).

The 32-cell-only alternative is not thrown away: §5.152 §B reports whether any verdict would differ
under it, which is the reviewable form of this decision.

### 2. Twenty-eight of thirty-two cells are byte-stable, and that is the bed talking

Twenty-eight of the 32 cells have exactly zero spread across all 21 pairs on every whole-cell
metric — the same construction that reproduced the first sitting's 505 unanimous cells (§5.151's
Surprise). It agrees again here: `materialize` published 28 of these 32 cells unanimously and 4 by
vote, and the four voted cells are the four with a non-zero spread. Two constructions, one on bytes
and one on metrics, agreeing cell for cell on a bed neither was tuned on.

## What this commit has not done

It has not read one 26.5 fixture against one coupled 27 fixture. It has changed no material, no
profile document, no bound, no floor, no golden and no row of `results/matrix.json`. It has taken
no capture — the machine's toggles are back off and the GPU belongs to G3.

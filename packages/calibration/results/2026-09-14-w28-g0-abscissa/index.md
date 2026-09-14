# W28 G0 — reproducing the native-only abscissa read

Claims §5.144; W28 acceptance 1, X10 and X11. **Not identifiable from this bed.**
No family and scale clears the 0.004 linear-Y separation bar across the required rows.
The row winners below are diagnostics, not selections or permission for G1 to build one.

## Reproduce

From the repository root, with Node ≥24, pnpm and Python 3.12 with numpy/scipy:

```sh
pnpm install --frozen-lockfile
python3.12 packages/calibration/results/2026-09-14-w28-g0-abscissa/test_read.py
python3.12 packages/calibration/results/2026-09-14-w28-g0-abscissa/read.py
pnpm -r build && pnpm -r lint && pnpm -r test
```

The executed Python was `/Library/Frameworks/Python.framework/Versions/3.12/bin/python3`,
numpy 2.5.1, scipy 1.18.0. No Python dependency was installed for this read.
`read.py` calls `extract.ts` through the calibration package's `tsx`. The latter directly uses
`src/component-region.ts` and `src/image.ts`. Raw arrays live in a temporary directory, removed
when the analysis finishes. Reproduction opens only the declared native PNGs and backgrounds.
There is no browser, renderer, vitrea prediction, live setting read/change or native rebuild.

`declare.py` is the metadata-only enumerator. It created `population.json`, committed at
**8ad63af before the first pixel read**. It is not a step for silently replacing the declaration:
`read.py` verifies the current JSON enumeration equals that file, and the pixel boundary refuses
unless the population is committed unchanged at HEAD. The test feeds D names on both poses,
including a tinted state suffix, to that same admission guard and expects refusal before image I/O.

## Evidence inventory

- `population.json`: immutable pre-pixel selection declaration, all admitted ids and exclusions.
- `declare.py`, `extract.ts`, `read.py`, `test_read.py`: enumeration, guarded calibration-instrument
  extraction, scientific calculation and four regression tests.
- `inputs.json`: population digest and every opened PNG's SHA-256.
- `per-cell.json`: 398 native ordinates, all 17 abscissae (five families, seven-rung ladders with
  zero-scale aliases), decoded-once values, region scales, contrast, pitch and confound flags.
- `predictor-table.csv`: every predictor × scheme × pose × thickness row, plus policy-separated,
  clean-standard and cohort-separated sensitivities. Every number has the JSON precision.
- `isotonic.json`: every fitted cell value and residual, not just an aggregate score.
- `summary.json`: verdict, rankings/margins, noise provenance and active input displacement.
- `uniform-check.json`: 52 non-D neutral uniform points, checked against diagnostic row-winner
  monotone envelopes, never supplied to the regression. No map was selected.
- `residuals.json`: 255 clean-standard per-cell residuals and 123 matched-region-mean pairs.

## Population and provenance

398 cells: 230 canonical active, 129 canonical inactive, 39 W9 active. W9 started with 56;
9 uniform cells and 8 D cells are excluded. All 39 admitted W9 ids also have a canonical cell;
24 of those pairs are byte-identical. Both observations remain equally weighted as declared,
not called independent repeats; separate cohort tables show their effect. There are 250 active
and 110 inactive standard-policy observations, 10 active and 10 inactive Increase Contrast,
and 9 active and 9 inactive Reduce Transparency.

The canonical inactive population comprises 97 recovered single-run entries and 32 subsequently
attested probe entries. **Metadata correction beside, not over, the original record:** the initial
population's `provenance` label incorrectly calls those 32 non-recovered rows “manifest-attested
active.” Their `pose` was always `inactive`; the ids, selection and analysis are unchanged.
`per-cell.json` corrects the label to “manifest-attested inactive (non-recovered probe).”

W9's materialized PNGs are keyed by `last-run-manifest.json`, with majority shares in
`provenance.json`, not by its old `probe-scores.json` response predictions. W9's directory does not
contain its backgrounds. Its manifest raster paths equal the canonical manifest's paths, and
`declare.py` checks the background declarations are identical excluding comments before resolving
those keys to committed canonical background rasters. This establishes the available committed
lineage, not a new hash attestation of W9's uncommitted original background directory.

Every D background/component base is refused on **both poses and every state suffix**, including
`checkerboard__rrect-ml`. The hc-text square sanity check opens its background only, not its D
native PNG. It gives silhouette/body **0.511000000 / 0.698841699**; the capsule gives
**0.602627258 / 0.529284834**. The reversal in region ordering is reproduced.

## Definitions and limits of the statistic

Means are Rec.709 luma over encoded RGB bytes. `decodedOnce` applies the sRGB inverse transfer
once to that scalar; no average of decoded luma is used as an abscissa. The ordinate is the mean
of native per-pixel linear Rec.709 Y under `componentRegion`'s union eroded 6 CSS px, exactly as
`native-response.ts` reads it. Every raster must match the declared canvas and scale.

The ladder is **0, 1/32, 1/16, 1/8, 1/4, 1/2, 1 times span**, where span is the declared short
side in CSS px (minimum constituent short side for the explicitly flagged composites). This is
the spec's span used for `sizeThickness = smoothstep(32,96,span)`, not a device-pixel radius.
Dilation thresholds the signed-distance field and clips at the canvas. Gaussian sampling is a
separable discrete normalized Gaussian, truncated at four sigma, edge-clamped at the canvas;
sigma is multiplied by backing scale before filtering. Both means renormalize their support.
The canvas does not tell us what the backdrop beyond its edges was.

The regression pools equal x rounded to 12 decimal places, then uses equal-weight PAVA. That
rounding prevents numerical summation order from creating a false ordering at an exactly equal
checker mean. RMS is **in-sample**, not a cross-validated curve prediction. Body and Gaussian(0),
silhouette and dilation(0), are aliases and are excluded from runner-up competition. Different
nonzero scales may still induce exactly the same isotonic fit: the statistic knows ordering,
not physical scale, and a scale plateau is genuinely unidentified by this statistic.

163 cells have intermediate thickness; all are in the thin bin and flagged, including the
capsule's **0.09228515625**. Composite, tint and interaction cells remain in the full population.
The clean-standard sensitivity removes those three confounds and accessibility policies, not
intermediate thickness. Its 255 cells still mix span within each bin, so a residual can be a
span effect rather than H4. These qualifications are not used to rescue a selection.

## Diagnostic row winners

Clean single-surface, untinted, unpressed standard-policy sensitivity. Fractions refer to span.
The complete required full-population and policy-specific rows are in the CSV and claims §5.144.

| scheme / pose / thickness | n | source RMS | diagnostic winner | best RMS | runner-up gap |
| --- | ---: | ---: | --- | ---: | ---: |
| dark / active / thick | 40 | 0.002205612 | Gaussian 1/4 | 0.002069496 | 0.000004242 |
| dark / active / thin | 29 | 0.016532556 | Gaussian 1/4 | 0.005499204 | 0.000409614 |
| dark / inactive / thick | 22 | 0.002936579 | Gaussian 1/32 | 0.002381128 | 0 |
| dark / inactive / thin | 6 | 0.000284997 | source | 0.000284997 | 0.000115415 |
| light / active / thick | 68 | 0.016186527 | Gaussian 1/32 | 0.008331712 | 0 |
| light / active / thin | 50 | 0.087204959 | silhouette | 0.011413806 | 0.002036644 |
| light / inactive / thick | 28 | 0.006115841 | silhouette | 0.001353681 | 0.000006114 |
| light / inactive / thin | 12 | 0.011857522 | body | 0.002758498 | 0 |

The margin bar is **0.004 linear Y**, adopted by the charter for the recovered single-run bed.
The sitting plurality records report state shares, not raw per-pixel Y spread; this gate does not
pretend to estimate a new variance from them. §5.139 §4 attests 20/24 E cells byte-identical and
the other four incidental, one code on 236–362 pixels. §5.143 §1 records the new neutral-anchor
minorities as at most one code. One encoded code is 1/255, **not** a universal 0.004 linear Y;
the latter is the charter's approximate decision bar, not a transfer-function identity.

## Residual classification and handoff

No selected predictor exists, so “the residual after the selected predictor” and a unique active
counterfactual do not exist either. The diagnostic residual is **not universally pitch-flat**:
for W9 rrect-md at pitches 8/16/32/64 the winner residuals are
−0.013425413 / −0.013387169 / −0.010316417 / −0.009094996 Y; the range is 0.004330417.
At equal region mean on the canonical 2x light capsule, pitch 32 versus 4 differs by
0.015579484 Y, larger than the bar. But **H4 is not identified**: of 123 same-profile,
same-component, same-cohort pairs within 0.001 encoded x, none changes body-contrast SD by
more than 0.05. The low-/high-contrast checker pair is not equal in encoded mean. Fitting a
contrast term to these residuals would repeat the confound W9 already exposed.

**Recommendation: stop at Decision Log 2; G1 builds neither mechanism yet.** Local candidates
substantially improve the clean light-active thin ordering, but both schemes do not select one
kind/scale, and shared active/inactive locality is neither established nor disproved. The original
whole-source approximation is not vindicated by a failure to identify its replacement.

The sitting's two neutral patches near encoded 0.80 and 0.88 would constrain the dark thin step
and light bright-end shape; they cannot discriminate any locality family because all predictors
coincide on a uniform field. The phase-shifted hc-text square is the spatial discriminator.
The original square is D and remains unavailable as a selection baseline. One new phase alone
cannot guarantee scale separation; if the parent chooses new evidence to identify locality,
predeclare multiple non-D phase placements whose candidate orderings differ, and a contrast
pair matched in **encoded region mean**, before capturing. This is a recommendation to the
parent/user, not an extension of the authorized sitting or a capture performed by G0.

X8: active candidate body/source shifts average 0.041478766 encoded (maximum 0.528000000);
silhouette/source shifts average 0.033288389 (maximum 0.528000000). These are input changes,
not predicted output Y or a rendered active-material comparison. No response curve was used,
no active document changed, and no CSS/per-pixel Jensen gap was measured. No D fixture, fresh
native fixture, vitrea image, reference executable, display setting, accessibility setting,
profile, material constant, golden, scene file or canonical matrix was changed or captured.

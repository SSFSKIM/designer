W34 G2 contour identification — §5.176, clauses 5, 6 and 8

Operational evidence index. The narrative and user decision draft are in the
fidelity ledger and W34 charter. This index is README.txt because the worker's
instructions forbid creating Markdown reports.

Inputs and access
  G0 wave.py owns the pinned identification split and all native payload reads.
  G1 repeat/inventory.json supplies fixed masks and captured dependencies.
  G1 probe/inventory.json supplies materialized native PNGs through the reader.
  G1 inventory.json supplies sealed bars only inside the once-only receipt.
  No canonical fixture, material document, threshold, golden or matrix is changed.

Instrument and fit evidence
  identification.py       Reader, fixed-mask instrument, family fits and bin referee.
  forward.py              Exact body-field integrals and separately propagated nuisance.
  fits.json               First 400 fitted configurations, W33 families run first.
  native-zero.json.gz      Every absolute/signed native-minus-no-glass bin, bar and count.
  native-notches.json      Model-free notch per cell, arcs and straights separate.
  native-controls.json     Ordinary-fill and glass isoresponse alignment readings.
  native-bodies.json       Interior baseline, uncertainty and structured-body routing.
  validation-residuals.json.gz
                          Every first-pass fitted configuration's per-cell/bin/shell RGB
                          residual, population, bar and one-code effective tolerance.
  validation-headlines.json
                          Maxima only; these do not replace the per-bin referee.
  family-best.csv/json     Best of LS/minimax per family/space/stratum on validation;
                          a reporting selection, not a fresh fit. Domain is explicit.
  strata.json             Native/web notch and band-gap headlines for all 16 strata.

The first pass's new-axis families are circular-only effective-response diagnostics.
Their compact body field uses pixel-centre extrapolation. The qualified follow-up
fits the exact subpixel body integral only on solids and affine gradients; structured
backdrops do not identify their boundary and are declined from that physical reading.
Continuous curves retain their supplied-path instrument, not a circular forward fit.
Least squares and pixelwise minimax are both calibration-only. Minimax is in the
nominated composition space. Coefficients, power grid and rotated-axis grid are
recorded. Failed nominated fits do not prove every possible coefficient or law fails.

Web side
  browser.py              G0 launcher command, narrowed to one profile per X6 read.
  browser-runs.txt         Four settings, idle and process census before every launch.
  browser-*.txt            Actual capture/comparer output, including failures.
  compare-fixtures/       G1 manifest plus missing caveats field; links unchanged pixels.
  manifest-projection.json
                          Projection provenance; no holdout payload link is supplied.
  matrix.json             Wave-local probe matrix, 333 rows from 336 rendered cells.
  web-captures/           Every captured PNG, cell descriptor and runtime report.
  web-gap.json.gz          Same native fixed masks against the 336 web captures.
  web-provenance.json      Real adapter, shipped endpoint identity and PNG hashes.
  remeasure-first-profile.txt
                          No-browser remeasure exposing the first curvature refusal.

The first compare run rendered successfully but its final caveat reporter threw
because G1 omitted manifest.caveats. Its pixels were not recaptured. Three cells lack
standard matrix rows because contourCurvature refuses a zero-length contour. All
three remain in the contour gap table. These are measurement-tool limitations,
not erased failures or a claim of 336 successful standard matrix measurements.
Circular-native versus circular-web compares actual stadium counterparts, subject
to the native cubic and isoresponse qualifications. Existing continuous native
capsules keep the runtime's older circular mapping, so those gaps include geometry.

Replay
  python3.12 test-identification.py
  python3.12 identification.py
  python3.12 forward.py
  python3.12 web-gap.py
  python3.12 summarize.py

Analysis commands refuse to overwrite recorded outputs. Use a fresh evidence copy
for replay; never erase these results to rerun them. Browser runs are not needed
for offline replay. No native capture, build or TCC action is part of this gate.
The receipt entry point is G0 wave.py expose, not these replay commands. Do not
open holdout directories, PNGs, statistics or crops directly.

Follow-up indices
  w33-web-*                The prior families against actual shipped web pixels, 176 fits.
  qualified-fits.json       The initial 400 plus 64 exact-body calibration fits.
  exact-validation-*       The exact body-integral nominees, still with point failures.
  alpha-fits.json           32 true source-over fits with one RGB-shared alpha and
                           premultiplied target constrained between zero and alpha.
  alpha-validation-*       Their absolute per-bin validation checks.
  family-best-complete.csv/json
                           Every family/comparator/domain in one index. Best method
                           per displayed part is diagnostic, not a part-switching law.
  candidates.json           Forty frozen validation nominees, five explicit comparators/
                           domains per endpoint; all three G1 inventory digests.
  read-holdout.py           Receipt-only entry point; refuses standalone execution.
  fast.py                  Full-pixel quadrature shortcuts, no changed samples or fit.
  quadrature-shortcut-check.json
                           Reference comparisons at 64/128 samples in both spaces.

The first unoptimized nuisance propagation was stopped for computational cost after
its fits and point-validation tables had completed; forward-run.txt is retained.
The replacement propagates the same finite quadrature, skipping indicator evaluation
where the one-Lipschitz SDF proves every subpixel lies on the same side. It does not
refit coefficients or select native runs. The finite perturbation envelope is not a
confidence interval or a proof over all possible hidden raster origins. Captured
no-glass pixels define a piecewise-constant device-pixel field; the constrained body
field is integrated in the declared encoded/linear composition spaces.

Pre-exposure amendment, retained beside the unspent first candidate document
  candidates-v2.json keeps all forty nominees, coefficients and inventories unchanged.
  Its forward.py dependency propagates the no-glass half-code through the actual
  body/stroke response and encoding. A constant .5 bound is too wide inside the
  body and can be too narrow for an unrestricted affine response that amplifies
  the backdrop. test-reference-propagation.txt checks zero interior contribution,
  physical attenuation and affine amplification. The second partial propagation
  log remains forward-quadrature-run.txt; no completed nuisance table or receipt
  existed from that attempt. The final run is forward-reference-propagation-run.txt.
  The receipt-only runner reads its candidate document from the authorization,
  not from a hard-coded filename. The first candidate file is not rewritten.

Structural limit
  coefficient-independent-floors.json and prove-baseline-floor.py show why retuning
  the outside band's coefficients cannot point-close the nominated six-shell model:
  shell [-2,-1) is wholly inside the body and the band has zero coverage there.
  Every endpoint and part has a populated validation counterexample above one code.
  This is a limitation of the nominated decomposition, not a universal rejection of
  Apple's colour law. It is why the body/geometry nuisance and non-identification
  language are necessary, rather than merely attaching a larger tolerance to a fit.

Completion
  Identification is delivered as a negative, not a material implementation. DL2
  recommends no G3 and remains the user's decision. Parent independent review is
  pending. The original Screen Recording grant remains DL4's wave-close obligation.

  closure-verdicts.json                   G0's 128 exact-body fit/part verdicts.
  qualified-validation-forward.json.gz    Separate point and nuisance interval tables.
  qualified-validation-discrimination.json.gz
                                         Competing predictions against the fixed rule.
  receipt-preflight.json                  Prepared configuration, before exposure.
  ../2026-09-23-w34-g0-contour-bed/wave-identification-receipt.jsonl
                                         Actual begin/complete, spent once.
  holdout-result.json / holdout-residuals.json.gz
                                         Only the frozen nominees' held result table.
  holdout-qualified-*.json.gz             Frozen physical nominees' held qualification.
  holdout-qualified-index.json            Local ids mapped to receipt candidate ids.
  holdout-native-* / holdout-web-*        The same receipt's native and shipped-web cut.
  holdout-browser-*.txt / holdout-read.txt Retained execution logs, no subsequent refit.
  close-*.txt                            Required closing checks.

Receipt configuration SHA-256:
  3c4c046541f91ab7cd5dab2bdd8c450869e595c50736d538085cbfb98e54b93f

Do not run expose again. It is spent, including for changed candidates. Read the
holdout result's own tables; do not reopen native held PNGs/crops/statistics. The
per-cell body estimate on held cells was part of the frozen instrument, not a
new stroke-coefficient fit. All 408 glass cells have shipped-WebGPU captures; the
standard comparer matrix has 333 non-holdout rows, with held contour readings kept
in their own receipt artifacts and the three non-holdout curvature refusals intact.

Diff check
  close-diff-check.txt reports one trailing blank line in the preserved raw
  close-calibration-tests.txt output. It is retained as evidence. Authored Python
  and specification text have no whitespace warning; no raw test log was rewritten.

Independent-review fix wave, 2026-09-24 (§5.176 §9)
  Every original reading, nominee and the spent receipt stay as recorded. The
  corrections are appended under review-fix/ and read no held payload.
  test-review-fixes.py      Regressions for the three findings, red before the fixes
                           (review-fixes-red.txt) and green after (review-fixes-green.txt,
                           review-fix/regressions-green.txt, review-fix/review-regressions.txt).
  review-rerun.py           Non-holdout re-reads only; refits nothing it re-evaluates.
  audit-receipt.py          Reads only the committed receipt events.

  Finding 1, the affine body's half-pixel coordinate convention
    review-fix/coordinate-offsets.json      Old-minus-corrected displacement, 56 affine bodies.
    review-fix/coordinate-compact-*         64 compact body-forward fits re-evaluated;
                                           the index maps them to their original ids.
    review-fix/coordinate-exact-*           64 exact-body fits re-evaluated.
    review-fix/coordinate-alpha-*           32 shared-alpha fits re-evaluated.
    review-fix/coordinate-qualified-*       The qualified forward and discrimination tables
    review-fix/coordinate-closure-verdicts.json
                                           and G0's verdicts, under the corrected convention.
    review-fix/coordinate-run.txt           The run's log.
    The corrected inner-shell floors are recomputed from coordinate-exact-residuals
    and recorded in §5.176 §9; coefficient-independent-floors.json is not rewritten.
    The held tables were not re-read with the correction.

  Finding 2, the faithful W33 bases
    review-fix/w33-variant-map.json         Original variant versus faithful reference.
    review-fix/w33-reference-{no-glass,web}-{fits,headlines,residuals}
                                           64 calibration fits per comparator and their
                                           validation referee; review-fix/w33-bases-run.txt.

  Finding 3, the receipt bookkeeping
    review-fix/receipt-integrity-audit.json Begin 3c4c0465..., complete daccc0e8...; the
                                           forty removed fields and the proof of equality.
    review-fix/receipt-audit.txt            The audit's printed digests.

  Closing checks: review-fix/{calibration,boundary,numerical}-tests.txt and
  review-fix/freeze-verify.txt; the re-run once every reading had finished is in §5.176 §9.

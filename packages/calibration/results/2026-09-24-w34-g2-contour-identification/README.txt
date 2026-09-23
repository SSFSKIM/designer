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

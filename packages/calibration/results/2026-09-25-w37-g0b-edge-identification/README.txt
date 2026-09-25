W37 G0b — DELIVERED FOR REVIEW, c9a §5.182

RECOMMENDATION: CLOSE W37 AT THE FINDING. The ruled hard stop fired. None of
three declared families closes calibration grey straights at both scales.
No G0c, shader, prototype, material change or partial-adoption proposal follows.

Branch w37-g0b-edge-identification, worktree agent-w37-g0b, parent f6dabeca.
Pre-score declaration commit89f45616; bounds-declaration.txt SHA-256
0ddc766612ab8f84143b7cef665e889c80437c423fc39e8253564d51b4f769bd.
The declaration and hash test were committed before the first score. All
numeric outputs are write-once. New evidence prose is .txt; the existing
ledger and charter are updated directly. No Markdown tool refusal occurred.

WHAT WAS DECLARED AND WHAT WAS SCORED

F1: encoded affine luma/chroma responses, ramp line.
F2: encoded affine luma/chroma responses, squared line.
F3: encoded quadratic luma/chroma responses, ramp line; opened only after F1
and F2 failed calibration grey straights. No fourth family or later form change.
Each has a signed independent shoulder spline at0/2/6/12 CSS px, zero at12,
with independent isotropic and vertical components. The line and each shoulder
coefficient have their own luma/chroma response. Angular power1/2/3/4/6; line
width.8..2.4 by.2,45 shapes per family/scheme. Tail beyond6 is extrapolation,
not an extended fit domain. Thickness1, fixed. Neutral encoded deep conditions
luminance; the full native encoded deep vector conditions chroma.

The numerical operator averages its radial/angular basis over each pixel with
8x8 midpoint quadrature, then transforms/clips the encoded composite, passing
through edge.forward with old rim/shadow off. It does not claim that averaging
and clipping commute. The centre arc/straight classification is held within a
pixel, a named tangent-transition approximation. Circular arc geometry is
otherwise exact; diagnostic straight geometry is affine. The same model applies
to every bin and both scales. No fractional-coverage branch is admitted.
Before scoring, grey128's24 at1x and18/31 at2x were checked against the declared
integrated ramp:24.171429 and17.457143/30.885714, all within1 code. The1x
integral equals the mean of the2x pair exactly. This is a consistency check,
not identification of Apple's reconstruction filter.

Native-only LS:28 circular active calibration cells per scheme, both scales,
all solid colours jointly. Equal fitting mass per bin/channel after excluding
censored pixel channels; validation and web deep never enter a solve. All270
matrices have their ranks, singular values, coefficients and objectives in
search.json.gz. F1/F3 each reject5 rank-deficient width2 shapes per scheme,
which duplicate the first shoulder hat; F2 admits45. Selected ranks28/28/42;
no coefficient reaches the declared4096 bound. Both schemes choose exponent4;
F1/F3 width1.2, F2 width2.4. These are failed measured hypotheses, not shipped
constants. fits.json records every coefficient and fit cell.

Maximum per-channel-bin mean ABSOLUTE error, codes, tolerance1:
             calibration grey straights     all calibration    all validation
  F1                  9.074443                  10.404696          19.911310
  F2                  8.706337                  10.985204          20.135255
  F3                  8.126100                   8.506613          20.637789
All calibration/validation here INCLUDE noncircular straight diagnostics.
Circular validation alone: F1 6.452957, F2 7.253433, F3 7.993987. The large
validation miss is span96 under fixed thickness1, not permission to fit it.

By scheme, circular calibration / circular validation / calibration grey
straights:
  F1 light 7.742870 /5.093591 /6.880492; dark10.404696 /6.452957 /9.074443.
  F2 light 7.901848 /5.315727 /6.824995; dark10.985204 /7.253433 /8.706337.
  F3 light 7.507326 /3.843518 /5.926100; dark 8.506613 /7.993987 /8.126100.
The best aggregate calibration family, F3, still underpredicts dark grey64's
2x top outer row: native45 over deep versus36.873900, all channels. The light
worst is grey1601x top: native excess23/21/21 versus17.073900 each. Failures
concentrate in the last CSS px across the grey ladder, not just at the old tail
cutoff. residuals.json.gz retains all66,765 bins including inactive and
below-floor records; failure-cells.json and family-summary.json retain each
cell and stratum. Censored forward channels remain; none are inverted.

THE FORM OBSTRUCTION — NOT JUST A FAILED SEARCH

At light grey255 circular200, native deep=(253,253,253), matched top/bottom
straight bins have EXACTLY the same inward depth and opposite unit normals:
 1x shell-6: t5.5 CSS px,156 pixels per side;
 2x shell-12: t5.75,312 pixels per side;
 2x shell-11: t5.25,312 pixels per side.
Bottom is253, top250 in every channel; all are uncensored. Every declared
family is even in normalY. Reflection preserves its integrated features, so
all coefficients and all declared shapes must give the SAME prediction to the
two sides. Triangle inequality puts the minimax residual at least1.5 codes,
above the one-code tolerance. form-obstruction.py reproduces native pixels
through the guarded reader and verifies equal features for all45 shapes of
each family at each witness. This obstruction survives arbitrarily better
coefficient fitting within these forms; it does not rule out direction-sensitive
or otherwise undeclared laws. No fourth family was tested to address it.
The independent signed tail removes G0's forced cutoff-ratio limitation but
cannot make an even shoulder distinguish top from bottom.

OLD TREATMENT COMPARISON AND TRANSFER

Per active admitted channel-bin, threshold.5 code, all geometries/roles:
           better       same       worse      total
 F1         20489       8902        3033        32424
 F2         20519       9004        2901        32424
 F3         20650       8927        2847        32424
This compares ABSOLUTE SIGNED-MEAN excess error on BOTH sides, because G0's
old-rim table stores means. It is not the per-pixel MAE closure estimator.
The comparator is the old FULL boundary treatment (rim+shadow); rim-alone
contributions remain beside it. old-rim-comparison.json.gz names every bin;
old-rim-summary.json partitions by scheme/role/geometry and names worst trades.
The worst all-role worsening is dark red continuous1601x bottom shell-2:
10.806078 /10.985825 /11.033006 codes F1/F2/F3. Calibration worst worsenings
are4.359058 /4.363823 on light red rectangle1202x side shell-5, and4.327718
for F3 on light magenta circular1202x horizontal arc shell-5. These families
trade bins; none meets DL1's 'moves every admitted bin toward Apple' rule.

Boundary-only conditioning transfer E(web deep)-E(native deep), fixed native
coefficients, pixel ranges (codes):
 F1 -7.447281..+33.741197; F2 -7.938211..+35.222517;
 F3 -8.163969..+29.217063.
transfer.json.gz records624 family/cell tables with every bin and raw output
delta beside boundary-only delta. Web inputs are G0's W34 historical non-black
bodies and W36's retained black-price bodies, not new captures. Body error is
not absorbed into an edge coefficient. The tail below6 could affect a rendered
deep estimator; no runtime deep-invariance or canonical transfer is certified.
Synthetic pre-composition tests run separately for each family, recover nonzero
coefficients and changed coefficients at a fixed body, and detect a changed
body at fixed coefficients. Half-alpha and fractional coverage are refused.

E1 AND PROSPECTIVE PRICE

canonical.py repairs G0 beside, without editing its reader or recorded data.
All four sides x every declared shell appear:504 bins across14 rows;108 absent
side/shell records explicitly UNMEASURED. Eight rows are fully measured; six
capsule rows have unmeasured sides and are now UNMEASURED, not 'measured'. Every
one of G0's396 existing numerical bins and each recorded maximum reproduces
exactly; maximum29.359375 remains. All14 rows have measured failing bins, but
only eight have complete measurement coverage. The proposal is not adopted;
its14-row population and one-code bound are not widened or silently restricted.
Tests first reproduced the missing-side/shell failures against the old geometry.

No family closes the calibration greys, so brief D's prospective E1/M2/CSS price
is NOT triggered: no viable law is nominated and no nonidentity canonical stop
prediction is invented. M2 remains2% against W36; L1 remains.055/.005 against
named W33; E1 remains1. At the actual no-change outcome G0's280-row stop snapshot
remains exact. No C1/X1/B1 or stacked/grouped nonidentity pixel proof is claimed.
No M2 mask, CSS carry/decline, predicate, golden, material or source changes.

REPRODUCTION AND LIMITS

G0's44,510 residual bins and416 transfer tables reproduce exactly; coefficients
within1.84e-13. Its208-cell native replay, memo diagnostics, old-rim11,117 bins,
black provenance, E1 and placement reproduce. G0 replay --verify originally
failed only because its recorded source/guard strings name its old worktree.
reproduce-g0.py compares every numerical field while preserving those paths as
recorded provenance; g0-replay-reproduction.json explains the difference. The
existing w37-edge-identification test now calls that sibling wrapper. No G0 or
W35 script is edited, no historical number/hash is rewritten.

verify-scores.py independently reconstructs the chosen basis and weighted LS
from native pixels: maximum coefficient difference2.56e-11, then every new
residual and transfer table reproduces exactly. At fixed coefficients16x16
integration changes a predicted bin mean by at most.064794 code; it does not
close the greys and is not used to refit/reselect. verification.json records it.
Use python3.12. Rechecks: test-instrument.py; test-canonical.py;
verify-scores.py --verify; form-obstruction.py --verify;
reproduce-g0.py --verify-native. Regeneration requires a fresh evidence output
directory preserving sibling layout; scored outputs refuse overwrite.

DECISION LOG1 — G0b draft, not ruled

Close W37 at the finding. Nominate none; do not open G1a or a G0c. Neither greys
nor chroma close, and every family trades bins. Keep E1 unwidened, no population
exclusions for partial adoption, and all existing stops. DL2's placement/backend/
policy decisions remain conditional, not implemented. The next identifying
work, if separately chartered, must distinguish signed normal dependence from
path/alignment/phase effects using top/bottom-matched uniform controls, repeated
1x/2x captures and genuinely independent subpixel phases, with a new split
before fitting and newly authorised native access. A second calibration span
would be needed to identify thickness rather than spending the160x96 validation.
The saturated-body gap remains W36's, not a fitted edge correction. This is an
evidence requirement for a future wave, not authority for another W37 experiment.

Final verification is recorded beside in checks.txt and the ledger. Parent owns
independent review and the closing ruling. No release/version step is opened.

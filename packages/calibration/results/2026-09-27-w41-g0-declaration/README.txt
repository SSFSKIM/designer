W41 G0 — declaration and instrument, delivered for parent gate review (§5.191)

Findings for the parent

1. STOP before declaration, resolved by charter v2.1 (9762ef9c).
Charter v2 clause 7 named the active top straight as a shadow-only control
without conditioning on scheme. Memo B and its shadow-reading.json show that
light-active top shell 0 carries -20 codes at grey128 and grey255, both scales,
while the held shadow is below 0.0003 code. Dark-active top is the observed zero.
The parent corrected the charter; the worker did not amend it. The declaration
will retain light-active top as a stroke bin and use the corrected control set.
The full copied numerical witness is stop-witness.json. These are existing
exploratory readings, not a new fit or a WGSL proof. The tiny modelled dark-active
shadow reaches 0.024649 code at 2x grey255; the charter's “below 0.02” shorthand
is the 1x reading, not a bound at both scales. This does not change the control.

Reading provenance

readings/ preserves the two grounding memos and all their available scratch
scripts and outputs. reading-provenance.json records their original byte hashes.
The large stroke reading is losslessly gzipped, mtime 0; its recorded SHA names
the decompressed original bytes. No copied script has been executed here.
The copies contain historical absolute paths and are not yet a G0 replay tool.

Workspace preparation

Branch w41-g0-declaration at /Users/new/vitrea-w41/g0, cut from main 55511a72,
then fast-forwarded to the parent's charter correction 9762ef9c.
The EnterWorktree session-switch tool refused this subagent; all work uses
absolute worktree paths and explicit command working directories instead.
pnpm install --silent and pnpm -r build passed. workspace-build.txt records build.
freeze-verify.txt: 26.5 freeze intact, 1818 entries.
No native payload, validation or holdout read; no fit, exposure, browser,
web/native capture, matrix CLI, or shipped file change in this preparation.

Committed checkpoints (chronological; earlier readings remain unchanged)

95e4e075 — Initial pre-fit declaration SHA-256
99e460d5cf83da086fb27dbd132058fe81c31767462917623ce9883c74c9c05c.
The initial closure/pins bind charter v2.1, W39 scenes/split, archive inventory,
all families, their bounded domains, the full exterior range and fixed strip.

0f46abe1 — Twin audit, no native fit. Of the preserved body predictions, >=3-code
separators exist for every pair. B0/B1: maximum21.149240, ordinary20.322433;
B0/B2:22.532827, ordinary22.532827; B0/B3:33.470862, ordinary20.872726;
B1/B2:3.225059 (ordinary); B1/B3:28.228170, ordinary maximum2.286147,
BRIDGE ONLY; B2/B3:27.976343, ordinary4.461176. These compare exploratory
instances, not certified family separations or survival. The O12 reading was
an unbounded local LS trial; G1's declared fit is bounded and remains local.
W39 whole-cell fit population is404/408 calibration cells,1212 channels;
W41 retains408 cells,1220 uncensored channels and4 one-sided rail bounds.
S0/S1's prior inactive separation1.15/2.03 is below3: insufficient resolution,
not evidence that S0 passes one code. S1/S2 and S0/S2 have the reflected-row
3-code observational witness, not an already-fitted S2 prediction. Stroke
M0/M1/M2 have observational witnesses rather than fitted family outputs.
1x rrect arc population2 is UNMEASURED; the2x n14/n4 contrast is admitted,
but path/angular sampling confounds curvature. Exact cells are twin-audit.json.

Core instrument e60cabc6 — Synthetic and replay results
instrument/test-attempt-1.txt:7 tests pass. At1x/2x, aligned one-device-pixel
band coverage is[1,0,0] for outside shells0/1 and inside shell-1. Oblique
shell1 reaches coverage0.46484375/0.45703125. A synthetic nonlinear backdrop
produces16.000000000000004 codes when sampled BEFORE area averaging, versus
0 if the order is wrong. Max-normal angular normalisation and M2's held luma
are tested. Synthetic strips:32/64 rows,48/96 pixels per row,zero residual.
instrument/rendered-attempt-1.txt:2 tests pass through a real synthetic PNG;
a G-only4-code top-shell error stays a G-only failure in all7 repeats.
instrument/shadow-attempt-1.txt:3 tests pass, including exact receded zero,
full supplied-path shift versus the wrong normal approximation,scale covariance.
instrument/shadow-gpu-attempt-1.json:360 actual runtime CPU-law cases differ
by at most6.938893903907228e-18;3240 real Apple M2 Pro Metal compute cases
match the unchanged WGSL arithmetic within0.00002836012339135774 codes.
No software fallback, browser, native capture or web capture. This proves
arithmetic with synthetic field inputs, not field-texture reconstruction or
browser compositing. The resolved-materials sidecar verifies the four documents
and source bytes; the shader proof pins it beside the source/wrapper hashes.
Environment: existing external /tmp/w39-g2-wgpu, Python3.12.3,NumPy2.5.3,
wgpu0.32.0. Ordinary pure-reader tests use python3.12/NumPy2.3.5.

instrument/replay-attempt-1.json: the fetched release inventory matches
58329732f947d42cd5e1518962016191faaa79d89b7089c6dadf5724dde35f61.
Guarded CALIBRATION ONLY, whole ~/vitrea-w39 tree denied:504 cells,64504
stroke bins reproduce exactly;408 uniform deep cells reproduce from crop
pixels;16 gradient strips reproduce memo row means exactly. The DECLARED
row medians equal those means here,maximum difference0,so the statistic change
is not hidden. No validation/holdout payload or native fit. The replay script
reads only through the inherited Reader and retains source hashes in its output.

Independent focused reviewer-high on e60cabc6: no material findings. It reran
all12 synthetic tests,360 runtime CPU cases,3240 Metal cases and the complete
calibration-only replay. Body solver,exposure,sheets and later stroke multistarts
were outside this focused review,not silently approved by that verdict.

Parent X31 aggregation ruling — charter v2.2, received in224b41e3
A measured comparison within max(1,bar) or a satisfied hard rail constraint
permits survival; rail violation/measured failure is binding. Population-deficient
bins are UNMEASURED,excluded and counted. At closure,censored held-out cells
are UNMEASURED and count toward neither pass nor coverage; every measured
held-out cell must pass and the measured coverage fraction is reported.
This resolves the initial declaration's ambiguous aggregation without widening
a tolerance or recutting a population. The amended declaration will bind it
beside the final solver execution budgets,retaining the initial hash above.

Archive limitations — grounding lists verbatim, not new claims

5. WHAT THIS ARCHIVE DOES NOT IDENTIFY
- Hue interpolation between the six factorial directions; matched-channel cells add some
  directions, not a dense hue sweep. No arbitrary hue harmonics are licensed by six anchors.
- A C response above.024: two remote red/green bridges do not form a chroma sweep or fix
  high-C behaviour in other hues. C12/C24 quantisation alone permits degree-scale angles.
- Full neutral behaviour below40/above150, nor the black branch below encoded.003.
  Scalar bridge lumas within the interval do not identify those extrapolations.
- An arbitrary group-level term: one gradient amplitude/mean, no textured, frequency,
  nonlinear-gradient or chromatic-gradient controls in this read. Blur/response factorisation
  and a group-mean coefficient remain unresolved; two-stage tone is similarly nonunique.
- General span/shape, other accessibility modes, dynamics or stacking. This memo reads
  only the span44 colour/gradient cells; validation span96 and all holdout remain unopened.
- Separation of directional deep-body variation from long boundary influence: even the
  >=14 strip shows active directional differences. No 'edge-free' baseline is certified.


7. What this archive cannot identify, and held tests to declare before fitting
- Physical coverage/opacity versus intrinsic stroke colour, exact subpixel width, and slight
inward support at curved boundaries: mixed-pixel darkening is not a location measurement.
The W39 phase actuator failed; no phase cells were admitted. Opaque coverage is NOT glass coverage.
- Whether active top absence is true removal or exact cancellation; no observed exterior bright
surplus separates them. Modeled shadow is not measured native shadow in the first two pixels.
- A universal curvature law from the44/64 ladder: path family, angular sample positions and
curvature change together. The circular160x96 holdout can test larger-radius transfer, not fit it;
96-span validation remains unopened here and is not a proposed source of coefficients.
- Window-relative versus local signed normal: all shapes are axis-aligned. Grey128 translations
are equal, but grey255 bottom-position pair is holdout and can test bright-level height transfer.
The circular200x44 W37 witness pair is also holdout: it can test width/tail transfer, not train it.
- Unseen chromatic mixing: six held-out colours remain sealed. Fresh-colour near-separability
cannot justify ignoring the saturated dark-green weak-channel gap7 at an input32.
- A full64..192 local gradient sweep, arbitrary images/frequencies, coloured gradients, tinted
stroke response, dynamic poses, accessibility endpoints, fractional DPR and independently
controlled phases: absent here. No rrect/gradient pair exists. Black intrinsic stroke is unmeasured.
- CSS projection quality and actual GPU raster/SDF/filter error: no web render was run. All
numerical model/LP readings must be refereed against actual rendering before any shipment claim.

Replay commands (run from this directory; write results only to fresh scratch)

python3.12 -B twin-audit.py > /tmp/w41-twin-audit-replay.json
python3.12 -B instrument/test-instrument.py
python3.12 -B instrument/test-shadow.py
python3.12 -B instrument/test-rendered.py
python3.12 -B instrument/replay-readings.py "$FETCHED_ARCHIVE_ROOT"

The archive argument is fetch-archive.py's verified extraction result. Default
archive-root.txt records this machine's cache, but an explicit root makes the
same guarded replay portable without editing committed provenance. It still
requires the pinned inventory, calibration role and whole-raw-root denial.
replay-attempt-2.json preserves that explicit-root replay beside attempt1;
the only intended report difference is the replay script's source hash.
The SciPy/Metal proofs run outside the normal unit suite in the recorded
/tmp/w39-g2-wgpu environment; a new environment must reproduce its package
versions before numerical byte comparison. No production receipt command is
part of a G0 replay. Exposure tests create scratch receipts and synthetic PNGs.

Stroke search checkpoint414ad23f (synthetic only)

instrument/stroke_fit.py implements M0/M1/M2 and both geometry rivals over the
joint four endpoints with shared width. Gamma uses eta*(1-beta), and sorting
all eight bounded ordinates maps onto the monotone domain without dropping a
parameter. The fitter owns arrays,not archive admission. Its caller supplies
calibration cells,population-admitted bins and held shadows; all seven repeats
remain the independent survival scorer's responsibility.

The planted G+M0 recovery reports LS maximum2.1050539089628728e-10 codes;
the best minimax forward bracket is[0,1.4883028143231058e-9]. The selected
minimax optimizer itself did NOT converge: the exact objective's nonnegative
floor and the forward-feasible upper certify this tiny bracket separately.
No success flag is invented. Fourteen of16 LS starts and15 of16 selected
minimax optimizers converge; every raw/refined result is retained. The original
raw-start failure (57.359128345132945 selected maximum; baseline line-search
failure at0.0005319104) remains in attempt1 and the diagnostic artifacts.
A declared LS-seeded refinement was added before any native fit; its budget
and zero-floor criterion are in stroke-execution-parameters.json,with original
bytes retained in stroke-execution-parameters.v1.json.

Rank is14 of15: binary subpixel quadrature makes width locally piecewise
constant,so gradient steps cannot identify it within a sampling plateau.
Only the16 declared initial widths explore that coordinate; the planted width1
was at the baseline. This is a LOCAL search,not width recovery or a global
family negative. A G1 report must preserve that limit rather than promote a
failed search into exclusion of every stroke coefficient. Max-normal gauge
normalisation does not make width or colour a physical opacity measurement.

Fixed-coefficient16/32 sensitivity over1136 exterior pixels at1x and4676 at2x
has maximum0.2475000000000449 code on the synthetic M0 material. It is not a
native stability measurement; G1 must report sensitivity for its own frozen
coefficients. Mixed-censor mass is explicitly normalised across the measured
bin/channel groups within a cell: the regression's squared objective is2.5,
not the erroneously diluted2.333333. Hard rail constraints remain separate.
M2 neutral identity and held-luma gamut behavior are covered by the core tests;
no claim of full M1/M2 native identification follows from these synthetic proofs.

Historical byte pins are not a new ordinary-CI invariant

The pure strip/geometry,PNG scorer and scratch exposure behaviors are wired
into calibration's Vitest suite. The epoch-pinned shadow tests stay standalone:
putting W39's full renderer-source SHA checks into ordinary CI would forbid
G1's expressly authorized identity-gated additions,not protect the shadow law.
The recorded765-pass checkpoint included that extra wrapper; the final scoped
verification will report the corrected count beside it. All shadow synthetic
and Metal proof evidence remains intact and independently replayed.

Body instrument complete — a62c89c1 and additive fix7377df28

body-instrument/body41.py exposes forward,solve_linear,survival_linear,
constraints,verify_certificate,fit_local and score in encoded0..255 units.
E3/EH6 LP survival is the authority; nonlinear O12 and LS/minimax multistarts
stay LOCAL. All15 synthetic tests pass. Planted E3/EH6 maxima are
4.263256414560601e-14 /3.979039320256561e-13 codes. A deliberately wrong EH6
family is rationally certified at[15.555596204576219,15.5556044024584] codes,
bracket width below1e-5. O12 LS/minimax recoveries are
1.4210854715202004e-13 /1.7195134205394424e-12,rank12.

Independent review found that approximate dual support omitted tiny positive
coefficient-bound weights. The separate fix preserves all positive weights
and searches augmented/replacement supports. Its100-noisy-case regression
now reports100 certified minimax brackets,95 certified survival negatives,
5 feasible survivors,0 stalls and0 uncertified outcomes. The same reviewer
reran the15 tests and100 cases and returned correct/no material findings.
Future bounded recovery exhaustion is still an explicit uncertified result,
never pass or negative. The final execution record declares2048 additional
exact attempts,eight extra slack-ranked observations,support size<=p+1 and
HiGHS cap10000. Original execution bytes remain in execution-parameters.v1.json.
The final body execution SHA is
a3947184dbd81edd6597517ec03cee736ecbf622b1cbf22a9fe5f3a3ecee4521.
SciPy1.18.1 is confined to the external recorded venv; ordinary tests need none.

Standing eye sheets complete — 568e59d7

sheets/sheets.ts enumerates the matrix-store current union and the W39 public
web plan. Canonical1893 rows reduce to1003 profile/scene cells: against the
explicit main capture root1003 MATCH,0 UNMEASURED. MATCH means metadata
provenance and file presence,not byte identity with a historical capture run.
The worktree itself has no capture tree:0 MATCH,1003 UNMEASURED there.
W39's138 declared web-plannable IDs expand544 profile/scene memberships:
0 MATCH,544 UNMEASURED. Eight of those memberships are unadmitted phase-zero
variants; the production exposure uses archive-admitted membership instead,
not a fabricated native comparison for those declarations.

Under the parent's explicit scope clarification,sheets/render-calval.ts
rendered330 existing canonical comparisons (266 calibration,64 validation),
skipping92 holdout and581 probe cells BEFORE pixels. No W39 pixels were read.
The inventory binds native/shipped PNG bytes and every HTML output. Three
representative HTML sheets and initial/corrected PNG witnesses are committed
under sheets/examples/. The worker opened all three corrected aligned PNGs.
The eye caught a3px panel-offset bug in the exporter; a separate fix wave
and common-baseline regression corrected it without changing any input pixels.
The original images/hashes remain beside the corrected exports. Native/shipped
contour and interior differences remain visible and are described in the sheets
README; the candidate column is honestly EMPTY,not a duplicate of shipped.

Eleven TypeScript synthetic tests,30 Python PNG-export tests and a focused
strict TypeScript check pass. Independent core/PNG reviews are clean after
separate pose-provenance and alignment fixes. Candidate canonical-holdout
rendering refuses before pixels unless the exact four-document and renderer
configuration is recorded; this boundary was tested synthetically only.
No browser or capture process ran. Full330 HTML output is scratch at
/tmp/w41-canonical-calval-sheets; committed inventory plus three examples are
in sheets/. The script is standing infrastructure,not a material improvement.

Exposure runner complete — 17e2fccc,33a8954f,87565d45

exposure/runner.py provides freeze,verify,run_synthetic and run_production.
Production fixes the inherited W39 receipt path and the real web-only driver;
there is no alternate production log or injected capture backend. The runner
binds committed numerical/rendered predictions,source revision,configuration,
all transitive instrument inputs and executed compiled-policy module snapshots.
It now derives both scopes from the PINNED ADMITTED inventory,not every declared
phase:648 numerical cells (576 cal/val+72 holdout),600 rendered (536+64).
The56 numerical/eight rendered unadmitted phase cells remain explicit exclusions.
The standing-sheet138-scene declaration is unchanged and keeps those rows honest.

As charter v2.3 clarifies,held-out web predictions are generated BLIND from
public backdrop/geometry and a committed generated-backdrop bundle before the
exposure. No native fixture/archive pixels supply them. Inside the sole receipt,
fresh web renders must match their frozen bytes/projections BEFORE native
scoring. G0 ran no browser and opened no production receipt.

The original dry run has two calibration stand-ins,two new synthetic2x2 RGB
PNGs and zero numerical/rendered residual. A two-code planted miss fails the
one-code bound. A censored held-out stand-in gives measured coverage1/2,not a
false two-cell pass. Forty-one tests now pass,independently rechecked by the
same reviewer with no material findings. Separate fix waves preserve failed
scores durably before verdicts,reject callback mutation,bind the actually
executed policy/dist bytes,and omit never-admitted phases. A SIGKILL between
score persistence and aggregation leaves the score record and spent scratch
receipt intact; retry is refused. Original16-test and24-test artifacts remain
byte-preserved beside the41-test correction,indexed by full hashes in
exposure/evidence-index.json. The trusted scorer is a procedural boundary,
not a sandbox for hostile code; real browser/native integration remains G1.

Final declaration

bounds-declaration.txt SHA-256:
850747c1f03781a6efe9b433bd4ce3bd6cf72b63c9befd8d5d98de9eadf7f759.
Superseded initial SHA-256:
99e460d5cf83da086fb27dbd132058fe81c31767462917623ce9883c74c9c05c.
The complete initial text,closure,pins and generator are preserved under
that hash in declaration-history/. declaration-amendment.json names both,
plus the final body and stroke execution hashes. No recorded numerical result
is rewritten. The addendum binds charter v2.2's censor aggregation,v2.3's
blind-render freeze,admitted exposure membership and the parent's curvature
interpretation before ANY native fit.

Not identified here — additional explicit curvature limit

The parent ruled retaining the declared NOMINAL-radius rival: circles R22/32
on calibration,rrect nominalR22; clip(A*(1+rho/R),0,1) on arcs,straights unchanged.
The supplied path still controls support/normals. Differential local curvature
kappa(p) along a continuous path is a different forward law,NOT declared in W41.
A later charter can declare it; this rival cannot identify or exclude it.

Correction beside the earlier stroke-search checkpoint — 71ab629f

The earlier “only16 initial widths explore” limit was independently found to
be an actionable omitted search direction. On two four-pixel straight bins,
width1.75 and stroke64 over128 produce64/80; the old width starts cannot do
better than6.1935483871 codes even with optimal amplitude. A separate fix now
crosses quadrature steps with a conditional bounded coordinate search:
65-point sweep plus4x9 refinement,at most8 alternations per objective/start,
with fixed-width coefficient solves. The fixed quadrature/forward model and
parameter domains do not change. Off-seed device1.75@1x and CSS.84375@2x
recover to7.105427357601002e-15 codes,against red baselines6.19/8.00.
The original optimizer outcomes and parameter v2 bytes remain beside the fix.

This is NOT exhaustive support-state enumeration. Narrow basins,coupled
width/colour crossings and infeasible crossings may still be missed; the
subpixel quadrature's local rank loss remains. Recovery proves a forward
prediction,not unique physical width (X30). The same reviewer approved71ab629f
after the four width regressions,mass regression and a separate16-start status/
budget check; no material findings remain in that scope. The full joint replay
has its own separate result and does not inherit this scoped approval.

Final package checkpoint

calibration-test-final.txt:59 files,764 passed,1 skipped. The earlier765-pass
checkpoint is retained; one historical-source-pin wrapper was intentionally
removed from ordinary CI,not a numerical test or bound. lint-final.txt records
ESLint and all calibration TypeScript configurations green. Workspace recursive
build already passed. freeze-verify-final.txt again reads1818 intact.
Archive integrity verification hashes the complete release tree; analytical
archive reads in this gate were calibration-only through Reader,with raw roots
denied. No native fit,validation/holdout analytical archive read,browser run,
web/native capture,material change,publication or push is claimed by G0.

Completed joint width-search proof — 963d058d

instrument/stroke-width-joint-attempt-1.txt completes the corrected two-test
joint suite in499.671s,beside the prior244.207s artifact. Best LS maximum is
4.263256414560601e-13 codes; best minimax1.3073986337985843e-12. Both selected
best optimizers converge; rank remains14/15. Across16 starts,15 selected LS
and14 selected minimax optimizers converge. Two selected minimax failures
retain separately labelled forward zero-floor brackets; the exhausted LS
failure remains visible. Original outcomes retain their historical14/15 counts.
The same reviewer's71ab629f recheck is clean and includes the four off-seed/
search-boundary regressions,the mass regression and an extra16-start status
check. It did not duplicate this separately recorded full joint replay.

G0 hand-off

All five brief steps are delivered. The only source change outside this evidence
dir is the pure synthetic Vitest wrapper; the claims ledger records§5.191.
The declaration's complete source/execution hash verification and path scope
are scope-audit.json. Protected scenes,fixtures,frozen rows,generations,
material documents,goldens and adopted thresholds are unchanged: they still
claim the shipped pre-W41 material,not any experimental closure. The production
W39 receipt remains absent. No new capture tree exists to copy or supersede.
Every initial failure/correction remains beside its replacement. The parent's
whole-gate review/merge is next; G1,not this gate,owns native identification,
blind web rendering and the one eventual held-out exposure.

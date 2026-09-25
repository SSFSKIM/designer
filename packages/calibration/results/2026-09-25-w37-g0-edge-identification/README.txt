W37 G0 — DELIVERED FOR REVIEW, qualified negative (c9a §5.181)

Recommendation: nominate NONE. Stop before G1a pending Decision Log 1. The encoded
family is closer, but neither family closes even the straight bins, and neither
supplies a grey-only closure at its joint native-identified coefficients. This is
not an impossibility theorem for a larger colour/radial model or a finer search.

DECLARATION AND REPLAY

Branch w37-g0-edge-identification. Dispatch snapshot main efe6066e; setup actually
branched from main7f254381 after its tracker-only advance. Pre-score declaration commit
6f2e89ed; bounds-declaration.txt SHA-256
270ba479c6599bea082696e111b1ba81d9f941d93cfb6343c29a387e3ca8328b.
E1 and the per-cell no-change stop snapshot were committed with it; their own
hashes are in declaration-pins.json. No score existed before that commit.
New prose files are .txt because this worker may not create Markdown reports.

replay.py reproduces 208 solid cells (168 calibration/40 validation), every deep,
straight row and whole-pixel angular mean, with zero difference from both W35 and
the grounding memo. diagnostics.py reproduces every grounding diagnostic exactly:
channel invariants, shoulder continuation, old candidate maxima, .5 bar, M2
-60.0283%/-48.4331% erosion, and eight W36 black-price cells. The retained black
price's base+tune/receded patch equal the shipped law, checked in provenance.json;
they are NOT fresh canonical captures. expanded-bar-replay.json independently
opens all seven admitted normal runs of W35's 2x dark maximum and recovers
(.0714285714,.2142857143,.1428571429), shell-4, arc8, population14. The matching
whole/straight bin bars are separately recomputed in closure-bars.json.gz.

line-tables.json, surface-transfer.json and css-bound.json are reductions of that
fresh replay; native-replay.json.gz retains the six-CSS-px shoulder and angles,
not only selected headlines. Inactive circular straights remain exactly their
own deep through the six CSS px, all channels; the old 2-code inactive arc floor
is not called flat. static-audit.json reduces the remaining HISTORICAL artifacts:
280/56 glass cells, 416/80 admitted probe cells, old fitted leaves and widths,
34 historical golden passes. Goldens are NOT rerun. W29's width is 2.41611 DEVICE
px at1x, not a universal 2.2 CSS-px kernel; at2x 1.66283 device/.83142 CSS px has
fwhmResolved:false. No historical reading is overwritten.

WHAT WAS FITTED, AND WHAT FAILED

The complete formulas and grid are in bounds-declaration.txt; law.py is a sibling
extension, not an edit of edge.forward. F1 operates in linear light and F2 in
encoded light; both finally pass an opaque, full-coverage transformed composite
through edge.forward with old shadow/rim OFF. Compact squared line+shoulder,
vertical |ny|^p, independent affine luma and chroma response and a signed isotropic
keep term. Nine line widths x three shoulder widths x four shares x five angular
exponents =540 shapes per family/scheme; least squares in the family's own space.
No third family was declared or scored. Finite search, not global optimization.

Coefficients use 28 native circular calibration cells per scheme, jointly across
both DPRs. Every fit matrix has rank5. Native deep is the conditioning composite;
clipped channels are excluded from inversion but remain in forward residuals.
Each bin/channel has equal fitting mass; each pixel within it has equal mass.
Validation grey96/cyan and continuous160 never fit. No web value enters the solve.
verify-scores.py independently reconstructs the chosen-shape LS from raw guarded
native pixels: coefficient differences <=1.84e-13 and all44,510 residual bins /
416 transfer-cell tables exactly reproduce. The negative includes censored-channel
forward checks; they are not silently removed from closure.

                         calibration max  validation max  calibration straight
  linear  light             10.428513         6.313231          10.428513
  linear  dark              20.882831        19.666667          19.684862
  encoded light              8.626390         5.896421           8.626390
  encoded dark              11.843356         7.955766          10.910036

Codes, circular whole-pixel closure; tolerance1 per channel/bin. Active admitted
bins:4322/4340 calibration light/dark and620 each validation. Linear fails2589/
2683 calibration bins and382/370 validation; encoded2645/2526 and374/358. Means
are absolute BEFORE spatial reduction. residuals.json.gz names EVERY failed bin;
failure-cells.json names every cell maximum. Worst light calibration is yellow
1x top; worst dark calibration is magenta2x near the top arc. Circular validation
is grey96 light / cyan dark. Continuous/rectangle STRAIGHT diagnostics are not
circular closure: calibration maxima6.091928/18.990385 linear light/dark and
5.648452/9.964220 encoded; validation continuous160 maxima5.524386/26.776469
linear and4.562483/22.053616 encoded. Thus full validation including diagnostic
path/span transfer is worse than the circular column alone. No family is nominated.

Both selected linear shapes are w1.6,v6,q.15,p3; encoded light w1.8, otherwise the
same, encoded dark w1.6. Coefficients [a,g,c,h,k]:
  linear light  [.301006126,-.024922299,.933732707,-.673065965,-.056551391]
  linear dark   [.088485672,.513183867,-.285999226,2.774149331,-.052653172]
  encoded light [.354865357,-.253855763,.503747849,-.247519005,-.024118822]
  encoded dark  [.265905829,-.101217442,-.683056105,1.770940789,-.021030985]
These are measured failed hypotheses, not proposed shipped constants.

BODY TRANSFER IS NOT THE EDGE FIT

At the SAME native-identified coefficients, E(web deep)-E(native deep), with each
output's own deep subtracted, ranges over active pixels:
  linear light -3.810762..+16.824851; dark -15.769234..+48.630010 codes;
  encoded light -3.650884..+14.947356; dark -7.882067..+35.822687.
Admitted-bin MEANS have narrower extrema (-3.810762..16.568620,
-15.769234..48.214133, -3.650884..14.739142, -7.758389..35.270973).
transfer.json.gz tables each cell AND each bin, with raw output deltas beside
edge-only deltas. Most web bodies are the guarded W34 historical captures;
only black uses W36's preserved price. W36 changes only its sub.003 black branch,
so these non-black uniform-body inputs are not claimed new captures. Synthetic
pre-composition tests recover nonzero gains and changed coefficients at fixed
baseline to1e-12 and detect a baseline change at fixed coefficients in BOTH
spaces. Red-before-implementation and green logs are retained. No runtime/shader
agreement or rendered improvement is claimed by this numerical extension.

PATH, SPAN, EXISTING CONTROLS

At grey128, circular120, circular200, continuous120 and radius12 rectangle have
EXACTLY the same top rows at both DPRs:24 light/30 dark at1x;18,31 light and
(23,22,22),(39,39,39) dark at2x. The span44 straight response does not need a
path-specific amplitude. Curved continuous-path observations remain diagnostic.
Continuous160 (span96) changes dark deep134->121 and excess30->6 at1x,22/39->
7/22.846 G at2x. Light changes much less (deep195->198;24->22.857 at1x).
That is a thickness-associated transfer failure under declared factor1, not an
identified sizeThickness response: no second circular radius is admitted and
validation is not a thickness objective. Path and thickness effects on ARCS are
not separated by these straights. No free slope is identifiable on span44.

old-rim.json.gz decomposes11,117 native-conditioned inherited-forward bins.
Grey1282x horizontal arc shell-1: native excess -2.5/-2 light/dark; old neutral
rim ALONE contributes+6.547/+17.510, leaving total excess+5.153/+16.522 after
shadow. At the top straight the old rim contributes+7.062/+23.265, against
native total+31/+39. Stacking another line cannot remove wrong horizontal light.
A future gated replacement can reuse rimLitAxis as vertical and rimLitExponent
as p (account for/remove the old sqrt2 normalization), rimWidth as w; the old
isotropic shadow's keep has a coherent role. The new colour gain has no meaning
as scalar white rimAlpha. rimAlongSideSlope's XY saddle is not this normal lobe;
retain it on the old identity path, do not stack it into the new one. No current
control or default is changed here.

AUTHOR TINT PLACEMENT

Main capture-tree checker BEFORE canonical reads:1900 captures,1893 match,7
no-row,0 mismatch/misfiled/superseded/unreadable. Twenty native tinted/untinted
pairs measured, eight absent from dark profile membership reported UNMEASURED.
Native dark-solid orange: light deep(212,120,0), top(255,148,3) at1x and
(247,141,2)/(255,157,4) at2x; dark deep(254,150,4), top(255,175,0) at1x and
(255,169,0)/(255,182,0) at2x. The line lifts the painted body's dominant channels
without an untinted neutral blue lift; structured pairs are retained separately.
Recommend runtime colour conditioning AFTER author tint (and after black/body/
retention), rather than adding a neutral pre-paint result. This is an effective
composition choice, not identification of Apple's hidden order. §5.102's26.5
numbers remain history; §5.103 already rejected a strictly buried rim under an
opaque paint. An equivalent tint-aware precomposition implementation cannot be
ruled out from final images alone. placement.json carries the actual27 values.

IDENTITY, ACCESSIBILITY, BACKENDS

identity-proof.ts extends the identity table IN MEMORY and sweeps nine unread
leaves at gate0. Frozen26.5 b2b570e4adcea8fb/874be66ea501621b and current27
be13dae45098fc89/b0d0d8dacc6a03af/2a4323f33df8d799/7c454858a3cbad5b are exact;
a nonzero gate changes each. Archived resolved inputs allow this numerical proof
to replay after later document changes. No shader branch or drawn identity is
proved. Proposed inertLawCase: renderer-webgpu/test/w37-body-edge.test.ts;
literal expect(DEFAULT_MATERIAL_PROFILE.bodyEdgeStrength).toBe(0), append-only
identity-group test; GPU/CSS identity and unsampled backend tests at G1a. Both
receded differences must explicitly contain bodyEdgeStrength:0, even if every
old regular/clear rimAlpha/rimLevelGain/shadowAlpha and collapsed rim is already0.

Important source correction to any generic 'RT/IC stand down' shorthand:
core/accessibility.ts maps Reduce Transparency to increased occlusion/frost,
NOT a strong border. renderer-webgpu/material.ts opticsUnderPolicy retains its
ordinary rim in RT alone. Increase Contrast substitutes the strong border:
both widths fixed, level gain0, lit exponent0, along-side slope0; collapsedRim-
UnderPolicy substitutes that border too. forced-colors has glass:none. The new
operator must follow THOSE rim stand-downs exactly: gate0 for strong-border/no-
glass, preserve old border; no extra RT-only stand-down invented. Ordinary
presence/mat and collapse handling must remain declared if a future law is
nominated; these opaque full-presence fits do not identify collapsed amplitude.
bodyChromaRetentionUnderPolicy is the useful exhaustive-CPU-switch SHAPE, not
the same predicate: it stands down under increased/opaque occlusion, whereas IC
alone need not lift occlusion. Accessibility native line behaviour is unmeasured.

Backend declaration: only gpu-texture gets a prospective new composite transform.
For WebGPU css-backdrop and none preserve the old path EXACTLY, operator declined;
layer RGB/nonunit alpha does not contain the page composite. No fractional helper
is smuggled in. Residual: unsampled glass keeps the wrong directional/chromatic
edge. G1a must use proxies.spec.ts-shaped e2e groups over differing black/white/
coloured DOM backgrounds, compare gate0/nonzero PNGs AND alpha on both unsampled
backends, and assert actual backend readout. The sampled change does not certify
those paths. No browser run was made here.

CSS PROJECTION PLAN, NOT A RENDER

A prospective positive vertical lobe becomes inset 0 +h and inset 0 -h shadows,
replacing the old all-round bright inset behind the gate. Take the neutral body
level supplied by shared optics; evaluate the same colour-space law at |ny|=1.
The positive encoded excess's integral divided by its peak defines h, and the
peak fixes screen alpha (peak/(255-bodyCode)); keep the signed isotropic keep as
its own existing boundary attenuation projection, not a third light. In the
linear unsaturated first-order limit the line/shoulder area is
((1-q)*w+q*v)/3: .753333 CSS px for w1.6 and .810000 for w1.8 at q.15,v6.
This is an explicit same-leaf projection plan, not chosen new constants or a
promise that CSS's screen operation equals the composite transform. Actual
filtered RGB/chroma and a normal-varying colour are unavailable in this tier.

A SINGLE constant-output1-CSS-px inset has exact DPR2 top-row minimax lower
bounds, G codes, per grey0/32/64/96/128/160/255:
  light8.5/8/7.5/7/6.5/6.5/0; dark11.5/10.5/9.5/9/8.5/8/7.
css-bound.json retains all channels, colours and both top/bottom. These bounds
are specific to two equal full rows; they are NOT a universal lower bound on
blurred or multiple-shadow radial approximations. No colour-conditioned CSS
closure is claimed. A viable law must be rendered and carried/declined by DL5
under coherence before seal; there is none to render from this gate.

E1 AND THE STOPS

E1 is completely frozen in e1-declaration.json:14 canonical untinted uniform
active standard27 WebGPU rows, fixed native PNG hashes, physical whole straight
pixels with1.6-radius corner exclusion, d<=-6 deep, -6..0 shells, all channels,
floor4 and one-code mean-absolute EXCESS bound. Native no-reach bins are included;
missing/deficient is UNMEASURED, never pass; no predicate drop. MATERIAL amendment
isolates a directly observable uniform boundary and a resolvable code-level
signal rather than an unidentifiable blur sigma. Body-conditioned transfer is
reported separately, not used to excuse actual E1 error. The current-generation
baseline recomputation fails all14 rows, max29.359375: E1 is NOT adopted here.
Adoption must regenerate from matrix-named PNGs and matching metadata, BOTH
shipped document hashes/source receipt, or return UNMEASURED if tree absent.

No family survives, so the280 per-cell baseline rows are exactly the expected
post-G0 values; protected source/doc/matrix bytes are unchanged. Nonidentity
M1/M2/L1/predicate predictions remain explicitly UNIDENTIFIED, not invented
expected passes. A larger-budget family needs a prospective price before its
first render. M2 remains2% against current W36; L1 remains.055/.005 against
NAMED W33, not re-baselined. C1/X1/B1 and coherence unchanged, no mask/stop waived.
No source change implies no new exterior; the existing X1 pixel check is also
run against the read-only main tree, not silently skipped for lack of a worktree
capture tree. No candidate stacked/grouped exterior proof is claimed.

DECISION LOG DRAFTS — G0 draft, not ruled

DL1: Nominate NONE. The linear family misses calibration20.882831 and circular
validation19.666667 codes (full path/span diagnostic validation26.776469); the
encoded counterpart11.843356/7.955766 (diagnostic22.053616), against1. Native-only
coefficients and per-cell transfer are in fits.json/transfer.json.gz; transfer
ranges are -15.769234..48.630010 linear and -7.882067..35.822687 encoded. Neither
is a grey closure with only chroma deferred. Do not open G1a on these coefficients.
A larger predeclared budget should separate radial shoulder/line colour responses
and test nonlinear native-level/chroma dependence, with a refined radial/angle
search and fixed thickness; it is a new hypothesis, not guaranteed closure.
Validation already read remains validation, never a new fit set; larger circular
radius/phase/blind confirmation needs a newly authorised native experiment.

DL2: If a later family is admitted, REPLACE the old rim/inner-shadow treatment
behind the gate, never stack it. Reuse axis/exponent/width only with one coherent
meaning and keep the old path exact at0. Recommend post-author-tint conditioning
from the20 tinted pairs; do not claim Apple's hidden layer order. Thickness factor1
(no free slope) was declared and fails dark span96 transfer; same-span straight
path controls agree, continuous arcs remain unresolved. No fitted thickness or
path coefficient is nominated. Unsampled css-backdrop/none keep old pixels;
strong-border/no-glass stand-down follows the actual rim policy, not retention.

DL4: Confirm or reject the frozen E1 proposal:14 canonical active uniform
WebGPU/gpu-texture rows, fixed native-reference excess, per-side/shell/channel
mean absolute error<=1 code, floor4, no predicate drop, no-reach bins retained,
missing UNMEASURED, rederived at adopting matrix/document bytes. Current14/14
misses mean this gate cannot adopt E1 or call it a pass. Its frozen bound is not
widened to admit either failed family; all existing stops retain their owners.

REPRODUCTION AND CHECKS

Python3.12 with numpy/PIL; run from this evidence directory. Recorded outputs are
write-once. For numerical verification without rewriting: replay.py --verify,
verify-scores.py, derived.py --verify, test-instrument.py, test-readers.py; identity-proof.ts --stdout
via pnpm exec tsx. Full regeneration requires a fresh evidence copy with its
repository-relative siblings, then replay.py, diagnostics.py, identify.py,
canonical.py, derived.py, closure-bars.py, summarize.py, static-audit.py. The
frozen declaration commit and hashes must still verify. No browser is involved.

Workspace install/build passed first. Full calibration48 files:690 passed, one
X1 skip solely because this fresh worktree has no canonical tree. The skipped
pixel check subsequently passed with VITREA_WEB_CAPTURES naming the read-only
main tree (one selected test;100 not selected, not newly failed/skipped work).
ESLint and all four calibration TypeScript checks pass. Frozen26.5:1818 before
and after. W34's inherited suite invokes its existing command-line harness
self-check; no native GUI bundle build/launch/capture/grant occurred. No holdout
payload, browser launch, src/profile/fixture/matrix/scene/canonical-capture write,
material improvement, runtime prototype, CSS render or seal is claimed.

Closing checks (beside the initial run): after adding the per-bin bar assertion,
the complete calibration suite was run with the read-only main tree available:
48 files,692 passed, NO skips. ESLint and all four tsc checks pass again.
freeze-after.txt:1818 intact. The initial scope audit compared against dispatch
snapshot efe6066e and saw the inherited tracker-only commit; the corrected audit
uses the actual branch parent7f254381. That tracker change is NOT this gate's.
No protected tracked path differs from the actual parent. Grounding numerical
pins are committed so derived.py --verify does not need the private memo files.

Whitespace check: only three preserved raw test logs have a final blank line;
whitespace-scope.json records the exceptions. No source/document whitespace
finding; raw logs were not rewritten to claim an unqualified clean check.

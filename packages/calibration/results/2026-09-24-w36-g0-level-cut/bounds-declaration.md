# W36 G0 frozen bounds — §5.178, clauses 1–6

Declared before the constrained fit and before its scratch render. These are stop conditions,
not new adopted rows; Decision Logs 1, 2 and 4 belong to the parent. No bound below can move in
response to the candidate. Expected values are hypotheses; the recorded candidate table will
state failures beside them. G0 does not authorise G1 by producing a candidate.

## L1 and its independent W34 referee

L1 population: macOS 27 standard glass0.5, both schemes and scales, WebGPU/texture,
canonical calibration and validation, every declared scene including tints and composites.
140 rows (49 per light profile; 21 per dark), without a shape-conditioning exclusion.
Estimator: absolute difference of `material.interiorMeanWeb` and `interiorMeanNative`,
mean linear Rec.709 luminance on the NATIVE silhouette bounded to the declared region.
Not a deep median. The native mask does not move when the web material moves.

Absolute bound 0.055; growth in absolute error <=0.005 from the pre-W36 W33 generation.
`l1-baseline.json` freezes its non-holdout numbers now. Light active document 6e509c7f76cc,
receded 45acb6d916b9; dark active eab099cc6698, receded 4e68f81869f6. After G1's split the
same rows must be read from `results/superseded/6e509c7f76cc.json` and
`results/superseded/eab099cc6698.json`. Those files do not yet exist: today these are the
working generation, not W32's older already-superseded generation. This naming freezes the
reference before fitting; G1 must not choose a convenient later baseline.

Today 136/140 have material means. The four dark inactive dark-solid capsule-button/rrect-md
cells (both scales) are UNMEASURED, never zero-error passes. New missing material rows stop
adoption; existing missing rows remain explicitly incomplete until the fixed native mask can
be measured. The two light `impulse__capsule-button__inactive-tint-orange` rows miss the
absolute bound at 0.066016126 / 0.066058940. They remain named misses, not floors or a 0.066
bound; growth applies to them too. Expected after Part A: those shade-model misses persist;
other measured rows <=0.055 and all growth <=0.005. A miss is not silently excused by a median.
Probes are diagnostic: including them changes the problem and gives misses as large as 0.192.

W34 is a SEPARATE referee. Every circular-120 uniform calibration/validation grey at both
scales, schemes and poses (56 cells), plus the admitted grey-128/255 cross-geometry cells;
black is included explicitly and grey-96 and continuous-160 remain validation, never fitted.
Use W35's per-channel median at d <= -6 CSS px; require >=4 deep pixels, otherwise UNMEASURED.
Tolerance max(1 encoded code, that cell's observed deep repeat bar); G0's inherited maximum
repeat bar is 0.5, so 1 code is the operative tolerance, not its unshrunk spatial envelope.
Censored channels (255 in either median) are excluded and named; full-RGB inversion excludes
an entire censored cell. Expected after a successful Part A: absolute uncensored channel
residual <=1 code, including black; zero black residual is the fitted target. Thick validation
is an extrapolation check and receives no wider tolerance. A constrained form that misses is
reported as a failure, not rescued by fitting validation or adding free thick ordinates.

MATERIAL-axis amendment for future adoption beside the gate header: level is directly
identifiable as two means on one fixed native mask, unlike fitted blur sigma; W34's black
misses of 28–49 codes and grey misses up to 10 codes exceed its <=0.5-code repeat bar.
The 0.055 canonical bound is far larger than one-code linear quantisation even at white
(~0.0089), not a sub-quantisation rim claim. Canonical means and W34 medians remain separate.
A native comparison fixed before fitting and an immutable pre-fit baseline make adoption
non-self-referential. This does not claim that every broader material sub-metric is identified.

## Identified fit and what is frozen

Per scheme/pose: one shared black level, identified by span-44 black only, with its cross-span
use explicitly extrapolated. It cannot be rendered with today's leaves. Existing-knot trial:
three shared thin/thick ordinate shifts, at knots 2, 3 and 4. Fit least squares in linear light
on non-black calibration greys and admitted canonical rrect-md neutrals; do not fit grey-96,
continuous-160, photo, impulse, checkerboard or text. Keep knot 1 and every abscissa frozen;
keep all thin-minus-thick differences frozen. This lower-dimensional family is a hypothesis,
not four independently identified thick ordinates. W34 span44 has sizeK 0.09228515625 and
thick weight 0.0239777478855. Canonical span96 has three neutral anchors in the declaration,
not an independent grey sweep (profile-specific absent cells stay absent); no thick black.
No retention, shade, size, scatter, lens, rim or shadow value changes in the Part A render.

## Other stops and their expected values

* Per-cell tables stay the 26.5 aliases, no new 27 floor. Expected colour/SSIM improvement on
  neutral greys; chromatic residuals persist because Part B is diagnostic. Shape extraction
  may change with dark level; count the predicate from the machine, do not preserve 67 by
  assertion. W29's 32->67 history is a warning, not a target. Existing eight MISSED_27_ROWS
  remain a measured set, never a permission for another miss. Its three light photo/rrect-sm
  M1 misses are expected to worsen under a lower light tone. CSS dark-photo P95 and other
  historical holdout entries are not re-read in G0; only G1's once-sealed holdout may decide them.
* M1: median [0.8,1.2], each cell [0.6,1.4] except the named existing misses. Current medians
  light active/inactive 1.049010884/1.022976822; dark 0.996608334/1.005977999. Part A's lower
  light level is expected to raise R, higher dark level to lower R; exact scratch readings
  are required. Retention-only Part B at r=.9 light/1 dark has OLD-tone secant expectations
  1.9848/1.76938/2.317745/3.5216, already outside the median stop. These are extrapolations,
  not predictions verified at Part A's tone. A plate-mean term has no nominated operator and
  therefore no defensible expected number: unidentified, not an assumed M1-preserving fix.
* M2: each photo cell's interiorStdDevWeb changes <=2% from the SAME pre-W36 generation
  named above, re-baselined at G1 as W32 DL4 requires. Expected delta 0 for a constant level
  shift in linear light; quantisation and solved opacity can violate that expectation, so
  read it. Table cumulative drift separately; do not use an old baseline to widen the stop.
* Structured read-only stops, including photo, impulse, checkerboard and admitted text:
  absolute level error <=0.055, growth <=0.005 from `structured-baseline.json` (probe text
  from `probe-level-diagnostics.json`); expected growth <=0, with lower light photo a known
  threatening case. No photo fit target. Require per-cell colour thresholds and the photo
  M1/M2 stops above. Exact canonical hc-text/rrect-md is HOLDOUT in both poses; it is refused.
  `hc-text-7__rrect-md__rest` is the separately named validation read, not that holdout.
* C1 <=0.0042 per admitted span, expected change exactly 0. X1 expected black exterior
  count exactly 0 and no new >1-code pixels. B1 existing sigma windows +/-5%, expected law
  values exactly unchanged. Show this through immutable shadow leaves AND same-native-mask
  exterior pixel comparisons on the rendered structured cells; at G1 regenerate full cuts
  and re-derive matrix bands. Body changes are not themselves proof of exterior identity.
* Tier coherence: GPU/CSS interior ratio [0.8,1.25], cross-tier mean OKLab DeltaE <=0.05;
  expected both tiers' response target equal, with the same black leaf and authority branch.
  G0's authorised renders are GPU only: numerical target identity is a plan, not a CSS
  measurement. G1 must read both tiers before claiming coherence.
* Tinted cells: shade law untouched; compare material.tintDeltaL{Web,Native}, level and the
  paired untinted rows. Expected existing light-inactive impulse shade gap remains, with
  no >0.005 growth in absolute level error. No negative shade fit is smuggled into tone.
* Receded flatness: expected spatially constant solid body remains flat under an ordinate
  shift (encoded deep max-min changes <=1 code); no rim or shadow is restored. Report
  native spatial envelope separately rather than mistaking it for a tolerance.

## CSS and identity route

Proposed flat gate `backdropToneBlackStrength`, literal identity 0, gates flat
`backdropToneBlackLevel`. Gate 0 executes today's branch exactly (smoothstep included).
At 1, full solve authority and a segment from (0,blackLevel) to the existing first knot;
above that first knot the response is unchanged. Shared black level is a cross-span assumption.
In platform-web/src/optics.ts thread the same two leaves through response constants and use
that same branch in toneRespondedSourceOptics. Preserve the alpha and collapse guards;
they guard divisions, whereas the removed fade preserves W9's impulse-domain behaviour.
The finite black ordinate must solve black without division by backdrop Y, respect [0,1],
join continuously at the first knot, and leave the gate-0 path bit-identical.

The identity script proves six digests in memory; it does NOT prove an unimplemented shader.
G1 appends the literal identity and named inertLawCase, sweeps gated levels at gate0, and proves
rendered/CSS identity before enabling it. CSS BODY_CHROMA_RETENTION remains0 until its mirror
is re-rendered at the candidate plate alpha on the same photo cohort: gain
1+r*alpha/(1-alpha), authored saturation1.8/1.4 fixed, retain only if it improves the native
chroma comparison without breaking L1/M2 or coherence. No CSS-only fitted cap.

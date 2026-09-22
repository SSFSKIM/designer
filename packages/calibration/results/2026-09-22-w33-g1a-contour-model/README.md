# W33 G1a — identification stops before a material fit

Claims **§5.171**. **No tested law closes; recommend Decision Log 3's stop-at-the-finding option.**
This gate supplies a falsified but composable candidate, not a material ready for G1b. No source,
profile, seal, matrix, native fixture or adopted threshold changes. No browser/native capture,
no holdout image read, no merge or publish. The optional scratch render was not used: rendering
an already-falsified colour law would not settle identification.

## What was measured

- G0's **304** non-holdout single-shape cells, **223,900** offset-one pixels. All six macOS 27
  profiles, both poses. The committed population is pinned by SHA and checked against scene
  membership before image access. `--include-holdout` retains G0's deliberate post-seal semantics;
  it was **not used**. No archival holdout census was rerun. Frozen controls are G0's recorded
  non-holdout notch readings, not a new measurement or a claim about frozen capture provenance.
- **456** angular strata: profile × pose × backdrop class × span × shape kind × part. Each of
  152 base strata has straight, arc and combined readings, in 16 nearest-normal bins at 22.5°
  steps. Coordinates use image y downward; 0° right, 90° bottom, 180° left, 270° top. Pixels
  enter once. Axis bins include near-axis arc pixels in the combined reading; they are NOT the
  pure straight-side means in G0. `angular.json` keeps each selected law's per-bin signed RGB,
  absolute RGB, fitted signed mean and signed residual; competing laws retain coefficients and
  error scores, with the unit-exponent shipped-diagonal diagnostic's bins beside.
- **5,472** radial rows, d ∈ [−2,−1), …, [3,4), in device pixels, separately on straight sides,
  their safe cores beyond the documented 1.528665-radius continuous-corner reach, and arcs.
  `coverage.py` additionally integrates an ideal annulus over an 8×8 pixel footprint on **26**
  available standard solid/capsule/md cells; every one is non-holdout.
- **400** refined colour strata (profile/pose/class/side), recombined into G0's **304** ceilings
  before applying those bars. Mid solids and other rasters are separate from dark-solid; the
  nine black-bearing rasters remain a class. `colour.json` keeps eight angular colour families
  per bed/pose and per refined side stratum, with channelwise residuals. A local fit is an
  optimistic diagnostic, NOT a permitted per-backdrop runtime switch.

**One byte is an encoding-resolution comparator, not a repeatability/noise bar.** No repeat
native captures exist for this angle/coverage instrument. “Closes” below means every populated
bin's signed channel-mean residual is ≤1 byte. This weaker diagnostic can fail before the
absolute per-pixel referee is considered; passing it would not establish fidelity.

## Angular finding

Tested constants, `|nx|^k`, `a+b|nx|^k` at k=.5,1,2,4,8, a one-sided diagonal light vector,
a shipped-diagonal unit-exponent factor, and an affine signed-normal field. Choose the fewest
coefficients among closures; otherwise show the smallest-error sampled family as **unclosed**.

| part | strata | closures under the diagnostic |
| --- | ---: | ---: |
| straight and arcs together |152|0|
| straight only |152|78|
| arcs only |152|3|

A two-term even response captures the axis contrast; no universal exponent or pose-independent
law is identified. Dark active photo/md's best sampled full profile is
`−2.678989 − 43.765422 |nx|^4`, with **14.762813** bytes worst bin residual. Its signed residuals
at 0°,22.5°,…,337.5° are:

`−0.26, +12.21, −7.91, −9.15, −0.68, −7.19, −3.19, +6.91, −4.19, +14.36, −2.15, −4.00, +2.04, −4.63, −0.86, +14.76`.

This is a diagnostic average, not a colour coefficient. The all-part winner is an
isotropic+even k=8 family on 81/152 strata: repeatedly selecting the grid's endpoint is NOT
an identified exponent. Straight-only fits cannot identify k at all, because |nx| is 0 or 1.

The shipped rim cannot produce the axis contrast **at any exponent**. Its declared diagonal
axis makes `(sqrt(2)*abs(dot(n,L)))^exponent` the SAME on four cardinal normals, and its
along-side field averages to zero on each straight side. G0's pure-side dark active photo/md
means are top/bottom **−0.353/−3.047**, left/right **−54.536/−50.488**. A common axis value has
at least **27.0915** bytes maximum residual on those four means (half their range). This is
independent of the unit-exponent diagnostic's ranking. The inactive capsule restores both
horizontal sides, **−29.566/−29.351**, so a capsule-wide disable is also wrong.

## Radial finding and uncertainty

On light-solid inactive safe straight sides, both scales put the notch in **[0,1)**, sampled
at **d=.5 device px**; native equals backdrop from the next row out. The nominal one-pixel
band has centre .5. Discrete centres alone do NOT measure its continuous boundaries: centre
precision is no better than ±.5 device px without a coverage model, and amplitude/width trade.

Capsules are the clean counterexample to interpreting every adjacent-shell residual as a
continuous-corner error. Their exact circular arcs have nonzero residuals in **[−1,0)** and
**[1,2)** from pixel-area coverage. On 1x light-solid inactive capsule the mean RGB residuals
in those shells are about **−9.06/−31.22/−5.70** for d bins −1/0/1; from d≥2 they are zero.
The 2x reading is about **−9.96/−28.31/−4.51**, also zero beyond d≥2. One device pixel of
geometric support can touch parts of three sampled shells; that is not three geometric pixels.

The 8×8 annulus grid (width .5,.75,1,1.25,1.5; centre 0,.25,.5,.75,1) on light-solid inactive
capsules selects centre **.5 at both scales and schemes**. Within best MAE+.5 byte, light
widths are **1–1.25**, dark widths **.75–1**. These are grid sensitivity intervals, NOT
confidence intervals or an identified universal width. Best full six-shell RGB MAE is
1x light **1.070/1.065/1.250**, still **2.427/2.392/2.381** in the offset-one shell itself.
The dark/backdrop-dependent fits move or hit the grid boundary; body mismatch is a confound.

Continuous md corners use the circular declared SDF as an instrument, NOT Apple's true
curve. Their best light-solid grid changes centre **.5 at1x → .25 at2x**, width1.25, where
capsule centre stays .5. At 2x light inactive the md best mean error is **2.98 bytes**, capsule
**1.63**. This supports the geometry/raster confound; it does not measure Apple's actual
continuous SDF or justify moving placement on straight sides. `radial.json` and `coverage.json`
keep every cell and every channel rather than fitting a radial width on a pooled notch.

## Colour finding and the candidate

No encoded/linear multiply, add, signed affine or tinted affine family closes, even after an
angular factor and optimistic per-side/backdrop fitting. The encoded/linear ordering changes
with stratum. No fixed blend colour, neutrality, tint or internal compositing space is identified.
Black-bearing inactive ring pixels brighten over backdrop black and darken over white on both
schemes. For example the light left-side class means are about **+37.4 RGB over black** and
**−138.3 over white**; these are the widened class, not §5.166's particular 0–6/156 transect.
A multiply cannot do both. Spatial sampling, native coverage and body colour remain confounded.

`candidate.json` declares one **falsified diagnostic family**, with coefficients in
`colour.json.models[].candidate`:

`T = clamp(W + gate * ((m0 + q*m1)*W + b0 + q*b1), 0, 1)`

where W/T are encoded RGB, `q=abs(dot(normal,axis))^k`, support d∈[0,1). Choose k on angular
errors, equally weighting full strata within each profile/pose, BEFORE fitting colour. Do not
choose a different runtime law per backdrop. k is2 for dark active,8 for the standard other
endpoints; accessibility diagnostics differ. The colour coefficients are still fit separately
at each scale, so **this is not a dpr-independent material proposal**. The binary support is the
price experiment, not a claim to reproduce the antialiased native annulus.

The **17 flat leaves** are gate `contourStrokeAlpha` (identity0), width in DEVICE px, centre in
DEVICE px, normal exponent, axis radians, and twelve channel leaves: Multiply/Add ×
Isotropic/Anisotropic × R/G/B. Matrix columns in the diagnostic fit are m0,m1,b0,b1.
The identity gate bypasses the entire colour/coverage solve, preserving original bytes.
`identity-proof.ts` extends G0's actual rule-2 path drop in memory. Six documents × sixteen
leaves × five sweep values = **480** gated sweeps, plus six width sweeps per document. Both
frozen digests and all four27 digests stay exactly their recorded values. Nonzero gate is not
silently dropped. This is a digest proof, **not a shader inertness test**; no shader was written.

WebGPU could use its existing signed distance/normal, build a target and solve valid
premultiplied coverage. CSS's uniform border/inset can carry an isotropic approximation, not
the measured angular response. A future CSS experiment must compare a dpr-aware inset with
side-separated approximations on solids, photo and checkerboards, including capsule arcs at
1x/2x, and read both G0's referee and dom bounds. No mirror or decline is asserted without that
experiment. Accessibility treatment remains G0's independent term, no forced-colours body.

## Two prices, not two implementations approved for shipping

`prices.ts` extends G0's real metric functions. It proves baseline shape and linear-departure
agreement against the matrix before changing pixels. Exact replacement solves the **minimum
finished coverage** over the backdrop, never confuses it with a new source-over stroke's alpha:
`A=max(oldA,ceil255(required(T,B)))`, `P=T−(1−A)B`. Cap previously sub-threshold A at **127/255**
for the other construction and project P into [0,A]. Round RGBA8 before compositing; the exact
branch reaches its integer target byte-for-byte. Gate zero would return the original pixel.

| construction | cells / conformance cells | broad contour / IoU failures | selected contour / IoU | distinct red cells broad / selected | ring MAE |
| --- | ---: | ---: | ---: | ---: | ---: |
| candidate, exact |304 /298|36 /14|2 /1|42 /2|18.1383|
| candidate, capped |304 /298|0 /0|0 /0|0 /0|18.4324|
| native-colour oracle, exact |386 /380|40 /45|19 /22|58 /24|0|
| native-colour oracle, capped |386 /380|0 /0|0 /0|0 /0|3.4464|

“Selected” is the adopted active non-probe selection, intersected with non-holdout measured
cells; candidate52 cells, oracle85. These are texture matrix rows, one per (profile,scene),
not two render tiers. Candidate exact would red **50 metric assertions on42 rows**, selected
**3 assertions on2 rows**. Oracle exact would red85 assertions on58 rows, selected41 on24.
The full unread holdout population is NOT projected. Six candidate cells have no conformance
axis under the production refusal; their null values are never labelled failures or passes.

Candidate baseline MAE **34.9791 →18.1383**, yet **52/304 G0 ceilings fail**. Capping loses
**.811/.909/.661 RGB bytes** against that target and has infeasible target pixels on120 cells.
Exact contour max√2, minIoU **.971292**. The oracle's minIoU **.945652** and cap loss
**3.271/2.602/4.466 RGB** describe freedom to choose every pixel's colour, NOT a material law.
Its296 infeasible cells include the six no-conformance cells; on G0's380-cell subset the count
is290, reproducing the review's population. Neither oracle is fed into a colour fit.

All four constructions leave area, body count, conditioning, and native-mask pixels unchanged:
**0 predicate moves, 0 touched M2 pixels**. `prices.json` lists every cell; `tables.json.prices`
lists losses and residuals by profile/pose/backdrop/span/kind. All offsets2–6 stay byte-identical
in these support-limited counterfactuals, including their pre-existing errors. This deliberately
leaves the arc's neighbouring-shell residual unresolved. A full antialiased term could enter
M2's ring and would need a NEW price, not inherit this zero-touch statement.

## Stops and decision

Stroke-only C1 change0 on all twelve rows (0.00088–0.00391 against.0042); thin change0 against
.002044; the inherited accessibility worst.02168 is not repaired. B1's six law values remain
light8.9600/13.1648/17.3696 and dark9.0400/12.9280/16.8160. Admitted B3 remains
**.00005596255774381109**, inactive half exactly0. Lift/anchor compensation has not run and
has no new forecast here. The warning, recomputed in linear light on the same166 rows:

| construction | whole .00071581358 → | inactive .00079671936 → |
| --- | ---: | ---: |
| candidate exact |.00032105718|.00038795541|
| candidate capped |.00031909808|.00038307209|
| oracle exact |.00006889629|.00005457293|
| oracle capped |.00008458555|.00007259456|

Candidate forecasts change only100/166 in-domain cells and explicitly HOLD the other66;
oracles cover166. No omitted row is treated as zero. Even exact offset-one native colours
cannot make the warning vanish: the radial remainder is outside this experiment's support.
M2: outside0 touched pixels; G0's inside alternative touches257–1,311 on all26 cells. A real
antialiased corner term must be priced afresh. Goldens were not run; at gate0 the declared
`inertLawCase` is a direct byte-preserving bypass, not an assumed nonlinear cancellation.

**Decision Log 3 draft, not a ruling: stop the contour term at this finding.** Do not widen
contour/IoU for a family that still fails52 ceilings, and do not adopt the cap merely because
it keeps shape: it limits a target whose law is still unknown. The alternatives remain exact
placement with both bounds reconsidered, or the cap with measured loss, AFTER identification.
The next identifying capture would hold geometry fixed with a circular capsule, vary uniform
grey and RGB backdrops, repeat measurements, and sweep subpixel phase at1x/2x before comparing
continuous rectangles. That separates angular response, pixel-area coverage and colour. It
requires a new authorised native capture/split plan; X5 forbids doing it in this gate.

## Reproduce and limits

Set `VITREA_WEB_CAPTURES` to the main checkout's read-only canonical tree. Run `model.py` with
python3.12, then `coverage.py`, `prices.ts` via calibration's `tsx`, `identity-proof.ts`, and
`tables.py`. These write ONLY beside themselves (or model's `--out`); use an isolated copy
for a later-generation reproduction, never overwrite historical outputs. No screenshot is
needed. Close checks are in `calibration-tests.txt`, `test-focused.txt`, `freeze-verify.txt`.

This gate does not claim an Apple shader, a closed colour law, a native noise bar, a universal
angular exponent, an exact continuous-corner curve, a CSS mirror, accessibility behaviour on
unmeasured beds, a whole-bed post-seal count, or a rendered candidate. It does not claim all
possible laws are refuted. It refutes these measured separable families, documents the
coverage ambiguity, and leaves the fitting gate blocked rather than inventing a fit.


**Close verification:** calibration644/644 across42 files, focused6/6; frozen1,818 intact.
The initial lint attempt rejected twelve `any` annotations in the new test; they were replaced
with evidence interfaces. `calibration-lint-fixed.txt` is the successful eslint/four-tsc run;
`calibration-lint.txt` preserves the initial diagnostic rather than being passed off as green.
The parent still needs to review this evidence; G1a was explicitly forbidden to dispatch agents.

The final prices inventory itself excludes holdout, not merely its pixel loop:380 conformance
cells,216 at contour1; selected85,30 at1. Of26 M2 cells,22 are in the candidate domain and four
are held unchanged, while the oracle covers all26. This qualification is separate from the
0-pixel-touch result. `prices-final.txt` records the final run; no measured price changed when
the inherited G0 archival metadata inventory was restricted to this gate's non-holdout scope.

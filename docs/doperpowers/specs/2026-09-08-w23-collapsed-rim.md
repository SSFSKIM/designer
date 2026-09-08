# W23 — the collapsed rim: a rim that survives the collapse, and the rim's law read at the contour on both beds (2026-09-08)

**Status: G1 DECLARED and READ 2026-09-08 (claims §5.101 by G1, §5.102 the parent's ruling; Decision
Log 3) — chartered 2026-09-08 from W22's Deferred list ("the collapsed rim", W22 Decision Log 4 (d);
claims §5.96 §4) and the user's eye on the W22 landing sheets (claims §5.99). G0 CLOSED (§5.100;
Decision Log 2). G1's dry run met the rim on every collapsed cell and the law on every solid, missed
clause 3 on the left/right sides under structure and clause 4 on the band read (the corners), and the
eye on its captures found the painted rim's hue wrong — Apple's rim on a tinted surface keeps the
paint's chroma, vitrea's adds white — so G3 (the rim beneath the paint) is inserted before the
landing; G1's holdout read is recorded as spent on a superseded configuration. G3 dispatched.**

Composite spec: design at the top; Decision Log, Surprises, Deferred and Revision Notes at the
tail. Parent: `2026-08-28-post-v1-wave.md` (the W23 row). The term it takes was deferred twice
under one name — W21 Decision Log 2 (b) at +0.017 on the dark bed's collapsed `rrect-sm`, W22
Decision Log 4 (d) at 0.031–0.093 on eighteen sides of three light cells — and this charter's
grounding found the name covered two mechanisms on one term (Decision Log 1 (a)). The rim it
re-reads is the ambient rim W11c fitted, W22 read per side and fitted `specularGain` 0 on
(`optics.regular.rimAlpha`, `rimWidth`; the dark patch's `rimAlpha` 0.082, W21 G1). The
thick-span composite (wave Decision Log 23 (c)) is the larger piece after this wave, on the user's
word.

## Purpose

Apple's glass on black is visible; vitrea's is not. On the dark bed's `dark-solid` capsule the
reference draws a body one code below its backdrop and a contour rim of +0.020 linear (55/255 on a
28/255 backdrop at 2x), and vitrea draws the backdrop: the tone collapse (`backdropToneLow` 0.02 /
`backdropToneHigh` 0.055, W7) folds the body AND the rim onto the sampled backdrop through the
shader's one `present = 1 − toneAdapt` factor, on the strength of a W7 reading that the settled
reference's collapsed capsule was "byte-identical to its background, rim included". Under the
contour read it is not: the reference keeps a rim under collapse, and the rim it keeps is the dark
material's (`dark-solid__rrect-md` in the dark scheme, uncollapsed: +0.026). The light and dark
fixtures of the collapsed capsules are byte-identical (`dark-solid__capsule-button` at both
scales, `impulse__capsule-button` at 1x; two pixels at ≤ 2 codes at 2x) — Apple's collapsed
appearance is one appearance in both schemes, which is W22's "the collapse and the appearance term
are one axis" seen from the fixtures' side.

The three light cells W22 deferred under the same name (`dark-solid__rrect-md`, `impulse__rrect-md`,
`mid-dark-solid__capsule-button`, eighteen sides 0.031–0.093 too dim) are not collapsed cells at
all: the size bias holds the thick surfaces' collapse argument above `backdropToneHigh` (the W9
re-scope in `material.ts`), `present` is 1 on all three, and the rim is drawn in full. Their miss
is the rim's amplitude law. Read at the contour, per pixel, in linear light (claims §5.99;
`results/2026-09-08-w23-collapsed-rim/finding/contour-table.txt`), vitrea's rim is the same
+0.060…0.078 on every light cell — the shader adds `rw × rimAlpha` and nothing scales it — while
the reference's is +0.23…0.26 over the dark solids, +0.13…0.21 over the structured backdrops and
clipped to white over `light-solid`, 3.4–4.0× vitrea's where the backdrop is dark and 1.3–1.7×
where it is bright. Over the solids a white line composited source-over at 0.41–0.45 of the body's
headroom reproduces the three dark cells within 2 %; over `light-solid` that alone leaves the
contour row at 0.982 where the reference reads 1.000, so a second, backdrop-fed term is there too
(the reference's only top-over-bottom split is over bright backdrops — §5.94 §3). The W22 G0 fit
that declined `rimAlpha` read the rim through the declared box's 3 CSS px band, whose peak-row mean
over a dark backdrop carries the corners' backdrop and dilutes the line; the leverage it measured on
the dark cells (0.019–0.049 per unit `rimAlpha` against 0.22–0.35 over `light-solid`) was that
dilution. The decline stands on that instrument and is corrected beside it here, not rewritten.

The two are one wave because they are one term: the rim under collapse is the dark material's rim,
the dark material's rim over a dark backdrop is what vitrea already draws (1.5× too bright on the
thick cell, 1.6–1.7× too dim over the structured backdrops), and the light material's rim over a
dark backdrop is what the same law must give at the other end. This wave reads the rim at the
contour on every cell of both beds, fits the law that reproduces it on the solid cells and checks it
on the structured and validation cells, gives the collapse a rim that survives it, lands both on the
GPU tier with the CSS tier deriving, rebuilds the bed and reads every rim row and floor, and puts
the black-on-black cells in front of the user's eye.

## Parent-Level Acceptance

Binding. The numbers are the charter's; G1 re-declares them with G0's readings beside. The
instrument is X1's contour read: the excess over the body summed over the first two CSS px inside
each side's contour, linear light, per CSS px; W22's band read reported beside it.

1. **Glass on black is visible.** On every collapsed cell of the bed (`dark-solid__capsule-button`
   in both schemes, `impulse__capsule-button` in dark, W21's probe `dark-solid__rrect-sm`) vitrea's
   contour rim is within 0.005 of the reference's (+0.020…0.021) on every side, and its body is
   within 0.002 of the reference's (one code below the backdrop). The user sees the outline on the
   2x dark sheet.
2. **The rim's law on the solids.** On every untinted texture-tier cell over a solid backdrop at
   both scales in both schemes, vitrea's contour rim is within 0.03 of the reference's per side
   (today 0.16–0.19 short on the three light cells; 0.010–0.014 over on the dark thick cell), and
   where the reference's contour row clips to 1.000 (`light-solid`) vitrea's does too. `L−R` within
   0.003 as W22 left it.
3. **The law holds off the solids.** On the structured calibration cells (`checkerboard`, `photo`
   at every component) the contour rim is within 0.05 of the reference's per side, and on the
   validation cells (`impulse__rrect-md`, `impulse__capsule-button`, `photo__rrect-sm`) no worse
   than the calibration cells' mean miss — the law was fitted on the solids and must not be a fit
   to them alone.
4. **The band read closes.** Under W22's per-side band read (clause 2 of W22), the eighteen sides
   on the three light cells come within 0.03 of the reference; no side that met W22 clause 2 leaves
   it.
5. **The bed no worse anywhere.** At both scales on the GPU tier: calibration ΔE mean not above
   the W22 bed's by more than 0.0001 in either scheme (W22 Decision Log 4 (b)'s tolerance); no
   untinted row worse by more than 0.001 in ΔE mean or 0.005 in `ssimMean`; every `rimPeakLuminance`
   / `rimFwhm` row moved recorded with its direction; no adopted bound widened; every floor re-read
   — a floor whose cell recovers goes inert and is removed with its reason, none re-pinned without
   the user.
6. **The holdout once**, at G1's dry run on the frozen configuration, both schemes, both scales;
   G2 reproduces byte for byte.
7. **The goldens attributable.** The rim moves every optics golden; each is re-recorded under the
   isolation proof with the rim's law and constants as the sole reason (the proof's ladder shows
   the change confined to the rim band); a golden that moves for any other reason stops G1.
8. **The CSS tier derives.** The CSS tier's inset rim already composites a white line source-over
   (the screen form); it takes the same constants through `optics.ts`'s mirror and the collapsed
   rim's floor through the same `(1 − k)` seam, with `tier-coherence` pinning the two tiers; every
   CSS mover explained.
9. **By eye, and the ledger.** The landing sheet (native | GPU before | GPU landed | CSS landed) at
   both scales on the solids in both schemes with the black-on-black cells at 4× zoom beside;
   the user's veto kept. **0.12.0** after the landing (a `vitrea-web` minor: the material moves).

## Grounding Baseline (the W22 bed, 2026-09-08, matrix at `3587400`)

- Light GPU calibration ΔE 0.00330 / 0.00333 (1x / 2x), holdout 0.0091; dark GPU calibration
  0.00404 / 0.00403, holdout 0.01326 / 0.01301 (claims §5.97–§5.98). `PREDICATE_EXCLUDES` 29,
  `UNMET_ROWS` 11, eleven floors (four W21 instrument floors on the 2x dark nested pane).
- The contour read (`finding/contour-table.txt`, `contour-profiles.txt`; the parent's script
  `contour-profile.py`): the tables in the Purpose. The reference's rim is one CSS px wide with an
  inner shoulder (2x: rows 0.744 / 0.629 linear over a 0.481 body on `dark-solid__rrect-md`;
  vitrea 0.610 / 0.532 over 0.492); vitrea's `rimWidth` 1.5 CSS px with the squared falloff puts
  69 % / 25 % of its peak on those two rows against the reference's 100 % / 56 %.
- The collapse: `optics.ts` line ~876 `present = 1.0 − toneAdapt`, multiplying the inner shadow,
  the rim and the specular; `material.ts` `backdropToneLow` 0.02 / `High` 0.055 / `SizeBias` 0.05
  / `Max` 1 (W7, re-scoped W9: full at `dark-solid` for thin surfaces, zero for thick ones by the
  bias); the CSS mirror `optics.ts` line ~555 `rimAlpha: source.rimAlpha * (1 − k)`; the CSS rim an
  inset `box-shadow` on the overlay layer (`css-tier.ts` L3, `borderAlphaPerRimAlpha`).
- The rim constants: light `optics.regular` `rimWidth` 1.5, `rimAlpha` 0.18, `specularPower` 6,
  `specularGain` 0 (W22), `highlight` white; the dark patch `rimAlpha` 0.082, `specularGain` 0;
  `clear` 1.25 / 0.14 / 0.45 (no rows on the bed).
- The dark bed's solid cells at the contour: `dark-solid__rrect-md` rim +0.0258 native / +0.0367
  web (1x), +0.0257 / +0.0399 (2x); `mid-dark-solid__capsule-button` (holdout) +0.0412 / +0.0364;
  the structured cells +0.058 / +0.036 (`checkerboard__rrect-md`), +0.059 / +0.035 (`photo`). The
  dark thick body over `dark-solid` 0.0130 against 0.0153 (three codes; W21 clause 1 met at 0.010).
- The fixtures' identity: the collapsed capsules' light and dark fixtures are the same bytes.
- W21's probe bed (`results/2026-09-06-w21-dark-scheme/probe/`, read by `g0/rim.txt`) carries the
  dark reference over `dark-solid`, `mid-dark-solid` and `light-solid` at three sizes — the dark
  law's fitting ground, not holdout — and W9's light probe snapshots carry the light reference on
  the same grid.

## Design (advisory unless marked)

**The instrument (binding).** The rim is read at the contour: for each side, the rows (top,
bottom) or columns (left, right) from the declared box's first pixel inside the shape inward, the
excess of each over the cell's body (W21's eroded box) in linear luminance, summed over the first
two CSS px and divided by the scale — one number per side in the units of `finding/contour-table.txt`,
with the first row's own excess and the reference's clip state reported beside. The straight span
only: the corner arcs are excluded by the component's radius so the read is not the band reader's
corner mixture. Validated by injection (a synthetic one-pixel line of known linear amplitude on a
copy of a capture reads back within 0.001) and against the parent's `contour-profile.py` on the
cells it read. W22's band read runs beside it wherever a clause of W22's is re-checked.

**The collapsed rim (binding as to shape; the constant G0's).** The collapse keeps a rim. The
shader's rim term becomes `rw × (rimAmplitude × present + rimCollapsed × toneAdapt)` — the
scheme's rim fading with the adaptation as now, and an absolute rim the collapsed appearance owns
rising with it — so that at `toneAdapt` 1 the surface draws the backdrop with a rim of
`rimCollapsed` and at 0 nothing changes. One constant in `DEFAULT_MATERIAL_PROFILE`, not in the dark
patch: the collapsed appearance is one appearance in both schemes (the fixtures are the same bytes),
so the constant is the material's and the dark patch inherits it. Its value is the reference's
collapsed contour rim (+0.020…0.021 per CSS px on the capsules, +0.017 on W21's `rrect-sm`), which
G0 reads against the dark material's own rim on the same backdrop (`dark-solid__rrect-md` +0.026):
if the two agree within the read's precision, the collapsed rim IS the dark rim and the constant is
expressed in the dark rim's units. The CSS mirror takes the same floor through its `(1 − k)` seam
(`rimAlpha × (1 − k) + rimCollapsed × k`). The inner shadow stays folded out under collapse (nothing
in the read says otherwise). The body's one code below the backdrop is the collapse's own level and
is read, not chased, unless one constant on the collapse's mean pull takes it inside the stops.

**The rim's law (advisory; G0 decides the form).** vitrea's rim is additive-constant and the
reference's is not. The candidates, each to be fitted on the solid calibration cells of both beds
(light: `dark-solid__rrect-md`, `light-solid__{capsule-button,rrect-md,rrect-ml}`; dark:
`dark-solid__rrect-md` and W21's probe grid over `dark-solid` / `mid-dark-solid` / `light-solid` at
three sizes) and checked on the structured calibration cells and the validation cells:

- (L1) additive with a larger amplitude (`rimAlpha` × 3.4–4.0 in light): refuted on the light bed's
  structured cells at the parent's read (0.13–0.21 where 0.23–0.26 is predicted) unless the
  structured cells' contour base — the lens's outside sample at the edge — accounts for the
  difference; G0 reads that base from the reference's own neighbouring rows before ruling.
- (L2) screen: a white line composited source-over at alpha α of the body's headroom, `rim =
  α × (1 − body)`. Fits the three light dark-backdrop cells within 2 % at α 0.41–0.45 and the
  structured cells at 0.37–0.55; leaves `light-solid`'s contour row at 0.982 against 1.000. The CSS
  tier's inset rim is already this form.
- (L3) screen plus an environment term: `α × (1 − body) + κ × outside`, the second term the
  backdrop just outside the contour, which is what the reference's bright-backdrop-only top/bottom
  split and its `light-solid` clip both point at, and what the dark rim's growth with the backdrop
  (0.026 over `dark-solid`, 0.041 over `mid-dark-solid`, 0.058 over the structured backdrops at a
  body that barely moves) reads as. Two constants per scheme at most; κ shared across schemes if
  the rows allow.
- (L4) any better law the data suggests, with the evidence.

The form is chosen on the solid rows (they are clean: the base is the body and the outside is the
backdrop level), and the rule is C9a §6.2's — a constant whose rows do not separate it is not
carried. The dark patch's `rimAlpha` is re-fitted on the contour under the chosen law (it is 1.5×
over on the thick solid and 1.6× under on the structured cells today, which a backdrop-fed term
would reconcile and a scalar cannot); `rimWidth` is read on the 2x rows (the reference's 100 % /
56 % against vitrea's 69 % / 25 %) and moved only if its rows move it. The specular stays at 0 on
the light profile (W22); the `clear` variant has no rows and does not move.

**How G0 fits without guessing (advisory).** The law is implemented in a worktree behind profile
constants (`rimLaw` selectable, α / κ / `rimCollapsed` as constants), and a short ladder is captured
in scratch on both beds at both scales on the GPU tier — W22 G0's method — so every fit is on
vitrea's actual pixels through the actual pipeline, not on an arithmetic prediction (the memory
note "a number that reproduces is not a mechanism until the pipeline is shown to hold it"). The
goldens are run at every point of the ladder; the isolation proof's attribution is the evidence
that only the rim moved.

**What ships.** `material.ts`: the rim law's constants with their rationale, `rimCollapsed`, the
shader's rim term; `optics.ts` (CSS mirror) the same two seams; the light profile document's hash
and `$comment-w23`; the dark patch only if its rows move it (`dark-profile.ts` regenerates, W21 X7);
the ten goldens re-recorded under attribution; `tier-coherence` and a renderer unit test on the
collapsed rim (gain at `toneAdapt` 0 / 1 / between); `adopted-thresholds` re-derived at G2.

## Children

### G0: The contour instrument, the rim read on both beds, the law fitted on the solids — spike (deliverable: findings)

- **Purpose:** (a) the instrument as the design binds (`read-contour.py`, validated by injection
  and against the parent's `contour-profile.py`); (b) the read on every untinted cell of both
  canonical beds at both scales, native against the landed captures, per side, with the band read
  beside — tinted cells reported as context; W21's probe bed and W9's light probe snapshots read the
  same way; (c) the collapsed rim: the collapsed cells' contour against the dark material's rim on
  the same backdrop, the fixtures' byte identity across schemes stated, the body's one code below
  the backdrop read; (d) the law: the candidates implemented in a worktree behind profile constants,
  the ladder captured in scratch on both beds (the GPU rule), each candidate fitted on the solid
  calibration rows and checked on the structured and validation rows with the structured cells'
  contour base read from the reference; (e) the dark thick body over `dark-solid` (three codes)
  read beside and its constant named if one separates it; (f) `g0-findings.md` — the tables, the
  law's verdict with the constants and a prediction per cell, `rimCollapsed`'s value and whether it
  is the dark rim, the goldens' attribution at every ladder point, the shape of the shader and CSS
  change for G1, and a Decision-Log-2-shaped recommendation.
- **Acceptance:** the instrument validated; the read on both beds; the fit tables with the
  separating rows named; the goldens attributed; nothing canonical written; the findings file; the
  claims section written by the parent from it.
- **Edges:** none. **Track:** spike; one worker in a worktree; findings, not the spec. The GPU is
  shared — one capture process at a time; the calibration server's port and the capture pgrep
  clear before every run.

### G1: The mechanism landed and the form declared and dry-run — controlled

- **Purpose:** the collapsed rim and the rim law as G0 recommends and Decision Log 2 rules, on
  main: shader, material, the CSS mirror, the unit tests, the goldens re-recorded under attribution;
  the constants fitted per G0 with `resolvedMaterialSha256` moved on any profile document that
  moves, with the reason; the dry run on both canonical beds at both scales on both tiers with the
  holdout read once (the frozen configuration), the gate run over the scratch matrix, the sheet with
  the black-on-black cells at 4× zoom, the declaration in claims before any landing capture.
- **Stops:** (S1) any untinted row worse than the W22 bed by more than 0.001 ΔE mean or 0.005
  `ssimMean`; (S2) any tinted cell moved by more than 0.002 in body; (S3) a calibration ΔE mean above
  the W22 bed's by more than 0.0001; (S4) a golden moved for any reason but the rim — the
  attribution failed; (S5) a fitted constant whose rows do not separate it; (S6) a CSS capture moved
  without an explanation; (S7) a collapsed cell whose body moves by more than 0.002; (S8) the user's
  eye.
- **Acceptance:** the claims section; the sheet sent; the stops dispositioned in a Decision Log.
- **Edges:** blocked-by G0. **Track:** controlled.

### G2: The landing and its referee — controlled

- **Purpose:** merge; the canonical rebuild from the main checkout (`rm results/matrix.json`
  first — the light profile's hash moves; both tiers, six profiles, `--alpha`, calibration and
  validation before the holdout); the referee — every capture against the dry run byte for byte;
  the gate — every rim row and floor re-read, inert floors removed with their reason,
  `PREDICATE_EXCLUDES` re-derived (the web silhouettes on the collapsed cells may change: a rim
  where there was none); the demo's calibration figures and its harness fixture; the landing sheet;
  the user's eye; the changeset (a `vitrea-web` minor, 0.12.0).
- **Acceptance:** clauses 1–8 and 9 of the parent's; the chain green; the claims section.
- **Edges:** blocked-by G1. **Track:** controlled; the landing is the user's call.

### G3: The rim beneath the paint — the painted surface's rim keeps the paint's hue — controlled (added by Decision Log 3)

- **Purpose:** on every tinted cell the reference's contour rim is the paint's own colour lifted in
  luminance with its chroma kept, and vitrea's is white added over the paint. At 2x in light, the
  contour row over the straight top span (mean RGB): `dark-solid__capsule-button__rest-tint-orange`
  native body (255, 148, 0) → rim (254, 188, 0) — blue stays 0 — against vitrea's (255, 192, 130) at
  G1 and (255, 149, 0) landed (collapsed, no rim); `photo__…-tint-orange` native (231, 134, 0) →
  (246, 189, 16) against G1's (255, 197, 153) and the landed bed's (247, 163, 99);
  `checkerboard__…-tint-blue` native (8, 120, 236) → (59, 199, 248) against G1's (145, 183, 255).
  The reference lifts the green channel of an orange paint by 27 % and leaves blue at 0: its rim
  passes through the paint, or is scaled by it; vitrea's rim is composited after the author's
  colour (the optics pass adds the rim last). Find the composition that reproduces the hue — the
  rim's light beneath the author layer, or a luminance lift the paint's colour scales — on the
  tinted calibration rows (seven light, three dark) with the tinted validation rows as the check
  (`checkerboard__capsule-button__rest-tint-blue`, `photo__rrect-md__rest-tint-orange`); re-read
  the painted rim's amplitude law under it (`rimCollapsedTinted` 0.337 and the material-level input
  were fitted with the rim over the paint and are replaced if the mechanism makes them redundant);
  the collapsed painted cells' +0.115 orange / +0.176 blue read against the mechanism's prediction.
- **Binding:** on every tinted calibration and validation cell at both scales, the contour row's
  chromaticity (OKLab a, b of the straight-span mean) within 0.02 of the reference's and its
  luminance rim within the tinted bindings of Decision Log 2 (c); no untinted capture moves (the
  mechanism reaches painted pixels only — byte identity on every untinted cell is the proof); the
  goldens attributed as X2; then the dry run again on all six profiles and both tiers with the
  holdout read once on the final configuration — G1's read at `ee0010558553ee12` /
  `afd0e999e2f5813e` stands on the record as a read spent on a configuration not landed.
- **Stops:** G1's S1–S8; (S9) a tinted cell whose luminance rim leaves Decision Log 2 (c)'s binding;
  (S10) any untinted capture moved.
- **Acceptance:** the hue clause; the tinted rows; byte identity elsewhere; the dry run's clauses
  re-read; the sheet with the tinted capsules at 4× beside the black-on-black cells; the claims
  section by the parent from the findings.
- **Edges:** blocked-by G1; blocks G2. **Track:** controlled; the G1 worker, on G1's branch.

## Cross-Child Contracts

- **X1 — the instrument.** The contour read is the rim definition on every gate in this wave;
  W22's band read is reported beside it wherever a W22 clause is re-checked. The straight span
  only; two CSS px; linear; per CSS px.
- **X2 — the goldens attributable.** At every ladder point and at G1 and G2 the isolation proof
  names the rim as the sole reason for every golden that moves.
- **X3 — the holdout once**, at G1's dry run on the frozen constants; G2 reproduces byte for byte.
- **X4 — one appearance under collapse.** `rimCollapsed` lives in the material, not the dark
  patch; a reading that separates the schemes under collapse is a `[parent-impact]`, not a second
  constant.
- **X5 — the CSS tier derives.** The same law and the same floor through `optics.ts`'s mirror;
  `tier-coherence` pins them; a CSS-only residual is recorded, not chartered.
- **X6 — by eye.** The sheet at W21's zoom plus the black-on-black cells at 4×: native | GPU
  before | GPU landed | CSS landed, both scales, both schemes.
- **X7 — one source.** A dark patch that moves regenerates `dark-profile.ts`; the two W21 tests
  pin it.

## Ordering & Dependency Map

G0 → G1 → G3 → G2 → the 0.12.0 cut (G3 inserted by Decision Log 3). After this wave: the thick-span composite (wave Decision Log 23
(c)) on the user's word; the appearance switch carries whatever this wave's collapse work leaves
it. The GPU is shared; one capture at a time.

## Risks & Mitigations

- **The law is undetermined from the desk.** Seven contour reads and two candidate laws each fit
  most of them; the solid rows of both beds and the probe grids are the discriminating data, and
  G0 fits on vitrea's own ladder captures, not on predictions. A law that needs more than two
  constants per scheme is a finding, not a fit.
- **The rim moves every cell.** Every light capture with a rim moves; the floors and the predicate
  are re-read at G2 as W22 did, and the tolerance on the calibration mean is W22's 0.0001.
- **The collapsed cells' silhouettes.** A rim on a surface that drew nothing changes the web
  silhouette; `PREDICATE_EXCLUDES` is re-derived, not edited.
- **The band read and the contour read disagree on purpose.** W22's clause 2 is re-checked on its
  own instrument (clause 4) so the two readers' verdicts are both on the record.
- **No native probe this wave** — every reference read is from committed fixtures and the two
  probe beds; the console lock is not in the path.

## Deferred / Out of Scope

- **The thick-span composite** (wave Decision Log 23 (c)) — the base pane's haze; the user's eye
  named it again on the W22 sheets ("Apple's bottom glass is very slightly less transparent").
- **The appearance switch** (W21 / W22 Deferred) — the dark thin cells over structured backdrops;
  the collapsed rim may be its rim, and G0's read of the collapsed cells is handed to it.
- **The dark thick body over `dark-solid`** (0.0130 against 0.0153, three codes) — read in G0;
  taken only if one constant on the dark law separates it inside the stops, else carried with its
  number.
- **The environment term** — declined at G0 (Decision Log 2 (a)): worse than the affine law on
  the reference in both schemes (0.0105 / 0.0042 against 0.0081 / 0.0013) and separated by no row on
  vitrea's side (0.0005 per 0.10 of gain). The reference's dark rim grows 0.026 → 0.041 → 0.055 →
  0.103 across `dark-solid`, `mid-dark-solid`, the structured backdrops and `light-solid` at a body
  that moves a twelfth as much; the affine law carries it through the body, a proxy. A bed with a
  mid-bright solid backdrop under a light-scheme thick surface would tell the two apart.
- **The probe grids as a harness capability** — W9's and W21's grids are the only fitting ground
  for a two-constant law on either material; G0 rendered them through a gate script.
- **`light-solid`'s second contour row** — 53 % of the peak in the reference against −6 %; once
  the first row clips no metric on the bed reads it.
- **The `clear` variant's rim** — no rows on the bed.

## Tracking Map

| child | status |
| --- | --- |
| G0 — the instrument, the read, the law | CLOSED 2026-09-08 (claims §5.100; branch `worktree-agent-aa0ee5ea92534c3fd` at `499f7c0`, carried into G1's worktree; Decision Log 2) |
| G1 — the mechanism landed, the form dry-run | DECLARED 2026-09-08 (claims §5.101; branch `worktree-w23-g1`; the holdout read once at fingerprints `ee0010558553ee12` / `afd0e999e2f5813e`) — clauses 1 (rim), 2, 5, 6, 7 and 8 met; clauses 3 and 4 missed with their numbers; stops S2 and S3 fire at the fifth decimal; the parent's calls are in `g1/g1-dryrun.md` §10 |
| G2 — the landing and its referee | — |

## Decision Log

### Decision Log 1 — the cut, the instrument, and what the user decides (2026-09-08; the parent, on the user's standing instruction)

(a) **One wave, two mechanisms on one term.** The user's charter named "the collapsed rim: three
light cells and the dark capsule, likely one fraction of the rim surviving the collapse". The
grounding read at the contour says the three light cells are not collapsed (`present` 1 by the
size bias) and their miss is the rim's amplitude law, while the collapsed cells' miss is a rim the
collapse folds out — and that the rim the reference keeps under collapse is the dark material's,
whose amplitude the same law must give. Split, each is a fit to half the evidence; together they
are the rim. The wave takes both, with the law's form G0's to decide.

(b) **The instrument is the contour, not the band.** W21's band read served the body and the
flatness; for the rim's amplitude its peak-row mean over a dark backdrop is corner-contaminated and
diluted, and W22 G0's `rimAlpha` decline (claims §5.94 §3) was made on it. That decline is not
rewritten — it was the right answer to the question the band asked — and the contour read's answer
is recorded beside it in §5.99. Every clause here is on the contour; W22's clause 2 is re-checked on
the band so the two instruments' verdicts both stand.

(c) **The collapsed rim is the material's, not the dark patch's.** The fixtures decide it: the
collapsed capsules' light and dark fixtures are byte-identical. A rim that survives the collapse is
therefore one constant on `DEFAULT_MATERIAL_PROFILE` (X4).

(d) **The user decides:** the landing, the eye's veto on the sheets, the 0.12.0 cut, and any floor
re-pinned. Everything else is the parent's on the standing instruction.


### Decision Log 2 — G0 read: the law is affine in the surface's own level, the collapsed rim is absolute, and the two terms the fit did not reach — the tinted rows and the 2x rows — go to G1 as mechanisms (2026-09-08; the parent, on the user's standing instruction)

Read from `results/2026-09-08-w23-collapsed-rim/g0/g0-findings.md` (claims §5.100), verified on the
branch: 400 renderer and 444 platform-web unit tests green, lint clean, 29 goldens byte-identical
at the shipped defaults, the one red the expected fingerprint move.

(a) **The law is (L4), `rim = rimAlpha + rimLevelGain × luminance(surface)`, and (L3) is
declined.** On the reference's own solid, unclipped, uncollapsed sides — 44 in light (bodies
0.43…0.93, both canonical scales and W9's grid) and 36 in dark (0.015…0.10, both scales and W21's
grid) — L4 reads mean |residual| 0.0081 / 0.0013 (light / dark) against additive 0.0249 / 0.0253,
screen 0.0168 / 0.0259 and screen-plus-environment 0.0105 / 0.0042; the light slope is −0.275 where
pure screen needs −α = −0.43, and the environment term separates on no row of either bed (the
`rimEnvGain` ladder moved every solid cell by 0 or 0.0005 — `light-solid` is clipped and the dark
solids have no environment). The charter's advisory preference for the screen form is overturned
by the probe grids' range, which the two canonical cells could not see. **`rimEnvGain` is removed
from the code at G1** — a constant whose rows do not separate it is not carried (C9a §6.2) — and the
environment term goes to Deferred with its numbers. The constants solved on vitrea's own captures:
light `rimAlpha` 0.844 / `rimLevelGain` −0.628, dark 0.0265 / +2.334 (condition 9.7 / 29.7); the
rendered confirmation takes the solid rows from 0.087 → 0.016 (light 1x) and 0.011 → 0.0005 (dark
1x) mean |d|. The sign of the gain is the finding: the light rim is a fraction of the body's
headroom, the dark rim rides its own body up.

(b) **`rimCollapsed` = 0.038 on the material, and it is NOT the dark rim.** The reference's collapsed
rim is +0.0189 mean over 28 sides (+0.0196…+0.0204 over `dark-solid`, +0.0149…+0.0168 over
`impulse`) against the dark material's +0.0257 over the same backdrop — nine codes on an instrument
exact in float. The charter's conditional resolves to no; the constant is absolute, in its own
units, and X4 holds and is strengthened: the byte identity across schemes extends to a tinted
collapsed cell (`dark-solid__capsule-button__rest-tint-orange`, both scales). 0.038 is the minimiser
(worst side 0.0031) and the only value that leaves every untinted collapsed side inside clause 1's
0.005; rendered, the collapsed sides go 0.0180 → 0.0021 mean.

(c) **The tinted rows are G1's, as a mechanism.** The fit was on untinted solids and the tinted
calibration rows were not in it; at the fitted point they overshoot by 0.05–0.09 (`checkerboard`
tint-orange 0.238 against 0.168; `photo` tint-blue 0.302 against 0.212; `light-solid` tint-orange
0.192 against 0.141; landed 0.05–0.07 on all three), and the tinted COLLAPSED cells undershoot by
0.10–0.16 (the reference keeps +0.115 on `dark-solid` / `impulse` tint-orange and +0.176 on the
holdout tint-blue where vitrea draws 0.0146 at `rimCollapsed` 0.038). Both are one shape: in the
reference an author tint sits above the rim and attenuates it, and a tinted surface over black does
not fold its rim out — the tint is painted, not adapted. G1 tests the rim's placement relative to
the author tint (the rim beneath the tint's coverage; the collapse's `present` on the rim gated by
the tint's strength) on a ladder with the tinted rows as its rows, before any constant is declared.
Binding: no tinted row worse than landed by more than 0.03 at the contour; the tinted collapsed
cells within 0.05 of the reference.

(d) **The 2x rows want a scale-graded width: `rimWidth2x` joins G1.** With one width the fitted
law lands 1x at −0.003…−0.007 and 2x at +0.037…+0.051 on the dark-backdrop solids; vitrea's
integral rises 19 % between the scales while the reference's falls 10 %. At 1x over a dark backdrop
the two rims are already the same one-pixel line (row 1 at 8 % against −7 %), so `rimWidth` does not
move; the 2x band narrows by about 20 % on the precedent of `sizeScatterGainMax2x`. One more ladder
pair, both scales. Clause 2 is not narrowed.

(e) **A collapsed-surface golden with a fed backdrop tone.** `rimCollapsed` moves no golden because
no golden scene collapses and the golden harness feeds no backdrop tone; G1 adds one scene that
does, so X2's attribution covers the constant.

(f) **The `rimLuma` feed is verified at G1, not assumed.** The shader takes the surface's level as
the tint shade does (the composite where the layer covers, the group's `toneColour.w` where it does
not), and G0 saw that feed at 0 on some groups (gap 5). G1 reads the published backdrop tone per
group on the calibration page for every scene and records it; the law's input is the tint shade's
quantity by construction, so the two level terms stay coherent whatever the feed.

(g) **Corrections beside the charter, not rewrites.** X1's injection bound is "exact in float,
under one code at 8 bits" — 0.001 is not reachable on a mid-grey body where one code is 0.0059; the
straight span excludes 1.6 radii (the rounded corner is continuous and the first row still climbs
between `r` and `1.5r`); the fit's quantity is `rimLocal`, the excess over the side's own base 2–4
CSS px in, with `rim` against the eroded body reported beside it (over a photograph the two differ by
up to 0.03 and the difference is the photograph); §5.99's width reading (69 % / 25 % against 100 % /
56 %) was the 2x reading and at 1x the lines are the same.

(h) **Declined for this wave, carried with numbers:** the dark thick body over `dark-solid` (−2.9
codes; no scalar separates it from `mid-dark-solid__capsule-button` at 0.02 of a code;
`adaptiveTintDark` is the constant a body wave would fit); the appearance switch, now measured at
−16 and −19 codes on the dark thin structured cells and +0.115 worse on W21's probe `light-solid__
rrect-sm` under the fitted dark law (not a canonical row); W21's probe anomaly (`rrect-sm` and
`rrect-lg` collapse over `dark-solid`, `rrect-md` between them does not); `light-solid`'s second
row (53 % of peak against −6 %, unreadable by any metric once the first row clips); the probe grids
as a harness capability rather than a gate's script.

(i) **G1 starts from G0's branch** (the mechanism at 0 is inert but moves the profile fingerprints;
landing it twice would move them twice), merges main, and lands everything in one merge with a
codex review on the whole diff before it.


### Decision Log 3 — G1 read: the rim landed and read on every cell; two clauses missed and recorded, two stops taken at the number, the painted rim's hue found by eye and taken as G3 before the landing (2026-09-08; the parent, on the user's standing instruction)

Read from `g1/g1-dryrun.md` and claims §5.101 (authored by G1 and adopted by the parent — the
section is the declaration's own record and every number in it was re-read here), the crops the
parent made from G1's dry-run captures (`w23/g1-review/`), and the codex review of the code diff.

(a) **Clause 1 met on the rim, the body's miss on `impulse__capsule-button` pre-existing and
unmoved** (−6.2 codes, S7 worst 0.00004; §5.100 §3). Glass on black draws its outline on every
collapsed cell of both beds at both scales, worst 0.0040 against 0.005.

(b) **Clause 2 met** (worst 0.0200 against 0.03; `L−R` inside 0.003; `light-solid` clips in both).

(c) **Clause 3 MISSED as a per-side bound and stands as missed.** 24 of 88 structured sides over
0.05 (68 before), five of them top/bottom; the residual is the left and right sides under a
structured backdrop, where the reference's own two sides split 2.4× on a cell whose top and bottom
agree to 0.002 — the per-pixel level under structure that the environment term was declined on and
the CSS tier cannot carry. The eight sides that met before and do not now (six `photo` rrect sides
at 2x overshooting +0.06…+0.12, two dark `checkerboard__rrect-md` left) are named; validation reads
0.0155 against calibration's 0.0479, so the law is not a fit to its own rows. Recorded, not
chartered; the clause is not restated.

(d) **Clause 4 MISSED and stands as written; the corner rim is named work.** The eighteen deferred
sides crossed the band target (1x −0.093 → +0.031, 2x −0.087 → +0.088) and 47 sides left W22's band
bound while the contour read on the same captures is inside 0.03. The two instruments differ only
where they differ — the corner arcs the contour read excludes and the band read averages in — so
the candidate is a rim brighter in the corners than on the span. No corner reader exists; G1's
tracker entry carries it. The wave's acceptance is X1's contour read; the band read stays on the
record beside it.

(e) **Clause 5 met on the GPU tier; S3 taken at the number.** Every GPU calibration mean improves;
the CSS 2x light calibration mean rises +0.00011 against the 0.0001 stop (W22 Decision Log 4 (b)'s
shape) and is taken with the number. **S2 taken at the number:** one CSS cell
(`photo__capsule-button__rest-tint-orange-half`) moves +0.0035 in body at both scales through
`interiorBandLight`'s brighter band in the derived level — the mechanism the stop watches, working;
a CSS-only residual under wave Decision Log 23 (a).

(f) **The holdout, read once at G1** — light 0.00914 → 0.00909 / 0.00906 → 0.00904, dark 0.01326
→ 0.01331 / 0.01301 → 0.01317 — **stands on the record as spent on a configuration that will not
land** (see (h)). The dark holdout's +0.00005 / +0.00016 is recorded with its sign.

(g) **Accepted as declared:** `rimWidth2x` 1.35; `rimEnvGain` removed; `rimTintKeep` refused on
rendered rows (0.534 light against 0.294 dark for a byte-identical fixture); the law's input the
material's own level; `borderAlphaPerRimAlpha` re-based and not refitted (the CSS rim's fit is a
CSS wave's, on the contour instrument — G1's tracker entry); the goldens re-recorded under
`W23_HASHES` with 0 pixels outside any band and a new `collapsed-tone` scene; the `rimLuma` feed
verified on 42 groups per bed; `PREDICATE_EXCLUDES` 29 → 27 to be re-derived at G2.

(h) **The painted rim's hue: G3, before the landing.** The parent's crops of G1's captures beside
the fixtures show Apple's rim on a tinted surface as the paint's colour lifted — orange (255, 148,
0) → (254, 188, 0) with blue at 0, blue (8, 120, 236) → (59, 199, 248) — and vitrea's as white
added over the paint ((255, 192, 130); (145, 183, 255)). The 0.11.0 bed drew the same white rim
fainter; G1's amplitude makes it plain. The luminance clauses cannot see it and the eye does, on the
most common surface an author paints. It is the composition order (the optics pass adds the rim
after the author's colour) and is a mechanism, so it is taken as G3 on G1's branch before any
canonical capture — the W22 precedent, where a known-wrong input is corrected before the landing's
one holdout read — and G1's read is recorded as spent. `rimCollapsedTinted` and the material-level
input, both fitted with the rim over the paint, are G3's to keep or replace.

(i) **The codex review's verified findings go to the same worker as a fix wave with G3**; a finding
that is real and small is logged, not fixed here.

(j) **The user decides:** the landing after G3, the eye on the sheets (the tinted capsules at 4×
beside the black-on-black cells), the 0.12.0 cut.

## Surprises & Discoveries

- **The "collapsed rim in light" was never collapsed.** Three cells, eighteen sides, two waves under
  one name; the size bias exempts every one of them from the collapse. The name came from the band
  reader's numbers looking like a folded-out rim.
- **The reference's collapsed capsule is the same bytes in both schemes.** W7's "byte-identical to
  its background" was a body reading; the rim was there, at 55/255 on 28/255, all along.
- **vitrea's rim is a constant; the reference's is a law.** +0.060…0.078 linear on every light cell
  against +0.10…0.26 — and the CSS tier's inset shadow already has the form (source-over white)
  the GPU tier lacks.
- **The law's slope changes sign with the scheme** (G0). Light −0.275 of the surface's level, dark
  +0.94: the same expression, the opposite reading. Neither the screen form the charter favoured nor
  the environment term survived the probe grids.
- **The canonical light bed has two fittable solid cells.** Any two-constant law on the light
  material is unfittable without W9's probe grid, which nothing in the harness captures routinely.
- **The tinted collapsed capsule keeps a rim of +0.115** (both schemes, both scales, byte-identical
  fixtures) where the untinted one keeps +0.020: an author tint over black is painted, not adapted.
- **W21's probe grid collapses `rrect-sm` and `rrect-lg` over `dark-solid` and not `rrect-md`.** On
  the record; read by nothing here.
- **The painted rim keeps the paint's hue** (G1, by eye on the crops). Every luminance clause was
  met on the tinted capsules and the rim was the wrong colour: orange's blue channel stays 0 in the
  reference and rises to 130 in vitrea. A clause on the rim's chromaticity did not exist until G3.
- **The two readers disagree only at the corners.** Clause 2 met on the contour and clause 4 missed
  on the band, on the same captures; the corner arc is the one region only one of them reads.

## Outcomes & Retrospective

(at recomposition)

## Revision Notes

- 2026-09-08: chartered; G0 dispatched.
- 2026-09-08: G1 DECLARED (claims §5.101). The law landed with the constants G0 solved, plus three
  terms Decision Log 2 handed it: `rimWidth2x` 1.35, `rimCollapsedTinted` 0.337 and the law's input
  moved to the MATERIAL's own level rather than the painted one — without which the dark bed's
  tinted rows drew +0.344 against a reference of +0.129. `rimEnvGain` removed and `rimTintKeep`
  refused, both on rendered rows. `cssTierMapping.borderAlphaPerRimAlpha` re-based 1.95 → 0.64.
  Clause 1's rim half met on every collapsed side of both beds at both scales (worst 0.0040);
  clauses 2, 5, 6, 7 and 8 met; clause 3 missed on 24 of 88 structured sides (68 before) and
  clause 4 not closed — the band read overshoots where the contour read matches, and the corner is
  where the two readers differ. Two stops fire at the fifth decimal, both on the CSS tier.
- 2026-09-08: G0 CLOSED (claims §5.100); Decision Log 2 — the law affine in the surface's own level
  (the charter's advisory preference for the screen form overturned on the probe grids), the
  collapsed rim absolute and not the dark rim (the charter's conditional resolved to no), the tinted
  rows and `rimWidth2x` added to G1 as mechanisms, a collapsed golden added, X1's injection bound and
  the straight span restated; `rimEnvGain` to be removed at G1. Deferred and Surprises updated.

# W21 — the dark scheme on the GPU tier (2026-09-06)

**Status: OPEN — chartered 2026-09-06 on wave Decision Log 23 (c) at W20's close and the 0.9.0
cut; the finding pinned the same day (claims §5.87). G0 CLOSED 2026-09-07 (claims §5.88–§5.89;
Decision Log 2): the dark reference measured over seven attested runs — W9's law carries for thick
surfaces with nothing fitted, the thin surface is an appearance switch the scene selects, the rim
has no light direction. G3 MERGED ahead of its edge. G1 dispatched.**

Composite spec: design at the top; Decision Log, Surprises, Deferred and Revision Notes at the
tail. Parent: `2026-08-28-post-v1-wave.md` (the W21 row; Decision Log 23 (c)). The law this wave
extends is W9's response-curve law (`2026-09-02-w9-backdrop-tone-sampling.md` Decision Log 3;
claims §5.30–§5.35), whose Deferred list named this work — "the dark response surface … needs a
dark-scheme probe; the canonical dark bed's four measurable cells are too thin to anchor it". The
profile document it re-records is `packages/calibration/profiles/apple-macos-26.5-1x-dark-standard.json`
(C9a's four-cell fit; W9's stand-down of the response law at strength 0; W10's stand-down of the
tint shade). The rim reading it takes up is C9a's §6.2, where a dark rim retune was found on four
cells and declined because the fit went to zero rather than to the reference.

## Purpose

The dark scheme is the largest measured gap on the GPU tier, and has been since the dark pair was
adopted into the gate. On the canonical bed the two dark profiles read OKLab ΔE 0.0085 / 0.0300
(calibration / holdout; the two scales within 0.0002 of each other on every row) against the light
profiles' 0.0033 / 0.0091. Every untinted dark cell but the collapsed capsules sits above 0.005, and
the three dark holdout cells — `photo__rrect-lg` (0.0572), `checkerboard__glass-over-glass`
(0.0274) and `mid-dark-solid__capsule-button` (0.0053) — carry the bed's worst rows outside the
increased-contrast profile.

Read under the declared geometry instead of the extracted silhouette (claims §5.87;
`results/2026-09-06-w21-dark-scheme/finding/`), the gap separates into two terms and a third
beside them:

- **The body is a response surface the dark profile does not have.** The dark reference's interior
  is not the fixed 0.05 the profile document fitted on four cells. Thin surfaces over structured
  backdrops settle at 0.096–0.106 (the capsule over `photo` and `checkerboard`) while thick ones
  settle at 0.045–0.047 (`rrect-md` and `rrect-lg` over the same backdrops); over `dark-solid` the
  thick body sits at 0.015 above a 0.012 backdrop and the thin one collapses onto it; over
  `mid-dark-solid` (0.060) the capsule settles at 0.029, BELOW its backdrop, and over `impulse` at
  0.007. vitrea's dark body is the same 0.048–0.064 everywhere the collapse does not fire — the
  profile's tint 0.05 at α 0.97 — so it is too dark on every thin cell by 0.04 and too bright on
  every thick one by 0.008–0.033. This is the shape W9 measured in the light scheme and wrote as
  `R(encodedMean, thickness)`: the dark profile runs that law at strength 0 because its anchors were
  never measured on the dark reference (`material.ts`'s own comment on
  `backdropToneResponseStrength`), and the canonical dark bed cannot supply them — it has no
  `light-solid` scene, and its solids leave the extractor nothing to read.
- **The rim is the light scheme's.** The dark reference's rim is faint and nearly uniform: 0.034 top
  and bottom, 0.030 left and right over `dark-solid`'s 0.012; 0.067 / 0.062 over `mid-dark-solid`'s
  0.060; +0.013 on the collapsed capsule. vitrea draws the two-light rim the light profile fitted —
  0.224 top, 0.233 left, 0.102 bottom, 0.085 right over `dark-solid`; 0.223 / 0.132 / 0.110 / 0.077
  over `mid-dark-solid` — seven to ten times the reference's excess, and top-left weighted where the
  reference is flat. C9a §6.2 called this "the dominant dark-scheme error term (0.084 of a 0.111
  objective)" and declined to fit it on four cells whose direction disagreed; W16's analytic check
  attributed `dark-solid__rrect-md`'s excess to the rim (+0.080) and the highlight (+0.053) over a
  near-black body. A per-side read on the probe's 56 cells is what makes it fittable.
- **The passthrough.** The dark reference passes more of the backdrop's structure than vitrea:
  interior sd 0.052 against 0.016 on the capsule over the checkerboard, 0.017 against 0.006 on
  `rrect-md`. The profile document's own caveat says why — a lerp at α 0.97 has to trade the
  structure away to hold the level — and W9's law removes the trade: once the solve owns the level,
  the alpha is free to carry what it was fitted to carry.

The tinted dark cells are untouched by any of this — body within 0.007, rim within the band's
noise, ΔE 0.0005–0.0010 — and are a stop.

The matrix under-reads the whole thing for a reason worth writing down. Over the dark solids the
body sits within the silhouette extractor's 0.02 threshold of its backdrop, so the native silhouette
is the rim ring in fragments — `dark-solid__rrect-md` recovers 370 px in six bodies of a 15 024 px
region — and the cell's `interiorMeanNative` 0.041 and `interiorMeanWeb` 0.211 are readings of the
RIM, not the body (the body reads 0.015 against 0.048). The conditioning predicate excludes the cell
on both tiers and both scales, so the bed's worst-shaped dark cell is not in the gate at all, and its
`rimPeakLuminance` rows read 0. Wave Decision Log 23 quoted that cell's "interior 0.21 against
Apple's 0.04" as this wave's headline; the number is real, and it is the rim.

This wave measures the dark reference on W9's grid, reads the response surface's anchors and the rim
per side from it, stands the response law up on the dark profiles with their own anchors, gives the
rim its dark amplitude and the alpha its passthrough, lands on the GPU tier with the CSS tier
deriving from the same patch, rebuilds the canonical bed — and ships the result, because today the
dark profile is a JSON in the calibration package that no published package exports and nothing
selects (C9a's parent-impact item, still open): a host in dark mode gets the light material.

## Parent-Level Acceptance

Binding. The numbers are the charter's; G1 re-declares them with the probe's noise floor beside
(Decision Log).

1. **The dark reference measured.** W9's 56-cell grid captured at 1x under the dark profile's
   environment by W9's protocol (at least seven attested runs, the majority byte-state per cell,
   provenance naming every disqualified run), committed under
   `results/2026-09-06-w21-dark-scheme/probe/`; nothing canonical written.
2. **The anchors are measurements.** The response surface's six anchor levels (the thin and thick
   rows at the three solid anchors) are read from the probe under the declared geometry and recorded
   in the profile document with their provenance; no anchor is tuned. The encoded-mean law is
   checked in the dark scheme by W9's declared rule (P0 / P1 / P3 on the structured cells, the
   equal-mean pair) before it is assumed.
3. **The body.** On every untinted dark texture-tier cell at both scales, the body under the
   declared geometry (the box eroded 6 CSS px) within **0.010** of the reference — today
   0.003–0.042 — with the collapsed cells (the `dark-solid` and `impulse` capsules) held within
   0.002 of where they are.
4. **The rim.** On every untinted dark cell over a solid backdrop, each side's rim-band peak within
   **0.03** of the reference's — today 0.07–0.21 — and the reference's flatness across sides
   reproduced (max side minus min side within 0.03).
5. **The matrix.** Dark calibration ΔE mean at each scale below **0.006** (from 0.0085); no untinted
   dark row worse than the W20 bed by more than 0.001 in ΔE mean or 0.005 in `ssimMean`; the
   holdout read once, the three cells at both scales named with their movement
   (`checkerboard__glass-over-glass` expected partial: the nested pane stands the tone axis down,
   W9 Deferred); every tinted dark cell within 0.001 of the W20 bed.
6. **The light profiles byte-identical** on both tiers; the CSS tier's dark rows derived from the
   same patch and recorded, moved or not (wave Decision Log 23 (a)).
7. **The constants named.** Every fitted constant — at most three: the alpha, the rim's ambient and
   specular amplitudes — carries the rows it was fitted on; a constant whose rows do not separate it
   is declined, not fitted (C9a §6.2's rule).
8. **Shipped.** The dark profile exported from `@vitreajs/vitrea-web` and selectable at the root;
   the shape is the user's (Decision Log 1); the calibration profile document and the shipped patch
   are one source.
9. **By eye, and the gap ledger.** The landing sheet (native | GPU before | GPU landed, both scales)
   before publish, the user's veto kept; every remaining gap named — the nested pane in dark, the
   collapsed rim, the pressed state, the passthrough's residual, the CSS tier's residual. **0.10.0**
   after the landing.

## Grounding Baseline (the W20 bed, 2026-09-06, `c9f724f`)

The canonical matrix at W20's landing (`results/matrix.json`, 229 cells), GPU tier, the two dark
profiles — the referee every gate reads against, frozen here:

| profile | calibration ΔE (n) | validation (n) | holdout (n) |
| --- | --- | --- | --- |
| 1x dark | 0.0085 (9) | 0.0029 (1) | 0.0300 (3) |
| 2x dark | 0.0086 (9) | 0.0033 (1) | 0.0302 (3) |
| 1x light, for scale | 0.0033 (20) | 0.0026 (6) | 0.0091 (10) |

Per cell at 1x, ΔE mean (2x within 0.001 on every row): `photo__rrect-lg` 0.0572 (holdout),
`dark-solid__rrect-md` 0.0286, `checkerboard__glass-over-glass` 0.0274 (holdout),
`photo__rrect-md` 0.0197, `checkerboard__rrect-md` 0.0111, `photo__capsule-button` 0.0077,
`checkerboard__capsule-button` 0.0056, `mid-dark-solid__capsule-button` 0.0053 (holdout),
`impulse__capsule-button` 0.0029 (validation), the three tinted capsules 0.0005–0.0010,
`dark-solid__capsule-button` 0.0008. The declared-geometry read (claims §5.87's tables, both
scales) is the baseline for clauses 3 and 4.

The dark profile document today: the patch is `backdropToneResponseStrength` 0,
`tintShadeStrength` 0, `optics.regular.tint` 0.05 at `tintAlpha` 0.97, both adaptive tints 0.05,
and W14's outer-shadow amplitudes; the fit that produced the tint was C9a's, on four cells, with an
objective of interior mean, spread and rim peak. The gate today: the dark pair's texture-tier
bounds are loose (IoU ≥ 0.93, ΔE mean ≤ 0.09, p95 ≤ 0.17, `ssimMean` ≥ 0.87 — adopted 2026-09-01
by the margin rule on a bed that read clean), there are no floors on the dark pair,
`dark-solid__rrect-md` is excluded by the predicate on both tiers and both scales, and
`dark-solid__capsule-button` carries no shape axis. The bounds will stop nothing in this wave; the
referee is the per-cell W20-bed reading (clause 5) and the declared-geometry read (clauses 3–4).

## Design (advisory unless marked)

**The law is W9's, with the dark reference's anchors (binding).** `R_dark(encodedMean, thickness)`
is the monotone curve through the dark probe's three solid anchors per row, thin and thick rows
smoothstepped in thickness — the same function, the same anchor inputs (`backdropToneAnchorX`; the
backdrops are the same rasters), the dark scheme's response rows. The solve shifts the dark
neutral's luma so the composite lands on it; the collapse is unchanged (its `dark-solid` domain was
measured in both schemes, and the dark capsule collapses byte-identically today); the composition
contract (scheme → adaptation → author tint) is unchanged; `backdropToneResponseStrength` goes to 1
on the dark profiles. Three places the light law's mechanics may not carry, each a G0 read rather
than an assumption: (i) the light scheme hands an upward remainder to the alpha where the white
neutral clamps; the dark neutral is 0.05 and the targets run 0.007–0.106 (and are unknown over
`light-solid`), so the mirror case is the black clamp on the downward side — G0's endpoint table
(the render at strength 0 and at strength 1 on the light anchors, §5.33's shape) states the
reachable span per cell before G1 declares; (ii) `backdropToneSolveWeight` fades the solve's
authority below the dark anchor's lower half, where the dark `impulse` capsule (validation) sits;
(iii) the row order inverts between schemes at the mid inputs — thin below thick at the light
scheme's dark anchors, thin ABOVE thick by 0.05–0.06 on the dark bed's `photo` and `checkerboard`
— which the smoothstep between rows carries without a new constant.

**The alpha carries the passthrough (advisory).** Under the solve the level is not the alpha's, so
`optics.regular.tintAlpha` is refitted on the probe's interior-sd rows — the pitch sweep gives the
passed structure against pitch, which also reads the dark blur. The lerp-versus-multiply question
the profile document raised in its caveat is decidable on that sweep: under a lerp the passed
structure is independent of the level, under a multiply it scales with it. G0 reads it; G1 decides
whether the lerp with a freed alpha is enough. The sd is reported beside the body on every gate and
is not a bound this wave.

**The rim's dark amplitude (advisory; G0 decides the form).** vitrea's rim is `rimAlpha` (ambient)
plus `specularGain` (the two-light term) plus the `highlight` colour, all on `optics.regular`,
which the dark patch can carry as it carries the tint. If the per-side read confirms the reference's
rim flat across sides, the specular goes to zero and the ambient is fitted on the solids' rim
excess; if the read shows a top/bottom against left/right split (the collapsed capsule hints
0.013 against 0.004), that is the specular's signature at a small gain. Two constants at most,
each on its own rows. The reference keeps a faint rim under collapse where vitrea's collapse folds
the rim out: read, and deferred unless it is one constant.

**The instrument (binding).** The body is read under the DECLARED geometry — `scenes.json`'s box
eroded 6 CSS px — and the rim in the box's outer 3 CSS px per side; the silhouette-based
`interiorLevel` is not used on the dark scheme because over the solids it returns the rim ring.
W9's `scripts/probe-score.ts` (P0 / P1 / P3 and the H4 statistic) is re-run on the dark probe with
its profile parametrised and its interior definition swapped for the declared read, so the
encoded-mean law's verdict in dark is by W9's declared rule; the backdrop's statistics are measured
under the footprint from the rendered raster as W9 did. The reader is validated by injecting a
known level and rim into a capture and recovering them (X4).

**What ships (advisory; the shape is the user's).** `@vitreajs/vitrea-web` exports the dark patch
(`darkMaterialProfile`: the profile document's `patch`, one source, a test pinning the export to
the document) and `createGlassRoot({ colorScheme })` takes `"light" | "dark" | "auto"`; `"auto"`
follows `prefers-color-scheme` through the media-query policy feed that already exists
(`planes.ts` already declares `color-scheme: light dark`); react's `GlassRoot` passes it through.
The default stays light — no behaviour change for an existing host — and a later major may flip it
to auto. A backdrop `hint={{ tone }}` and the scheme are different things (the hint is the
backdrop's tone, the scheme the material's), and the docs say so.

**The CSS tier derives.** The tone response and the rim on the CSS tier read the same patch
(`optics.ts`'s `resolvedBackdropTone`; `css-tier.ts`'s rim from the CSS optics), so the dom-tier
dark rows move with the profile; what remains is the CSS tier's residual, recorded (Decision Log 23
(a)).

## Children

### G0: The dark probe and the instrument — spike (deliverable: findings)

- **Purpose:** (a) `apps/reference-apple/scenes-w21-probe.json` — W9's grid under
  `apple-macos-26.5-1x-dark-standard` (`colorScheme: dark`), the split re-derived by W9's rule
  against the canonical DARK bed: `recorded` for the twin of the dark holdout (`photo__rrect-lg`),
  holdout the `checkerboard-8` column and the three large extremes, validation W9's five,
  calibration the rest; (b) the native probe by W20's runner from the main checkout's bundle
  (a ten-run budget, at least seven attested, the majority byte-state, provenance); (c) the reader
  under the declared geometry: per cell the body level and sd, the rim band's peak per side, the
  backdrop's linear and encoded means under the footprint; the anchor table (thin row `rrect-sm`;
  thick `rrect-md` / `ml` / `lg` pooled with their spread; the capsule and `ml` as interpolation
  checks) with run-to-run σ beside every level; the encoded-mean verdict in dark by W9's rule; the
  equal-mean pair; sd against pitch; the rim per side against backdrop and size; the tints,
  descriptive; (d) vitrea's side on the same grid — the GPU tier captured at the shipped dark
  profile (strength 0) and at strength 1 on the LIGHT anchors (the diagnostic), into scratch, read
  by the same reader: the reachable span and the required strength per cell (§5.33's table), the
  rim per side on vitrea's own captures; (e) `g0-probe.md` — the findings, claims-ready tables, and
  a Decision-Log-2-shaped recommendation for G1: the anchors, whether the law's form carries, what
  the alpha and the rim need, the noise floor per row.
- **Acceptance:** the probe committed with provenance; the anchor table with σ; the encoded-mean
  verdict by the declared rule; the endpoint table; the reader's recovery (X4); nothing canonical
  written; the findings file; the claims section written by the parent from it.
- **Edges:** none. **Track:** spike; one worker; findings, not the spec. The GPU is shared — one
  capture process at a time.

### G1: The form declared and dry-run — controlled

- **Purpose:** the dark profile document re-recorded — the six anchors as measurements
  (`backdropToneResponseThin` / `Thick` in the patch, with provenance), `backdropToneResponseStrength`
  1, the alpha and the rim's amplitudes fitted on their rows on the probe's calibration split
  (validation read; the probe holdout not read — the canonical bed's holdout is this wave's one
  read), `resolvedMaterialSha256` moved and explained, `tuned-profiles.test.ts` green; the dry run
  on the canonical dark bed at both scales on the GPU tier with the holdout read once (the frozen
  configuration), the CSS tier captured beside it, every light-profile capture verified
  byte-identical; the sheet; the declaration in claims (form, constants, the stops with numbers,
  the rows the landing must reproduce) before any landing capture.
- **Stops (declared here; G1 refines with numbers):** (S1) any untinted dark row worse than the W20
  bed by more than 0.001 ΔE mean or 0.005 `ssimMean`; (S2) any tinted dark cell moved by more than
  0.001; (S3) a collapsed capsule moved by more than 0.002 in body; (S4) any light-profile capture
  not byte-identical; (S5) a fitted constant whose rows do not separate it; (S6) the encoded-mean law
  refuted in dark by W9's rule — the form goes back to the design table with G0's finding and the
  wave re-declares; (S7) the user's eye.
- **Acceptance:** the claims section; the sheet sent; the user's reading recorded; the stops
  dispositioned in a Decision Log.
- **Edges:** blocked-by G0. **Track:** controlled.

### G2: The landing and its referee — controlled

- **Purpose:** merge; the canonical rebuild from the main checkout (W20's `g2-rebuild.sh` pattern
  with `--alpha`, both tiers, six profiles, `rm results/matrix.json` first — the dark profile's
  hash moves and the old rows must not sit beside the new); the referee — the dark rows against the
  W20 bed and against the dry run byte for byte, the light rows byte-identical; the gate
  (`adopted-thresholds`: the dark pair's bounds re-proposed by the margin rule as a user decision,
  `PREDICATE_EXCLUDES` re-derived — expected unchanged, the native silhouettes do not move); the
  demo's dark calibration figures; the landing sheet; the user's eye; the changeset (a `vitrea-web`
  minor).
- **Acceptance:** clauses 3–7 and 9 of the parent's; the chain green; the claims section.
- **Edges:** blocked-by G1. **Track:** controlled; the landing is the user's call.

### G3: The dark scheme shipped — controlled (the shape user-decided)

- **Purpose:** the dark patch exported from `@vitreajs/vitrea-web` from ONE source with the profile
  document (a test pins the export to the document's `patch`); `colorScheme` on `createGlassRoot`
  and on react's `GlassRoot` (`"light" | "dark" | "auto"`, default light); `"auto"` via the
  media-query policy feed; the demo gains a scheme switch on at least one scene; the docs.
- **Acceptance:** a host on a dark OS theme with `colorScheme: "auto"` renders the dark profile on
  both tiers (a platform-web e2e under `colorScheme: "dark"` emulation reads the resolved profile;
  react's test the same); the shipped patch equals the document's; the same 0.10.0 changeset.
- **Edges:** blocked-by G2 (ships the landed numbers); the API shape blocked-by Decision Log 1's
  user answer. **Track:** controlled.

## Cross-Child Contracts

- **X1 — measurements before constants.** The anchors are read by G0 and never tuned; a constant
  fitted by G1 carries the rows it was fitted on.
- **X2 — the instrument.** The declared-geometry read is the wave's body and rim definition on
  every gate; on the dark scheme the silhouette-based rows are reported beside it, never the verdict.
- **X3 (inverse) — the light profiles byte-identical** on both tiers at G1 and G2.
- **X4 — the reader's recovery.** A known level and rim injected into a capture and recovered,
  recorded beside the first reading.
- **X5 — by eye.** The sheet at the W20 sheet's zoom on the dark cells at both scales: native | GPU
  before | GPU landed | CSS.
- **X6 — the holdout once**, at G1's dry run on the frozen constants; G2 reproduces byte for byte.
- **X7 — one source.** The shipped patch and the profile document are the same bytes (G3's test).

## Ordering & Dependency Map

G0 → G1 → G2 → G3 → the 0.10.0 cut → the thick-span composite (wave Decision Log 23 (c)). The
native probe rides inside G0 behind the TCC gate as W18–W20's did; the GPU is shared, one capture
at a time.

## Risks & Mitigations

- **The probe's dark solids leave the silhouette nothing** — by design the reader does not use it
  (X2).
- **A two-state epidemic on the dark reference.** The W9 probe saw ten of 56 two-state cells in
  light; the dark `dark-solid` capsule was the canonical bed's worst refuser (settled 2-of-4). The
  majority rule with a ten-run budget; a tie topped up; an epidemic reopens the doctrine question
  before scoring (W9's stop).
- **The dark reference over `light-solid`, never captured**, may settle at the light-state
  attractor (the reference's two-state pair is its own light/dark appearance, §5.31). The probe
  measures it; whatever it is, it is an anchor and the law carries it.
- **The alpha refit moving the tinted cells.** A full-strength tint displaces the adaptation (W9
  finding); S2 guards.
- **The window-activation loss** (tracker) — the run budget.
- **Shipping touches the public API.** G3's shape is the user's; the fidelity gates do not wait on
  it.

## Deferred / Out of Scope

- **The nested pane in dark** (`checkerboard__glass-over-glass`: the inner pane 0.021 against
  vitrea's 0.051): the tone axis stands down over a glass backdrop (W9 Deferred); expected partial;
  recorded at G2 with its number.
- **The pressed state** (`photo__capsule-button__pressed` is `recorded` on the dark profiles and
  unmeasured) — the motion harness's, with the rest of the press claim.
- **The collapsed rim** (+0.013 on the reference's collapsed capsule; vitrea's collapse folds the
  rim out) unless G0 shows it is one constant.
- **The dark tint shade** (`tintShadeStrength` 0; W10 Deferred's question needs a dark tinted cell
  over a light backdrop — the probe's tint capsules are over checkerboards and are descriptive).
- **A 2x probe.** W9's scale-free finding holds on the dark bed (every 2x row within 0.001 of its
  1x twin); the 2x canonical bed is the referee.
- **The accessibility response surfaces** (W9 Deferred).
- **The CSS tier's dark residual** — recorded, not chartered (Decision Log 23 (a)).
- **The gate's dark bounds** — re-proposed at G2 by the margin rule; adopting is the user's.
- **Default `colorScheme: "auto"`** — a later major.
- **The appearance switch** (Decision Log 2 (a); claims §5.89 §2): the dark material's thin surface
  draws the light appearance over a uniformly bright scene — `light-solid__rrect-sm` 0.9666 against
  `checkerboard-64__rrect-sm` 0.1611 at the same footprint input. A scene-level term neither tier
  has an input for; no canonical dark cell exercises it; both readings on file. A spike's shape:
  which scene statistic selects the appearance, on a ladder of scenes between the two.
- **The thin row's residual after the footprint anchor** (0.0244 mean on the probe grid, rising
  with the encoded input) — the same term seen as a residual.
- **The rim's horizontal-against-vertical split over bright backdrops** (0.09–0.12 over
  `light-solid`, the vertical edges brighter; §5.89 §5) — recorded, not fitted; no dark canonical
  cell shows it.
- **The collapsed rim** (+0.017 on `dark-solid__rrect-sm`; Decision Log 2 (b)) — one number, a
  renderer mechanism to take, below every bound.
- **`hc-text__rrect-sm`'s 4-of-7 state share** — topped up when the console allows; in no fit.
- **W9's H4 remainder in dark** (0.0010–0.0013 on the thick rows, sign-consistent) — where the
  light scheme left it.
- **A unit suite for the demo.** `apps/demo` has no vitest; G3's `reportsFor` and `nativeCaptureFor`
  are pure over committed data and are pinned only by the demo's e2e. Twenty lines of test behind a
  config, a script and a lockfile entry — small infrastructure, not opened mid-wave.

## Tracking Map

| child | status |
| --- | --- |
| G0 — the dark probe and the instrument | CLOSED 2026-09-07 (claims §5.88–§5.89): seven attested runs of eighteen (the rest disqualified by name — a locked console, one mid-run input), the six anchors read at majority σ 0.0000, P3 0.0078 on the thick rows and the candidate at the measured anchors 0.0044 mean body error with nothing fitted; the thin row an appearance switch (`light-solid__rrect-sm` 0.9666 against `checkerboard-64__rrect-sm` 0.1611 at the same footprint input); the rim flat to 0.001–0.004 on the dark solids where vitrea spreads it by 0.15; the passthrough a lerp three to five times too strong; the tints untouched; Decision Log 2 |
| G1 — the form declared and dry-run | DISPATCHED 2026-09-07 on Decision Log 2 |
| G2 — the landing and its referee | — |
| G3 — the dark scheme shipped | MERGED 2026-09-06 (`c017625`, `bc0b9e8`; Decision Log 1's shape): `darkMaterialProfile` generated from the profile document and pinned to it in two packages (X7), `colorScheme: "light" \| "dark" \| "auto"` on both roots with `"auto"` on the media feed and one re-derivation path for every profile change, the demo's scheme switch with its Reference section following the resolved scheme (12 of 32 picker scenes carry a dark capture; the rest withdraw the pair with a sentence); Codex review's one finding fixed; browser suites 21 / 21 on three engines and 5 / 5 on the demo; ships its numbers with G2 — X7's test carries G1's re-recording through |

## Decision Log

### Decision Log 1 — the cut, the binding rules, and what the user decides (2026-09-06)

**The cut.** Four children: G0 a spike (the dark probe, the instrument, vitrea's endpoint table,
the recommendation), G1 and G2 controlled (the form declared and dry-run; the landing, the rebuild,
the referee), G3 controlled with its shape user-decided (the dark scheme shipped). G0 is a spike
because the anchors do not exist yet and the form's three open questions (the clamp side, the
alpha, the rim's shape) are answered by measurement, not by design.

**Binding.** The law is W9's with the dark reference's anchors; the anchors are measurements and
are never tuned; the body and the rim are read under the declared geometry on every gate; the
light profiles are byte-identical on both tiers; the canonical holdout is read once, at G1's dry
run; the shipped patch and the profile document are one source.

**Rejected.** (a) Fitting the dark profile on the canonical bed's thirteen cells — no `light-solid`
anchor exists there, the solids are unreadable by the silhouette, and a four-cell fit is how the
profile got the numbers it has. (b) A rim retune alone — C9a §6.2's fit went to zero on four cells;
the per-side read on 56 is what changes the answer, and the rim is the second term, not the first.
(c) A multiply composite as a new renderer mechanism before the freed alpha is tried — the profile
document's caveat was written against a lerp that also had to carry the level; under the solve it
does not, G0 reads the discriminator and G1 decides on evidence. (d) Opening the thick-span
composite first — Decision Log 23's order stands; the dark bed is the larger gap and its thick
cells are in this bed.

**The user decides.** (1) G3's API shape — recommended: `darkMaterialProfile` exported from
`vitrea-web` and `colorScheme: "light" | "dark" | "auto"` on both roots, default light, in the
same 0.10.0; (2) the landing, on the sheet; (3) the gate's dark bounds re-proposed at G2; (4) the
0.10.0 cut. Under the standing instruction ("for decisions, all according to your
recommendation") the parent proceeds on (1) as recommended, opt-in, unless told otherwise.

### Decision Log 2 — G0 read: the law carries for thick surfaces, the thin row's top is the footprint reading, the rim loses its light direction; G1's design made binding (2026-09-07; the parent, within G1's remit, on the user's standing instruction)

**What G0 measured** (claims §5.89). Seven attested runs; the six anchors at majority σ 0.0000;
W9's law at the measured anchors predicts every thick cell to P3 0.0078 and the candidate render
lands the thick rows at 0.0044 mean body error with nothing fitted; the thin surface is bistable
between the material's own light and dark appearances and the scene, not the footprint, chooses
(`light-solid__rrect-sm` 0.9666 in six runs of seven against `checkerboard-64__rrect-sm` 0.1611 in
seven of seven at the same uniform-white footprint input); the reference's rim has no light
direction (top = bottom, left = right, to three decimals on every solid); the passthrough is a lerp
and vitrea holds back three to five times too much structure at every pitch; the tinted cells are
untouched by everything.

**Rulings, binding on G1.**

(a) **The anchors, as measured (X1):** `backdropToneAnchorX` [0.1104, 0.2706, 0.9505] (identical to
the light profile's, as it must be), `backdropToneResponseThick` [0.0131, 0.0238, 0.1006],
`backdropToneResponseThin` [0.0110, 0.0284, **0.1611**], `backdropToneResponseStrength` 1, on the
dark profile document (which serves both dark profiles). The thin row's top is
`checkerboard-64__rrect-sm`'s uniform-white FOOTPRINT reading, not `light-solid__rrect-sm`'s 0.9666.
The reasoning is the ruling: 0.9666 is the material's light appearance drawn on a scene that is
bright everywhere (it sits within 0.005 of the light scheme's own thin top, 0.9713); the law's input
is the footprint by W9's design; no canonical dark cell puts a thin surface over a bright scene; and
a dark profile that reproduced it would draw the light material on a white page — which is exactly
what `backdropToneResponseStrength: 0` had been protecting against. Both readings are on file
(`anchors-measured.json`, `anchors-footprint-top.json`); the RMS is flat in the anchor between
0.145 and 0.170, so its exact value is not load-bearing. The scene's appearance switch is
**deferred by name** with its evidence: a scene-level term neither tier has an input for.

(b) **The rim:** `optics.regular.specularGain` 0 on the dark profile — the reference's four sides
agree to 0.001–0.004 on both dark solids where vitrea spreads them by 0.147–0.150, so the constant's
rows do not separate it and it is carried for nothing; `optics.regular.rimAlpha` fitted on the six
solid cells' rim excess over the body (0.015–0.019 over `dark-solid`, 0.035–0.039 over
`mid-dark-solid`, thin to thick — two rows of three cells for one constant). The
horizontal-against-vertical split over bright backdrops (0.09–0.12 over `light-solid`) is recorded,
not fitted. **The collapsed rim (+0.017 on the one cell vitrea collapses) is deferred**: it is one
number, but taking it is a renderer mechanism (the collapse retaining a rim trace) for a cell whose
ΔE is 0.0008 — below every bound; recorded with its number.

(c) **The alpha:** a lerp (three of four components on the equal-mean pair; the multiply is not
needed and the profile document's caveat is answered). `optics.regular.tintAlpha` refitted on the
passthrough rows — the pitch sweep at fixed component (`rrect-md` 0.0143 → 0.0637 in `pass` against
vitrea's 0.0030 → 0.0197), checked on the equal-mean pair where the level and the structure move
independently — with `hc-text__rrect-sm` (4-of-7, too close to call) in no fit. The blur's shape is
nearer than its amplitude, so the alpha alone is tried first; a second constant only if the sd rows
separate it (S5).

(d) **The solve's reach:** the collapse keeps the near-black domain (the collapsed and tinted cells
are degenerate in the endpoint table; the `impulse` validation cell stays the collapse's); the
solve-weight fade below the dark anchor is untested by this grid and is left alone.

(e) **The dry run and its stops** (X6): the canonical dark bed at both scales on the GPU tier at the
frozen constants with the holdout read once, the CSS tier captured beside it from the same patch,
every light-profile capture verified byte-identical on both tiers; the stops as chartered (S1–S7)
with G1's numbers, plus the acceptance re-read: clause 3's 0.010 body is met on the thick rows by
construction, and on the thin rows the canonical bed's capsules over structured and dark backdrops
read within 0.02 on the probe grid, so G1 reports each thin cell's body against 0.010 and the parent
rules on the remainder with the appearance term named — no constant is added to the law for it.

(f) **The instrument's noise floor** for every bound: majority σ 0.0000 within a settled appearance;
the reader's recovery bound 0.0028 is the floor quoted beside a level; the full σ is quoted beside a
bistable cell (four cells, all thin).

(g) **Housekeeping that rides G1:** the profile document's `$comment-w21` block and its `entries`
re-recorded with provenance, `resolvedMaterialSha256` moved, the generated `dark-profile.ts`
regenerated (`pnpm --filter @vitreajs/vitrea-web run profile:dark`; X7's tests fail until it is),
the scene server's `VITREA_FIXTURES` containment check fixed with `resolve()` (claims §5.89 §8).

**Rejected.** Adopting 0.9666 as the thin top (reproduces one cell to 0.0019 and costs nineteen; a
white page would get the light material). A scene-level appearance term in this wave (no input for
it exists on either tier; no canonical cell needs it; a spike's shape, deferred). A multiply
composite (the pair says lerp). Fitting `specularGain` to a small value (its rows do not separate
it). The collapsed rim now (a renderer mechanism for +0.017 on a 0.0008 cell).

## Surprises & Discoveries

- **The dark material's thin surface is an appearance switch the scene selects** (G0, claims §5.89
  §2): over a scene that is bright everywhere it draws its light appearance (0.9666, within 0.005
  of the light scheme's thin top), over a dark scene with a locally white footprint it stays dark
  (0.1611) — the same footprint input, 0.81 apart. Every genuinely bistable cell on the grid is
  thin, and the bistability's direction mirrors between schemes.
- **The reference's rim has no light direction** (§5.89 §5): top equals bottom and left equals
  right to three decimals on every solid; vitrea's two-light rim spreads the sides by 0.15.
- **W9's law is better in dark than in light on the thick rows** (§5.89 §3): P3 0.0078 against
  0.0400, the equal-mean gap predicted to 0.001, `rrect-ml` interpolated to 0.0038 with no anchor.
- **The dark remainder runs downward** (G0, claims §5.88 §3): every thick dark cell settles below
  the strength-0 render, so the clamp in play is the black one — the mirror of W9's white clamp —
  and at strength 1 the light anchors overshoot the dark reference by a factor of six. The
  thin/thick inversion shows as opposite signs of the required strength at one encoded input.
- **A locked console session blocks the native probe totally and invisibly** (G0, §5.88 §4 and
  its correction): the window never becomes key, every cell attests inactive, and HID idle, the
  session flags and the power assertions all look healthy. First read as a Screen Sharing failure
  — that session was coincident — and corrected the same day by asking LaunchServices, which
  names `loginwindow` in front and the lock flag set. §5.17's failure mode, now refused by the
  runner in one second; in the tracker with the harness-side fix.
- **The harness's tint guard reported the activation fault as a colour fault** and its default
  deletes the staged bundle — the evidence that diagnosed the fault survived only because the
  second run passed `--allow-colourless-tints`.
- **The canonical dark bed's worst "interior" gap is the rim.** Over the dark solids the native
  silhouette is the rim ring in fragments, so the interior rows of `dark-solid__rrect-md` measure
  the rim on both sides (0.041 native, 0.211 web) and the cell is excluded from the gate by the
  predicate. The finding, claims §5.87.
- **Thin brighter than thick in the dark scheme** over structured backdrops (0.10 against 0.047) —
  the row order inverts between schemes at the mid inputs.
- **The dark reference's rim is flat across sides** where the light scheme's is two-light.

## Revision Notes

- 2026-09-07: G0 CLOSED (claims §5.89) — the dark reference measured over seven attested runs (a
  locked console cost ten runs and one mid-run input another; every one named in provenance);
  Decision Log 2 written with G1's binding design: the measured anchors with the thin top at the
  footprint reading, `specularGain` 0 and `rimAlpha` on the solids, `tintAlpha` on the passthrough
  rows, the appearance switch and the collapsed rim deferred with their numbers; three Surprises;
  six Deferred entries; G1 dispatched.
- 2026-09-06: G3 MERGED ahead of its edge — the plumbing needs no probe number and X7's test fails
  G1's re-recording until the export is regenerated; the API lands opt-in on the parent's
  recommendation under the standing instruction (Decision Log 1); one review finding and two
  browser-test defects fixed before the merge; one Deferred entry (the demo's unit suite).
- 2026-09-06: G0 PARTIAL (claims §5.88) — the bed, the instrument (validated by injection and by
  re-scoring W9's light probe under both interiors) and the endpoint diagnostic delivered and merged;
  the native probe blocked by a locked console session (first read as Screen Sharing, corrected the
  same day), the user's to unlock; three Surprises. G3 built on its branch ahead of its edge (the plumbing does not need the probe's
  numbers; X7's test carries G1's re-recording through), one review finding in fix.
- 2026-09-06: v1 — chartered on wave Decision Log 23 (c) from claims §5.87, the finding pinned the
  same day (the dark bed read under the declared geometry: the body a response surface the profile
  lacks, the rim the light scheme's at seven to ten times, the passthrough halved; the matrix's
  "interior" on the dark solids a rim reading); Decision Log 1 written; G0 dispatched.

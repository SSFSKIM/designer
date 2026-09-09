# W25 — the thick-span composite: the thick surface's body, its kernel and its key (2026-09-09)

**Status: CHARTERED 2026-09-09 on the user's word ("the thick-span composite is the larger piece
after it", at the 0.11.0 bump; "looking good, better fidelity" on the W24 sheets at the 0.13.0
publish) — the last item of wave Decision Log 23 (c)'s GPU order. G0 dispatched on the fixtures
already on disk; the bed amendment and every native capture wait on the user (Decision Log 1).**

Composite spec: design at the top; Decision Log, Surprises, Deferred and Revision Notes at the
tail. Parent: `2026-08-28-post-v1-wave.md` (the W25 row; Decision Log 23 (c)). Grounding dossier:
`packages/calibration/results/2026-09-09-w25-thick-span-composite/finding/dossier.md` (read-only,
assembled from the ledger at `4c6b321`; every number below is cited there).

## Purpose

Every wave since W20 fitted the thin capsule and read the thick surfaces out once per frozen
configuration. What the ledger records on thick surfaces is one family with five names: the base
pane's haze in the nested pane (the user's eye, twice: "Apple's bottom glass is very slightly less
transparent"), the scatter kernel's width (the reference's σ 2.63 device px at 1x and 1.30 at 2x
through the collapsed capsule, vitrea's 1.68 → 4.86 running the other way), the transmitted dot's
width (7.57 against 4.99 CSS px at 1x), the along-side rim variation on thick panels (0.0442 →
0.0158 along one straight edge of the 2x dark `dark-solid__rrect-md`, flat on the capsule and
`rrect-sm`, graded on `rrect-md` and `rrect-lg`), and the thick rrect's body level (−2.93 codes on
the dark bed). Behind all five is one mechanism and one bed: the size law's argument is the short
side in CSS px and saturates at 96, so `rrect-md`, `rrect-ml`, `rrect-lg` and the nested base are
one number to it; and the two largest spans and the only stacked case are wholly holdout, so no
thick constant has ever been fitted on the rows it is for.

The wave's purpose is the thick surface's body as Apple draws it — its haze, the kernel that haze
comes through, what the kernel and the level do as the span grows past 96, and what keys the
collapse on a thick surface — measured by an instrument that returns a width with a residual it
trusts on both sides, fitted on rows that identify the constants, and read on the eye's cell: the
nested pane's base.

## Parent-Level Acceptance

Binding. The numbers are the charter's; the declaring child re-declares them with G0's readings.

1. **The haze is measured before it is fitted.** The reference's kernel width on every thick cell of
   both beds at both scales (`rrect-md`, `rrect-ml`, `rrect-lg`, `toolbar-group`, the nested base)
   reads with a residual the instrument's own validation bounds, on both sides; the σ-match's
   16.00 ceiling and the edge-spread's "not identifiable" residual are retired as readings. What
   unit the reference's width is invariant in (device px, CSS px, a fraction of span, neither) is
   stated with the evidence.
2. **The thick surface's body matches.** On every thick untinted cell of both beds at both scales,
   the body's kernel width within 15 % of the reference's and its level within 0.002 linear
   (the dark `dark-solid__rrect-md`'s −2.93 codes closed or the read says which term keeps it);
   the transmitted dot's FWHM through `impulse__rrect-md` and the collapsed capsule within 1 CSS
   px of the reference's at both scales.
3. **The nested base is Apple's.** `checkerboard__glass-over-glass__rest`'s base pane (the eye's
   cell): its σ-match within 15 % of the reference's at both scales in both schemes, read with the
   W22 stack reader whose ceiling is raised until neither side saturates; the overlay's sign
   (W22 G3) held.
4. **The size law's argument is the one the reference uses.** Whatever grades the reference's
   width and level across spans 44, 96, 128, 130 and 160 (short side, long side, area, or a
   saturating curve at some other knee) is what vitrea's law reads, with the knee fitted and the
   lens, occlusion, inner shadow and tone bias that ride `sizeThickness` re-read, not re-fitted.
5. **The collapse's key is read.** `dark-solid__rrect-sm` / `-md` / `-lg` over the dark bed at one
   sitting say whether the reference keys the collapse on span (the tracker's contradiction is a
   fixture state flip) or on something else; the answer is a claims section either way.
6. **The bed no worse anywhere.** Calibration ΔE mean not above the 0.13.0 bed's by more than
   0.0001 in either scheme on the GPU tier; no thin row worse by 0.001 ΔE / 0.005 `ssimMean` (the
   thin capsule is not this wave's and must not move: `sizeThickness` 0 below span 32 and the
   ramp's thin start hold by construction or the read says why); W24's angular reads and W23's
   straight-span reads within 0.005; the fourteen thick floors re-read, every one expected to move
   toward its bound, none re-pinned without the user.
7. **The holdout once**, at the declaring child's dry run on the frozen configuration — on the
   amended bed if the user amends it, and read on `rrect-lg` and `glass-over-glass` as holdout if
   they stay so.
8. **The CSS tier derives what it can.** Its one `blur()` carries the kernel's width; its interior
   spread on the large spans (32–63 % under) and the coherence pin (`crossTierOklabDeltaEMean`
   ≤ 0.05, the checkerboard cells already at 0.023–0.043) are re-read, and a residual is recorded
   under Decision Log 23 (a), not chartered.
9. **By eye, and the ledger.** The sheet with the nested pane and the thick rrects native | before
   | landed at 2× with the base pane cropped; the user's veto kept. The cut after the landing.

## Grounding Baseline (the 0.13.0 bed, matrix at `4a2f766`)

- The haze headline is half a measurement. `blurSigmaNative` on the 2x dark nested base reads
  4.8397 at residual 0.3575 (identified); the web side reads 0.6920 at residual **1.8113**, which
  `src/report.ts:391–397` defines as "σ is not identifiable"; the CSS sibling 1.2393 at 1.1816.
  Claims §5.94 §5 quoted the web residual as the pair's — corrected beside (claims §5.112). The
  σ-match reads 16.00 native at both scales' 2x, the grid's ceiling; at 1x it reads 1.50 native
  against 2.20 web, the opposite sign. Two instruments, two units, one saturated.
- The kernel through the dot (`g1/psf.py`, box ⊗ sharp + heavy Gaussians in device px, bounds
  load-bearing): native `impulse__rrect-md` 2.87 / 1.40 device px at 1x / 2x, landed 1.68 / 4.86;
  native `impulse__capsule-button` 2.63 / 1.30. The 2x/1x peak ratio 3.85 is the dot's geometry.
- The along-side variation: 2x dark `dark-solid__rrect-md` top edge 0.0442 → 0.0158, silhouette
  straight to 0.06 px, interior uniform; no vitrea number (constant along a side by construction).
- Body levels: `dark-solid__rrect-md` dark 0.01527 native / 0.01299 web (−2.93 codes) at both
  scales; the collapsed capsule −0.0029 / −0.0033.
- The size law: `spanPx = min(width, height)` (`instances.ts:204`); `sizeThickness` = smoothstep(32,
  96, span), exactly 1 at 96 and above; the scatter ramp's `far` anchor (`material.ts:847–858`)
  exists to route around that saturation; the collapse's size bias 0.05 enters the tone curve's
  argument. `sizeScatterFloor2x` = 1 makes the deep-value span curve inert at 2x.
- The bed: `rrect-lg` and `glass-over-glass` wholly holdout; the light bed has two fittable solid
  thick cells and the dark bed one; 11 of 31 predicate exclusions and all 14 floors are thick rows.
- The probe grids (W9 light, W21 dark) were rendered by wave-local scripts with `VITREA_SCENES`;
  their native fixtures are what W23 fitted the rim's law on; the dark grid collapses `rrect-sm`
  and `rrect-lg` and not `rrect-md`.
- A native capture needs the console session unlocked (claims §5.17's mode; W21 G0's blocker).

## Design (advisory unless marked)

**The instrument comes first, and it is three readers agreeing (binding: the joint view settled
it — every prior width number is from a different instrument in a different unit).** (a) The dot's
PSF (`psf.py`) where an impulse backdrop exists — `impulse__rrect-md` on both beds, the collapsed
capsule — extended to a per-span probe if the grids are captured. (b) The edge-spread on a
resolvable checker step (`blurEdgeSpread`) with the ceiling raised from `max(length/2,
4·guess)` until the residual identifies σ on the web side, read on every checkerboard thick cell.
(c) The whole-region σ-match (`read-stack.py`) with the grid extended past 16 until the native side
leaves the ceiling. Where two of the three agree within their residuals, the width is a reading;
where they do not, the disagreement is the finding.

**One law, one unit, per scale (advisory).** The reference's width halves in device px from 1x to
2x and quarters in CSS px; vitrea's doubles. A per-scale anchor already exists for every scatter
constant. The likely form is the sharp σ in device px as a function of span with a knee above 96,
and the heavy share riding the same knee — the `far` anchor generalised into the law rather than
bolted beside it. The size law's argument may stay the short side (the nested base's 130 grades
between 128 and 160 in the outer shadow's lift, which is the one thick-span quantity Apple's
already fit); if the reference grades on area or the long side, that is clause 4's finding.

**The along-side term is a rim term and waits for its reader (advisory).** The angular reader bins
by normal; a position-along-side reader on `rrect-md`, `-ml`, `-lg` and the nested base is G0's
to build and read. If it is a thickness term (graded with span, flat on the capsule), it is this
wave's; if it is the reference's lens (a refraction of the backdrop's own gradient), it is W12's
and is recorded, not taken.

**The collapse's key is a native question.** The dark grid's `rrect-sm` / `-md` / `-lg` at one
sitting; the user's console. Until then, G0 reads the existing grid fixtures for a state flip (the
bistability's signature, claims §5.17) and says what a re-capture would settle.

**The bed amendment is the user's, and G0 makes it concrete (binding: it re-partitions the
holdout).** Two shapes, not exclusive: (i) `rrect-lg` and `glass-over-glass` cells moved from
holdout to calibration — the rows the constants are for, at the cost of the two largest spans as
the independent check; (ii) the probe grids captured as a declared harness set with structured
backdrops (`impulse` and `checkerboard` over `rrect-sm`, `-md`, `-ml`, `-lg`) — the fitting ground
for a width law that a solid backdrop cannot measure, keeping `rrect-lg` and the stack as holdout.
The parent's recommendation is (ii), with (i) for `photo__rrect-lg` alone if the grids cannot be
captured; G0 reports which constants each shape identifies (the W23 lesson: the condition before
the fit) and Decision Log 2 rules with the user.

**The fourteen floors move (advisory).** All are thick rows over `checkerboard`; the seven
nested-pane shape floors are the extractor's and will move both ways as the base's haze changes.
The extractor fix (a morphological close at the rim's own width before counting bodies; the
tracker's two entries) is in scope for the landing child if the floors move against their bounds
for that reason alone, and out of scope otherwise.

## Children

### G0: The width instrument, the read on every thick cell, the size law's argument, the along-side reader — spike (deliverable: findings)

- **Purpose:** three width readers validated on a known kernel and agreeing on the reference; the
  reference's width and level on every thick cell of both beds at both scales in both schemes with
  residuals; the same on vitrea's landed captures; what the width and level do across spans 44 →
  160 and in which unit; the along-side rim profile on the four thick shapes; the dark grid's
  fixtures read for a state flip; which constants each bed amendment identifies. No native
  capture; the fixtures on disk and the canonical `web-captures/` only. Findings in
  `results/2026-09-09-w25-thick-span-composite/g0/g0-findings.md`.
- **Acceptance:** each reader recovers a known σ within 5 % on a synthetic (the W13 validation
  pattern); on the reference every thick cell has a width with a residual under the reader's own
  bound or is named as unmeasurable with the reason; the argument question answered with a table
  (span, short side, long side, area against width and level); the along-side profile tabled per
  shape with the capsule and `rrect-sm` as the flat controls; the amendment's identification table.
- **Stops:** none (a spike). **Edges:** blocks G1, G2. **Track:** spike; opus; worktree.

### G1: The bed amendment and the native captures — controlled (the user's)

- **Purpose:** the split amended in `scenes.json` as Decision Log 2 rules (the grids as a harness
  set with structured backdrops, and/or large spans into calibration); the reference harness
  capturing the new scenes at one sitting in both schemes at both scales with the console
  unlocked; the collapse's key read on the dark `rrect-sm` / `-md` / `-lg` at that sitting;
  the fixtures committed as evidence. The only child that writes `scenes.json` or `fixtures/`.
- **Edges:** blocked-by G0 (the identification table), the user (the amendment, the console).
  Blocks G2's fit on the amended rows. **Track:** controlled; in the main checkout; the parent
  runs the harness with the user present.

### G2: The kernel and level law fitted, the argument re-keyed — controlled

- **Purpose:** the width law per scale in the unit G0 found, the level's term, the size law's
  argument and knee, fitted on the identifying rows through a scratch ladder and checked off them;
  the lens, occlusion, inner shadow and tone bias that ride `sizeThickness` re-read at the new
  knee; the along-side term taken or recorded per the Design; the collapsed body's level if a
  row identifies it. Mechanisms inert at the defaults so 33 goldens stay byte-identical before the
  declaration.
- **Edges:** blocked-by G0; G1 for the amended rows (G2 may start on the current bed's rows and
  re-fit when G1 lands). **Track:** controlled; opus; worktree.

### G3: The form declared and dry-run — controlled

- **Purpose:** the constants declared with the fingerprints, the documents re-recorded once, the
  goldens under `W25_HASHES` with attribution, the CSS mirror (`blur()` at the new width; the
  coherence pin re-read), the dry run on all six profiles and both tiers with the holdout read
  once; stops declared before the run; the sheet; the claims section by the parent.
- **Stops:** W24 G2's S1–S8, S10, S11 (with W24's angular reads added to S11's family); (S12) any
  thin cell moved by more than 0.001 ΔE; (S13) a golden moved outside a thick surface's body.
- **Edges:** blocked-by G2. **Track:** controlled.

### G4: The landing and its referee — controlled

- As W24 G3: the canonical rebuild from the main checkout, the referee, the predicate re-derived,
  every floor re-read (the extractor fix if the Design's condition holds), the demo fixture, the
  changeset (`vitrea-web` minor, 0.14.0), the sheets, the chain, the user's eye.
- **Edges:** blocked-by G3. **Track:** controlled; the landing is the user's call.

## Cross-Child Contracts

- **X1 (binding)** The width instrument is G0's three readers; every width in this wave is read by
  them, with the residual beside the value, and a saturated grid or an unidentifiable residual is
  not a reading.
- **X2 (binding)** `scenes.json`, `fixtures/`, the canonical `matrix.json` and `web-captures/` are
  written only by G1 (the amendment and its captures) and G4 (the rebuild). Every other child
  works to scratch with `--out-matrix` and `VITREA_WEB_CAPTURES`.
- **X3 (binding)** The holdout is read once, at G3's dry run, on the frozen configuration; G4
  reproduces the bytes.
- **X4 (binding)** The GPU is shared: one capture process at a time; the harness's native
  capture and the web capture never overlap; goldens in the foreground.
- **X5 (binding)** The thin capsule does not move: `sizeThickness` 0 below 32 and the ramp's thin
  anchors are re-read at every rung, and a thin cell moved by more than 0.001 ΔE stops the ladder.
- **X6 (binding)** The user's eye keeps its veto; nothing publishes before the sheets.
- **X7 (binding)** The dark profile is a difference document; a thick constant lands on the light
  patch unless the dark bed separates it, and `dark-profile.ts` is regenerated, never edited.

## Ordering & Dependency Map

G0 → (the user: the amendment, the console) → G1 → G2 (may start on G0 alone) → G3 → G4 → the
0.14.0 cut. G1 is the only child gated on the user's presence at the capture machine.

## Risks & Mitigations

- **The reference's width is not identifiable on structured backdrops either** (the checkerboard's
  step is 20 CSS px; the dot is 4). Mitigation: three readers, and the grids' impulse rows if
  captured; if none identifies it, the wave narrows to the level and the argument, recorded.
- **Moving the knee moves four laws** (lens depth, occlusion, inner shadow, tone bias). Mitigation:
  re-read, not re-fit; the ladder reads all four at every rung; any that moves against a bound is
  a stop.
- **The fourteen floors flip on the extractor.** Mitigation: the Design's condition; the fix is a
  landing-child item with its own read.
- **The console stays locked.** Mitigation: G0 and G2 run on the fixtures on disk; the wave lands
  what the current bed identifies and records the rest.

## Deferred / Out of Scope

- The CSS tier's large-span interior spread (32–63 % under; the encoded space) — Decision Log 23
  (a); recorded, not chartered.
- The dark thin capsules' passthrough (−16 / −19 codes; §5.89) — a thin term.
- The lit edge's scale-dependent exponent and the null's floor (W24's tracker entries).
- The coverage charters after this wave (Decision Log 23 (c)'s tail).

## Tracking Map

| child | status |
| --- | --- |
| G0 — the width instrument, the read, the argument, the along-side reader | DISPATCHED 2026-09-09 |
| G1 — the bed amendment and the native captures | — (the user's; Decision Log 1) |
| G2 — the law fitted | — |
| G3 — declared and dry-run | — |
| G4 — the landing | — |

## Decision Log

### Decision Log 1 — the charter, the instrument first, the amendment and the console named as the user's (2026-09-09; the parent, on the user's word)

(a) **Chartered** on the user's word at the 0.11.0 bump and the eye's verdict at the 0.13.0 publish;
the last item of wave Decision Log 23 (c)'s GPU order. The dossier grounded it read-only.

(b) **The instrument before the fit.** The haze headline was one identified number and one
unidentifiable one (the web residual 1.81 misquoted as the pair's at claims §5.94 §5; corrected
beside in §5.112), and the σ-match's native 16.00 is a ceiling. No constant is fitted on a width
until three readers agree; G0 is a spike for that reason and reads only what is on disk.

(c) **The amendment is the user's**, because it re-partitions the holdout. The parent recommends
the probe grids as a declared harness set with structured backdrops (the fitting ground a width
law needs) over moving `rrect-lg` and the stack out of holdout; G0's identification table makes
the choice concrete and Decision Log 2 rules it with the user.

(d) **The console is the user's.** Every native capture — the grids, the collapse's key at one
sitting — needs the console session unlocked at the capture machine. G0 and G2 do not wait on it;
G1 does.

(e) **Scope.** The five named items are one family and are taken together as far as the bed
identifies them; the along-side term is taken only if G0 reads it as a thickness term; the
extractor fix only if the floors move on it alone. What the bed cannot identify is recorded with
the rows that would.

## Surprises & Discoveries

- **The haze was never measured on the web side.** The residual that says so was quoted as the
  reference's.
- **The size law cannot tell the thick cells apart.** Span 96, 128, 130 and 160 are one number to
  `sizeThickness`; the scatter ramp's third anchor is the workaround on record.
- **The two largest spans were never fitting rows.** Every thick constant was read out on them.

## Outcomes & Retrospective

(at recomposition)

## Revision Notes

- 2026-09-09: chartered; G0 dispatched; the amendment and the console named as the user's.

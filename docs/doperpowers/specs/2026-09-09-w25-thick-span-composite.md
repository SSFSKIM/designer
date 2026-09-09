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
| G0 — the width instrument, the read, the argument, the along-side reader | CLOSED 2026-09-09 (claims §5.113; `g0/g0-findings.md`; merged `058dd64`; Decision Log 3) |
| G1 — the bed amendment and the native captures | CAPTURED 2026-09-09 (claims §5.115; `b60706b`: 207 fixtures at both scales, one omitted by ruling; `g1/provenance.json`, `sweep-read.txt`; Decision Log 5) |
| G2 — the law fitted | CLOSED 2026-09-09 (claims §5.114; merged `17b7af1` inert; the 1x fits as priors; every constant to G3 on the probe set; Decision Log 4) |
| G3 — declared and dry-run | CLOSED 2026-09-10 (claims §5.116; `g3/g3-dryrun.md`; merged `0011bf5`; the pair (0.85, 0.10) declared, four constants declined; Decision Log 6, 7) |
| G4 — the landing | DISPATCHED 2026-09-10 (the main checkout; Decision Log 7 (d)) |

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

### Decision Log 2 — the bed amendment and the console, both on the parent's recommendation by the user's word (2026-09-09; the user: "both on your recommendation")

(a) **The amendment is (ii):** the probe grids captured as a declared harness set with structured
backdrops — `impulse` and `checkerboard` over `rrect-sm`, `rrect-md`, `rrect-ml`, `rrect-lg`, with
`capsule-button` as the thin control — in both schemes at both scales, as calibration rows;
`rrect-lg` and `glass-over-glass` stay holdout. (i) for `photo__rrect-lg` alone if the grids cannot
be captured. G1 designs the set on G0's identification table (which spans and backdrops separate
which constants) and writes `scenes.json` once; the split's new rows are named in the claims
section before the first capture.

(b) **The console:** the parent runs the harness when the screen is unlocked and asks the user to
unlock it at that moment. Read now: `CGSSessionScreenIsLocked` true with the user on console and
a Screen Sharing agent active — W21 G0's blocker exactly (claims §5.17: Screen Sharing does not
unlock the console session). G1's capture waits on the unlock; G0 and G2 do not.

(c) **The read that settles the collapse's key** (`dark-solid__rrect-sm` / `-md` / `-lg` at one
sitting) is taken at G1's sitting, in the same session as the harness set, so the grid and the
key share a session state.

### Decision Log 3 — G0 read: the kernel is two components and the thick-span mechanism is the heavy share; clauses 1, 2 and 4 re-declared on the evidence; the along-side term taken as a position field; the amendment sharpened to the grids whole at both scales with coarse structure; two grid fixtures withdrawn; G1 and G2 dispatched (2026-09-09; the parent, on the user's standing instruction)

Evidence `results/2026-09-09-w25-thick-span-composite/g0/` (`g0-findings.md`, `validate.txt`,
`widths.txt`, `levels.txt`, `argument.txt`, `along-side.txt`, `grid-state.txt`,
`identification.txt`), merged at `058dd64`. Verified by the parent: the validation table (reader
A recovers 2–16 device px at both scales; B binds on the backdrop's step pitch, not the ceiling;
C's guards), the headline widths, the levels table, the antisymmetric slopes, the grid's manifest
frequencies and the two byte-identical files.

(a) **The kernel is two components, and every width in the ledger was a true reading of a
different part of it.** The same reference cell at 1x reads 1.30 device px against a 16 CSS px
checkerboard, 4.75 against 32 and 6.25 against 64, where a single Gaussian returns one number at
every pitch (validated to 0.00 %). Reader A on the uncollapsed `impulse__rrect-md`: sharp 2.79 →
1.40 and heavy 19.52 → 11.29 device px from 1x to 2x (both halve; W24 G1's 2.87 / 1.40 and 28.9 /
11.1 reproduced to 0.08 px), and the heavy SHARE 0.47 → 0.69. The collapsed capsule's share is
0.00 — W24's "reference kernel" was the collapsed material's, and the Design's "vitrea runs the
other way" compared vitrea's single width with the reference's sharp component; like for like,
both grow. The thin and the thick surface differ in the share, not in a width (pitch 64: thin
2.00–2.10, thick 6.00–6.75; pitch 16: all 1.2–1.6). vitrea's share at 1x is 0.23 against 0.47,
and its 1x kernel is 32–46 % too wide on every thick span on two readers in both schemes; on
`photo` its width falls 14–19 % short on `rrect-ml` and `-lg`, a gap that opens with span.
**Ruling: the wave's mechanism is the heavy share and the sharp width per scale, riding
`sizeThickness`** — the deep-value law re-expressed as a share the bed can identify — and clause 1
is re-declared: the width is the triple (sharp σ, heavy σ, share) read by reader A on the impulse
rows and by readers B and C on the coarse checkerboards, with the residual beside; the edge-spread
reader identifies to one eighth of the pitch and no ceiling changes that, so "retired as a
reading" is struck and "read at the pitch that identifies it" stands. Clause 2's "kernel width
within 15 %" becomes sharp σ within 15 % and share within 0.05 at both scales on every thick
untinted cell a fixture identifies.

(b) **Clause 4 is answered in the landed law's favour, with a residual above the knee.**
`sizeThickness(short side)` at knee 96 scores r 0.95–0.998 against 0.68–0.96 for the long side,
area, √area and radius, on width and level, both grids, both schemes. The width does not grade
above 96; the LEVEL does, by about a fifth of the thin-to-thick step per span doubling to 160,
where the curve is flat. The knee's lever is 0.002 on every bed shape (a smoothstep's derivative
vanishes at its edge). **Ruling: the argument and the knee stay; a level term above the knee is
this wave's** (identified on 118–238 level rows), and the lens, occlusion, inner shadow and tone
bias are not touched. Two levels larger than the chartered miss are on record now and are the
level term's rows: `checkerboard__toolbar-group` +8.77 / +9.34 codes (a calibration row; members
span 44, thin to the law — G2 reads whether the level term or the group's sampling carries it)
and `photo__rrect-md` dark −5.41 / −5.55.

(c) **The along-side term is taken, as a position field.** Present on flat solids where a lens
has nothing to refract (range 0.0187 / 0.0226 / 0.0345 at span 96 on `light-solid` /
`dark-solid` / `mid-dark-solid`), zero at spans 32 and 44, saturating above 96 — it rides
`sizeThickness`. Its shape is a corner-to-corner diagonal ramp: the four sides' slopes exactly
antisymmetric (top −0.000192, bottom +0.000192, left −0.000379, right +0.000379 luma per CSS px
on the 1x dark `dark-solid__rrect-md`), slope × side length reproducing the range. vitrea's
per-normal factor is 1 on every straight side (landed range 0.0015–0.0083 against 0.0206–0.0357).
**Ruling: the lit-edge amplitude takes a linear field along the diagonal across the surface,
riding `sizeThickness`, one constant for the slope per unit span** — G2's third mechanism, with
its clause: the corner-to-corner range on the thick solids within 20 % of the reference's, zero
on the capsule and `rrect-sm` by construction. On `checkerboard` the reader correlates 0.85–0.96
with the backdrop under the body — that is the lens, separable only on the solids, and the
solids are where the constant is fitted. The 2x reference's rim MEAN is top-left/bottom-right
asymmetric (0.0330 / 0.0313 against 0.0168 / 0.0176) where the 1x is symmetric: recorded, not
taken (tracker).

(d) **The grid's contradiction resolved into two halves; two fixtures withdrawn.** The W21 dark
grid is seven attested runs at one sitting with per-cell byte-state frequencies; 18 of 56 cells
are bistable. `dark-solid__rrect-sm` is one, and its majority state is byte-identical to the W9
LIGHT grid's file — as is `light-solid__rrect-sm`, whose body 0.96659 over a 0.8918 backdrop is a
light-scheme frame beyond doubt. **Both are withdrawn as dark readings** (a tracker entry names
them; nothing on the bed was fitted on them). `rrect-md` (96, uncollapsed) against `rrect-lg`
(160, collapsed) is single-state in all seven runs and SURVIVES: the reference collapses the
large surface and not the middle one over `dark-solid`, and on the 320 × 200 canvas span is
confounded with clearance (84 / 52 / 20 CSS px at 32 / 96 / 160). **Ruling: G1's sitting
re-captures the two withdrawn cells under the dark scheme, adds `dark-solid` at spans 48, 64, 80
and 128 in both schemes, and separates span from clearance (`rrect-md` at a 20 px margin, or
`rrect-lg` on a wider canvas) — clause 5 is read on those rows.** The dark contrast is six codes
where the light is a hundred; the light grid carries the same question at a hundred.

(e) **The amendment, sharpened within Decision Log 2 (a).** Shape (ii) buys one 2x width row at
span 96; the grids as they stand are 1x only and buy nothing at 2x; the heavy share is carried by
four rows today, all of them collapsed or `checkerboard-64`; the collapsed body's level needs the
grids' solids. **Ruling: the harness set is the grids whole — solids kept — captured at BOTH
scales in both schemes, plus coarse structured backdrops (`checkerboard` at 32 and 64 CSS px
pitch, and `impulse`) over `rrect-sm`, `-md`, `-ml`, `-lg` at both scales, which is the only
fixture that identifies the 2x width above span 96.** Declared as a `probe` fixture set in
`scenes.json` beside `recorded`: read by the fits and by claims, captured routinely by the
harness, and not a gated set — the gate's counts, predicate and floors do not move on it.
`rrect-lg` and `glass-over-glass` stay holdout. G1 designs the set to that rule and the parent
runs the harness at the user's unlock.

(f) **G1 and G2 dispatched.** G1 (a worker in a worktree, then the parent at the console): the
`probe` set declared in `scenes.json` and the harness's scene files, `compare.ts` reading it
through `--set probe`, the gate ignoring it by name, the two withdrawn fixtures listed; then the
native capture at both scales in both schemes at one sitting with the collapse-key rows. G2 (a
worker in a worktree, on the current bed and the 1x grids): the three mechanisms inert at the
defaults — the share law per scale on `sizeThickness`, the level term above the knee, the
along-side field — with the readers of G0 as the ladder's instruments, fitted on what the 1x rows
identify (the 1x sharp σ and share, the level term, the along-side slope) and re-fitted at 2x
when G1's fixtures land; a thin cell moved by more than 0.001 ΔE stops the ladder (X5).

### Decision Log 4 — G2 read: the three mechanisms merged inert; the share's only identifying row is a validation row and its off-row check runs the other way, so every constant is fitted once at G3 on the probe set; the level term's shape and the field's form re-formed on the rows; the sitting under way (2026-09-09; the parent, on the user's standing instruction)

Evidence `results/2026-09-09-w25-thick-span-composite/g2/` (`g2-findings.md`, `fit-share.txt`,
`fit-level.txt`, `fit-field.txt`, `condition.txt`, `thin-invariance.txt`, `rides.txt`,
`goldens-attribution.txt`, `ladder.sh`), merged at `17b7af1` with the constants at their inert
defaults (fingerprints unchanged at the defaults; the renderer's goldens not yet re-run on the
GPU because the sitting owns it — G3's first step, expectation 33 / 33). Verified by the parent:
the chain green on the branch, the thin-invariance table (worst 0.000196 ΔE, 21 `rrect-sm` cells
at exactly 0), the four riders unmoved, the ladder's ΔE columns.

(a) **The mechanisms stand as landed.** The share law: `kDeep` gains `lift · sizeThickness(span)`
with `sizeScatterHeavyShareThick1x` / `2x`, the thin end untouched (X5 by construction: 0 at and
below span 32). The level term: `sizeToneLevelFar` on the tone response's return, on
`smoothstep(sizeSpanMax, sizeScatterSpanMax, span)`, exactly 0 at and below 96 (77 control rows
read a rendered lever of 0.000000). The along-side field: the rim's amplitude ×
`max(1 + slope · sizeThickness · (x/hw)(y/hh), 0)` in `rimLit.w`, `rimAlongSideSlope`. The 1x
sharp σ is `blurSigma`, the thin capsule's own width (the reference's sharp component is span-flat
to 6 %: 2.62 collapsed against 2.79 thick), and this wave may not move it.

(b) **Two forms overturned on the rows, accepted** (the worker's Surprises above record them). The
field is the PRODUCT of the normalised coordinates, +1 at the top-left and bottom-right corners,
not a ramp along the diagonal: a ramp gives the top and bottom the same slope in x, and G0
measured them equal and opposite. The level term is an OFFSET above the knee, not the
thin-to-thick blend continued: Decision Log 3 (b)'s "the sign follows the backdrop" read the
reference's absolute grading, and the residual against vitrea is backdrop-independent because
vitrea's own deep value keeps rising to `sizeScatterSpanMax` 256 where the reference's width stops
at 96. The blend form explains 0.3 % of it, an offset 39 %. Decision Log 3 (b) corrected beside.

(c) **The share is not landed at 0.455, and the reason is the discipline, not the number.** The
1x share is identified by ONE row on the canonical bed, `impulse__rrect-md`, a validation row
(the only other impulse cell is collapsed, share 0.00 on both sides). Its check off that row runs
the other way: reader C's single-width objective over the grids' structured rows worsens
monotonically with the lift (0.2507 → 0.2769), because vitrea's heavy component is 13.3 device px
at the reference's own share against 19.5, and `sizeScatterGainMax` is not a lever on it (8 →
10.3 left the reading at 13.29: the heavy tap is a mip-chain level whose width saturates). And
the bed cost breaks clause 6 (+0.00041 canonical, +0.00087 on the grids at lift 0.48 against
+0.0001). The worker recommended landing it and recording the cost; the parent rules otherwise:
a constant fitted on one validation row, contradicted by its off-row check, at a cost above the
clause, with 44 identifying rows at five spans and both scales arriving from the sitting within
hours, waits for those rows. **Every constant — the share at both scales, the level term, the
field — is fitted once at G3 on the probe set**, G2's 1x fits (lift 0.455 → share 0.434 against
0.473; `sizeToneLevelFar` 0.029 light / 0 dark on 14 rows, RMS 1.486 → 0.977; slope 0.45 on 64
sides, range 0.743 of the reference's) standing as the priors with their condition recorded. One
declaration, one holdout read (X3).

(d) **The level term's scheme separation is provisional.** The dark grid fits ~0 and worsens by
2.5 codes RMS at the light value, and the reason is physical (its collapsed-to-uncollapsed
contrast is six codes where the light's is a hundred); G3 re-reads it on the probe set's dark rows
at both scales before the dark document pins anything.

(e) **The 2x anchors need a different lever.** At dpr 2 `sizeScatterFloor2x` = 1 saturates
`kDeep`, so the 2x lift is clamped away whatever it says, and vitrea's sharp width runs 1.67 →
3.51 device px across scales where the reference's halves (2.79 → 1.40). G3 fits the 2x share
through the floor (or the constant that has headroom) and adds a `blurSigma2x` sibling only if
the 2x coarse checkerboards identify it. Tracker.

(f) **Gaps recorded** (tracker): the heavy tap's saturated width; the sharp component 1.67
against 2.79 at 1x (X5-entangled with the thin capsule); the field closing three quarters of the
range (the last quarter in W23's amplitude law); the CSS tier unable to draw the field (X8
residual, Decision Log 23 (a)); the above-knee residual being vitrea's own span curve continuing
(a lower `sizeScatterSpanMax` may be the reference's term, X5-entangled; the wave's Deferred list).

(g) **The sitting.** The harness rebuilt for the `probe` role (`build.sh`, 14 backgrounds
byte-stable against the W21 grid's rasters), the grant re-added by the user and confirmed through
the bundle's own path (`open … --args probe`: ScreenCaptureKit OK, window key), the screen
unlocked; the 1x pass started 06:33Z by W9's protocol (`g1/run-sitting.sh`: 6 s reset, 45 s
idle, seven attested runs), the display held awake, every other capture held (G2 told to hold;
the runner refuses a running capture). The 2x pass follows; then `materialize --set probe`, the
two withdrawn cells checked against the light grid's bytes, the bistable shares read; then G3.

### Decision Log 5 — the sitting read: 207 probe fixtures at both scales, one cell omitted by ruling, the two withdrawn cells reinstated as readings, the collapse keyed on span with the level above the knee grading in the scheme's own direction; G3 dispatched to fit every constant on the probe set (2026-09-09; the parent, on the user's standing instruction)

Evidence `results/2026-09-09-w25-thick-span-composite/g1/` (`provenance.json`, `runs-2x-pass.log`,
`runs-1x-pass.log`, `materialize-*.txt`, `stability-*.txt`, `sweep-read.txt`, `NOTE-labels.txt`),
`apps/reference-apple/fixtures/` at `b60706b`. The parent ran the sitting.

(a) **The record.** The 2x pass ran FIRST: the virtual display was in its HiDPI arrangement and the
harness files pixels under the scale it captures at, so the runs written under `1x/` with labels
`w25-1x-N` carry the 2x profile keys (the manifest's caveat says so; `NOTE-labels.txt`). Seven runs,
six at 158 / 158 and run 3 at 78 / 158 — its first 80 cells captured while the window was denied
activation during remote Screen Sharing activity (the tracker's activation-loss entry; the
per-cell majority is over the runs that attested each cell). Its backdrops were rendered at the
requested 1x naming; every synthetic backdrop's frozen-bed cell captured alongside is
byte-identical to the canonical 2x fixture, the photo backdrop differs (max 7 codes, mean 0.88 —
a bitmap upscaled), and no probe scene uses it. Then `betterdisplaycli set --hiDPI=off`, the
bundle's probe reading backingScaleFactor 1.0, and the 1x pass: seven runs at 158 / 158. The
runner's own guard refused the 1x pass once (the probe app still quitting) and it was restarted.
The fourteen rasters the sitting rendered are byte-identical to the committed ones where both
exist; the seven new ones enter the manifest at both scales.

(b) **One cell omitted by ruling.** `2x-dark / checkerboard-8__capsule-button__rest` returned three
structurally different settled appearances across the seven runs (3 / 3 / 1; maxDelta 51–58 over
19–38 k px, coherence 1.000): a tie no majority settles, and "a majority would publish whichever
state happened to win two runs, which is a coin flip wearing a reference's name" (the tool's own
words). `materialize` gained `--omit PROFILE/SCENE=REASON`, which leaves the hole and writes it,
with the reason and the states, into the bed's provenance. 103 of 104 2x cells published, 70 of
them majority-settled with their shares recorded; at 1x 104 of 104, 3 settled. **The 2x
reference is far less stable across runs than the 1x** — recorded for G3's fit, which reads the
majority states with their shares.

(c) **The two withdrawn cells are reinstated as readings, and §5.113 §6 is corrected beside.** In
every 1x run the dark profile's `dark-solid__rrect-sm__rest` and `light-solid__rrect-sm__rest`
are byte-identical to the same run's LIGHT profile's capture and to the W9 light grid's file — the
flip reproducing under the controlled protocol with the same-sitting light capture as the control
(`g1/sitting.md` §5 (a) named this outcome). They are dark-scheme readings whose appearance equals
the light one: over `dark-solid` the collapse (every span to 64 collapses in both schemes, a shade
below the backdrop, W23's finding); over `light-solid` a small surface renders the LIGHT
appearance in the dark scheme where `rrect-md` and `-lg` render the dark material (0.096 / 0.103)
— a size-keyed scheme adaptation of the reference, a term for the ledger, not a fixture defect.
The withdrawal at Decision Log 3 (d) is overturned on this evidence.

(d) **Clause 5 answered: the collapse keys on span, and the "collapse" of the large panel is the
level law's floor.** `sweep-read.txt`: the clearance variant (`rrect-md` at rrect-lg's 20 px
margin) reads exactly `rrect-md`'s body (0.0153) in both schemes at both scales, so edge
proximity is not the key. Over `dark-solid` in the dark scheme the body reads 0.0110 at spans 32 /
44 / 48 / 64 (collapsed), 0.0169 at 80, 0.0153 at 96, 0.0130 at 128 and 0.0110 at 160; in the
light scheme 0.4739 / 0.4798 / 0.4910 / 0.5022 at 80 / 96 / 128 / 160. **Above the knee the level
grades with span in the direction of the scheme's own material** — darker in dark, lighter in
light — and the 160 px dark panel's collapsed level is where that decline arrives, not a switch.
The W21 grid's contradiction closes. Consequence for G3: the level term above the knee is
SCHEME-SIGNED (G2's 0.029 light and the dark grid's refusal were the two signs seen through three
spans), and the dark document pins its own value, not 0 — Decision Log 4 (d) resolved. The numbers
are identical at 1x and 2x to the fourth decimal: the reference's level is scale-invariant.

(e) **G3 dispatched**: the renderer's goldens first (pending since G2); the probe set captured on
the web on both tiers at both scales to scratch; every constant fitted on the probe set — the
heavy share per scale (with the 2x lever through the floor, Decision Log 4 (e)), a `blurSigma2x`
sibling if the 2x coarse checkerboards identify it, the level term per scheme, the along-side
slope — each with its condition and its check off its rows; the declaration; the documents
re-recorded once; the goldens under `W25_HASHES`; the dry run on all six profiles and both tiers
with the holdout read once; the stops; the sheets.

### Decision Log 6 — G3 read: one constant landable and it collides with W24's exponent at the corners; the share, the 2x share, the level term and the 2x sharp width declined on their own checks; a joint re-fit of `rimLitExponent` with `rimAlongSideSlope` ruled, the W24 constant re-opened; the heavy width chartered as the next wave's mechanism (2026-09-09; the parent, on the user's standing instruction)

Evidence `results/2026-09-09-w25-thick-span-composite/g3/` (`g3-dryrun.md` and the files it names),
on `worktree-agent-a60d759ed0e4373f6` at `6bfe1ba` (not merged: the configuration will not land).
Verified by the parent: the goldens 33 / 33 at the inert defaults; the per-bin table; the share's
three-row identification and its off-row checks; the level term's sign flip across row sets.

(a) **The declines stand, and each is a measurement.** The 1x heavy share is identified on three
rows (implied lift 0.32 / 0.67 / ≈0.51 at spans 128 / 160 / 96) and every check off them runs the
other way — the coarse checkerboards' width objective 0.2373 → 0.3402, nine probe rows past 0.002
ΔE at lift 0.45 and five already at 0.18, the probe mean +0.00018 — because vitrea's heavy
component is 13.3 device px at the reference's share against 19.5 and its width is not a lever
(`sizeScatterGainMax` 8 → 10.3 leaves 13.29). **The wave's central mechanism waits for a heavy
width that is a continuous parameter, which is the next wave's** (Decision Log 7 charters it). The
2x share is arithmetically inert (206 of 206 2x probe captures byte-identical at lift 0.50;
`sizeScatterFloor2x` = 1 saturates `kDeep`) and its lever reaches span 32 / 44 — X5. The level term
is not identified: −0.0035 light / −0.0074 dark on the declared rows, +0.0046 / +0.0006 with every
untinted backdrop counted, the RMS moving less than a twentieth of a code either way — the sweep's
clean grading over `dark-solid` (Decision Log 5 (d)) is one backdrop, and across backdrops the sign
is not one thing; recorded, the mechanism inert. A `blurSigma2x` sibling is not added: reader A
degenerates at 2x above the knee (share pinned 1.000) and a per-scale sharp anchor reaches the
thin capsule.

(b) **The along-side field lands only jointly with W24's exponent.** At slope 0.45 the field
grades the thick solids' rim as the reference does on the straight runs and the near-null bins
(NNE error 0.02837 → 0.00304 on the 1x light `dark-solid__rrect-md`), and OVERSHOOTS the two lit
corners (NW 0.14220 → 0.20344 against 0.12223): W24's `rimLitExponent` was fitted with the position
term absent, on 285 bins that include the corner arcs, and the two terms peak on the same
diagonal. Mean bin error improves on 5 rows (thin) and worsens on 9 (the thick solids the field is
for); no smaller slope rescues it. **Ruling: a joint re-fit of `rimLitExponent` and
`rimAlongSideSlope` on the existing fixtures** — the angular bins and the along-side profiles
together, the thick solids' error at or under the 0.13.0 bed's on every row as the condition to
land — the exponent re-opened by this decision (W24's spec, Revision Note), the light document
re-recorded once more, S11b re-read as an error bound, the dry run re-run, the holdout read once
on the configuration that lands (G3's read belongs to one that does not). G3b on the same branch.

(c) **The gate and the floors.** Fourteen thick floors read, none breached; the predicate moves
31 → 33 (three 2x light cells in, `checkerboard__toolbar-group` 2x light out) — G4's re-derivation.
The isolation proof's shadow bound narrowed to one code (premultiplied two-pass rounding) and
named.

(d) **What the wave will land**: the along-side field with the jointly fitted exponent, the
mechanisms for the share and the level inert with their constants named, the probe set as a
harness set, the width readers, and the record. Clauses 2 and 3 are carried to the heavy-width
wave with their numbers; the recomposition says so.

### Decision Log 7 — G3b read: the pair (0.85, 0.10) lands — the thick solids' angular error at or under the 0.13.0 bed's, the range error down an eighth, the null's floor drawn where the reference keeps one; the landing ruled; the heavy width chartered as the next wave (2026-09-10; the parent, on the user's standing instruction)

Evidence `g3/g3-dryrun.md` (the G3b section), `g3b-fit.txt`, `g3b-bins.txt`, `g3b-stops.txt`,
`g3b-floors.txt`, `g3b-gate.txt`, `g3b-delta-e.txt`, `g3b-digests.txt`,
`g3b-goldens-attribution.txt`, `sheets/`; merged `0011bf5`. Verified by the parent: the per-bin
table, the improve / worsen counts, the sensitivity band, the corner strips by eye on `g3-2x.png`
— the two dim corners now carry the faint rim the reference keeps at the null where the 0.13.0
panel draws nothing, and the two lit corners no longer overshoot.

(a) **The pair.** `rimLitExponent` 1.15 → **0.85**, `rimAlongSideSlope` 0.45 → **0.10**, fitted
together on a rendered grid of 46 points (the two multiply one amplitude and the exponent is a
power; not separable), on 54 rows / 864 angular bins and 58 rows / 220 straight sides of the
untinted solids of both beds and the probe set at both scales, the holdout never opened; the two
readers weighted to contribute equally at the 0.13.0 material, the pick moving one grid step over
±50 % of that weight. The objective's own minimum (0.55, 0.45) is refused because only 5 of 28
thick rows improve there; the allowed minimum (0.70, 0.15) is refused because at it the collapsed
`dark-solid__capsule-button` loses its contour on the GPU tier at 1x and two calibration cells
drop out of the bed — a material change can remove a cell with no stop to catch it (tracker). At
(0.85, 0.10): thick bin error 0.17527 → 0.17208, thick range error 0.43269 → 0.37472, 16 thick
rows improving against 12; on the 1x light `dark-solid__rrect-md` the NW / SE corners 0.203 →
0.137 / 0.139 against 0.122 / 0.127 and the null 0.004 → 0.010 against 0.037. **The gain is
small and it is real**; the reader that measures the along-side range still reads 0.375 of the
reference's grading missing, and the arc's AMPLITUDE (W23's law on the straight spans) is the
wave's largest remaining rim gap, a three-term joint fit for a later wave.

(b) **The clauses and the stops.** Every stop clear with S11b re-read as an error bound (5 of 8
canonical thick solid GPU rows improve, 3 worsen, worst +0.00064); fourteen floors read, none
breached, none moved; the gate 37 / 37 and the predicate unmoved; the holdout read once on this
configuration, every group holding and one CSS group improving; twelve goldens under
`W25B_HASHES` with no pixel outside a contour band. Fingerprints light `9b7806cdefd1d1d6`, dark
`eec7c2ea8dc89cae`; the dark patch unmoved. Clauses 1, 4, 5, 6, 7, 8 met or answered; 2 and 3 not
met, each miss a declined constant (Decision Log 6 (a)); 9 the sheets and the user's eye.

(c) **Two dry runs in one matrix.** G3 and G3b wrote to the same `--out-matrix` and `compare`
appended, so the gate read every cell twice (25 of 37 failing on duplication alone) until
`g3b-reduce.py` kept the rows whose capture path names the documents on disk; the run script now
removes its own matrix first. Tracker.

(d) **G4 dispatched: the landing.** From the main checkout: `rm results/matrix.json`, the whole
bed rebuilt — six profiles × two tiers × (calibration, validation, then holdout) AND the probe set
on the four standard profiles × two tiers (the canonical matrix carries the probe rows under
`fixtureSet: "probe"`; the gate ignores them by test) — the referee against `g3b-digests.txt`,
the gate (37 / 37 expected, no re-derivation), every floor re-read, the demo fixture, the
changeset (`vitrea-web` minor → **0.14.0**: the along-side field, the exponent re-fitted with it,
the probe harness set, the width readers, the three inert mechanisms named), the sheets, the
chain; the user's eye before publish; 0.13.0 published stays.

(e) **The next wave, chartered by this decision: the heavy width.** The thick surface's haze is
the heavy component's share, and the share cannot be raised until the heavy tap's width is a
continuous parameter (13.3 against 19.5 device px at 1x; the mip level saturates). W26 takes the
renderer mechanism (a further pyramid level or a separable blur at the tap, the width fitted on
the probe set's coarse checkerboards at both scales), then the share per scale, the 2x lever
through the floor, and the level term re-read on those rows; the CSS mirror follows. Charter at
recomposition.

## Surprises & Discoveries

- **The haze was never measured on the web side.** The residual that says so was quoted as the
  reference's.
- **The size law cannot tell the thick cells apart.** Span 96, 128, 130 and 160 are one number to
  `sizeThickness`; the scatter ramp's third anchor is the workaround on record.
- **The two largest spans were never fitting rows.** Every thick constant was read out on them.
- **The kernel is two components, and the ledger's widths were all true.** 1.30 / 4.75 / 6.25
  device px on one cell against three pitches; the share is what moves between thin and thick and
  between scales.
- **The along-side term is a diagonal field, not a function of the normal.** Slopes exactly
  antisymmetric across opposite sides on every thick cell.
- **Two of the dark grid's fixtures are the light grid's files**, flagged bistable by the grid's own
  manifest; and span is confounded with clearance on the canvas.
- **The edge-spread reader binds on the backdrop's pitch.** No ceiling identifies a kernel wider
  than an eighth of the step.
- **The reference's level above the knee grades in the scheme's own direction**, darker in dark
  and lighter in light, identical at 1x and 2x to the fourth decimal; the large dark panel's
  "collapse" is where the decline arrives.
- **A small surface over a bright solid renders the light appearance in the dark scheme.** The
  two "withdrawn" fixtures were readings: the flip reproduced in every run with the same-sitting
  light capture as control.
- **The 2x reference is unstable across runs where the 1x is not**: 70 of 104 cells multi-state
  at 2x against 3 at 1x, one cell with no majority at all.
- **A material change can remove a calibration cell with no stop to catch it.** At (0.70, 0.15)
  the collapsed dark capsule loses its contour and two cells drop out of the bed.
- **Two dry runs appended into one matrix read as one bed twice.** The gate failed on duplication.
- **The field and W24's exponent double-count the lit corners.** Two terms on one diagonal, fitted
  apart; the near-null bins improve and the corners overshoot until they are fitted together.
- **The level term's sign depends on which backdrops are counted.** One backdrop grades cleanly;
  across backdrops the residual is not one thing.
- **The along-side field is a saddle, not a ramp.** The product of the normalised coordinates has
  the antisymmetry G0 measured; a ramp along the diagonal does not.
- **The above-knee level residual is not the reference's grading — it is vitrea's own span curve
  continuing where the reference's stops.** G0 read the reference's WIDTH flat above span 96 while
  vitrea's `kDeep` keeps rising to `sizeScatterSpanMax` 256, so the two gradings largely cancel and
  what is left is backdrop-INDEPENDENT (+2.2…+4.2 codes at span 160 over eight backdrops of the W9
  grid spanning 0.012 to 0.89 linear). The term chartered on the tone response's thin-to-thick blend
  explains 0.3 % of it; an offset on the response's settled level explains 39 % on the grid that
  identifies it (G2 `fit-level.txt`).
- **The heavy width is not a lever on `sizeScatterGainMax` at 1x.** Raising it 8 → 10.3 beside the
  fitted share left reader A's heavy reading unchanged at 13.29 device px against the reference's
  19.52, and the width objective moved by 0.0001 (G2 rung `rG`). The heavy tap is a mip-chain level
  and its effective width saturates there.
- **One row on the canonical bed identifies the 1x heavy share**, `impulse__rrect-md`, and it is a
  validation row.

## Outcomes & Retrospective

(at recomposition)

## Revision Notes

- 2026-09-09: chartered; G0 dispatched; the amendment and the console named as the user's.
- 2026-09-09: Decision Log 2 — the user's word "both on your recommendation": the grids as a
  harness set (ii), the console unlocked at G1's sitting on the parent's ask; the console read locked.
- 2026-09-09: G0 CLOSED (claims §5.113); Decision Log 3 — clauses 1, 2 and 4 re-declared (the
  triple, the share, the level above the knee), the along-side field taken, two grid fixtures
  withdrawn, the amendment sharpened to the grids whole at both scales with coarse structure as a
  `probe` set; G1 and G2 dispatched.
- 2026-09-09: G2 CLOSED (`g2/g2-findings.md`). The three mechanisms are in the code at their
  defaults and draw nothing; the fits are on scratch and the profile documents carry no fitted
  value, only the fingerprint the three new keys moved. Two items are the parent's to rule and are
  named in the findings' §9: (i) the level term's shape — Decision Log 3 (b) put it on the tone
  response's thin-to-thick blend and the rows above the knee refuse that shape, so G2 re-formed it
  as an offset on the response's settled level and fitted 0.029 on the light grid with the dark
  grid pinning 0; (ii) the share law's landing, where clause 2 (share within 0.05, needing a lift
  ≥ 0.39) and clause 6 (calibration ΔE not worse by 0.0001, capping the lift at ≈ 0.31) have an
  empty window, G2 recommending 0.455 and the ΔE recorded as a claim. The golden re-run after the
  level term's re-form is deferred to G3 by the parent's capture hold during G1's sitting.
- 2026-09-09: G1 DECLARED (merged `0f30529`) and the sitting started at 06:33Z after the rebuild
  and the user's re-grant; G2 CLOSED by the parent (claims §5.114; merged `17b7af1` inert);
  Decision Log 4 — every constant to G3 on the probe set, the two re-formed shapes accepted.
- 2026-09-09: G1 CAPTURED (claims §5.115; `b60706b`); Decision Log 5 — one cell omitted by ruling,
  the two withdrawn cells reinstated, clause 5 answered (span; the level's floor), the level term
  scheme-signed; G3 dispatched.
- 2026-09-09: G3 READ; Decision Log 6 — four constants declined on their checks, the field's
  corner confound with W24's exponent diagnosed, a joint re-fit ruled (G3b), the heavy width
  chartered as the next wave's.
- 2026-09-10: G3b read; Decision Log 7 — the pair (0.85, 0.10) lands, the gain small and real; G4
  dispatched; the heavy width chartered as W26 at recomposition.

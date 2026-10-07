# W49a — the opaque receded body repaired with the receded far delta: no shipped glass draws opaque, and a landing that cannot trade new cells for old (2026-10-07)

**Status: G0 READ — the gate reads NEITHER; STOPPED for the parent (2026-10-07).** Decision Log RULED by the parent (DL1–DL8, verbatim below). W49
splits (DL1): **W49a**, this charter, repairs the opaque receded dark `-glass0.25` body with one existing
leaf pair and ships as patch 0.28.1; **W49b**, the pitch-selective thick body, is chartered after W49a
lands and nothing of it is declared here. Branch `w49-g0-grounding`; evidence
`packages/calibration/results/2026-10-07-w49-grounding/` (the grounding) and
`packages/calibration/results/2026-10-07-w49a-g0-declaration/` (G0). Ledger §5.215 (G0), §5.216 (G1),
§5.217 (G2).

## Decisions

| DL | question | ruled |
| --- | --- | --- |
| 1 | scope | W49 splits: W49a repairs the opaque receded body with family R alone (receded `tintAlphaFar1x/2x`, signed domain [-0.3, 0.2]), patch 0.28.1; W49b chartered after W49a lands |
| 2 | the landing rule | binding, hashed in part 2 before any gate read: (a) the three repair cells against `d0219cd684bf`, (b) the three opacity-flattered cells against `d0219cd684bf`, (c) every other cell against `b2d074d2df24`, zero away beyond B, (d) W48's halvings hold |
| 3 | invariants | X75 (no opaque glass, ≤ 0.95, both tiers, both scales, spans 0..1024; a runtime test and a seal/builder refusal), X74 (authority report), X76 (no silent receded inheritance) adopted |
| 4 | the selection | hashed in part 2 before the gate; NO post-gate amendment; no point passing DL2 closes W49a at the finding |
| 5 | re-authorisation | none |
| 6 | referees | the dark 0.25 holdout and W46 referees are spent; read once as read 9, a prediction check |
| 7 | release | `@vitreajs/vitrea-web` patch 0.28.1 naming the defect |
| 8 | renders | not before the census passes (Zoom quit with the user's permission at G0; the census then passed) |

## Purpose

**What the wave is for.** 0.28.0 ships a product defect. The dark `-glass0.25` material draws an
unfocused window's glass as an opaque slab wherever a surface's shorter side is 160 CSS px or more,
on both tiers and both scales: the receded document `29da6a888a23` names `tintAlpha` 0.8 and carries
the active's far deltas 0.2 / 0.2 at span tops 160 / 160 (W48 materialised them by inheritance), so
operator 1's `alphaBase = clamp(tintAlpha + far · farS(span), 0, 1)` is 1.0 there and the backdrop's
transmission is zero. Apple's unfocused glass is transmissive at every span the bed carries (native
T1 0.073 on `checkerboard-64__rrect-lg__inactive`). Three of W48's seventeen authorised regressions
are this defect (grounding F1). W49a repairs it with the one leaf pair that caused it, the receded far
delta, and makes the class of defect impossible to ship again (X75, X76).

**What a good outcome is.** An unfocused dark 0.25 window draws transmissive glass at every size; the
three repair cells leave `T1_DARK_AUTHORISED_REGRESSIONS`; no other cell is bought away from Apple to pay
for it; W48's halvings stand; and the runtime refuses, by test and in the tools, any document that
would draw opaque glass again. If the existing leaf cannot do all of that, the wave says so at its
gate and the parent asks the user (DL4), rather than trading or re-authorising (DL5).

**What the wave does not do.** No active-document change, no light change, no 0.5 change (X60, X41). No
change to T1's statistic, bar or arithmetic. No new operator, leaf or shader line (family R is an
existing leaf; neither tier validates its sign). The other eleven authorised entries, the pitch-selective
thick body, operator 1's own span top and a blind thick-span native referee are W49b's.

## Grounding (main at `a58573d2f`, W48 closed)

All numbers are T1 (`interiorStdDev`, linear light, over the native silhouette), WebGPU tier, from W48's
exposure cut `cut-025-w48-dl9-exposure`, W46's gate cut of point A and the archived W48 fit summaries
(`2026-10-07-w49-grounding/attribution.txt` §1–§5).

### F1 — the receded body is opaque at span 160 (W49a's question)

- **The mechanism.** `farS = smoothstep(sizeSpanMax, sizeScatterSpanMax(dpr), span)` is 1 at `rrect-lg`
  (span 160), 0.5 at `rrect-ml` (128), about 0.55 at the glass-over-glass base (130) and 0 at or below
  96. At the receded `tintAlpha` 0.8 and far 0.2 the receded `alphaBase` is 1.0 on `rrect-lg`, 0.9 on
  `rrect-ml`, 0.8 at and below `rrect-md`.
- **Authority.** Over all 191 stage-2 fit summaries W48 archived, every `rrect-lg` inactive cell reads ONE
  value at each scale: no stage-2 leaf reached it (the reason X74 exists).
- **The same scatter without the opacity.** W46's point A (receded `tintAlpha` 0.8, no far delta) read
  `checkerboard-64__rrect-lg__inactive` 0.0480 / 0.0686 against native 0.0733 / 0.0742, toward Apple by
  6.45 / 10.27 B against `d0219cd684bf`.
- **By eye** (`authorised-sheet.png`): `b2d074d2df24` draws the thick inactive cells perfectly flat where
  Apple and `d0219cd684bf` keep the blurred checker and the photo's hues. The CSS tier mirrors it
  (`spanGradedTintAlpha`): its `checkerboard-64__rrect-lg__inactive` reads 0.0000 / 0.0001.
- **The opacity flattered three cells.** At the opaque floor `hc-text__rrect-lg__inactive` and
  `impulse__rrect-lg__inactive` read nearer Apple than any transmissive body draws them, and
  `checkerboard-8__rrect-lg__inactive` is one of the F inactive cells W48's 1x halving counts. DL2 (b)
  reads those three against `d0219cd684bf` for that reason.
- **Eight of W48's nine stage-1 operator-1 pairs drew the active `rrect-lg` rest body opaque**
  (`tintAlpha + far ≥ 1`); only the landed pair (0.7, 0.2) did not. X75 now refuses such a point before
  it is built.

### F2–F5 — W49b's material, recorded here and not declared

The other eleven authorised entries are not the opacity. F2: the three thick rest cells pay for the
span top shared by operator 1 and the scatter (W48 moved it 256 → 160). F3: `checkerboard-lc16__rrect-
md__rest` and `impulse__capsule-button__rest` pay for operator 1's opening at spans 96 and 44. F4: the
two 2x capsule inactive cells are W46 point A's receded thin start. F5: Apple's thick body is
pitch-selective (64 px structure passes at span 160 about as at 96, text and impulses weakly), which a
transmission alone cannot draw. The grounding's per-cell attribution table and the families it
proposed (A, D, W, O) are W49b's starting point (Deferred).

## Design

### Family R (DL1)

The receded dark document's `tintAlphaFar1x` / `tintAlphaFar2x` as its own fit members, no longer the
active's 0.2 materialised. Signed domain **[-0.3, 0.2]**. Neither tier validates the sign: the shader
line (`src/wgsl/optics.ts`, `alphaBase = clamp(tint.w + far · farS, 0, 1)`) and both tiers'
`spanGradedTintAlpha` clamp into [0, 1] and nothing else reads the leaf; `tier-coherence.test.ts`
already holds the two tiers equal on a synthetic far −1 (the clamp), so a negative delta needs no runtime
change, only the builder's domain (W47's X68 said [0, 0.6]). The active document does not move. The two
anchors are scale-separable: at dpr exactly 1 a cell reads only `tintAlphaFar1x`, at 2 only
`tintAlphaFar2x`.

The receded far delta reaches every receded surface whose span exceeds 96 CSS px: `rrect-lg` at full
weight, `rrect-ml` and glass-over-glass's base at about half. It cannot reach a cell at or below 96.

### The probes (part 1; the ladder)

- **P1** — `d0219cd684bf` with only the active span tops `sizeScatterSpanMax` / `…2x` at 160 (the receded
  inherits them), the 45 dark rest gate cells per scale. A prediction check of F2 by render, for W49b's
  record: the three thick rest cells within B of 0.0228 / 0.0297 / 0.0270 (1x) and 0.0283 / 0.0347 /
  0.0287 (2x). It selects nothing in W49a.
- **P2** — `b2d074d2df24` with the receded far delta at {-0.1, 0, 0.05, 0.09, 0.1, 0.15}, both anchors at
  the value, the 21 dark inactive gate cells per scale. These six points per scale are the rendered
  points DL4 selects among. A rest cell reads `b2d074d2df24` by construction (the receded document is not
  drawn in the rest pose).
- Both in candidate mode, WebGPU, into scratch, built by W49a's builder (`fit/build-candidate.ts`) into the
  evidence root's `probes/candidates/` and rendered and read by `probes/probe.py`. No referee or holdout
  cell is rendered. A tooling smoke before part 1 drew the published `d0219cd684bf` on one rest cell and
  read its published value exactly (`probes/smoke/smoke.json`).
- **The first-order predictions** (`probes/predict.py`, from `b2d074d2df24` and W46's point A on a line
  in `alphaBase`): `checkerboard-64__rrect-lg__inactive` within B of `d0219cd684bf` only for far ≈ 0.05–0.09;
  the lg text and impulse cells within B of `d0219cd684bf` from about 0.05 (1x) and 0.09 (2x) up; and
  **`impulse__rrect-ml__inactive` away from `b2d074d2df24` beyond B at every far that repairs the lg cell**
  (+2.1 / +1.7 B at 0.09), because the smoothstep moves span 128 by half of span 160's change. So the
  prediction is that **no P2 point meets DL2 at either scale** (Risks).

### The invariants (DL3)

- **X75 — no opaque glass.** No shipped endpoint resolves `alphaBase` above 0.95 at any integer span
  0..1024 CSS px, dpr 1 and 2, both variants, both tiers, nominal policy (Reduce Transparency and forced
  colours raise the body by design). One statement, `packages/calibration/scripts/no-opaque-glass.ts`;
  read by `packages/calibration/test/x75-no-opaque-glass.test.ts` over `SHIPPED_MATERIAL_PROFILE_DOCUMENTS`
  (it fails 0.28.0's dark 0.25 receded endpoint from span 140 on both tiers and scales; that case runs as
  an expected failure naming W49a, removed at G2), and refused by W49a's builder and seal. A float
  allowance of 1e-9 admits the bound itself (0.8 + 0.15 is 0.9500000000000001 in f64).
- **X74 — the authority report.** Over a probe's points, a cell that reads one distinct value is outside
  the family's reach and is named, with its reason where the arithmetic predicts it (farS = 0 at span ≤
  96); the selection's objective excludes it by declaration. Those cells are also the reproduction
  control: each must read its `b2d074d2df24` value within 0.1 bar, or the probe set is VOID.
- **X76 — no silent receded inheritance.** A receded leaf inherited from the active is fitted or held
  explicitly in the document's method record, never materialised silently. W49a's seal refuses a leaf
  stated at its active's value, or an active-fitted leaf the receded does not name, unless the method
  record holds it with a reading. The audit of every receded document is `x76/audit.txt`: the dark 0.25
  receded document materialises thirteen leaves silently (the two far deltas among them), the light
  0.25 receded inherits four active fits unrecorded, and the 0.5 documents predate the form.

### The landing rule (MARKED: DL2, hashed in part 2) and the selection (MARKED: DL4)

Per dark 0.25 profile, WebGPU tier, T1 by W44 G1's `classify` (`B = max(code, 2·bar)`, growth `|k − n| −
|c − n|`; T cells read away on T1-low):

- (a) **repair:** `checkerboard-64__rrect-lg__inactive` against `d0219cd684bf`, growth ≤ B; its withheld
  siblings `checkerboard-32__rrect-lg__inactive` (referee) and `photo__rrect-lg__inactive` (holdout) are read
  once at read 9 on the selected point. Their six entries leave `T1_DARK_AUTHORISED_REGRESSIONS`.
- (b) **flattered:** `hc-text__`, `impulse__` and `checkerboard-8__rrect-lg__inactive` against
  `d0219cd684bf`, growth ≤ B.
- (c) **no new trade:** every other cell against `b2d074d2df24`: zero cells away beyond B (so none past 3 B).
- (d) **W48's halvings hold:** C rest at both scales, F inactive at 1x, against `d0219cd684bf` as W48 read
  them, over every partition. At the gate a withheld cell R cannot move enters at its read-8 value, which
  it reads by construction; read 9 re-reads it.

**The selection** (`probes/rule.py`, hashed in part 2): per scale, among P2's points meeting DL2, the
minimum of the median |log((k + ε)/(n + ε))| over X74's reachable gate cells (ε the cell's code); points
within τ (the median log(1 + bar/(n + ε)) over the same cells) are tied; among tied points the largest far
(the smallest departure from the shipped bytes). The landing is (far1x, far2x). A scale with no passing
point: NEITHER, W49a closes at the finding and the parent asks the user. Part 2 admits no amendment after
any probe render.

### The reads

1. **The gate** (G0's renders, under part 2): P2's 21 inactive gate cells per scale, rest cells by
   construction, the selection. STOP for the parent.
2. **Read 9** (G1, once, on the selected and sealed point only, in strict mode): every DL2 clause over all
   partitions, the two withheld repair cells binding; the other withheld cells (the glass-over-glass
   inactive pair, which R reaches, and the cells it cannot) recorded as a prediction check against part
   1's numbers (DL6). A clause failing there means the point does not meet DL2: W49a closes at the
   finding and the parent asks the user; no other point is read.
3. **Every other adopted row** (the owner test's M2, L1, E2 and T1 blocks) at G2: a failure stops for the
   parent.

### The CSS tier

Family R is mirrored per surface (`spanGradedTintAlpha`; X65): the CSS tier's thick inactive cells are
opaque today and draw the repaired alpha with the document. X75 holds on both tiers.

## Children

### G0: the declaration, the invariants, the probes (ledger §5.215)

- (a) **X75** as a runtime test and in the builder and seal; its failing output on 0.28.0 recorded.
- (b) **X76**: the audit as evidence, and the method-record rule in the seal.
- (c) **The builder** re-bound to W49a (two bases, `b2d074` and `d0219`; family R's signed domain; X75), and
  the seal (the receded document only; X75; X76), each with tests.
- (d) **The two-part declaration** hashed (`declare.py`): part 1 the probes, their predictions, X74–X76 and
  the tools; part 2 DL2 and DL4 verbatim with the rule's arithmetic pinned, and no post-gate amendment.
- (e) **The renders** after both hashes and a passing census: P1 and P2 into scratch, read, and the report
  (X74, DL2 per point, DL4). STOP for the parent.

### G1: the seal, the strict-mode stage, read 9, the publication (ledger §5.216)

On the parent's go and a landing selection: the seal of the receded dark document (X75, X76 holds), the
strict-mode stage of the dark pair, read 9 (once) and STOP; publication superseding `b2d074d2df24`.

### G2: the landing (ledger §5.217)

T1's dark row re-baselined in the five-part order (X59) with the six repair entries removed from
`T1_DARK_AUTHORISED_REGRESSIONS` (the eleven others stay, W49b's), `MISSED_27_ROWS` re-derived,
`T1_DARK_REFERENCE` moved last; X75's `KNOWN_DEFECT` entry removed; the generated 0.25 module, the c9d
chain, the sheets; CLAUDE.md's W48 paragraph corrected (its deferral named the wrong cause); the changeset
`@vitreajs/vitrea-web` patch 0.28.1 naming the defect (DL7).

## Referees and the holdout (DL6)

The canonical dark 0.25 holdout and W46's referees were read once at `b2d074d2df24`'s bytes (read 8), and
the grounding read their exposure values and images, so they are not blind for W49a. They are withheld
from every probe and gate read and read once, at read 9, against part 1's numeric predictions. A blind
thick-span native referee needs the user's lift of X5 and is W49b's question.

## Cross-Child Contracts

**Carried from W44–W48:** X1, X3, X24, X33, X41, X44 (as narrowed), X45, X49–X55, X57–X73 as W48 bound
them, with X52's reference per DL2 (`b2d074d2df24` for (c), `d0219cd684bf` for (a), (b), (d)); X62's
snapshots taken at this charter (`documents/`, six files); the census, no attribution, path-scoped adds,
freeze 1,818 and X41 911 at every merge.

**Adopted (DL3):** X74, X75, X76 as Design states them.

## Risks & Mitigations

- **The predicted obstruction: `rrect-ml` moves with `rrect-lg`.** First order, every far that repairs
  `checkerboard-64__rrect-lg__inactive` (≈ 0.05–0.09) moves `impulse__rrect-ml__inactive` away from
  `b2d074d2df24` beyond B (+2.9 / +2.1 B at 1x, +2.3 / +1.7 B at 2x), and 0.15, which holds the ml cell,
  leaves the lg cell 5–7 B away. The withheld `checkerboard__glass-over-glass__inactive` is predicted
  +2.5 B at 0.09 on the same coupling. If the renders confirm it, no P2 point meets DL2 and W49a closes at
  the finding (DL4). *Mitigation:* the prediction is in part 1 before any render; the parent decides
  whether to amend part 1 before the renders (one pre-render amendment per part is admitted; none after).
  Routes the parent could consider, none declared here: the receded `tintAlpha` beside the far delta
  (0.89 with far ≈ 0 puts lg and ml near `d0219cd684bf`'s 0.89, at a cost to the thin inactive cells W48
  improved at 0.8), or operator 1's own span top (D), which is W49b's.
- **The census.** Zoom was quit with the user's permission at G0 and the census passed; a capture process
  refuses a launch, which `probe.py` records and does not retry.

## Deferred / Out of Scope

- **W49b** (DL1), chartered after W49a lands: the pitch-selective thick body through
  `sizeHeavySecondShareFar1x` (W), operator 1's own span top (D), the active's thick end (A), operator 2
  re-read (O), the other eleven authorised entries (F2–F5), and a blind thick-span native referee (X5,
  the user's).
- The dark photo body (P), S1 dark, the dark 0.5 pair (X41), the light scheme (X60), the CSS tier's fine
  pitch, accessibility at 0.25.
- The two review findings on W49a's pinned tools (G0 outcome): any later copy of `rule.py` reads clause (c)
  growth-only, and any later seal applies X76 to every named receded leaf, not only the extension keys.
- X76's reach beyond W49a's seal: the light 0.25 receded document's four unrecorded active fits and the
  pre-form 0.5 documents (`x76/audit.txt`) are recorded, not re-sealed; a future seal of either meets the
  rule.

## Tracking Map

| child | status | ledger |
| --- | --- | --- |
| grounding | DONE on `w49-g0-grounding` `4559dc41b` | (§5.215) |
| G0 | declared (part 1 `a7403d3e…`, part 2 `bffb524b…`), P1 and P2 rendered and read: NEITHER at both scales | §5.215 |
| G1 | not started | §5.216 |
| G2 | not started | §5.217 |

## Decision Log

The parent's rulings on the grounding (2026-10-07), over branch `w49-g0-grounding` `4559dc41b`, verbatim.
The parent verified: the shipped dark 0.25 receded document names `tintAlpha` 0.8 with
`tintAlphaFar1x/2x` 0.2 and span tops 160/160, so alphaBase = 1.0 at span >= 160; the grounding sheet
shows b2d074 drawing checkerboard-64/-32 rrect-lg inactive flat at both scales.

### DL1

DL1 (scope). W49 splits. **W49a** repairs the opaque receded body with the existing leaf alone
(family R: receded tintAlphaFar1x/2x, signed domain [-0.3, 0.2]) and ships as patch 0.28.1.
**W49b** (pitch-selective body via sizeHeavySecondShareFar1x; operator 1's own span top D) is
chartered after W49a lands; nothing of it is declared in W49a.

### DL2

DL2 (W49a landing rule, binding, hashed in part 2 before any gate read):
(a) repair: checkerboard-64__rrect-lg__inactive, checkerboard-32__rrect-lg__inactive and
photo__rrect-lg__inactive, both dark 0.25 profiles, WebGPU, each read against d0219cd684bf:
growth <= B (i.e. no longer away beyond B). Their six entries leave T1_DARK_AUTHORISED_REGRESSIONS.
(b) the three opacity-flattered cells (hc-text, impulse, checkerboard-8 __rrect-lg__inactive)
are read against d0219cd684bf, not b2d074, under the same growth <= B.
(c) every other cell: zero new cells away beyond B against b2d074d2df24, none past 3 B.
(d) W48's halvings that held (C rest both scales, F inactive 1x, against d0219) still hold.
The other eleven authorised entries are W49b's and stay listed; W49a neither repairs nor
re-authorises them.

### DL3

DL3 (no opaque glass, X75, adopted). No shipped document may resolve alphaBase above 0.95 at any
span 0..1024 CSS px at dpr 1 and 2, on either tier: a runtime test over every shipped endpoint and
a refusal in the seal/builder. It must fail on the shipped 0.28.0 dark receded document.
X74 (authority check: a stage reports cells it cannot move, and a selection excludes them by
declaration) and X76 (a receded leaf inherited from the active is fitted or explicitly held in
the document's method record, never silently materialised) adopted.

### DL4

DL4 (selection). The selection rule over rendered points is hashed in part 2 before the gate;
part 2 admits NO post-gate amendment. If no point passes DL2, W49a closes at the finding and
the parent asks the user.

### DL5

DL5. No ruling re-authorises a cell already on the list.

### DL6

DL6 (referees). The dark 0.25 holdout and W46 referees are spent and not blind for W49; they are
read once as read 9, recorded as a prediction check, not a blind referee. A blind thick-span
native referee is W49b's question (needs the user's X5 lift).

### DL7

DL7 (release). W49a's landing ships as @vitreajs/vitrea-web patch 0.28.1 (changeset patch),
naming the defect: dark 0.25 unfocused glass drew no backdrop structure at short side >= 160 CSS px.

### DL8

DL8 (renders). The classifying census currently refuses on Zoom's caphost (user's app; never kill
it). The parent asks the user; until then do every non-render step.

*Later the same day (the parent, in the G0 worker's session):* Zoom has been quit with the user's
permission (no zoom or caphost process remains, verified by the parent); re-run the classifying census
at the render step and, if it passes, render P1 and P2 as declared.

## G0 outcome (the gate, read under the hashed part 2)

`probes/report.txt`, from the cuts in `probes/readings/` (P1 and P2, both scales, 66 + 21 cells per
scale, every launch census-passed, `census.jsonl`, `runs.jsonl`).

- **X74.** At each scale family R reaches exactly the seven predicted cells (the four `rrect-lg` and three
  `rrect-ml` inactive gate cells); the other fourteen read one value across the six points, all predicted
  (farS = 0), and every one reproduces its `b2d074d2df24` value (the control holds).
- **DL2, per point** (growth in B; (b) and the repair against `d0219cd684bf`, (c) against `b2d074d2df24`):

  | far | 1x | 2x |
  | --- | --- | --- |
  | −0.10 | (b) hc-text +5.52, impulse lg +11.66; (c) impulse ml +7.35, checkerboard ml +2.53 | (b) +5.94, +8.89; (c) +7.36, +2.76 |
  | 0 | (b) +1.99, +5.90; (c) +4.90, +1.58 | (b) +2.34, +5.01; (c) +4.93, +1.70 |
  | 0.05 | (b) impulse lg +3.07; (c) +3.75, +1.13 | (b) +3.01; (c) +3.48, +1.22 |
  | 0.09 | (c) impulse ml +2.76 | (b) impulse lg +1.47; (c) impulse ml +2.79 |
  | 0.10 | (c) impulse ml +2.37 | (b) +1.09; (c) +2.63 |
  | 0.15 | (a) checkerboard-64 lg +4.92; (c) impulse ml +1.41 | (a) +7.00; (c) +1.49 |

  The repair cell reads within B of `d0219cd684bf` at every far ≤ 0.10 (at 0.09: −0.61 / −0.17 B); what
  no point clears is `impulse__rrect-ml__inactive` against `b2d074d2df24`, at every far, as part 1
  predicted, and at 2x the lg impulse cell too. **No point meets DL2 at either scale: NEITHER (DL4). W49a
  closes at the finding and the parent asks the user.**
- **P1** reads the three thick rest cells exactly at the predicted values at both scales (F2 confirmed by
  render, for W49b).
- **The review** (`doperpowers:reviewer-medium`, after the hash, before the renders finished) found two
  real defects in pinned tools, neither changing this verdict: (1) `rule.py` counts only cells labelled
  `away` in clause (c), so a crossing (`overshoot`) regression with growth beyond B would escape it, where
  W46's partition is growth-only; read beside the hashed rule (`probes/review-corrected-c.txt`) it adds no
  failure to any point, and a stricter (c) can only remove passing points. (2) `seal.ts` applies X76 only
  to the X64/X67 extension keys, so a 0.5-twin leaf stated at its active's value with no record (e.g.
  `backdropToneAnchorX`, `backdropToneBlackStrength`) seals silently. Both are pinned in the hashed parts,
  and the renders had begun, so neither is amended (DL4); any later wave's copies carry the fixes.

## Surprises & Discoveries

- **W48's deferral named the wrong cause** (F1): the thick inactive cells are opaque, not under-scattered,
  and W48's stage 2 could not have seen it because no stage-2 leaf reached them.
- **X75 reaches 0.95 at span 140**, not 160: the smoothstep is 0.77 there, so the defect starts below the
  bed's largest span.
- **X76's audit found thirteen silent leaves** on the dark 0.25 receded document, the two far deltas
  among them, and four unrecorded active fits on the light 0.25 receded document.
- **The reference's captures moved.** W48's cut tools default to the canonical capture tree, which now
  holds `b2d074d2df24`'s captures; a read against `d0219cd684bf` passes its superseded tree
  (`web-captures-superseded/d0219cd684bf/`) explicitly.
- **A candidate-mode render reproduces a published row exactly** (the tooling smoke: 0.0337913274553524 on
  both), which is why X74's control can be tight.
- **The predicted coupling at `rrect-ml` is confirmed by render:** the receded far delta cannot repair
  the `rrect-lg` cell without moving `impulse__rrect-ml__inactive` beyond B from `b2d074d2df24` (G0 outcome).

## Revision Notes

- 2026-10-07 (v0): drafted by the grounding worker from main `a58573d2f`; Decision Log open.
- 2026-10-07 (v1, G0): rewritten for W49a under the parent's rulings DL1–DL8 (folded verbatim); W49b named
  as the follow-on; family R, the probes, X74–X76, DL2 and DL4 as Design; the first-order predictions and
  the `rrect-ml` risk recorded before any render.
- 2026-10-07 (v2, G0 read): both parts hashed (`a7403d3e…`, `bffb524b…`) at `034da9318`; the census passed
  after Zoom was quit; P1 and P2 rendered and read; the gate reads NEITHER at both scales; the review's two
  findings recorded and read beside the hashed rule. STOPPED for the parent (DL4).

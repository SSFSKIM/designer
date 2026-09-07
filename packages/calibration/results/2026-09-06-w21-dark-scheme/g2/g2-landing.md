# W21 G2 — the landing and its referee (2026-09-07)

The dark profile G1 froze, landed on the canonical bed from the main checkout, and refereed against
the dry run it must reproduce and against the W20 bed it must not disturb. Every number below cites
the file beside it.

**The headline, in two halves.** The render landed exactly as declared: all 52 dark captures come
back with G1's digests byte for byte, so the wave's one holdout read (contract X6) stands, and the
canonical bed now carries GPU dark calibration ΔE 0.0041 at both scales against 0.0085, and a
holdout of 0.0161 / 0.0160 against 0.0300 / 0.0302. **And the gate is RED.** Thirteen adopted rows
on the dark pair miss — three fidelity rows and ten on the cross-tier coherence axis — every one of
them the CSS tier's structured-backdrop residual that W21 Decision Log 3 (a) recorded as a residual
without weighing that the gate asks a second question about it. Nothing was widened and no floor was
pinned. `g2-gate.txt` is the enumeration; §4 below is the shape of the ruling it needs.

---

## 1. The rebuild

`g2-rebuild.sh` from the main checkout at `4c8f397`, the dark document at file digest `ebfb0858…`
and `resolvedMaterialSha256` `d86f480c0e136627` — G1's frozen configuration, checked by the script
before it starts. `results/matrix.json` removed first, because the dark profile's hash is part of a
cell's key and the old rows would otherwise sit beside the new; the whole bed rebuilt, both tiers,
six profiles, with `--alpha`, into the canonical matrix and the canonical `web-captures/`. The
previous matrix and captures were copied to scratch first and are the referee's "before".

Twenty-four runs, 16:56:52–17:04:02, the calibration and validation column before the holdout
column (`g2-runs.txt`). Twenty-three exit 0 and one exit 1 — the increased-contrast CSS holdout
run, on `hc-text__capsule-button__rest`, the cell the harness refuses to measure a conformance
reading for because that tier's interior alpha over a transparent page is 0.2667 against the 0.9 an
alpha coverage rule needs; the same refusal as at W19 and W20 (claims §5.79 §1, §5.86 §1). 0 scenes
fell back to the CSS tier and 0 carried problems across all 24 runs. **229 cells**, the W20 bed's
keys, no row lost and none new.

## 2. The referee (`g2-verify.py`, `g2-verify.txt`)

**(i) Contract X6 — the dark captures reproduce G1's digests.** **52 / 52 byte-identical** to
`g1-digests.txt`, on both tiers at both scales, holdout included. The holdout was read once, at the
dry run, and this is the proof that the landing re-rendered it rather than re-read it.

**(ii) Contract X3's inverse — the light profiles byte-identical.** **176 of 177**. The four light
profiles' captures on both tiers come back bit for bit as the W20 bed left them, with one exception,
named rather than absorbed: `photo__toolbar-group__rest__css.png` under
`apple-macos-26.5-1x-light-increased-contrast` differs in **17 of 64 000 pixels by one code**, on
the antialiased edge of the third capsule, and its row moves in the seventh decimal (ΔE mean
0.01523996 → 0.01523987, the largest movement `ssimMin` by 0.00035). Re-captured to scratch
immediately afterwards it reproduces the LANDED bytes, not the W20 bed's, so this is a
session-to-session byte-state of that cell on this machine and not a coin flip inside a run — the
capture's own determinism check ("byte-identical over two loads") passed on both. It is not a
material change: the light document is untouched, all 144 light-standard captures and both other
light profiles are identical, and the cell is a CSS-tier capture that no dark constant reaches.

**(iii) The rows.** The dark rows against G1's dry-run matrix: **52 rows, 0 readings moved**. The
164 readings that differ are the four declaration-conformance metrics (`declaredIoUWeb`,
`declaredContourMaxWeb`, `declaredContourP95Web`, `drawnAreaWeb`) on the 41 dark cells with a shape
axis, absent on the dry-run side because G1's run did not pass `--alpha`; a difference in what was
measured, not in what was rendered, and (i) covers the rendering. The light rows against the W20
bed: 177 rows, **8 readings moved, all eight on the one cell of (ii)**.

**(iv) Contract X2 — the declared-geometry read.** `g2-read-canonical.sh` re-read the two dark
profiles on both tiers from the LANDED captures against the canonical fixtures, and
`g1-clauses.py` over `canonical-reads/` printed `g2-clauses.txt`. `diff g1/g1-clauses.txt
g2/g2-clauses.txt` is **empty**: clause 3's bodies, stop S3's collapsed capsules and clause 4's
per-side rims reproduce G1's reading line for line. The thick rows land at 0.0039 mean and 0.0079
worst against the 0.010 clause, the collapsed capsules move 0.0000, and the two structured capsules
carry the deferred appearance term at 0.0386 and 0.0433.

**(v) The bed's shape.** 229 cells, and the partition `adopted-thresholds.test.ts` asserts holds per
profile: 72 / 72 / 26 / 26 / 17 / 16.

## 3. What landed, per cell

GPU tier, OKLab ΔE mean, W20 bed → canonical (`g2-verify.txt`'s last table):

| profile | calibration | validation | holdout |
| --- | --- | --- | --- |
| 1x dark | 0.00846 → **0.00410** (9) | 0.00291 → 0.00291 (1) | 0.02996 → **0.01612** (3) |
| 2x dark | 0.00860 → **0.00410** (9) | 0.00329 → 0.00329 (1) | 0.03017 → **0.01596** (3) |

Below the charter's clause 5 (0.006) by 0.0019 at both scales. Per cell at 1x: `dark-solid__rrect-md`
0.02861 → **0.00401** (p95 0.116 → 0.013, ssim 0.931 → 0.988), `photo__rrect-md` 0.01972 → 0.01313,
`checkerboard__rrect-md` 0.01110 → 0.00395, `photo__capsule-button` 0.00774 → 0.00753,
`checkerboard__capsule-button` 0.00558 → 0.00503; the collapsed and tinted cells unchanged to
0.00004. The holdout's three cells, each improving: `photo__rrect-lg` 0.05720 → **0.03047** (the
bed's worst dark row, halved), `checkerboard__glass-over-glass` 0.02736 → **0.01765**,
`mid-dark-solid__capsule-button` 0.00532 → **0.00025** (p95 0.00000). Every figure equals the dry
run's, which is what (iii) says formally.

CSS tier, the same table: 1x calibration 0.01147 → 0.01163 and holdout 0.03623 → **0.04340**; 2x
0.01166 → 0.01129 and 0.03676 → **0.04183**. The split is the one G1 declared — right over a solid
(`dark-solid__rrect-md` 0.03065 → 0.00455), too dark over a structured backdrop.

## 4. The gate (`g2-gate.txt`)

`pnpm --filter @vitrea/calibration test`: **271 passed, 6 failed**, all six in
`adopted-thresholds.test.ts` (33 cases: 27 passed, 6 failed). `MATRIX_CELLS` and `MATRIX_PARTITION`
unchanged and asserted green. No bound was widened and no floor was pinned.

**The predicate moved, and the list is updated** (29 → 34 lines, with a doc comment in the file's
voice). Decision Log 3 (d) expected it unchanged because "the native silhouettes do not move" —
they do not, every native reading is identical — but the predicate has read both sides since §5.15's
final form, and the WEB side moved with the material. Four dom rows (`checkerboard__rrect-md` and
`checkerboard__glass-over-glass`, both scales) lose about half their region to the extractor because
the CSS tier's body over a checkerboard lands at 0.0122 against a reference of 0.0468; one texture
row (`checkerboard__rrect-md` at 2x) loses 7.5% for the opposite reason — the GPU body moved
0.0628 → 0.0475 against a reference of 0.0475, so coherence with the reference cost the instrument
what the renderer gained, which is W17's and W18's mechanism in a new place.

**Three adopted fidelity bounds miss**, all on the dark bed's nested pane
`checkerboard__glass-over-glass__rest`, a holdout cell and the partial the charter predicted: dom
`ssimMean` 0.80048 against ≥ 0.83 at 1x and 0.83543 against ≥ 0.85 at 2x (the CSS residual), and
texture `silhouetteIoU` 0.92673 against ≥ 0.93 at 2x (the extractor again — the GPU tier's own ΔE on
that cell improved 0.0274 → 0.0177).

**Ten coherence rows miss.** Eight `interiorLevelRatioGpuOverCss` readings against a 0.8…1.25 gate —
`checkerboard__capsule-button` 2.07 and 2.00, `photo__rrect-md` 1.50 and 1.52, `photo__rrect-lg`
1.49 and 1.50, `photo__capsule-button` 1.28 and 1.28 — and two `crossTierOklabDeltaEMean` readings
against ≤ 0.05, the nested pane at 0.0624 and 0.0578. Worth reading beside them: on the W20 bed
`checkerboard__capsule-button` sat at 1.24602 against the 1.25 bound, so that axis was already
carrying the two tiers' disagreement over a checkerboard as far as it would go. Four more dark dom
cells would miss it worse (ratios 3.90, 3.33, 2.47, 2.28) and are skipped by the predicate instead.

One mechanism under all of it: the CSS tier resolves the response law from one backdrop level for
the whole surface. Decision Log 3 (a) recorded that as the CSS-only residual of wave Decision Log 23
(a) and deferred the diagnosis by name, because a CSS derivation change moves the light captures
this wave binds byte-identical. What that ruling did not weigh is that the gate has adopted
cross-tier coherence bounds, so a residual recorded on one axis is an exceedance on another — the
W16 lesson in a new place, since the dry run's referee measured the material and never ran this file
over the candidate matrix. The three constructs a ruling can reach are the bounds (a widening the
doctrine forbids), a regression floor pinned at the measurement with a §5.27 row saying what stopped
being claimed (a user decision), and the CSS derivation itself (a wave). None is the landing
worker's, so none was taken.

**The dark bounds re-proposed** (`g2-dark-bounds.txt`, `g2-dark-bounds.py`), by claims §5.15's margin
rule on the landed bed, **as a proposal and nothing more** (Decision Log 3 (d)). The proposal cuts
both ways and that is the interesting part. On the texture tier seven of eight rows tighten, several
sharply — 1x `oklabDeltaEMean` ≤ 0.09 → **≤ 0.05**, `oklabDeltaEP95` ≤ 0.17 → **≤ 0.14**,
`ssimOutside` ≥ 0.83 → **≥ 0.92**, `ssimMean` ≥ 0.87 → **≥ 0.93**, and the 2x table the same shape.
On the dom tier four rows would have to LOOSEN (`ssimMean` ≥ 0.83 → 0.78, `oklabDeltaEMean` ≤ 0.09 →
0.10, `oklabDeltaEP95` ≤ 0.18 → 0.23 at 1x, and the 2x twins), which the founding rule forbids: the
rule may not be used to authorise a widening.

## 5. The demo

`apps/demo/src/site/calibration.ts` imports `results/matrix.json` at build time, so the demo's
figures follow the rebuild with no edit. Its e2e fixture
`apps/demo/e2e/fixtures/checkerboard__capsule-button__rest__webgpu.png` is **byte-identical** to the
new canonical capture (`755f6fab…`, a light-standard cell, unmoved under X3), and its `.cell.json`
matches the capture's `cell__webgpu.json` field for field. Nothing to re-copy.

## 6. By eye (contract X5)

`../sheets/g2-1x.png` and `g2-2x.png`, thirteen rows each — every dark cell the profile declares
except the `recorded` pressed capsule, which has no capture — four panels wide: Apple's own
fixture, the GPU tier on the W20 bed, the GPU tier landed, the CSS tier landed, whole canvas at
zoom 2 (1x) and 1 (2x), each row captioned with the cell and its GPU ΔE before → after.

What the eye reads, and it agrees with the numbers on both halves. On `dark-solid__rrect-md` the
before panel is a pale slab with a bright top-left rim and the landed panel all but disappears into
the black as Apple's does. On `checkerboard__rrect-md`, `photo__rrect-md` and `photo__rrect-lg` the
before panel hides the backdrop behind a flat grey and the landed panel lets the board and the
photograph through at about the reference's strength. On the two structured capsules the landed
panel passes more than before and is still flatter and darker than Apple's — the appearance term,
visible. And the CSS column is visibly too dark over every structured backdrop, worst on the nested
pane, which is the residual of §4 with a face on it. The tinted rows are indistinguishable across
all four columns.

## 7. The chain (`g2-chain.txt`)

Run on the landed tree, one at a time, each after the GPU was free, 17:11:00–17:13:47. Build clean;
lint clean; **1 848 unit tests passed and 6 failed**, the six being §4's gate cases and the only red
step in the chain (policy 23, motion 162, geometry 170, renderer-webgpu 396, core 302, platform-web
423, react 101, calibration 271 + 6 failed). The renderer's golden suite **29 passed,
byte-identical** — the dark patch is not the default material and no golden hash moved, which is the
check that this wave reached the profile and not the renderer's own constants. platform-web
Playwright **376 passed** on four projects; react **105 passed, 3 skipped** on three engines; demo
**39 passed**, including the reference-panel GPU spec against the fixture of §5.

## 8. The release

`.changeset/dark-scheme-measured.md` — `@vitreajs/vitrea-web` minor, beside G3's
`quiet-scheme-arrives.md` (web + react minor), both for the 0.10.0 cut. It says what a dark-mode
user sees, gives the calibration and holdout numbers in one sentence, and says in one sentence that
on the CSS tier the dark material is right over solid backgrounds and still too dark over busy ones
(Decision Log 3 (a)). Not versioned; `changeset version` is the parent's step.

## 9. One paragraph the parent can lift into claims

W21 G2 rebuilt the canonical bed once from the main checkout at the dark document G1 froze, and the
render reproduced that gate exactly: all 52 dark captures return `g1-digests.txt`'s SHA-256 byte for
byte, so the wave's single holdout read stands, and the declared-geometry read off the landed
captures reproduces `g1-clauses.txt` line for line. The bed carries 229 cells on the W20 bed's keys,
with the GPU tier's dark calibration ΔE mean at 0.00410 at both scales against 0.00846 / 0.00860 and
the holdout at 0.01612 / 0.01596 against 0.02996 / 0.03017, all three holdout cells improving and
`photo__rrect-lg` halving to 0.03047; the tinted and collapsed cells are unmoved to 0.00004. Of 177
light captures 176 are byte-identical to the W20 bed and the one exception is bounded and named —
the increased-contrast CSS toolbar group differs in 17 of 64 000 pixels by one code, reproduces the
landed bytes on an immediate re-capture, and moves its row in the seventh decimal. The gate,
however, is red for the first time at a landing: `PREDICATE_EXCLUDES` gains five checkerboard rows
in the dark pair (four dom, one texture) and is updated from the artifact with its reasons, and
thirteen adopted rows miss — the nested pane's dom `ssimMean` at both scales and its 2x texture
`silhouetteIoU`, eight `interiorLevelRatioGpuOverCss` readings between 1.28 and 2.07 against a
0.8…1.25 gate, and the nested pane's `crossTierOklabDeltaEMean` at 0.0624 and 0.0578 against ≤ 0.05.
Every one of them is the CSS tier's structured-backdrop residual that W21 Decision Log 3 (a)
recorded rather than chartered, reaching an axis that ruling did not weigh: the gate asks whether
the two tiers agree with each other, and over a structured dark backdrop they no longer do. Nothing
was widened and no floor was pinned, because a widening is forbidden and a floor is a user decision;
the margin rule re-proposed on the landed bed would tighten seven of eight texture rows (1x ΔE mean
≤ 0.09 → ≤ 0.05, `ssimOutside` ≥ 0.83 → ≥ 0.92) and would have to loosen four dom rows, which is
the shape of the decision rather than its answer.

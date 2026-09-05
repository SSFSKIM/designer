# W19 G1 — the pre-check at the gate (Decision Log 2's re-declared stops)

The fold is implemented where G0 placed it, pinned by seven unit assertions, one cross-package
coherence assertion and one Chromium pixel assertion, and re-captured on G0's own twenty-scene
ladder bed. **The defect is gone and nothing else moved.** On the standard light profile the
tinted ladder's worst `CSS − GPU` interior mean falls from **−0.0684 to +0.0039** across both
scales, both seeds, both backgrounds and all six strengths — every one of the thirty-six tinted
cells inside S4's 0.005, against sixteen of them outside it before. The cross-tier OKLab ΔE, the
quantity the interior mean under-reports and which G0's Deferred asked for, falls on **every**
sub-unit tinted cell, by 0.0030 to 0.0323, and does not rise on any cell anywhere. Every GPU
capture is byte-identical to G0's; every untinted CSS capture is byte-identical; every
full-strength tinted capture differs on 21 to 42 pixels of the component region, none of them
more than two device pixels from its contour, with the interior mean moving at most 0.00013.
Every cell still drew the `linear` form. The transfer table's clamp share is unchanged and the
floor now holds at 0.340 where it used to be 0.100.

**Two stops fire, and neither is the fold's arithmetic.** The fold profiles' movement clause
(Decision Log 2 (5)) misses on **increased contrast** at strengths 0.5 and 1.0 — and at 1.0 the
number is unchanged by this whole change (−0.0332 before, −0.0333 after), so the clause is
measuring a preference-fold gap that exists with or without W19. And S5's control misses on three
of the thirty-six cells, all at dpr 2, by 0.0001 to 0.0027 beyond the bound; the pattern says the
decoration constant the clause subtracts is itself a function of L3's alpha, which the clause
assumes it is not. Both are laid out with their numbers in §6 and §5 and are the parent's to rule
on.

## 0. What changed

| file | what |
| --- | --- |
| `packages/platform-web/src/optics.ts` | `foldedOverlay` split out of `tintedCssOptics` — the encoded-space fold of one `{color, strength}` layer over one `{tint, tintAlpha}` overlay, in one place. `tintedCssOptics` calls it with the whole converted material, exactly as before. |
| `packages/platform-web/src/css-tier.ts` | `CssTierSurface.untintedOptics`, optional. In the `tintForm === "linear"` branch only: the transfer's `floorEncoded` comes from it, and L3's overlay is `foldedOverlay({tint: untintedOptics.tint, tintAlpha: floorAlpha}, authorLayer)`. Absent, every declaration is what this function wrote before. |
| `packages/platform-web/src/root.ts` | `cssOpticsFromSource(...)` computed once as `nodeUntintedOptics`, passed to `cssTierDeclarations` beside the folded `nodeBaseOptics`. `nodeBaseOptics` and `nodeOptics` — the renderer's input — are untouched. |
| `packages/platform-web/test/author-tint-fold.test.ts` | the seven pins. |
| `packages/platform-web/test/w19-fold-cases.ts` | `root.ts`'s chain and the 190-case bed the pins and the recorded declarations share. |
| `packages/platform-web/test/w19-pre-fold-declarations.json` | the 190 declarations as the tier wrote them **before** the change, recorded off the stashed tree. |
| `packages/calibration/test/tier-coherence.test.ts` | X7's tinted clause (48 cells: four backdrops × two seeds × six strengths). |
| `packages/platform-web/e2e/pixel/css-tier-pixels.spec.ts` | the contrast floor at strength 0.1, in Chromium. |
| `.changeset/css-author-tint-fold.md` | `@vitreajs/vitrea-web` minor, beside W18's `css-shadow-carriers.md`. |

Three consequences of the placement are worth naming because they are what makes the "nothing else
moves" clauses true by construction rather than by measurement. The `encoded` branch never reads
`untintedOptics`. An engine without `referenceFilterInBackdrop` never reaches the branch at all,
because `transfer` is `undefined` there. And a caller that passes no `untintedOptics` takes the
same path it took before, which is why the recorded 190 declarations replay exactly.

A fourth is a small cost saving rather than a gap: a tinted surface's `floorEncoded` is now the
untinted surface's, so `referenceFilterId` gives a tinted and an untinted surface at the same σ and
the same backdrop the same `id`, and a tinted group stops needing a `<filter>` of its own (G0 §7).

## 1. The pins (`pnpm --filter @vitreajs/vitrea-web test`, 410 tests over 31 files green)

The bed is the canonical 120 × 44 capsule at the canonical radius, resolved through `root.ts`'s
fourteen-step chain in the shipped order, over five uniform backdrops (0.15, 0.30, 0.45, 0.60,
0.80), at the charter's six strengths, on both seeds — 190 cases across the `linear` form, the
`encoded` form, a plain-`blur()` engine and the untinted controls.

| pin | claim | result |
| --- | --- | --- |
| (i) | the identity in real arithmetic: `(1 − α″)·F(b) + α″·C″ = (1 − s)·E(M) + s·E(L)`, composing the table the declarations name and the overlay they write | worst **8.885e−8** over 60 cells × 3 channels — G0's 8.9e−8 reproduced from the shipped declarations |
| (i) | the same identity with `C″` and `α″` as the declaration writes them (eight bits, a thousandth) | worst **1.490e−3**, under the 2.85e−3 quantum §5.80 §3 names |
| (i) | the table's argument `(E(M) − α₃·E(T))/(1 − α₃)` inside [0, 1] on every cell and channel | range **[0.742, 0.966]** — never within 0.03 of either end |
| (ii) | `α″ ≥ α₃` on every tinted declaration | holds; least margin **+0.07318** at `s = 0.1` (the written 0.340 against 0.2668229) |
| (iii) | at `s = 1` the L3 declaration byte-identical to the pre-change one | holds on all 10 full-strength cells |
| (iv) | the `encoded` form's and a plain-`blur()` engine's whole declarations byte-identical before and after, tinted and untinted, WITH the new field passed | holds on all 130 |
| (v) | a caller passing no `untintedOptics` gets the recorded declarations | holds on all 190 |

X7 (`packages/calibration/test/tier-coherence.test.ts`, 42 tests green): the tier's tinted
composite against `(1 − s)·E(M) + s·E(L_css)` with `E(M)` the **renderer's** own composite for that
span and backdrop, at four backdrop levels × two seeds × six strengths × three channels — worst
**0.00158**, under both the 0.004 bound and the chain's 2.85e−3 quantum. Stated against the tier's
`L` per Decision Log 2 (7); the renderer's per-pixel shade sits above it by the term §3 measures.

The e2e (`npx playwright test e2e/pixel/css-tier-pixels.spec.ts --project=chromium`, 11 tests
green, run alone on the adapter): a panel tinted `rgba(255, 149, 0, 0.1)`, L3's **computed**
`background-color` read out of a real Chromium at alpha **0.34**, and the surface still reading as
a surface against the bare page underneath it, by more than the assertion's floor of eight
codes, with both filter layers' `backdrop-filter` forced to `none`.

## 2. The capture runs

G0's `run-ladder.sh` and `make-scenes.mjs` unchanged. `make-scenes.mjs` regenerated the bed from
`apps/reference-apple/scenes.json` and the result is **byte-identical to G0's**
`w19-ladder.json`, so the two runs are over one bed. Eight `capture-web` runs, one at a time on
the shared adapter (`pgrep` and `lsof -i :5189` clear before the first), GPU tier first, 2026-09-05
00:32:12Z–00:34:16Z, every run exit 0, 20/20 and 4/4 scenes each, **every scene byte-identical over
two page loads**, no fallback to the CSS tier, no problems reported. Nothing canonical written:
the bed through `VITREA_SCENES`, the captures under `/Users/new/.claude/jobs/5c70e47f/tmp/w19/g1/`.

**No GPU capture was reused.** All four GPU trees were re-captured and then compared to G0's file
for file: **0 of 48 PNGs differ**. X3 holds through the change by capture rather than by argument.

**X4, re-run on this run's captures** (`x4-recovery.ts`, `photo__…-tint-orange-010` at 1x): a
nominal +0.030 offset recovers as **+0.030343** under the declared component region and under the
declared surface, and the reader's answer matches the offset actually achieved on disk to
**3.0e−15**. No masked pixel clamped at white. The reader is sound before any number below is used.

## 3. S4 — CSS − GPU, declared component region, standard light

`CSS − GPU` interior mean in linear luminance; `granularity` is W10's per-pixel-versus-per-source
tint shade measured on that cell (§3a). Full table in `parts/ladder-{1,2}x.json`.

### dpr 1

| cell | s | before | after | granularity |
| --- | --- | --- | --- | --- |
| photo, untinted | — | +0.0011 | +0.0011 | — |
| photo, orange | 0.10 | **−0.0684** | **+0.0004** | −0.0000 |
| photo, orange | 0.20 | **−0.0408** | −0.0019 | −0.0000 |
| photo, orange | 0.35 | −0.0121 | +0.0010 | −0.0001 |
| photo, orange | 0.50 | −0.0008 | −0.0007 | −0.0001 |
| photo, orange | 0.75 | +0.0027 | +0.0011 | −0.0002 |
| photo, orange | 1.00 | −0.0001 | −0.0002 | −0.0003 |
| photo, blue | 0.20 | **−0.0220** | −0.0009 | +0.0003 |
| photo, blue | 0.50 | **+0.0146** | −0.0010 | +0.0004 |
| photo, blue | 1.00 | −0.0014 | −0.0015 | +0.0004 |
| checkerboard, untinted | — | +0.0006 | +0.0006 | — |
| checkerboard, orange | 0.10 | **−0.0325** | +0.0017 | +0.0005 |
| checkerboard, orange | 0.20 | **−0.0117** | −0.0003 | +0.0009 |
| checkerboard, orange | 0.35 | +0.0008 | −0.0000 | +0.0013 |
| checkerboard, orange | 0.50 | +0.0020 | −0.0026 | +0.0016 |
| checkerboard, orange | 0.75 | −0.0008 | −0.0023 | +0.0017 |
| checkerboard, orange | 1.00 | −0.0016 | −0.0017 | +0.0013 |
| checkerboard, blue | 0.20 | +0.0050 | −0.0023 | +0.0005 |
| checkerboard, blue | 0.50 | **+0.0164** | −0.0010 | +0.0009 |
| checkerboard, blue | 1.00 | −0.0017 | −0.0017 | +0.0006 |

### dpr 2

| cell | s | before | after | granularity |
| --- | --- | --- | --- | --- |
| photo, untinted | — | +0.0018 | +0.0018 | — |
| photo, orange | 0.10 | **−0.0673** | +0.0010 | −0.0000 |
| photo, orange | 0.20 | **−0.0397** | −0.0015 | −0.0000 |
| photo, orange | 0.35 | −0.0116 | +0.0013 | −0.0001 |
| photo, orange | 0.50 | −0.0004 | −0.0005 | −0.0001 |
| photo, orange | 0.75 | +0.0029 | +0.0013 | −0.0002 |
| photo, orange | 1.00 | −0.0001 | −0.0001 | −0.0003 |
| photo, blue | 0.20 | **−0.0212** | −0.0006 | +0.0003 |
| photo, blue | 0.50 | **+0.0148** | −0.0009 | +0.0005 |
| photo, blue | 1.00 | −0.0016 | −0.0017 | +0.0004 |
| checkerboard, untinted | — | +0.0101 | +0.0101 | — |
| checkerboard, orange | 0.10 | **−0.0294** | +0.0036 | +0.0007 |
| checkerboard, orange | 0.20 | **−0.0130** | +0.0029 | +0.0012 |
| checkerboard, orange | 0.35 | −0.0026 | +0.0007 | +0.0019 |
| checkerboard, orange | 0.50 | −0.0006 | +0.0028 | +0.0024 |
| checkerboard, orange | 0.75 | −0.0032 | −0.0034 | +0.0028 |
| checkerboard, orange | 1.00 | −0.0031 | −0.0031 | +0.0027 |
| checkerboard, blue | 0.20 | +0.0003 | +0.0039 | +0.0008 |
| checkerboard, blue | 0.50 | **+0.0120** | −0.0005 | +0.0014 |
| checkerboard, blue | 1.00 | −0.0026 | −0.0026 | +0.0014 |

**Verdict: S4 met on every tinted ladder cell at both scales.** Worst |CSS − GPU| across the
thirty-six tinted cells is **0.0039** (`checkerboard`, blue, `s` 0.20, dpr 2). Sixteen cells were
outside 0.005 before and none is now. **No checkerboard cell misses 0.005**, so Decision Log 2
(7)'s conditional re-declaration is not needed and the granularity term is reported for the record
only.

The two untinted controls are byte-identical to G0's captures and therefore unchanged: `photo`
+0.0011 / +0.0018 and `checkerboard` +0.0006 / **+0.0101**. The 2x checkerboard control is outside
0.005 and was before this wave — it is W18 §2a's structure-dependent remainder on the 120 × 44
capsule over the checkerboard at dpr 2, already carried as a measured bound per box and scale
(claims §5.79). It is named here because it is on the ladder bed, not because this change moved it.

Every cell of both scales and both fold profiles drew `cssTint: "linear"` — **48 of 48 readings, no
flip**, which is the reading the charter's Design bullet asked for rather than an assertion.

### 3a. The granularity term, for the record

W10's known granularity, measured per cell on the GPU tier's own untinted capture: the renderer's
per-pixel tint shade against the tier's one colour per source. It runs **−0.0003 to +0.0028**,
largest on the checkerboard at dpr 2 and rising with strength, which is the direction and the
order of magnitude G0's analytic sweep found (0.0000 to +0.0084 over a wider backdrop range,
claims §5.80 §8). Nothing in this wave creates or removes it, and no clause needed it.

## 4. The hue — cross-tier OKLab ΔE, the gap G0's Deferred named

Mean OKLab distance between the CSS and GPU captures of the same cell, under the declared region.

| cell | dpr 1 before → after | dpr 2 before → after |
| --- | --- | --- |
| photo, untinted | 0.02480 → 0.02480 | 0.02659 → 0.02659 |
| photo, orange 0.10 | **0.05481 → 0.02255** (−0.03226) | **0.05615 → 0.02424** (−0.03191) |
| photo, orange 0.20 | 0.04985 → 0.02089 (−0.02896) | 0.05167 → 0.02237 (−0.02930) |
| photo, orange 0.35 | 0.04528 → 0.01754 (−0.02774) | 0.04659 → 0.01885 (−0.02774) |
| photo, orange 0.50 | 0.03539 → 0.01413 (−0.02126) | 0.03661 → 0.01513 (−0.02148) |
| photo, orange 0.75 | 0.02082 → 0.00979 (−0.01103) | 0.02159 → 0.01043 (−0.01116) |
| photo, orange 1.00 | 0.00718 → 0.00718 (−0.00000) | 0.00768 → 0.00767 (−0.00000) |
| photo, blue 0.20 | 0.04377 → 0.02045 (−0.02332) | 0.04537 → 0.02210 (−0.02327) |
| photo, blue 0.50 | 0.04171 → 0.01354 (−0.02817) | 0.04326 → 0.01497 (−0.02829) |
| photo, blue 1.00 | 0.00694 → 0.00691 (−0.00002) | 0.00765 → 0.00763 (−0.00002) |
| checkerboard, untinted | 0.02654 → 0.02654 | 0.03131 → 0.03131 |
| checkerboard, orange 0.10 | 0.04416 → 0.02557 (−0.01859) | 0.04555 → 0.02803 (−0.01752) |
| checkerboard, orange 0.20 | 0.04167 → 0.02442 (−0.01724) | 0.04165 → 0.02632 (−0.01532) |
| checkerboard, orange 0.35 | 0.03939 → 0.02299 (−0.01640) | 0.03834 → 0.02426 (−0.01408) |
| checkerboard, orange 0.50 | 0.03395 → 0.02134 (−0.01261) | 0.03292 → 0.02263 (−0.01028) |
| checkerboard, orange 0.75 | 0.02343 → 0.01925 (−0.00418) | 0.02330 → 0.02029 (−0.00301) |
| checkerboard, orange 1.00 | 0.01892 → 0.01892 (−0.00001) | 0.01985 → 0.01985 (−0.00000) |
| checkerboard, blue 0.20 | 0.04228 → 0.02392 (−0.01836) | 0.04182 → 0.02632 (−0.01550) |
| checkerboard, blue 0.50 | 0.04052 → 0.02023 (−0.02029) | 0.03762 → 0.02147 (−0.01615) |
| checkerboard, blue 1.00 | 0.01693 → 0.01691 (−0.00001) | 0.01796 → 0.01796 (−0.00000) |

**Down on every sub-unit tinted cell and up on none, anywhere.** The largest fall is on the photo
at strength 0.1, which is where the clamp share and the level error were largest. At full strength
and untinted the reading is unchanged to five places, which is the same statement §5's `s = 1` rows
and §7's byte comparison make in a third measure. The residue after the fold — 0.010 to 0.028 on
the sub-unit cells, against 0.007 to 0.020 on the full-strength ones — is the level-agnostic part
the two tiers already carried untinted.

**S6's spirit is met** (the cross-tier ΔE down or flat on every profile), though S6 as the charter
states it is a matrix clause and belongs to the dry run.

## 5. S5 — measured against `predFold + c`

`predFold` is `predict.ts`'s per-pixel prediction of the tinted capture from the tier's own
untinted capture through the FOLD's expression; `c` is that cell's own decoration constant, read
at `s = 1` on the same backdrop and scale as `measured − predFold` there (G0 §4). The four
constants are +0.00377, +0.00416, +0.00379, +0.00425 at dpr 1 and +0.00392, +0.00421, +0.00390,
+0.00429 at dpr 2 — the rim, border, highlight, shadow and antialiased contour that no flat-colour
prediction carries, tight across cells as G0 found.

| cell | dpr 1 miss | clamp fold | dpr 2 miss | clamp fold |
| --- | --- | --- | --- | --- |
| photo, orange 0.10 | −0.00384 | 0.0000 % | −0.00398 | 0.0000 % |
| photo, orange 0.20 | −0.00499 | 0.0000 % | **−0.00511** | 0.0000 % |
| photo, orange 0.35 | −0.00100 | 0.0000 % | −0.00109 | 0.0000 % |
| photo, orange 0.50 | −0.00311 | 0.0000 % | −0.00327 | 0.0000 % |
| photo, orange 0.75 | +0.00020 | 0.0000 % | +0.00017 | 0.0000 % |
| photo, orange 1.00 | +0.00000 | 0.0000 % | +0.00000 | 0.0000 % |
| photo, blue 0.20 | −0.00350 | 0.0000 % | −0.00357 | 0.0000 % |
| photo, blue 0.50 | −0.00211 | 0.0000 % | −0.00219 | 0.0000 % |
| photo, blue 1.00 | +0.00000 | 0.0000 % | +0.00000 | 0.0000 % |
| checkerboard, orange 0.10 | −0.00102 | 0.0000 % | **−0.00768** | 0.0582 % |
| checkerboard, orange 0.20 | −0.00217 | 0.0000 % | **−0.00549** | 0.0582 % |
| checkerboard, orange 0.35 | −0.00078 | 0.0000 % | −0.00454 | 0.0582 % |
| checkerboard, orange 0.50 | −0.00341 | 0.0000 % | −0.00065 | 0.0582 % |
| checkerboard, orange 0.75 | −0.00150 | 0.0000 % | −0.00309 | 0.0582 % |
| checkerboard, orange 1.00 | +0.00000 | 0.0000 % | +0.00000 | 0.0582 % |
| checkerboard, blue 0.20 | −0.00480 | 0.0000 % | −0.00450 | 0.0582 % |
| checkerboard, blue 0.50 | −0.00216 | 0.0000 % | −0.00403 | 0.0582 % |
| checkerboard, blue 1.00 | +0.00000 | 0.0000 % | +0.00000 | 0.0582 % |

**The clamp share is exactly G0's** — 0.0000 % everywhere except the 2x checkerboard's
0.0582 %, which is the number G0's `parts/predict-2x.json` already carries and reported at three
places as 0.000. Both runs compute it from the same byte-identical untinted CSS captures and the
same resolved `T`, so the agreement is a check on the reader rather than a new reading. Under
today's table the same cells clamp on **0.14 % to 14.99 %** of masked channel samples, rising with
strength, and the fold removes all of it.

**Verdict: S5 met on 18 of 18 cells at dpr 1 (worst −0.00499) and on 15 of 18 at dpr 2.** The
three misses are `photo`/orange at 0.20 (−0.00511, over by 0.00011) and `checkerboard`/orange at
0.10 (−0.00768) and 0.20 (−0.00549).

**What the pattern says, and it is about the control rather than the tier.** Every miss is
negative, every miss is at low strength, and the miss is exactly zero at `s = 1` **by
construction**, because that is where `c` is read. The fold changes L3's alpha as well as its
colour — from `s` to `α″`, which is 0.34 where `s` is 0.10 — and L3 also carries the inset rim and
the press-glow gradient, so the decoration those contribute is composited at a different alpha at
every rung. A constant read at `α″ = 1` cannot represent that, and the residual it leaves is
largest exactly where `α″` is furthest from 1. The clause therefore misses because the control it
subtracts is `α″`-dependent, which S5 as re-declared assumes it is not. The same three cells meet
S4 against the GPU tier at +0.0029, +0.0036 and −0.0015, and the fidelity claim is S4's.

## 6. The fold profiles, 1x over the photo (Decision Log 2 (5))

Movement is `(CSS − GPU)_tinted − (CSS − GPU)_untinted`; the untinted control is byte-identical
before and after on both profiles.

| profile | cell | CSS − GPU before → after | movement before → after | inside 0.01 |
| --- | --- | --- | --- | --- |
| increased contrast (control +0.0364) | orange 0.20 | −0.0126 → +0.0274 | −0.0490 → **−0.0090** | yes (was no) |
| | orange 0.50 | +0.0186 → +0.0146 | −0.0178 → **−0.0218** | **no** |
| | orange 1.00 | +0.0032 → +0.0031 | −0.0332 → **−0.0333** | **no**, and it was not before |
| reduced transparency (control −0.0070) | orange 0.20 | −0.0000 → −0.0033 | +0.0070 → +0.0037 | yes |
| | orange 0.50 | +0.0137 → −0.0030 | +0.0207 → **+0.0041** | yes (was no) |
| | orange 1.00 | +0.0002 → +0.0002 | +0.0072 → +0.0072 | yes |

**Reduced transparency: met on all three rungs, and the 0.5 rung came inside the clause from
outside it** (+0.0207 → +0.0041).

**Increased contrast: the stop fires at 0.5 and at 1.0.** The 1.0 row is the decisive one for
reading it. At full strength the fold degenerates to the opaque layer the tier already drew — the
declaration is byte-identical, §1 pin (iii) — and the movement is −0.0332 before and −0.0333
after. So the increased-contrast profile has a **−0.033 tinted movement that this wave neither
created nor can touch**, and a clause bounding movement at 0.01 is unmeetable there for reasons
that predate W19. What the fold did do is make the strength curve monotone in `s`: before it ran
−0.049, −0.018, −0.033 with no order in it, and it now runs −0.009, −0.022, −0.033, walking from
the untinted material's own increased-contrast gap toward the full-strength tint's. The 0.5 row's
own share of the change is **−0.0040**; the other −0.0178 was already there.

For the parent: this looks like a second, separate item — the increased-contrast fold's tint gap
at full strength — of the same shape as W18 §5.79 §7's untinted +0.0364 and belonging beside it,
rather than a reason to hold this fold. It is stated as an observation, not a ruling.

## 7. S3 by capture (Decision Log 2 (4))

`moved.ts` compares each CSS capture against G0's pre-fold one and classifies every differing
pixel against the declared component region eroded by two device pixels.

**Every untinted CSS capture is byte-identical**, both scales: `photo__capsule-button__rest` and
`checkerboard__capsule-button__rest`. The change touches only surfaces with an author layer, by
capture and not by argument.

**Every full-strength tinted capture is within the clause.** Four cells, both scales:

| cell | dpr | differing px (whole image) | in region | in the eroded interior | worst code | interior mean move |
| --- | --- | --- | --- | --- | --- | --- |
| photo, orange 1.00 | 1 | 116 | 21 | **0** | 35 | −0.00010 |
| photo, blue 1.00 | 1 | 116 | 21 | **0** | 34 | −0.00013 |
| checkerboard, orange 1.00 | 1 | 112 | 21 | **0** | 25 | −0.00005 |
| checkerboard, blue 1.00 | 1 | 112 | 21 | **0** | 25 | −0.00007 |
| photo, orange 1.00 | 2 | 240 | 42 | **0** | 37 | −0.00005 |
| photo, blue 1.00 | 2 | 240 | 42 | **0** | 38 | −0.00006 |
| checkerboard, orange 1.00 | 2 | 218 | 40 | **0** | 27 | −0.00002 |
| checkerboard, blue 1.00 | 2 | 224 | 40 | **0** | 27 | −0.00003 |

Not byte-identical, and the reason is the one claims §5.80 §7 predicted: the transfer's floor
colour moves from the folded colour to the untinted one, so the table's output changes even where
an opaque layer covers it — and it reaches the screen only at the mask's antialiased contour and in
the few pixels just outside the region that the surface's own filters touch. **Not one differing
pixel lies more than two device pixels inside the region**, the worst channel difference is 38 of
255 and lives on the contour, and the interior mean moves by at most 0.00013 against the clause's
0.0005. The remaining 74 to 200 differing pixels per cell are outside the region entirely, on the
same contour band.

The sub-unit tinted cells move as they are supposed to: 4324 (dpr 1) and 18368 (dpr 2) interior
pixels differ on every one, the interior mean by −0.0174 to +0.0688, which is the defect being
removed and is what §3 reads as a level.

## 8. The floor (Decision Log 2 (6), q2 (a))

`α₃` = 0.2668229. The alpha L3 paints, per strength, from `foldedOverlay` and confirmed against
the declarations by pin (ii) and against a real Chromium's computed style by the e2e:

| s | painted before | painted after (written) | margin over the floor | under the floor before? |
| --- | --- | --- | --- | --- |
| 0.10 | 0.100 | 0.34014 (0.340) | +0.07318 | **yes** |
| 0.20 | 0.200 | 0.41346 (0.413) | +0.14618 | **yes** |
| 0.35 | 0.350 | 0.52343 (0.523) | +0.25618 | no |
| 0.50 | 0.500 | 0.63341 (0.633) | +0.36618 | no |
| 0.75 | 0.750 | 0.81671 (0.817) | +0.55018 | no |
| 1.00 | 1.000 | 1.00000 (1.000) | +0.73318 | no |

Two of the six strengths — twelve of the thirty-six captured tinted cells — painted under the
doctrine's floor before and none does now. The least margin is +0.07318 rather than G0's +0.0733
because `rgba()` writes the alpha to a thousandth; the difference is the declaration's own quantum.

## 9. S8 — the cost

From the diff, and it is short. No layer is created or destroyed: `css-tier-layers.ts` is not
touched and the tier still writes L1, L2 and L3. No filter primitive is added: the `<filter>` still
carries one `feGaussianBlur` and one `feComponentTransfer`, whose table is the same length as
before — only the constant it is solved against moved. L3 still carries one `background-color`, one
`background-image` and one `box-shadow` list. The only arithmetic added on the paint path is
`foldedOverlay`, three multiply-adds and three roundings per tinted surface per frame.

W16 G0's knee harness was **not** run, per the dispatch's condition: it is run only if a layer or a
filter primitive changed, and neither did. The knee stands where W18 left it.

## 10. What contradicts Decision Log 2, and `[parent-impact]`

1. **[parent-impact] The fold profiles' clause is unmeetable at `s = 1` under increased contrast.**
   Decision Log 2 (5) bounds `(CSS − GPU)_tinted − (CSS − GPU)_untinted` at 0.01 on each fold
   profile at the ladder's strengths. On increased contrast that movement is −0.0333 at `s = 1`
   after the change and −0.0332 before it, on a declaration this wave proves byte-identical. The
   clause is measuring the increased-contrast fold's own tint gap, not the fold. Recommended: the
   parent re-declare the clause at the strengths where the fold can move the number (0.2 met at
   −0.0090; 0.5 misses at −0.0218, of which −0.0040 is this change) and carry the full-strength
   −0.033 as a named increased-contrast gap beside W18 §5.79 §7's untinted +0.0364.
2. **[parent-impact] S5's decoration constant is a function of L3's alpha.** Read at `s = 1` it is
   +0.0038 to +0.0043 and forces the miss to zero there by construction, while the sub-unit rungs
   carry a residual up to −0.0077 whose sign and shape follow `1 − α″`. Fifteen of eighteen cells
   at dpr 2 and eighteen of eighteen at dpr 1 still meet 0.005. Recommended: keep the clause and
   record the three misses with this attribution, or re-declare it at 0.008 at dpr 2 with the
   reason; S4 against the GPU tier is the fidelity claim and it passes at 0.0039.
3. **[parent-impact] The clamp share under the fold is 0.0582 %, not 0.000, on the 2x
   checkerboard.** It is exactly the number in G0's own `parts/predict-2x.json`, reported there at
   three places as 0.000; both runs read it off byte-identical untinted captures. Nothing moved —
   the claims text should carry the fourth place so the stop is checkable as written.
4. **[parent-impact] The 2x checkerboard untinted control is +0.0101, outside 0.005.** Byte-identical
   to G0's, W18's known structure-dependent remainder on this box and scale (claims §5.79). Named
   because S4 says "every ladder cell" and the bed's untinted controls are cells; the tinted rungs
   over the same backdrop all sit inside 0.005.
5. **[parent-impact] A cost saving worth recording as a claim, not a gap.** A tinted surface's
   transfer is now the untinted surface's, so `referenceFilterId` collapses the two into one
   `<filter>` definition per group per σ where a tinted group used to need its own (G0 §7 predicted
   it; it follows from `floorEncoded` and is not separately measured here).
6. **[parent-impact] G0's Deferred item "the clamp's cost as a colour" is closed by §4** — the
   cross-tier OKLab ΔE on the ladder, before and after, at both scales. It falls on every sub-unit
   tinted cell and rises on none.
7. **Not read, by instruction:** the whole canonical bed, the holdout (X8), the sheets (X5), the
   knee (S8's harness), S1/S2/S6/S7 as matrix clauses. All belong to the dry run.

## 11. Suites

`pnpm -r build && pnpm -r lint && pnpm -r test` — green, 26 package tasks, no errors:
platform-web 410 tests over 31 files, calibration 265 over 18, react 97 over 12, core and the
private packages as before. `npx playwright test e2e/pixel/css-tier-pixels.spec.ts
--project=chromium` — 11 passed.

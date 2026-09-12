# W27c G2's checking-bed read — the verdict (2026-09-13)

Claims §5.139. The frozen inactive endpoint of §5.130 read once against the 26.5 checking bed of
§5.134 §5, captured in the sitting of §5.136 §10, under the bound §5.134 §6 declared on 2026-09-11
before the bed existed. Nothing is fitted, no profile, golden, `scenes.json` entry, canonical matrix
row or pre-existing fixture entry moves, and no floor is adopted.

**The bound holds on 2 of 6 profiles. G2 stays blocked.**

## 1. What was published, and what did not move

`materialize` ran once per pass of the sitting with `--set probe --frequency-settle`, which is how
§5.134 §5 and §5.136 §6 declared these rows enter: the whole bed is `probe` in `scenes.json`'s
split, so the seven bed ids that already carry a `calibration` or `holdout` role are skipped before
their bytes are read and the frozen bed's own cells are untouched.

| | |
| --- | --- |
| cells published | 156 (62 inactive at 1x, 62 at 2x, 12 per accessibility profile, 4 active per scale) |
| entries before → after | 455 → 611 |
| pre-existing entries lost / changed | **0 / 0** (`round-trip.json`, diffed against `ec809ae6`) |
| pre-existing fixture PNGs changed | **0** |
| `manifest-doctor` | 455 entries before, 611 after; the same four undeclared fields it named before (`recoveredProvenance` ×121, the three frequency fields ×102 → ×103) |
| bed provenance blocks | 5 → 11, all five prior blocks kept |

Two defects in `cli/materialize.ts` were found by doing this and fixed before the bundle was
written. Both are recorded in §5.139 §1.

## 2. The seven-run plurality

188 cells over six passes, each of seven runs; every run's manifest sha256 matches the sitting's
committed `provenance.json`.

| pass | cells | 7/7 | 6/7 | 5/7 | 4/7 |
| --- | ---: | ---: | ---: | ---: | ---: |
| inactive-2x | 76 | 65 | 11 | — | — |
| inactive-1x | 76 | 71 | 5 | — | — |
| active-2x | 4 | 2 | 1 | — | 1 |
| active-1x | 4 | 4 | — | — | — |
| 1x increased contrast | 14 | 9 | — | 4 | 1 |
| 1x reduced transparency | 14 | 9 | 2 | 3 | — |
| **all** | **188** | **160** | **19** | **7** | **2** |

**Two cells fell below five of seven**, both at 4/3 and both resolved by `resolveCell` as *voted*
(the minority reading differs at or below one 8-bit code, or scatters rather than forming a region):
`apple-macos-26.5-2x-light-standard/mid-chroma-solid__rrect-md__rest` and
`apple-macos-26.5-1x-light-increased-contrast/checkerboard__rrect-ml__inactive`. No cell was
refused, none was state-ambiguous, and one cell — 2x light
`mid-chroma-solid__capsule-button__rest-tint-orange` — was frequency-settled at a 6/1 majority.

**The cells captured under 45 s of input idle agree at least as often as the rest.** The sitting
lists 50 such cells; 43 of them are unanimous across all seven runs (86.0%) against 117 of the other
138 (84.8%), and only one is below 5/7 (`checkerboard__rrect-ml__inactive` under increased contrast,
disturbed in runs 1 and 6 and voted 4/3 within one code). The tracker's open question — whether a
mid-run touch changes the byte-state — reads **no** on this bed.

**The six background-identical cells enter as what they are.** `dark-solid__capsule-button`,
`dark-solid__rrect-48` and `dark-solid__rrect-sm`, each in both schemes, carry the harness's
`identicalToBackground` caveat in every inactive standard run at both scales: over that backdrop the
recede leaves no component pixel at all. They are published with the caveat, and vitrea reproduces
all three of them exactly: in every standard profile at both scales the three cells read body ΔE
**0.000000**, web and native interior Y both **0.011712**, which is the backdrop's own level. The
one thing the endpoint gets exactly right on this bed is the disappearance.

## 3. The bound, clause by clause

WebGPU tier throughout, real Apple `metal-3` adapter, no fallback, every row `gpu-texture` sampled,
zero `problems` and zero diagnostics over all 174 rows. Scored: group D, the 12 checking ids, on
every profile that declares them — 72 cells. Groups A, B, C and E are read and published and not
scored, exactly as `bound.json`'s scope states.

| profile | clause 1 (ceiling, full-canvas) | clause 2 (mean body ΔE) | clause 3 (2× floor) | joint |
| --- | --- | --- | --- | --- |
| 1x light standard | holds (worst 0.00458 / 0.07) | holds (0.01321 / 0.032, 0.41×) | **fails** — `hc-text__rrect-sm__inactive` 0.07793, 2.44× | **FAILS** |
| 2x light standard | holds (0.00400 / 0.07) | holds (0.01198 / 0.034, 0.35×) | **fails** — `hc-text__rrect-sm__inactive` 0.07310, 2.15× | **FAILS** |
| 1x dark standard | holds (0.01604 / 0.09) | holds (0.02040 / 0.034, 0.60×) | holds | **HOLDS** |
| 2x dark standard | holds (0.01603 / 0.09) | holds (0.01781 / 0.041, 0.43×) | holds | **HOLDS** |
| 1x light increased contrast | holds (0.01090 / 0.06) | **fails** (0.01936 / 0.0078, 2.48×) | **fails** — `dark-solid__rrect-48__inactive` 0.16224, **20.80×** | **FAILS** |
| 1x light reduced transparency | holds (0.01071 / 0.04) | **fails** (0.02138 / 0.011, 1.94×) | **fails** — `dark-solid__rrect-48__inactive` 0.17417, **15.83×** | **FAILS** |

Clause 4's reported, non-gating figures: the checking set's footprint fraction is 0.2138 against the
calibration sets' 0.081–0.107, so it is 2.0–2.6× larger by construction; the full-canvas ratio to
calibration runs 0.98–2.44× and the body ratio 0.72–3.71×. The full-canvas ratio is reported and is
not a gate quantity, for the reason `decomposition.json` gives.

Clause 5: no row was refused, none was suspended, nothing stopped. Group E's re-attestation is §4.

**Holding is clauses 1, 2 and 3 jointly on every profile the checking set covers.** Two profiles
hold. G2 stays blocked by default; shipping the pose on the profiles that hold and withholding it on
the others is the user's decision, not this read's.

### The inversion

Retro-applied to the spent holdout, the same bound failed four of six profiles: both dark on clauses
2 and 3, both light standard on clause 3 alone, and **only the two accessibility profiles held all
three**. On the checking bed the pattern is almost exactly reversed.

| profile | on the spent holdout (§5.134 §6) | on the checking bed |
| --- | --- | --- |
| 1x / 2x light standard | fails clause 3 alone (`photo__rrect-lg__inactive-tint-orange`, 2.20× / 2.07×) | fails clause 3 alone (`hc-text__rrect-sm__inactive`, 2.44× / 2.15×) |
| 1x / 2x dark standard | fails clauses 2 and 3 | **holds all three** |
| 1x increased contrast | holds all three | **fails clauses 2 and 3** (20.80× on one cell) |
| 1x reduced transparency | holds all three | **fails clauses 2 and 3** (15.83× on one cell) |

Only the light standard verdict generalised — same clause, same failure mode, a different cell
family. The dark pair's holdout failure did not, and the accessibility pair's holdout pass did not.

A profile holding this bound is not a claim that the recede is matched there. On 1x dark
`checkerboard-lc16__rrect-md__inactive`, which clears clause 3 at 1.67× and sits inside its profile's
mean, the sheet shows the web body visibly darker than the reference (0.05217 against 0.07956 Y) with
the backdrop's checker reading through an interior the reference keeps smoother.

## 4. Group E: the recovered bed is confirmed

28 cells where a bed id already had a recovered fixture: the sitting's plurality bytes against the
bundle's recovered ones, native against native, no vitrea capture in it.

**24 of 28 are byte-identical.** The other four — 2x light and 2x dark `checkerboard__rrect-md` and
`photo__rrect-md` — differ at **one** code on 236–362 pixels (0.09–0.14% of the canvas) with
coherence 0.13–0.32, which is *incidental* by `src/plurality.ts`'s own rule. Clause 5's suspension
condition does not fire. A fresh, attested, seven-run 26.5 session reproduces fixtures the record
held as schema-2, single-run, pose-inferred evidence: **W27 Decision Log 5's admitted bed is
confirmed by measurement**, and the DL14 post-mortem's inference of the pose is right.

## 5. What the bed says about §5.134's five classifications

| residual | §5.134's class | the checking bed |
| --- | --- | --- |
| (a) mid-dark-solid's middle anchor | **bed** | confirmed, and now supplied. Fresh dark `mid-dark-solid__rrect-sm` reads web 0.08866 / native 0.04092 — the spent holdout's own pair to five decimals, on a different component and a fresh capture — and the thick spans read 0.06480 / 0.03310. Light: 0.40198 / 0.45079 thin, 0.52100 / 0.52712 thick. Arm A3 has its two ordinates. |
| (b) far-span scatter | **model-form** | confirmed and widened. At span 128 `checkerboard__rrect-ml` is over-structured — web/native interior SD 1.10× (1x dark), 1.41× (1x light), 1.64× / 1.70× at 2x — while at fine pitch the same material is *under*-structured (0.48–0.76× at pitches 8 and 32 in 1x dark). The deficiency is a pitch × span surface, not one far anchor; `impulse` reads the kernel directly and the body gathers far too much light (dark 0.04303 / 0.01546 Y, light 0.46446 / 0.41427). |
| (c)/(e) chroma transfer | **model-form, one cause** | confirmed decisively by the background built for it. Untinted `mid-chroma-solid` interior chroma: web 0.0673–0.1006 against native 0.1648–0.2326, 29–61% of it, while the level misses in the *opposite* direction per scheme (light too bright 0.619 / 0.476, dark too dark 0.057 / 0.094). Tinted: web chroma **exactly 0** against native 0.1207 (light) and 0.1926 (dark). Level and chroma cannot both be met by the declared family, measured on a zero-variance anchor rather than inferred from `photo`. |
| (d) the stacks | metrology | **not re-read.** Both `glass-over-glass` ids carry §5.130's holdout role; the read produces no vitrea-against-native distance for a spent-holdout id, so arm A4 stays declared and unrun and the stack-specific term stays unmeasured. |

## 6. Three findings the classification did not anticipate

1. **The dark thin response at a bright backdrop is not merely unmeasured — it is wrong by 0.77 Y.**
   `light-solid__rrect-sm__inactive` in dark reads web 0.16225 / native 0.93261, body ΔE **0.43179**,
   the largest reading on the bed. The native recede over a bright solid at span 32 is *invisible*;
   vitrea paints a dark panel. §5.130 recorded dark `backdropToneResponseThin`'s far ordinate as
   "an extrapolation of this selected family, not a measured bright-background level" — the bed
   measures it, and the extrapolation (0.1611) is off by a factor of six. At thick span the same
   backdrop reads 0.09339 / 0.11753, so it is the thin row alone. A supplying cell, not scored.
2. **The accessibility recede is backdrop-coupled where Apple's is not.** Over `dark-solid` under
   Increase Contrast the native material is an opaque near-white panel at every span — 0.9945 at
   span 48, 0.9937 at 80, 0.9935 at 96 — while vitrea follows the backdrop down at the thin end:
   0.5841 at span 48, recovering to 0.9560 by span 80. That one cell is the 20.80× and 15.83×
   clause-3 exceedance and most of both accessibility profiles' clause-2 failure. §5.130 fitted
   `increasedOcclusionLift` on 1x light accessibility bodies and recorded that "their different
   native levels are not fully expressible by this shared policy fold"; the fold misses by 0.41 Y.
3. **The chroma deficit is the active material's, not the recede's** (§7).

## 7. The four active `mid-chroma-solid` cells

Read against the active profiles, no receded patch, 1x and 2x light.

| cell | full-canvas ΔE | body ΔE | body Y web/native | body chroma web/native |
| --- | ---: | ---: | --- | --- |
| `capsule-button__rest` | 0.00978 | 0.12540 | 0.67344 / 0.45199 | 0.08323 / 0.15937 |
| `capsule-button__rest-tint-orange` | 0.00328 | 0.03883 | 0.36642 / 0.31126 | 0.16618 / 0.15897 |
| `rrect-md__rest` | 0.02925 | 0.11447 | 0.69324 / 0.52594 | 0.07671 / 0.16797 |
| `rrect-lg__rest` | **0.08645** | 0.11671 | 0.69360 / 0.52257 | 0.07678 / 0.16963 |

The active material over a saturated uniform backdrop transmits **about half** the backdrop's chroma
and sits 0.17–0.22 Y too bright. So the chroma half of residuals (c)/(e) is **inherited, not caused
by the recede**: the missing degree of freedom is in the shared material model. The tinted cell is
the good one (body ΔE 0.039) because the author's own hue dominates what the body fails to transmit.

The reference's own inactive/active chroma ratio on this background is **1.034** at the capsule and
**1.058** at `rrect-lg` in light — the recede transmits slightly *more* chroma than the active pose,
which is §5.128's census finding reproduced on a purpose-built backdrop rather than on `photo`.

`mid-chroma-solid__rrect-lg__rest` reads full-canvas ΔE **0.08645**, above the 0.07 the active
material is held to on this profile. It is a `probe` cell, so no adopted bound and no floor moves,
and none is proposed here — but it is the first cell in the bed where the *active* material would
not clear its own ceiling, and it is recorded rather than left in the matrix.

## 8. Files

| file | what |
| --- | --- |
| `plurality-report.py` → `plurality.json` | the seven-run agreement per cell, and the idle group apart |
| `materialize-bed.sh` → `materialize.out` | the six publication phases, exactly as run |
| `round-trip-check.py` → `round-trip.json` | every pre-existing entry and PNG diffed against `ec809ae6` |
| `manifest-doctor-before.txt` / `-after.txt` | the Swift round trip either side of publication |
| `g2-read.ts` → `checking-matrix.json`, `checking-read.out` | the web read, 174 rows, scratch only |
| `native-attestation.py` → `attestation.json` | group E, native against native |
| `score-bound.py` → `verdict.json` | the bound applied, clause by clause |
| `sheet.py` → `sheets/*.png` | native \| webgpu \| 8× difference, per profile, worst body ΔE first |

The web captures themselves are scratch (`VITREA_WEB_CAPTURES=/tmp/w27c-g2/captures`) and are not
committed; every row carries its capture's sha256.

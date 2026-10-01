# W42 G2 — the improvement-landing addendum (Decision Log 7), committed before any vitrea render (2026-10-01)

**Status: the user's ruling and the parent's terms, written out before any vitrea render of the new
bed or of a candidate document.** It is committed on its own and its SHA-256 is recorded in the
charter's Decision Log 7. It changes no recorded number and no verdict of step 2
(`step2/verdicts.txt`, ledger §5.196). It replaces clause 6's survival as the landing path's
structural bar with an improvement rule over what ships. Every other clause stands as written
unless an item below says otherwise.

## 1. The ruling

The question put to the user (verbatim):

> "No declared model reproduces Apple to within 1 code on every cell, so W42's identification is
> negative. But the main law (LT) is much closer to Apple than what ships ... Should W42 continue
> toward landing on that measured improvement, or close here?"

The option the user chose, **"Land on improvement (Recommended)"** (verbatim):

> "Record the identification as negative (LT is not Apple's exact law). Before rendering anything,
> declare an improvement rule: on the new capture's test cells, vitrea with LT must be closer to
> Apple than shipped vitrea in every backdrop type, with no cell worse by more than ~1-2 codes.
> Then run every existing landing check, then the one blind test on the unseen holdout. Three
> window states only: dark focused is excluded (its two required fits disagree). The live-backdrop
> cost (~4-5.5 ms/frame) comes to you for a decision before release."

## 2. What stays recorded

1. **The identification is negative in all four endpoints** (§5.196): no declared family survives
   max(1 code, bar) on every calibration and validation statistic, and it stays recorded so. LT is
   not Apple's exact law.
2. **Endpoints on this path: light active, light receded, dark receded.** Dark active stays at the
   identity under Decision Log 5f: its narrow-mask and 53.6-pt fits differ (dk +0.150,
   dλ −0.238 against k +0.049 / −0.048 and λ ±0.029).

## 3. The values (LT at the least-squares point)

**Why least squares, stated before any render.** The declared refinement is minimax on the region
statistics. In light active the minimax point (k 1.405, λ 1.323) is dragged by the one class (a)
cell, the 1x pitch-8 rrect-lg checker, which no Gaussian closes (memo E §2e). That move takes the
cell from 14.1 to 12.4 codes and costs 3,584 failing statistics instead of 2,322 and a 2x worst of
12.4 instead of 4.1. At the least-squares points the k ladder keeps `k@global`: no less restricted
level beats it by more than max(3, sum of bars) = 3 codes at an admitted discriminator, the
largest gain being 1.80 (`step2/verdicts.txt`).

The law's values are those of `step2/fits/main/LT@k@global__all__n.json`, least-squares point:

| leaf | light active | light receded | dark receded | dark active |
| --- | --- | --- | --- | --- |
| `bodyLawStrength` | 1 | 1 | 1 | **0 (identity)** |
| `bodyLawK` (k_n, k_w) | 2.1378819065300068 × 2 | 2.1378819065300068 × 2 | 2.1378819065300068 × 2 | — |
| `bodyLawLambda` | 0.868087996132754 | 0.7668713671405096 | 0.7588099764934113 | (0.8511525213644479, not used) |
| `bodyLawKnee` | 0 (per-channel) | 0 | 0 | — |
| `bodyLawWidthUnit` | 1 (points) | 1 | 1 | — |
| `bodyLawEncodedAveraging` | 1 | 1 | 1 | — |
| `bodyLawNormal` | 0.5 | 0.5 | 0.5 | — |
| `bodyLawHinge` | +1 | +1 | −1 | — |
| `bodyLawPose` | 0 | 1 | 1 | — |
| `bodyLawEdgeSwap` | 0 | 0 | 0 | — |

The knee is per-channel and the width unit is points (§5.196 §4–§5). In light active the
refraction order is AFTER: S2 was admitted and read Â −6.53 pt, so refraction acts after the blur.

**Candidate 1** (the landed T):
- Light active and dark receded: the shipped solve's uniform response per pixel, with the
  black-join bridge of `candidate1-black-join-addendum.md` (SHA-256 `8ad314c1…`).
- Light receded: E3 under the law. E3's F keeps its seven neutral ordinates (150, 157, 164, 171,
  178, 188, 197 at 40, 56, 72, 88, 104, 128, 150). It is extended above 150 by family A's
  light-receded ordinates, `bodyE3NeutralHigh` = **201.9278, 208, 215, 221, 228, 234, 240** at
  160, 176, 192, 208, 224, 240, 255. These are the Rec.709 values of the 2x capsule greys; R and G
  read 202 at 160 and B reads 201. g is W41's shipped E3 gain, evaluated at L(W).
- Values: `step2/candidates.json`, `endpoints.light-inactive.candidate1`.

**Candidate 2** (native T):
- `bodyToneTableCodes`: the native-T tables under `native-t-addendum.md` (`23e400bf…`), exactly as
  declared. Five rows (64, 80, 96, 128, 160) by eleven levels, one row set per channel, because
  the greys are not neutral within the bar.
  - Values: `step2/candidates.json`, `endpoints.<endpoint>.candidate2.bodyToneTableCodes`. The
    source is `step2/native-t/ordinates.json`.
  - Its dark completion below s = 128's lowest measured level is recorded and **not repaired**
    after the read (section 7).
- The chroma scale, read by least squares at these landing values on family E's calibration cells
  with the per-channel knee (`step2/landing-scale.json`, `step2/landing_scale.py`):
  **light active 0.976496, light receded 0.987365, dark receded 0.909586**. g is W41 G1's E3 fit
  per endpoint (`local.leastSquares.coefficients`).
- `candidates.json` also carries the per-endpoint (`k@endpoint`) LT fits and the earlier scale
  readings. They are not this path's values; the two tables above are.

## 4. The improvement rule (rule 4; clause 9′ on the landing path)

**Population.** The new bed's web-plannable calibration and validation cells of the three claimed
endpoints, at both scales. Each is rendered by vitrea twice: with the candidate, and with the
shipped documents (the clause 8 base). Both renders are read with the declared instrument
(`instrument/regions.py` on `forward.Cell`'s deep masks: active d ≤ −(20 + 16.8 t) pt, receded
d ≤ −8 pt), as is Apple's plurality frame from the archive (`step2/common.py`). Every channel is
required.

**Errors.** For each cell, region statistic and channel, e = rendered − Apple:
- *measured* when Apple's value lies in (5, 250);
- *censored* otherwise, entering as the rail deficit of W41 G1's `body41.score`: max(pred − 5, 0)
  when Apple reads ≤ 5, and max(250 − pred, 0) when Apple reads ≥ 250.

**(a) Stratum improvement.** For every declared stratum of an endpoint (section 5) that has at
least one measured statistic, the candidate's pooled rms is ≤ the shipped render's pooled rms.
- The pooled rms of a stratum is sqrt(mean over its cells of [mean over the cell's measured
  statistics and channels of e²]): equal weight per cell, measured statistics only.
- There is no tolerance: ≤ is literal.

**(b) No statistic worse by more than 2 codes.** For every region statistic and channel of every
cell:
- measured: |e_candidate| ≤ |e_shipped| + 2 codes;
- censored: deficit_candidate ≤ deficit_shipped + 2 codes.

2 is the upper end of the user's "~1-2".

**(c) Uniform invariance is unchanged.** Clause 7 holds as written: candidate 1's deep median on
the uniform cells equals its reference within one code (the shipped render; light receded, E3 with
its extended F alone), and candidate 2's equals its own T with every W42 spatial gate at identity.

A candidate passes rule 4 in an endpoint only if (a), (b) and (c) all hold there.

## 5. The strata for rule 4(a), enumerated from the bed

- **Backdrop kind**, by bed family: uniform (A); grey two-level checker (B, B′); colour isoluminant
  checker (E); patch or impulse (C); step (D).
- **Span class**, the declared strata: t = 0 (every s ≤ 64), s = 80, 96, 128, 160.
- **Both scales** are pooled within a stratum.
- Family F (bridge-only) and H are not in the population.
- Counts below are cell-passes; "val" marks validation cells.

**Light active: 17 strata, 85 cell-passes.**
- Uniform:
  - t=0: 13 (2x capsule ×10; 2x rrect-64 ×3 val);
  - s=96: 12 (2x rrect-md ×10; 1x rrect-md ×2 val);
  - s=128: 3;
  - s=160: 4.
- Grey checker:
  - t=0: 7 (P1 pitch 32 on the capsule and rrect-64; P1 pitch 64 on the capsule; P1 pitch 8 on
    the capsule, 2x and 1x; P1 pitch 4 on the capsule and its odd offset, 1x);
  - s=80: 1 (val);
  - s=96: 9 (P2, P4 and P5 at pitch 16 and 64; P3 at 16 and 64, val; P1 pitch 4, 1x);
  - s=128: 3 (P1 at pitch 32, 64 and 8);
  - s=160: 8 (P5 at 16 and 64; P3 16, val; P1 pitch 32 at 2x and 1x; P1 pitch 8 at 2x and 1x;
    P1 pitch 4, 1x).
- Patch / impulse:
  - s=96: 6 (S 32 hi/lo; S 8 hi, d34; S 8 hi and lo at the centre; S 8 hi d24, val);
  - s=128: 1 (the impulse grid);
  - s=160: 5 (the impulse grid at 2x and 1x; S 8 hi at d60 and d80; S 8 hi d40, val).
- Step:
  - t=0: 1 (δ0 lo|hi on the capsule, val);
  - s=96: 4 (δ0 and δ32, both polarities);
  - s=160: 2 (δ0, both polarities).
- Colour checker:
  - s=96: 4 (rg at pitch 16 and 64; by at pitch 16; by at pitch 64, val);
  - s=160: 2 (rg at pitch 16; by at pitch 16, val).

**Light receded: 16 strata, 92 cell-passes.**
- Uniform: t=0 13; s=96 12; s=128 3; s=160 4.
- Grey checker:
  - t=0: 9 (P1 pitch 16 and 8 on rrect-sm at 2x, pitch 8 at 1x; the capsule at pitch 32 and 64
    at 2x, pitch 8 and 4 at 1x, plus pitch 4 at its odd offset; rrect-64 at pitch 32);
  - s=80: 1 (val);
  - s=96: 9;
  - s=128: 2;
  - s=160: 4.
- Patch / impulse:
  - t=0: 4 (S 16 hi/lo on the capsule; S 16 lo at the capsule's end, val; S 8 hi on rrect-sm);
  - s=96: 7;
  - s=128: 1;
  - s=160: 5.
- Step:
  - t=0: 3 (δ0 on the capsule and rrect-sm, val; δ12 on the capsule);
  - s=96: 11 (δ0, δ12, δ32 and outside 8 / 16 pt, both polarities; outside 8 pt lo|hi at 1x).
- Colour checker: s=96 4.

**Dark receded: 17 strata, 107 cell-passes.**
- Uniform: t=0 13; s=80 3; s=96 12; s=128 3; s=160 4.
- Grey checker: t=0 9; s=80 1 (val); s=96 9; s=128 2; s=160 4.
- Patch / impulse:
  - t=0: 4;
  - s=96: 11 (with the 16 / 112 patches);
  - s=128: 5 (the impulse grid; the 16 / 112 patches at S 8, and at S 32 as val);
  - s=160: 5.
- Step: t=0 3; s=96 15.
- Colour checker: s=96 4.

The cell lists are derived mechanically from `bed/bed.json` (SHA-256 `53870f47…`): role
calibration or validation, the pass `{scale}x-{scheme}-{pose}` present, kind by family and span
class by `geometry.shortSide`.

## 6. Clauses 10, 11′ and X40

- **Clause 10 is unchanged.** Every landing referee runs in candidate-admission mode on the
  canonical calibration/validation bed, with the paths of Decision Logs 5a–5e and the eye sheets
  by stratum. The two directional stops and the owner test are included. Any failure means no
  exposure.
- **Clause 11′, the one exposure on H:**
  - First, the blind rendered predictions for H's cells (candidate and shipped, every claimed
    endpoint, both scales where H is captured) are frozen by artifact, under clause 11's X26
    machinery.
  - **H's bar is rule 4 (a)–(b) applied to H's cells, read once.**
  - H's strata are its declared cells by the same kind × span class: uniform s=96 (grey 184; grey
    232 at 2x and 1x), grey checker t=0 (128 / 229 at pitch 64 on the capsule), s=96 (P6 32 / 176
    at pitch 32), s=112 (P1 at pitch 24 on rrect-112, the unseen span), s=160 (P3 at pitch 64 on
    rrect-lg, 2x and 1x), step s=96 (δ20), patch s=96 (S 24).
  - Clause 6's survival is **not** H's bar on this path.
  - A censored H statistic enters (b) by its rail deficit. H is spent either way, and nothing
    changes after the receipt.
- **X40 as declared:** two candidates, one receipt. Candidate 2 lands instead of candidate 1 only
  if it passes every check candidate 1 faces.
- **Performance** goes to the user before release, in G3, with the bench. The law cost +3.7–5.8 ms
  a frame on live backdrops at the last bench.

## 7. Named gaps carried on this path

1. **The identification negative** (§5.196). No declared family survives one code in any
   endpoint; LT's worst is 10–16 codes. The 1x pitch-8 rrect-lg checker (class (a)) and the
   rrect-ml / rrect-lg span growth (class (b), 5–16 codes) are unclosed by any family.
2. **Dark active** stays at the identity (Decision Log 5f, the two fits differ).
3. **The native-T addendum's dark black completion.**
   - Dark T decreases above 208 at s ≥ 96.
   - The addendum's guard steps the s = 128 / 160 rows from 129 / 123 to 121 / 114 between 208 and
     224.
   - Its completion reads black at s = 128 as 26 / 14 (active / receded) where both full strata
     measure 32 / 20.
   - Candidate 2's table and the blind H predictions at s = 112 inherit it: dark receded black there
     is 17.
   - It is recorded and not repaired after the read.
4. **The level misses.** Candidate 1's landed T carries W36's grey-middle miss and the named black
   miss. The L1 named misses of Decision Log 5d stand.
5. **The chroma misses.** On family E the per-channel luma closes within 2 codes, but chroma misses
   by up to 15–16 codes in the receded endpoints. It depends on pitch and on position, and one scale
   on W41's g cannot carry it. The landing scales in section 3 are read, not identified.

# W26 G2 — the declaration: the heavy width at 9 and 9

**Written before this child rendered a single pixel.** The wave's rule is that the constants, the
documents, the fingerprints, the goldens' attribution and the stops are declared BEFORE the bed is
run, so that a reading cannot be chosen after the fact. Everything in this file was committed
before the first capture; what the run then read is in `g2-dryrun.md`, and the two are separate
files rather than two halves of one so that the boundary is a commit rather than a horizontal rule.

Parent: `docs/doperpowers/specs/2026-09-10-w26-heavy-width.md`. This child executes **Decision Log
6 (f)**, on the candidate **Decision Log 6 (a)** declared. Claims §5.119–§5.122 are the ledger
entries the evidence lives in; §5.123 is this landing's and is drafted with the run.

---

## 1. What lands

| constant | 0.14.0 | **W26 lands** | fitted on |
| --- | --- | --- | --- |
| `sizeHeavyTapSigma` | 0 (the mechanism off; the chain's clamped tap drew 13.418) | **9** | the family reader (claims §5.121 §1) on `rrect-md` and `rrect-lg` at dpr 1 in both schemes, holdout-free: 9.48 / 8.63 / 9.19, spread 9.8 %, mean 9.10 |
| `sizeHeavyTapSigma2x` | 0 (the chain's trilinear tap at `scatterLod`) | **9** | the same at dpr 2: 8.13 / 9.79 / 8.37, spread 20.4 %, mean 8.76 (mean 8.96 over the two light cells) |

Both are a Gaussian σ in **device px**, resolved per scale by `rampAtScale`
(`heavyTapSigmaAtScale`), and they are the width of the heavy component the optics pass samples in
place of the chain tap. Nothing else on either document moves: `blurSigma`, the ramp's anchors,
`sizeScatterFloor` / `…2x`, `sizeScatterSpanMax` / `…2x`, `sizeSpanMin`, `sizeSpanMax`, W23's rim
law, W24's lit edge and transmission, W25's along-side field and the three constants W25 and W26
declined are all where their own rows put them.

### 1.1 Why 9 at dpr 1, and why the number is not 13.418

The 0.14.0 material had no heavy width at all: the deep sample was one level of the backdrop
pyramid, and at dpr 1 `scatterLod` was clamped at `chainMaxLod`, so what vitrea drew was
`CHAIN_LEVEL_SIGMA[4]` = 13.418 device px whatever the three gain constants said (claims §5.116 §2;
W26 Decision Log 2 (a)). **Apple's heavy width, identified without a shape assumption, is 8.6–9.2
device px at 1x on both surfaces and in both schemes** (claims §5.121 §2), so vitrea's 1x heavy
component was about half again too wide, and the share — which W25 and W26 both tried to raise —
was already right to within 0.07.

The reading is the family reader's, and the family reader is the instrument of record because it is
the only one in this wave that passed a control: it reproduces vitrea's OWN drawn width to 0.6 % and
its share to 0.043 where the drawn tap is a member of the fitted family, and every reading of the
reference moves by under 6 % when a backdrop is dropped, the band moved or the raster tiled. The
two-Gaussian readings this wave quoted earlier — 19.52 at 1x through the impulse tile, 8.4 through
`checkerboard-64` — are single-backdrop projections and are quoted from here on only with the
backdrop they were read through (Decision Log 5 (a)).

### 1.2 Why 9 at dpr 2, and what one number gives up there

At dpr 2 the reference asks 8.13 on the 96-span surface, 9.79 on the 160-span one and 8.37 on the
96-span dark one — a spread of 20.4 %, so **one number does not serve both spans at this scale**.
The mechanism is one width per SOURCE, not per pixel (Decision Log 2 (b), ruled by the parent at
2 (f)), so the span grading `sizeScatterGainFar2x` used to carry cannot be carried, and its size is
measured: **1.66 device px between spans 96 and 160**, 20 % of the smaller. 9 is within 11 % of each
of the three 2x readings and 0.4 % of the two light ones' mean. That gap is recorded, not chartered.

### 1.3 The mechanism has no small values, and the declaration says so

`pyramid.ts` builds the heavy texture whenever `heavySigmaCss > 0`, and `heavyTapPlan` at a σ of
0.001 selects chain level 0 with a residual of a thousandth of a texel — which makes the deep
sample the RAW backdrop and moves every 2x row. So a σ of 0.001 is not "almost off"; it is the
opposite of off. **The inert control is exactly 0, both anchors land at 9, and neither anchor may
ever be a small non-zero** (Decision Log 6 (c)). Both profile documents carry that sentence, and the
tracker carries the shape of the fix — a floor in `heavyTapPlan` at the chain's level-1 width would
make the constant's domain continuous.

## 2. What does NOT land, and why each is a measurement

| constant | value | why |
| --- | --- | --- |
| `sizeScatterHeavyShareThick1x` | 0, declined | the share was already within 0.06 of the reference's and the candidate does not move it (claims §5.122 §4). W25's decline and W26 Decision Log 4 (b)'s stand, now confirmed by an instrument with a control. |
| `sizeScatterHeavyShareThick2x` | 0, declined | the 2x share is too HIGH, so a lift is the wrong sign (Decision Log 3 (e)). |
| `sizeScatterFloor2x` | 1, unchanged | the objective is flat and every value off 1 moves the thin `impulse__rrect-sm` row, which X5 forbids (Decision Log 3 (e)). |
| `sizeToneLevelFar` | 0, declined | the candidate moves no probe solid by more than 0.00001 and W25's sign flip across backdrops is unchanged. |
| `sizeScatterGainMax`, `sizeScatterGainMax2x`, `sizeScatterGainFar2x` | 8 / 4.8 / 9.9, **kept and now inert** | they feed only `scatterLod`, which the heavy texture overwrites on every group whose source carries a pyramid: fifty rows byte-identical between 9.9 and 4.8 at the candidate (claims §5.122 §6a). Their doc comments say so this wave. **Retiring them is not folded into a declaration**, because it means deciding what a profile naming NO heavy width draws, which is a code-removal wave with no fidelity content (Decision Log 6 (b)); the tracker carries it. |

## 3. The fingerprints

| document | before | after |
| --- | --- | --- |
| `apple-macos-26.5-1x-light-standard.json` | `e6edd84292259f3a` | **`b2b570e4adcea8fb`** |
| `apple-macos-26.5-1x-dark-standard.json` | `874be66ea501621b` | **`eee7294f409966d7`** |

Computed by `g2-fingerprint.mjs --heavy 9 9` before the edit, so the declaration records the number
it measured rather than the number it expected. **Only the LIGHT document names the two constants**
(with a `$comment-w26`); the dark document is a difference document (X7) and inherits them through
`DEFAULT_MATERIAL_PROFILE`, which is why its fingerprint moves while its `patch` does not. G1c
measured the dark reference at 9.15 (dpr 1) and 7.80 (dpr 2), so the dark scheme does not ask for a
different value and nothing is named there. Both documents' fingerprints move, so **all six profiles
are re-run and none rides along as a byte check**, and `platform-web/src/dark-profile.ts` is
regenerated and diffed before the run.

## 4. The stops, declared

W25 G3's set carried — S1–S8 and S10–S14, the numbers unchanged — with S13 re-stated onto this
wave's mechanism and S15 added as Decision Log 4 (a) re-stated it and Decision Log 6 (f) assigned
it. Where a stop is expected to fire, **it is declared as firing here, before the run**, with the
ruling that dispositions it; a stop nobody expects to fire is not a stop, and a firing discovered
after the fact is not a reading.

- **S1** — any untinted row worse than the 0.14.0 bed by more than 0.001 ΔE mean or 0.005
  `ssimMean`.
- **S2** — any tinted cell moved by more than 0.002 in body.
- **S3** — a calibration ΔE group mean above the 0.14.0 bed's by more than 0.0001. **Expected to
  fire on the two dark profiles.** Decision Log 6 (e): the dark bed's thick spans worsen at the
  candidate (1x span 128 0.01703 → 0.01892, span 160 0.02173 → 0.02404) on a width its own reference
  reading asks for, and the dark bed's thick-span error is three times the light bed's both before
  and after. Its disposition is that ruling; the number is read per group and written down.
- **S4** — a golden moved for any reason but the two constants, read by the attribution spec of §7
  before a golden byte is rewritten.
- **S5** — a fitted constant whose rows do not separate it. Read as the ladder's own condition: the
  mapping from the named σ to the read width has slope 0.995–1.111 with an rms of 0.03–0.06 device
  px over seven rungs, and the two off-diagonal rungs `x98` / `x910` separate the two scales
  exactly (claims §5.122 §3).
- **S6** — a CSS capture moved without an explanation. **This tier moves this wave**, and the
  prediction is arithmetic rather than a hedge: the heavy layer's composed width goes 13.80 → 9.00
  CSS px at dpr 1 at every span, 4.455 → 4.500 at dpr 2 span 96, 6.121 → 4.500 at dpr 2 span 160 and
  9.188 → 4.500 at dpr 2 span 256 (§6). A CSS capture that does NOT move is the thing to explain.
- **S7** — a collapsed cell whose body moves by more than 0.002.
- **S8** — the user's eye (X6), over `sheets/`.
- **S10** — a cell the constants cannot reach that moves. The constants reach every group whose
  source carries a backdrop pyramid, which on this bed is every group at every span — the heavy
  share has a floor of 0.4, so even a 32 px surface carries a heavy component — so this stop's
  expectation is inverted: a cell that holds byte-identical is the one that needs a reason.
- **S11** — W23's straight-span contour reads moved by more than 0.005 on any solid side, and W24's
  angular bins moved by more than 0.005 on any bin of any untinted solid row.
- **S12 / X5** — any thin cell (span at or below 44 CSS px) moved by more than 0.001 OKLab ΔE.
  **Read on BOTH tiers this wave**, which is a change: G1c read X5 on the GPU tier alone (worst
  0.00021 over 81 thin probe cells) because a scratch rung moved no CSS code, and this landing moves
  the CSS tier's own heavy width at every span including the thin ones.
- **S13** — re-stated for this wave. W25's form ("a golden moved outside a thick surface's body or
  rim") named a rim mechanism; the heavy width is a BODY quantity, so the form that carries the same
  content here is: **a golden moved outside the drawn area of a glass surface**. The delta must lie
  inside the surfaces the scene declares and nowhere else.
- **S14** — a probe row worse by more than 0.002 ΔE at the candidate than at the inert control.
  **Expected to fire on the dark thick spans**: G1c measured 1x dark span 160 at +0.00231 and span
  128 at +0.00189. Same disposition as S3, and the per-row numbers are read and recorded.
- **S15** — *this wave's, and the one the mechanism is answerable to.* The heavy σ read on the
  **family reader** (`g1b/w26blib.py` through `g1c/g1c-read.py`) on any fitted row, or any row whose
  reference two-component fit is conditioned (a sharp component under 4 device px), further from the
  reference's than at 0.14.0. **Expected to fire on two of the six fitted cells**, both at dpr 2:
  `rrect-md` 2x light |log(read/ref)| 0.064 → 0.119 and `rrect-md` 2x dark 0.032 → 0.092 — the two
  cells the 0.14.0 material already had nearly right at that scale. Its disposition is Decision Log
  6 (a), which declared the candidate on the aggregate (0.275 → 0.069 over six cells, a 75 %
  reduction) with the 2x spread of 20.4 % in view, and Decision Log 2 (f), which recorded the span
  grading one width per source gives up. The reading is taken cell by cell and written down.

## 5. How the bed is run

Three runs, in this order, one capture process at a time (X4), everything to scratch under
`/Users/new/.claude/jobs/5c70e47f/tmp/w26/g2/` through `--out-matrix` and `VITREA_WEB_CAPTURES`:

1. `g2-bed-run.sh` — the frozen bed, **calibration and validation**, all six profiles, both tiers,
   the GPU tier first within each column so every dom cell's coherence axis is measured against a
   GPU capture already on disk.
2. `g2-probe-run.sh` — the probe set (`--set probe`), the four standard profiles, both tiers. Both
   tiers rather than G1c's one, because the CSS tier's own width moves this wave and X5 is read on
   it.
3. `g2-holdout-run.sh` — **the wave's one holdout read (X3)**, all six profiles, both tiers, run
   only after every clause and every stop above has been read on the first two, with nothing in the
   material, the documents, the goldens or the code moved in between.

The flags are the canonical rebuild's — `--alpha` and `--write-partial` — because G3 has to
reproduce these bytes with them, and every capture's sha256 goes into `g2-digests.txt`. The matrix
is REMOVED before each run rather than appended to: a cell's key carries the material document's
sha256, so a second run at a second material leaves every cell twice (W25 G3b's own gate failed 25
of 37 cases on that alone). The canonical `results/matrix.json`, `web-captures/`,
`apps/reference-apple/fixtures/` and `scenes.json` are read-only throughout; the canonical rebuild
is G3's, from the main checkout.

**The run is taken IN THIS WORKTREE, and that is a change from G1c.** G1c captured in the shared
checkout and proved with `g1c-same.sh` that every capture-relevant source was byte-identical to it,
because a worktree carries no `node_modules`. That proof cannot be made by a child that CHANGES the
sources: this landing moves `material.ts` and `platform-web/src/optics.ts`, so a capture taken in
the checkout would be a capture of the old material on the CSS tier. `pnpm install --frozen-lockfile`
against the same store makes the worktree the same toolchain in seconds, and the run is then this
branch's code by construction rather than by comparison.

The control the run is read against, per column:

| column | control |
| --- | --- |
| the bed (calibration, validation), both tiers | the canonical `results/matrix.json`, and G1c's `c0b` rung — the 0.14.0 material captured on this machine, both tiers, 170 cells |
| the probe set, GPU tier | G1c's `c0p` rung (203 cells) |
| the probe set, CSS tier | captured by this child **before the landing edit**, at the 0.14.0 code, as `c0css` — the one control this wave did not already have |
| the holdout | the canonical `results/matrix.json`'s own holdout rows, read-only |

## 6. What the CSS tier takes, and what it cannot

**It takes the width, and this is the first wave in which the two tiers' heavy components are the
same number rather than the same law read through a conversion.**

Until now the CSS tier derived its heavy layer from the GAIN constants:
`cssTierHeavySigmaCssPx` computed `blurSigma · scatterGainAt(span, dpr)` as a nominal in device px
and multiplied it by `scatterHeavyEffectiveRatioAtScale` — 1.38 at dpr 1, 1.485 at dpr 2 — because
the GPU tier's heavy component was a mip-chain tap and NOT a Gaussian, and drawing the nominal would
have drawn a narrower body than the tier it has to agree with (claims §5.71 §5). That conversion was
a measurement of the other tier's kernel and it was right for the kernel it measured.

**That kernel is gone.** Where the profile names a heavy width the GPU tier's deep sample is the
heavy texture — a true Gaussian of exactly `heavyTapSigmaAtScale` device px, built by
`heavyTapPlan` and the separable pair, with the residual carrying whatever octave the chain lacks —
and `backdrop-filter`'s blur is a true Gaussian too. So the CSS tier draws the same number:
`heavyTapSigmaAtScale(size, dpr) / dpr` CSS px, with **no effective-ratio conversion**, because
there is no longer a non-Gaussian kernel to convert. The gain path stays in the code, exactly as it
is, for a profile that names no heavy width — which is the same material the GPU tier draws there —
and `tier-coherence.test.ts` pins both branches: the heavy branch against the renderer's own
`heavyTapSigmaAtScale`, and the gain branch against the conversion, on a profile with the anchors at
zero.

What the tier writes, before and after, at `blurSigma` 1.25:

| dpr | span | composed heavy σ before (CSS px) | after |
| --- | --- | --- | --- |
| 1 | any | 13.800 | **9.000** |
| 2 | 96 | 4.455 | **4.500** |
| 2 | 128 | 4.947 | **4.500** |
| 2 | 160 | 6.121 | **4.500** |
| 2 | 256 | 9.188 | **4.500** |

**The share does not move**: it is `scatterSharpShare`'s complement under the same fold, which is
the profile's size law and is untouched.

**The X residual, recorded and not chartered** (wave Decision Log 23 (a); parent clause 7). Two
things this tier cannot carry, and both are named rather than discovered:

1. **The two-component kernel under the cost collapse.** Where the root's cost budget collapses the
   body to one layer — or the surface has no span, or the step rounds below a quantum — the tier
   writes the single projected σ `sizeScatterSigma` computes, which is still
   `blurSigma · (1 + (gain − 1) · mix)` off the GAIN constants. That projection is now derived from
   three constants that grade nothing on the GPU tier, and one `blur()` cannot carry a sharp
   component and a heavy one at a share whatever number it is given. The collapse is a degradation
   to a known form and it stays one; what is new is that the known form is now further from the
   two-layer material than it was.
2. **The span grading at dpr 2.** The reference wants 1.66 device px more heavy width at span 160
   than at span 96 and one width per source cannot give it — on either tier. On this tier the
   arithmetic is visible in the table above: the old gain-derived width DID grade with the span
   (4.455 → 6.121) and the new one does not, so the CSS tier loses a grading it had while gaining a
   width that is right. It graded the wrong way at the wrong size (the reference's own grading is
   1.66 device px where the gain's was 3.33 in CSS px at dpr 2), which is why the width wins; but a
   tier that had a grading and now has none is a difference to macOS and it goes in the ledger.

## 7. The goldens

The two constants reach every golden scene whose backdrop carries a pyramid, so the goldens WILL
move and the movement has to be attributed before it is re-recorded. `g2-golden-attribution.spec.ts`
renders every scene twice — at the landed material and with the two anchors declined to 0 — and
compares per pixel, splitting the delta by whether the pixel lies inside the drawn area of a glass
surface (S13) and by the surface's span (X5's golden half). It is run **before any golden byte is
rewritten**, and its output is `g2-goldens-attribution.txt`.

Then, and only behind that proof: `W26_HASHES` is added to
`packages/renderer-webgpu/e2e/golden/isolation.spec.ts` with the two constants as its reason,
`W25B_HASHES` is KEPT beside it as the record of the material W25 G3b declared and ran (a recorded
reading is not rewritten to what it should have been — the correct reading goes beside it),
`goldens:regen` runs, and `test:golden` is required to pass **33 of 33** in the foreground with the
GPU guard clear first.

`highlight-press-glow` is the control and is expected to hold at **0 pixels**, byte-identical to its
2026-08-25 original for the thirteenth wave running: it captures the HIGHLIGHT canvas and the heavy
width lives in the optics pass.

## 8. What will be measured, clause by clause

| parent clause | how it is read here |
| --- | --- |
| 1 — the width is a lever | claims §5.122 §3's ladder, already run; the condition (slope, rms) is restated at S5 and not re-rendered |
| 2 — the thick surface's body matches, as Decision Log 5 (d) narrowed it | the family reader's heavy width and share per surface per scale, within 15 % and 0.05, on the dry run's own captures |
| 3 — the nested base is Apple's | `checkerboard__glass-over-glass__rest` is **holdout-only** on this bed (claims §5.122 §6c), so W25 G0's reader C is run at the holdout read and nowhere else — once |
| 4 — the collapsed dot's width | `impulse__capsule-button` FWHM through reader A, read not fitted: 6.167 native against 4.037 at the control and 4.262 at the candidate at 1x. Not met at the control either; carried |
| 5 — the bed no worse anywhere | the fourteen thick floors, every adopted bound, W23's straight spans, W24's angular bins, S1, S12 |
| 6 — the holdout once | §5's third run, and Decision Log 6 (d)'s sentence beside it: G1b was a spike that validated its instrument on three holdout scenes, so this is an untouched check of the FIT and not of the INSTRUMENT |
| 7 — the CSS tier derives what it can | §6 |
| 8 — by eye | `sheets/`: native \| 0.14.0 \| candidate at 2× on the thick rrects and the nested pane, and the impulse dot at 4× |

The gate — `adopted-thresholds.test.ts` over the scratch matrix through `VITREA_MATRIX_PATH` — is
read with the rung's own calibration and validation cells beside the canonical holdout cells, as
G1's `g1-gate.py` assembles them, and again over the dry run's own holdout once that has been read.
**`PREDICATE_EXCLUDES` is expected NOT to move**: G1c measured 38 of 38 passing at this candidate
with the file untouched, which is worth stating because W26 G1's candidate admitted two cells and
needed it edited. If the machine's output differs, the file is edited to the machine's output and
the difference is recorded.

## 9. What is already known not to be met, and is carried rather than hidden

- **The 2x span grading**, 1.66 device px between spans 96 and 160, carried by no constant this wave
  has (Decision Log 2 (f), measured at claims §5.122 §3).
- **The dark bed's thick-span ΔE worsens** at every thick span on a candidate its own reference
  reading asks for, and what the 13.418 was masking in the dark scheme is not identified (Decision
  Log 6 (e)).
- **The sharp component**: the reference's is 1.30–1.55 device px at 1x against vitrea's body of
  about 1.6, and it is `blurSigma`'s, the thin capsule's own and X5-entangled — the wave after this
  one's (Decision Log 5 (e)).
- **What no convolution explains**: about one display code RMS of Apple's interior is left by every
  family, the free forty-node profile included, with a displaced raster ruled out. It is the bound
  on every width fitted on this bed (claims §5.121 §6).
- **W25 clause 4**, the collapsed dot, not met at the control either and not regressed by the
  candidate.
- **The mechanism's domain**: 0 or at least the chain's level-1 width, with nothing usable between
  (Decision Log 6 (c)).

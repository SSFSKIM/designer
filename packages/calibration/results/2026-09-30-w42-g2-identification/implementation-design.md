# W42 G2 step 3 — the implementation design: LT, both T candidates, D1, D2 and the F extension behind zero gates (2026-09-30)

**Status: DESIGN, reviewed by the parent; its rulings on the six forks are §9 and the named gaps
§10. Nothing is fitted or rendered.**

Governed by the charter `docs/doperpowers/specs/2026-09-29-w42-body-spatial-structure.md` (G2 step 3;
X35, X36, X40; Decision Logs 3, 4, 5b–5f) and the hashed declaration
`packages/calibration/results/2026-09-29-w42-g0-declaration/declaration.json` (SHA-256 `f04ae95b…`;
items `law`, `kneeForms`, `accessibility`, `supersededLeaves`, `candidate1`, `candidate2`,
`candidate2Chroma`, `runtimeBase`). The oracle is the instrument's numpy forward model
(`instrument/forward.py`, `families.py`, `tone.py`) and the rehearsal's candidate construction
(`gate/rehearsal/body.py` `landed_T`, `swap.py`'s r3 variants). The base is `main` at `19db06ec`,
which includes PR #2; every `file:line` below is that commit's. Evidence for §2.4 is beside this
note in `implementation-design/` (`narrow_error.py`, `narrow_interp.py` and their outputs;
Python 3.12, numpy 2.3.5, scipy 1.18.0), run under `taskpolicy -b nice -n 19` with one BLAS thread
while G1's sitting held the display.

**The rule that shapes everything below.** Step 3 runs before step 2 has read the bed, so every
quantity step 2 identifies — k (one or two), λ, the knee form, the width unit the 1x cells decide,
native T's ordinates, the F extension's seven ordinates, candidate 2's chroma scale — arrives as a
document value and never as code. The declared discrete choices that need no new operator (LT-2k's
second k, the three knee forms, the three width units, the edge-mode swap) are leaves. A rival
that needs a new operator (W-shape, W-tails, K2, free σn, R1, the bleed, C-linear) is not built
unless step 2 selects it (Fork 2).

## 0. The decisions

1. **Five entries appended to `MATERIAL_IDENTITY_TABLE`**: the law (a gate-group), D1 and D2
   (plain value drops whose identities are the shipped conventions, read only by the law), the F
   extension (a gate-group) and candidate 2's tone (a gate-group). No shipped document carries a
   new key, so every entry drops at its identity under rule 2 and none of the six digests moves.
2. **The law is a new per-group stage** between the field pass and the optics pass, with one set
   of textures per surface on its declared footprint R_fp. It writes the law's encoded argument
   into one group-local texture. The optics pass samples that texture at the refracted position
   and replaces the untinted body in E3's slot, weighted by the active band.
3. **The shipped per-source pyramid is not edited.** D1 and D2 live inside the law, where the law
   is the only reader; `bodySigmaCssFor`, `heavySigmaCssFor` and the decode at
   `wgsl/backdrop.ts:86` keep serving the active band and every group the law stands down for
   (Fork 1).
4. **The narrow term is four fixed-σ levels plus one contour level**, blurred in shared-tap
   multi-target passes and interpolated per pixel by a cubic in σ through the four nearest.
   Measured against the exact per-pixel Gaussian on 96 active cells, with decimation and float16
   tiles: **0.115 code of output on the deep mask and 0.127 band-weighted at worst**; the receded
   single level 0.096 (§2.4). The repeat floor is 0.5.
5. **Candidate 1's T is the shipped solve re-executed per pixel** on the law's argument (a WGSL
   duplicate of the shipped arithmetic, pinned to it line by line); light receded is E3 with the F
   extension and g read at L(W). **Candidate 2's T** is a five-row by eleven-level table with the
   E3-form gain times one scale.
6. **One accessibility fold** covers every W42 gate, E3-under-the-law included: an exhaustive
   switch on the occlusion axis.
7. **The CSS tier** gets its derivation, filter builder and declarations now, behind the gates
   and an engine row that stays `"unverified"` until Decision Log 4's Chromium proof in G3.

## 1. Leaves and gate-groups

### 1.1 The leaves

Every default below is the leaf's value in `DEFAULT_MATERIAL_PROFILE` (`material.ts:2230`), and a
gate's default is its identity forever (`material.ts:3237–3244`). A gated leaf has no identity of
its own; its default is the declared hypothesis where one exists and is unread at the gate.

| entry | leaf | default | range | meaning |
| --- | --- | --- | --- | --- |
| **A, the law** (gate-group) | `bodyLawStrength` (gate) | **0** | [0, 1] | weight at which the law's body replaces the shipped untinted body, times the band weight; documents carry 0 or 1, fractional is E3's unmeasured linear convention (`material.ts:2124–2129`) |
| | `bodyLawK` | [2, 2] | each [0.8, 4.0] | (k_n, k_w), the radius scales: σn = k_n·5·o, σw = k_w·8, in the D1 unit. LT writes one k twice; LT-2k two |
| | `bodyLawLambda` | 0.9 | [−0.5, 1.6] | λ, the Lighten/Darken weight (the dump's 0.9; the fit's interval, declaration `law`) |
| | `bodyLawNormal` | 0.5 | [0, 1] | w, the Normal fill = `NSGlassTintAmount` (memo D §0); a leaf because `-glass0.25` is the user's next phase (charter Deferred) |
| | `bodyLawHinge` | 1 | {1, −1} | Lighten (light) or Darken (dark) |
| | `bodyLawPose` | 0 | {0, 1} | 0 active, 1 receded: selects the declared o law, margin, edge mode and band (§2.2) |
| | `bodyLawKnee` | 0 | {0, 1, 2} | `kneeForms`: 0 per-channel (the carried tie form), 1 on-luma whole colour, 2 on-luma with W's chroma |
| | `bodyLawEdgeSwap` | 0 | {0, 1} | the `edge-swap` rival: 1 swaps clamp-to-edge and normalised between the poses |
| **D1** (value drop) | `bodyLawWidthUnit` | **0** | {0, 1, 2} | the law's width unit: 0 device px (the shipped convention, W12 G3 §5.56), 1 CSS px = points (LT as declared), 2 capture texels (f device px). The 1x cells decide it (declaration `rejectedNulls`) |
| **D2** (value drop) | `bodyLawEncodedAveraging` | **0** | {0, 1} | the law's averaging space: 0 linear light (the shipped space, `wgsl/backdrop.ts:86`), 1 encoded (LT) |
| **F, the F extension** (gate-group) | `bodyE3HighStrength` (gate) | **0** | [0, 1] | above encoded 150, E3's F moves from today's continued last segment toward the table |
| | `bodyE3NeutralHigh` | [160, 176, 192, 208, 224, 240, 255] | each [0, 255] | F's ordinates at inputs 160 … 255 (family A's seven, `candidate1`); the default is the abscissae, E3's own identity-map convention (`material.ts:2947`) |
| **T2, candidate 2's tone** (gate-group) | `bodyToneTableStrength` (gate) | **0** | [0, 1] | weight of the native table against the tone below it in precedence (§2.9) |
| | `bodyToneTableLevels` | [0, 64, 96, 128, 160, 176, 192, 208, 224, 240, 255] | strictly increasing, [0, 255] | encoded input levels, family A's |
| | `bodyToneTableSpans` | [64, 80, 96, 128, 160] | strictly increasing | span rows in CSS px, the declared strata (t = 0, 80, 96, 128, 160) |
| | `bodyToneTableCodes` | 5 rows = the levels | each [0, 255] | output codes per row and level (the identity map by default) |
| | `bodyToneChromaGains` | [1, 1, 1] | each [0, 3] | W41 G1's E3-form gains at encoded luma 63, 93, 118 |
| | `bodyToneChromaScale` | 1 | [0, 3] | the one per-endpoint scale (`candidate2Chroma`, Decision Log 5c) |

The declared constants — the radii 5 and 8, t = clamp((s − 64)/96, 0, 1), the o laws, the margins,
the floor 0.4·f device px, the texel rule f = 4 on w ≥ 280 and h ≥ 160 (`geometry.py`
`backdrop_texel_dev`), the 20 pt band — are one exported constant in the new `body-law.ts`, pinned
by a test to the instrument's values (§6). They are not leaves: the declaration fixes them, and
none is fitted. If step 2 frees one (a W-shape margin, a free σn), it becomes a gated leaf then.

`validateBodyLawPatch` joins `validateBodyE3Patch` at the patch boundary (`material.ts:2204–2228`,
called at `material.ts:3718`), with the ranges above, dense fixed-length tuples, strict ordering of
the table's axes and the discrete sets checked by membership.

### 1.2 Why at identity every document draws today's bytes

- **Digests.** None of the six documents names a new key, so each resolves every new leaf at its
  default, every gate at its identity, and `materialDigestDroppedLeaves` (`material.ts:3415–3425`)
  drops all five entries: `materialDigestInput` is the object it is today and the frozen macOS 26.5
  pair (`b2b570e4adcea8fb` / `874be66ea501621b`) and the four macOS 27 digests (`be13dae45098fc89`,
  `2a4323f33df8d799`, `b0d0d8dacc6a03af`, `7c454858a3cbad5b`) are unmoved. E3 landed the same way
  (`w41-body-e3.test.ts` "drops the whole zero-gate group").
- **Pixels.** At `bodyLawStrength` 0 the renderer encodes no law pass, binds the placeholder view
  in the new slot (the `heavy2` precedent, `passes.ts:1017–1021`), writes zero into the appended
  uniform lanes, and the optics pass takes an early return before any law arithmetic (E3's
  precedent, `wgsl/optics.ts:339`). The shipped expression is not edited: every W42 branch is a
  new function called after `body_e3_composite` (`wgsl/optics.ts:1372`). T2 is read only
  through the law and F only through E3, whose own gate is 0 in every document, so both are doubly
  inert.
- **D1 and D2 as plain value drops.** The declaration's `supersededLeaves` and X36 name D1 and D2
  as their own identity-table entries whose identity draws what ships. They are that here: each
  identity is the shipped convention (device-px widths, linear-light averaging), a plain value
  drop is injective for free (`material.ts:3246–3254`), and the frozen pair never leaves it. They
  differ from the charter's picture in one way, which is Fork 1: they are read only by the law's
  own pass, so neither can move a pixel while the law's gate is at its identity, and a document
  that turns the law on must set both explicitly (LT is D1 = 1, D2 = 1; a law at D1 = 0, D2 = 0 is
  the rejected F2 in device px). G2's candidate-document writer asserts both.

Each entry's `inertLawCase` names the unit case of §6 that sweeps its gated leaves with the gate
held and proves the digest input unchanged, and `w31-identity-table.test.ts` gains five lines in
`IDENTITIES` (`w31-identity-table.test.ts:120–128`), appended, none edited.

### 1.3 What the candidate documents set (scratch, G2 steps 4–5)

| candidate | endpoint | sets |
| --- | --- | --- |
| 1 | light active, dark active, dark receded | A on (k, λ, hinge, pose, knee from step 2), D1 by the 1x cells, D2 = 1 |
| 1 | light receded | the above, plus `bodyE3Strength` 1 with W41's `bodyE3Neutral` and G1's light-receded `bodyE3Gains`, and F on with family A's seven ordinates |
| 2 | all four | A, D1, D2 as candidate 1; T2 on with the table, W41 G1's endpoint gains and the fitted scale; `bodyE3Strength` 0 |

A partial-endpoint adoption (Decision Log 3) leaves the unclaimed documents with every W42 gate at
its identity, which is the state they are in today.

### 1.4 Where the superseded leaves sit when the law is on

The leaves the declaration names as superseded — the linear pyramid's share (`sizeScatter*`),
`sizeHeavyTapSigma`/`2x`, the second heavy tap, the dark `scatterLod` path
(`wgsl/optics.ts:1052`), the scatter's spatial-scale conditioning, `collapseTransmission`/`2x`'s
group/local mix — **stay in the documents at their shipped values and stay live** in two places:

- the active pose's band, where the body is mix(shipped, law, smoothstep(0, 20 pt, depth))
  (Decision Log 5e; the rehearsal's `swap_weight`, `swap.py:293–304`), so the lens, the ramp and
  the heavy share still shape the outer 20 pt;
- every group the law stands down for (§4), and the unsampled and DOM paths.

They are **unread wherever the law's weight is 1**: the whole receded body and the active body
deeper than 20 pt. Neither the candidate documents nor this step moves them; whether a sealed
document drops any of them is G3's question, and the answer is no while the band reads them. The
tone solve's own leaves (`backdropTone*`, the black branch, `tintAlpha`, `sizeOcclusionGain`,
`bodyChromaRetention`) are not superseded under candidate 1 — they are its T — and are unread
inside the law's weight under candidate 2 and under E3.

## 2. The WebGPU computation

### 2.1 Where it runs

A new stage in `drawGroups`, after the field pass (`renderer.ts:1058`) and the silhouette tone
(`renderer.ts:1066–1083`) and before the optics pass (`renderer.ts:1143`), encoded only when the
policy-folded `bodyLawStrength` is above 0 and the group samples a pyramid (a `gpu-texture`
source). Three new files: `body-law.ts` (pure: the declared constants, the per-surface plan, the
policy fold, validation and the CPU references the tests read), `body-law-pass.ts` (the GPU stage,
on the silhouette tone pass's model of per-group resources and a geometry-and-epoch cache,
`silhouette-tone.ts:92–157`) and `wgsl/body-law.ts`. The stage's output is one group-local texture
**A** (rgba16float, the group's device rect at one texel per device pixel): rgb is the law's
argument in encoded values, a is L(W), the wide term's encoded luma, which E3's gain reads (§2.8).

The per-source pyramid (`pyramid.ts:21–25`) is not the right host, for the law's own reasons:
LT's support is per surface (box plus a span-graded margin, with the edge mode by pose), σn is
per surface and per pixel, and the floor is per surface (1.6 device px on rrect-lg). The charter's
tie-break already prices this (`renderer.ts:633–638`'s per-source sharing is lost).

### 2.2 The per-surface plan (CPU, `body-law.ts`)

For each surface of the group, from the resolved surface the field pass also packs:

- s = min(w, h) CSS px, t = clamp((s − 64)/96, 0, 1); f = 4 if w ≥ 280 and h ≥ 160 else 2
  (a named gap between rrect-ml and rrect-lg, charter Risks); σ_F = 0.4·f device px.
- The unit multiplier u (device px per width unit) from D1: dpr, 1 or f.
- R_fp: the device pixels whose centres lie in the shape's box, grown by round(m·dpr) with
  m = 0.35 s if s > 64 else 16 pt when active and m = 1 device px when receded, then intersected
  with the source's extent on the plane (the cover fit or the placement). That is `forward.py`'s
  `Cell.crop('box')` (`forward.py:156–171`) with the canvas replaced by the source's extent; at the
  canonical bed they coincide.
- Edge mode: clamp-to-edge active, normalised receded, swapped by `bodyLawEdgeSwap`.
- σw = k_w·8·u. σn: receded, one width k_n·5·(0.4 + 0.4t)·u; active with t > 0, four levels
  uniform in σ over k_n·5·[0.4t, 0.8t]·u plus a contour level at k_n·5·0.5·u where 0.5 > 0.8t
  (t < 0.625, spans under 124); active with t = 0, none (C = S).
- The decimation factor per width (§2.4): direct below 6 device px, q = 2 below 48, q = 4 above.

The o law is the rehearsal's `np.interp(d, [−s/2, −1, 0], [0.8t, 0.4t, 0.5])` held at 0.5
outside (`body.py:670`); `forward.py:85–86` holds 1 beyond d = 1e-6, which differs only where the
band weight is 0 (active) and where the receded law is flat anyway. The receded law is flat
everywhere (`body.py:672`).

### 2.3 S: the capture and its floor

The declared half-resolution capture is built the way the law models it: memo C's Gaussian floor
on the device grid, before the knee (declaration `law`; `forward.py:7–9`), not a literal
half-resolution texture. The literal box decimation is the descriptive null the 1x cells read
(declaration `rejectedNulls`), so building it would render the null rather than the law.

**Capture pass.** One draw per surface into its S tile (R_fp at one texel per device pixel,
rgba16float). At each device-pixel centre it loads chain level 0's four neighbours, un-premultiplies
each, encodes each (D2 = 1) and interpolates the encoded values bilinearly: the silhouette tone
pass's order, whose note says why (`wgsl/silhouette-tone.ts:4–7`, `52–62`: encoding after the
filter is a Jensen gap). On the canonical and bed sources the chain's level 0 is the device grid,
so the load is exact. Alpha is written 1: it is the normalised mode's weight channel (§2.5).

**Floor.** One separable pair at σ_F with clamp to the tile: memo C's floor, applied before the
knee as declared, at full resolution. It is not folded into the later widths: C = S exactly at
t = 0 is the most common active case, and the floor is two small passes (7 or 13 taps).

A source whose level 0 is not the device grid (a placed or cover-fit image denser or sparser than
the display) is a named gap: sampling level 0 at device-pixel centres aliases a minified source,
and sampling the chain at the matching lod encodes after a linear prefilter. The canonical bed and
the new bed are one texel per device pixel, so neither reading moves a measured cell.

### 2.4 C: the narrow term, and what it costs against the exact Gaussian

The receded narrow width is one number per surface, so it is one level and exact up to the
decimation and the tile format. The active width varies per pixel, σn(d) = k_n·5·o(s, d)·u, on
every surface with t > 0; the rest of this section is about that case.

**Measured** (`implementation-design/narrow_error.py`, output `narrow_error.txt`): every strategy
against an exact per-pixel Gaussian at the pixel's own σ (a direct sum with ndimage's truncation
and clamp), on 48 active cells — checkerboard pitches 8, 16 and 64, hc-text, the synthetic photo
and the impulse grid, on rrect-80, rrect-md, rrect-ml and rrect-lg, at 1x and 2x, light and dark,
at memo E's k and memo C's λ — sampling 700 pixels in the 20 pt band and 700 on the deep mask per
cell. Errors are in codes. "C" is the narrow term's encoded value (× 255); "y" is the output
through LT and memo C's native-T stand-in; "band-weighted" multiplies each pixel's error by
Decision Log 5e's weight smoothstep(0, 20 pt, depth), which is how much of it reaches the render.

| strategy (direct blurs, float64) | C deep max | C band-weighted max | y deep max | y band-weighted max |
| --- | --- | --- | --- | --- |
| mip chain, trilinear at lod log2(2σ) ("interpolate pyramid levels") | 62.2 | 62.2 | 13.2 | 13.2 |
| one separable pair at the pixel's own σ, no levels | 4.34 | 4.34 | 1.07 | 1.07 |
| 3 levels, linear in σ | 3.31 | 5.62 | 0.85 | 1.37 |
| 4 levels, linear in σ | 2.04 | 2.25 | 0.49 | 0.51 |
| 6 levels, linear in σ | 0.73 | 0.92 | 0.18 | 0.21 |
| 8 levels, linear in σ | 0.37 | 0.42 | 0.09 | 0.10 |
| 6 levels, variance-matched weight | 0.93 | 1.23 | 0.22 | 0.28 |
| 4 levels, quadratic in σ through the 3 nearest (light only) | 0.53 | 0.96 | 0.12 | 0.21 |
| **4 levels, cubic in σ through the 4 nearest** (light only) | **0.40** | **0.46** | **0.09** | **0.10** |
| 6 levels, cubic in σ (light only) | 0.04 | 0.04 | 0.01 | 0.01 |

(The rows marked light only are `narrow_interp.py`'s, on the same cells and samples in the light
scheme; the rest are `narrow_error.py`'s over both schemes.) Four readings decide it. Interpolating
a mip chain is out by two orders of magnitude: a box pyramid is not a Gaussian at any lod. One pair
of passes at a per-pixel σ misses by a code, because the horizontal pass has run at the
neighbours' σ before the vertical pass reads it. Weighting two levels to match the pixel's
variance is worse than weighting linearly in σ: the error sits at the pattern's fundamental, where
the attenuation is exp(−ω²σ²/2), and linear-in-σ tracks that better than the second moment does.
And the response is smooth enough in σ that the order of the interpolation buys more than the
number of levels: a cubic through four levels beats linear through six by half, and costs two more
reads per pixel in the composite, not two more blurs. The worst cells are the pitch-8 and pitch-16
checkers on rrect-ml and rrect-lg; the photo stays under 0.02 code.

**Chosen: four interior levels uniform in σ plus the contour level, a cubic in σ through the
four nearest levels (clamped to [0, 1]), every width at or above 6 device px decimated (q = 2
below 48 device px, 4 above), float16 at every stored pass.** Measured as a whole
(`narrow_interp.txt`, `chosen`) on the 96 active cells, both schemes: **y 0.115 code on the deep
mask and 0.127 code band-weighted at worst (band-weighted rms 0.025); C 0.47 encoded codes on the
deep mask and 0.57 band-weighted.** The receded single level at the same rule reads 0.096 code
over the whole body (`narrow_error.txt`, float16 with σ_q 6), all of it from the decimation and
the tile format (0.055 and 0.032 alone, exactly 0 with neither). The worst cell is a quarter of
the 0.5-code repeat floor, so the shader's own arithmetic cannot move a region statistic by a
resolvable amount, and the shader-against-oracle test of §6 can hold it to about 0.13 code plus
the output's rounding. The first proposal, six linear levels decimated from 12 device px as
`forward.py` decimates, reads 0.181 / 0.211 (`lin6-q12`), with two more blurs.

The levels are blurred in shared-tap multi-target passes in groups of **four**: the device is
requested with default limits (`platform-web/src/webgpu.ts:120`), whose
`maxColorAttachmentBytesPerSample` of 32 admits four rgba16float targets. rrect-ml and rrect-lg
(t ≥ 0.625) need no contour level, so their four levels are one group; smaller spans add the
contour level, which is decimated where the interior levels are not, so the groups also split by
resolution.

### 2.5 W: the wide term

σw = k_w·8 pt is about 16.8 pt: 33 device px at 2x. W is computed the way the oracle computes it,
`forward.py`'s `_blur_decimated` (`forward.py:246–271`): pad the tile by the kernel's reach at full
resolution (edge replication for clamp, zeros for normalised), average q × q blocks (q = 2 below 48
device px, 4 above; one bilinear tap per block at q = 2), blur at the reduced width
σd = √(σ² − (q² − 1)/12 − q²/6)/q, and return bilinearly. The instrument measured this at ≤ 0.037
code of the direct filter on the whole bed (`instrument/README.md:66–67`); here W's encoded value
sits within 0.060 code of the exact Gaussian (0.119 with float16 tiles) over the 72 receded cells,
and its share of the active output error is inside §2.4's figures.

**The normalised edge rides the alpha channel.** Every tile stores rgba with a = 1 inside R_fp and
0 in the zero padding; the blur passes filter all four channels, and a read divides rgb by a. That
is `forward.py`'s num/den (`forward.py:240–243`, `269–271`) in one texture, and the clamp mode is
the same pass with the taps clamped to the tile and a identically 1.

### 2.6 The composite pass: the knee and M

One render pass per group into A, one draw per surface, each over its own R_fp ∩ the group rect.
A fragment of surface i computes the analytic circular-corner SDF d_i of every law surface of the
group (a storage buffer of shapes, the silhouette tone's `packToneShapes` convention,
`silhouette-tone.ts:26–37`) and discards unless d_i is the smallest: the rehearsal's owner rule
(`body.py:140`, `np.argmin(ds)`). The toolbar's three capsules, whose active R_fp overlap, each
read their own tile. Then, in f32 with exact manual bilinear reads of the decimated tiles:

- σ = σn(d_i) by the o law; C by the cubic in σ through the four nearest levels, clamped to
  [0, 1] (§2.4).
- W from its tile; with D2 = 0 both are decoded back to linear first (the rejected F2 at identity).
- The knee by `bodyLawKnee`, with h = `bodyLawHinge`: per channel N = C + h·λ·max(0, h·(W − C));
  on luma the hinge is decided on h·(L(W) − L(C)) and applied to the whole colour
  (`forward.py:497–501`); with W's chroma, A = M_L + (W − L(W)) (`body.py:713`).
- M = (1 − w)·N + w·W with w = `bodyLawNormal`; A.rgb = M (encoded), A.a = L(W).

A is written for every owned pixel with d_i up to one device pixel outside the contour, so the
coverage ramp and a bilinear read at a pixel centre only ever meet written texels.

Uniform invariance holds by construction (`forward.py:20–23`): every blur and every normalisation
maps a constant to itself and the hinge reads max(0, 0), so on a uniform backdrop A = the
backdrop's encoded colour to within the tile format, which is clause 7's premise.

### 2.7 In the optics pass

A new function `body_law_composite`, called immediately after `body_e3_composite`
(`wgsl/optics.ts:1372`) and before the author tint reads the body (`materialColour`,
`wgsl/optics.ts:1463`), returns at once when `bodyLaw.x ≤ 0`. Otherwise:

- **Refraction after the blur.** A is sampled bilinearly at the pixel's refracted position mapped
  into the group rect (the displacement `wgsl/optics.ts:1020–1021`, with the rect origin in a new
  uniform lane). That is the rehearsal's order: the law's maps are computed on the unrefracted
  plane and resampled by the lens (`swap.py:215`, `226`), which is also the declared primary
  refraction order (declaration `refractionOrder`).
- **The band.** weight = strength × (active ? smoothstep(0, 20 pt, −d) : 1), with d the field's
  own distance (`wgsl/optics.ts:771`), so the coverage ramp stays the output composite's.
- **The tone** by precedence: T2 if its strength > 0 (§2.9), else E3 if `bodyE3Strength` > 0
  (§2.8), else the landed solve (§2.8); each returns a linear colour. A fractional T2 strength
  mixes toward the table in linear light.
- **Presence and replacement.** target = mix(backdrop, law body, mat) and
  colour = mix(colour, target, weight): E3's own convention for a fractional presence
  (`wgsl/optics.ts:338–343`), an unmeasured interpolation recorded as such.

It sits before the author tint because the rehearsal swapped the untinted body and applied the
tint's fitted transfer after it (`swap.py:325–327`).

### 2.8 T for candidate 1

**The landed solve per pixel** (light active, dark active, dark receded). The rehearsal's
`landed_T` (`body.py:504–537`) tones each pixel as the shipped material tones a uniform backdrop
of colour A(x). In the shader that is a new function `landed_tone(A)` that re-executes, with
per-pixel inputs, the solve at `wgsl/optics.ts:1165–1262`, the collapse target at `1292–1303`, the
composite at `1318–1319` and the retention at `1369`:

- toneColour.rgb = dec(A) and toneLinearMean = L(dec(A)); the abscissa by
  `backdropToneAbscissa`: silhouette → level = dec(L_enc(A)), source → level = L_lin(dec(A))
  (`body.py:515`); the "backdrop" of the composite and of the retention is dec(A), so the
  collapse's target is dec(A) whatever `collapseTransmission` holds;
- the tone strength is `backdropToneUnderPolicy(policy)·backdropToneMax` (`material.ts:4123–4128`)
  **without** the "no measured tone" gate of `renderer.ts:1121–1128`, since the argument is always
  measured; this takes one new lane;
- sizeK, the fold, `toneLevelFar` and the neutral are the pixel's and the group's as the shipped
  path computes them (`wgsl/optics.ts:868–874`, `959`, `1135`); the macOS 27 documents' adaptive
  poles equal their tints, which is why the rehearsal's resolved `tint` (`resolved.json`) is the
  same neutral.

It is a **duplicate** of the shipped lines rather than a refactor of them into a shared function,
so the shipped expression is textually untouched until the goldens can be read on a GPU; a
structural test pins the duplicate to the original line by line, the way
`w31-body-chroma.test.ts:196–226` pins the retention. W36's black branch is carried as it is, so
the per-pixel response keeps its non-monotone dip below encoded 0.003; the rehearsal's
`mono_black` was a device, not a declaration (`body.py:507–509`), and is not built.

**Light receded: E3 with the law's argument and the F extension.** `body_e3_codes`
(`wgsl/optics.ts:320–332`) gains two inputs rather than a copy: the gain's argument and the chroma
vector. Under the law, level = L(A), chroma = A − L(A), gain at L(W) = A.a; F above 150 follows
the extension when `bodyE3HighStrength` > 0, interpolating (150, n₆), (160, h₀) … (255, h₆) and
mixing from today's continued segment (`wgsl/optics.ts:314–317`) by the strength. With A − L(A)
the per-channel form carries M_rgb's own chroma, as `kneeForms` declares and the rehearsal's
per-channel candidate 1 did (`swap.py:231–234`); under knee form 2 it is exactly v(W), the
declaration's literal `g(L(W))·v(W)` (Fork 5). Without the law, E3 still reads the sampled
backdrop as W41 shipped it, and its own fold still governs it (§4).

### 2.9 T for candidate 2

`law_table_codes(A, span)`: level = L(A); for each of the two span rows bracketing the pixel's
span (clamped to the first and last rows), the piecewise-linear value at the level over
`bodyToneTableLevels` (held at the ends); linear in span between the rows; then
y = clamp(f + scale·g(level)·(A − level), 0, 255) with g the E3-form gain over the knots 63, 93,
118 and E3's clipping order (F clipped, chroma added, channels clipped; `material.ts:2119–2152`).
The span is `aux.z`, the field's per-pixel span (`wgsl/field.ts:360`). How a span between strata
and a sparse stratum (three or four ordinates at 128, 160 and dark 80) read native T is fixed
before family A is read by the pre-read addendum (`native-t-addendum.md`; §9, Fork 3): the grid is
that rule sampled at its knots, and the shader's bilinear read reproduces it exactly.

### 2.10 Cost

**Passes per law surface per rebuild**: capture 1, floor 2, decimate 1, W 2, C 2 or 4 (one
multi-target pair per group of four levels of one resolution; the receded single level one pair),
composite 1 draw: nine to eleven passes, plus the A pass per group. Rebuilt only when the source's
built epoch, the fit or placement, the dpr, the surfaces' rects or spans or the law's leaves
change (the silhouette tone's cache, `silhouette-tone.ts:141–157`); under PR #2's demand-driven
frames a static page rebuilds nothing.

**Texture fetches**, 2x rrect-lg active (R_fp clipped to the 640 × 400 canvas, 256 k pixels): the
floor about 4 M, W about 9 M at q = 2 with paired bilinear taps, the four levels about 20 M at
q = 2 (the horizontal taps shared, the vertical ones per level), the composite about 3 M: of the
order of 35 M fetches, against the shipped body's one separable pair on one chain level per
source. On an Apple M-class GPU that is of the order of 1 ms per rebuild for the largest surface
and a few tenths of a millisecond for rrect-md, an estimate and not a reading. The tie-break
priced it and G3 reads the bench; the W26 row (+1.1 ms for an in-shader 9 × 9 grid,
`wgsl/optics.ts:1075–1076`) is the precedent for measuring rather than guessing. The optics pass
adds one bilinear fetch of A and ALU for the tone.

**Memory per law surface**, rgba16float, at peak: S and one scratch at R_fp, the levels'
horizontal and vertical halves at R_fp or R_fp/q², W at R_fp/q², and A per group at the group
rect: about 8–12 MB for a 2x rrect-md or rrect-lg in the active pose (rrect-md's levels are below
6 device px and so full resolution), pooled by group and surface keys and released on `forget`, as
`tone-field:` is (`silhouette-tone.ts:114–118`). A level-at-a-time schedule halves the peak at
twice the passes; the bench chooses.

**Uniforms and bindings.** The optics uniform grows from 152 floats (`passes.ts:786`) by appended
vec4s only, no older lane changing owner (the rule at `passes.ts:971–977`): the law (strength,
band flag, rect origin, tone strength, T2 strength) in two vec4s, the F extension in two, the
table in eighteen (11 levels, 5 spans, 55 codes, 3 gains, the scale). One new texture binding, 12,
for A.

## 3. The shipped operators that read a blurred backdrop

| operator | today | once C, W and M exist |
| --- | --- | --- |
| body chroma retention (`wgsl/optics.ts:711–724`, `1369`) | toward the shipped blurred backdrop | candidate 1: inside `landed_tone`, toward dec(A) at the solve's luma, as the rehearsal reads it (`body.py:390–418` with `bt = c`); E3 and candidate 2: not applied, g carries chroma; the band's shipped share: unchanged |
| the scatter's spatial-scale statistic (`wgsl/optics.ts:976–980`) | conditions `kScatter`, the linear share | conditions only the band's shipped share; unread at weight 1. The analysis pass still computes it for that share and for the readout |
| `collapseTransmission` (`wgsl/optics.ts:1292–1295`) | lerps the collapse target toward the blurred backdrop | candidate 1: its target is mix(dec A, dec A, ·) = dec A, inert by construction; E3 and candidate 2: unused; the band's shipped share: unchanged |
| the silhouette local tone (`renderer.ts:1066–1083`) | the group solve's receded abscissa | superseded inside the law's weight by the per-pixel abscissa; still drawn for the band, the readout (`backdropToneAbscissae`) and stood-down groups |
| the lens (`wgsl/optics.ts:990–1023`) | samples the shipped body at the refracted uv | also samples A there (§2.7); unchanged otherwise |
| presence (`wgsl/optics.ts:1126–1129`) | lerps toward chain level 0 | the law's body follows E3's convention toward the presence-mixed backdrop |
| the outer shadow's lift (`wgsl/optics.ts:611`) | reads a chain level | unchanged; its amplitude is 0 in all four macOS 27 documents (W33) |

## 4. Accessibility

`bodyLawStrengthUnderPolicy(strength, policy, variant, sampled)` in `body-law.ts`, an exhaustive
switch on the occlusion axis on the model of `bodyChromaRetentionUnderPolicy`
(`material.ts:2105–2116`): `nominal` returns the strength where the group is sampled and the
variant is regular (Fork 4), `increased` and `opaque` return 0. The declaration's three sentences
map onto core's rows (`accessibility.ts:233–260`):

- **Reduce Transparency** sets occlusion `increased`, so the law's strength is 0; T2 is read
  only through the law and F only through E3, whose own fold is 0 there too, so every W42 gate is
  at its identity. The shipped RT path draws.
- **`forced-colors`** sets glass `none` and occlusion `opaque`: 0 again, and the renderer draws no
  sampled body at all (`renderer.ts:1180–1192`).
- **Increase Contrast alone** touches border, foreground and ambient tint, not occlusion, so the
  law keeps its strength.

The fold is applied once in `renderer.ts`, beside the retention's and E3's
(`renderer.ts:1292–1300`), and its result both gates the stage's encoding and fills the uniform.
**E3 under the law takes this fold, not its own**: `bodyE3StrengthUnderPolicy`
(`material.ts:2190–2201`) stands E3 down under Increase Contrast alone, which would leave light
receded's candidate 1 with the law over the shipped solve, the fallback the parent struck
(declaration `candidate1`, rulings). So the law path reads E3 through a lane of its own,
`bodyE3Strength × (folded law strength > 0)`, and `bodyE3.x` keeps E3's own fold for the W41 path.
The CSS tier applies the same function.

## 5. The CSS tier

What is implemented now, behind the same gates, is everything that is arithmetic and DOM
construction; nothing is measured, and nothing a page draws moves at identity
(`w30-css-declaration-identity.test.ts` compares every declaration against bytes recorded before
any W30 leaf existed).

- **The derivation** in `platform-web/src/optics.ts`: `cssTierBodyLaw(material, spanPx, dpr)`
  returns the law's CSS parameters from the same leaves — σw, one σn (the receded value exactly;
  active, one width standing for the depth-graded term, which Decision Log 4 measures: the
  proposal is the band-weighted mean of σn over the body), λ, w, the hinge, the floor folded into
  both widths as √(σ² + (0.4 f/dpr)²) CSS px, and the tone as tables. Every new leaf gets its line
  in `tier-coherence.test.ts`'s exhaustive `CSS_COUNTERPART` (`tier-coherence.test.ts:3222–3257`).
- **The primary route**, one reference filter inside L1's `backdrop-filter` on an engine whose
  row says `referenceFilterInBackdrop` (`css-tier.ts:479–489`): at
  `color-interpolation-filters="sRGB"`, `feGaussianBlur in="SourceGraphic"` twice (C and W),
  `feBlend mode="lighten"` (dark `darken`) of W over C, then `feComposite operator="arithmetic"`
  with k2 = λ, k3 = 1 − λ (N) and again with k2 = 1 − w, k3 = w (M), then T. T is a luma matrix,
  an `feComponentTransfer` table of T(L) and the chroma rebuilt by two arithmetic composites with
  a 0.5 offset (every intermediate stays in [0, 1], because each primitive clamps): exact in form
  for candidate 2 and E3, and for candidate 1's landed solve an approximation whose chroma gain is
  read off the solve, which Decision Log 4 measures. The filter
  builder is a new `CssTierFilterSpec` kind beside today's (`css-tier-layers.ts:432–437`,
  `498–564`); L2 is `display: none` under the law; L3 keeps the rim, glow, shadow and author tint
  and drops the plate, which T already contains.
- **The receded normalised edge comes free** in that route: with `edgeMode="none"` the blurred
  alpha is the normalisation and the un-premultiply at the next primitive divides by it, as the
  rgba tiles of §2.5 do. **The active clamp at R_fp** needs L1 outset by the margin and masked back
  to the shape, which is a Chromium measurement.
- **The stacked approximation** for engines with no reference filter: L1 `blur(σn)`, L2
  `blur(√(σw² − σn²))` over L1's output with `mix-blend-mode: lighten` (dark `darken`) at opacity λ
  — exactly N, because a lighten at opacity λ over C is (1 − λ)C + λ max(C, W) — then the Normal
  fill cannot read W again (a later layer's backdrop is N), so it is approximated by one more
  layer, and T by W41's affine route (`78c4b854`, re-derived as W41 Deferred at close 5 lists).
- **What needs Decision Log 4's Chromium proof after the sitting**: whether Skia's
  `feGaussianBlur` is Gaussian enough at these widths, whether `edgeMode` is honoured inside
  `backdrop-filter`, the eight-bit intermediates of a seven-primitive chain (the tint route
  already met them, `core/src/state.ts:96–103`), the outset-and-mask support, the
  single σn against the graded term, and the stacked route's error. Until it is read, a new
  engine row `bodyLawFilterInBackdrop: "unverified"` keeps the law off on this tier whatever the
  document says (the fail-closed rule `maskOnBackdropFilter` already follows,
  `css-tier.ts:2241–2250`), and `GlassGroupState` says so.

**The readout.** The honesty core gains `bodyLaw?: "drawn" | "stood-down"` on `GlassGroupState`
(`core/src/state.ts:64–148`), resolved where the fold is, and a CSS twin beside `cssBody`, so a
capture cell records whether the law drew.

## 6. The test plan

**Now, with no GPU** (unit suites and the evidence root; nothing launches a browser):

1. *Identity and digests* (`renderer-webgpu/test/w42-body-law.test.ts`): each entry drops its whole
   group at identity while its gated leaves are swept (E3's case, `w41-body-e3.test.ts`); each
   gate off its identity discriminates; the six documents' recomputed digests equal their recorded
   ones; `w31-identity-table.test.ts` gains its five literals; `withMaterialOverrides` rejects every
   malformed patch even behind gate zero.
2. *The plan against the oracle*: a committed fixture generated by a script in this evidence root
   from `geometry.py` and `forward.py` — R_fp windows, f, σ_F, σw, σn and the level set, the band
   and deep masks — for every canonical and bed shape at dpr 1 and 2, all three units; the vitest
   reads it and compares `bodyLawSurfacePlan` exactly.
3. *The CPU references against the rehearsal*: `landedToneCpu(A)` against `body.py`'s `landed_T`
   on a colour grid per endpoint and span, from `resolved.json`, and equal to the shipped CPU
   mirror of a uniform backdrop (clause 7 by construction); the E3 extension and the table
   against numpy; the composite algebra (three knee forms, both hinges, both spaces) against
   `forward.py`'s `_hinge` and `compose` on random vectors.
4. *Packing and encoding* with the fake GPU (`test/harness/fake-gpu.ts`; the E3 pattern,
   `w41-e3-uniform.test.ts`): at identity no law pass label is encoded, the optics uniform's first
   152 floats are unchanged and the appended lanes zero, the placeholder is bound; on, the stage
   encodes the expected passes per surface with textures sized to the plan, and the fold's cases
   (RT, forced colours, IC alone, clear variant, unsampled, DOM) set the lanes as §4 says.
5. *WGSL structure*: the gate's early return is the first statement; `landed_tone` matches the
   shipped lines term for term; the transcendentals pass `w31-wgsl-range.test.ts`'s scan; the
   binding and the lanes are where §2.10 puts them.
6. *The realisation's error* (this note's §2.4, committed and re-runnable): a numpy mirror of the
   chosen passes (levels, decimation, float16 at every stored pass) against the exact Gaussians.
7. *The CSS tier*: the derivation pinned by `tier-coherence.test.ts`; the filter builder's DOM in
   jsdom; the declaration identity test untouched and green.

**After the sitting, on a GPU:**

1. `pnpm --filter @vitrea/renderer-webgpu test:golden` byte-identical at identity, the isolation
   hashes unmoved, and the `e2e/gpu` suites green; then the runtime-base proof (clause 8) as G2's
   step 1 already requires.
2. A wgpu compute proof of the WGSL functions (the composite, `landed_tone`, the table, the E3
   extension) against numpy on synthetic inputs, W41's `e3-gpu-proof.py` pattern.
3. Rendered agreement: the calibration page renders web-plannable bed cells (synthetic
   backdrops, `bed/web-plan.json`) with the law on at fixed k and λ and candidate 2's table set to
   a known `TableT` (memo C's stand-in), so `forward.py` composed with that same T is the
   prediction; the captures agree within the §2.4 budget plus the output's rounding. Candidate 1's
   landed T is compared the same way against the rehearsal's `landed_T` composition. ON draws
   differently from OFF; clause 7's uniform invariance holds on rendered cells.
4. The bench beside the goldens (G3 reads it).

## 7. The work breakdown

In order; units that touch the same files are marked.

| unit | owns | files | depends on |
| --- | --- | --- | --- |
| U1 | leaves, validation, the five table entries, the fold, `body-law.ts`'s constants and CPU references, tests 1–3 | `material.ts`, new `body-law.ts`, `index.ts` exports, `w31-identity-table.test.ts`, new tests | — |
| U2 | the oracle fixtures for tests 2–3 and the realisation mirror (test 6) | this evidence root | — (parallel to U1) |
| U3 | the GPU stage: capture, floor, decimate, blurs, composite, A; the cache | new `body-law-pass.ts`, `wgsl/body-law.ts`, `wgsl/index.ts`, `renderer.ts` (drawGroups) | U1 |
| U4 | the optics integration: `body_law_composite`, `landed_tone`, E3's two inputs and extension, the table, the lanes and binding 12; tests 4–5 | `wgsl/optics.ts`, `passes.ts`, `renderer.ts` (the pack site) | U1, U3 (**shares `renderer.ts` with U3**: one worker, or U4 after U3 merges) |
| U5 | the CSS tier: derivation, filter builder, gating, `CSS_COUNTERPART` lines, test 7 | `platform-web/src/optics.ts`, `css-tier.ts`, `css-tier-layers.ts`, `root.ts`, `calibration/test/tier-coherence.test.ts` | U1 |
| U6 | the readout | `core/src/state.ts`, the platform's fold | U4, U5 |
| U7 | after the sitting: goldens, compute proof, rendered agreement, bench | e2e only | U3, U4 |

**Size**: about 3,000–4,000 lines with tests — U1 about 700, U3 about 1,100 (400 of WGSL), U4
about 600, U5 about 700, U2 about 300 of Python and fixtures, U6 about 100. For workers, U1 and U2
in parallel, then U3+U4 as one owner, U5 in parallel with them, U6 last: two to three waves of
work before U7 can run.

## 8. Forks

Each is a question the charter and the declaration leave open, with the option this design takes.

1. **Where D1 and D2 act.** (a, taken) Inside the law only, as plain value drops whose identity is
   the shipped convention: nothing the band or a stood-down group draws moves, and the law's unit
   stays open for the 1x cells. (b) As gated leaves of the law's group with LT's values as
   defaults: fewer entries and no way to turn the law on in device px by omission, but not the
   declaration's letter ("each a gate-group"). (c) On the shipped per-source pyramid at the
   charter's cited sites: moves the band, the lens, presence and every stood-down group, none of
   it rehearsed, and still cannot give LT its per-surface support. (b) becomes the better pick if
   the parent reads X36 as satisfied by the law's own gate.
2. **Which rivals are built now.** Taken: LT plus the declared discrete choices that need no new
   operator (LT-2k's second k, the three knee forms, the three units, the edge swap). A survivor
   that needs an operator (W-shape, W-tails, K2, free σn, R1, the bleed, C-linear) is built after
   step 2 names it, in the same stage.
3. **Candidate 2's T between strata.** Taken: a fixed 5 × 11 grid, linear in span between rows,
   clamped outside 64–160, luma only, with the completion of sparse strata as step 2's recorded
   output. Open alongside it: per-channel ordinates, if family A's greys read non-neutral beyond
   the bar; and a row at 104, where dark MaxLuma's knee sits between the 96 and 128 strata, which
   no bed cell reads.
4. **The law on variants other than regular.** Taken: stood down (identity) on every other
   variant, as E3 is (`material.ts:2196`); the bed measured regular only. The alternative applies
   the law to the clear variant unmeasured.
5. **Candidate 1's light-receded chroma vector.** Taken: A − L(A) with g at L(W), which is
   M_rgb's chroma under the carried per-channel knee (`kneeForms`: "per-channel (N and M per
   channel, chroma argument M_rgb)"; the rehearsal's per-channel candidate 1 followed it) and
   exactly v(W) under knee form 2. The literal reading, v(W) under every knee, would give the
   per-channel knee W's chroma and not its own.
6. **E3's fold under the law** (§4). Taken: the law's (Increase Contrast alone keeps E3 in the
   light-receded candidate), because the declaration says Increase Contrast alone does not stand
   the law down and E3 is part of that candidate's T. The alternative keeps E3's own fold and
   draws the struck fallback under Increase Contrast.

## 9. Rulings (the parent, 2026-09-30)

The parent read this design at `67e9d784` and accepted all six forks, one on a condition
(verbatim in `implementation-design-rulings.md`).

1. **Fork 1, ACCEPTED as (a).** D1 and D2 act inside the law only, as plain value drops whose
   identity is the shipped convention. That matches the rehearsal, where the band's shipped share
   is the shipped path.
2. **Fork 2, ACCEPTED.** LT is built with the declared discrete choices that need no new operator.
   A survivor that needs one is built after step 2 names it.
3. **Fork 3, ACCEPTED ON A CONDITION**: candidate 2's rules between spans and for a sparse stratum
   must be what the declared path uses, and where it is silent a pre-read addendum states them
   before family A is read, with no free parameter, through every measured ordinate, monotone,
   reducing to the full row where no residual exists, and with the s = 112 reading explicit; no 104
   row. **Outcome: the declared path is silent on both** (the instrument's `tone.py:8–9` says only
   that G2 builds `TableT` from the measured ordinates; `memo_c_T`'s snapping and base-plus-residual
   are memo C's spans and table; the runner forms no T; the rehearsal uses memo C's table). The
   addendum is `native-t-addendum.md`, with its executable form and self-check in
   `implementation-design/native_t.py` and `native_t.txt`: full rows at t = 0 and 96, a base linear
   in t between them, each sparse stratum as base plus its residuals held beyond them (the
   stand-in's own convention), a monotone guard that never moves a measured ordinate, linear in t
   between strata, and **T(L, 112) = ½ T₉₆(L) + ½ T₁₂₈(L)**. The parent reviews it before step 2.
4. **Fork 4, ACCEPTED.** The law stands down on non-regular variants; the clear variant under the
   law is a named gap (§10).
5. **Fork 5, ACCEPTED.** The governing text is `kneeForms`' own definition of the per-channel form
   (chroma argument M_rgb); the rehearsal is corroboration.
6. **Fork 6, ACCEPTED.** E3 under the law takes the law's fold.

## 10. Named gaps and debt (carried to the tracker at G2's landing)

- **A source whose level 0 is not the device grid** (§2.3): the capture reads level 0 at
  device-pixel centres, which aliases a minified source, and the chain at a matching lod encodes
  after a linear prefilter. The canonical and new beds are one texel per device pixel.
- **Groups sampling through `css-backdrop` on the WebGPU tier.** Verified: the bridge hands the
  renderer a `backdropSourceId` only when the group's sampling backend is `gpu-texture` and the
  source has a backdrop (`platform-web/src/renderer-bridge.ts:310–323`), so such a group has no
  pyramid, the fold's `sampled` is false, and the law cannot run; its body is the proxy's CSS blur
  under the optics layer (`platform-web/src/root.ts:2569`), which is the CSS tier's carry and
  Decision Log 4's.
- **`landed_tone` is a duplicate** of the shipped solve (§2.8), kept textually separate until the
  goldens can be read on a GPU; it is deduplicated into one function after they pass
  byte-identical, with the structural pin retired then.
- **The clear variant under the law** (Fork 4): unmeasured, so the law stands down there.

## 11. Revision after the adversarial review of `67e9d784` (R1–R6; the parent's dispositions, 2026-09-30)

An independent adversarial review read the design and returned needs-attention with two P1 and four
P2 findings. The parent verified the reasoning and accepted all six; its dispositions are kept
verbatim beside the Fork rulings in `implementation-design-rulings.md`. The text above is left as
it was reviewed. Where this section and the text above disagree, this section governs.

**R1 [P1] — the on-luma knees are discontinuous in their hinge decision.** Knee forms 1 and 2
decide the hinge on h·(L(W) − L(C)) > 0, and a stored rounding flips that decision near
L(W) = L(C). Family E's isoluminant pairs sit exactly there. The discontinuity belongs to the
declared family, not to the implementation, and §2.6 now says so: the per-channel knee (form 0,
the carried form) is continuous, and the on-luma knees are not. Consequences:
- The implementation must agree with the f64 oracle except on a set of pixels whose size is
  measured and reported. U2's mirror (R3) reports each knee's **flip fraction** (the share of drawn
  pixels whose decision differs from the oracle's) and its worst error, per storage format, on RGB
  cells with family E included. The measured figures are below.
- No epsilon or deadband is added to the decision, because that would change the declared family.
- The luma comparison needs f32 precision end to end whenever `bodyLawKnee` ≠ 0: rgba32float
  tiles, or an f32 luma companion. The review did not name one further source of the problem, and
  this revision records it: the capture's input is chain level 0, which is **rgba16float linear**
  (`color.ts:50`, `pyramid.ts:21`). Re-encoding an f16 linear value carries about 0.02 code of
  rounding, and the isoluminant pairs' luma contrast is 0.004–0.007 code (`bed.json`, `isoluminant`).
  The mirror therefore also runs the luma knees with the capture reading the 8-bit source directly
  (`exact8`), so that the budget separates the tile format from the capture's input.

**R2 [P1] — A left union pixels outside every member unwritten** (`geometry/src/union.ts:101–116`).
Revised §2.6:
- A is **initialised over the whole sampleable group texture to the captured encoded backdrop**, as
  the rehearsal initialises its whole canvas (`body.py` `lt_argument`: `A_out = B.copy()` before
  any surface writes).
- Each owned R_fp is overwritten in full, not only within one device px of the contour.
- A pixel of the union that lies outside every member's R_fp reads the backdrop. The rehearsal's
  owner rule gives it exactly that: `A_out` keeps B wherever no surface's crop owns the pixel.
- U3 proves coverage against the real union (`@vitrea/geometry`'s smooth union, not the argmin of
  circles) and against the bilinear read's support, with a close-member, receded,
  refraction-off test.

**R3 [P2] — the error mirror did not model the planned storage graph.** U2's test 6 is rebuilt as
`implementation-design/u2_mirror.py`. It models every stored pass's format: chain level 0 as
rgba16float linear, the capture, both floor passes, the numerator-and-weight channels of the
normalised mode, the decimation, each separable pass, the composite in f32, the stored A and its
read. It covers the whole drawn population, including the shell at depth 20 to 20 + 16.8t pt, and
runs through both implemented tones: candidate 1's landed solve (E3 in light receded) and
candidate 2's table. **Its figure replaces 0.115 / 0.127 (§2.4) as the budget and as the
shader-against-oracle tolerance.** The numbers are below.

**R4 [P2] — the band blend's space differed from the rehearsal's.** §2.7 blended in linear light
before the tint. The rehearsal adds the two bodies' difference in encoded output codes, after the
tint's transfer (`swap.py:322–337`). Revised: the runtime reproduces the rehearsal. A cheaper order
is admitted only if the CPU reference puts it within 0.1 code of the rehearsal on the canonical
band cells, tinted cells included. `implementation-design/u2_band_blend.py` measures this. What was
built, and why, is below.

**R5 [P2] — the CSS filter algebra (§5) was wrong.** `feBlend` composites source-over on the
blurs' partial alpha, and an `feComposite` arithmetic primitive clamps, which clips N when λ lies
outside [0, 1]. Revised §5:
- Each blur is normalised to opaque before it is blended, for example by an alpha
  `feComponentTransfer` set to 1 on un-premultiplied values.
- M is composed without clipping inside the admitted λ range wherever the primitives allow it.
  Where they do not, the route is classified as an approximation and measured under Decision
  Log 4.
- The engine row stays `"unverified"`.
This is U5's, held with U3–U5.

**R6 [P2] — the table needs 75 floats, and 18 vec4s hold 72.** Revised §2.10: the table takes
**19 vec4s** (11 levels, 5 spans, 55 codes, 3 gains and the scale, with one lane of padding).
U4 pins the complete CPU/WGSL offset map and its final extent in a test.

### 11.1 What U2 measured (R1, R3), and what it changes before U3

`implementation-design/u2_mirror.py` ran the planned storage graph on 216 cells: the six canonical
backdrops on the capsule, rrect-80, rrect-md, rrect-ml and rrect-lg (active) and on the capsule,
rrect-md and rrect-lg (receded), at 1x and 2x in both schemes, plus the six family-E cells (2x,
both poses and schemes). Each cell has 250 samples per stratum, and every figure is the worst cell
in output codes before rounding.

**The first realisation broke the target.** Four interior levels decimated from 6 device px
(§2.4, `u2_mirror-l4-q6.txt`) put the landed tone **0.295 code** from the oracle with float16 tiles
and 0.210 with float32. The worst cells are dark receded impulse cells, where candidate 1's landed
solve is steep near black (W36's branch) and amplifies small argument errors. §2.4's 0.115 / 0.127
was a luma-only figure through memo C's table, and it missed that amplification.

**Revised realisation, forced before U3.** It uses six interior levels plus the contour level,
decimates from 12 device px as `forward.py` does, and stores **float32 tiles** (and a float32 A)
for every knee. `BODY_LAW_REALISATION` and the fixtures now carry it. The subset runs that led here
are kept as `u2_mirror-l4-q12-subset.txt` and `u2_mirror-l6-q12-subset.txt`. The full run is
`u2_mirror.txt`. Worst band-weighted output error, codes:

| knee (`kneeForms`) | tiles | canonical: landed / table | family E: landed / table |
| --- | --- | --- | --- |
| 0 per-channel (carried) | f32 | **0.148 / 0.064** (rms ≤ 0.024) | **0.022 / 0.030** |
| 0 per-channel | f16 | 0.231 / 0.143 | 0.151 / 0.194 |
| 2 on luma, W's chroma | f32 | 0.148 / 0.064 | 0.020 / 0.022 |
| 1 on luma, whole colour | f32, chain16 capture | 0.148 / 0.064 off the flips | 24.3 / 35.6 |
| 1 on luma, whole colour | f32, exact8 capture | — | 0.094 / 0.265 |

**The budget and the shader-against-oracle tolerance** become **0.15 code** for knees 0 and 2,
not ~0.13. One cell sets it: the dark receded impulse capsule at 1x, where W's decimation meets the
landed tone's near-black slope. The next worst cell is 0.073. Two routes would hold 0.13 there: a
direct W below 24 device px, which costs about twice W's taps at 1x, or a tolerance relative to T's
local slope. Neither is taken, and the parent decides (§11.3).

**R1's flip fractions** (knee 1's decision differing from the oracle's, share of drawn pixels,
worst cell):
- float16 tiles: 53.6 % canonical and 58.8–74.2 % family E. A flip costs up to 7.4 codes on the
  canonical cells and 38.5 on family E.
- float32 tiles, chain16 capture: **1.5 %** canonical, a flip costing 0.010 code on this run's
  samples; the six-level subset run's samples found flips costing 1.8 and 9.3 codes. Family E flips
  **100 %**, at 24–36 codes. The rgba16float linear chain reverses the isoluminant pairs'
  0.004–0.007-code luma order, so the decision is inverted everywhere, not just noisy.
- float32 tiles with the capture reading the 8-bit source (exact8): family E **3.6 %**, worst
  0.094 / 0.265 code.

Knee 2 records "flips" too (up to 100 % on family E), but they cost at most 0.022 code at float32.
Its luma hinge, max(0, ·), is continuous, and its chroma is W's. **Only knee 1 is discontinuous.**
R1's "on-luma knee" is form 1. So knee 1 would need float32 tiles **and** a capture that bypasses the
rgba16float chain: the provider's texture read directly, or a float32 import. Even then its flips
are unbounded in cost where the two terms differ in chroma at equal luma. If step 2 selects knee 1,
the tolerance is a flip fraction plus an off-flip bound (0.15 code), not a single maximum.

**Formats for U3, then**: every tile and A in rgba32float, which is not filterable without the
`float32-filterable` feature. The decimated levels and A are therefore read by manual bilinear
(four `textureLoad`s at f32 weights), the design's plan for the levels already. The optics pass's
read of A moves from the sampler to manual bilinear too. The default
`maxColorAttachmentBytesPerSample` of 32 admits **two** rgba32float targets per pass, so six levels
plus the contour level take four pass pairs per resolution group. Requesting 64 from an adapter
that offers it would halve that, and U3 chooses by the bench. The memory estimate of §2.10 doubles.

### 11.2 R4: which band blend was built, and why

`implementation-design/u2_band_blend.py` read every active tinted cell of the canonical
calibration/validation population: 40 cells in the four macOS 27 profiles, each for candidate 1
(per-channel knee, its own chroma, `r3-1pnb`) and candidate 2 (`r3-2pgb`) at the rehearsal's own
bodies, plus four untinted cells as a control. It compares each order with the rehearsal's
y = t(ship) + w (t(cand) − t(ship)) over the band (0 < depth < 20 pt):

| order | untinted | tinted |
| --- | --- | --- |
| the bodies blended in encoded codes, tinted once | **0.0000** (identical by algebra) | **28.1** codes max; 55 of 80 cell-candidates above 0.1 |
| the bodies blended in linear light, tinted once (§2.7 as written) | 2.35 | 28.4 |

The tinted gap is real, not a fitting artefact. The worst cells' tint fits reproduce their shipped
tinted captures to 0.26–0.28 code rms, and on those cells (the dark tinted capsule over checkerboards) the
fitted transfer has s = 1 with a shade that clips in the blue channel. The author tint there is
an opaque paint whose shade depends on the body's luma, so it does not commute with a blend of two
bodies.

**Built: the rehearsal's construction.** The shipped path draws its whole output as it does today.
The law adds a delta in encoded output codes,
strength × band weight × (enc(tint(law body)) − enc(tint(shipped body))), where tint(·) is the
optics pass's own author-tint composition of an untinted body, evaluated on each body. The rim,
the highlight and the inner shadow stay as the shipped path draws them, which is what the
rehearsal kept in its residual. On an untinted pixel tint(·) is the identity and the delta is one
encode of each body. The cost is one extra tint evaluation on tinted pixels where the weight is
above 0. This replaces §2.7's "mix before the author tint". U4's CPU reference is held to
`swap.py`'s construction on these cells.

### 11.3 What goes to the parent before U3

1. **The tolerance.** The landed tone near black makes the budget 0.15 code, not ~0.13, at one
   cell (the dark receded impulse capsule at 1x; next worst 0.073). The options: accept 0.15, the
   recommendation; take W direct below 24 device px; or state the tolerance relative to T's slope.
2. **Formats.** Float32 tiles and A for every knee, as §11.1 found; two targets per pass under the
   default limit.
3. **Knee 1.** It is carried only if step 2 selects it. It then needs a capture that bypasses the
   rgba16float chain, and its tolerance is a flip fraction plus an off-flip bound.
4. **R4.** The encoded-output delta after the tint on both bodies, as above.

## 12. The parent's rulings on U1/U2 (2026-10-01), and the capture path U3 built

The rulings are kept verbatim in `implementation-design-rulings.md`, which now holds all three of
the parent's sections: the fork rulings, the dispositions of R1–R6, and these.

1. **The native-T addendum is accepted as written** (`native-t-addendum.md`, SHA-256
   `23e400bffb923db7c2453c0ed6062a3c4b4217d1217817adb635ef7eb7085362`). Step 2 pins that hash
   beside the declaration's and cites it wherever native T is read. A decreasing measured ordinate
   is still a finding for the parent.
2. **The realisation of §11.1 is accepted**: six interior levels plus the contour level, the
   oracle's own 12-device-px decimation rule, and a shader-against-oracle tolerance of **0.15
   code** for knees 0 and 2.
3. **Formats are accepted**: every tile and A are rgba32float, read by manual bilinear, two targets
   per pass. The G3 bench reads the cost; if it is prohibitive the formats are revisited on that
   measurement.
4. **Built: one capture path for every knee form, reading the source at its own precision.** The
   bypass was not materially harder than the chain, because the placement mapping it needs is the
   one the chain already has:
   - The pyramid's import pass is stretch-fit: level 0 is the source resampled to the plan's
     extent, and a group's framing is applied later through its `fit` uniform
     (`pyramid.ts` `runImport`; the silhouette tone and the optics pass read level 0 that way).
   - When a group sampling the source runs the law, the import writes a **second attachment at
     level 0**, rgba32float, from the same sample of the source that the chain's level 0 is made
     from: the source's encoded colour, premultiplied by its alpha, (enc·α, α).
   - For an 8-bit encoded source with sRGB primaries (every image, gradient and canvas copy), the
     encoded colour is the sampled value itself, un-premultiplied and clamped as the chain's own
     decode clamps it. That is the 8-bit value exactly at a texel centre. Any other source is
     decoded, converted and re-encoded in f32.
   - The law's capture reads that texture at device-pixel centres by manual bilinear, through the
     group's `fit` (the silhouette tone's mapping). This is the mirror's `exact8` input wherever
     the plan's level 0 is the source grid, which it is on both beds.
   - Where no group runs the law, the import pipeline, its uniform words and the chain are what
     they were: nothing is allocated, and the second pipeline is never created.
   - Every tile carries (value·weight, weight), and every read divides by the weight. That is the
     normalised mode's numerator and weight (`forward.py` `_blur`), and the same straight-colour
     convention the optics pass applies to the chain. The weight is 1 over an opaque source, which
     is every cell of both beds.
   Knee 1's tolerance is therefore a flip fraction plus a 0.15-code bound off the flips, whichever
   knee step 2 selects.
5. **The suite timeouts seen under the sitting's load are environmental.** The full suites are
   re-run at normal load after the sitting and before any merge.

## 13. What U3 and U4 built (2026-10-01)

**The stage** is `renderer-webgpu/src/body-law-pass.ts` with its WGSL in `src/wgsl/body-law.ts`.
It runs in `drawGroups` after the silhouette tone and before the optics pass, for a group whose
folded strength is above 0 and whose source carries the encoded level 0 of §12 item 4. Per
surface, on R_fp, it encodes:

- the capture;
- the floor (a clamp-mode pair);
- one grid per decimation factor, with the widths in two-target pairs (a horizontal and a
  vertical pass per pair) and a block-mean pass for each decimated grid;
- one draw into A, after A's initial fill.

**What that costs in passes.** On the canonical widths that is 8 passes per surface (receded) to 15. For
example, rrect-md at 1x in points takes 1 + 2 + 4 × 2 + 1 + 2 = 14, plus one A pass per group. The
stage is cached on the silhouette tone's model, so a static frame encodes nothing. A frame whose
encoder never reached the queue is built again.

**Sharing a padded grid is exact.** The widths of one q share one decimated grid, padded by the
largest padding any of them needs. `test/w42-body-law-stage.test.ts` holds that schedule to
`u2_mirror.py`'s per-width graph. It emulates the runtime's passes in f64 on five cells
(`u3_fixtures.py`, `fixtures/stage.json`), which exercise every branch:
- direct and decimated levels;
- two grids;
- the normalised mode's zero padding;
- the t = 0 linear case.

It agrees with the mirror to 1e-6 code. Against the exact per-pixel Gaussian it is at most 0.022
code band-weighted.

**One real error, outside the band.** Unweighted, rrect-80's cubic across the gap between its top
interior level (2.8 device px at 2x) and the contour level (10.5) misses by 5.0 codes inside the
last point of depth. The band weight there is below 0.008, so this is inside the accepted budget.
It is recorded because a linear last interval, or one more level, would remove it if a later
reading needs that shell.

**The optics pass (U4).** The uniform grows from 152 to **248 floats** (62 vec4s, 992 bytes) by
appended vec4s only. The lanes are:

| Floats | Contents |
| --- | --- |
| 152–155 | the strength, the band, and A's origin |
| 156–159 | A's extent, the landed solve's ungated tone strength, and the abscissa flag |
| 160–163 | the E3, F-extension and table strengths |
| 164–171 | the F extension's ordinates |
| 172–247 | the table: levels 0–10, spans 11–15, codes 16–70, gains 71–73, scale 74, padding 75 |

`OPTICS_BODY_LAW_LANES` names the map, and `test/w42-optics-law.test.ts` pins it against the WGSL
struct (R6). A is bound at 12, with the placeholder in its place when the law is not handed over.

The law's body is formed after `body_e3_composite` from A read at the refracted position. The tone
takes precedence in this order: the table, then E3 with the F extension under the law, then the
landed solve. A fractional E3 or table strength mixes toward that tone in linear light; U5's CSS
algebra assumes the same for E3. Presence follows E3's convention. After the author tint the law
adds R4's delta, strength × band × (enc(tint(law)) − enc(tint(shipped))), times the coverage, to
the shipped output. The landed solve (`body_law_landed`) and the tint (`body_law_tinted`) are duplicates of
the shipped lines, and the import's chain target duplicates `fs_import`. Each is pinned line by
line with its differences named. They are deduplicated after the goldens (§10).

**At identity** the renderer encodes no law pass and creates no encoded level 0. It writes zeros
into lanes 152–247 after the first 152 floats, which are unchanged, and binds the placeholder.
With every law leaf moved but the strength at 0, the frame's uniform words and passes are the
shipped frame's (the same test).

**Not verified here** (U7 verifies these on an adapter):
- that the WGSL compiles as the adapter's own compiler parses it. naga 30.0.1 (wgpu's WGSL front
  end) validates every new and changed module: the optics pass, the encoded import in both source
  kinds, the capture, both blurs, the decimation and the composite. The adapter's compiler has not
  read them;
- that `layout: "auto"` gives an rgba32float binding read only by `textureLoad` the
  `unfilterable-float` sample type. Every stage binding here and A's binding at 12 rely on that
  reading of the default-layout rule; it was not checked against the specification's text;
- the shader-against-oracle tolerance of 0.15 code.

## 14. U6, and the fix wave after the reviews of U1–U5 (2026-10-01)

**U6, the readout.** `GlassGroupState` gains two fields, both absent where the material asks for
no law, which is every shipped document:
- `bodyLaw` is the WebGPU tier's reading. The renderer resolves it where the fold is, in
  `drawGroups`, and exposes it as `GlassRenderer.bodyLawReadout`.
- `cssBodyLaw` is `cssBody`'s twin, folded to the group's weakest present member. The CSS tier
  reports `stood-down` while its `bodyLawFilterInBackdrop` row is `"unverified"`, which is every
  row.

React's structural state equality compares both fields.

**Item 1: M is stored unclipped.** The review found that the composite clipped M to [0, 1] before
storing A, and that the mirror clipped both its oracle and its simulation, so it could not see the
clip. The declared oracle does not clip there:
- `forward.py:527` returns `T(255 * M)` with M unclipped, and T (`tone.py:70–71`) holds its table's
  ends;
- the rehearsal's argument is unclipped (`body.py:706`, `713`);
- each tone clips where its own gamut step does. The landed solve clips each channel and,
  separately, the luma (`body.py:513`, `515`, through `dec` at `69–71`). E3 clips F, adds the
  argument's chroma, and clips the channels (`body.py:550`, `573`; `swap.py:219`, `233`).

The fix, file by file:
- `wgsl/body-law.ts` stores `vec4f(M, law_luma(W))`. The optics pass's tones already clip where
  the oracle's do, and their CPU references (`landedToneLinear`, `bodyLawE3Codes`,
  `bodyToneTableCodesAt`) never clipped their argument.
- `u2_mirror.py` no longer clips M on either side. Rerun as `u2_mirror-unclipped.txt`, it matches
  `u2_mirror.txt` line for line except the run time: no budget figure of §11.1 moves on the bed's
  population, so 0.15 code stands.
- `u4_out_of_range.py` writes `fixtures/out-of-range.json`, and `test/w42-out-of-range.test.ts`
  holds the CPU references to it. The fixture has the 226 composite cases of `composite.json`'s
  generator whose M leaves [0, 1] (all three knees; M from −0.236 to 1.371), each through the
  landed solve at every endpoint, E3 with the F extension, and candidate 2's table.
- A constant-128 table shows what the clip cost: up to **45.75 codes** at span 96, median 6.39.

**Item 2** is recorded in `u5_css_algebra.md` §4. Between the tone tables' knots the filter reads
a chord. Above 4 codes that is within 0.065 code. Across W36's black join the chord misses by
43.2, 16.0, 53.1 and 200.6 codes on the four endpoints, each between code 0 and code 1. It is a
Decision Log 4 approximation, pinned by `test/w42-css-filter-algebra.test.ts`, and the engine row
stays `"unverified"`.

**A finding for the parent from item 2: the landed solve's response between codes 0 and 1.**
Candidate 1's landed solve, evaluated per pixel, is sharply non-monotone below the join on a
uniform backdrop:
- receded dark: 20.0 at code 0, 215.9 at code 0.60, 12.4 at code 1, 0.2 at code 1.05;
- active light: 132.0, 177.0 at code 0.60, 135.2 at code 1.

This is the declared construction: the rehearsal's `landed_T` reproduces it, and U1's fixture pins
it to 1e-12 on encoded 0.0005 to 0.003. §2.8 carried W36's branch "as it is" and called the
result a dip. At these magnitudes it is more than a dip.

The WebGPU tier evaluates A at f32. A blurred near-black argument there (the dark squares of a
checkerboard beside a light edge, a dark photo) lands inside the first code and draws the spike.
The mirror's 0.15-code budget does not show it, because it compares the implementation to the
oracle at the same argument. The rehearsal's `mono_black` was the device for exactly this, and
it was declined as not declared (§2.8). Whether step 2 reads candidate 1 through it as declared,
or a declaration amends the region below the join, is the parent's decision.

## 15. The black-join amendment, implemented (2026-10-01)

The parent ruled a pre-read amendment on §14's finding. It is `candidate1-black-join-addendum.md`,
SHA-256 `8ad314c13047722c22869b2bd46d1691f1adfd232ccb1209b48264c5ca52a1f6`, committed on its own
as `eaafdf7b` before any read of the archive.

**The rule.** Inside W36's open interval below the join (0 < x < 0.003 on the branch's own
abscissa), where the branch's strength is above 0, candidate 1's per-pixel landed tone is the
straight line in x. It runs from the solve's value at black to its value on the argument's own ray
at the end, per channel, in linear light.

**Its executable form** is `implementation-design/candidate1_black_join.py`. It wraps the hashed
`landed_T` and edits no G0 file. Its report is `candidate1_black_join.txt`, and it writes the
fixture `fixtures/landed-bridged.json`.

**The implementation:**
- **WGSL:** `body_law_landed` bridges around `body_law_landed_solve`, the declared solve, whose
  structural pin to `fs_optics` is unchanged. The shader's end constant is `LAW_BLACK_JOIN_END`.
- **CPU reference:** `landedToneLinear` is now the amended tone. `landedToneSolveLinear` is the
  solve as declared, and U1's `landed.json` test now reads it.
- **CSS:** `cssLandedToneLinear` is now the amended tone, over `cssLandedToneSolveLinear`.

`test/w42-black-join.test.ts` holds the CPU reference to the wrapper's fixture. It also checks:
- that the tone equals the solve at black and at or above the end, and lies on the line between
  the two ends inside, for greys and for chromatic arguments on their own rays;
- that the tone stands down at strength 0;
- that the shader carries the same lines;
- that none of the six digests moves.

**The CSS tier's tables do not change**, because codes 0 and 1 lie outside the interval. Its
fractional-grey misses shrink by 21–40 % against the tone they are measured against
(`u5_css_algebra.md` §4, re-read):

| endpoint | before (codes) | after (codes) |
| --- | --- | --- |
| active light | 43.20 | 28.04 |
| active dark | 16.03 | 9.69 |
| receded light | 56.87 | 39.35 |
| receded dark | 45.23 | 35.83 |

Each amended worst sits at the bridge's end. The same re-read found that the algebra test and
`tier-coherence.test.ts` composed the receded endpoints over the renderer's default instead of
over their scheme's active endpoint. Both now compose them as a root does.

**A correction to §14.** Its receded-dark profile (20 → 216 → 12.4 → 0.2) was read on that
mis-composed material. The declared `landed_T` on the correct receded dark reads 20 → 53.6 at
code 0.60 → 0.7 at code 1 → 0.2 above. The finding stands on every endpoint at these smaller
magnitudes: active light 132 → 177 → 135.2 was read correctly.

The dip above the end remains the named black-level miss. For example, dark receded falls from
39.9 at code 0.7 (bridged) through 36.2 at 0.8 to 0.7 at code 1.

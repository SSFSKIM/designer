# W22 G3 — the overlay's backdrop input: the mechanism, the fix, and the read (2026-09-08)

**Verdict: the overlay group of a stacked scene was handed no backdrop at all, on three gates that
each read "there is a texture bound" as "there is a backdrop". The fix derives the tone from the
surface underneath, forwards it, and lets the shader use it. The dark inversion closes on both tiers
at both scales — the overlay's body 0.0493 → 0.0239 (1x) and 0.0494 → 0.0229 (2x) on the GPU tier,
within 0.0017 of the shipped dark law's answer at the base pane's own output. Every one of the 144
non-stacked captures is byte-identical to G0's, and all 29 renderer goldens reproduce.**

Executes W22 Decision Log 2 (e). Reads: claims §5.94 §5, `../g0/g0-findings.md` §6,
`../g0/stack.txt`, `../g0/overlay-prediction.txt`.

**No native fixture was opened by this gate, and no matrix was written.** The stacked cells are
holdout and the wave's one holdout read belongs to G1 (X5). Verification is vitrea's own capture
against vitrea's own response law, through `capture-web.ts` — which renders and writes a PNG and
never reads `apps/reference-apple/fixtures` — so there was no scratch matrix to delete. The
reference numbers quoted below are G0's, already committed in `../g0/stack.txt`, and nothing here
re-read them from a fixture.

---

## 1. The mechanism, with its arithmetic

### 1.1 The live read

`probe-overlay.ts` runs the calibration page in the same Chromium the captures use (real adapter,
`apple/metal-3`) and reads the page's own resolved state. On
`checkerboard__glass-over-glass__rest`, `apple-macos-26.5-1x-dark-standard`, webgpu, **before the
fix** (`probe/probe-before-1x-dark.json`):

| group | configured | activeRenderer | samplingBackend | measured backdrop tone | unsampled layer pair |
| --- | --- | --- | --- | --- | --- |
| `component` (base) | `texture` | webgpu | `gpu-texture` | level 0.21404, linear 0.5, rgb (0.5, 0.5, 0.5) | — |
| `component-over` | `dom` | webgpu | `css-backdrop` | **`null`** | tint (0.05, 0.05, 0.05), α **0.9198011518738324** |

**The overlay was handed no backdrop tone at all.** Not a wrong one — none. So the whole
backdrop-tone axis stood down for it by design (`backdrop-tone.ts`'s rule 3: no measurement, no
adaptation), and the overlay drew the material's **unadapted** body.

### 1.2 The arithmetic that reproduces the capture

The overlay's optics pass writes a LAYER at the host's `unsampledMaterial` pair (W11a), and the
browser composites it over the proxy carrying the base pane's rendered output. The base pane's own
body measures **0.0470** of linear luminance on that capture. So:

```
(1 − 0.9198) · 0.0470  +  0.9198 · 0.05  =  0.003770 + 0.045990  =  0.049760
```

against a measured overlay body of **0.0493** — **0.0005 apart**, the whole of it accounted for by
the rim and inner-shadow terms the body mask does not fully exclude. The flat mid grey the user's
eye found is the material's own tint at its own alpha, and nothing else.

The response law never ran, so §5.94 §5's inverted input — "a backdrop of linear 0.1344" — is not a
number anything in the pipeline held. It is what you get by asking which input would have made the
law produce a body the law did not produce.

### 1.3 The three gates

One premise, spelled three times, each written when it was true:

1. **`root.ts`** — a group's backdrop tone came from `backdropToneFor(backdropSourceId)`, and
   `sampleBackdropTone` reads **registered textures only**: it draws the source into a scratch
   canvas and averages it. A `dom` group's source is `DEFAULT_DOM_SOURCE_ID`, which carries no
   texture, so the lookup returned `undefined`.
2. **`renderer-bridge.ts`** — `toRendererGroups` forwarded `backdropTone` only under
   `sampled = backdropSourceId !== undefined && samplingBackend === "gpu-texture" && hasBackdrop(...)`,
   with the comment "a group with no backdrop has no tone to take".
3. **`wgsl/optics.ts`** — both the tone collapse and W9's response solve were gated on
   `ou.flags.x > 0.5 && ou.toneAdapt.w > 0.0`, where `flags.x` is `hasBackdrop` (a bound pyramid).
   The comment beside it says the guard exists so that a zero vector is not read as a black
   backdrop — which is exactly what `toneAdapt.w` already answers.

Each gate alone was enough to keep the overlay unadapted, and they had to come off in that order:
opening only (1) moved the CSS tier and left the GPU tier at 0.0493 to four decimals; opening (1)
and (3) still left it there; the GPU tier moved only when (2) came off too. That sequence is the
attribution, and it is in this gate's own capture rounds.

### 1.4 The other candidates, each refuted with a number

**(a) G0's candidate — the proxy sampling past the base pane through the padding W8 enlarged for
the outer shadow. REFUTED, at 0 %.** Read live off the DOM:

| | x | y | width | height | span |
| --- | ---: | ---: | ---: | ---: | --- |
| the overlay's proxy box | 86.9375 | 50.9375 | 146.109375 | 82.109375 | x [86.94, 233.05], y [50.94, 133.05] |
| the base pane's border box | 50 | 35 | 220 | 130 | x [50, 270], y [35, 165] |

The proxy box sits **entirely inside** the base pane, with margins of 36.94 px left, 36.95 px right,
15.94 px top and 31.95 px bottom. Its effective padding is 13.05 px, which is exactly 3σ at the
group's σ of 4.35186 (`backdrop-filter: blur(4.35186px) saturate(1.8)`, read off the element), and
the overlay's nearest approach to the base's edge is 29 CSS px — more than twice the padding. **None
of the proxy's sampling region lies over raw checkerboard.** The candidate needed 19.3 % of it to.

**(b) The tone measured under both planes, off the raw checkerboard. REFUTED.** There is no DOM tone
measurement in the runtime at all: the group's tone was `null`, not 0.5. Had anything read the raw
checkerboard, the overlay would have carried level 0.21404 / linear 0.5 — which is precisely what
the BASE group carries, and it is visibly a different number.

**(c) The proxy compositing the base plane's canvas at the wrong alpha. REFUTED.** The base pane's
own body reads 0.0470 – 0.0471 on the capture, and §1.2 reproduces the overlay's body to 0.0005 from
that number at the published layer alpha. There is no room for a compositing error of the size in
question (2.9×).

**(d) The overlay's material evaluated with the base's texture. REFUTED** by the same read: the
group's tone was absent, not the base group's.

---

## 2. The fix

Three commits' worth of one mechanism, in the three places §1.3 names. No constant moved; no value
in `material.ts` or in any profile document changed.

### 2.1 `packages/platform-web/src/backdrop-stack.ts` (new)

The arithmetic, pure and unit-testable. Two functions:

- **`compositeToneOver(interior, tone)`** — what a surface renders at, given what it is over.
  `cssTierCompositeLevel` already names the renderer's composite as `(1 − α)·b + α·T + X` per channel
  in linear light; that is an affine in the backdrop, so the surface's output tone is the same affine
  applied to its backdrop's tone. Nothing here carries a number of its own, which is what makes it a
  mechanism.
- **`toneBeneath(footprint, plane, painted)`** — which surface is underneath. §Geometry's X1 forbids
  two overlapping nodes in one plane, so a stack is two planes by law; the answer is the
  last-painted surface in a **strictly lower** plane whose border box **contains** the whole
  footprint. Containment and not overlap: a footprint half on glass and half on a page vitrea has
  not measured has no single backdrop, and the rule then finds nothing and the group keeps the
  unadapted body it always drew.

### 2.2 `packages/platform-web/src/root.ts`

A third statement in the order the app's statements deserve, after X6's declared hint and after the
pixels the app handed over: **the glass this group is standing on**. Reached only from the
`css-backdrop` backend. The frame's group loop now runs **back-plane first** (stable within a plane,
so every single-plane page — which is every page that is not a stack — resolves in exactly the
sequence it always did), and each surface publishes the tone it renders at as it resolves, but only
where a backdrop was measured for it.

### 2.3 `packages/platform-web/src/renderer-bridge.ts`

The tone is forwarded wherever the host **measured** one, rather than wherever a texture is bound.

### 2.4 `packages/renderer-webgpu/src/wgsl/optics.ts`

The collapse and the W9 solve take `ou.toneAdapt.w > 0.0` alone. The strength is already zero
wherever nothing was measured and zero wherever the policy stood the axis down (under
`glass: "none"` the refraction cap is `none` and `backdropToneUnderPolicy` folds to 0), so
`hasBackdrop` beside it said the same thing twice until this gate — and then said something false.
The solve reads the backdrop as `toneAnchor.w`, the group's own linear mean, and never as the
per-pixel sample, so it is the same closed form whether the pass composites the backdrop itself or
writes a layer for the browser to composite over a proxy carrying the same mean.

### 2.5 What the derived level is, and the one thing it gives up

The tone COLOUR and `linearLuminance` are linear means and the affine carries them exactly. The tone
LEVEL is the backdrop's encoded-space mean decoded, and an encoded-space mean does not commute with
a linear affine.

**The derived level is the derived linear mean, and that is a measurement rather than an
assumption.** Read off this gate's own captures (`base-stats.txt`), the base pane's rendered body
has an encoded-space mean **0.0020 – 0.0027 below its linear mean in dark** and **0.0037 – 0.0048
below it in light**, on both tiers and at both scales — against an input whose two statistics stand
**0.286** apart. The surface's own occlusion and the blur it drew the backdrop through are what
flatten the structure the split exists to carry.

A first form transported the input's gap scaled by the square of the transmission — exact at both
ends of the transmission range, and wrong in the middle by more than the whole quantity. It read
**−0.0749** on the light base pane where the capture reads **−0.0042**, because the variance is not
the only thing the composite changes and sRGB's curvature at a body near 0.66 is nothing like its
curvature at a checkerboard's 0.5. It was measured, rejected, and is recorded here rather than in
the code. Carrying nothing is off by at most 0.005; carrying the transported gap was off by 0.07.

### 2.6 The instrument the page gained

`packages/calibration/web/scene.ts`'s `GroupReport` now publishes the backdrop tone each group was
handed. The same honesty rule the rest of that record follows: until this field existed a capture
said what a group *drew* but not what it was drawing *over*, and a group handed no backdrop at all
looked exactly like a group whose response law had missed. That is how this defect survived three
waves of material fitting.

---

## 3. The test

`packages/platform-web/test/backdrop-stack.test.ts`, eleven cases at the two levels the mechanism
has.

The arithmetic: a surface that occludes nothing passes its backdrop's light through; one that
occludes everything collapses onto its own tint with both statistics on one number; and the
backdrop's own encoded/linear split does not travel into the output — the residual §2.5 measures,
pinned as the behaviour rather than left implicit.

Which surface is underneath: a lower plane's surface that carries the whole footprint is found; a
footprint that hangs over the edge is refused; a same-plane neighbour is refused however its `order`
reads (reading `order` as depth would invent a stack X1 forbids); the nearest of two candidates
wins; and a surface with no extent is not a backdrop.

The wiring, on a root built to the calibration bed's own stacked geometry (base 220 × 130 at
(50, 35), overlay 120 × 56 at (100, 64)): a DOM-sampling overlay over the base is handed the base
surface's rendered output, and an overlay clear of the base — or overhanging it — is handed nothing,
which is the rule this must not weaken.

`packages/renderer-webgpu/test/backdrop-tone.test.ts`'s WGSL contract moved with the shader: the axis
stands down on the measurement alone, and the test now asserts the flag is *not* read beside it.

---

## 4. The panes, before → after (web side only)

`before` is G0's canonical read (`../g0/stack.txt`), the committed `web-captures/` at the 0.10.0
landing. `after` is this gate's own capture, `stack-web.txt`. `native` is G0's already-recorded
reading of the reference, quoted for direction and not re-read here. The base pane's rows are within
0.0002 across the change on every cell except where noted, which is the control: this fix reaches
the overlay group and nothing else.

`law` is the shipped response law's thin row evaluated at the base pane's own measured output —
`over − law` is the acceptance quantity, and the wave's band is ± 0.004.

### Dark — the inversion, closed

| profile | tier | over before | **over after** | law | over − law | excess before | **excess after** | native excess |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1x dark | webgpu | 0.0493 | **0.0239** | 0.0245 | **−0.0006** | +0.0023 | **−0.0232** | −0.0260 |
| 2x dark | webgpu | 0.0494 | **0.0229** | 0.0247 | **−0.0017** | +0.0018 | **−0.0246** | −0.0267 |
| 1x dark | css | 0.0502 | **0.0235** | 0.0240 | **−0.0005** | +0.0048 | **−0.0220** | −0.0260 |
| 2x dark | css | 0.0506 | **0.0238** | 0.0248 | **−0.0010** | +0.0025 | **−0.0244** | −0.0267 |

Every cell lands within **0.0017** of the law, against a band of 0.004. **The sign is right on all
four**: Apple's overlay is darker than its base and vitrea's now is too, at 85 – 92 % of the
reference's magnitude, where before it was lighter on every one.

### Light — the GPU tier held, the CSS tier recovered

| profile | tier | cell | over before | **over after** | law | over − law | excess before | **excess after** | native excess |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1x light | webgpu | `checkerboard` | 0.8902 | 0.8902 | 0.8894 | +0.0007 | +0.2291 | +0.2291 | +0.2371 |
| 1x light | webgpu | `photo` | 0.8736 | 0.8736 | 0.8786 | −0.0050 | +0.2423 | +0.2423 | +0.2439 |
| 2x light | webgpu | `checkerboard` | 0.8925 | 0.8925 | 0.8917 | +0.0008 | +0.2252 | +0.2252 | +0.2375 |
| 2x light | webgpu | `photo` | 0.8733 | 0.8732 | 0.8786 | −0.0053 | +0.2421 | +0.2420 | +0.2441 |
| 1x light | css | `checkerboard` | 0.8432 | **0.9010** | 0.8908 | +0.0102 | +0.1784 | **+0.2363** | +0.2371 |
| 1x light | css | `photo` | 0.8161 | **0.8838** | 0.8781 | +0.0056 | +0.1861 | **+0.2538** | +0.2439 |
| 2x light | css | `checkerboard` | 0.8502 | **0.9059** | 0.8940 | +0.0119 | +0.1766 | **+0.2322** | +0.2375 |
| 2x light | css | `photo` | 0.8162 | **0.8850** | 0.8780 | +0.0070 | +0.1866 | **+0.2554** | +0.2441 |

The **GPU tier's light rows do not move** — to 0.0001 on three of four and exactly on the fourth.
That is the correct outcome and it is worth stating plainly: the light material at the mapping's
reference alpha already composites within 0.0008 of the law's answer over a body near 0.66, which is
why the light bed never showed this defect. The adaptation now arrives at the same place on
purpose rather than by coincidence.

The **CSS tier's light rows recover 0.056 – 0.069** and land on the reference's own excess to 0.001
– 0.005 on `checkerboard` (a residual that was 0.059 – 0.061); `photo` overshoots the reference's
excess by 0.010 – 0.011 where it was 0.058 short. That is a CSS-tier residual, recorded in §6.

---

## 5. The byte-identity and the goldens

**Every non-stacked capture is byte-identical.** `byte-identity.txt`: 144 PNGs over the four standard
profiles, webgpu, `--alpha`, the calibration and validation sets — the same flags and the same scene
lists as `../g0/g0-capture.sh` — compared against G0's scratch bed at
`/Users/new/.claude/jobs/5c70e47f/tmp/w22/g0/after/web-captures`, which is still on disk and was
taken at the sweep gate.

```
byte-identical: 144   moved: 0   not in G0: 0
```

Nothing G0 captured went un-recaptured, so the set is the same on both sides. `digests.txt` records
the sha256 of every PNG this gate produced, stacked and bed.

**The goldens: 29 / 29 byte-identical**, including `concentric-nesting` and `union-pair`, the nested
and grouped scenes, and `highlight-press-glow`, the one that captures the highlight canvas. Run
after the shader change and again after the level simplification; no golden was re-recorded and none
moved. The isolation spec's pinned hashes stand.

---

## 6. Gaps, blocks and what this hands on

1. **The derived level's residual (§2.5).** The derivation reports the output's linear mean as its
   level; the capture says the true encoded-space mean is 0.0020 – 0.0027 (dark) and 0.0037 – 0.0048
   (light) below it. The limit it gives up is a surface transparent enough to pass its backdrop's
   structure through: this tells the pane above it that it is over a flat backdrop when it is over a
   faint checkerboard. Correcting it needs the backdrop's distribution and the surface's blur kernel,
   and the tone sample carries two moments and no kernel. Bounded at 0.005 of level, which is 0.004
   of what the overlay then draws in light and 0.0006 in dark.

2. **The derived linear mean overshoots the base pane's measured body, and in light it survives.**
   Derived against measured, on this gate's own captures: dark **0.04833 against 0.0471 (+0.0012)**;
   light **0.69590 against 0.6610 (+0.0349)**. The cause is inherited and already documented:
   `backdrop-tone.ts` measures **one number per SOURCE**, the whole texture's mean, and the base
   pane's own footprint over that texture need not average to it. In dark the base's transmission is
   0.095 and the error is scaled away; in light it is 0.51 and it is not. It costs nothing measurable
   on the GPU tier (the light rows do not move) and it is part of what the CSS tier's +0.010 on
   `photo` is. Closing it is the per-footprint sampling `backdrop-tone.ts` declines by name — a
   charter, not a wave clause. **Recommend the tracker.**

3. **The CSS tier's light `photo` overshoot** (+0.010 / +0.011 of excess against the reference, where
   `checkerboard` lands within 0.005 and dark lands within 0.005 of the law). A CSS-only residual on
   a holdout cell; it should be read against the reference at G1's holdout read rather than guessed
   at here.

4. **Containment is tested on border boxes.** A footprint tucked into a rounded surface's own corner
   is treated as contained when a sliver of it is not; the error is bounded by that surface's radius
   and it moves the derived tone by whatever that sliver's backdrop differs by. Not reachable on the
   calibration bed, where the overlay clears the base's corners by 29 px.

5. **One hop, and one surface.** A group over a group over a group takes the tone of the surface
   immediately beneath it, which is the right answer because that surface's tone already carries
   everything below it. A footprint straddling two surfaces of a lower plane, or half off the glass,
   takes nothing — the unadapted body, as before. Both are stated in the module and neither is
   exercised by the bed.

6. **Unexercised profiles.** `apple-macos-26.5-1x-light-reduced-transparency` and
   `-increased-contrast` declare no `glass-over-glass` scene, so the fix has no capture under either
   accessibility fold. The policy path is the shipped one (`backdropToneUnderPolicy` folds the
   strength to 0 under `glass: "none"`, which is what keeps the axis down there), and the unit suite
   covers the fold, but there is no pixel for it.

7. **No block.** Everything this child was asked to do ran: the live read, the fix, the test, the
   captures, the byte-identity and the goldens. The GPU was free before every capture and every
   golden run, one process at a time.

---

## 7. Review fix wave (2026-09-08)

An independent review of the branch against `516f71f` returned two P2 findings, both reproduced
against the runtime with in-memory root probes. Both are real, both are about the same thing — the
published tone has to be **what a group above would actually sample**, and the first version
published something narrower than that twice. Both are fixed, both carry a test that fails against
the pre-fix code, and neither moves a number on the calibration bed.

### 7.1 The published tone ignored the author's tint

`interior` describes the **untinted** material; `authorTintLayer` is computed after it and never
entered `compositeToneOver`. So a full-strength red base published the same achromatic tone as an
untinted one, and the pane above it adapted, on both tiers, to a colour and a level that were on
nobody's screen.

W10's composition contract puts the author's layer last — the seed at its shade, opaque, at the
author's opacity, composited over the converted material in the ENCODED space, which is what a
`CALayer` with `opacity` does and what both tiers draw. `compositeToneOver` now takes that layer and
applies it in that space, after the material's affine and not folded into it; `root.ts` publishes the
surface after the layer is resolved rather than before. At strength zero, and where there is no
layer, the result is the identity by branch rather than by round trip.

**Tests** (`backdrop-stack.test.ts`): three on the arithmetic — the identity at zero strength and at
no layer; a full-strength red layer publishing red (`rgb` (1, 0, 0), `linearLuminance` 0.2126)
rather than the material's grey; and a half-strength layer moving the colour and the level together
in the encoded lerp. One at the root — two stacks built to the bed's own geometry, one with a
`#ff0000` base and one without, asserting the overlay's handed tone is achromatic in the first and
red by more than 0.2 of a channel in the second, with a level that moved with it.

### 7.2 Containment was tested on the unclipped border box

A host's border box is reported **unclipped** — Decision Log #41(k)'s own point, and the reason
`ProxyGeometry.clipUnion` is documented as the *visible* extent rather than the measured one. So a
base scrolled out of an `overflow` ancestor kept a full-size box while painting nothing, satisfied
containment, and handed its tone to the overlay.

Both sides of the test now use the visible extent: a painted surface publishes
`clipRect(bounds, node.clip)`, and the querying group's footprint is the union of its members'
clipped rects on the same rule. A fully cropped surface reduces to no extent, and `contains` already
refuses a rect without extent on either side — so the hidden case falls out of the rule rather than
needing a second one.

**Tests** (`backdrop-stack.test.ts`, at the root, with a real `overflow: hidden` ancestor so the clip
travels the chain the runtime reads it on): a base cropped away entirely → the overlay is handed
nothing; a base cropped back so the overlay's footprint is no longer inside what is left → nothing;
and the control, a crop that trims only margin the overlay does not stand on → the tone still
arrives.

### 7.3 Re-verification

| step | result |
| --- | --- |
| `pnpm -r build`, `pnpm -r lint`, `pnpm -r test` | clean; `backdrop-stack.test.ts` now 18 cases |
| the three new root cases against the pre-fix code | **3 failed / 15 passed** — the fail-before record |
| `pnpm --filter @vitrea/renderer-webgpu test:golden` | **29 / 29 byte-identical** |
| `platform-web` Playwright, `chromium` + `chromium-gpu` | **150 passed** |
| byte-identity, `--set calibration,validation`, four profiles, webgpu, `--alpha` | **144 / 144**, 0 moved |
| the two `glass-over-glass` cells re-read, web side only | **every figure in §4 reproduced to four decimals** |

The bed carries no tinted stack and no clipped stack, so neither fix can reach a committed capture,
and neither did: `stack-web.txt`, `byte-identity.txt` and `base-stats.txt` are unchanged by this
wave, and only `digests.txt` moved — on its timestamp line.

---

## 8. The chain

| step | result |
| --- | --- |
| `pnpm -r build` | clean |
| `pnpm -r lint` | clean |
| `pnpm -r test` | clean (the platform-web suite with `backdrop-stack.test.ts`'s 11 new cases; the renderer suite with the moved WGSL contract) |
| `pnpm --filter @vitrea/renderer-webgpu test:golden` | **29 / 29 byte-identical** |
| `platform-web` Playwright, `--project=chromium --project=chromium-gpu` | **150 passed** (includes `e2e/shared/proxies.spec.ts`, `e2e/shared/overlap.spec.ts`, `e2e/pixel/backdrop-tone-pixels.spec.ts`, `e2e/gpu/*`) |
| the live read | `probe/probe-before-1x-dark.json`, `probe/probe-after-1x-dark.json`, `probe/probe-after-1x-light.json` |
| the captures | `g3-capture.sh` → scratch; `digests.txt` |
| the per-pane read | `run-stack-web.sh` → `stack-web.txt`, `stack-reads/` |
| the base pane's two statistics | `base-stats.txt` |
| byte-identity against G0 | `byte-identity.txt` — 144 / 144 |

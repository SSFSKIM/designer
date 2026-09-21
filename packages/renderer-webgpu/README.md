# @vitrea/renderer-webgpu

The optical engine — child **C6** of
`docs/doperpowers/specs/2026-08-24-vitrea-liquid-glass-design.md`.

Internal package. `vitrea` reaches it through a single dynamic import (X7's
lazy seam), so a CSS-tier consumer never downloads a byte of WGSL.

## Running the suites

| command | what it runs | needs a GPU |
| --- | --- | --- |
| `pnpm test` | 198 unit tests, including the CPU half of the f32 cross-check and the dirty-epoch invariant driven by core's own scheduler | no |
| `pnpm test:golden` | 11 sRGB-locked golden-image tests | yes |
| `pnpm test:gpu` | f32 cross-check, dirty-epoch invariant, device-loss recovery, shader compilation | yes |
| `pnpm test:bench` | the two declared benchmark scenes, pass by pass | yes |
| `pnpm test:e2e` | all of the above GPU suites | yes |

Only `pnpm test` is part of `pnpm -r test`. The GPU suites need a browser and an
adapter, so they stay out of the default chain and are run deliberately.

## Regenerating the goldens

```sh
pnpm --filter @vitrea/renderer-webgpu goldens:regen
```

Writes every scene in `e2e/fixtures/scenes.ts` to `e2e/goldens/*.png` and skips the
comparison for that run. Review the diff before committing: a golden that changed
because the optics changed is the suite working, and a golden that changed because
somebody regenerated on a failing build is the suite defeated.

The committed goldens were produced on an `apple / metal-3` adapter. §Calibration
keys results by adapter class, so regenerating on different hardware is expected to
move some pixels; the tolerance in `e2e/golden/scenes.spec.ts` is what says how
much is a rounding difference and how much is a change in the optics.

## The launch mode matters

This machine hands out three different WebGPU answers depending on how Chromium is
launched:

| launch | adapter |
| --- | --- |
| Playwright's default headless shell | `google / swiftshader` — **software** |
| `channel: "chromium"`, headless | `apple / metal-3` — hardware, `timestamp-query` |
| `channel: "chromium"`, headed | the same |

`playwright.config.ts` asks for the full Chromium binary for that reason, and the
adapter gate **fails** rather than skips when it finds a software fallback —
goldens and benchmark numbers from a CPU rasteriser are not what they claim to be.
`VITREA_ALLOW_FALLBACK_ADAPTER=1` opts into the software path deliberately.

WebGPU also needs a secure context: `navigator.gpu` is undefined on `file://` and
`data:` URLs, which reads exactly like "no WebGPU on this machine". The fixture
server serves `http://localhost`.

## The two operators, and the leaves they are made of (W30)

`DEFAULT_MATERIAL_PROFILE` carries eight leaves at values that make them do
nothing, and **that is the macOS 26.5 material's own measurement rather than a
placeholder**: its outer shadow's σ genuinely is span-invariant across spans 32…160
and its diffusion is what the existing kernel expresses. The leaves landed there
first, at algebraic identities and ahead of any value, because adding a leaf moves
every profile document's `resolvedMaterialSha256` — the digest is taken over the
fully resolved material — and the project spends that disturbance once rather than
twice (W30 Decision Log 1 (a) and (b)).

**Three of the eight are fitted in the shipped macOS 27 documents** (claims
§5.159): the σ law's slope, reference and thin floor, on both schemes. Two more —
the scatter's scale gain and the reference it is read about — are fitted in the
macOS 27 **dark** document and declined in the light one, and the three that
remain, the second heavy tap's two widths and its signed share, are declined on
both with a measurement rather than by omission. What a document does not name it
inherits, so the renderer's defaults are what the frozen macOS 26.5 material goes
on drawing.

**The outer shadow's σ law**, on `MaterialOuterShadow`. macOS 27 blurs the outer
shadow wider under a wider surface, so σ becomes a function of the casting span:

```
σ_css(span) = sigmaPx + max(sigmaThinOffsetPx,
                            sigmaSlopePerSpan · (span − sigmaSpanRefPx))
```

`sigmaSlopePerSpan` is CSS px of σ per CSS px of span, `sigmaSpanRefPx` is the
span at which σ equals `sigmaPx`, and `sigmaThinOffsetPx` is the signed floor the
thin regime holds, as an offset from `sigmaPx`. All three ship at 0 in the
renderer's own defaults, where the whole law is `sigmaPx` at every span — a
multiplied zero under a `max` whose other arm is an added zero — and the knee is
DERIVED from the three rather than being a fourth leaf. There is no device-ratio
argument: the thin regime's device-px reading was tested and rejected. The law is
evaluated **per caster** on both tiers — the WebGPU tier per pixel from the
casting surface's span, the CSS tier per surface into one `box-shadow` blur radius
— and the two group-level readers (the optics pass's scissor pad, the CSS tier's
group-shadow clip) take it at the widest span among the members, which bounds
every member's σ rather than naming any member's, exactly while
`sigmaSlopePerSpan ≥ 0`.

**The shipped macOS 27 documents fit it** (claims §5.159): the light material's
law is `8.96 + max(−6.8328, 0.1314 · (span − 96))` and the dark material's
`9.04 + max(−6.968, 0.1340 · (span − 96))`, both with the derived knee at a span
of 44. The reference is held at 96 rather than fitted, because the law has one
flat direction — shifting `sigmaPx`, `sigmaThinOffsetPx` and `sigmaSpanRefPx`
together leaves σ unchanged at every span — and 96 is the span the amplitude's own
anchor is keyed to, so the shadow's two laws pivot on one abscissa. A 44 px
control's σ goes from the 11.0 that 0.19.0 drew to 2.13, and a 160 px panel's to
17.37.

**The scale-selective scatter's spanning set**, on `MaterialProfile`. The
diffusion residual is non-monotone in the backdrop's pitch, which a positive mix
of two Gaussians cannot be, and two mechanisms can express it, so both are
expressible. `sizeHeavySecondSigma` and `sizeHeavySecondSigma2x` are a second
heavy tap's width per scale; `sizeHeavySecondShare` is that sample's signed weight
in the deep mix **and the single gate on the whole mechanism**, so at 0 no texture
is allocated, no separable pass is encoded and no sample is taken.
`sizeScatterScaleGain` and `sizeScatterScaleRef` condition `kScatter` on the
source's own measured spatial scale — the analysis pass's per-source edge density
— about a reference. All five ship at 0 in the renderer's defaults.

**Which of them a shipped document fits** (claims §5.159 §4). The macOS 27 dark
document takes `sizeScatterScaleGain` −2 about a `sizeScatterScaleRef` of 0.03,
which moves how much of a structured backdrop survives its body toward what
Apple's material passes on both scales. The macOS 27 light document declines it,
and the second heavy tap is declined on both — each with a measurement rather
than by omission. The one worth knowing before reaching for either: **the
per-source statistic is scale-invariant by construction**, because the analysis
reduction reads a fixed 64 × 64 grid off a mid-chain level whatever that level's
real size is, so one scene's edge density is the same number at dpr 1 and dpr 2
(measured 0.170 against 0.176). A residual that changes sign between the two
scales cannot be reached by a gain on that statistic, whatever its value.

A binding is the one thing that is not saved: a WGSL bind-group layout is one
layout, so the second heavy texture's slot exists at every draw and takes the
same placeholder view the first one already takes when a material declines it.
What the share gates is every resource and every pass behind that slot.

`packages/renderer-webgpu/test/w30-inert-laws.test.ts` states each identity over
a span sweep and both scales, and `e2e/gpu/w30-heavy-second-tap.spec.ts` opens
the gate on a test profile so the ON path is proved to exist and not only to be
inert. `packages/platform-web/test/w30-inert-laws.test.ts` holds the SHIPPED law
to the condition that makes a group's reach a bound — a negative slope would
invert it — on the documents a page actually draws rather than on an illustrative
shape.

## The body's chroma retention, and the digest rule that let it land free (W31)

Over a photograph Apple's macOS 27 material carries the backdrop's hues through
the body and vitrea's rendered a flat grey of the right level. No constant could
close that: the body is a neutral plate composited over the blurred backdrop, so
what a photograph's hues survive at is `1 − sizedAlpha` — 0.513 light, 0.095 dark
— against a reference that reads 0.709–0.833 of its own backdrop's chroma on the
light cells and 0.903–0.973 on the dark ones. It is a mechanism the material lacked, and **`bodyChromaRetention`**
is it (claims §5.161 §5, fitted in §5.164).

**Said in the statistic the reference is quoted in, before and after** (2026-09-21,
review closure; claims §5.165 §9, finding R5). `1 − sizedAlpha` is what the plate
TRANSMITS; the reference's 0.709–0.833 and 0.903–0.973 are a measured mean, the
body's per-pixel OKLab chroma over the backdrop's, and the two are not the same
number even before the fit — the light body measured **0.2385–0.3304** and the
dark one **0.1059–0.1227** on the declared bed (§5.161 §3). After the fit the same
measurement reads **0.5118–0.5716** light active, **0.5757–0.6616** light
inactive, **0.3499–0.3672** dark active and **0.2188–0.2291** dark inactive
(`chroma-mean-after.txt`, off the committed matrix). None of those is what was
FITTED: the wave fitted `R`, the chroma-to-structure SPREAD ratio, in which the
blur cancels and which is what the eye reads as colour in a body, and `R` is what
`M1` bounds. The mean is recorded beside it because it is the statistic the gap
was first stated in.

The colour is mixed toward `backdrop · (Y / Y_backdrop)` — the backdrop's
chromaticity carried to the colour's own linear luma — by the retention. **Luma
is held by construction, not by correction**: both endpoints of the mix carry
linear luma exactly `Y` and linear luma is a linear functional, so the shader's
renormalisation is an f32 rounding guard. Gamut is taken by scaling chroma toward
the neutral at fixed luma, never clipped per channel, because a per-channel clamp
moves the level. It is applied immediately after the composite and before the
tint composition, so the tint's shade law — which reads the untinted material's
LUMINANCE — is bit-identical whatever the retention holds.

**The CSS tier carries none of it, and that is a measurement.** The mirror was
written — a gain on the one `saturate()` that tier already has, at the alpha it
actually solves — rendered on the declared bed, and taken back out (claims
§5.164 §5). On the DARK scheme it bought **nothing**: ratio (ii) over the active
cells reads 0.2024 before and after, and still 0.2024 at a retention of 1,
because the converted alpha there leaves no backdrop for a saturation to act on.
On the LIGHT scheme it bought 0.76–1.04 of the gap and broke both stops doing it
— the level-growth stop on 10 of 26 cells and the structure stop on 13 — because
`saturate()` is a matrix on sRGB-ENCODED channels and stops preserving luminance
the moment one clips. So `BODY_CHROMA_RETENTION` in `@vitreajs/vitrea-web` is
**0**, mirroring this package's default rather than the documents, and the
residual is recorded beside it. A page on the CSS tier draws the body it drew
before.

**Under an accessibility OCCLUSION LIFT the retention stands down**
(W31 Decision Log 3 (d); claims §5.164 §13). A lift sends the plate's alpha to
`α + lift·(1 − α)`, so the plate covers more of the backdrop than nominal and
restoring the nominal fraction of its chromaticity gives back exactly what the
preference asked to have covered up. Applied unconditionally it took the
chroma-to-structure ratio on those beds to three times the reference's;
`bodyChromaRetentionUnderPolicy` is an exhaustive switch on the occlusion axis
and returns 0 on `increased` and `opaque`, so those pages draw what 0.20.0 drew,
to the byte.

Which preferences that is, said exactly, because the axis and the preference are
not the same thing (2026-09-21, W31 G3c review, folded at G4; claims §5.165).
**Reduce Transparency** raises occlusion and stands the retention down.
**`forced-colors`** takes `glass` to `"none"` and draws no body either way.
**Increase Contrast alone does NOT**: §Accessibility gives it `border`,
`foreground` and `ambientTint` and no occlusion key, `prefers-contrast: more`
and `prefers-reduced-transparency: reduce` are matched independently, and macOS
27 decoupled the two switches where macOS 26.5 coupled them
(`apps/reference-apple/scenes.json`, the `-increased-contrast-` entry). So a
0.21.0 page under Increase Contrast alone draws the retention at its full value.
That is not a regression against 0.20.0 — which had no operator — and it is not
measured either: the wave's increased-contrast bed is the COUPLED one, whose
occlusion is lifted. It is recorded as an open gap, with the design question
named beside it: `ambientTint: "reduced"` is documented as the material's colour
cast picked up from its backdrop, which is literally this leaf.

**The leaf landed without moving a single document's digest, and that is the
second half of the wave** — true of the LEAF commit, which is the claim being
made; the fit that followed moved all four macOS 27 documents to
`3dc24a74f17fd87e`, `8a43f54162606db4`, `ab3ed65aa02869b1` and
`e1f42c5656ef392f`, as a fit must (claims §5.164 §13, findings F6 and N11).

`resolvedMaterialSha256` is taken over the fully resolved material, so before
W31 a material that gained a key moved every document's digest whatever that key
held — which is why the paragraph above this
one says W30 "spends that disturbance". W31 Decision Log 1 (a) ruled the rule
that ends it:

> The fingerprint drops a leaf whose resolved value equals its declared inert
> identity, and drops a **gate-group** — a gate leaf at its identity together
> with the leaves it makes unread — as one unit.

`MATERIAL_IDENTITY_TABLE`, beside `DEFAULT_MATERIAL_PROFILE`, is that table:
append-only, versioned, each entry naming the committed unit case that proves
its drop. `materialDigestInput` is the one implementation of the rule; the HASH
stays duplicated at each pin site, because an algorithm restated is an algorithm
two places can check and a table walk that drifted would drift silently.

**What a later wave has to do to add a leaf for free.** Add the entry in the
same commit as the leaf, ship the default AT the declared identity, and name the
case that proves it. A leaf added without an entry is carried at whatever it
holds and moves every document's digest at once — the loud failure, and the one
worth having. A post-seal leaf's default IS its identity, forever: the digests
recorded against this table are taken with those leaves dropped at those values.

`test/w31-body-chroma.test.ts` states the law as arithmetic and asserts the
shader's own text term for term; `e2e/gpu/w31-body-chroma.spec.ts` opens it on a
hardware adapter over a chromatic backdrop, where the ON path moves the raster
and the interior's mean luminance moves by a sixth of one 8-bit code;
`test/w31-gate-groups.test.ts` holds each gate at its identity while the gated
leaf is swept off it.

## Where the contracts live

| contract | made true in |
| --- | --- |
| X3 — BackdropFrame protocol (this child owns its operational detail) | `src/backdrop.ts` |
| X5 — colour pipeline | `src/color.ts`, `src/wgsl/prelude.ts` |
| X8 rider 2 — concentric renders as a level set of the parent's field | `src/instances.ts`, `src/wgsl/field.ts` |
| §Core model — ≤1 pyramid rebuild per dirty source per frame | `src/rebuild-ledger.ts` |
| Decision Log #19 — the dual refraction cap | `src/material.ts` |
| Decision Log #20 — family C's f32 cross-check | `src/governor.ts` gates it; `test/f32-cross-check.test.ts` and `e2e/gpu/cross-check.spec.ts` run it |

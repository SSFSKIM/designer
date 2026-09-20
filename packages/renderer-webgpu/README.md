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

## Where the contracts live

| contract | made true in |
| --- | --- |
| X3 — BackdropFrame protocol (this child owns its operational detail) | `src/backdrop.ts` |
| X5 — colour pipeline | `src/color.ts`, `src/wgsl/prelude.ts` |
| X8 rider 2 — concentric renders as a level set of the parent's field | `src/instances.ts`, `src/wgsl/field.ts` |
| §Core model — ≤1 pyramid rebuild per dirty source per frame | `src/rebuild-ledger.ts` |
| Decision Log #19 — the dual refraction cap | `src/material.ts` |
| Decision Log #20 — family C's f32 cross-check | `src/governor.ts` gates it; `test/f32-cross-check.test.ts` and `e2e/gpu/cross-check.spec.ts` run it |

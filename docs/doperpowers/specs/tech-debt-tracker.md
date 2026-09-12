# Tech debt tracker

Small, real defects that were found while doing something else and deliberately
not fixed there: too minor to justify widening a change's blast radius, but not
so minor that the next person should have to rediscover them. One entry each —
what is wrong, how it shows up, and the shape of the fix, so picking one up is
an implementation job rather than an investigation.

Entries are removed when they are fixed, not struck through: the commit is the
record.

---

## The e2e suites inherit the machine's accessibility settings

*Found 2026-08-29, during the overlap-check narrowing.*

Chromium answers `prefers-reduced-transparency` and `prefers-contrast` from the
operating system's own settings, and Playwright can emulate neither (it covers
`reducedMotion`, `forcedColors`, `colorScheme` and `contrast`). So a developer
who has macOS *Reduce Transparency* switched on — or a capture session that
switched it on and did not switch it back — runs a different suite from CI's.

Observed: with `reduceTransparency = 1` system-wide, seven `@vitreajs/vitrea-web`
e2e cases fail on a clean tree, in four specs — `e2e/shared/proxies.spec.ts`,
`e2e/shared/media-policy.spec.ts`, `e2e/shared/probe.spec.ts` and
`e2e/pixel/proxy-pixels.spec.ts`. They fail with σ = 14 artifacts where they
expect σ = 8: proxy boxes padded 42 instead of 24, `blur(14px)` instead of
`blur(8px)`, `refraction: "reduced"` instead of `"nominal"`. Nothing is wrong
with the runtime; the tests are reading a preference nothing in the test set
asked for.

There is a second-order version of the same fault that is worse, because it
fails *silently* rather than loudly: a fixture that frames a scene, clears
diagnostics, and then flips the preference is asserting on the difference the
flip makes. With the preference already on system-wide, the "before" frames are
already the "after", every finding lands before the clear, and the diagnostics
channel's dedupe (keyed by code and subjects) then suppresses the re-report — so
the test sees an empty list and passes for the wrong reason.

**The fix shape**, applied already in `e2e/shared/accessible-padding.spec.ts` and
`e2e/shared/overlap.spec.ts`: state the preference instead of inheriting it —
`window.h.requireRoot().setAccessibilityOverrides({ reducedTransparency: false })`
immediately after `createRoot`, in every case whose subject is not the system
state itself. Same for `increasedContrast` where a case depends on it.

`e2e/shared/media-policy.spec.ts`'s "reports the nominal policy when the system
asks for nothing" is **exempt by design**: its subject *is* what the platform
reports when the system asks for nothing, so pinning an override would gut it.
That case genuinely requires the machine's preferences to be off, and it is the
one that should stay loud about it.

## The shape axis mis-segments a glowing interior over a near-tone backdrop

*Found 2026-08-30, fixing the W1/coherence press-glow divergence.*

`extractSilhouette`'s `luminance-delta` rule calls a pixel "inside" when it
differs from the shared background raster by more than 0.02 linear luminance
(`DEFAULT_SILHOUETTE_THRESHOLD`). The press glow sweeps the interior smoothly
from the material's own level up toward the highlight, so on a dark backdrop it
*crosses* the backdrop's level somewhere inside the surface — and the extractor
punches a ring-shaped hole through the middle of the silhouette there. The
contour trace then runs around the hole, and the shape axis reports a contour
error that is a segmentation artifact rather than a geometry one.

Measured on `photo__capsule-button__pressed`: both tiers now read contour p95
12.93/13.0 at 1× and 26.0/27.0 at 2× with IoU ~0.86, against ~0.92 and 4–6px for
the same surface unlit. The texture tier has carried these figures since the
scene was added; the dom tier joined it once it started drawing the glow. The
dark profile's own `$comment` already names the underlying property — over a
backdrop of its own tone the reference sits within 0.02 of it — so this is that
limit reaching the web side through a new route.

**The fix shape:** the extractor needs a rule that does not assume the surface is
monotonically separated from its backdrop — hole-filling the mask before the
contour trace is the cheap version; extracting the web silhouette from alpha over
a transparent capture is the honest one, and would need the capture harness to
render the scene twice. Either is a calibration-instrument change and must not be
made by tuning the 0.02 threshold, which would move every cell.

Until then: **the dark profiles' contour thresholds cannot be proposed from this
cell** (the post-v1 wave's W1/coherence entry already parks them behind the fix,
for what turns out to be this reason).

## The CSS tier's press glow does not fall across the label

*Found 2026-08-30, same fix.*

X1's sandwich puts the highlight canvas above the semantic host precisely so a
highlight can fall across the label. The CSS tier has no layer above the host, so
its press glow — a `background-image` on the host itself — paints under the text.
The interior level is coherent between the tiers; what a pressed label looks like
is not.

**The fix shape:** an `::after` rule in `ink-stylesheet.ts` carrying the same
gradient, fed the numbers through custom properties. It must not introduce
`opacity`, `filter`, `mask`, `clip-path` or `mix-blend-mode` on anything the
proxies live inside (`planes.ts`'s constraint), which a plain background does not.

## `merge-distance-below-padding` still quotes the retired 17/255

*Found 2026-08-30, extending that narrowing to core.*

`packages/core/src/scene.ts` (the message at the `merge-distance-below-padding`
report, and the `DEFAULT_GROUP_SAMPLING` docblock above it) describes the
within-group case as "drifting up to 17/255". That figure is S1's cross-group
8px-gap row, and the overlap experiment
(`spikes/s1-proxy-topology/overlap-experiment/` §4.5) showed most of it to be
the clip path's corner antialiasing — a separation-independent cost of splitting
a proxy, not a leak. The cross-group messages have been reworded; this one was
left alone because it is a different mechanism (members inside one group that
did not merge) and nothing has measured *it*.

**The fix shape:** either measure the unmerged within-group case and quote what
it actually is, or drop the magnitude and let the message describe the mechanism
alone. Quoting a borrowed number is the one option that should not survive.

## `packages/react`'s press and morph specs are flaky on Firefox

*Found 2026-08-30, running the suites for the tint API (W3).*

Two to four cases in `packages/react/e2e/press.spec.ts` and `morph.spec.ts` fail
on the `firefox` project on any given run, and a **different** subset each time:
across three consecutive runs of one unchanged tree the failures were
{morph reversal, press compression, glow attack/decay, keyboard press}, then
{morph reversal, press compression}, then {press compression, glow, keyboard}.
Chromium and WebKit pass every time. Every affected case asserts a *driver output
at a moment* — a compression partway through a spring, a glow between attack and
decay — so the likely mechanism is Firefox's frame pacing under Playwright rather
than anything in the motion drivers.

This is invisible in CI because the react e2e suite is not run there
(`.github/workflows/ci.yml` runs only `@vitreajs/vitrea-web`'s), which is its own
half of the problem: a suite nobody runs is a suite nobody can trust.

*Re-measured 2026-08-30, at the end of the deferred API round (W5), over four
consecutive full runs of one unchanged tree: **0, 2, 4, 4** failures, always from
the same four candidates and always only on `firefox`.* Two things that adds.
First, a fully clean run happens — so "it passed" is not evidence that a change
is safe, and the only usable signal is the distribution over several runs.
Second, the rate drifts within a session: W5's morph child measured the *same*
baseline at 0, 6 and 7 failures an hour earlier. Anything triaging against this
entry should compare distributions rather than single runs, and should expect
the comparison to be noisy in both directions.

**The fix shape:** make the assertions bracket the driver's trajectory rather
than sample it — poll for the channel to cross a threshold, the way the
accessibility specs already `expect.poll` — and then put the suite in CI, because
a flake visible only locally will keep being triaged as "probably pre-existing"
by everyone who meets it.

## ~~The untinted material's ink is still decided by the colour scheme~~ — CLOSED 2026-09-10 by W27a

*Found 2026-08-30, building the tint API (W3).*

`boundedForegroundLevel` decides a surface's ink with no backdrop hint at all
whenever the level's whole reachable range lands on one side of the crossover —
provably, because the level is monotonic in the backdrop. W3 wires it in only for
surfaces carrying an **author** tint, leaving the untinted material's behaviour
exactly as it was.

The same reasoning applies to the untinted material, and there it would fix a
real defect: at the measured `tintAlpha` of 0.62 the CSS tier's converted alpha
is ~0.78, so a hintless surface is at least 78% of the way to its (white) tint,
and `light-dark()` in a dark colour scheme then puts the light ink on a near-white
surface. That is K5's failure class, still reachable through the no-hint path.

Left alone deliberately: it changes `--vitrea-foreground` on every untinted
surface in the library, and the untinted material's behaviour belongs with the
child that owns its adaptation (W7) rather than with the one that added a colour
axis.

**The fix shape:** drop the `surface.tint === undefined` guard on `level` in
`packages/platform-web/src/css-tier.ts`, and the matching `seed === undefined`
guard in the GPU tier's ink in `root.ts`, then re-baseline whatever pins
`light-dark(` for a hintless surface. Worth doing with W7's measurements in hand,
not before.

**CLOSED 2026-09-10 by W27a** (commit *"platform-web: the untinted material's ink
is decided by the material, on both tiers"*), as the fix shape above described it
and with two corrections to what it predicted.

Both guards are gone and `boundedForegroundLevel` is now one rule over every
surface; its own docblock in `optics.ts`, which named the tinted-only scope as
deliberate, was rewritten rather than left to contradict the code.

What the re-baseline actually cost was **five** assertions, not the "whatever pins
`light-dark(`" the entry expected, and four of them were not about the untinted
material at all: `css-tier.test.ts`'s block on X6 hint shapes that carry no usable
tone (`mixed`, `fixed`, `sampled-async`, and no hint) pinned `light-dark()` as
each one's *outcome* where the property being tested is that the four are
indistinguishable from each other. They now pin the material's own answer and the
indistinguishability directly (`toEqual` over the whole render), which is the
stronger claim and the one those cases were always about. The fifth is
`tint.test.ts`'s "leaves an untinted hintless surface on the scheme's own answer",
which pinned the defect by name.

The regular variant's bracket lands wholly above the crossover, so a hintless
untinted surface now takes `#1c1c1e` for every backdrop there is. The **clear**
variant's still straddles it and still resolves to `light-dark()` — at its alpha
the backdrop genuinely does decide — so this is the material answering rather than
a blanket flip, and a new case in `css-tier.test.ts` pins that pair.

Not re-measured against the reference: this moves a token, not a pixel, and no
calibration cell reads `--vitrea-foreground`.

## The dark scheme's own material leaves the primary ink at 4.95 over a bright backdrop

*Found 2026-09-10, deriving the named ink levels' alphas (W27a).*

Solving `inkAlphaHoldingContrast` across the material's reachable level range to
choose `--vitrea-foreground-secondary`'s alpha turned up a reading about the
**primary** ink that nobody had taken. The dark profile's GPU-tier level runs
`[0.2348, 0.4169]` (`gpuTierForegroundBounds(sourceOptics(darkMaterialProfile).regular)`),
and the top of that range — the dark material over a white backdrop — puts the
light ink `#f5f5f7` at a WCAG contrast of **4.945** against a 4.5 floor. The
light scheme has room to spare on the same instrument (7.29 at its darkest
reachable level of 0.665, 8.26 on the GPU tier); the dark scheme has 0.445 of
headroom, which is roughly one 8-bit step of the level.

Two consequences, one of them already visible. W27a's secondary level is
therefore raised to 0.924 on exactly that surface — the token is honest, but the
scale it belongs to has collapsed onto the primary there, and an app reading
`--vitrea-foreground-secondary` on dark glass over a photo gets no visible second
level. The other is that the primary itself is one profile tweak away from
failing AA, and nothing currently watches it: the adopted-threshold suite
measures fidelity to Apple, not legibility, so a retune could take the ink under
4.5 with every bound still green.

**The fix shape:** the same instrument the alphas are chosen with, run as a
guard. A test that walks both schemes' and both tiers' reachable level ranges and
asserts the *primary* ink holds 4.5 would fail today, which is why it is recorded
here rather than added — landing it is a decision about the ink tokens or the
dark profile, not a test. The two candidate resolutions are a darker light ink
(`#f5f5f7` is 0.898 linear; pure white would buy about 0.24 of contrast on this
cell) and moving `foregroundCrossover`, which is derived rather than chosen and
would have to be re-derived from whatever pair replaced it. Worth doing with the
dark profile's next re-fit in hand.

## The renderer's CPU-side `lensDepthPx` readout ignores the lens channel

*Found 2026-09-10, lifting the channel's upper clamp (W27a).*

`resolveSurfaces` in `packages/renderer-webgpu/src/instances.ts` publishes
`lensDepthPx` per surface — documented there as "the CPU's reading of" the depth
the shader evaluates — and computes it from `shape.channels.thickness` alone,
with no `lensStrength` term. Before W27a that was wrong only for a disabled
surface (0.5, the one value the old clamp let through). It is now wrong for every
interaction state: hover, focus, press and morph all scale the shader's depth and
none of them moves the readout.

Nothing reads it in anger today, which is why W27a left it alone — the shader
evaluates both depths from the `lensThick` slot and the span, and the readout is
a reporting field. But the honesty core's rule is that a readout says what
actually drew, and this one says what would have drawn at rest.

**The fix shape:** fold the same `max(0, lensStrength)` into the `lensDepthOf`
call, and check whether any capture cell or readout consumer was silently relying
on the resting value — a cell that samples a pressed surface would start
reporting a different number, which is the point.

---

## ~~The renderer's eight GPU goldens are stale, and have been since W2~~ — CLOSED 2026-09-01

*Found 2026-08-30, during the deferred API round (W5). Closed by the flip's landing (`263f004`).*

`packages/renderer-webgpu`'s golden suite fails 16 of 22 on a clean tree at
`b6dcbac` — both `e2e/golden/scenes.spec.ts` (each scene against its committed
PNG) and `e2e/golden/isolation.spec.ts` (each scene re-rendered under the
pre-C9a profile). `field-mask` reports a max channel delta of 8 against an
allowed 4; the largest is `lens-size-scaling` at 32.

Nothing is wrong with the renderer. The goldens were last recorded at `f028b2a`,
and `packages/renderer-webgpu/src/material.ts` has changed twice since — W2's
size law (`21e87ed`) and W7's backdrop tone adaptation (`7eec80c`). Both moved
the material on purpose. Neither re-recorded the bed, and nothing caught it,
because `pnpm run ci` runs no Playwright at all and `.github/workflows/ci.yml`
runs only `platform-web`'s suite.

**Why this matters more than a red suite.** The golden bed is the only
instrument that can say a renderer change left the pixels alone. W5 needed
exactly that twice: the refraction-ladder dedup proved byte-identity by running
the bed before and after and showing the *failure figures* and the rendered-byte
md5s unchanged, which works but is a workaround; and per-corner radii were
re-deferred partly because a change to v1's corner algebra cannot be landed
against a bed that cannot say whether it moved.

**The fix shape:** re-record the eight goldens, as a fidelity judgment against
the calibration cells rather than a mechanical `goldens:regen` — Decision Log
#30(d) is explicit that regeneration is a judgment, and `isolation.spec.ts`'s
`SUPERSEDED` mechanism exists to carry the argument for why a delta is correct.
It belongs to whoever owns the material change (W2 and W7 between them), not to
an API round. Worth pairing with the second half of the problem: a suite CI does
not run is a suite nobody can trust, which is already recorded above for the
react specs and is the same root cause here.

**Updated 2026-08-31 (the recalibration cascade).** Still red, now 16 of 34, and
deliberately not re-recorded here. The material moved a third time and much
further — eleven constants, refitted against the active-pose bed (claims §5.13) —
so every golden and every isolation case is stale by construction rather than by
neglect. Re-recording was declined for a reason the earlier entry did not have:
the refitted material is a **proposal awaiting the human gate**, and baking an
unadopted configuration into the golden bed would make the bed assert a claim
nobody has approved. The regeneration should ride the adoption, in one commit
with it.

One structural note for whoever does it. `isolation.spec.ts` is built to prove
that "the C9a delta is exactly the two tuned constants" by re-rendering each
scene under a patch that restores the pre-C9a values of `tintAlpha` and
`adaptiveTint`. That argument cannot be made at all now: the cascade moved
`blurSigma`, `shadowAlpha`, `sizeShadowGainMax`, both tint-tone constants, two
backdrop-tone constants and two outer-shadow amplitudes as well, so a two-constant
patch no longer isolates anything. The spec needs its patch widened to the full
refitted set — or its claim restated as "the delta is exactly the constants this
profile names", which is the version that survives the next retune too.

**CLOSED 2026-09-01, in `263f004`, riding the adoption exactly as the entry above
asked.** Decision Log 22 landed the flip; the goldens were re-recorded in the same
commit that adopted the material, so the bed never asserted an unapproved claim.
Eight moved; `highlight-press-glow` did not, and its hash is still byte-identical
to the 2026-08-25 original through C9a, W8 and this wave — which is what makes the
other eight legible as facets rather than as drift.

The structural note above was right and the resolution went further than either
option it offered. Widening the patch to the full refitted set would not have
worked: the wave also moved **shader and pass code** (`passes.ts`, `renderer.ts`,
`wgsl/optics.ts`, `wgsl/highlight.ts`), and no value injected through the material
profile seam can reconstruct a renderer whose shaders differ. So the
reconstruct-the-old-renderer reading was retired rather than patched, and
`isolation.spec.ts` is now a **pinned-bytes regression guard over a named
configuration**: these are the bytes today's renderer produces from one explicitly
written patch, and anything that moves them — constant, shader, pass or geometry —
fails and must be attributed before the table is touched.

`sizeOcclusionGain` was deliberately left OUT of that patch. Naming it would have
made the hashes reproduce across the wave, and would have bought that by blinding
the guard to the very constant the wave had just refitted. Coverage beat
continuity.

**What is NOT closed** is the second half this entry named: a suite CI does not
run is a suite nobody can trust. `pnpm run ci` still runs no Playwright, and
`.github/workflows/ci.yml` still runs only `platform-web`'s suite, so the bed can
go stale again silently. That remains open under the react-specs entry above and
is the reason this debt was found by a person rather than by a build.

---

## `vitrea-web`'s published declarations alias core's `RefractionQuality`

*Found 2026-08-30, during the refraction-ladder dedup (W5).*

`packages/platform-web`'s emitted `dist/index.d.ts` imports core's
`RefractionQuality` as `RefractionQuality$1`, because `root.ts` takes the type
from `@vitreajs/vitrea` while the package's own re-exports carry
`@vitrea/policy`'s. The two are structurally identical and no consumer can tell,
so this is cosmetic.

It is recorded rather than fixed because the obvious fix is arguably the wrong
one: `root.ts` taking a core type from core is correct layering, and re-pointing
it at the leaf package to tidy a declaration would invert that. Core itself used
to have the same collision and no longer does, so the workspace is net one
better off either way.

**The fix shape:** if it is worth doing at all, have `@vitreajs/vitrea`
re-export policy's type as the identity it already is and confirm the two
resolve to one declaration in the emitted `.d.ts` — a build-output check, not a
source change.

## ~~Ten `vitrea-web` chromium e2e cases fail at HEAD with nominal system settings~~ — CLOSED 2026-09-04

*Found 2026-09-03, during W11c G1's verification (the worker reproduced all ten
by stashing the change; the seven padding/proxy cases were already failing in
W11a's run on 2026-09-02).* System `reduceTransparency` and `increaseContrast`
both read 0, so this is not the entry above.

- Seven still expect the CSS tier's blur from before the 2026-08-31 refit
  (σ = 8, padding 24): `e2e/shared/accessible-padding.spec.ts` (four cases:
  "and it still fires where the leak is real…", "the geometry really is at
  the floor…", "an author's own padding keeps their number…", "nothing moves
  at the nominal state…"), `e2e/shared/overlap.spec.ts` ("reports an overlap
  that only the 3σ floor creates") and `e2e/shared/proxies.spec.ts` ("raises
  a padding below 3σ of the group's blur…", "emits both spellings of the
  filter"). The fix is to derive their expected numbers from the resolved
  material (`requiredSamplingPadding(cssTierOptics().regular.blurRadius)` and
  the scatter-widened σ at the surface's span since W11c) rather than from
  literals.
- Three pixel cases read identical values at HEAD and after W11c:
  `e2e/pixel/backdrop-tone-pixels.spec.ts` ("an ordinary backdrop moves
  nothing at all" reads 0.773 where it expects no movement; "the response
  across the transition is continuous and monotone" reads 0.666) and
  `e2e/pixel/tint-pixels.spec.ts` ("stays glass — the backdrop still varies
  through a tinted surface", spread 0). Unattributed; they need their own
  read against the W9/W10 laws (the tone response and the opaque tint both
  moved what these assert on) before anything is re-recorded.

The `chromium-gpu` project (nine cases) and the renderer's golden/gpu suites
are green; these ten are the CSS-tier project only.

**Closed 2026-09-04 (observed at the W16 landing).** The whole platform-web Playwright suite
passes on the landed tree, four projects, 342 cases. The seven padding and proxy cases were
re-derived from the resolved material at W13 G1's review (`8f00c0c`: the e2e helper reads the
law like the tier), and the three pixel cases at `35a2311` (the suites read the W9 and W10 laws);
neither commit closed this entry, so it is closed here on the green run.

## Texture placement, deferred edges (claims §5.47, 2026-09-03)

- **Partial overlap.** A surface hanging past a placed texture's box samples
  the clamped edge texel out there; the W11a unsampled layer (the material as
  a browser-composited layer) is not applied to the part of a surface no
  texture is under. Right answer: split the surface's footprint at the box's
  edge — layer outside, sampled inside — which is a per-pixel branch in the
  optics pass on `refractedUv` leaving [0, 1]. Deferred until a page needs it.
- **Anisotropic placement.** A box that distorts its source (an `<img>` under
  `object-fit`, a CSS-stretched canvas) has two densities and the body blur has
  one σ; the width's is honoured. A per-axis σ is a separable-pass change.
- **Declared placements do not follow layout.** `placement: { kind: "rect" }`
  is a fixed box until the app calls again; `{ kind: "element" }` is measured
  like a source element. An `ImageBitmap` drawn for a `<div>` should declare
  the element, not the rect — said in the type's doc, not enforced.
- **Both tiers over-fill their declared contour** (W14 G0, 2026-09-03; claims
  §5.62, `results/2026-09-03-w14-shadow/g0/g0-instrument.md` §4). Measured by
  the shadow instrument's guard at the contour: the GPU tier's capsule
  over-fills by 3.5–4 CSS px at the caps, the CSS tier by 3–3.5 CSS px toward
  the bottom right on every component at both scales; Apple over-fills by ≤ 1.
  The shape axis is bounded to the declared region (claims §5.12) and cannot
  see it. Shape of the work: run the guard on every cell, then find the cause
  (the field's coverage ramp on the GPU tier; the CSS tier's box against its
  border-radius and shadow spread) — its own small round, W14 Deferred.

## The demo's law readout does not carry the device scale (W12 G3 / W13 G1, claims §5.56, §5.61, 2026-09-03)

`apps/demo/src/laws/law.ts`'s `bodyLaw` reports the sharp width, the scatter
width and the CSS tier's single σ at the shipped constants and at no device
pixel ratio, so the three numbers it prints are the law at dpr 1. The GPU tier's
two widths are device-pixel quantities (W12 G3), so on the Retina display most
visitors read the page on, the widths that tier actually draws are half the
printed ones; the CSS tier's single σ is the printed one at every scale by
decision (W13 Decision Log 5, 2026-09-03), so for that tier the readout is
right and the sentence above is about the GPU tier alone. Since W13 G1 the readout is also one projection short of the
truth: the GPU tier mixes by the pixel's own depth under the contour and the
number printed is that ramp's area average, which is what the CSS tier renders
and not what the GPU tier does anywhere in particular. The fix is to thread
`window.devicePixelRatio` into `bodyLaw`, show it as a fourth readout, and say
that the mix is an average over the surface. Small and self-contained, and a
documentation gap rather than a fidelity one: nothing the runtime draws is
affected.

**Amended 2026-09-04 (W13 Decision Log 8, user-decided).** The first half of
this entry rested on a premise the bed withdrew: the body's two widths are *not*
device-pixel quantities on either tier. W13 carried W12 G3's reading into its dry
runs and retired it — at 2x the ramp is a null, so the halved widths were the
only change at that scale, and they moved the four large checkerboard rows the
wrong way (claims §5.68). Both widths are CSS px at every scale, so the readout's
two width numbers are right as printed on both tiers and no Retina visitor reads
a doubled value. What stays open is the other half, and only that: the printed
mix is the depth ramp's area average read at dpr 1, while the GPU tier mixes per
pixel and projects the ramp with the 2x start and reach on a Retina display. The
remaining fix is smaller than the one above — thread `window.devicePixelRatio`
into `bodyLaw`'s projection and say in the readout that the mix is an average
over the surface. Still a documentation gap and not a fidelity one.

**Amended 2026-09-04 (W16 landing, claims §5.72 §1, §5.73 §7).** The sentence above about the
CSS tier is superseded: the tier's two widths are device-pixel quantities through the live ratio
at the renderer's effective kernel width (1.380× at dpr 1, 1.485× at dpr 2), so it no longer draws
the printed 1x σ at every scale, and the GPU tier's 2x body has its own second-scale terms since
W15. The readout is now short on both tiers by the device scale, and on the CSS tier by the
effective-width ratio as well. The fix keeps its shape — thread `window.devicePixelRatio` into
`bodyLaw`, show it, say the mix is an average over the surface — and gains one line for the
CSS tier's ratio. Still a documentation gap.

## The CSS tier's reduced-transparency proxy spec is flaky on WebKit in CI

*Found 2026-09-03, watching CI over the W13/W14 wave commits.*

`packages/platform-web/e2e/shared/proxies.spec.ts:203` ("honours reduced
transparency by frosting harder, and never occluding less") failed on the
`webkit` project of the `platform-web integration` job on commit `3c76f8a`,
which changes two specs and no code: `blur(reduced)` read **4.79 against a
nominal 4.79**, where the assertion wants strictly greater. Both the retry
inside Playwright and a re-run of the whole job on the same tree passed, and
the 338 other cases passed throughout; the sibling commits either side
(`3fb3b7c`, `2c16b2a`) were green.

The mechanism is the one this tracker already names for `packages/react`'s
motion specs: the case asserts a **computed value at a moment**. It applies the
override, sleeps 400 ms and reads the style once. The transition is 240 ms
(`NOMINAL_DURATION_MS`), so the wait is sound when the page is scheduled
promptly and is not sound when a loaded CI runner starves the frames — the
reading equal to nominal to the last digit is a transition that had not
advanced, not a policy that failed to frost.

**The fix shape:** `expect.poll` the blur until it exceeds nominal, with a
timeout well past the transition, the way the accessibility specs in this same
suite already do. That converts "the material frosted harder within a bounded
time" — which is the claim — into the assertion, and stops the wall clock being
part of the contract. The occlusion assertions below it read a settled value
and are unaffected.

**Recurred 2026-09-04** on `e59b900` (W16 G1 DECLARED, a docs-only commit): the same case on
`webkit`, the in-run retry failing too, the 341 other cases green; the next push (`862b65e`,
the W16 landing) was green on every job. Second occurrence; the fix shape above stands.

### Release chain: the publish order leaves a window where the pair is uninstallable (2026-09-04)

At the 0.4.0 cut `changeset publish` (through `pnpm release`) put `@vitreajs/vitrea-web@0.4.0`
and `@vitreajs/vitrea-react@0.4.0` on the registry at 17:25:44Z / 17:25:46Z and
`@vitreajs/vitrea@0.4.0` — the package both depend on at `^0.4.0` — at 17:26:57Z. For those 70
seconds a cold `npm install @vitreajs/vitrea-web@0.4.0` failed with `ETARGET` (no matching
version for `@vitreajs/vitrea@^0.4.0`); after, all three resolve. The cause is not in the
artifacts: with npm 2FA each package's publish waits on its own one-time code, and the order
the codes were entered put the dependency last. The window is small and closes on its own,
but a dependent that is installable before its dependency is a real state of the registry.
Shape of the fix, if it is ever worth taking: publish in dependency order explicitly
(`pnpm publish -r` honours the workspace's topological order and can take the OTP once via
`--otp`), or accept the window and say so in the release checklist. Evidence: registry
`time` fields; the failed cold install at 17:26:38Z and the passing one after.

**Second occurrence, the 0.5.0 cut (2026-09-04):** the same shape at 73 s —
`@vitreajs/vitrea-web@0.5.0` at 23:03:34Z and `@vitreajs/vitrea-react@0.5.0` at 23:03:36Z,
`@vitreajs/vitrea@0.5.0` at 23:04:47Z (registry `time`). Two cuts in a row make the order a
property of the chain rather than of one evening; the fix above stays the shape, and the
choice of taking it is still the user's.

**Third occurrence, the 0.6.0 cut (2026-09-04):** the same shape, wider — `@vitreajs/vitrea-web@0.6.0`
at 11:22:13Z and `@vitreajs/vitrea-react@0.6.0` at 11:22:15Z, `@vitreajs/vitrea@0.6.0` at
11:26:21Z (registry `time`): 248 s against 70 and 73. Three cuts; the fix above is unchanged
in shape and the choice is still the user's.

**Fourth occurrence, the 0.7.0 cut (2026-09-04):** the same shape, wider again —
`@vitreajs/vitrea-web@0.7.0` at 16:38:28Z and `@vitreajs/vitrea-react@0.7.0` at 16:38:33Z,
`@vitreajs/vitrea@0.7.0` at 16:42:55Z (registry `time`): 267 s against 70, 73 and 248. Four
cuts, the window growing with each; the fix above is unchanged in shape and the choice is still
the user's. The cold install this time waited for the window to close and passed first time.

**Fifth occurrence, the 0.8.0 cut (2026-09-05):** the same shape, and read from inside the
window this time — `@vitreajs/vitrea-web@0.8.0` at 06:40:39Z and `@vitreajs/vitrea-react@0.8.0`
at 06:40:41Z, `@vitreajs/vitrea@0.8.0` at 06:44:45Z (registry `time`): 246 s against 70, 73,
248 and 267. A registry read at 06:44:07Z still listed core at 0.7.0, and a cold
`npm install @vitreajs/vitrea-web@0.8.0` failed with `ETARGET` on `@vitreajs/vitrea@^0.8.0`;
the read at 06:47:57Z had all three and the cold install passed. Five cuts, the window at
four minutes on the last three; the fix above is unchanged in shape — `changeset publish`
starts the three publishes concurrently and each waits on its own one-time code, so the order
is whichever prompt the user answers first, where `pnpm publish -r` publishes sequentially in
the workspace's topological order and takes one `--otp` — and taking it at the next cut is now
the parent's recommendation rather than an open choice (the wave doc's 0.8.0 addendum).

**Sixth occurrence, the 0.9.0 cut (2026-09-06):** the same shape, narrower this time —
`@vitreajs/vitrea-web@0.9.0` at 08:47:04Z and `@vitreajs/vitrea-react@0.9.0` at 08:47:06Z,
`@vitreajs/vitrea@0.9.0` at 08:49:09Z (registry `time`): 124 s against 70, 73, 248, 267 and 246.
A cold `npm install` of the three at 08:49:01Z failed with `notarget` on `@vitreajs/vitrea@0.9.0`
and passed at 08:49:33Z. Six cuts; the fix above is unchanged in shape and remains the parent's
recommendation for the next cut, the user's call.

**Seventh occurrence, the 0.10.0 cut (2026-09-08):** the same shape, the narrowest yet —
`@vitreajs/vitrea-web@0.10.0` at 01:19:42Z and `@vitreajs/vitrea-react@0.10.0` at 01:19:44Z,
`@vitreajs/vitrea@0.10.0` at 01:20:35Z (registry `time`): 53 s against 70, 73, 248, 267, 246
and 124. No install was attempted inside the window; the cold install after all three were
listed passed. Seven cuts; the fix above is unchanged in shape and remains the parent's
recommendation for the next cut, the user's call.

## The CSS tier's captures move by a code between runs on two 2x cells (W15 G2, W16 G2, 2026-09-04)

*Found at W15's landing (one cell), confirmed at W16's.* Re-capturing the CSS tier from an
identical build reproduces every row to the fifth decimal and every capture byte-for-byte except
a few 2x cells over a flat or photo backdrop, which differ by 1–2 codes with alpha untouched:
`light-solid__rrect-md__rest` at W15 (2 codes, 9 853 px); `light-solid__capsule-button__rest`
(473 px) and `photo__capsule-button__rest-tint-blue` (1 203 px) at W16, 1 code each, with no
row moving past 0.000008; `photo__toolbar-group__rest` under increased contrast at W17's
landing (96 px, 1 code, no row past 0.00005); `checkerboard__glass-over-glass__rest` on the 2x
dark profile (6 408 px) and `hc-text__capsule-button__rest` at 2x light (746 px) at W18's
landing, 1 code each with alpha untouched, no row past 0.00003 — the fifth wave in a row, and
the fix's shape unchanged. The GPU tier reproduces 115 / 115 every time. The tier's capture is a
Playwright element screenshot of a page whose `backdrop-filter` layers the compositor rasterises
on its own cadence, so the shot lands on one of two frames that differ by rounding — the
harness's, not the tier's. Shape of the work: settle the page (two animation frames after the
last style write) before the screenshot in `cli/compare.ts`'s CSS path, then confirm on a
from-empty rebuild. Below any bound and any floor's epsilon; recorded so the next byte-identity
scan does not chase it.

*W19 (2026-09-05), the pair's shape sharpened:* the same two cells, one code, at the same pixel
counts (746 and 6 408) — but W19's dry run, its second run and its canonical rebuild, three
Chromium processes on one day, are byte-identical to each other on both cells and differ only
from W18's landing captures. The pair flips between landings, not within a day's runs, which is
what a byte-identity scan should expect: a same-day control isolates a change from it exactly
(W19 Decision Log 4 (1); claims §5.81 §4, §5.82 §1). The fix's shape is unchanged.


*Addendum 2026-09-07 (W21 G2 and G2c):* a third cell — the increased-contrast dom
`photo__toolbar-group__rest` — differed from the W20 bed by one code on 17 of 64 000 edge pixels
at G2's rebuild, reproduced the landed bytes on an immediate re-capture, and reverted to the W20
bytes at G2c's re-capture: a session byte-state, settled as such because a material change does
not reverse itself (claims §5.91 §1, §3).

## Six unverified Codex findings on the W18 CSS tint path (2026-09-05)

*Found 2026-09-05, as a side effect of the designer-skill stance-derivation work.* The
skill initiative's third Codex review (`gpt-5.6-sol`, xhigh) ran against `33fc55e` after a
rebase that pulled in W18's `packages/platform-web` commits, so its diff covered that code.
The skill diff drew no findings; all six below are in the runtime and are **not verified**
by the session that logged them — it did not own the code and did not touch it. Each names
a file and line as of `70a588c`; treat them as leads for the W18 owner, not as accepted
defects.

1. **P1 — `css-tier.ts:988-990`**: on Chromium's linear path with an `authorLayer`,
   `cssTierTintTable` is solved for the overlay `(optics.tint, floorAlpha)` but the branch
   paints `(authorLayer.color, authorLayer.strength)`, so the compensating table no longer
   composites to the requested material and sub-floor strengths drop the contrast floor.
2. **P2 — `root.ts:1374`**: `cssTintForms` is cleared before `stateFor(groupId)` is copied
   into `groupInputs`, and repopulated at ~1913, so `root.renderInput().groups[*].state`
   omits `cssTint` on every CSS frame while `capabilities()` includes it.
3. **P2 — `css-tier.ts:533-535`**: the clear variant's floor returns a constant `0.2668`
   from the shipped defaults instead of resolving from the active material profile.
4. **P2 — `css-tier.ts:772-775`**: `cssTierDeclarations` is still re-exported and
   `CssTierSurface.policy` still describes the policy fold, but the assignment discards the
   alpha from `opticsUnderPolicy`, so a direct caller gets nominal opacity under reduced
   transparency or increased contrast.
5. **P2 — `optics.ts:2196-2197`**: the rim band clamps `depth` by corner radius, so a
   square surface (radius 0) gets no band light while the WebGPU shader still lights the
   straight edges.
6. **P2 — `root.ts:1912-1913`**: `tintForm` is computed per surface but stored per group,
   so `capabilities()` reports the last host's form while another host in the group can
   draw the other one.

Shape of the fix: the W18 owner verifies each against the current tree; the ones that hold
become W18 follow-ups or their own entries here; the ones that do not are deleted from this
entry with a line saying why.

**Verified 2026-09-05 by the W18 owner against `8f57b0b`** (one worker, read-only, with a
scratch vitest kept at `~/.claude/jobs/5c70e47f/tmp/w18/findings/zz-w18-verify.test.ts`, not
committed). All six hold in some form; none is deleted. Disposition per finding:

1. **HOLDS — a W18 follow-up, chartered, not fixed in passing.** The transfer table is solved
   for the overlay `(optics.tint, floorAlpha)` and the branch paints the author layer at its
   own strength, so the composite misses the material by `(1 − s)·α₃/(1 − α₃)` of the gap
   between the material composite and the folded tint colour — at strength 0.2 by
   −0.053…−0.014 of linear luminance across backdrops 0.15–0.6, at 0.5 by −0.002…+0.025; the
   control without an author layer reproduces the material to 0.00004. Below strength
   0.2668 the painted alpha is under the contrast floor. The bed carries only strengths 1.0
   (insensitive by construction) and 0.5 (`photo__capsule-button__rest-tint-orange-half`,
   −0.0011 / −0.0005 against the GPU tier), so it cannot see the large end. This is the
   re-derivation W17 Decision Log 2 (c) promised if S5 fired on a tinted cell, and S5 did.
   A CSS-tier material change with a bed referee: W18 Deferred, "the author-tint fold on the
   linear path".
2. **HOLDS — fixed** (the fix wave after this entry): `renderInput().groups[*].state` omitted
   `cssTint` AND `cssShadow` (the finding understated it) while `capabilities()` carried both,
   because the state snapshot is taken before the per-host loop records the forms.
3. **HOLDS BUT BY DESIGN, one gap logged here.** The floor literal is pinned against the
   shipped profile's clear variant by two tests, so shipped drift is caught; W17 Decision Log
   4 (a) chose a named constant. The gap: a profile patched at runtime through
   `createGlassRoot({ materialProfile })` leaves the floor at the shipped number and the
   `α₃ ≤ α` condition unguaranteed. No adopted profile patches the clear variant; nothing on
   the bed or in the shipped build is affected. Closes with the floor read from the active
   profile's clear variant when the module-scope constraint that forced the literal is lifted.
4. **HOLDS BUT BY DESIGN; the public doc was the defect — fixed** (the same fix wave):
   `cssTierDeclarations` keeps the source alpha on purpose (W17 Decision Log 2 (b): the fold's
   occlusion lands on the source alpha before the response solve, and `root.ts` does the
   folding); `CssTierSurface.optics` now says so for a direct caller.
5. **HOLDS — a W18 follow-up, chartered.** `optics.ts` clamps the rim band's depth by the
   corner radius, so a radius-0 box gets no band light (`X` 0.000 at radius 0, 0.0016 at 0.5,
   0.0047 at 8) where the renderer's `rim_weight` is radius-independent and lights all four
   straight edges; a square CSS-tier surface draws about 0.003–0.005 of linear luminance under
   the renderer's. Inert on the bed (narrowest radius 8 CSS px against a 1.5 px band), so a
   gap the bed does not carry: W18 Deferred, "the rim band on square boxes".
6. **HOLDS (latent) — fixed** (the same fix wave): the group's `cssTint` was the last host's;
   it is now the weakest form across the hosts that declared one, as `cssShadow` folds, and
   the comment says so. Reporting only; what each surface draws is unchanged.

## The demo's reference-pair test reads `img.complete` without waiting for the load (2026-09-05)

*Found on the chain after the W18 post-landing fix merge; one run in three.* `apps/demo/e2e/
site.spec.ts` › "the reference pair is a comparison › both sides load, and the native capture is
a real image" evaluates `element.complete` and `naturalWidth` on the two `.pair__raster` images
straight after the section is shown, with no wait on the load; it failed once with
`complete: false` (the rest of the suite green) and passed on the immediate re-run, 34 / 34, as
it had on the landing tree half an hour earlier and on every prior wave's chain. Nothing in the
runtime is involved — the images are static fixtures. Shape of the fix: poll the assertion
(`expect.poll` on `complete`, or wait for the `load` event through `page.waitForFunction`)
before reading the natural size. Logged so the next chain that trips on it does not chase the
runtime.

## The reference harness loses cells to window activation with the machine idle (W19 G0, 2026-09-05)

*Found on W19's native ladder.* W9's protocol attests every cell (`presentedActive`,
`deterministic`, `materialRendered`, HID idle) and disqualifies a run that fails; W18's probe lost
one run to HID activity near the end, which is the failure the attestation was written for. W19
G0's run 7 lost six of twelve cells to `presentedActive: false` with 700–818 s of HID idle at start
and end — nobody was near the machine — so the session denying the window activation is a second,
distinct failure mode (`probe/provenance.json` in `results/2026-09-05-w19-author-tint-fold/`).
It costs runs rather than correctness: the protocol catches it, and a probe now banks seven attested
runs in about ten (W19: ten taken, eight attested). Shape of the fix: on a cell whose window fails
to present active, the harness retries the activation once after its own reset interstitial before
recording the cell as failed, and logs which activation path (`NSApp.activate`, the window's
`makeKeyAndOrderFront`) declined; then confirm over a probe bed that the retry recovers the cell.
Below every bound; recorded so the next probe budgets its runs.

## The shape axis clips both silhouettes to the declared region and cannot see a surface larger than declared (W20, 2026-09-05)

`component-region.ts` bounds both extractors to the scene's declared geometry (wave Decision Log
15 — the fix for the outer shadow being read as the surface, claims §5.11), and `silhouette.ts`
rules a pixel outside the region outside the silhouette whatever it holds. A surface that is LARGER
than declared therefore fills the region exactly and reads as perfect: on every capsule cell of the
canonical bed `silhouetteAreaWeb` = `componentRegionArea` = 4872, IoU 1.000, contour p95 0,
corner-curvature delta 0 — on both tiers — while the GPU tier has drawn every capsule with its
corner clamped to 0.327 of its height since v1 (claims §5.83; W20). The axis was blind in exactly
the direction the defect took. Shape of the fix, owned by W20 G0: the region dilated per side by
the corner budget where the shadow does not reach (left, right, above), or the tier's own raster
silhouette read from the optics canvas on a transparent page, so a surface up to its bounding box
shows; the referee is the capsule cells reading what the pixels say before the fix and about 1.000
after, with a synthetic dilation recovered beside the first reading. Until it lands, every
shape-axis figure on the bed is a lower bound on the contour error, not a measurement of it.

## A locked console session refuses the reference harness activation while HID idle and the power assertions look healthy (W21 G0, 2026-09-06; first read as a Screen Sharing failure, corrected the same day)

*Found on W21's dark probe; the whole gate blocked on it.* The harness captured 56 of 56 cells
byte-stable and every one attested `presentedActive: false` while `ScreenCaptureKit: OK` — the
Screen Recording grant is live and what is refused is activation (`isKeyWindow: false,
`NSApp.isActive: false`). The protocol's idle guard did not fire: HID idle read 5 038 s, the session
read on-console and logged in, and the power assertions showed nothing unusual once a coincident
Screen Sharing session (the first reading's culprit) had ended. What settles it is LaunchServices:
`lsappinfo front` → `loginwindow`, and `IOConsoleUsers` carrying `CGSSessionScreenIsLocked=Yes`. The
screen is locked — claims §5.17's failure mode, this time invisible to every signal the protocol
reads (claims §5.88 and its correction; evidence under
`results/2026-09-06-w21-dark-scheme/g0/blocked/`). System Events' `frontmost process` is the wrong
instrument for this: it reports the frontmost ordinary process, needs an Accessibility grant, and
cannot see `loginwindow`. The harness's tint guard reported the same fault as a colour fault and its
default deletes the staged bundle, which would have destroyed the evidence. Shape of the fix, two
parts: the harness reads the lock flag before the first cell and refuses the run naming it (the
probe runner already does from the shell, in one second, and stops after a first run that attests
fewer than 50 of 56); and the tint guard keeps the staged bundle beside its refusal rather than
deleting it. Below every bound; it costs a run and, without the up-front refusal, the diagnosis.

## The luminance-delta extractor perforates a silhouette that agrees with its backdrop over a checkerboard, and the contour rows measure the holes (W21 G2c, 2026-09-07)

*Found at W21's landing on the 2x dark nested pane.* A body that agrees with the reference sits
nearer its own backdrop, so over a checkerboard's white squares the 0.02 threshold loses it in
patches: the dom silhouette of `checkerboard__glass-over-glass__rest` at 2x carries 34 interior
holes (the texture tier's 40; the light bed's none), the conditioning predicate admits the cell on
area and bodies — holes are not among its arms — and `contourDistanceMean` / `P95` read 1.76 and
13.0 against ≤ 0.5 and ≤ 3.0 as every hole's boundary is measured as contour, while W20's
conformance rows read the same tier's drawn shape at `declaredIoUWeb` 0.99919 with a one-pixel
contour (claims §5.91 §3; §5.27's addendum; four floors). W17's and W18's mechanism in a third
place. Shape of the fix: an extractor arm that separates a surface from its backdrop by something
other than luminance (W11b's chroma arm was one; the alpha-coverage read W20 added is another, on a
transparent page), or a hole-fill step declared as part of the silhouette's definition with its
own recovery check. Four floors carried until then.

## Nine dark dom cells lose their declaration-conformance reading on the linear form (W21 G2c, 2026-09-07)

*Found at W21's landing.* On the CSS tier's linear form the material composites inside the sharp
layer's filter and only the contrast floor is an element paint, so the tier's alpha over the
transparent conformance page is the floor overlay's 0.267–0.271 and the coverage rule's 0.9 refuses
the reading ("declaration conformance NOT MEASURED"). The class has always held 24 of the 36
light-standard dom cells; W21's form ruling moved nine dark dom cells into it and one out (claims
§5.91 §3). The gate asserts conformance on the texture tier only, so nothing is red; it is a
measurement the bed carried and now does not. Shape of the fix: a conformance read for the linear
form that sees the filter's coverage — the optics canvas's alpha is what the texture tier reads,
and the dom tier's filter layer could expose an equivalent on the transparent page — or the
reading stays a texture-tier instrument by declaration.

## The highlight pass draws its specular sweep as a stationary band on the left edge of every resting surface, in both colour schemes (W21 G1, 2026-09-07)

*Found on W21's rim fit, read per side against a reference whose sides agree to three decimals.*
`packages/renderer-webgpu/src/wgsl/highlight.ts` draws the specular sweep as a Gaussian band centred
at `hu.sweep.x · 2π`, the motion driver's sweep channel; that channel is 0 at rest
(`render-model.ts`), and 0 radians in the gradient's angular coordinate is the left edge. Every
surface not being interacted with therefore carries a stationary shimmer on its left side: with the
rim's specular term at zero, the left edge reads 0.12–0.15 above the other three sides on every
solid, and the same documents with `sweepGain` 0 move the left side by −0.119 to −0.145 and every
other side by +0.0000 (claims §5.90 §4; `results/2026-09-06-w21-dark-scheme/g1/fit-rim.txt`). The
pass's own comment says Reduced Motion zeroes the gain because "the band is not drawn stationary,
it is not drawn" — at nominal motion it IS drawn stationary, and nothing had measured it; three
waves of rim work (W11c, W12, W18) fitted a two-light rim over it. On the canonical dark bed it is
the whole of W21 clause 4's miss (`dark-solid__rrect-md` +0.1394 at 1x, +0.2445 at 2x on the left
side). Shape of the fix, a renderer mechanism: gate the band's weight on the shimmer actually
running (the driver's channel non-zero, or a phase that parks the band off the surface at rest),
so a resting surface draws the ambient rim alone; then re-read the rim per side on both beds — the
light captures move, so it cannot ride a wave that binds them byte-identical and is recommended as
its own corrective wave (W22) ahead of the thick-span composite. Above the wave's rim clause on two
cells; below every adopted bound.

**Chartered 2026-09-08 as W22** (`2026-09-08-w22-resting-sweep.md`; claims §5.93): the gate is an
amplitude channel the driver owns (`shimmer`, 0 at idle); the rim read per side on both beds before
the light rim's constants move. Closes at W22's landing.

## The CSS tier's dark material over-darkens structured backdrops under the response law (W21 G1, 2026-09-07)

*Found on W21's dry run.* With the dark profile's response law at strength 1, the CSS tier's dark
rows split cleanly: over a solid the tier reads the law correctly and improves enormously
(`dark-solid__rrect-md` 0.0307 → 0.0046 ΔE), over a structured backdrop it over-darkens
(`checkerboard__rrect-md` 0.0213 → 0.0416; ten rows worse by more than W21's S1). The
declared-geometry read: the CSS body lands at 0.0122 on `checkerboard__rrect-md` against the
reference's 0.0468 and the GPU tier's 0.0475 — the dark anchor's level, on a backdrop whose encoded
mean is 0.5 and where the law says 0.047 (claims §5.90 §6). Recorded as the wave's CSS-only
residual (wave Decision Log 23 (a); W21 Decision Log 3 (a)). Shape of the diagnosis, bounded: read
what input the CSS tier's `resolvedBackdropTone` / `backdropToneResponseLevel` path receives over
the checkerboard on the dark profile (the proxy's sampled level, the hint, or a decoded value fed to
an encoded-space law) against the GPU tier's per-pixel input; if the input is in the wrong space
or the wrong statistic it is a derivation defect and closes in `optics.ts`; if the input is right
and one level per surface cannot carry the law over a busy backdrop, it is the tier's limit and the
residual stands. Either way the light CSS captures move, so it rides a wave that does not bind them.

## The calibration scene server's `VITREA_FIXTURES` containment check compares a normalised path against the raw environment value (W21 G0, 2026-09-07)

*Found on W21's probe, vitrea's side.* `packages/calibration/web/vite.config.ts` mounts the
fixtures directory named by `VITREA_FIXTURES` and then checks each served path's containment with
`startsWith` against the environment value as given, while the served path has been normalised — so
a fixtures path carrying a `..` segment fails its own containment check and every background
returns 403 with a message about running `capture.sh backgrounds`, which is the wrong diagnosis.
`run-web.sh` in the W21 G0 results canonicalises the path before exporting it. Shape of the fix,
one line: `resolve()` the environment value before both the mount and the check. Taken by W21 G1
(Decision Log 2 (g)).

## `capture.sh probe` reports the Screen Recording grant BLOCKED from a shell while the bundle's own path is granted (W20 G0, 2026-09-06)

`./capture.sh probe` `exec`s `build/harness` as a child of the calling shell, so TCC attributes the
ScreenCaptureKit request to the shell and answers `BLOCKED` (`SCStreamErrorDomain` −3801). The same
`probe` subcommand launched the way every capture is launched — `open` on
`build/VitreaReference.app` with the bed and fixtures passed as `open --env` — answers
`ScreenCaptureKit: OK`. W20 G0 recorded both outputs (`results/2026-09-05-w20-capsule-corner/g0/
g0-probe.md` §2) and captured twenty cells over ten runs with the grant live throughout. A session
that trusts `capture.sh probe` alone stops for nothing; the README's "grant Screen Recording, then
re-run" instruction is right for the bundle and misleading for the shell path. Shape of the fix:
`capture.sh probe` launches the bundle through `open` as `capture` does, or the README says which
path the answer is for. Owner: the harness; not this wave's code.

## The light material's rim over a dark backdrop is too dim by 0.05–0.11 — the collapsed rim, read in light (W22 G0, 2026-09-08)

*Found when the resting sweep's band came off the left side and the light bed was read per side for
the first time (claims §5.94 §3).* `dark-solid__rrect-md` under the light profile misses W22
clause 2 on three sides at 1x and four at 2x, worst −0.093 / −0.088 on the bottom: the reference
keeps a bright rim where the light material collapses onto a near-black backdrop and vitrea's
collapse folds the rim out with the body (W7). `rimAlpha`'s rows on that cell demand 2.4–2.9, so no
admissible value of the ambient rim reaches it; W21 deferred the same term at +0.017 in the dark
scheme ("the collapsed rim"). **At W22 G1 (claims §5.96 §4), three cells:** `dark-solid__rrect-md`,
`impulse__rrect-md` and `mid-dark-solid__capsule-button` under the light profile at both scales,
eighteen sides 0.031–0.093 too dim — every standing clause-2 miss on the bed is this one term. Shape of the fix: a rim that survives the collapse — the reference's
rim under collapse read against the un-collapsed rim on both beds, one fraction if it is one. Not
created by the sweep gate; hidden under the band until W22.

**Chartered as W23 (2026-09-08; `2026-09-08-w23-collapsed-rim.md`; claims §5.99), and re-read at the
contour first:** the three light cells are NOT collapsed (the size bias holds their collapse argument
above `backdropToneHigh`; `present` is 1) — their miss is the rim's amplitude law, vitrea's additive
+0.060…0.078 linear on every cell against the reference's +0.23…0.26 over dark solids, +0.13…0.21
over structured backdrops and clipped over `light-solid`; the band read's per-row leverage on the dark
cells was the corners' dilution. The collapsed cells proper (the capsules over `dark-solid` and
`impulse`, W21's `rrect-sm`) lose their rim to the collapse's one `present` factor where the reference
keeps +0.020 — the dark material's rim, the same bytes in both schemes. W23 takes both as one term:
a rim that survives the collapse (one constant on the material) and the rim's law fitted at the
contour. Closes when W23 lands.

## The overlay group of a stacked scene is handed a backdrop 2.9× its base pane's output (W22 G0, 2026-09-08; taken as W22 G3)

*Found by the user's eye on the W21 landing sheet — "Apple's topmost glass is noticeably darker
than ours" — and measured at claims §5.94 §5.* The shipped dark response law evaluated at the
overlay's true backdrop (the base pane's measured body, 0.0470 linear) gives 0.0245 against the
reference's 0.0207; the capture is 0.0493, the law's answer at linear 0.1344. The candidate
mechanism is the overlay's `css-backdrop` proxy sampling past the base pane through the padding W8
inflated for the outer shadow (19.3 % raw checkerboard mixed into the base's output reproduces the
number). Dark-only by visibility; the same input error moves a bright backdrop very little. Fixed
in W22 G3 if the mechanism is what the candidate says; closes at W22's landing.

**Closed at W22 G3 (2026-09-08; claims §5.95), with the mechanism corrected beside the candidate:**
the proxy box sat wholly inside the base pane; the overlay had been handed no backdrop tone at all
(a `css-backdrop` group has no texture for `backdrop-tone.ts` to measure), so the tone axis stood
down and the pane drew the unadapted material. Fixed as a mechanism (`backdrop-stack.ts`): a group
on other glass is handed that glass's composite tone. The overlay's dark body 0.0493 → 0.0239 against
the law's 0.0245.

## The backdrop tone is one number per source, and a light surface over a structured source carries the difference (W22 G3, 2026-09-08)

*Found deriving the base pane's output tone for the overlay above it (claims §5.95 §5).*
`backdrop-tone.ts` measures a source once — the whole raster's mean — and every group over that
source is handed the same tone whatever its footprint covers. Pushed through the material's
composite, the derived output level overshoots the base pane's measured body by +0.0349 in light
and +0.0012 in dark: a light material's 0.51 transmission carries the source-level error where a
dark material's 0.095 scales it away. Nothing measurable on the GPU tier's own rows (the response
law's input is the footprint's encoded mean sampled by the shader); it reaches the CSS tier's level
and any group stacked on a light surface. Shape of the fix: the tone measured under the group's
footprint rather than the source's extent — the declared-geometry reader already does this on the
calibration side.

## The CSS tier under increased contrast is 0.00006–0.00025 worse in ΔE at W22 G1 while its GPU twin improves (2026-09-08)

*Found at W22 G1's dry run (claims §5.96 §6).* With `specularGain` 0 on the light profile the CSS
tier's derived level (`interiorBandLight`) loses 0.0013–0.0053 of band light; under the
increased-contrast profile the CSS calibration ΔE moves 0.01293 → 0.01300 and the holdout 0.04531 →
0.04557 while the GPU tier's rows improve. Small, one profile, the CSS tier only — a CSS-only
residual under wave Decision Log 23 (a), recorded, not chartered. Shape of the work: the
increased-contrast fold's band term read against the reference on that profile's own rows.

## A conformance capture moved by one code value between a dry run and its landing, three times (W21 G2, W22 G2, W23 G2; 2026-09-09)

*Second sighting at W22 G2 (claims §5.97).* The 1x dark `checkerboard__glass-over-glass__rest` CSS
alpha conformance render differed from G1's dry run by 2 of 64 000 pixels, ±1 code in alpha at the
canvas edge, rgb identical, no measured row moved; a third capture reproduced the dry run's bytes.
W21 G2's sighting was the increased-contrast toolbar's render capture (17 of 64 000 edge pixels).
Both are session byte-states that a re-capture settles; neither moved a row. The referee compares
declared digests and reports the conformance renders beside them; a determinism claim on the
conformance path is not made. Shape of the work: a second capture of any differing file inside
the rebuild, and the pair recorded.

*Third sighting at W23 G2 (claims §5.104).* The increased-contrast
`photo__toolbar-group__rest` CSS alpha conformance render differed from G3's dry run by 19 of
64 000 pixels, alpha by exactly one code on every one of them, at interior pixels of the toolbar's
own soft edge; the rgb differences that come with them (51→55, 225→229) are the un-premultiply of
that one code. No measured row moved — the landing's 15 218-row comparison against the dry run finds
none differing, and the cell's render capture is one of the 229 that reproduce their declared digest
exactly. A third capture in the landing session reproduced the LANDED bytes, not the dry run's,
which is W21's shape rather than W22's: the state belongs to a session, not to a file. Three
landings, three cells, one code each. The fix's shape is unchanged.

## A wave's own claim survived in an e2e spec that no child's chain runs (W23 G2, 2026-09-09)

*Found at W23's landing.* `packages/platform-web/e2e/gpu/tint-gpu.spec.ts:82` asserted that the rim
on an orange surface raises the BLUE channel the paint leaves at zero — the white rim's signature,
correct when it was written. W23 G3 measured that composition against Apple's own captures and
refuted it (claims §5.103): the reference lifts an orange's green channel and leaves its blue at 0.
The spec still passed at G1 and at G3 and through the merge, because a child's chain runs build,
lint, the unit suites and the goldens, and the platform-web Playwright projects are not in it. The
landing ran them and the spec failed, on the wave's own new behaviour. Nothing shipped wrong and the
spec is corrected in place — but a gate that only the landing runs is a gate the wave discovers its
own contradictions at the latest possible moment. Shape of the work: when a child moves a term the
e2e suites read (the rim, the tint, the shadow), that child's chain runs the suites that read it,
or the suites gain a pointer to the claims section they encode so a wave that moves the claim finds
them by grep.

## The react e2e suite cannot be read as pass/fail at a landing (addendum, W22 G2, 2026-09-08)

*Addendum to the standing entry on `packages/react`'s press and morph specs.* Three consecutive
runs of the unchanged tree at W22's landing failed 3, then 1, then 1 case from `press.spec.ts` /
`morph.spec.ts`, a different case each time, each passing on repeat — a fourth distribution beside
the entry's 0/2/4/4, and one failure on chromium where the entry says chromium passes every time.
Nothing the wave moved touches a press or a morph; the landing was recorded with the suite "not
claimed green" (claims §5.97). The shape of the fix is the entry's.

## The demo's harness fixture is a hand-kept byte copy that went stale silently (W22 G2, 2026-09-08)

*Found at W22's landing (claims §5.97).* `apps/demo/e2e/fixtures/checkerboard__capsule-button__rest__webgpu.png`
is the harness capture `reference-panel.gpu.spec.ts` compares against, kept current by a doc
comment; at W22's landing it was 178 px / 46 code values from the landed capture at the rim band,
and only the spec's 0.02 tolerance kept it green through W21 and W22. Re-copied with its cell
record (document digest `9360d73bd071`). Shape of the fix: a script the canonical rebuild runs, or
the spec reading the capture from `web-captures/` on the capture machine with the fixture as the
fallback.

## The appearance switch measured at the contour instrument: the dark thin cells over structured backdrops are −16 and −19 codes in body (W23 G0, 2026-09-08)

*Found beside the rim read (claims §5.100 §7).* `checkerboard__capsule-button__rest` and
`photo__capsule-button__rest` in the dark scheme sit −16.05 and −19.05 codes below the reference's
body at both scales, five to six times the thick cell's −2.93 over `dark-solid`; and on W21's probe
grid the reference draws its LIGHT appearance on `light-solid__rrect-sm` in the dark scheme (body
0.9666, contour clipped) where vitrea draws the dark material, which the W23 rim law makes 0.115
worse on that non-canonical row. The same term W21 and W22 deferred by name, now with numbers in the
contour instrument's units. Closes with the appearance switch's charter.

## W21's probe grid collapses `rrect-sm` and `rrect-lg` over `dark-solid` and not `rrect-md` between them (W23 G0, 2026-09-08)

*Found reading the collapsed cells (claims §5.100 §3).* In the dark reference's probe grid
`dark-solid__rrect-sm` and `dark-solid__rrect-lg` both draw the collapsed appearance (body 0.0110,
rim +0.0201 / +0.0196) while `dark-solid__rrect-md` does not (body 0.0153, rim +0.0256). A size law
that collapses the small and the large surface and not the middle one is not a size law; the probe
fixture may carry a state flip (claims §5.17's bistability) or the reference may key the collapse on
something other than span. Read by nothing; a native re-capture of the three at one sitting would
tell. Closes when the collapse's key is read.

## The probe grids are the only fitting ground for a two-constant material law, and nothing in the harness captures them routinely (W23 G0, 2026-09-08)

*Found fitting the rim's law (claims §5.100 §4).* The canonical light bed has two fittable solid
cells (`dark-solid__rrect-md`, `impulse__rrect-md`, bodies 0.43 and 0.48 — nearly collinear) and the
dark bed one; any law with an intercept and a slope on either material is unidentifiable without
W9's light grid and W21's dark grid, which G0 rendered through its own `probe-ladder.sh` with
`VITREA_SCENES` / `VITREA_FIXTURES`. If the material's laws are to be maintained, the harness should
capture the probe grids as a declared set with their own reads, not a gate's script. Closes when the
grids are a harness set.

## `light-solid`'s second contour row carries 53 % of the reference's rim and −6 % of vitrea's, and no metric can read it once the first row clips (W23 G0, 2026-09-08)

*Found on the width read (claims §5.100 §5).* Over `light-solid` both contour rows clip to 255 on
the first row, so the summed rim differs by 0.024 at 1x through the SECOND row alone; ΔE and SSIM
on a clipped row report nothing. The eye sees a softer edge. A width term (`rimWidth2x` at G1 for
the 2x rows) does not reach the 1x second row; recorded as unreadable on this bed.


## The CSS tier's rim is 30–45 % short over a dark backdrop in light and 1.6× too bright in dark, and the fixtures cannot fit the constant that would close it (W23 G1, 2026-09-08)

*Found landing the rim's law (claims §5.100 §8).* The contour instrument reads the CSS tier for the
first time: light 1x `dark-solid__rrect-md` +0.1576 against the reference's +0.2293,
`checkerboard__rrect-md` +0.0985 against +0.1763 and `mid-dark-solid__capsule-button` +0.1719
against +0.2421; dark 1x `dark-solid__rrect-md` +0.0415 against +0.0256. W23 G1 re-based
`cssTierMapping.borderAlphaPerRimAlpha` 1.95 → 0.64 so the conversion survives a numerator whose
scale tripled — the product on an unsampled surface is 0.3509 against the 0.351 it drew before —
and did NOT refit it, because the sweep that declined it moved the cross-tier ΔE over a 1.01× grid
between 0 and 1.95 and the fixtures still cannot identify it. The contour read can. Closes when a
CSS wave fits this tier's border on the contour instrument rather than on the matrix's ΔE.

## The collapsed rim a painted surface keeps depends on the tint's own colour, and every collapsed blue cell on the bed is holdout (W23 G1, 2026-09-08)

*Found fitting `rimCollapsedTinted` (claims §5.100 §5).* The reference's collapsed tint-ORANGE
capsule keeps +0.1149 of contour rim at 1x and the collapsed tint-BLUE one +0.176, against +0.020
bare — so what the collapse keeps under paint is a function of the paint, and `rimCollapsedTinted`
is one absolute number fitted on orange alone (0.337, worst residual 0.0039 over the four orange
cells at both scales). The two blue collapsed cells (`dark-solid__capsule-button__rest-tint-blue`
and its 2x sibling) are holdout, so no calibration row can fit the colour dependence and the wave
did not try. Closes when the bed declares a non-holdout collapsed cell in a second tint, or when the
quantity is read as a function of the seed's own luminance on a probe grid.

## The contour read and W22's band read disagree about the same rim, and the difference is in the corners (W23 G1, 2026-09-08)

*Found on the parent's clause 4 (claims §5.101 §4).* On `dark-solid__rrect-md` in light at 1x the
CONTOUR read gives vitrea +0.2176 against the reference's +0.2293, inside the wave's 0.03; the BAND
read on the same captures gives an excess over the body of +0.078 against the reference's +0.047,
1.65× over, and 47 sides that met W22's band bound of 0.03 no longer do. The contour read excludes
1.6 radii of corner by construction and the band read averages the corner arcs in, so the only place
the two can disagree is the rim in the CORNERS: on the straight span vitrea now matches the
reference and over the whole side it overshoots. A candidate rather than a proof — no reader in the
project measures the corner arc's rim. Closes when a corner reader exists and says which of the two
is right, or when the parent restates clause 4 on the straight span.

## The dark bed's tinted rows are 0.031 of contour rim against a reference of 0.127, and no colour the rim is spent in can move their hue (W23 G3, 2026-09-09)

*Found landing the painted rim's colour (claims §5.102).* `rimTintChroma` brought the tinted rows'
OKLab b to within 0.009 of the reference's on average, and left `a` at 0.022 — with every one of the
36 sides still outside the wave's 0.02 sitting on the DARK bed, where `checkerboard__capsule-
button__rest-tint-orange` and `photo__…-tint-orange` draw 0.031 of contour rim against +0.127. A rim
that dim cannot move its row's hue whatever colour it is spent in, so the residual is the dark
amplitude law's amount and not the composition's. The dark law is fitted on one canonical solid cell
plus W21's probe grid (the tracker entry above), so closing it needs a bed with more than one
fittable dark solid. Closes with the dark bed's own fitting ground.

## The CSS tier colours one inset shadow where the renderer adds a coloured light per pixel (W23 G3, 2026-09-09)

*Found mirroring the painted rim (claims §5.102).* The renderer spends the rim's light in
`mix(white, paint / luminance(paint), chroma × strength)` and adds it to a linear composite, where
the CSS tier can only set the `border-color` of one inset `box-shadow` whose alpha is fixed by
`borderAlphaPerRimAlpha`. A channel the normalisation pushes past the border's own value is clamped
on this tier and clips in the composite on the other, and the mix is taken in the encoded space this
tier composites in rather than in linear light. The two agree at the ends — chroma 0, and a white
paint — and differ in the middle by the transfer's curvature. A CSS-only residual under wave
Decision Log 23 (a); closes with the CSS rim wave that fits `borderAlphaPerRimAlpha` on the contour
instrument.

## The collapse pulls the material onto the backdrop's MEAN and removes the transmission the reference keeps; W7's "texture collapse" was fitted where there was no texture (W24 finding, 2026-09-09)

*Found by the user's eye on the W23 landing sheets (claims §5.107 §2).* Through the collapsed
`impulse__capsule-button` the reference passes the centre dot at +0.0254 over a 0.0065 body, 4 CSS
px wide at 2x (+0.0065, 8 px at 1x); vitrea passes 0.0000 in both schemes at both scales, because
the collapse's target is the group's mean backdrop colour (`toneColour.rgb`) and the alpha solve
stops the material transmitting. W7 measured the collapse on `dark-solid`, a backdrop with nothing
to transmit, and named it texture collapse; the reference's collapsed material is a dark glass that
transmits what lies beneath it, blurred. Chartered as W24 G1; the same term as the appearance
switch's −16 / −19 codes on the dark thin structured cells. Closes when W24 lands.

## A diagonal rim light is invisible to every per-side reader, and three waves of rim instruments were per-side (W24 finding, 2026-09-09)

*Found by the user's eye on the W23 landing sheets (claims §5.107 §1).* The reference's rim varies
around the contour as |cos| about the top-left ↔ bottom-right diagonal (dark rrect corners 0.042 /
0.006, sides 0.032); a light on the 45° diagonal projects equally on all four straight sides, so
W21's band peak, W22's per-side contrasts and W23's contour span all read the reference flat and
fitted vitrea flat. The variation lives in the corner arcs; W23 clause 4's corner overshoot was it.
Chartered as W24 G0 with an angular instrument. Closes when W24 lands; the lesson is in memory.


## The lit edge's exponent depends on the scale, and the reference's angular profile keeps a floor at the null that a single power law takes to zero (W24 G2, 2026-09-09)

`(√2·|n̂ · L|)^p` at one exponent, 1.15, is what the rows separate; the 2x rows want 1.30–1.45
and the 1x rows 0.85–1.10 (`g0/fit-law.txt`), so the brightest-to-dimmest ratio under-reaches at
2x (0.78 and 0.53 of the reference's on the dark capsule and rrect) and the dark 1x rows meet it.
And the reference's dim bins do not go to zero where the law's do: the light bed's ratio overshoots
by 2.3–8.8× because the quotient's denominator is the null, where the reference keeps a floor and
`|cos|^p` does not. The floor is not an ambient term — the charter's `a + (1 − a)|n·L|^p` fits
`a` to 0.000 on every grouping — but a shoulder in the lobe (G0 §8.5). Shape of the work: a second
exponent anchor per scale (as `rimWidth2x` and `collapseTransmission2x` already are), and a lobe
with a shoulder (`|cos|^p` blended with a wider power, or a Lambert-plus-power) fitted on the same
285 bins; four solid rows per scale cannot separate either alone, so the probe grids (W23's
tracker entry) are the rows to add. Numbers: `g2/g2-clauses.txt`; W24 Decision Log 3 (a).

## The collapsed capsule's transmitted dot is 2.6 CSS px too narrow at 1x, and the collapsed body sits 0.003 below the reference's (W24 G2, 2026-09-09)

The transmission share puts the dot's PEAK within 0.0002 of the reference's at both scales
(`g2/impulse-read.txt`), and two things it cannot move are recorded beside it. The FWHM is 4.99
against 7.57 CSS px at 1x (4.64 against 3.80 at 2x): the reference transmits through σ 2.63 device
px at 1x / 1.30 at 2x, the same kernel as its uncollapsed cells, while vitrea's scatter kernel runs
1.68 → 4.86 — a width no share can change. And the collapsed body is −0.0029 / −0.0033 linear
below the reference's on both schemes: the collapse's target sits at the backdrop's mean where
Apple's collapsed glass sits above it. Shape of the work: the kernel is the thick-span composite's
(wave Decision Log 23 (c)); the body level is one constant on the collapse's target (a lift above
the mean), fittable on the same validation row whose independence W24 already spent, so it wants
a calibration row — the probe grids again. W24 Decision Log 2 (f) and 3 (b).

## The CSS tier's anchored conversion is degenerate over a backdrop whose tone equals the tint, returns alpha 1, and throws the collapse's transmission away (W24 G2, 2026-09-09)

The mirror is exact — `A' = A − k·c` with the tone's share `k(1 − c)` re-solved — and inert on
every collapsed cell of the bed, because every one of them sits below the linear chain's reach and
anchors its conversion on the group's own tone (W21 Decision Log 4 (a), `conversionAnchor`). That
solve reproduces the GPU tier's LEVEL; over a backdrop whose tone is the tint, every alpha
reproduces the same level, and it returns `cssTintAlpha` 1 for source alphas of 0.983 and 0.800
alike. Measured: at `collapseTransmission` 0.2 the collapsed `impulse__capsule-button` CSS capture
is byte-identical to the landed one. So **the CSS tier does not transmit on the cells this bed can
see**, and the impulse dot the GPU tier now passes is absent on the CSS tier. The candidate fix is
one line — a tier may not draw a surface MORE opaque than the material is, so cap the anchored
solve at the source's own alpha — but it changes the conversion on every anchored cell and belongs
to a gate with its own rows and the parent's word. `g2/g2-dryrun.md` clause 7; W24 Decision Log 3
(f).

## The WebGPU tier over a `css-backdrop` proxy keeps W7's opaque collapse: the transmission is gated on a sampled pyramid, and root.ts paints CSS layers only for the CSS renderer (W24 G2 review, 2026-09-09)

The shader lerps the collapse's target toward the per-pixel blurred backdrop only when
`flags.x` says a pyramid was sampled; with a DOM proxy beneath the canvas the backdrop vector is
zero and the target stays the group's mean, while `adaptedAlpha` still reaches 1 — so a fully
collapsed untinted group on the WebGPU renderer over `css-backdrop` writes an opaque layer that
hides the blurred proxy entirely, exactly as before W24. The doc comment says the CSS tier's
`backdrop-filter` carries the transmission there, but root.ts paints the CSS layers only for the
CSS renderer and `unsampledMaterial` carries the unadapted pair. No bed cell is that combination
alone (six are `gpu-texture+css-backdrop`, 109 `gpu-texture`), so nothing measured moves. Shape
of the work: apply the transmitting decomposition (`A − k·c`, the tone's share re-solved) to the
unsampled GPU path's output alpha so the proxy shows through by the profile's share; a gate with a
cell in that combination. The independent review's first finding, verified; W24 Decision Log 3 (g).

## The `clear` variant's one-sided specular (0.45, never fitted) retired with the rim's `spec` term, on no rows in either direction (W24 G2, 2026-09-09)

W22 fitted `specularGain` to 0 on `regular`; W24 G0 read why — the one-sided `max(n · L, 0)^p`
cannot reach both ends of a diagonal whose two corners the reference draws equal, and degenerates in
the fit trying to become symmetric — and G2 retired the term from the rim on both tiers so the rim
has one law. `clear` carried a structural 0.45 that no scene on either bed or in the golden suite
declares, so it lost a visible highlight without a measurement either way. `specularPower` and
`specularGain` stay on the profile and in both documents so the W22 record is unchanged; nothing
reads them. One line restores the term for `clear` alone if a row ever asks for it; the lit edge
at `optics.clear.rimLitExponent` 0 is the flat rim. Named in 0.13.0's changeset. W24 Decision Log
3 (h).

## The nested pane's extractor rows move by a hundred times the level shift that causes them, in opposite directions at 1x and 2x, and the gate reports one breach where there are two (W24 G2, 2026-09-09)

The CSS tier's band integral over the arcs moved the 1x dark
`checkerboard__glass-over-glass__rest` CSS cell's interior by 0.00005 linear (a fiftieth of a
code) and its ΔE by +0.00005, and its `silhouetteIoU` fell 0.91007 → 0.90804 and its
`contourDistanceP95` rose 8 → 8.25, breaching the two W23 first-reading floors (0.9090 / 8.1); the
2x sibling's same three rows swung the other way by ten times on the same change (IoU 0.90482 →
0.92878, mean 1.760 → 1.289, P95 13 → 10). Both are the extractor's threshold crossing on the
nested pane's low-contrast contour, as the W21 and W23 pins' comment says. The gate reported the
first only — `adopted-thresholds.test.ts` stops a profile's test at its first failed assertion —
so a parent reading the gate's output alone would have re-pinned one floor and left G3 to find the
other. Re-pinned by the parent on the standing instruction (W24 Decision Log 3 (d)), W23's numbers
beside. Shape of the work: a silhouette extractor for nested panes that does not threshold on the
material's own level (the W21 G2c entry on the luminance-delta extractor's perforated silhouette,
above), and a gate that reports every breach
of a profile rather than the first — collect the failures and assert once. `g2/g2-gate.txt`.

## The session byte-state on `photo__toolbar-group__rest` under increased contrast has a fourth sighting, the first on the render path (W24 G3, 2026-09-09)

At W24's canonical rebuild the `1x-light-increased-contrast / photo__toolbar-group__rest / css`
RENDER capture differed from G2's dry-run digest by 17 of 64 000 pixels, at most one code, colour
channels only, inside the toolbar's soft edge (its alpha sibling by 19 px, max 4 codes — the
un-premultiply of one alpha code W23 measured on the same file). Re-captured a third time to
scratch under identical flags it reproduces the dry run's bytes (`24cda2a5…` render,
`fb25641867…` alpha), not the landed `001eceb6…`: the rebuild's own capture is the outlier, and the
dry-run session and the recheck agree. W21 G2 and W23 G2 saw this cell on its `__alpha` render;
this is the first time the render path itself moved. A validation cell, so the holdout read stands;
228 of 229 digests reproduced. Eight matrix rows on the cell move, seven in the sixth decimal or
beyond and `ssimMin` by 0.00035; no bound, floor or predicate arm reads differently. The landed
file is left as captured. Shape of the work: it is always this cell, always this profile — the one
whose accessibility policy composites an extra opaque layer over a photo — and always one code at
a soft edge; a capture-time re-read of that cell against its own second frame (the harness already
takes eight frames) would name whether the byte-state is the compositor's or the page's.
`g3/g3-landing.md` §2.1, `g3-referee.txt`.

## The lit arcs move two passing 2x light calibration cells out of the shape gate on the predicate's topology arm (W24 G3, 2026-09-09)

`checkerboard__rrect-md__rest` and `checkerboard__toolbar-group__rest` at 2x light on the texture
tier: the unlit north-east and south-west arcs pinch the extractor's silhouette into one more
body each (`bodiesWeb` 1 → 2 and 3 → 4), and the predicate excludes them from the shape rows
(`PREDICATE_EXCLUDES` 27 → 31 with the two 1x collapsed capsules whose lit arcs are all the
extractor recovers). Both meet every shape row the gate would have asked — `rrect-md` IoU 0.99634,
contour mean 0.236, p95 1; `toolbar-group` 0.99026 / 0.205 / 1.414, better than the 0.12.0 bed's
0.98714 / 0.288 — and both ΔE means improve. The landing's one loss of gated coverage, recorded
rather than recovered, because the predicate is a construct no wave touches to make a gate pass.
Shape of the work: the extractor's body count is a threshold crossing on a rim that now varies
around the contour by design; a silhouette extractor that closes the arcs (a morphological close
at the rim's own width before counting bodies) would keep these two and the nested-pane rows
honest at once — the same work as the nested pane's extractor entry. `g3/g3-predicate.txt`.

## The nested pane's base is hazier than vitrea's, and the web side's haze has never been identified (W22 finding, entered W25, 2026-09-09)

The user's eye, twice: "Apple's bottom glass is very slightly less transparent" (claims §5.99 §1;
W23 spec). The numbers on record are two instruments in two units, one saturated and one
unidentifiable: `blurSigmaNative` 4.8397 at residual 0.3575 on the 2x dark reference base against
0.6920 at residual 1.8113 on the web (the residual `report.ts` defines as "σ is not
identifiable"; the CSS sibling 1.2393 at 1.1816); the σ-match 16.00 native at 2x (the grid's
ceiling) against 8.00 web, and 1.50 against 2.20 at 1x, the opposite sign. Chartered as W25 with
the instrument first (three readers agreeing; claims §5.112 §3). Closes when the base's σ-match
is within 15 % of the reference's at both scales in both schemes with neither side saturated
(W25 clause 3).

## The reference's rim varies along a straight side of a thick panel, and no vitrea number exists for it (W24 G0 finding, entered W25, 2026-09-09)

2x dark `dark-solid__rrect-md`: the top edge's rim runs 0.0442 → 0.0158 along the side with the
silhouette straight to 0.06 px and the interior uniform; flat on the capsule and `rrect-sm`,
graded on `rrect-md` and `rrect-lg` (W24 Decision Log 2 and 3 (c); claims §5.108 §1). vitrea's
rim is constant along a side by construction (the lit factor is exactly 1 on every straight
side). By shape a thickness term; by quantity a rim term every reader to date read per side or
per bin. W25 G0 builds the position-along-side reader on the four thick shapes; the term is
W25's if it grades with span and W12's (the lens refracting the backdrop's gradient) if it does
not. Closes when the profile is read on both sides and the term is taken or attributed.

## The CSS tier's interior spread is 32–63 % under the reference on the four large spans, and the residual is the encoded space (W16 finding, entered W25, 2026-09-09)

W16's table (`2026-09-04-w16-css-two-layer-body.md:158–193`): interior standard deviation web /
native on the dom tier, light, checkerboard — `rrect-md` 0.0767 / 0.1131 (1x), `rrect-ml`
0.0591 / 0.0865, `rrect-lg` 0.0375 / 0.0650, `glass-over-glass` 0.1279 / 0.1321; 39–63 % under at
2x. The forward-model residual is 2.4–2.8× on the thick spans and "no σ, share or mask can move
it" (claims §5.60); `backdrop-filter: url(#f)` with linearRGB reads 1.17–1.50× of the GPU law at
dpr 1 and 0.97–1.03× at dpr 2. Recorded under wave Decision Log 23 (a) as a CSS-only residual,
not chartered; W25 re-reads it and the coherence pin (≤ 0.05; the checkerboard cells at
0.023–0.043) as the GPU kernel widens. Closes only with a tier that can encode the space.

## The reference's kernel is two components and the thick surface differs from the thin in the heavy SHARE; vitrea's share at 1x is 0.23 against 0.47 and its 1x kernel 32–46 % too wide on every thick span (W25 G0, 2026-09-09)

One reference cell at 1x reads 1.30 device px against a 16 CSS px checkerboard, 4.75 against 32
and 6.25 against 64 (`g0/argument.txt` Table 1); a single Gaussian returns one number at every
pitch. Reader A on the uncollapsed `impulse__rrect-md`: sharp 2.79 → 1.40, heavy 19.52 → 11.29
device px from 1x to 2x, share 0.47 → 0.69 (`g0/widths.txt` Table 1); thin cells at pitch 64
read 2.00–2.10 where thick read 6.00–6.75. vitrea's share at 1x 0.23; its single width 1.66–1.73
against 1.14–1.30 on every thick span at 1x (both readers, both schemes); on `photo` 14–19 % short
on `rrect-ml` and `-lg`. Chartered as W25 G2's first mechanism (the share and the sharp width per
scale on `sizeThickness`; Decision Log 3 (a)). The 2x width above span 96 is identified by NO
fixture on disk (`g0/identification.txt`) — the coarse structured backdrops at 2x of W25's
`probe` set are the rows. Closes when clause 2's triple is met.

## The thick surface's body level keeps grading above the knee, and two levels larger than the chartered miss were not in the ledger (W25 G0, 2026-09-09)

`sizeThickness(short side)` at knee 96 is the right argument (r 0.95–0.998 against every
alternative) but the reference's level grades on by about a fifth of the thin-to-thick step per
span doubling to 160 where the curve is flat (`g0/argument.txt` Table 2). Levels in codes,
reference minus GPU (`g0/levels.txt`): `checkerboard__toolbar-group` **+8.77 / +9.34** — the
largest thick-cell miss, a calibration row whose members are span 44 (thin to the law; the
group's sampling or the level term, G2 reads which); `photo__rrect-md` dark **−5.41 / −5.55**,
nearly twice the chartered `dark-solid__rrect-md` −3.07; `photo__rrect-lg` −3.35 / −3.55;
`impulse__rrect-md` +5.93. W25 G2's second mechanism, a level term above the knee (Decision Log 3
(b)). Closes when clause 2's level is met.

## The along-side rim term is a diagonal position field on thick solids, which a per-normal lit-edge factor cannot express; and the 2x reference's rim mean is corner-asymmetric where the 1x is not (W25 G0, 2026-09-09)

Supersedes the along-side entry above for its verdict. Present on flat `light-solid` /
`dark-solid` / `mid-dark-solid` (range 0.0187 / 0.0226 / 0.0345 at span 96), zero at spans 32
and 44, saturating above 96 — it rides `sizeThickness`; the four sides' slopes exactly
antisymmetric (±0.000192 top/bottom, ±0.000379 left/right luma per CSS px on the 1x dark
`dark-solid__rrect-md`), slope × side length reproducing the range: a corner-to-corner ramp.
vitrea's landed range 0.0015–0.0083 against the reference's 0.0206–0.0357 (`g0/along-side.txt`
Tables 2, 4). Taken as W25 G2's third mechanism — a linear field along the diagonal on the rim's
amplitude riding `sizeThickness` (Decision Log 3 (c)). On `checkerboard` the reader correlates
0.85–0.96 with the backdrop under the body: the lens, separable only on the solids. Found beside
and NOT taken: at 2x the reference's rim MEAN is 0.0330 / 0.0313 (top / left) against 0.0168 /
0.0176 (bottom / right) where the 1x reads 0.0248–0.0251 on all four — a scale-dependent
asymmetry of the mean, unexplained. Closes when G2's clause is met; the 2x mean asymmetry closes
with a reason.

## Two of the W21 dark grid's fixtures are the W9 light grid's files, and span is confounded with clearance on the 320 × 200 canvas (W25 G0, 2026-09-09)

Resolves the `rrect-sm` half of the entry "W21's probe grid collapses `rrect-sm` and `rrect-lg`
and not `rrect-md`" above, and leaves the other half standing. The dark grid's manifest records
18 of 56 cells bistable across seven attested runs at one sitting; `dark-solid__rrect-sm__rest`
and `light-solid__rrect-sm__rest` are bistable and their majority files are byte-identical
(SHA-1) to the W9 light grid's captures of the same scenes — `light-solid__rrect-sm` reads a body
of 0.96659 over a 0.8918 backdrop, a light-scheme frame beyond doubt (`g0/grid-state.txt`
Tables 1, 4). **Withdrawn as dark readings**; nothing on the bed was fitted on them; re-captured
under the dark scheme at W25 G1's sitting. `rrect-md` (96, uncollapsed) against `rrect-lg` (160,
collapsed) is single-state in all seven runs and survives — but on the canvas the short-axis
clearance is 84 / 52 / 20 CSS px at spans 32 / 96 / 160, so a size-keyed collapse and an
edge-proximity one fit the fixtures equally. G1 adds `dark-solid` at 48, 64, 80, 128 and a
clearance variant (`rrect-md` at a 20 px margin or `rrect-lg` on a wider canvas). Closes when
clause 5 is read on those rows.

## The edge-spread reader identifies a kernel only to an eighth of the backdrop's step pitch, and no ceiling changes that (W25 G0, 2026-09-09)

Addendum to the base pane's haze entry above. `blurEdgeSpread`'s window is bounded by the
neighbouring step, so on the 16 CSS px canonical checkerboard it identifies to 2 device px at 1x
and 4 at 2x; ceilings of 8 → 128 were swept and the best row is usually the smallest
(`g0/validate.txt`). The web residual 1.81 recorded at §5.94 §5 was that bound, not a property of
vitrea's material. The reading that identifies a thick kernel is reader A on a dot or readers B / C
on a coarser pitch (32, 64 CSS px), which W25's `probe` set carries. Closes with the set.

## The heavy tap's width does not follow `sizeScatterGainMax`: a mip-chain level saturates at 13.3 device px where the reference's heavy component is 19.5 (W25 G2, 2026-09-09)

Reader A on `impulse__rrect-md` at 1x reads vitrea's heavy component at 13.29 device px at the
reference's own share, against the reference's 19.52; rung `rG` raised `sizeScatterGainMax` 8 →
10.3 — the value the mix's arithmetic says should take it to 19.5 — and the reading stayed 13.29
(`g2/fit-share.txt`, `g2/g2-findings.md` §2). The heavy tap samples a mip-chain level whose
effective width does not scale with the gain past that level's own. It is why raising the share
to the reference's costs ΔE on the grids (+0.00087 at lift 0.48): the structure vitrea adds
comes through a kernel narrower than the reference's. Shape of the work: a heavy tap whose width
is a continuous parameter (a further pyramid level, or a separable blur at the tap) with the
width fitted on the probe set's coarse checkerboards at both scales. Closes when reader A's heavy
σ is within 15 % of the reference's at both scales.

## vitrea's sharp component is 1.67 device px against the reference's 2.79 at 1x and runs the other way across scales, and it is the thin capsule's own `blurSigma` (W25 G2, 2026-09-09)

The reference's sharp component is span-flat (2.62 device px collapsed, 2.79 thick) and halves
between scales (2.79 → 1.40); vitrea's is `blurSigma` 1.25 CSS px, 1.67 device px at 1x and 3.51
at 2x (`g2/g2-findings.md` §1, §6, §10). No thick-only sharp width exists to fit, so closing the
gap re-fits `blurSigma` against a bed where the thin cells are not the constraint — X5-entangled —
and adds a `blurSigma2x` sibling that the 2x coarse checkerboards of the probe set identify.
Closes with that fit.

## The along-side field closes three quarters of the reference's range; the last quarter is in W23's amplitude law on the straight spans (W25 G2, 2026-09-09)

At slope 0.45 the field's corner-to-corner range reads 0.743 of the reference's over 64 sides
(27 inside 20 %), opposite sides agreeing to 0.002 (`g2/fit-field.txt`). The residual is not in
the field's shape (residual slope −0.004) but in the rim's mean amplitude on the straight spans,
which W23 fitted per side and this factor deliberately leaves alone. Closes when the amplitude law
and the field are fitted jointly on the probe set's solids. The CSS tier cannot draw the field at
all (one inset shadow, one alpha around the contour) while staying coherent with the GPU tier's
side mean — an X8 residual under wave Decision Log 23 (a).

## The W21 grid's "collapses `rrect-sm` and `rrect-lg` and not `rrect-md`" is closed: the key is span, the small spans collapse in both schemes, and the large panel's level is the dark decline's floor (W25 G1, 2026-09-09)

Closes the two entries above on this contradiction, and corrects the second: the two fixtures
byte-identical to the light grid's were not the light grid's files but the reference rendering
the same appearance in both schemes, reproduced in every run of the W25 sitting with the
same-sitting light capture as control (claims §5.115 §3). The sweep over `dark-solid` at spans
32 / 44 / 48 / 64 / 80 / 96 / 128 / 160 and the clearance variant (`g1/sweep-read.txt`): every
span to 64 collapses in both schemes (0.0110 against the backdrop's 0.0117); the clearance
variant reads `rrect-md`'s body exactly, so edge proximity is not the key; above the knee the
level grades in the scheme's own direction (dark 0.0169 → 0.0110, light 0.4739 → 0.5022 from 80
to 160) and the dark 160 px panel's "collapse" is that decline reaching the collapsed level. What
remains open is the term itself: a scheme-signed level above the knee (W25 G3's fit) and the
size-keyed LIGHT adaptation of a small surface over a bright backdrop in the dark scheme
(`light-solid__rrect-sm` 0.96659 in dark where `rrect-md` reads 0.096) — no vitrea mechanism, no
number yet. Closes when both are fitted or attributed.

## The 2x reference is unstable across runs where the 1x is not, and one 2x cell has no majority state at all (W25 G1, 2026-09-09)

On W9's protocol at one sitting, seven runs per scale: at 1x 138 of 158 cells deterministic and
5 bistable; at 2x 48 deterministic and 45 bistable, with 70 of 104 probe cells published at a
majority state and `2x-dark / checkerboard-8__capsule-button__rest` returning three structurally
different settled appearances (3 / 3 / 1) — omitted by ruling (`materialize --omit`; the hole in
the bed's provenance). The 2x canonical bed was materialised from five runs (claims §5.53) and
carries the same instability unread. Shape of the work: read the 2x bed's state shares against
the probe set's, and give the 2x material's fits the share-weighted variance as an uncertainty
rather than a byte. `g1/stability-2x.txt`, `g1/materialize-2x.dry.txt`.

## CLOSED by W25 G3b's joint re-fit: W24's lit edge and W25's along-side field grade the SAME diagonal, and the exponent was fitted before the field existed (W25 G3, 2026-09-09)

`optics.regular.rimLitExponent` 1.15 multiplies the rim by `(√2·|n · L|)^p` with `L` the exact
top-left/bottom-right diagonal, so it is maximal at the NW and SE arcs; `optics.regular
.rimAlongSideSlope` 0.45 multiplies it again by a saddle that is `+1` at exactly those two corners.
W24 fitted the exponent with the position term absent, on 285 bins that include the corner arcs, so
it absorbed part of the position grading — and G0's along-side reader, which walks only the STRAIGHT
part of a side, could not see the overlap from its side either. The two now double-count on the
arcs. Measured at G3's dry run on the canonical bed, 1x light `dark-solid__rrect-md`: the NW bin
goes 0.14220 → 0.20344 against a reference of 0.12223 and SE 0.14384 → 0.20347 against 0.12739,
while the bins straddling the null improve sharply (NNE 0.06435 → 0.03902 against 0.03598) and the
straight sides move 0.003. Over the 28 untinted solid rows of both beds the mean bin error improves
on 5 and worsens on 9, and the nine are the thick solids the field is for. No smaller slope rescues
it: on that cell the peak bins' error grows at ≈0.136 per unit slope where the near-null bins'
shrinks at ≈0.056, so the break-even is below zero. Shape of the work: fit `rimLitExponent` and
`rimAlongSideSlope` JOINTLY on W24's 285-bin row set together with W25's 64 straight sides — the
fixtures all exist and neither constant needs a new capture. Evidence
`results/2026-09-09-w25-thick-span-composite/g3/g3-stops.txt` and `canonical-reads/`.

## The heavy share is identified and cannot land until the heavy WIDTH is a lever (W25 G3, 2026-09-09)

The probe set identifies `sizeScatterHeavyShareThick1x` at ≈0.5 on three rows — implied 0.320 at
span 128 and 0.670 at 160 on the 1x light `impulse` rows, ≈0.51 on the canonical validation row at
96 — and every check off them runs the other way: the coarse checkerboards' single-width objective
over 24 thick rows worsens 0.2373 → 0.3402 at a lift of 0.45, five probe rows exceed 0.002 ΔE at a
lift of only 0.18 and nine at 0.45, and the probe mean rises +0.00018 against the wave's 0.0001
clause. The measured cause is the width and not the share: vitrea's heavy component is 13.3 device
px at the reference's own share where the reference's is 19.5, and `sizeScatterGainMax` is not a
lever on it (8 → 10.3 left the reading at 13.29 — the heavy tap is a mip-chain level whose effective
width saturates). Shape of the work: give the heavy tap a width that follows a constant, in
`packages/renderer-webgpu/src/wgsl/`, and re-fit the share on these same rows behind it. Evidence
`results/2026-09-09-w25-thick-span-composite/g3/g3-dryrun.md` §1.2 and the g2 rung `rG`.

## The 2x heavy share cannot be reached without moving a W15 constant that reaches the thin capsule (W25 G3, 2026-09-09)

`sizeScatterFloor2x` is 1, so `kDeep` is saturated at every 2x span before `sizeScatterHeavyShare
Thick2x` is added and the clamp absorbs it: measured, not argued — at a 2x lift of 0.50 all 206 of
the probe set's 2x captures are byte-identical to the inert ones and reader A's rendered lever is
exactly 0.000 on every 2x row. The constant with headroom is the floor itself, W15's, which enters
`floor + (1 − floor)·smoothstep(sizeSpanMin, sizeScatterSpanMax, span)` and therefore reaches span
32 and 44 as well, which X5 forbids. Shape of the work: a 2x body re-fit that treats the floor and
the thick lift together on the probe set's 2x rows, with the thin capsule's 2x reading (reader A:
reference share 0.111, vitrea 0.338 at span 32) as its own row rather than as a stop.

## No golden scene is thin enough to test the size law's zero (W25 G3, 2026-09-09)

The renderer's thirteen golden scenes have thickest spans 44 … 92, so every claim of the form "a
surface at or below `sizeSpanMin` = 32 cannot move" is vacuous in the golden suite and is carried
only by unit tests and by the calibration bed's `rrect-sm` cells. W25 G3's attribution spec asserts
it and passes on an empty set. Shape of the work: one golden scene whose surface is 32 CSS px or
smaller on its short side, which would make every future size-law wave's thin claim a byte check.

## The isolation proof's "the outer shadow moves no colour and takes no alpha down" is now a one-code bound, not zero (W25 G3, 2026-09-09)

Both canvas passes blend premultiplied source-over into an eight-bit target, so the optics pass
composites onto an already-quantised shadow and the two roundings can differ where the rim is
brighter. Measured at the declaration: 45 colour channels move by exactly 1 on 15 pixels lying on
the contour at the checkerboard's own 16 px pitch, and 5 pixels in the canvas's last column take
alpha down by exactly 1 with their RGB unchanged; at `rimAlongSideSlope` 0 both counts are 0, which
is why the strict form held for eleven waves. The assertions in
`packages/renderer-webgpu/e2e/golden/isolation.spec.ts` are now "no channel by more than one code,
on fewer than a thousandth of the canvas" with the measurement in the doc comment. Shape of the
work: read the shadow and the optics passes back at float precision, or compare premultiplied
values, so the guard can go back to zero.

Closed 2026-09-10 by W25 Decision Log 6: the parent re-opened `rimLitExponent` and the two were
fitted TOGETHER on a rendered grid of 46 points over the plane, landing (0.85, 0.10). The thick
solids' aggregate bin error goes 0.17527 -> 0.17208 where the field alone under the old exponent
took it to 0.26311, and the named cell's NW and SE bins come back inside the reference (0.020 ->
0.015 and 0.016 -> 0.011 against 0.081 and 0.076). What is left is a different object and has its
own entry below.

## The rim's AMPLITUDE at the corner arcs is too high, and it is what both rim factors now trade against (W25 G3b, 2026-09-10)

With the direction and position halves fitted jointly there is no confound left, and the residual
that remains is one number in the wrong place: on the 1x light `dark-solid__rrect-md` the reference
reads 0.189 on its straight sides and 0.122–0.127 on its diagonals, where vitrea reads 0.211 and
0.137 — brighter everywhere, and brightest where the reference is dimmest relative to its own
sides. Three of the canonical bed's eight thick solid rows still worsen at the landed pair for that
reason (worst +0.00064 of normalised bin error, 1.8 %), all of them `dark-solid__rrect-md`, and no
(exponent, slope) pair on the grid fixes it because neither factor can lower a rim's amplitude
without also flattening its shape. The amplitude is W23's law (`rimAlpha`, `rimLevelGain`,
`rimWidth`), fitted on the STRAIGHT spans that both of these factors leave exactly alone, so the
arcs have never had a row of their own. Shape of the work: give the amplitude law an arc term, or
re-fit it on the angular reader's bins rather than on the contour reader's spans, and re-run the
joint fit behind it. Evidence
`results/2026-09-09-w25-thick-span-composite/g3/g3b-bins.txt` and `g3b-fit.txt`.

## A material change can make a calibration cell unmeasurable, and only the run says so (W25 G3b, 2026-09-10)

At the joint objective's own minimum over the allowed set, (0.70, 0.15), the collapsed
`dark-solid__capsule-button` loses its contour on the GPU tier at 1x in both schemes: the capsule's
band is entirely corner arc, both rim factors dim it there, and `contourCurvature` reads a 0.00 px
contour, so `compare` refuses the cell and two calibration rows drop out of the bed. Nothing in the
fit's objective, the wave's stops or the adopted gate would have caught it — the gate never sees a
cell that was not written — and it was found only because the dry run's own group counts fell from
nine to eight. Shape of the work: make `compare` report a cell it could not measure as a FAILED
cell in the matrix rather than an absent one, so a coverage loss fires a stop instead of quietly
shrinking a mean; and give the fidelity gate a pinned cell count per profile and tier.

## A second dry run into the same `--out-matrix` doubles every cell and the gate reads both (W25 G3b, 2026-09-10)

CLAUDE.md warns that a cell's key carries the material document's sha256 and that `compare` appends
beside the old rows after the profile changes. W25 G3b hit it: two dry runs at two materials into
one `--out-matrix` left 397 cells where 229 were expected, and the adopted gate failed 25 of 37
cases on the duplication alone before anything about the material was read.
`g3b-reduce.py` is the fix used here — keep the rows whose capture path names the documents on disk
now — but the run scripts should not need it. Shape of the work: have `g3-dryrun-run.sh` and its
siblings `rm -f` the matrix they own before the first run, and have `compare` warn when it appends
a cell whose (profile, scene, tier, renderer) already exists under a different document digest.

## The demo page reads `scenes.json` directly, so any declared set reaches the public scene picker unless filtered there (W25 G4, 2026-09-10)

From G1's declaration to G4's landing the 52 probe scenes were in the demo's reference picker
(`apps/demo/src/site/scenes.ts` builds `REFERENCE_SCENES` from the split), and the rebuilt matrix
handed them figures from the wrong profile. G4 filters `split.probe` out. The next declared set
needs the same line, or the filter inverts to an allow-list of the gated sets — the second is the
one that does not rot. Closes with the allow-list. `g4/g4-landing.md` §4.

## The CSS tier writes a tone response onto an unpainted texture source for about 120 ms after load, before the stage canvas's first frame (W25 G4's bisect, 2026-09-10)

The demo's untinted plate carries `--vitrea-occlusion` 0.667 / `rgba(254, 254, 254, 0.667)` for
~120 ms and then settles at 0.815 / `rgba(255, 255, 255, 0.815)` once the rAF-driven stage canvas
delivers a frame and is analysed. A test that baselined on the transient was green or red by how
fast the page came up (`color-scheme.spec.ts:90`; fixed in the spec at `19be52f`). An honest
state of the page, but a visible one: the runtime could withhold the CSS tier's write until a
registered source has delivered its first frame. Closes with that guard and a pixel test of the
first 200 ms.

## A second session-flake cell, on the nested pane at 1x dark, whose recheck agrees with the landing rather than the dry run (W25 G4, 2026-09-10)

`1x-dark / checkerboard__glass-over-glass__rest / css`: the landing's render differs from
G3b's dry-run digest by 1 px / 1 code at (279, 198); re-captured twice to scratch it matches the
LANDING — the opposite verdict to the toolbar cell's five sightings, where the recheck matches
the dry run. No shape metric moved. Two cells now, two directions; the toolbar entry's shape of
work (a capture-time re-read against the cell's own second frame) covers both.
`g4/g4-referee.txt`.

## The contour instrument refuses a flat-cornered dark square, so eight probe cells and the increased-contrast holdout cell land without shape rows (W25 G4, 2026-09-10)

Six of the eight probe runs exit 1 on "contourCurvature: a 0.00px contour … carries no
curvature" — the same refusal `hc-text__capsule-button__rest` under increased contrast has exited
on since W20 — so 408 of 416 probe rows land, the dry run's set exactly. If the probe set is to
be the fitting ground for a width law, the instrument's refusal on a dark solid whose silhouette
the extractor cannot round is worth a look in W26: the cells' perceptual rows are intact, and a
`--write-partial` that records the shape axis absent rather than exiting would keep the run's
exit code honest. `g4/g4-runs.txt`.

*Amended 2026-09-10 (W26 G3a; claims §5.124):* **the silhouette IoU's correction to the decidable
region does not touch this entry, and it is not a partial fix of it.** That correction changes what
population one metric is averaged over; this refusal happens earlier and elsewhere — `contourCurvature`
exits on a contour it measures as 0.00 px long, on a silhouette the extractor recovers with no
roundable corner at all — and it takes the whole shape axis with it rather than moving a number.
The two share only a cause, which is the luminance-delta rule on a dark solid, and that cause is
untouched. This entry stands exactly as written.

## The material's sharp blur component, the heavy component's width and the level above the knee: what W25 measured and could not move (W25 recomposition, 2026-09-10)

The thick surface's body against Apple's at the 0.14.0 landing, all from the probe set at both
scales: vitrea's sharp component 1.67 device px against 2.79 at 1x (35–40 % low; it is
`blurSigma`, the thin capsule's own, X5-entangled); the heavy share 0.23 against 0.47 (1x) and
the heavy component 13.3 against 19.5 device px at the reference's share, the width not a lever
on `sizeScatterGainMax` (a mip level saturates); the level above the knee +2 … +4 codes on one
backdrop and sign-flipping across backdrops; the nested base's σ-match untouched. Chartered as
W26: a heavy tap whose width is a continuous parameter, fitted on the probe set's coarse
checkerboards at both scales; then the share per scale (the 2x lever through the floor), the
level re-read, the CSS mirror. Closes when W25's clauses 2 and 3 are met.

## The heavy tap's gain has been clamped at the pyramid's last level since it was fitted, and three constants grade an axis the clamp discards at 1x (W26 G0, 2026-09-10)

`scatterLod = clamp(bodyChainLod + log2(gain), 0, chainMaxLod)`: on the bed's 320 × 200 backdrop
the chain has five levels (`MIN_LEVEL_EXTENT` 8), `chainMaxLod` is 4 and `bodyChainLod + log2(8)`
is 4.06, so every gain from 7.5 up draws level 4 — reader A reads the three 1x impulse rows
identical to the last digit at gains 8 / 10.3 / 16 / 32. `sizeScatterGainMax`,
`sizeScatterGainMax2x` and `sizeScatterGainFar2x` were fitted on real objectives and moved them
at dpr 2 (a level deeper); at dpr 1 they are inert above the clamp, and a larger backdrop raster
would give the same profile a different heavy width. W26 replaces the width with a Gaussian at the
tap (claims §5.119 §1, §4); the three gain constants stay as the below-saturation grading until
the wave's G2 declares what it retires. `g0/tap-today.txt`.

## `CHAIN_SIGMA_AT_LEVEL_1` under-states the chain's level-1 width by 24 %, and the chain's kernel is platykurtic (W26 G0, 2026-09-10)

The downsample pass simulated exactly reads σ 1.570 / 3.340 / 6.799 / 13.660 / 27.351 level-0
texels at levels 1…5 with kurtosis −0.23 at every level — neither a Gaussian nor a box, 12 % of
peak from the best Gaussian. The advisory constant is 1.2; the body blur's residual pass absorbs
the miss, so nothing drawn is wrong, but every "the chain's blur is about σ" statement inherits it.
W26 carries the measured table as `CHAIN_LEVEL_SIGMA` for the heavy tap, which has no residual to
absorb with. Closes when `bodyBlurPlan` reads the same table and the goldens attribute the move.
`g0/chain-kernel.txt`.

## Reader A's window on the 64 CSS px impulse pitch cannot hold a 19.5 device px heavy component at 1x (W26 G0, 2026-09-10)

The reader's window is half the dot pitch — 30 device px at 1x, 60 at 2x — so the 1x ladder over
σ 10 → 25 reads 14.66 / 14.84 / 16.99 / 12.91 / 61.75 / 61.75 (non-monotone, then parked on its
own `delta ≤ 60·scale` bound) while the identical drawn kernel reads monotonically at 2x. The
reference's own 1x read of 19.52 sits at that edge and is quoted with the caveat from here on;
vitrea's per-row 1x spread at one true width (9.08 / 14.36 / 19.78, median exact) is the same
effect. W26 G1 extends the reader to a lattice model over the whole tile; a wider-pitch impulse
probe scene is the fallback and a sitting. `g0/mapping.txt`, claims §5.119 §6.

**Amended (W26 G1, 2026-09-10; claims §5.120 §2).** The window is the smaller half of the cause and
the entry stands as written. G1 built the window away — reader D fits the whole tile as a lattice
and is validated exact on the model, within 5.2 % on the chain's own kernel and within a median
4.5 % of reader A where reader A works — and the 1x rows are still unreadable, because the FIXTURE
does not carry them. See the entry below.

## One heavy width per source loses the 2x span grading the reference shows on the largest impulse row (W26 G1's structure, 2026-09-10)

The reference's heavy component at 2x reads 11.29 / 12.03 / 16.92 device px on `impulse__rrect-md`
/ `-ml` / `-lg`; a third pyramid texture at one σ per source lands the first two and misses the
third by about 30 % (W26 Decision Log 2 (f)). Recorded as a gap rather than answered with a second
texture: closes with a per-span width — the residual blur graded by the same ramp the share
follows, or a second texture blended by span — once the one-width material's floors are known.


## The 1x `impulse` fixture cannot carry the heavy component at 8 bits, so no reader can fit the 1x width on this bed (W26 G1, 2026-09-10)

The native 1x `impulse__rrect-lg` interior has a standard deviation of 0.0055 in linear luma at a
level of 0.4508, where one 8-bit sRGB code IS 0.0059 — the whole surviving modulation is about one
display code, and the HEAVY component's own peak is 0.08–0.33 codes on every 1x row (2.56 on
`2x rrect-md`, which is why the 2x rows read). Quantisation is then a deterministic staircase of the
field rather than noise, concentrated at the dot cores, and a spurious NARROW second component fits
it better than the true wide one; a matched low-pass scanned 0 → 4 device px quiets the staircase and
collapses the sharp component into the heavy one instead. Decisively: a heavy component of 13.42
device px and one of 25.0 device px, each at its own share, are bit-identical on 96.7 % of the tile
after quantisation. Closes with a probe scene whose transmitted dot peak is many codes rather than a
fraction of one — the arithmetic puts that at about a 12 CSS px dot on a 128 CSS px pitch, nine times
the present heavy amplitude — declared in `scenes.json` and captured in a native sitting, which is
the user's console. `g1/reader-d.txt`, claims §5.120 §2.

**Amended (W26 G1 §7, 2026-09-10; claims §5.120 §11).** The entry stands for the IMPULSE fixture and
is narrowed: the coarse `checkerboard-64` rows carry 63-73 display codes and reader D returns the
drawn 1x heavy width on them to 0.0-1.8 %, so a 1x width IS readable on this bed and the wider-pitch
probe scene drops to second priority. It is not the blocker any more; the entry below is.

## Reader A's fitted SHARP component is a conditioning statistic, and two reference rows fail it (W26 G1, 2026-09-10)

Where reader A's two-component fit returns a sharp σ of 9–12 device px it has split one wide kernel
into two wide halves and the "heavy" it reports is not the heavy component. The reference's 2x
`impulse__rrect-ml` and `-lg` do exactly that (sharp 11.80 and 9.67, against `rrect-md`'s 1.40 and
the 1x rows' 2.74–2.79), so §5.113 §2's 12.03 and 16.92 are not readings of the heavy component.
Closes by reporting the sharp σ beside every reader-A heavy σ in the ledger and by refusing a fit on
a row whose reference sharp exceeds a stated bound. `g1/fits.txt` §0, claims §5.120 §3.

## Vitrea's SHARP component is about 40 % narrow at 1x and no constant addresses it (W26 G1, 2026-09-10)

Reader A reads vitrea's sharp σ at 1.65–1.84 device px on every rung of both of W26 G1's ladders,
against the reference's 2.74–2.79 on all three 1x impulse rows. W26 Decision Log 2 (d) made the
sharp width a named quantity of the wave because the coarse checkerboards' residual belongs to it;
this is what it reads, and nothing in the material moves it — `blurSigma` is fitted on other rows and
was declined as a sibling in W25. Closes with a wave that fits the sharp component on the impulse
rows with the heavy one held. `g1/fits.txt` §5, claims §5.120 §8.


## The reference's heavy component is not identified: two backdrops give it a factor of 3 apart, because Apple's kernel is not two Gaussians (W26 G1 §7, 2026-09-10)

The 1x reference `rrect-lg` reads a heavy component of 19.52 device px through the impulse tile
(reader A) and 8.42 through `checkerboard-64` (reader D), and the two instruments therefore disagree
on the SIGN of vitrea's error. A joint fit of ONE kernel across both tiles at once does not
reconcile them and fails its own control — it under-reads vitrea's KNOWN 13.42 device px, the
chain's level 4 at the inert default, by 14-23 % — and its residual on the impulse tile is 2-7 times
its residual on the checkerboard for both surfaces. Debiasing each instrument by what it reads
vitrea's known kernel as leaves the reference at 18.2 (impulse), 6.0-7.1 (checkerboard) and 11.1-12.4
(joint). Every reader's residual on the real surfaces is 5-7 times its residual on its own
synthetics. So a two-Gaussian reader recovers whichever two Gaussians the backdrop weights, and W25
clause 2's "heavy sigma within 15 % of the reference's" is not a well-posed target at 1x. This
blocks the 1x width fit that W25 and W26 exist to take. Closes with a kernel model of more than two
components — or two with a shape parameter — fitted jointly across three or more backdrops of one
surface and validated FIRST on vitrea's own known kernel; no sitting needed. `g1/joint.txt`,
`g1/checker.txt`, claims §5.120 §12.

## A scratch rung patches the light document only, so its dark captures render the OLD material (W26 G1 §7, 2026-09-10)

`g0-candidate.py`'s `light:` scope writes a constant into the light profile document, and the dark
profile is a difference document resolved over `DEFAULT_MATERIAL_PROFILE` rather than over the light
patch (`tuned-profiles.test.ts` resolves both the same way). A dark capture at a scratch rung
therefore takes any constant the dark patch does not name from the CODE default, which for a wave's
new constants is inert — while a LANDING, which edits the default, does reach the dark scheme. W26
G1's first probe table read every dark cell as moving by exactly 0 for this reason and had to be
re-captured with `both:`. The tell is a column of exact zeros. Closes by making a rung's candidate
writer default to `both:` for constants the dark patch does not name, or by having a rung refuse to
capture a dark profile whose resolved material does not carry the constants the rung names.
`g1/g1-dark.sh`, claims §5.120 §10.

## Vitrea's own drawn kernel is a ground truth no reader was calibrated against until W26 G1 (W26 G1 §7, 2026-09-10)

At the inert default the deep sample is exactly the chain's level 4, whose half-maximum sigma is
13.42 device px, mixed with a body of 1.25 — so every width reader built since W24 could have been
calibrated against a known answer at any point. Doing it for the first time in `g1/joint.txt` put a
bias of +7 % on reader A over the impulse tile, +23 to +39 % on reader D over `checkerboard-64` and
-14 to -23 % on the joint fit, and turned a disagreement between readers into a measurement. Closes
by making that calibration a standing part of any width reader's validation, beside the synthetic
kernels: a reader that has not been read against vitrea's own known kernel has an unmeasured bias.
`g1/joint.txt`, claims §5.120 §12.

## About one display code of Apple's thick interior is not a radially symmetric convolution of the backdrop (W26 G1b, 2026-09-10)

Every kernel family, a free forty-node radial profile included, leaves 1.79–2.01 display codes RMS
of the reference's interior unexplained against 0.83–1.17 of vitrea's through the same reader —
3.22 on `hc-text` at 1x against 1.35. The raster is aligned (0.00 codes at zero shift), and a depth
nuisance absorbs anything that varies with depth alone. Candidates: a non-symmetric kernel, a
transmission not affine in the backdrop's luma (per channel or per level), a kernel varying with
something other than depth, or a component that is not a convolution. It bounds the trust in every
width fitted on this bed. Closes with an instrument that separates those four: a per-channel read,
an oriented read on the text row, a read at two tone levels of one backdrop. `g1b/reference.txt`.

## The sharp component is 20–30 % too wide, reversing the ledger's sign; it is the body (chain level 1 plus a third of a texel), thin-entangled (W26 G1b, 2026-09-10)

The reference's sharp Gaussian reads 1.29–1.40 device px across eight backdrops against vitrea's
1.64–1.75; §5.120 §3g's "40 % too narrow against 2.74–2.79" was the impulse tile's single-backdrop
projection. Vitrea's sharp is the chain's level-1 kernel (half-maximum 1.542, not the advisory 1.2)
plus `bodyBlurPlan`'s residual, so `blurSigma` 1.25 does not name what is drawn. It is the thin
capsule's own width (X5) and is not fitted in W26. Closes with a wave that fits `blurSigma` on the
family reader with the thin cells' floors re-read — and reads `bodyBlurPlan` on `CHAIN_LEVEL_SIGMA`
rather than the advisory constant.

## `sizeScatterGainFar2x` grades the 2x heavy width from 8.0 to 12.2 across spans 96 → 160 where the reference goes 7.9 → 9.0 (W26 G1b, 2026-09-10)

Read with the family reader, the reference's heavy width barely grades with span at 2x and
vitrea's grades by half. With the heavy texture in place the thick body no longer reads
`scatterLod`, so the constant is expected to fall silent above the knee; G1c states what it still
grades and G2 declares whether it is retired. Supersedes the direction of the W26 G1 entry "one
heavy width per source loses the 2x span grading", which is kept beside as recorded.

## The heavy width has no small values: a σ just above 0 draws the raw backdrop, not "almost the chain tap" (W26 G1c, 2026-09-10)

`heavyTapPlan` at σ 0.001 selects chain level 0 with no residual, so the deep sample becomes the
unblurred backdrop — the opposite of the σ 0 meaning (the chain at `scatterLod`). Both anchors are
declared at 9 and `rampAtScale` never visits a small value, but a profile author could. Closes with
a floor in the plan (a σ below the chain's level-1 width reads as the level-1 kernel) or a
validation that rejects 0 < σ < `CHAIN_LEVEL_SIGMA[1]`. `g1c/ladder.txt` §1.

## `sizeScatterGainMax`, `sizeScatterGainMax2x` and `sizeScatterGainFar2x` are inert at any material naming a heavy width; their retirement is a code-removal wave (W26 Decision Log 6 (b), 2026-09-10)

Fifty rows byte-identical between 9.9 and 4.8 at the candidate: the heavy texture overwrites the
tap `scatterLod` feeds on every group whose source has a pyramid. They still define what a profile
naming NO heavy width draws. Closes with a wave that removes `scatterLod` and the three constants
and defines the σ 0 path (the chain's last level, today's dpr 1 draw), with the goldens attributing
the move and the fingerprints re-recorded. `g1c/clause.txt`.

## The dark bed's thick-span ΔE prefers a heavy width its own reference does not have (W26 G1c, 2026-09-10)

At the candidate the dark reference reads 9.15 (1x) / 7.80 (2x) and the dark bed's thick spans
worsen (1x: 128 0.01703 → 0.01892, 160 0.02173 → 0.02404) — errors three times the light bed's
before and after. The 0.14.0 width of 13.418 was masking something in the dark scheme's thick body
(a level, a tone response, or the W25 size-keyed adaptation), not describing its kernel. Closes with
the dark thick body read with the family reader's residual split by backdrop and by level, against
the dark difference document's own constants. `g1c/bed.txt`.

## The holdout scenes' fixtures were read by W26 G1b's instrument; the fit is holdout-free and the once-read checks the fit, not the instrument (W26 Decision Log 6 (d), 2026-09-10)

Three of the eight backdrops G1b's reader was validated on are holdout scenes. G1c dropped them and
fitted on the rest; G2's holdout read therefore checks the constants and not the reader that
produced them. A future instrument built on this bed should exclude the holdout scenes from its
validation set from the start — the probe set exists for that.

## The accessibility frost no longer reaches the heavy component, on either tier (W26 G2, Decision Log 7 (d), 2026-09-10)

`frost: "increased"` multiplies `blurSigma`, and until W26 both tiers' heavy components were
multiples of it — so an increased frost widened the whole body. A heavy width named in device px is
not a multiple of anything, so the fold now reaches the SHARP component alone. Measured cost: on
`apple-macos-26.5-1x-light-reduced-transparency` the CSS tier's heavy layer goes 24.15 → 9.000 CSS
px, `dom / calibration / checkerboard__capsule-button__rest` reads `silhouetteHolesWeb` 0 → 6 against
a native 0 and leaves the shape gate (`PREDICATE_EXCLUDES` 31 → 32), and that profile's CSS
calibration ΔE rises 0.00447 → 0.00464. **The tiers AGREE for the first time here**: at dpr 1
`scatterLod` was clamped at `chainMaxLod`, so the frost could not widen the GPU tier's heavy tap at
all and the mirror was drawing nearly twice the renderer's width under this preference. Closes with
a reading of Apple's own reduced-transparency thick body on the family reader and a decision on
whether the fold multiplies `sizeHeavyTapSigma`; it is a material change and needs its own rung.
`g2/g2-dryrun.md` §5, `g2/gate-calval.txt`.

## The two tiers' heavy widths are different numbers as of W26, and the CSS tier's is derived from constants the GPU tier no longer reads (W26 Decision Log 7 (b) and (f), 2026-09-10)

**RULED, and this is the residual the ruling leaves.** Deriving the CSS tier's heavy layer from the
profile's own width — one quantity across the seam for the first time — took twelve of the fourteen
thick regression floors under, all `dom` rows at spans above 96, while the GPU tier's canonical
groups moved by less than 0.00001; the same constants without it breach ONE floor, measured on
captures rather than inferred. By eye the 1x dark nested pane at that configuration showed the
checkerboard through the inner glass where neither the native capture nor the GPU candidate does. The
user ruled the derivation declined for this wave.

So the CSS tier goes on deriving its heavy layer from `sizeScatterGainMax` / `…Max2x` /
`…GainFar2x`, which the GPU tier no longer reads at all — **13.800 CSS px here against 9 device px
there at dpr 1, and 4.455 → 6.121 across spans 96 → 160 against a flat 4.500 at dpr 2**: 53 % wide,
36 % wide, and 1 % narrow respectively. `tier-coherence.test.ts` pins those three ratios so the gap
cannot widen quietly and cannot be closed by accident.

Closes with a CSS-tier wave that asks the question this one could not: why a two-layer body at the
CORRECT component widths loses structure the mip-tap projection kept. The suspects are named — the
series-with-mask composition against the renderer's per-pixel mix, and the collapsed
single-`blur()` projection, which runs off the same gain constants — and the bed to answer it on is
the large-span checkerboards, where the whole cost landed. `g2/floors.txt`, `g2/floors-gpuonly.txt`,
`g2/g2b-floors.txt`, `g2/g2b-css-identity.txt`.

## The CSS tier's sampling padding is derived from the PROJECTED sigma and the heavy layer is wider than it at the thin end (checked at W26 G2, pre-existing and improved, 2026-09-10)

A group's `samplingPadding` floor is `3 x groupScatterSigma(...)` at dpr 1 — the ramp's area-average
projection, which is `blurSigma x (1 + (gain - 1) x mix)`. The two-layer body's HEAVY layer has never
been a function of that mix: before W26 it was `blurSigma x gain x effectiveRatio` = 13.8 CSS px at
every span, and since W26 it is the profile's own 9.000 CSS px. At the size law's thin end the
projection is 4.75 CSS px, so the padding floor is 14.25 px against a 27 px (was 41.4 px) reach.
**W26 does not introduce this and strictly reduces it**; it is recorded because the wave checked it
and because `root.ts`'s own comment names the same class of bug one wave earlier. Closes with a
padding floor taken over the widest layer the tier will actually write rather than over the
projection it no longer draws — `cssTierHeavySigmaCssPx` at the group's largest member.

## ~~`checkerboard__glass-over-glass` at 2x dark: a silhouette floor that measures the extractor's threshold, not the material~~ (W26 G2b, Decision Log 7 (f), 2026-09-10) — CLOSED 2026-09-10 by W26 G3a

`texture / holdout / … :: silhouetteIoU` 0.92707 → 0.90362 against a floor of 0.9257, with
`silhouetteHolesWeb` 39 → 45 against a native 0 — the one floor W26 breaches. Measured: the pane's
interior level moves 0.11419 → 0.11418 and its standard deviation 0.24677 → 0.24685, and the picture
moves by a mean of 0.19 of an 8-bit code. What moves is a population on a fence — 21 290 of 135 200
pixels sit within 0.005 of a 0.02 luminance-delta probe and 2 640 cross under it with none coming
back — and it crosses TOWARD the native, whose own under-threshold count (17 010) is above the
candidate's (16 970) and far above 0.14.0's (14 330). The harness nevertheless recovers a hole-free
mask from that native, so its rule does more than threshold and **whatever fills the native's holes
does not fill vitrea's**; that asymmetry is the thing to fix, and it is the same instrument the
tracker's flat-cornered-dark-squares entry names. Closes with the silhouette recovery made
symmetric between the two sources, or with the floor re-pinned by the user on this measurement.
`g2/g2b-nested.txt`, `g2/sheets/g2b-nested-4x.png`.

**CLOSED 2026-09-10 by W26 G3a** (claims §5.124; W26 Decision Log 8), and one sentence of the entry
above is wrong, kept as written with the correction beside it. **The harness does NOT recover a
hole-free mask from that native**: the committed matrix records `silhouetteHolesNative` = 14 on this
very cell, and the native's silhouette is the *smallest* of the three (106 876 px against 0.14.0's
109 698 and the candidate's 107 058, of a 112 416 px region). The "hole-free native" reading came
from a proxy that thresholded distance from the checkerboard's mean over a hand-cut rectangle; the
extractor thresholds against the background raster pixel by pixel, and the two are different
quantities. There is therefore **no asymmetric rule** — one extractor, both sides, nothing keyed on
the native. What there is: each side loses ~5 400 pixels over black checker cells with 33 px of
overlap, the native under its inner pane (transmission 0.02029, one code over the rung) and vitrea on
the single-glazed base, and IoU was paying for both. The metric is corrected — taken over the
decidable region, the declared region minus every pixel enclosed by a hole of either mask — the row
reads 0.92707 → 0.99979 on the committed bed, and the floor is removed rather than re-pinned. The
extractor itself is unchanged and its own charter stays open in the W21 G2c entry above.

## Two things W26 G3a's silhouette correction left undetermined: whether the reference's dark-cell transmission is real, and what the IoU stopped seeing (W26 G3a, 2026-09-10)

Both are named in claims §5.124 and neither is a defect in what landed; they are the parts of the
correction that a measurement could not settle.

**Is 0.02029 Apple's material or ScreenCaptureKit's quantisation?** On
`checkerboard__glass-over-glass__rest` at 2x dark the reference's transmission through its
double-glazed inner pane over a black checker cell has a median of **0.02029** linear — one 8-bit
code above the extractor's 0.02 rung, and the reason the reference's silhouette carries 14 interior
holes there. One code decides whether those holes are a property of the material vitrea is chasing
or of the capture path it is measured through, and one fixture at one scale cannot say. It matters
past this metric: a material target read off that pane inherits the same ambiguity. Closes with the
same surface captured through a second path (a higher bit depth, or a native readback that is not
ScreenCaptureKit's 8-bit composite), or with the transmission read on a backdrop whose dark level is
not zero, where the rung is not an absolute brightness test.

**The IoU no longer prices a punched interior, and only two rows still do.** By construction the
corrected metric drops every pixel enclosed by a hole of either mask, so a tier that genuinely
perforated its own surface would now score full IoU over the remaining population. What sees it
instead: `silhouetteHoles{Native,Web}` on every cell, and W20's `declaredIoUWeb` on the tiers whose
alpha the harness will read. That is a deliberate trade, not an oversight — the alternative rules
were measured and were worse (hole-filling drags ten cells down; hysteresis moves two thirds of the
bed) — but it is a real loss of sensitivity in one metric, and nothing gates on the two rows that
replace it. Closes either by gating on the hole counts against the reference's own (the topology arm
claims §5.14 built, withdrawn at §5.15 for costing 77 cells — re-measurable now that the contour and
the IoU are both immune to holes), or by an extractor that has no undecidable pixels to begin with,
which is the W21 G2c entry's charter.

## The dark nested pane's topmost glass does not transmit the checkerboard, and the dark bottom pane and the dark 64-checker rrect are darker than Apple's (the user's eye on W26 G2b, 2026-09-10)

Apple's inner (topmost) dark pane lets the checkerboard show through; vitrea's is opaque. Apple's
bottom dark pane, and the dark `checkerboard-64__rrect-*` probe rows, read brighter than vitrea's
by eye. These are the dark scheme's level and transmission at thick spans — the thing the W26 G1c
entry says 13.418 was masking — and they are what the dark bed's thick-span ΔE (three times the
light bed's) is measuring. Closes with a dark-scheme wave that reads the dark transmission and level
per span against the dark reference with the family reader's residual split by level, and the
nested pane's two layers separately. Evidence: `g2/sheets/g2b-nested-4x.png`, G2c's ring reads.

## Apple's rim reads more three-dimensional than vitrea's on the dark solid rrect — "edgy-glassy" against a hint flat, about 2 % short (the user's eye on W26 G2b, 2026-09-10)

By eye after W24's lit edge and W25's along-side field. The rim's curvature and the lens's band at
the contour are the mechanisms recorded at W24 (the arc amplitude as a three-term joint fit is in
W26's Deferred). Closes with the rim's radial profile read against the reference at the contour on
the dark solids, and a curvature term declared on it.

## The dark scheme's thick body holds at its 0.14.0 draw: the family reader's dark width (9.15) is contradicted by three appearance measures, and Apple's dark pane is milkier AND brighter (W26 Decision Log 10, 2026-09-10)

At σ 9 the dark bed's thick spans worsen, the eye's cell's transmission moves away from Apple's
(0.0566 → 0.0673 against 0.0477) and the user's eye reads a gradient; Apple's pane has 7.38 codes
of its own light against vitrea's 4.95 and washes the checker more. The dark difference document
names the heavy width 0 / 0 (the chain tap, byte-identical to 0.14.0), so the three gain constants
still draw the dark scheme. Closes with the dark wave: the dark thick body's level, transmission and
width read together (the family reader with the milk term modelled per ring), the nested pane's
two layers read separately (Apple's topmost passes 3.1× ours in dark; ours passes 1.9× Apple's in
light), and the dark panes' 1.3–1.6 codes. `g2/g2c-eye.md`, claims §5.125.

## The 0.02 luminance rule reports a coarse dark backdrop's structure as the silhouette's, and it has now produced a second cell one wave after the first (W26 G3, 2026-09-10)

W26 Decision Log 8 found the extractor's `|Y − Y_background| ≥ 0.02` rule degenerating toward an
absolute brightness test over a black checker cell, reporting the BACKDROP's structure as the
surface's, and corrected `silhouetteIoU` for it (claims §5.124). The landing's re-derivation of
`PREDICATE_EXCLUDES` turned the same mechanism up on a different cell: `texture / holdout /
checkerboard__rrect-lg__rest / apple-macos-26.5-2x-light-standard` enters the exclusion list on the
BODIES arm at the landed material, `silhouetteBodiesWeb` **1 → 3** against a native 1 and a region
of 1, with `silhouetteHolesWeb` 4 → 7 beside it and the area arm nowhere near (0.9978 against 0.95).
Largest span on the bed, coarsest committed checkerboard, the scale where the heavy component
narrows most: less blur leaves more of the backdrop inside the surface and the rule pinches it into
two more pieces. **Every gated row is met on the cell** — IoU 0.99807, contour mean 0.204, p95 1,
max 2 — so nothing is hidden by the exclusion, and its real cost is recorded where it stays gated
(ΔE mean 0.00795 → 0.01145).

Why this is an entry rather than a note: one sighting is a cell and two is a class, and the second
one arrived from a change in the MATERIAL rather than in the instrument. As the body's heavy
component narrows toward Apple's, more of the backdrop survives inside every thick surface over a
coarse pattern, so the rule will keep converting fidelity gains into topology exclusions — the shape
gate quietly covering fewer cells the closer the material gets. `silhouetteIoU` was corrected;
`silhouetteBodies*` and `silhouetteHoles*` were deliberately left reading the interior, which is
what makes them the arms that fire.

Closes with an extractor whose rule is relative to the local backdrop rather than to one absolute
rung — the same charter as the W21 G2c entry and as the "two things W26 G3a left undetermined" entry
above, and the three should be read together and answered once. Until then, every wave that narrows
the body should expect to re-derive the predicate and should check, as this one did, that the rows a
newly excluded cell takes out of the gate are MET rather than merely unread.
`results/2026-09-10-w26-heavy-width/g3/g3-landing.md` §5.1; claims §5.126 §6.

## Black on black: vitrea reads lighter than Apple on the dark impulse and darker on the dark checkerboard (the user's eye on the 0.15.0 sheets, 2026-09-10; rated unimportant)

On the dark impulse rows vitrea's black surface over black reads lighter than Apple's; on the dark
checkerboard rows it reads darker (G2c measured the second half: Apple's dark panes 1.3–1.6 codes
brighter in what the eye receives, claims §5.125 §5). Opposite signs on two backdrops of one
scheme point at the dark tone response's shape rather than a level offset — the term W26 could not
model in the dark scheme (the "milk" of Decision Log 10). Belongs to the dark wave; the user rates
it a minor gap and the next priority is coverage.

## The `clear` variant's dimming layer is painted by no renderer (the coverage re-score, 2026-09-10)

`Glass.clear` requires a dimming policy — the runtime refuses the variant without one
(`DEFAULT_CLEAR_DIMMING`, `packages/core/src/material.ts`) — and `ResolvedMaterial.dimming` is
produced for every clear group. Nothing consumes it: `grep -rn dimming packages/renderer-webgpu/src`
returns zero hits, and `packages/platform-web/src/optics.ts` (around line 257) says so in the code
("Uncalibrated in either tier: the canonical scene matrix has no clear-variant scene"). The variant
resolves, warns and tints; its defining layer is not drawn. Found by the 2026-09-10 re-score
(`2026-09-10-coverage-rescore.md`, §1.1 and §3 "rows wrong at the time"), which moves the matrix's
`replicated, unmeasured` reading to what it should have been in August: `partial`.

Shape of the work: a `dark-solid__rrect-md-clear20__rest` probe scene now exists in `scenes.json`
(W25), so one native clear cell is capturable; paint the dimming layer on both tiers as the policy
declares (a group-level darkening beneath the material, 35 % black by Apple's one published number
as the seed), and measure it against that cell. Not a W27 child; goes to the next cut with the
`clear` variant's other absent rows (the three preconditions, the omission and localization rules).

## W27f's scratch provenance drops the first character of the first dirty path (2026-09-10)

The measurement runner `packages/calibration/results/2026-09-10-w27f-g1-measure.py` strips the
whole porcelain output before taking each line's path at offset 3. A first line whose status
starts with a space therefore loses the first path character; the ordinary candidate manifest
records `ackages/platform-web/src/optics.ts`. Commit and source-tree digests are unaffected.
This is cosmetic, nonblocking provenance debt; the gate's frozen runner and historical evidence
are not rewritten. Before reusing this runner, preserve porcelain's leading status columns and
add a test with an unstaged first entry. Keep the recorded path beside the correction, not a
replacement pretending the historical capture recorded something else. Claims §5.131 separately
limits the old capture's narrow source fingerprint; this parser issue does not excuse that limit.

**Closed for reuse by W27f G2, 2026-09-11 (claims §5.135).** The runner this gate runs is
`packages/calibration/results/2026-09-11-w27f-g2/measure.py`, G1's file with `porcelain_paths`
preserving both status columns and reporting a rename's destination, and five cases in
`measure-tests.py` — the first of them an unstaged first entry, which fails against the G1 parser.
The G1 runner and every reading it produced are untouched; `ackages/platform-web/src/optics.ts`
stays in the candidate manifest as the thing that was recorded.

## The frozen W27f G1 runner's own test suite no longer passes at this head (W27f G2, 2026-09-11)

`packages/calibration/results/2026-09-10-w27f-g1-measure-tests.py` fails one of its 35 cases on
`main` at `8cf6a89`, and has since W27c G1 merged. `StackCoverage.test_the_declared_stacks_of_the_
holdout_bed_are_the_two_glass_over_glass_cells` pins the holdout bed's declared stacks at
`{checkerboard,photo}__glass-over-glass__rest`; W27c G1 added both `__inactive` twins to
`split.holdout` in `apps/reference-apple/scenes.json`, so `stacked_scenes` now returns four. The
runner itself is correct — it reads the split rather than a hard-coded list — and no reading it
produced is affected. Only the test's expectation aged.

It is left failing rather than edited, because that file is the frozen record of how G1's evidence
was checked and editing it would make the historical suite describe a bed G1 never measured. W27f
G2's copy states the current four and adds a case for the two cells it measures. The shape of the
work, if the G1 file is ever run as a gate again: re-point that assertion at the split it is
asserting about, and note in the same commit which scene-set change moved it. The general lesson
is the one the entry above shares — a dated runner's tests are evidence of a past check, and a
scene-set change can silently invalidate one.

## Calibration and renderer tests share a fixed port and can reuse the wrong harness (W27c G1, 2026-09-10)

`packages/calibration/web/vite.config.ts` and
`packages/renderer-webgpu/playwright.config.ts` both hard-code port 5189. The renderer's
Playwright config also sets `reuseExistingServer: true` outside CI. In parallel worktrees this
can connect a golden test to a sibling's calibration page rather than its own renderer harness.
W27c G1 observed the foreign page first, then `ERR_CONNECTION_REFUSED` when that sibling's
capture driver shut its server down. The failed run was not an optical regression reading.

The isolated rerun used a scratch Playwright config with a verified-free port (5213), an explicit
worktree-local server cwd, and `reuseExistingServer: false`; the existing goldens and isolation
pins then passed unchanged. Shape of the work: parameterize the port consistently in both
configs and their drivers, and verify the harness identity before reusing any listener. Merely
choosing another shared constant moves the collision; the two independent child tasks both
initially chose 5198, which the coordinator caught before either reused it.

**Half closed by W27f G2, 2026-09-11 (claims §5.135).** The parameterisation is done: the
calibration scene server reads `VITREA_SCENE_SERVER_PORT` and the renderer's golden server reads
`VITREA_GOLDEN_SERVER_PORT`, each defaulting to 5189 so every recorded capture keeps the port it
was taken on. The renderer's two halves — `playwright.config.ts`'s `baseURL`/`webServer.url` and
`e2e/vite.config.ts`'s `server.port` — now read one variable instead of holding two copies of one
number, which is the specific way a golden run came to be pointed at a foreign page. A port is
not part of a capture's identity: `capturePath` records the browser, viewport and material
document and never the URL, so no cell key and no recorded number moves.

**Still open: identity before reuse.** `reuseExistingServer` is still `true` outside CI, so a
run that finds *something* listening on its port still trusts it. Moving the port makes a
collision avoidable, not detectable. The remaining work is a cheap identity check before reuse —
fetch the expected fixture path and refuse a listener that does not serve it — and it is worth
taking the next time either suite's harness is touched.

## The recovered inactive bed has no fresh native capture path (W27c G1, 2026-09-10)

W27c adds 121 historical inactive fixtures under a real scene state, but
`apps/reference-apple/Sources/main.swift`'s capture and layer-dump paths activate their window
and attest active presentation. They previously interpreted only `state == "pressed"`; an
inactive scene id by itself therefore could have produced active pixels under an inactive name.
The recovered entries are explicitly schema 2, single-run, pose inferred from DL14 (claims
§5.128 and §5.130), not a substitute for a newly attested native inactive run.

G1's boundary is to refuse unsupported inactive requests before capture output, while leaving
active-only scratch declarations and historical fixture consumption usable. Closing this gap
requires a native deactivation path with an inactive-presentation attestation and its own repeat
check, including preservation of tint and the separate pressed interaction. It is not a change
to the web runtime's root-pose observer, and making the Swift decoder accept the word is not a
capture implementation.

**CLOSED 2026-09-11 (claims §5.136; W27 Decision Log 13).** `capture --inactive` presents under
the `.accessory` activation policy through a window that cannot become key, ordered front and
never activated, and attests `!isKeyWindow && !NSApp.isActive` per cell into a new `presentation`
manifest field before it captures; a cell that does not attest fails the run. The tint axis and
the separate `pressed` interaction are untouched, `--scenes` narrows a run to the cells a session
asked for, and `--dry-run` rehearses every refusal without capturing. Two caveats travel with it,
neither blocking:

- **ScreenCaptureKit was never asked for an inactive window's pixels.** Screen Recording is TCC-
  denied to the build the mechanism was proved on, and TCC is keyed per bundle path, so every
  rebuild — and every worktree — needs a fresh grant. The window is `occlusionState.visible` in
  the pose and the 121 recovered fixtures are SCK output from exactly this configuration, so the
  inference is strong, but it is inference plus history. `./capture.sh probe` settles it in
  seconds and the runbook makes it the session's first step. If it ever turns out that SCK will
  not serve an inactive window, the pose is unreachable by this harness and the shape of the work
  is a second process holding the capture while the harness holds the window.
- **The repeat check is the settle loop, not a second pose.** A run proves the pose held for the
  frames that produced its bytes; it does not prove that two independent inactive *sessions* agree,
  which is what the seven-run probe bar and `materialize`'s plurality resolution are for.

## Two rehearsal-only wording limits in the capture harness (W27 DL13 review, 2026-09-12)

Both are in the dry-run path only — no real capture, no fixture and no attestation depends on
either — and both were found by review rather than by a run. Logged instead of fixed because the
change is small, the payoff is a slightly better sentence in a rehearsal, and the session the
harness exists for is days away; the next person in this file should take them.

**`rehearsalWarned` is one flag per run, so a rehearsal reports only its FIRST cause.**
`runCapture`'s per-cell gate (`apps/reference-apple/Sources/main.swift`) prints `WOULD REFUSE` once
and then stays quiet, which is deliberate — 76 copies of one sentence buries the cell count that
the runbook tells the operator to read. But the flag is a single Bool, so a rehearsal that hits a
locked screen and then a genuine pose mismatch reports only the lock. The shape of the fix: key the
flag on `Capture.CellRefusal`, once per case rather than once per run, which keeps the anti-noise
intent and costs one `Set`.

**The opening gate's dry-run branch says "LOCKED" when the session was UNREADABLE.** The gate tests
`Environment.screenIsLocked() != false`, which is true for both `true` and `nil`, and its dry-run
message names only the lock. Its own real-pass twin distinguishes the two ("or the session could
not be read, which is not the same as unlocked"), and so does `poseRefusalMessage` through
`CellRefusal.screenStateUnreadable`. Only this one branch flattens them. An unreadable session and
a locked one want different next steps, so the distinction is worth carrying here too.

## Two bounded W27d limits, real and not worth a change here (W27d review, 2026-09-11)

Both were confirmed by the independent panel and verified as bounded rather than defective. They
are logged so the next person to touch either mechanism finds the reading rather than rediscovers
it.

**The CSS tier's tint-table cache cycles above 32 distinct live transfers.**
`packages/platform-web/src/css-tier-layers.ts` keeps at most `TINT_TABLE_CACHE_LIMIT` (32) solved
tint tables and evicts the oldest inserted, not the least recently used, so a root with more than
32 distinct live transfers thrashes: every solve is a miss and every miss evicts a table that is
still on screen. It is pre-existing and not a W27d regression — the cache key is the quantised
transfer and never the blur width, so presence moving a width per frame does not multiply the
keys, and the degraded cost is exactly what the tier paid before the cache existed. The bound is
documented as deliberate at the constant ("one per material on screen is the working set; a page
with more distinct materials than this is redrawing them all anyway"). The shape of the work, if a
page ever appears that holds more than 32 materials at once: make the eviction least-recently-used
so the working set survives, and measure a real page before raising the number.

**`GlassMorph transition="materialize"` calls presence arrived within 1e-3 of its endpoint.**
`presenceReached` in `packages/react/src/morph.tsx` compares the published
`--vitrea-materialization` against its target with a tolerance rather than for equality. Today
that window cannot open: host presence runs on `DEFAULT_MOTION_PROFILE` and the content fade runs
on the root's resolved profile, which is the same channel unless an app retunes it, so
`fade.settled` already gates completion to the exact endpoint. Only a *custom* content channel
shorter than the host's 220 ms ease opens it, and then by roughly the ramp's last tenth (~22 ms),
during which the destination could be released and `onMorphEnd(false)` fire at a presence of up to
0.001 — a material that draws nothing perceptible. No user-visible failure exists today. The shape
of the fix is comparing the published endpoint exactly, and it belongs with the deferral it
depends on: the framework-agnostic root taking a motion profile so host presence can be tuned at
all (claims §5.132 §6). That deferral was decided against on 2026-09-11 (wave Decision Log 11:
a custom profile retunes only the content crossfade; the material's arrival keeps the system's
timing), so the window stays closed by design. If that decision is ever reversed, compare exactly.

## The demo's material-stage contrast test runs at 80% of its timeout on an idle machine (W27 stopping point, 2026-09-11)

`apps/demo/e2e/contrast.spec.ts` "the plates' labels hold the large-text floor" took 24.1 s alone
against Playwright's default 30 s test timeout when it was re-run by itself on `108b40d`, and it
passed. In the full serial verification of the same commit it timed out at the element-stable
check before its first screenshot, with another Claude session active on the repository. The
budget is structural: `worstRatio` in `glass-contrast.ts` sleeps through `SAMPLE_DELAYS`
(400 + 2 200 + 4 200 + 6 200 = 13 s of fixed waiting) and screenshots every `.plate strong` at each
phase on a GPU page, while the suite runs `fullyParallel` with its GPU specs beside it. The same
suite showed five failures under concurrent load at W27d's landing head and 48/48 serially, and
the port-sharing entry above is a separate cause with the same symptom. Nothing in the material
moved: every demo test has passed on `108b40d`, just not all in one run. The fix is one line —
`test.slow()` or a per-test timeout proportional to `SAMPLE_DELAYS` on the phase-sampled
contrast tests — and it was left out of the stopping-point commit so that commit changes no test
configuration; take it with the next demo e2e change and re-run the suite once, serially.

## Three W27a features have a prop and a README paragraph and no live instance (0.16.0 eye sheet, 2026-09-11)

`GlassButton tint` / `foreground`, `GlassGroup tint` and the four named ink levels
(`--vitrea-foreground{,-secondary,-tertiary,-quaternary}`) landed in W27a and shipped in 0.16.0
with nothing in `apps/` using them: every `tint=` in the demo is on a `GlassSurface`, and no file
under `apps/` passes `foreground` or names the three lower tokens (they occur only inside a built
bundle). The W27 wave's acceptance clause 2 requires "a live instance in the demo or the playground
that a reader can operate", and it was checked at each landing by prop and README, not by reading
the demo. Two pieces of work: (1) the instance — one playground plate showing a tinted button, a
tinted group and all four levels, chartered into W27e G2 because that gate re-derives the levels
and touches the playground anyway; (2) the check — a demo-side test that maps each README-documented
prop on the three public packages to at least one live site under `apps/`, so the clause fails at
the landing rather than on a release sheet. Until (2) exists, a landing's clause-2 review must grep
`apps/` for the prop, not the README.

**(1) landed 2026-09-12 (W27e G2):** the playground's tint-and-ink band
(`apps/demo/src/TintInkPlate.tsx`, `/playground/`) is that instance — a `GlassGroup tint` over a
light and a dark ground, a `GlassButton tint` in the group it steps out into, and all four levels
side by side on one surface, with both seeds under controls. **(2) is still open**, and it is the
half that stops this happening again: this entry stays until a test maps documented props to live
instances.

## Core's advisory sampling padding is still σ = 8's 24 px and wins the toolbar gap on the regular variant (W27b, measured 2026-09-11)

A toolbar partition clears `max(DEFAULT_GROUP_SAMPLING.samplingPadding, samplingPaddingFor(members))`:
core's advisory constant, which its proxy-overlap check is written against, and the material's own
requirement derived in `platform-web/src/optics.ts`. The advisory is 24 (3σ at σ = 8, the blur
when S1 wrote the padding rule); at the shipped profile the material asks 11.1 for an empty row,
11.3–12.7 for a button, a capsule and a 420 × 52 bar, 14.9 for a 420 × 72 bar, and 35.5 on the
clear variant. So on regular the advisory dominates by about 2× and the spacer is wider than the
material needs (never narrower; the 0.16.0 eye sheet read 24 px on the demo), and on clear the
material dominates and the max does real work. Retiring the constant means core's overlap check
taking the padding as an input from the platform that resolved it — core is pure and cannot import
the derivation — with `DEFAULT_GROUP_SAMPLING` kept only as the value a host without a resolved
policy is checked against. A W27b-scale change; not chartered.

## `interiorMeanBackdrop` is not a backdrop level on a sparse high-contrast backdrop (W27e G0, 2026-09-11)

The canonical matrix's `material.interiorMeanBackdrop` is the backdrop's mean over the **extracted
native silhouette** (`cli/measure.ts`, `const interior = nativeSil`), not over the declared region.
`src/report.ts` already documents what the luminance-delta extractor does over a high-contrast
backdrop — it "necessarily loses any part of the material whose level coincides with the
backdrop's" — but the consequence for this *backdrop* figure was not written anywhere, and it is
larger than the holes warning suggests. On `impulse__capsule-button__rest` the surviving population
is 71 pixels weighted to the bright impulses: the cell records **0.112676** where the same fixture
over the declared capsule region reads **0.003284**, a miss of 0.109392, and the recorded
`interiorStdDevBackdrop` 0.316196 is exactly `√(p(1−p))` at `p = 8/71`, which is how the population
size is recoverable at all. Every other dumped scene agrees with the declared region to 4.6e-5
(29 of 30 checked), so this is one cell, not a systematic bias — which is what makes it dangerous:
it reads plausibly. W27e G0 would have reported the vibrancy operator's selector as non-monotone in
backdrop luminance had it taken this figure; `packages/calibration/scripts/vibrancy.ts` reads the
fixture over the declared region instead and records both matrix statistics beside it.

Shape of the fix: report the backdrop level over the **declared** region rather than the extracted
silhouette (the declared region is already computed for `componentRegionArea`), and keep the
silhouette-scoped figure beside it under a name that says which population it has, plus the
population size so a reader can see 71 without reverse-engineering a Bernoulli standard deviation.
Recorded numbers stay as they are: the corrected reading goes beside them, never over them.

## The backdrop-root probe fails on an ancestor opacity that costs sampling nothing (W27e G0, 2026-09-11)

Measured in the W27e G0 composite probe
(`packages/calibration/results/2026-09-11-w27e-g0-vibrancy/composite-probe/`, cases
`q3--body--opacity` and `q3--body--filter`). With `opacity: 0.99` or `filter: blur(0px)` on
`document.body`, the runtime reports `probe: "fail"`, the diagnostic `backdrop-root-broken` and
`demotion: "probe-failed"` — while the material measures **unaffected**: 230,226,223 sd 3.58 against
a baseline of 232,228,225 sd 3.58, the difference being exactly the 0.99 dimming. The same
declarations on the *glass root* do break it, and there the diagnostic is right.

The rule the pixels support is narrower than the one the probe applies: an ancestor's backdrop root
costs sampling only when the content the proxy needs ends up outside it. `body` contains the page,
so nothing is lost; the glass root does not, so everything is. A page that sets an animation-time
`opacity` on `body` therefore loses the WebGPU tier for no optical reason. Shape of the fix:
condition the probe's verdict on whether the new backdrop root contains the sampled content rather
than on a root existing above the proxy — the probe already paints and reads its own patch, so the
discriminating case is one more sample outside the root. Contract X6 is unchanged by this: a sub-1
opacity on the host or on the root still kills sampling, and that was re-measured here.

## One dark CSS calibration capture is bistable between runs (W27f G2, 2026-09-11)

`checkerboard__toolbar-group__rest`, dark scheme, CSS tier, lands on one of two digests depending
on the run. Six independent capture invocations at a fixed head put `css-today` on
`625742f5a2af…` twice and `8689d9ef6fc9…` four times and on no third value; the `css-hint` arm is
bistable on two further digests, and its within-run repeat noise is 5.859375e-05 in five runs of
six and exactly 0 in one. The difference is five pixels, all outside every declared shape, at most
one channel code, with every measured term equal. Evidence:
`packages/calibration/results/2026-09-11-w27f-g2/css-bistability.json`.

This resolves an open reading rather than creating one: claims §5.131 §4 recorded the same two
digests as a change, `625742f5 → 8689d9ef`, because it had one run on each side and could not tell
a change from a flip. §5.135 §6 records the correction; §5.131 §4's numbers stand as written.

Why it is not urgent: the cell is CSS-tier, the pixels are outside every declared shape, and no
adopted bound or floor reads a digest. Why it is not nothing: a byte-identity check is a real
instrument on this bed — it is how W27f G2 certified that the sampled path had not moved — and a
capture that flips makes that check report a change where there is none. The shape of the work is
to find the source (a compositing or rasterisation race in the CSS tier's proxy on this one
geometry is the obvious candidate, and the cell is a toolbar group, the one component with several
members) and to decide whether the settle protocol needs another frame for it. Until then, treat a
digest change on this one cell as unproven until it is repeated.

A general lesson, worth more than the cell: **an instrument stop written as "any capture is
byte-repeatable" will eventually be tripped by something the claim it guards does not depend on.**
W27f G2's declaration did exactly that and had to resolve it against contract X1 at landing time.
Scope an instrument stop to the arms the bound is stated on.

## The matrix schema has no per-surface metric, so a stack's overlay cannot carry a floor (W27f G2, 2026-09-11)

`results/matrix.json` states every perceptual, shape and material row over a cell's whole declared
footprint. For `{checkerboard,photo}__glass-over-glass__*` that footprint is the union of the base
and the overlay (`placeComponent` returns both), so there is no way to express a bound on the
overlay alone — and the overlay is the only part of those cells that is a `css-backdrop` group,
which is what makes them the native evidence for the page-content path (claims §5.129 X8).

The consequence is concrete. W27f G2 adopted a bound on that overlay (claims §5.135) and could not
express it as a `GateRow`: it is seven assertions over a committed reading instead, which catches the
ledger and the evidence drifting apart but not a material change, because nothing regenerates that
reading in CI. Claims §5.131 §6 forbids the obvious shortcut — a whole-footprint floor on these
cells would let the overlay's residual disappear behind the base's larger footprint, which is the
specific error that section warns about.

The shape of the work: carry per-surface readings into the matrix for cells whose declaration has
more than one plane, so a stack cell's overlay has adopted rows like any other cell. The reader
already exists and is not the hard part — `read_region` in `2026-09-10-w27f-g0-read.py` takes a
surface selection and the W27f runners call it per surface. The decisions are schema ones: whether
a per-surface axis is a new axis or a nesting of the existing ones, how the cell count assertions
in `adopted-thresholds.test.ts` change, and whether the coherence axis follows. Worth taking with
the next wave that touches stacked material; not worth a wave of its own.

## Nothing checks the canonical matrix against a fresh capture (W27f G2, 2026-09-11)

W27f G2 found the canonical `results/matrix.json` carrying **pre-W27f-G1 rows for the two
`glass-over-glass` scenes through the whole 0.16.0 release** (claims §5.135 §8). The rows were
captured 2026-09-10T05:22–05:23Z, before G1 merged, so the committed bed described the flat-white
overlay the wave had replaced. Twelve rows across 1x/2x and both tiers were affected. They are
corrected; no bound, floor, cell count or partition moved.

The miss is instructive and the shape of it will recur. G1 made two correct statements — the
`gpu-texture` material path is byte-identical, and the DOM material changed — and the stack cells
fall between them: they are **texture-tier cells whose overlay is a DOM-sourced group**, so a change
to the DOM material reaches a canonical cell that every "the sampled path did not move" check
correctly reports as unmoved. Nothing caught it for a day, because **no test compares the canonical
matrix against a fresh capture of the same configuration.** The adopted gate reads the committed
numbers and asks whether they are inside their bounds; it cannot ask whether they are current.

Shape of the work, cheapest first: (1) a landing checklist item — when a change alters what any
group draws, name the canonical cells it reaches and re-capture them, and remember that a stacked
cell's overlay is DOM on every route; (2) a staleness signal — record in each cell the runtime
fingerprint that drew it (the material-source digest the W27f runners already compute) and fail
when a cell's fingerprint is older than the head's, which turns this from a thing someone must
remember into a thing the bed reports; (3) a periodic re-capture of the frozen bed, which is
expensive and catches it only late. (2) is the one worth designing.

## The composite-probe drivers write over their own committed evidence (W27e G1, 2026-09-12)

Both W27e browser probes — `results/2026-09-11-w27e-g0-vibrancy/composite-probe/run.mjs` and
`results/2026-09-12-w27e-g1/operator-probe/run.mjs` — set `const outDir = HERE` and write
`results.json` plus every PNG beside themselves with a plain `writeFile`. So **a bare re-run of
either script silently overwrites the committed reading it is sitting in**, with no flag, no
prompt and no create-only guard.

That is the opposite of the convention the rest of this harness follows. `scripts/vibrancy.ts`
writes its tables with `flag: "wx"` and takes a scratch directory through `W27E_OUT` precisely so
that re-running a reading cannot replace a recorded one; the calibration CLI has `--out-matrix` and
`VITREA_WEB_CAPTURES` for the same reason. The probes have neither. Nothing has been lost — the
G1 run was a first write into a new directory, and a re-run's diff would show in `git status` — but
the failure mode is a worker who re-runs a probe to look at one number and commits a whole
re-recorded evidence directory without noticing, on a machine whose adapter or engine version is
not the one the claim was written against.

Shape of the fix, and it is small: give both drivers the two things the reader already has — an
`--out` (or an env var, matching `W27E_OUT`'s spelling) defaulting to a scratch path rather than to
`HERE`, and a create-only write for `results.json` so replacing a recorded reading has to be
deliberate. The PNGs can stay overwriting inside whatever directory is chosen. Worth taking with
the next gate that touches either probe; not worth a commit of its own.

## The tint-and-ink band costs the playground's frame loop a noisy few milliseconds a frame (W27e G2, measured 2026-09-12)

Measured on `/playground/?renderer=css` at rest, headless Chromium, 150 `requestAnimationFrame`
intervals per run, three runs a side. **Before the band:** means 12.0 / 13.6 / 16.6 ms, p50s
10.4 / 14.0 / 17.9 ms. **With it:** means 12.8 / 20.1 / 20.9 ms, p50s 11.0 / 20.6 / 20.8 ms. Long
intervals reach ~27 ms before and ~35 ms after.

The first run on each side is nearly identical, and the spread within a side is as large as the
difference between the sides, so what the six readings support is a few milliseconds a frame with
a wide harness-produced variance rather than a clean step. *This entry first quoted the middle run
per side — "p50 14 → 21 ms, mean 13.6–16.6 → 20.1–20.9" — which is the flattering summary of the
same measurements and is superseded by the six above.* The direction is consistent across the
three pairs: the band adds four sampling groups — four more masked `backdrop-filter` proxies for a
software rasteriser to paint — and six surfaces to a scene that had five groups.

Nothing about the product is implicated: no site composes four groups into 26 rem, the harness is
not a performance target, and the GPU tier draws the same band on one canvas. What it did do is
push `morph.spec.ts`'s reversal case past a per-frame bound that assumed adjacent samples are
adjacent frames — the long intervals do that whatever the average is — fixed by weighing each step
against the interval it happened over. It is recorded because the next surface added to the
playground pays the same cost and the next flaky timing case will have the same cause.

Shape of the work if it ever matters: measure where the time goes — per-host measure-and-write
against proxy rasterisation — before trimming anything. Trimming the band itself is the wrong first
move: its four groups are the minimum the composition needs (a tinted group and the group a second
seed must step out into, once per ground), so a cheaper band is a weaker demonstration.

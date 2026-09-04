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

## The untinted material's ink is still decided by the colour scheme

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

## The CSS tier's captures move by a code between runs on two 2x cells (W15 G2, W16 G2, 2026-09-04)

*Found at W15's landing (one cell), confirmed at W16's.* Re-capturing the CSS tier from an
identical build reproduces every row to the fifth decimal and every capture byte-for-byte except
a few 2x cells over a flat or photo backdrop, which differ by 1–2 codes with alpha untouched:
`light-solid__rrect-md__rest` at W15 (2 codes, 9 853 px); `light-solid__capsule-button__rest`
(473 px) and `photo__capsule-button__rest-tint-blue` (1 203 px) at W16, 1 code each, with no
row moving past 0.000008. The GPU tier reproduces 115 / 115 every time. The tier's capture is a
Playwright element screenshot of a page whose `backdrop-filter` layers the compositor rasterises
on its own cadence, so the shot lands on one of two frames that differ by rounding — the
harness's, not the tier's. Shape of the work: settle the page (two animation frames after the
last style write) before the screenshot in `cli/compare.ts`'s CSS path, then confirm on a
from-empty rebuild. Below any bound and any floor's epsilon; recorded so the next byte-identity
scan does not chase it.

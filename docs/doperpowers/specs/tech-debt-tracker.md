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

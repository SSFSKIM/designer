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

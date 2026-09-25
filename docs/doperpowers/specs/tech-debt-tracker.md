# Tech debt tracker

Small, real defects that were found while doing something else and deliberately
not fixed there: too minor to justify widening a change's blast radius, but not
so minor that the next person should have to rediscover them. One entry each —
what is wrong, how it shows up, and the shape of the fix, so picking one up is
an implementation job rather than an investigation.

Entries are removed when they are fixed, not struck through: the commit is the
record.

**Reconciled with what this file actually does, 2026-09-21** (W31 G4 review
closure; claims §5.165 §9, finding N12). Both practices are in here — about twenty
entries are CLOSED IN PLACE, some struck through in their heading, rather than
removed — so the rule above described one of two. It is kept as the default and
the second is now stated rather than left to be inferred:

- **Removed when the commit is the whole record.** The entry said what was wrong,
  a commit fixed exactly that, and nothing a later reader needs survives the fix.
  This is most entries and stays the default: a tracker of closed items is a
  tracker nobody reads to the bottom.
- **Closed in place when the CLOSURE's own reading is worth keeping beside the
  finding.** The fix measured something, or took a different shape from the one
  the entry proposed, or closed one half and left the other, or reversed the
  entry's premise. Then the pair — what was believed and what was found — is the
  record, and splitting it across a commit message and a deleted entry loses it.
  Mark the heading CLOSED with the date and the gate, keep the original text
  unedited, and put the closure under it.

When in doubt, close in place: a reader can skip a closed entry and cannot
recover a deleted one without knowing it existed.

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

*W28 G3, 2026-09-15 (claims §5.147):* the single full three-engine run reproduces
`presence.spec.ts`'s nominal 220 ms budget case on Firefox: **433.6 ms** elapsed against
**354.2 ms** allowed after that run's longest-frame allowance. This is the existing class
below, not an activation-state failure. It is retained in
`results/2026-09-15-w28-g3-runtime/react.txt` and **not rerun to green**; the separate activation
assertion-carrier correction is tested only in its own file.

*W28 G4, 2026-09-15 (claims §5.148): the heading's "on Firefox" is now too narrow.* Three full
three-engine runs at three heads on the same day read **red, green, red** on the same timing cases,
and the third one is not only Gecko. G4's c9d chain at `1400f604` passed the suite outright — 174
passed, 3 skipped, 0 failed — and the review fix wave's run at `20d3f3e0` failed three:
`presence.spec.ts`'s elapsed window on **chromium** at 558.7 ms against 389.7 allowed and on firefox
at 418.64 against 387.36, plus one `morph-materialize.spec.ts` release-timing case on **chromium**.
None was rerun and all three are in code those gates did not touch. What the three readings together
say is that this is one elapsed-window class rather than a Gecko-specific one, and that a green run
is evidence of nothing: the entry stays open on the strength of the reds. The shape of the fix is
unchanged and is below — assert the trajectory in the page rather than a driver's reading of a
moment — and it now has a second engine's evidence that the driver round trip, not the engine, is
what the budget is measuring.

*2026-09-16:* 0.18.0 was published with this class as disclosed above — the acceptance is the
user's, recorded in W28 §Status — and nothing was rerun. The entry stays open.

*2026-09-20 (the parent, at the 0.19.0 head `eac168bb`):* the third full three-engine run of the
day read one red, `press.spec.ts` "re-pressing mid-release continues the same trajectory" on
**chromium** — frame 1 stepped 0.097 against a 0.061 travel and a 0.046 budget — after two green
runs of the same suite at the G4 merge (`cb7c8ae5`, 174 passed) and at G4's own version head (174
passed). Not rerun. The log is committed as `results/2026-09-20-w29-g4-landing/chain-parent-final-tree.txt`.
The class is the driver's reading of a moment; a step larger than the whole travel is a sample
taken across a frame boundary. The 0.19.0 publish accepts it as disclosed, as 0.17.0 and 0.18.0 did.

*2026-09-20 (the parent):* 0.19.0 was published by the user on `26250e97` (registry 04:40Z) with
this class as disclosed above and nothing rerun; tag `v0.19.0`. The entry stays open.

*2026-09-20 (W30 G4, the 0.20.0 landing; claims §5.160):* the gate's single full three-engine run
read **two red, 172 passed, 3 skipped** — `presence.spec.ts`'s elapsed window on **chromium** at
**485.0 ms against 406.7** allowed after that run's longest-frame allowance, and
`morph-materialize.spec.ts`'s "the end that is absent is inert, and is released when it has gone"
on **firefox**, where the destination end was still in the document 5 s after `Escape`. Neither was
rerun and the log is committed as
`packages/calibration/results/2026-09-20-w30-g4-landing/chain-react-e2e.txt`. Both are this class
and neither is in code the wave touched: the gate's own React change is `GlassRootHandle`'s
material document and the toolbar's gap, which no presence or morph case reads. Worth adding to the
record for its cross-product: the release-timing case has now fired on chromium (W28 G4) and on
firefox (here), and the elapsed window on firefox (W28 G3) and on chromium (W28 G4, here) — so
**both cases have now failed on both engines**, which retires the last reading of this as an
engine's property rather than the driver round trip's. The 0.20.0 cut is prepared with it disclosed,
as 0.17.0, 0.18.0 and 0.19.0 were.

*2026-09-20 (the parent, the final chain at the 0.20.0 head `ec9e136f`):* the three-engine run read
**two red** again — `presence.spec.ts` "authored presence is monotone in place" on **chromium**
(elapsed 528.2 ms against 425.1 allowed) and `morph.spec.ts` "a reversal mid-flight redirects
instead of restarting" on **firefox** (frame 6 of 50 stepped 31.4 ms against a 29.3 budget) — a
third distinct case of the class, the second on chromium in one day. Not rerun. The log is
`results/2026-09-20-w30-g4-landing/chain-parent-final-react-e2e.txt` beside G4's. The entry stays
open; the 0.20.0 cut carries it disclosed.

*2026-09-21 (the parent, the 0.20.0 publish):* 0.20.0 published by the user on `484ec8a4` with
the two reds above disclosed, the fourth cut in a row carrying this class. The entry stays open.

*2026-09-21 (the parent, the final chain at the 0.21.0 head `05d2d5a7`):* the three-engine run read
**two red** — `presence.spec.ts` "authored presence is monotone in place" on **chromium** (elapsed
533.1 ms against 420.1 allowed) and `morph-materialize.spec.ts` "the end that is absent is inert, and
is released when it has gone" on **firefox** (`toHaveCount` on the release) — the same two cases as
W30's G4 run; W31 G4's own run of the suite at `3e3c906c`, minutes of docs earlier, read 174 / 3 / 0.
Two runs of one head, one green and one red on the same two cases, is the class's own signature.
Not rerun. Log `results/2026-09-21-w31-g4-landing/chain-parent-final-react-e2e.txt`. The entry stays
open; the 0.21.0 cut carries it disclosed.

*2026-09-21 (the parent, the 0.21.0 publish):* 0.21.0 published by the user on `c87b5493` with
the two reds above disclosed, the fifth cut in a row carrying this class. The entry stays open.

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

*Measured either side of W27e G2's tint-and-ink band, 2026-09-12, three consecutive full
three-engine runs of each tree on one machine:* **`bdac5222` failed 0, 0, 0** (135 passed, 35.3–37.4
s) and **the band's head failed 0, 2, 1** (155–156 passed, 41.5–42.1 s). The failures are this
entry's class and nothing else — `morph-materialize.spec.ts`'s tab-order and focus cases and
`presence.spec.ts`'s 220 ms budget, all on `firefox`, all assertions of a driver at a moment; the
presence one missed by 45 ms against an allowance built from its own longest frame. So the band did
not introduce a mechanism, it widened the window of one that was already here: it costs the
playground's frame loop a few milliseconds a frame (its own entry below), and every case in this
class is written against a page that keeps up. A clean baseline today is also a reminder of what
the 2026-08-30 readings say — the rate drifts by session, so 0/0/0 against 0/2/1 is a signal about
this machine this afternoon rather than a coefficient. **The fix shape below is unchanged and is
now the thing worth doing**: bracketing these assertions rather than sampling them fixes the class
for whatever is added to the playground next, and W27e G2 did exactly that for the one case that
had crossed onto Chromium (`morph.spec.ts`'s reversal, which weighs each step against the interval
it happened over) and deliberately left the other three to this entry rather than spreading one
child's repair across another's tests.

*Seen on Chromium once, 2026-09-12 (W27e G2's review repair), which the readings above say does
not happen:* `morph-materialize.spec.ts`'s "returns focus to the trigger when the menu is
dismissed" failed with "focus never entered the open platter" in a full three-engine run, then
passed 3 of 3 in isolation and in the next full run of the same tree. One sighting is not a
distribution, and the case is a focus assertion rather than a driver sample, so it may be a
different mechanism with the same cause — the engines contending — but "Chromium passes every
time" is no longer something to triage against.

**The fix shape:** make the assertions bracket the driver's trajectory rather
than sample it — poll for the channel to cross a threshold, the way the
accessibility specs already `expect.poll` — and then put the suite in CI, because
a flake visible only locally will keep being triaged as "probably pre-existing"
by everyone who meets it.

*Disclosed at the 0.17.0 cut (2026-09-14): 4 of 162 on the recomposition head, the same
press / morph-materialize / presence timing-and-focus class, none in the wave's new cases; not
rerun for a green record. The user's publish accepted the class as disclosed (W27 wave spec,
Outcomes clause 5). The fix shape above is unchanged and still owed.*

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

*Built, and gated to one pose (2026-09-15, claims §5.145 and §5.148).* W28 G1 built exactly the fix
this entry names — `backdropToneAbscissa: { kind: "silhouette" }`, a per-surface encoded-space mean
under the host's own region, carried through the response, the collapse compensation, the nominal
composition and the opacity solve on the WebGPU tier and through `sampleBackdropTone`'s rect on the
CSS tier — and it passes 335 / 335 unpressed canonical cells per tier against G0's independently
computed silhouette means. **It is off everywhere the active material draws.** Only the two receded
documents opt in; absent or `"source"` is today's arithmetic bit for bit, because W28 held the
active material byte-identical by contract (X11) rather than reopening eighteen waves of active
fits inside a wave about the recede. So this entry is no longer "no mechanism exists"; it is "the
mechanism exists and the active pose has not been refitted under it". G0 recorded what the abscissa
would do to the active pose and W28 acted on none of it. Two things the switch-over needs that this
wave did not produce: G0's verdict was **not identifiable from this bed**, so the kind and scale
that win for the active pose are not known either, and the CSS tier carries a per-surface mean
where the GPU carries a per-pixel field, whose Jensen difference has its own entry below.

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

**CLOSED 2026-09-20 by W29 G4** (claims §5.155 §6), in the shape this entry names and at the moment
it predicted. `test.slow()` at the top of `apps/demo/e2e/contrast.spec.ts` gives every case in the
file three times the default, and nothing else moves: no sample, no floor and no assertion. What
tipped it over was the material — the macOS 27 document blurs the CSS tier at 2.2 times the sigma
the macOS 26.5 one did, which is more work per frame at each of the ground sweep's twenty stops, and
"the plates' labels hold the large-text floor at every ground level" timed out **serially on an idle
machine** where this entry had it at 24.1 s of 30. It is worth recording that the failure arrived as
a timeout rather than as a contrast miss: the floors all held, and a budget written against one
material is not a property of the page.

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

**Recomposition repair 2026-09-14 (`9650921`):** the same band now also passes the ownership half
of W27a/W27e's `foreground` prop in live code: one operable checkbox moves both bookmarks between
`"vibrant"` and `"token"`, the runtime marker follows and the returned app-owned ink is visibly
stronger. A three-engine browser assertion pins the instance. The generic README-to-live-instance
inventory in (2) remains open; this closes the concrete omission the audit found, not that broader
lint.

## Core's advisory sampling padding is still σ = 8's 24 px and wins the toolbar gap on the regular variant (W27b, measured 2026-09-11)

A toolbar partition clears `max(DEFAULT_GROUP_SAMPLING.samplingPadding, samplingPaddingFor(members))`:
core's advisory constant, which its proxy-overlap check is written against, and the material's own
requirement derived in `platform-web/src/optics.ts`. The advisory is 24 (3σ at σ = 8, the blur
when S1 wrote the padding rule); at the shipped profile the material asks 11.1 for an empty row,
11.3–12.7 for a button, a capsule and a 420 × 52 bar, 14.9 for a 420 × 72 bar, and 35.5 on the
clear variant. So on regular the advisory dominates by about 2× and the spacer is wider than the
material needs (never narrower; the 0.16.0 eye sheet read 24 px on the demo), and on clear the
material dominates and the max does real work.

**Amended 2026-09-20 (W29 G4, claims §5.155): the advisory stopped dominating on the regular
variant, and it is now the case that can be too NARROW.** The macOS 27 document carries
`cssTierMapping.blurSigmaScale` 2.2 against the module default of 1 — the CSS tier's whole share of
the 27 diffusion refit — and the proxy's σ, its 3σ floor and this derivation all read that same
number, so the material's requirement multiplies by 2.2 while the constant does not. A group that
takes core's advisory 24 now sits under a floor of roughly 24–28 on regular and is raised with a
`sampling-padding-below-3-sigma` finding, where before 0.19.0 it sat comfortably over it. Nothing
is wrong — the floor is enforced where it matters and the raise is reported rather than silent —
but the constant has crossed from "wider than needed" to "a warning an upgrading app will see", and
the fix shape below is unchanged and now has a second reason. Retiring the constant means core's overlap check
taking the padding as an input from the platform that resolved it — core is pure and cannot import
the derivation — with `DEFAULT_GROUP_SAMPLING` kept only as the value a host without a resolved
policy is checked against. A W27b-scale change; not chartered.

**W30's numbers, added 2026-09-20 (claims §5.160; contract X8 leaves the
retirement undecided, so this entry stays open).** The operator wave graded the
outer shadow's σ by the casting span, which moves two pads in opposite
directions and leaves the one this entry is about exactly where it was.

- **The backdrop sampling pad — this entry's own quantity — did not move at
  all**, and that is a reading rather than an omission (§5.159 §5). It is 3σ of
  the BACKDROP blur and the σ law reaches the shadow, not the body. So the
  advisory's relationship to it is unchanged: 24 against the material's 11.10 on
  the macOS 26.5 endpoints and 22.69 on the macOS 27 light one at span 0, and
  23.66 / 27.35 on a 420 × 52 bar in the two schemes — still a warning an
  upgrading app will see on a taller bar, still never an under-pad.
- **The outer shadow's REACH did move, both ways, and by a lot.** On the light
  document it goes 20.90 → **13.39** CSS px at span 32 (−35.9 %) and 31.88 →
  **42.93** at span 160 (+34.7 %), and it keeps growing above the bed: a 220 px
  caster pads **57.40** against the old 31.88 (+80.1 %). The dark document reads
  **12.76** at span 32 and **61.50** at span 220 (`reach-pad.txt`, the corrected
  figures of §5.159b §10 finding 3). So the constant that used to be one number
  at every span is now a line with a four-fold range across the bed, which is the
  shape a retired advisory would have to be replaced by rather than a number.
- **What that says about the fix shape.** Core's overlap check takes a scalar
  because the padding was a scalar. It no longer is on the shadow's side, and the
  platform already resolves both pads per group — so "core takes the padding as
  an input from the platform that resolved it" is now the only shape that can
  state either of them, and the two-number answer is a second reason for it
  beyond the one this entry opened with.

**W32's numbers, added 2026-09-21 (claims §5.168; contract X8 again leaves the
advisory constant where it is, so this entry stays open).** The shadow wave fits
the exterior's OUTSET and stands the receded material's amplitude down, and both
move the reach the platform resolves.

- **The advisory's own quantity is again unmoved.** `samplingPaddingFor` is 3σ of
  the BACKDROP blur and this wave touches no backdrop constant, so 24 against the
  material's 22.69 at span 0 on the macOS 27 light document is exactly where W30
  left it.
- **The active reach SHRINKS at every span, by the outset.** Light
  13.39 → **9.08** CSS px at span 32, 13.41 → **9.23** at 44, 23.74 → **20.20**
  at 96, 32.89 → **30.18** at 128 and 42.93 → **40.70** at 160; dark 12.76 →
  **9.90**, 12.83 → **10.22**, 24.54 → **22.06**, 34.60 → **32.49** and 45.69 →
  **43.04** (`results/2026-09-21-w32-g1-shadow-fit/reach.txt`, the runtime's own
  `outerShadowReachPx`). The CSS tier's group clip follows: light 15.30 →
  **12.70** at the thin end and 45.79 → **43.19** at span 160.
- **And the RECEDED reach is 0 at every span, on both documents.** It was the
  ACTIVE reach at every span — 13.39 to 42.93 on the light document — because
  both receded documents carried their active document's anchors leaf for leaf.
  W32 Decision Log 2 sets their amplitude to 0 on the measurement that Apple's
  receded window removes no light from 3 CSS px outward, and
  `outerShadowReachPx` returns 0 when `outerShadowAlpha(occlusion)` is 0, so the
  group clip in the inactive pose collapses to the surface itself. **A pad that
  is a function of the POSE as well as the span is a third reason for the fix
  shape**, and the first one that can make a pad go to zero rather than merely
  vary: an overlap check written against a scalar cannot express "this group needs
  no pad while its window is unfocused".

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

## Nothing checks the canonical matrix against a fresh capture (W27f G2, 2026-09-11) — NARROWED 2026-09-21 (W32 G0b): shape (2) is half-built

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


**Shape (2), the staleness signal, is half-built and the built half is the cheap
one.** A capture already records the runtime fingerprint that drew it — the
material profile documents and their twelve-hex hashes, in its own `capturePath` —
and `scripts/check-capture-tree.ts` now fails when a capture's fingerprint is not
the one the row beside it names (claims §5.167 §3). That turns a stale GENERATION
from a thing someone must remember into a thing the tree reports, at every merge,
with no browser.

It does not answer this entry's original question. A cell whose overlay is a
DOM-sourced group still moves when the DOM material moves, and if that change
moved no profile document the fingerprint does not move either. The W27f defect
would still be invisible. What answers it is the same `compare --skip-capture`
re-derivation the `web-captures/` entry now names: the committed number
re-computed from the committed pixels. Shapes (1) and (3) are untouched.

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

## The capture's idle gate is enforced once per run and only recorded per cell (26.5 sitting, 2026-09-12)

`--min-idle-seconds 45` refuses a run at its opening; after that each entry carries
`hidIdleSeconds` and nothing refuses, so a touch mid-run files the cell with its idle beside it. The
runbook said "a disturbed run retries rather than filing a disturbed cell", which is true only
before the first cell (corrected in the runbook; claims §5.136 §10). On the sitting this filed cells
at 0.08 s of idle in inactive 2x run 4 and at 0.1 s in the increased-contrast run 1, every one with
its pose attestation intact — the recede is held by construction and the cursor is excluded from
the capture, so the byte-state is probably unaffected, but "probably" is what the seven-run
plurality at `materialize` time exists to test, and `sitting.md` lists the cells so it can. The shape
of the fix, for the next bed: sample idle per cell against the same threshold and retry the cell
(not the run) when it is under, recording the retry; or lower the per-cell bar deliberately and say
why. Either is a harness change and a run declaration, not a change to this bed's evidence.

## Apple's own glass adaptation is not reproducible cell-for-cell across runs (W27e G2, 2026-09-13)

*Found while reading the 1x both-pose corpus; claims §5.138 §7, evidence
`packages/calibration/results/2026-09-13-w27e-probe-1x-reading/`.*

Three of the corpus's 50 scene-and-scheme cells carry a different `vibrantColorMatrix` in different
runs of the same bed, and the difference is not a filter detail: the whole body moves with it —
`inputFaceColorMatrixFillColor` flips white to black, both face points move and
`inputShadowColorMatrixFillColor` goes `nil`. All three sit at the two backgrounds whose adaptation
is marginal, `dark-solid` in light and `light-solid` in dark.

It is not a pose effect. Two of the three put two arms of the **same** pose on opposite sides:
`light dark-solid__rrect-48__rest-label` reads the default operator in the `active` arm and the
high-gain one in `policy-only`, both key, and `dark light-solid__capsule-button__rest` reads
high-gain in `policy-only` alone. The third, `light dark-solid__capsule-button__rest`, is one of the
two cells claims §5.133 §4 named as switching at 1x in the key pose — and here the two key arms read
it as not switching. §5.133 §4's reading stands as recorded; §5.138 §7 is the second reading beside
it.

What it costs: any selector law for the surface operator, and any threshold fitted for the body's
adaptation, is bounded from above by this. A law fitted on the key pose alone would be fitted on a
cell two arms disagree about, and a bound stated tighter than one cell in 25 could not be met by a
second run of the same bed.

Shape of the work: a settle study, which `dump-layers` can run in minutes and which no capture has
needed before, because until now the body's adapted state was only ever read off pixels that had
already settled. One scene — `dark-solid__capsule-button__rest` in light — dumped n times at
`--settle` 8 and n times at a longer settle, reading `inputFaceColorMatrixFillColor` rather than a
pixel, and the same for `light-solid` in dark. If the longer settle is unanimous the 8 s figure is
too short for the adaptation and every dump-derived reading inherits that; if both settles are split
the decision is bistable near its threshold and a selector law has to say so.

## The wave's Tracking Map drops W27f's status cell when rendered (found 2026-09-13)

*Found while validating the tables W27e G2 edited; the row itself predates this branch
(`ec809ae6`) and belongs to W27f G2's landing.*

`docs/doperpowers/specs/2026-09-10-w27-coverage-wave.md`'s Tracking Map is a three-column table —
`| child | where | status |` — and every row carries four pipes except `| W27f |`, which carries
five. A renderer drops cells past the header's count, so W27f's actual status cell ("G2 CLOSED and
LANDED; bound adopted; **S4 scoped to the WebGPU arms and the eye taken, both user rulings of
2026-09-12**; canonical stack rows corrected") is **invisible in the rendered document**, and what
shows in the status column is the tail of the previous cell. Every other child's status renders.

Not fixed here: it is another gate's record and the repair is a judgement about which of the two
cells was meant to be the status, which the child that wrote it can make in one edit. The check that
would have caught it is the one that found it — a pipe-count-per-table pass over the spec, worth a
line in whatever lints these documents if anything ever does.

*The plurality has now been asked, and the bed is inconclusive (W27c G2 read, 2026-09-13; claims
§5.139 §2).* The pooled comparison is the tempting one and it is confounded: of the 50 cells the
sitting lists as low-idle, 43 are unanimous across all seven runs (86.0%) against 117 of the other
138 (84.8%) — but **three of the six passes contain no low-idle cell at all** and only pad the
comparison arm. Restricted to the three passes that have them the comparison reverses, 86.0% against
**87.9%**, and inside `inactive-1x` alone it reverses hard: **84.6% (22 of 26) against 98.0% (49 of
50)**. At the capture level the 56 low-idle captures are 4.26% of all 1,316 and **2 of the 39
minority captures** (5.1%), which is the base rate — except that both of the two are in
`inactive-1x`, where they are 2 of that pass's 5 minority captures against its own 5.83% base rate.
Five events decide nothing in either direction.

What the bed does establish is that the plurality absorbed whatever the disturbance was: every
minority capture lost, no cell was refused, none was state-ambiguous, and the only LOW-IDLE cell
below five of seven (`checkerboard__rrect-ml__inactive` under increased contrast, disturbed in runs 1
and 6) was voted 4/3 inside one 8-bit code. The bed's other 4/3 cell was captured at full idle. So the entry stays open and the fix's shape is unchanged —
and there is a second lesson in it for the next bed: **a low-idle group that is concentrated in some
passes cannot be compared to a pooled remainder**, and the design that would answer the question is
the per-cell retry, which produces the comparison within a pass rather than across passes.

## The inactive endpoint's dark thin response at a bright backdrop is wrong by 0.78 Y (W27c G2 read, 2026-09-13)

*Measured on the checking bed, claims §5.139 §6; supplying cells, not scored ones, and nothing was
fitted to them.*

`light-solid__capsule-button__inactive` in the dark scheme reads web **0.15637** against native
**0.93261** linear Y on the eroded body — body ΔE **0.43838** — and its `rrect-sm` sibling at span 32
reads 0.16225 against the same 0.93261, body ΔE **0.43179**. They are the two largest readings
anywhere on the bed. Apple's recede over a bright solid at a thin span in dark is *invisible* — the
interior is the backdrop's own level — and vitrea paints a dark panel over it. At thick span the same backdrop reads
0.09339 / 0.11753, so it is the **thin** row alone, and it is exactly the ordinate §5.130's table
flagged: dark `backdropToneResponseThin` is `[0.011, 0.089, 0.1611]` and its far entry is recorded
there as "an extrapolation of this selected family, not a measured bright-background level". The bed
measures it and the extrapolation is off by about a factor of six.

Shape of the fix: it is a **fit**, not a repair — the field expresses the value, the evidence simply
did not exist when it was set, and it does now. It belongs to whatever gate next opens the inactive
endpoint, together with §5.139 §5 (a)'s two fresh middle ordinates, because both move the same
`backdropToneResponseThin`/`Thick` pair and a fit that moved one knot without the other would
propagate through the interpolation's slopes. Nothing may be fitted at the probe bar in a way that
adopts a floor (W27 Decision Log 13).

*W27c G1c tried it and the cells REFUSED it (2026-09-13, claims §5.141 §3). The entry stays open and
its shape has changed.* On the GPU the measured ordinate does close its own cell —
`light-solid__rrect-sm__inactive` from body ΔE 0.43179 to **0.00406** — and takes
`checkerboard__capsule-button__inactive` from 0.00653 to **0.19450**, 29.8× its baseline, with
`photo__capsule-button__inactive` at 21.1×; every intermediate rung is refused on the same control
(9.40× at 0.30, 17.75× at 0.50, 23.93× at 0.70). It is not the frozen middle knot's fault either: the
CPU mirror's counterfactual, with residual (a)'s measured 0.04092 released, still puts `hc-text` at
0.61229 against a native 0.08985.

So this is **not a fit waiting for a gate**; it is a fit waiting for a CELL. The reference's dark thin
row is flat and low from encoded 0.1104 to 0.7400 and then steps by 0.84, and the two readings that
bracket the step differ in two ways at once — the abscissa, and whether the backdrop is uniform. The
bed's four uniform backdrops sit at 0.1104, 0.2554, 0.2706 and 0.9504, so the widest uniform gap is
**0.6798, 68% of the axis**, and its brightest structured backdrop is 0.7652
(`identifiability.json`). What closes it, in order: **one uniform neutral patch between the middle
anchor and the far one** — same argument, same shape, as `mid-dark-solid` in W7 and `mid-chroma-solid`
in W27c G1b, and one cell answers it; then, *if* the answer is the abscissa, a **fourth knot** in
`backdropToneAnchorX` and its two ordinate arrays, which is a `MaterialProfile` type change and not a
profile-document fit; and if the answer is the structure, the response law's structure-independence
premise (W9, validated on the LIGHT ACTIVE material) does not hold for the recede, which is a larger
finding than this entry. The same three-knot ceiling is what fails the two light standard profiles'
clause 3 on `hc-text__rrect-sm__inactive`, where the far anchor IS measured and the curve
over-predicts at encoded 0.74 instead of under-predicting at 0.95 — one cause, two schemes, opposite
symptoms.

*One more ordinate of the same document, measured by the same bed and out of W27c G1c's scope:* the
dark **thick** row's far entry. `light-solid__rrect-lg__inactive` and `light-solid__rrect-ml__inactive`
read web **0.09339** against native **0.11753** — §5.130 recorded that ordinate as an extrapolation
too, and the bed measures it at 0.024 Y away rather than at the thin row's 0.78. W27 Decision Log 17
scoped this child to the thin row alone, so it was not swept. It is small, it is on the same
`backdropToneResponseThick` array the thin row's neighbours sit on, and whatever gate opens the
response next should move it in the same pass rather than in a third.

*The bright-end gap is CLOSED by W27c G1d (2026-09-14, claims §5.143), and the residual it reveals
stays here rather than being hidden by closing the heading.* The new uniform 140/255 anchor reads
0.12214 Y at encoded 0.5490 and agrees with the structured checker at the same abscissa, so the
answer is **abscissa**, not structure. A fourth knot at x 0.70 with the measured 0.9326072 thin far
and 0.11753 thick far ordinates closes the light-solid rrect-sm body error 0.43179 → **0.00406** and
the thick error 0.03626 → **0.00161**, while its worst declared control is 5.68×, below the 9× cap.
The remaining term is the middle response: the new anchor's held-out capsule is still **0.03937**
body DeltaE at both scales (WebGPU/native Y 0.09531/0.12214), and the selected response makes the
checker capsule visibly darker than native. The two light-standard profiles also retain their
opposite `hc-text__rrect-sm__inactive` over-prediction and fail clause 3 at 2.44× / 2.15×. Closing
that shared middle/bright structure without reopening the dark controls is the next response work;
the bright dark endpoint and dark thick ordinate themselves no longer are.

*The clause-3 failure above is superseded, and the residual it was evidence for is not
(2026-09-15, claims §5.146; kept as written per this file's rule).* W28's footprint abscissa moved
`hc-text__rrect-sm__inactive` from 2.44× / 2.15× of its per-cell floor to **0.9269× / 0.8023× of
its ceiling** — under it by 7 % and 20 % — and the unchanged bound now holds on all six profiles,
which is what lifted W27c's hold. The paragraph's sentence about failing clause 3 therefore
describes the G1d head and not any head since. What did not move is the reason this entry exists:
that cell is still the worst light checking cell and still reads **visibly too bright** on the
sheet at WebGPU/native body Y 0.6791 / 0.5485 (1x) and 0.6907 / 0.5690 (2x), and the dark
low-contrast checker capsule is still both dark profiles' clause-3 worst at 0.05936 / 0.05994. A
bound holding is not pixel identity, and the shared middle/bright structure named above is still
the work.

## The window-activation runtime is held behind the inactive response (W27 recomposition, 2026-09-14)

**2026-09-15 — ~~The window-activation runtime is held behind the inactive response~~ CLOSED
by W28 G3, claims §5.147 (`2026-09-14-w28-footprint-response.md`).** The admitted endpoints now
follow document focus by default, with explicit root/React pins, a resolved readout and an
operable playground. G4 still owns runtime-pose capture publication, the demo/native eye and
the coverage re-score; the activation transit's native timing remains unmeasured.

**2026-09-15 — the three items handed to G4 are closed too (claims §5.148).** Runtime-pose capture
publication: the calibration page poses its root and hands it the capture's scheme, and 470
inactive rows are in the canonical matrix as the scene's declared `state`, captured that way and
proved byte-identical to G2's own captures — 354 / 354 inactive, 60 / 60 active — before a row was
written. No floor is adopted and none may be; the gated bed excludes the pose by axis, and
`PREDICATE_EXCLUDES` is byte-identical. The demo/native eye: three sheets and `eye.md`, the
playground's pin at 2× in both schemes beside the harness capture, and a **real** focus change read
without a driver — `hasFocus` false, root `inactive`, `visibilityState` still `"visible"`. The
coverage re-score: §3.6's window-focus row moves to `replicated+measured` in the coverage matrix's
2026-09-15 re-score. The transit's native timing is still unmeasured and now has its own entry
below, so it does not disappear with this heading.

W27 Decision Log 20 closes the coverage wave without W27c G2 or G3. The endpoint documents, the
four-knot response and the per-policy accessibility lift ship inert; there is no
`windowActivation` root option or `<GlassRoot>` prop, no activation observer or
`setWindowActivation`, no inactive scene rows or floors, and no operable demo pose. This is a held
runtime, not a replicated matrix row.

What closes the hold is the response work claims §5.143 and the entry above identify: fit the shared
middle/bright response across uniform and structured backdrops without reopening the dark controls,
then separate the cap/refraction and one-pixel contour terms visible on the sheets. Re-apply the
unchanged §5.134 §6 bound on a sealed configuration and require all six profiles to hold. Only then
land G2's framework-agnostic root option, explicit setter and React prop through
`applyMaterialProfile`; G3 adds inactive `state` rows, any evidence-supported floors, the demo's
backgrounded-window pose and the user's eye. Decision Logs 17 and 20 explicitly reject shipping the
hook on the four profiles that hold today.

*Taken up by W28 (2026-09-14, `2026-09-14-w28-footprint-response.md`): the response work is read
as W9's deferred per-footprint abscissa first (§5.31, §5.34 residual class 1), a structure term
second and only on evidence; G2 and G3 above are W28's G3 and G4 behind the unchanged bound holding
on six profiles. ~~This entry closes when W28's G4 lands.~~ The runtime hold closes at G3 above;
G4 retains the landing work.*

G0's medium review (claims §5.144, 2026-09-14) leaves bounded evidence/documentation debt:
W9's original background-directory bytes lack a committed hash attestation, and the matched-mean
pairs supply essentially no contrast axis (maximum body-contrast-SD difference **0.000024540389**;
the read's looser descriptive cutoff remains 0.05). Preserve the old evidence; a future identifying
sitting must carry its background hashes and an encoded-region-mean-matched contrast pair, and its
report should state the exact observed contrast range. No defect changes G0's not-identifiable
verdict; choosing that sitting or stopping is W28 Decision Log 2's task, not a G0 refit.

## The inactive material under the accessibility policies follows its backdrop where Apple's does not (W27c G2 read, 2026-09-13)

*Measured on the checking bed, claims §5.139 §6. This one is scored: it is both accessibility
profiles' clause-3 exceedance and most of their clause-2 failure, at 20.80× and 15.83× the
threshold.*

Over `dark-solid` under Increase Contrast the reference is an opaque near-white panel at every span
the bed carries — 0.99445 at span 48, 0.9937 at 80, 0.9935 at 96 — while vitrea follows the backdrop
down at the thin end: **0.58408** at span 48, recovering to 0.9560 only by span 80. Under Reduce
Transparency it is 0.53328 against 0.95597. §5.130 fitted `increasedOcclusionLift` (0.92) and
`reducedTintAdaptation` on 1x light accessibility bodies only, and recorded that "their different
native levels are not fully expressible by this shared policy fold". The fold misses by **0.41 Y**,
and it misses in the direction that defeats the setting: an accessibility material that reveals its
backdrop is the opposite of what Increase Contrast and Reduce Transparency are for.

Shape of the fix: read the accessibility fold's own span law off the bed rather than inheriting the
standard profile's thin/thick knee — the bed now has three spans over the same backdrop in both
accessibility profiles, which is what the fit never had. Note the confound to avoid: macOS
force-couples Reduce Transparency on with Increase Contrast, so the increased-contrast rows are
*both* settings and the reduced-transparency rows are one (the harness records the coupling as a
profile caveat). Dark accessibility and 2x accessibility still have no inactive evidence at all.

*The backdrop coupling is CLOSED by W27c G1c (2026-09-13, claims §5.141 §4), and what is left behind
is a different entry, written here rather than opened as a third.* The bed says the reference is not
a span law at all: under Reduce Transparency **twelve of fourteen** cells read **0.95597** linear Y
to five decimals over `dark-solid`, `checkerboard`, `photo`, `hc-text` and `light-solid` at spans 32
through 160. The exceptions are `light-solid__rrect-ml__inactive` at **0.95660** and
`photo__rrect-md__inactive` at **0.95411**, the latter with native SD **0.002962**; native SD is
exactly zero on **eight of fourteen** and below 1e-5 on thirteen. The complete 0.002497-Y range still
identifies an occlusion floor per policy, on two existing fields of the light entry:
`refractionScale.approximate` 0.45 → **0**, the single factor `backdropToneUnderPolicy` rides and
therefore what kept 45% of the backdrop adaptation
alive under a preference that asked for the opposite, and `increasedOcclusionLift` 0.92 → **0.96**.
`dark-solid__rrect-48__inactive` goes from body ΔE 0.16224 to 0.00410 under Increase Contrast and
0.17417 to 0.00894 under Reduce Transparency; the increased-contrast profile crosses the declared
bound from FAILS to HOLDS and both per-cell exceedances are gone.

**Named residual in that form:** neither side is perfectly flat. Apple's two exceptions above span
0.002497 Y, with the photo cell carrying the one material native variance; vitrea's fitted panel has
exactly zero web SD on only **eight of fourteen** cells and reaches **0.004904** on
`hc-text-28__rrect-md__inactive`. That web structure is visible in
`sheets/apple-macos-26.5-1x-light-reduced-transparency.png`. The opaque-panel form remains the right
one at this scale, but a future fidelity pass must explain and fit the residual structure rather than
reading “opaque” as perfectly uniform.

**What remains, and it is a model-form gap and not a tuning residual: the two accessibility policies
settle at different levels and one shared fold cannot hold both.** The reference is 0.95597 under
Reduce Transparency and 0.99110–0.99445 on eleven of fourteen Increase Contrast cells, **0.0375 Y
apart**; its three lower cells are `hc-text__rrect-lg__inactive` at 0.98731,
`hc-text-28__rrect-md__inactive` at 0.97792 and `light-solid__rrect-ml__inactive` at 0.95895.
`increasedOcclusionLift` is one number for both because macOS force-couples the two settings and
`occlusion: "increased"` comes from the Reduce Transparency row alone
(`core/src/accessibility.ts`). At 0.92 the Reduce Transparency reference is reproduced exactly
(body ΔE 0.00000) and Increase Contrast reads 0.01304; at 1.00 the order reverses. That is what leaves
`apple-macos-26.5-1x-light-reduced-transparency` failing clause 2 at 1.04× on a uniform
0.026–0.044 Y overshoot spread across all twelve cells rather than concentrated in one. Shape of the
fix: a per-policy level on the occlusion fold — either a second constant that Increase Contrast
selects, or the existing `ambientTint: "reduced"` axis given a level term, which is the one axis the
two policies already differ on. It needs no new capture: the bed measures both levels.

Two smaller things G1c left beside it. **The accessibility cap conflates three axes** — zeroing
`refractionScale.approximate` stands down the tone adaptation, the size occlusion grading and the
refraction together, and a flat zero-variance panel gives no evidence to separate them, so the recede
cannot currently say "no adaptation but some refraction". **And the contour is now the visible
residual under Increase Contrast**: with the bodies matched, the 8× difference strips show a
one-pixel ring on every cell, which is `strongBorderRim`, fitted in §5.130 on the 1x
increased-contrast outline and untouched since. Dark accessibility and 2x accessibility still have no
inactive evidence at all.

*The per-policy level gap is CLOSED by W27c G1d (2026-09-14, claims §5.143); the smaller residuals
above remain open.* `increasedOcclusionLiftByPolicy` uses the existing ambient-tint distinction and
falls back to the shared 0.96 for every document that does not name it. Fitted on the two banked
supplying cells per policy, Reduce Transparency selects **0.88** (mean body DeltaE 0.00522) and
Increase Contrast **0.98** (0.00112). Both profiles now hold all three clauses of the unchanged
bound: 0.00600 against the 0.011 Reduce Transparency body threshold and 0.00278 against 0.0078
under Increase Contrast, with no per-cell exceedance. The sheets keep the work this did not close
visible: a near-complete one-pixel contour under Increase Contrast, and under Reduce Transparency a
level that is still darker than native on dark-solid and brighter on light-solid. The cap still
conflates adaptation, size grading and refraction; dark accessibility and 2x accessibility remain
unmeasured.

## The active material passes about half the chroma Apple's does over a saturated backdrop, and one probe cell sits above the active bed's own ceiling (W27c G2 read, 2026-09-13)

*Measured on the four active `mid-chroma-solid` cells the checking bed added, claims §5.139 §7. They
are `probe` cells: no adopted bound, no floor and no `PREDICATE_EXCLUDES` entry moves, and none is
proposed.*

Over a uniform patch at `photo`'s luminance and OKLab chroma **0.3089**, Apple's active material
passes interior chroma **0.159–0.170** — 52–55% of the backdrop's — and vitrea's passes
**0.077–0.083**, 25–27%. So vitrea transmits about **half of what the reference transmits**, a
quarter of the backdrop's own, and sits 0.17–0.22 Y too bright besides:
`mid-chroma-solid__capsule-button__rest` 0.67344 / 0.45199 Y and 0.08323 / 0.15937 chroma,
`rrect-md__rest` and `rrect-lg__rest` the same shape. The tinted cell is the good one (body ΔE
0.0388) because the author's own hue supplies what the body fails to transmit.

Two consequences. First, residuals (c) and (e) of claims §5.134 — the inactive material's chroma
transfer — are **inherited from the active material**, so a fit confined to the inactive difference
document cannot close them; the missing degree of freedom (a neutral-density absorber with separate
level and chroma coefficients, named and unfitted in `classification.json`) belongs to the shared
model. Second, `mid-chroma-solid__rrect-lg__rest` reads full-canvas ΔE **0.08645** where the active
material is held to 0.07 on that profile. Every backdrop in the gated bed is either neutral or
`photo`, where chroma, level and structure co-vary, so no gated cell could have shown this.

Shape of the work: it is a material change on the WebGPU tier and therefore a wave, not a fix —
whoever charters it needs the freeze bar on this background before any of it can carry a floor, and
should read §5.139 §7's inactive/active chroma ratios (1.034 at the capsule, 1.058 at `rrect-lg`)
first, because the recede transmits slightly *more* chroma than the active pose and a change that
closed the active gap without that term would open an inactive one.

## `GlassSurface`'s `foreground` prop now carries two axes and they are mutually exclusive (W27e G2, 2026-09-13)

The prop was `ForegroundAdaptation` — the *cadence* the foreground decision is fed at, `fixed`,
`author-hint` or `sampled-async`. W27e G2 added `"vibrant"` and `"token"`, which say who owns the
label's `color` declaration, and the W27 §Design clause that spells the opt-in `foreground="vibrant"`
is binding, so the two live in one prop. A union of an object and two strings is discriminable, so
nothing is ambiguous — but a surface that needs `sampled-async` adaptation *and* the vibrant
precedence cannot say so, and neither can one that needs `author-hint` and `"token"`.

It bites hardest on the controls, which now default to `"vibrant"`: an author who passes
`foreground={{ mode: "sampled-async" }}` to a `GlassButton` silently drops the label back to the
token path. Nothing is wrong with either result; the author simply cannot have both.

Shape of the fix, and it is additive so it can wait: give the object form an optional field —
`{ mode: "sampled-async", vibrant: true }` — and keep the two strings as shorthands for
`{ vibrant: true }` and `{ vibrant: false }` over the default cadence. That is a `@vitreajs/vitrea`
minor (the type is core's) plus a react minor, and it breaks nothing already written. Do it the next
time either axis is touched, not on its own.

## The two tiers pick opposite ink poles on the clear variant over a narrow backdrop window (W27e G2, measured 2026-09-13)

The CSS tier's foreground level runs brighter than the renderer's for the same material over the
same backdrop — up to **0.0502** on the regular variant and **0.0824** on the clear one — because the
two composite the same profile in two different spaces. On the regular material that is never enough
to reach `foregroundCrossover`. On the **clear** variant it is: over backdrop luminances in
**(0.0656, 0.1020)** the CSS tier reads above the crossover and the renderer reads below it, so a
demotion from the WebGPU tier to the CSS one flips the label from white to black on the same surface
over the same page.

Found while pinning the ink across the tiers (claims §5.140 §2) and it predates W27e: nothing in the
ink's derivation moved the levels, and the same window existed with `#1c1c1e`/`#f5f5f7`. It is not
the operator's, which is why it is here and not chartered — X1 makes a CSS-tier fidelity difference a
recorded residual rather than work. It is now bracketed to a thousandth of the backdrop's luminance
in `packages/calibration/test/tier-coherence.test.ts`, so a material change has to move it
deliberately.

Shape of the work if it ever matters: it is the tiers' composite gap and not the ink's rule, so
closing it means narrowing `cssTierForegroundLevel` against `gpuTierForegroundLevel` — a material
question on the fidelity target's terms and therefore a wave, not a fix. A cheaper mitigation that
is *not* recommended without measuring first: hysteresis on the pole per surface would hide the flip
at a tier switch and would also hide a genuine adaptation, which is the one thing the ink must
follow.

## The band's secondary ink reads 4.463 against a token that promises 4.5, and did before the operator (W27e G2, measured 2026-09-13)

`--vitrea-foreground-secondary` is solved to hold WCAG 4.5 against the composite the runtime
computes for the surface (Decision Log 9). The demo's contrast harness reads the same level on the
ink band's light ground at **4.463** on the CSS tier after W27e G2 and **4.481** before it, so the
operator moved it by 0.018 and the shortfall predates the gate (claims §5.140 §9). The two figures
are not the same measurement: the token is solved against the runtime's computed composite, the
harness composites the recovered ink over the plate's *median rendered pixel*. Which of the three
candidates named in `apps/demo/e2e/ink-band-contrast.spec.ts` accounts for the 0.037 — the median of
a plate that contains its own specimens, the tint's chroma against a solve taken on the computed
composite, or a declared backdrop that is not exactly what is behind the plate — is not measured.

Until it is, `ink-band-contrast.spec.ts` holds the reading at a **pixel** floor of 4.45, named as a
pixel floor and not as the token's promise, so a change that pushes it further under fails the suite
while this known gap does not.

Shape of the work: W27e G3 runs the contrast harness on every glass label in the demo and is the
place to separate the cause — read the token's own solve inputs beside the harness's surface pixel
for the same element, and attribute the difference to one of the three candidates. If it is the
plate's median, the harness's surface should be the pixel under the glyphs and the floor returns to
4.5; if it is the solve's composite, the floor stays and the token's solve is the thing to move.

## A fit's selection objective can be a different population from the bound that scores it (W27c G1c, 2026-09-13)

*Found by this gate in its own method, not in the material. Real, small, and worth one line in
whatever writes the next fit's declaration.*

W27c G1c's sweep rule, declared before the fit, selected on the equal-cell mean body ΔE over a term's
**six** calibration and control cells. The bound that scores the result reads the profile's **twelve**
checking cells. On T2's second stage the two disagreed: `increasedOcclusionLift` 0.96 beat 0.92 by
0.00700 against 0.00721 — a 3% margin on six cells — while 0.92 is the value that reproduces the
Reduce Transparency reference exactly (body ΔE 0.00000 on its calibration cell), and it is the
reduced-transparency profile that then fails clause 2 at 1.04% over. Whether 0.92 would have carried
that profile's twelve-cell mean is **not measured**: the bound is applied once, to the configuration
the declared rule selected, and scoring a second configuration would be shopping for one
(claims §5.141 §10).

Nothing here was done wrong — the rule was declared before the numbers and applied as written, which
is the discipline working. The lesson is about writing the rule: a fit whose objective population is
not the scoring population can select against the gate it is trying to pass, and the cheap fix is to
say so in the declaration — either weight the objective by the scored population, or state why the
smaller population is the right one. Not worth re-opening this fit for: the outcome of the ruling is
the same either way, because the light standard pair fails on a different, refused term and G2 stays
blocked regardless.

**Resolution appended by W27e G3 (2026-09-13; claims §5.142 §3).** It is the **solve's
composite**, not the plate median and not a false backdrop hint. On the CSS light plate the median
rendered pixel and the independently exposed pixel under the secondary glyph are both
`[163, 192, 235]`; hiding the complete glass overlay exposes `[231, 231, 231]`, exactly the byte the
page paints and the hint decodes. The token instead solves against the ideal tinted composite
`[164.241, 192.852, 236.202]`, **+1.241 / +0.852 / +1.202 code values** from the pixels the selected
CSS drawing form renders. The exact token alpha 0.589676 reads **4.500132** on that solve input and
**4.482090** on the rendered pixel, so the physical shortfall is 0.018042. The canvas method's
8-bit black/white recovery resolves the alpha to 0.588235 and reads **4.462809**; its quantum is the
remaining 0.019281 of the originally reported 0.037323. The 4.45 CSS pixel floor therefore stays.

G3 also made the GPU reading explicit instead of leaving it inside G2's JSON: the two plate grounds
read **4.308564 / 4.278166** on the WebGPU tier, already present at those values in G2's
`readings-after.json`, and are held at a separately named **4.25 WebGPU pixel floor**. Neither pixel
floor is Decision Log 9's token promise. Closing this entry means solving each tier's secondary
against the composite its selected drawing form actually publishes — the CSS transfer/overlay form
rather than `cssTierForegroundColour(optics, hint)`, and the renderer output rather than
`gpuTierForegroundColour(material, hint)` — then retiring both pixel floors by fix. This is a
material/composite change and remains deferred; the landing gate records and guards it rather than
retuning the material without a wave.

## W27a, W27b and W27d have no from-empty rest rebuild at their landing heads (W27 recomposition, 2026-09-14)

Parent clause 3 requires two independent proofs that each non-optical child left the resting bed
byte-identical: the renderer isolation spec and a from-empty calibration rebuild. The golden PNGs and
`packages/calibration/` are unchanged across all three child ranges; W27a records 33/33 goldens,
W27d records 34/34 plus 21/21 GPU e2e, and W27b's unchanged composition is argued from the source.
But none of the three landing records contains a from-empty rebuild. The isolation spec itself was
last changed before the W27 charter and still pins `W26_HASHES`; the last from-empty canonical build
is W26 G3 at `2a235f36`. The recomposition therefore marks this half of clause 3 NOT MET rather than
promoting an unchanged git diff into capture evidence.

What closes it is a historical reconstruction, not a canonical rewrite: check out each landed head
(`bc14af9`, `38d782c`, `108b40d`) in isolation on the capture machine, rebuild the declared resting
calibration population into an empty scratch capture root, and compare every digest with the common
W26 baseline. Never write `results/matrix.json`, a profile document or a golden. A current-head
rebuild can show the final composition rests identically, but cannot by itself prove each
intermediate landing did.

## W28's interaction predictors still use unpressed geometry (2026-09-14, §5.145)

G0's predictor masks use the declared component, including the 24 canonical interaction cells.
The web path actually compresses their hosts: the photo capsule reads 118.20001220703125 ×
43.339996337890625 at (100.89999389648438, 78.33000183105469), rather than the declared
120 × 44 at (100, 78). G1 therefore records those cells' geometry and abscissa differences but
excludes them from its raw-input pass condition, by the parent's clarification. The evidence is
`results/2026-09-14-w28-g1-silhouette/mechanism-table.json`. Closing this gap requires predictors
built from the interaction's actual geometry and a state-attested native interaction bed, not a
response fit against an unpressed mask or the recovered pressed/rest duplicate fixtures.

## The source-profile CSS harness retains its historical content-box sizing (2026-09-14, §5.145)

The calibration page specifies a capsule as 120 × 44, but the CSS tier's 1px transparent border
makes its content-box host measure 122 × 46. G1 makes the silhouette-profile harness border-box
before registration so its input can be checked against native geometry; source-profile captures
are deliberately unchanged, proved by eight before/after capture pairs in
`results/2026-09-14-w28-g1-silhouette/source-harness-isolation.json`. A separate CSS measurement
correction should declare border-box geometry for the source-profile bed and rescore that bed in
scratch. The runtime must not silently change an application's box sizing to repair a harness.

## Silhouette locality beyond the native-size inactive bed remains unmeasured (2026-09-14, §5.145)

The new GPU reduction reads imported mip zero. The canonical input check has no downscaled source,
but a resolution cap can already have linearly filtered that mip; its encoded mean then need not
be the raw raster's mean. Original and sampled dimensions are exposed in the readout. G1's
input-only diagnostic measures mip-zero versus analysis-level shifts up to 0.13629209995269775
encoded on non-D shapes. Exact high-resolution locality needs a raw-source reduction or an
encoded-space statistic that preserves the region mean through downscaling, with its cost measured.

The CPU outer-shadow thin regime also still uses a group/source reference. Every receded shadow
amplitude is zero, so this is inert for W28; active adoption must move that reference too. G1's
queue-completion timing measures warmed, static canonical-sized scenes, not first-reduction cost,
4K scenes or live-source adaptation fidelity. Those limits are future work, not general performance
or active-material fidelity claims.

## The activation transit's timing and curve are unmeasured against any native sequence (2026-09-15, §5.147, §5.148)

*Named at W28 G3 and carried out of that gate's closed heading so it does not disappear with it.*
The pose is two frozen endpoints and the transit between them is inherited: the CSS tier keeps its
existing armed property transitions at **240 ms** under nominal motion and **120 ms** under Reduced
Motion with the existing easing, and the GPU tier takes the selected endpoint's uniforms on its next
frame with no interpolation of its own. Those numbers are implementation choices from the motion
kernel, not readings — the native bed holds endpoint stills and nothing else, so no duration, no
curve and no per-channel ordering has ever been compared against macOS receding a window. W28 G4's
sheets are settled endpoints for the same reason. This sits under the same blocker as identity and
`materialize`: there is no native frame sequence for any transition in this project. Shape of the
work: the motion-metrics harness the parent's Decision Log 23 (c) charters — a native capture path
that records a sequence rather than a still — and then this transit read against it, which is when
240 / 120 stop being authored numbers.

## No engine will report a real unfocused document to a test driver (2026-09-15, §5.147, §5.148)

*Found twice, from both sides.* W28 G3 opened a second page and called `bringToFront()`: the
original document went on answering `document.hasFocus() === true` on Chromium, Firefox **and**
WebKit, so the three-engine activation tests drive a synthetic `hasFocus` feed and say so. W28 G4
then made another **application** frontmost through LaunchServices with the page under Playwright,
and got the same answer — still focused, still `active`. The mechanism is the driver, not the
engines: Playwright turns Chromium's focus emulation on for every page it owns so a suite does not
break when the developer clicks away, and a page held focused by the protocol cannot report losing
it. G4's reading had to launch the binary itself and speak CDP over a bare socket to get the true
answer (`hasFocus` false, root `inactive`, `visibilityState` still `"visible"`). The cost is that
**every automated activation test in the repository is a synthetic feed**, on all three engines, and
the one real reading is a manual-class script on one machine and one engine. Shape of the work: if
Playwright ever exposes focus emulation as an option, the three-engine specs can drive the real
path on Chromium at least; failing that, a small CDP-only case in the platform suite, run headed,
would keep one non-synthetic reading in the chain rather than in a wave's evidence directory.

## The CSS tier's inactive abscissa is a per-surface mean where the GPU's is a per-pixel field, and the Jensen term is unmeasured (2026-09-15, §5.146, §5.148)

*Named by W28's contract X1 and left unmeasured by G2 and G4.* Under `backdropToneAbscissa`
`silhouette` the WebGPU tier keeps a per-pixel local reference and the CSS tier can carry one number
per surface — one `rgba()` layer cannot hold a field — so over a backdrop that is not uniform under
the body the two differ by a Jensen term. Nothing has measured that term **in isolation**. What
exists instead is an equal-cell mean absolute body-Y gap between the tiers: 0.0014–0.0095 over
§5.146's 182 common cells and 0.00077–0.0048 over §5.148's 235 published inactive dom rows, both of
which sum the Jensen difference together with every other cross-tier difference the two layers
already had. The widest single cell in both readings is `mid-chroma-solid__rrect-lg__inactive`
(0.0412), which is dominated by the chroma-transfer entry elsewhere in this file rather than by
locality. Shape of the work: evaluate the WebGPU tier's own per-pixel abscissa field and its
per-surface mean over the same footprints on the committed rasters, off-line, and report the
composite difference the two inputs produce through the same solve — a reading that needs no
capture and no native fixture, and would let the coherence pins compare like with like.

## The dark low-contrast checker capsule is the worst inactive checking cell and has no entry of its own (2026-09-15, §5.146, §5.148)

*Found reading §5.146's verdict table and confirmed in §5.148's published rows.*
`checkerboard-lc16__capsule-button__inactive` is clause 3's worst cell on **both** dark profiles —
0.05936 against a 0.068 ceiling at 1x and 0.05994 against 0.082 at 2x — and the eye reads it as a
capsule that is visibly lighter on WebGPU than native while transmitting a **stronger** checker
amplitude. Two errors in one cell, and they point in different directions: a level that is too high
and a structure transfer that is too strong. The light profiles show the same cell with a different
amplitude and level again. It is unentered because every earlier inactive entry was written about
`hc-text` or about the accessibility policies, and this is neither. Shape of the work: it belongs
with the structured-transfer residual below rather than with a level fit — a low-contrast checker at
pitch 16 is the one backdrop on the bed where amplitude and level can be separated, because the
source mean and the silhouette mean nearly coincide there while the contrast does not.

## Structured transfer and the rim/lens band are the inactive material's largest eye residuals and neither is a fitted term (2026-09-15, §5.146, §5.148)

*Read on the G2 sheets at the bound's own verdict, and again on G4's harness band.* On every large
pane over a structured backdrop — `hc-text` at three row heights, the checkers at four pitches, and
`photo` — the body level agrees closely with native while the **difference** is a band following the
whole contour plus a low-frequency pattern across the interior that follows the backdrop's own
structure. G4's sheet shows it on `photo__rrect-md__inactive`, a cell outside the checking set, with
the contour band reading red on one side and blue on the other, which is lens displacement rather
than a level error. No constant in either endpoint expresses either one: the response fits a level
against an abscissa, and W28's abscissa work moved **where** that level is read rather than how much
structure the material passes. A third member of the same family, smaller and on the dark standard
profiles: a **hairline contour** on the bright-solid pane, where no `strongBorderRim` is active and
so the accessibility-contour entry above does not reach it. W9's H4 is the candidate law for the
interior half and W28 G0 found the bed carries no contrast axis at matched abscissa to test it with
(largest body-contrast-SD difference 0.000024540389 over 123 pairs). Shape of the work: the identifying sitting priced in
W28's §Deferred is what would supply that axis; the contour half needs the cap/refraction separation
§5.143 §8 named, which is still unstarted.

## The light dark-solid intermediate-span inactive body is darker and cooler than native (2026-09-15, §5.146)

*Read on the light-standard sheets at both scales.* `dark-solid__rrect-80__inactive` retains a
visible cool, dark body difference where the smaller `dark-solid` controls beside it visually
coincide, and `light-solid__rrect-ml__inactive` is the clause-3 worst cell on both accessibility
profiles at the other end of the same axis. The pattern is a span, not a backdrop: the response's
thin and thick rows are blended by `smoothstep(32, 96, span)` and 80 sits inside that blend, so an
error there is an error in the blend rather than in either row. Nothing has fitted the blend for the
receded endpoint — W28 G1 fitted anchors and ordinates and left the thickness law where the active
material put it. Shape of the work: read the receded interior level against span on the uniform
backdrops, where the abscissa is unambiguous, and see whether the knee wants moving for this pose
before any row is touched.

## The Increase Contrast inactive light-solid pane is whiter than native (2026-09-15, §5.146)

*Read on the increased-contrast sheet.* Beside the one-pixel contour residual that dominates that
profile, `light-solid` at a large span is visibly whiter on WebGPU than the native panel, which reads
greyer. W27c G1d fitted `increasedOcclusionLiftByPolicy` to **0.98** for this policy against body
ΔE, and the cell clears its bound at 0.01388 against 0.0156 — so this is a residual the metric
scores as passing and the eye does not. The bed cannot currently separate it from the contour: both
are read on the same twelve cells, and the contour's own amplitude biases a whole-canvas statistic.
Shape of the work: an interior-only reading of the accessibility cells at large spans, excluding the
contour band, which would say whether 0.98 is a level error or whether the panel's opacity is right
and its border is what differs.

## The inactive bed's dark holdout cannot discriminate the abscissa (2026-09-15, §5.146)

*Named by W28 Decision Log 2 (f) and confirmed by the read.* W28's own design asked for a holdout
cell per scheme whose silhouette mean differs from its source mean by more than 0.05, because a
holdout that cannot tell the two abscissae apart cannot test the mechanism. In **dark** the bed has
no such non-D cell: the largest available displacement is `photo__capsule-button__inactive` at
0.03734 (1x) and 0.03801 (2x). The dark holdouts were admitted anyway, with the limit recorded, and
they passed at 0.026–0.054 body ΔE — which is evidence that the endpoint predicts well, and is not
evidence about locality. The light holdout, at −0.137, is the only strong discriminator the bed has
ever held, and it is spent for this configuration. Shape of the work: the identifying sitting's dark
half — a dark structured cell whose body sits over a region whose mean is far from its source's —
captured on a 26.5 machine while one exists.

## The `clear` variant and the stack regime are not established as inactive evidence classes (2026-09-15, §5.146, §5.148)

*Carried from W27's hand-forward list and unchanged by W28.* The receded documents zero a clear
rim and a clear shadow, and the bed's one `clear` id, `dark-solid__rrect-md-clear20__inactive`,
declares no material variant — so those two constants are identified by nothing and simply ride along
whenever a `clear` surface recedes. The stack regime is worse off: its only inactive ids are spent
holdout, so W27f's arm A4 stays declared and unrun. W28 G4 published 470 inactive rows and neither
gap moved, because publishing a row that exists is not the same as creating the cell that does not.
Shape of the work: both need a scene declaration before they need a capture — a `clear`-variant
inactive id that actually declares the variant, and one non-holdout inactive stack id — and then a
26.5 sitting to capture them.

## The inactive pose and the receded document are not in the cell key (2026-09-15, §5.148)

*Found by the independent review of W28 G4.* The 470 inactive rows published at that gate carry a
`key.web.capturePath` that is byte-identical to their active twin's on the same profile: the active
material profile document's SHA-256 is in it, the receded document's is not, and neither is the
pose. The precedent for what that costs is in `packages/calibration/src/backdrop-probe.ts`'s own
header, about the two axes that used to be in the same position — "Until these travelled in the
report and in the cell's `capturePath`, the only thing separating them was the directory a run
happened to write to — which is not evidence, because the matrix's key does not contain it." The
consequence here is narrower and sharper: a change to `packages/platform-web/src/receded-profile.ts`
silently invalidates all 470 rows without moving one key, where the same change made to a material
profile document would append new rows beside the old ones and leave both readable. Half of the gap
is closed — `capturePoseRefusal` in `packages/calibration/cli/gates.ts` refuses to measure a capture
whose resolved pose or scheme disagrees with the cell being planned, so a mislabelled capture cannot
reach a published row — but a correctly labelled row still cannot be told from a stale one. Shape of
the work: a `backdropProbeLabel`-shaped clause appended to `capturePath`, empty on the active pose so
the shipped bed's keys stay unchanged to the byte, and naming the pose and the resolved receded
document's SHA-256 otherwise. Taking it means re-capturing the 470 inactive rows, because every one
of their keys changes.

## `dump-layers --inactive` cannot name a declared inactive scene (2026-09-18, §5.149)

*Found by W29 G0's SDK comparison.* `main.swift`'s `dump-layers` calls
`refuseScenesUnreachableInPose(ids, in: loadSpec(), pose: .active, …)` **before** it reads
`--inactive` off the arguments, so every id whose declared state is `inactive` is refused whatever
pose the run is about to present in — including the run that exists to present the recede. The W27e
recipe never met it because its probe spec declares only `rest` ids. The consequence is narrow: the
recede is a property of the presentation rather than of the scene (`Capture.presentInactive`'s own
doc comment says so, and `capture --inactive` is built on it), so a `rest` id under `--inactive` is
the same reading, and G0 took it that way. Shape of the work: read `--inactive` first and pass the
pose it names into the refusal, which is a two-line move inside the same `case`. Doing it rebuilds
the harness, so it waits for a build some later wave is taking anyway — X4 says the granted bundle
is not rebuilt for it.

## The manifest's `sdk` field is an environment read, and a pass's own launch leaves it `unknown` (2026-09-18, §5.149)

*Found by W29 G0 (a).* `capture.sh` derives `VITREA_SDK` from the installed SDK and exports it;
`run-sitting.sh` launches the bundle through `open` without it, because `launchctl setenv` does not
reach a GUI launch from a background session. Every manifest G0 wrote therefore reads
`"sdk": "unknown", "xcodeVersion": "unknown"`. The committed 26.5 bundle carries `MacOSX26.5.sdk`,
so the field was populated when that bed was published — and what it records is **the SDK installed
on the machine, not the one the binary links**, which after a toolchain upgrade is a different
thing. X2 asks for the linked SDK read from the binary; that read is `LC_BUILD_VERSION`'s `sdk`, and
on this build path even that is not the SDK the bundle compiled against (§5.149 §1: `swiftc` links
through `clang` with `--sysroot`, so `ld` records `sdk == minos`). Shape of the work: the harness
reads its own `LC_BUILD_VERSION` at startup — its executable is on disk and the load command is four
fields — and records it beside a build-time SDK string the build script stamps in, so the two are
separable rather than conflated. Until then a bed's SDK provenance is a build fact somebody has to
write down by hand.

## The capture harness cannot be narrowed to one profile (2026-09-18, §5.150)

*Found by W29 G1 while building the 27 sitting.* `main.swift` selects which profiles a run captures
from two things and nothing else: the machine's accessibility mode, matched against
`profile.a11y`, and the display's real backing scale, matched against the substring `-<scale>x-` in
the key. `--scenes` narrows *cells*, not profiles. That was invisible while one bed existed, and it
became load-bearing the moment `scenes.json` declared two: a 2x standard pass against the canonical
version-6 declaration selects **four** profiles rather than two — the 26.5 pair and the 27 pair —
and spends twice the priced machine hours writing 27 pixels into `apple-macos-26.5-…` directories
inside the run snapshot, which is twelve extra hours of a sitting and a snapshot that invites exactly
the confusion X1 exists to prevent. The workaround is `results/2026-09-18-w29-g1-bed/pass-spec.py`,
which derives a profile-narrowed specification from the canonical file at every pass's opening and
refuses unless the canonical file still declares what clause 2 names. It works and it is verified per
pass, but it means a sitting reads a document that is not the one in the repository, and every future
bed that lives beside another one will need the same scaffolding. Shape of the work: a `--profile
KEY[,KEY]` option on `capture` that intersects with the a11y-and-scale selection and fails when it
selects nothing, which is the same shape `--scenes` already has and about fifteen lines beside it.
Doing it rebuilds the harness, so it waits for a build a later wave is taking anyway — X4 says the
granted bundle is not rebuilt for it, and any bundle added to Screen Recording under its identifier
evicts its grant.

## The SDK-gating pixel arm is settled in the active pose only (2026-09-18, §5.150)

*Left open by W29 G1 (4).* The pixel arm closed G0's residual decisively — two bundles recording
`LC_BUILD_VERSION` `sdk 26.0` and `sdk 27.0` produce byte-identical captures on 16 of 16 attested
cell pairs at zero run-to-run spread — but only through the **active** presentation. The side
bundle's inactive run failed after one cell and was not retaken while it held the grant, so there is
nothing for a harness inactive half to be compared against; the declared-material arm had the same
limit for a different reason (the granted bundle predates `dump-layers --inactive` and presented
active). Why it is small: SDK gating, if it existed, would be a property of the requesting binary
rather than of the window's activation state — the compositor would have to read a load command that
does not change between poses — and the active arm leaves no difference for a pose-conditional gate
to hide in. Shape of the work: a three-run inactive arm through each bundle at slider 0.5, on the
same four ids. It needs the 27-SDK side bundle's Screen Recording grant back, and granting it evicts
the harness bundle's (W29 Surprises), so it costs two hands on System Settings and should be done
only alongside something else that already needs the side bundle granted.

## `cornerCurvature` reports a number on a contour too short to carry one (2026-09-19, §5.151 §4)

*Found by W29 G2, reading two native beds against each other.* `contourCurvature` refuses a
zero-length contour outright — "a 0.00px contour sampled 512 times at σ=3 carries no curvature" —
which is right, and G2 catches that refusal and records the axis as absent. What it does **not**
refuse is a contour that is merely far too short for its own smoothing scale. On the four
`dark-solid__rrect-64__rest` cells the 26.5 silhouette is a 574-px fragment, and the estimator
returns a characteristic corner curvature of **338.9 /px** — an implied corner radius of 0.003 px,
on a component whose declaration says 64. Two cells further along, `dark-solid__rrect-48__rest` at
2x returns 3.68 /px and `dark-solid__rrect-80__rest` returns 39.4 /px, from 431-px and 331-px
fragments of a shape that encloses ten to sixteen thousand pixels.

The number is not wrong arithmetic; it is the curvature-scale-space estimator applied to a perimeter
shorter than the σ = 3 px Gaussian it is differentiated with, where the smoothed derivatives are
dominated by the fragment's own ends. It is dangerous rather than merely useless because it is a
*plausible-looking* float in a column of plausible-looking floats: a per-component median over those
cells would report that Apple moved a corner from radius 0.003 px to radius 12.95 px, which is the
extractor's story and not the material's. G2 names those cells and reads its corner verdict off the
539 cells whose two silhouettes are within 2x of each other, but the next reader has to know to.

**The fix shape**, in `src/metrics/shape.ts`: refuse in `contourCurvature` when the traced perimeter
is under a few multiples of `smoothingSigmaPx` — the same `CalibrationError("empty-region", …)` the
zero-length case already raises, with the perimeter and the sigma in the message — so a caller gets
an absence with a reason instead of a number. The threshold wants one measurement behind it rather
than a guess: sweep a rasterised circle of known radius down through short perimeters and record
where `cornerCurvaturePerPxA` leaves the ±12 % of `1/r` the doc comment already claims for it. About
twenty lines and one test beside the existing curvature tests, plus a re-read of any committed row
that would newly become absent.

## `compare` picks the web side's accessibility flags off a field that cannot tell macOS 27's two contrast states apart (2026-09-19, §5.152 §B §10)

*Found by W29 G1c, publishing the coupled increased-contrast bed beside the decoupled one.*
`cli/compare.ts`'s `webAccessibilityFlags` maps the **manifest's** `a11yMode` to the flags the web
capture renders with, and in its default `as-captured` mode it renders `increased-contrast` with
**both** `reduced-transparency` and `increased-contrast`. Its doc comment gives the reason and the
reason was true: "macOS force-enables Reduce Transparency when Increase Contrast is on … there is no
single-flag increased-contrast state on that platform to capture."

macOS 27 decoupled them, and the bed now holds both states —
`apple-macos-27.0-1x-light-increased-contrast-glass0.5` captured with contrast alone and
`…-increased-contrast-coupled-glass0.5` with both. **Both record `a11yMode: "increased-contrast"` in
the manifest**, because that field is `SystemAccessibility.current` and it answers only "is contrast
on". So `compare` cannot distinguish them: `as-captured` is correct and now *measured* for the
coupled profile, and **wrong** for the decoupled one, whose like-for-like mode is `contrast-only`.

Nothing committed is affected — no 27 contrast profile has been read against vitrea, and W29
Decision Log 4 (a) declares no table for increased contrast — so this is a trap laid for the next
reader rather than a wrong number on disk.

**The fix shape**: key on the **profile key's** `a11yMode` via `parseProfileKey`, which since W29
G1c distinguishes `increased-contrast` from `increased-contrast-coupled`, rather than on the
manifest field, which cannot; keep the manifest field as the honest record of what the machine
reported. `webAccessibilityFlags` then returns one flag for the decoupled key and two for the
coupled one, `contrast-only` keeps its meaning as the *bound* on vitrea's contrast-only path, and
the doc comment's premise is restated as a 26.5 fact with the 27 split beside it. Perhaps thirty
lines with the switch's `default` refusal unchanged, plus rows in `compare-gates.test.ts` for both
keys. It should land with, or before, the first read of either 27 contrast profile against vitrea.

## The wave's allowance columns were hand-transcribed from the adopted tables, and four rows were wrong (2026-09-19, claims §5.151 §12, §5.152 §B §12)

*Found by the independent review of W29 G1c Part B, and closed there for the two review
closures — this entry is the part that is not closed.*

`test/adopted-thresholds.test.ts` is the source of truth for every adopted bound. W29's native
delta reasons against those bounds constantly (Decision Log 4 (c) is a table of them), and each
place that needed them **copied them in by hand**. Four of the forty-eight texture-tier rows came
out wrong, and they reached a decision the user ruled on: a risk named in Decision Log 5 that did
not exist, a uniqueness claim that was not unique, and a `2x-light-standard` SSIM allowance quoted
0.04 looser than the file's.

The two review closures now import `adopted_allowances.read_allowances()`, which parses the tier
tables and `GATED_PROFILES` out of the test file, so those two cannot drift again. **What is not
fixed is the general case**: the next instrument that wants an adopted bound will find no
TypeScript-side export to read — the tables are `const`s inside a test file, reachable from Python
only by a regex over the source — and will transcribe them like the others did.

**The fix shape**: move the tier tables and their profile mapping into a module the test file
imports (say `src/adopted-tables.ts`, exporting the rows and the `profileKey → tables` map, with
`adopted-thresholds.test.ts` keeping every comment that explains *why* a row holds its value), and
give it a tiny CLI or generated JSON artifact so a Python instrument reads one file instead of
parsing the suite. The test keeps asserting the matrix against the tables, so nothing about the
gate's behaviour changes; what changes is that "the allowance for this profile" becomes something a
tool asks for rather than something a person retypes. Perhaps a hundred lines and a mechanical move,
best done when the next wave needs the numbers outside the suite. Until then, `adopted_allowances.py`
is the one reader, and anything new should import it rather than start a fifth copy.
---

## The runtime ships the macOS 26.5 recede while the macOS 27 endpoints sit in the calibration package

*Found 2026-09-19, during W29 G3's refit (§5.153 §7); the fit landed in G3b
(§5.154) and this is what is left of it.*

**Half of this entry is closed.** The driver it asked for exists —
`compare --receded-profile <file>` through `capture-web` to `web/scene.ts`'s
candidate seam, with the receded document's hash in the cell's `capturePath` — and
the two macOS 27 endpoints are fitted through it, sealed, and read into the
canonical matrix:
`packages/calibration/profiles/apple-macos-27.0-1x-{light,dark}-standard-glass0.5-receded.json`.
The inactive body's level residual went 0.1174 to 0.01017.

**CLOSED 2026-09-20 by W29 G4** (claims §5.155; Decision Logs 2 and 7 (b)), and by the
second of the two shapes this entry named: the receded difference is now a field
on the material profile document itself. `packages/platform-web/src/material-document.ts`
holds one document per measured material with a `receded` endpoint per colour
scheme, `macos27MaterialProfileDocument` is what a root resolves by default, and
`posedProfile()` reads the recede off the same document the active patch came
from — so a material and its recede cannot be selected apart. The macOS 26.5
endpoints stay exported as `recededMaterialProfile` and stay selectable, as
`macos26MaterialProfileDocument`'s receded half. The inactive body's level
residual the fit bought (0.1174 → 0.01017) is what a page now draws.

---

## The outer shadow's blur is span-invariant in the material and is not on macOS 27

*Found 2026-09-19 by W29 G3b's native-against-native read of the shadow axis
(claims §5.154), which closed the previous entry here — the 27 constants are refit
and the seven rows §5.153 §5 named are re-read.*

`MaterialOuterShadow`'s header records, as a positive measurement, that the
reference's three lengths are span-invariant on macOS 26.5: across spans 32, 44, 96
and 160 the fitted σ stays within 15.4–15.9 CSS px. On macOS 27 it is not. The
native falloff σ reads **1.8 CSS px at span 44, 8.8 at 96, 13.1 at 128 and 17.3 at
160**, the same law on the light, dark and reduced-transparency beds and at both
scales, and linear in the casting span to within the reading's own noise
(σ ≈ 0.131 · (span − 26)). The offset grades with it: 4.0 CSS px at span 44 against
8.0 at 128.

**Corrected beside, 2026-09-19 (review closure of W29 G3b; claims §5.154 §4).** The
law is **σ_css ≈ 0.133 · (span − 30), over spans 96–160**, and it is not supported
below that. Least squares over the 1x light cells gives 0.1334 · span − 4.013, zero
at span 30.1; against the published intercept the span-44 cell reads 1.84 where the
law gives 2.36 (−28 %). **Scale invariance also fails at the thin spans**: 1.84 at
1x against 3.92 at 2x, a ratio of 2.13 — the device pixel ratio — where at 96–160
the two scales agree to 1.3–6.8 %. The figures in the table above are single
`checkerboard` cells; the bed-wide median at span 44 is 1.52 at 1x light. "About
six times too wide" below is a **1x** figure — 11.0 against 1.84 is 5.97× and
against the 2x span-44 reading of 3.92 it is 2.80×. Nothing this entry asks for
changes: one `sigmaPx` still cannot be both ends of the thick range, and the
thin-span behaviour is now open structure rather than a fitted law.

`sigmaPx` is one constant and the shader reads it from a uniform, so no value of it
is both 1.8 and 17.4. The 27 documents carry 11.0, which is the best the thick
regime admits and is where every row the refit existed to clear sits; the thin
cells keep a shadow about six times too wide, carrying the right energy in the
wrong shape. The amplitudes fitted beside it absorb the energy error, which is why
the departure residual is 0.0007 and the residual this entry names does not show in
it.

~~**The fix shape**: `cli/native-delta.ts` already is the bed-against-bed instrument
and `cli/measure.ts` already computes the shadow metrics (`meanDeparture`,
`strengthPeak`, `falloffSigma`, the four extents); adding the shadow axis to the
delta's metric vector is a small change to `cli/native-delta-metrics.ts`. Read the
27 bed against the 26.5 bed on that axis, then refit the fifteen `outerShadow`
constants in the 27 documents against it. **No new capture is needed** — both beds
are on disk — which is what makes this the cheapest of the three causes Decision Log
6 puts to the user.~~ **Done by W29 G3b** (claims §5.154), which is what left this
entry holding only the span grading. The fix shape that remains is the paragraph
below.

**The fix shape**: a span grading on the length, profile-gated so the runtime
default and the two 26.5 documents resolve bit-identically. It is smaller than it
sounds — the casting surface's span is already in the shader as `shadowAux.z` and
`outer_shadow_thick` already grades the AMPLITUDE by it, so the change is that
interpolation applied to `ou.shadow.y`, new leaves under `outerShadow`, the CSS
tier's mirror in `platform-web/src/optics.ts`, and `outerShadowReachPx` taking the
maximum over spans for the pad. It is not taken in G3b because Decision Log 6 (a)
ruled the shadow's CONSTANTS refit; it is put to the user as Decision Log 7, which
**ruled it deferred to one operator wave after 0.19.0**, carried there with the
scale-selective scatter under a single one-time X1 exemption — each adds leaves to
the renderer default and so moves every document's fingerprint, the frozen macOS
26.5 pair included, and chartering them apart would spend two exemptions.

*Moved here 2026-09-20 (W29 G4): this paragraph was filed at the foot of the
"A material profile document is two options" entry below, where it described a
fix for a defect that entry does not name. Nothing in it is changed except the
last sentence, which now records Decision Log 7's ruling.*

---

## A material profile document is two options, and no option takes the document

*Found 2026-09-19, by the review closure of W29 G3 (claims §5.153).*

A profile document has two halves that have to travel together: `patch`, the
renderer's material, and `cssTierMapping`, what that same material costs to express
as one `backdrop-filter` plus an overlay. `createGlassRoot` takes them as two
options of the same name, and nothing joins them — so the natural reading, "a
document is a value `materialProfile` accepts", silently gives a page the 27
material on the GPU tier and a CSS tier still blurring at the 26.5 scale
(`blurSigmaScale` 1 against the document's 2.2, which is the constant that carries
that tier's whole share of the 27 diffusion refit). The harness itself passes both
(`packages/calibration/web/scene.ts`), which is why the split has never bitten a
measurement; an app has nothing to copy from.

`@vitreajs/vitrea-react`'s `<GlassRoot>` surfaces neither option, so a React app
cannot select a 27 document at all today. That is a deliberate omission for
`cssTierMapping` — its doc comment calls it calibration's seam rather than an
application knob — and an unstated one for `materialProfile`.

**CLOSED 2026-09-20 by W29 G4** (claims §5.155), in the shape this entry proposed and
one field wider. `createGlassRoot({ materialProfileDocument })` takes a whole
measured material and reads every half off it — the active patch per colour
scheme, the receded difference per colour scheme (the entry above), and the CSS
crossing — and the two older options stay, merging over whatever the document
selected, for an app tuning one tier by hand. `<GlassRoot>` surfaces all three
props; the "deliberately not an application knob" line survives intact for
`cssTierMapping`, which is documented as being there so an app naming a whole
material by hand can name both halves of it. The document's own
`resolvedMaterialSha256` reaches the readouts: `root.material` and every resolved
`GlassGroupState` name the endpoint that drew, its digest, and whether an app
merged a patch over it. Both package READMEs state the one-option instruction.

## The highlight's angular directionality has no web-side reader, so it cannot be fitted

*Named by W29 Decision Log 4 (a) as an unclosed law, left unfitted by G3
(§5.153 §2 item 3) and carried here by Decision Log 6 (e).*

macOS 27 moved the highlight's directionality: §5.151 §7's review closure measured
the dimmest of W24's sixteen angular bins falling 0.0784 → 0.0242 while the
brightest barely moves, and said the fit belongs on the bins rather than on the
ratio the wave first quoted. G3 refit the rim's amplitude and width and left the
angular floor exactly where W24 put it, because **the bins are not a reading
`cli/measure.ts` takes**: W24's angular reader lives in
`cli/native-delta-readers.ts` and reads a pair of NATIVE captures, so there is no
native-against-web number for any bound or fit to move.

**The fix shape**: give the angular read a web side. `angularRead` already takes a
raster and a declared box and has nothing native about it — what is missing is a
call in `cli/measure.ts` that runs it on both captures and a block on the material
axis that records the sixteen bins, the integral and the peak angle per side, with
the same absences the reader already reports for a composite with no declared box.
Then the floor is fittable and a bound on it is statable. Perhaps a hundred lines
and one schema addition, and it is the last of Decision Log 4 (a)'s six laws with
no instrument behind it.

---

## `results/matrix.json` is 52.9 MB, past GitHub's recommended file size

*Found 2026-09-19 when GitHub warned on the W29 G3 merge; carried here by G3b,
which appended a second 27 generation to it.*

The canonical matrix is one committed JSON file holding every cell of every bed,
pretty-printed one field per line so that "this cell moved" is a small diff. It
crossed 50 MB at G3's append and G3b's read adds a generation beside it, because a
profile document change re-keys every row it drew and the rule is that a recorded
number is never rewritten. GitHub warns above 50 MB and refuses above 100; at the
current rate of one OS recapture per wave the file reaches the hard limit in two
or three more.

Nothing is broken and nothing should be deleted — the old generations are the
evidence a claim cites, and the project's rule against rewriting a recorded number
is the reason the file grows at all. **Not acted on here**, because how to split
committed evidence is a decision about what the repository promises and not a
mechanical one.

**Three shapes, for whoever rules it.** *Split by bed*: one file per OS
(`results/matrix-26.5.json`, `matrix-27.0.json`), which halves the working file
today and moves the problem one recapture along; the gate reads a directory
instead of a file and every path that names the matrix changes. *Split by
generation*: the current generation in `results/matrix.json` and superseded ones
under `results/superseded/<document-sha>.json`, which keeps the working file small
forever and makes "which generation is this" a directory rather than a regex over
`capturePath` — the gate's own `atAShippedDocument` becomes a file listing.
*Compress the tail*: keep the newest generation pretty-printed and store the rest
as one `.json.gz`, which is the smallest change and the worst diff. The second is
the parent's recommendation; all three are the user's to rule, and the axis they
differ on is whether a superseded row should still be one `git show` away.

**Left exactly as W29 G3b wrote it, with a recommendation added 2026-09-20 (W29 G4,
claims §5.155).** G4 seconds the *split by generation* option, and for a reason G3b
could not have had: the landing found a second consumer that needs to answer
"which generation is this", and it had to answer by **timestamp**. The demo reads
the matrix at build time and prints one cell's figures beside a live surface; with
two macOS 27 generations in the file, one profile and one tier no longer name one
cell, so `apps/demo/src/site/calibration.ts` now breaks the tie on `capturedAt`
descending. That works and is honest, but it is a heuristic standing where a name
belongs — a generation captured out of order, or a partial re-read, makes it wrong
with nothing to catch it. Under the generation split the same question is a
directory listing and `atAShippedDocument` is a file lookup, which makes the demo's
tie-break a lookup too. The file measures **72.1 MB** at this landing's head
(`stat`, 2026-09-20), which is the number the next reader should check against
GitHub's 100 MB refusal: it is one recapture from it, not two or three.

**EXECUTED 2026-09-20 by W30 G1** (claims §5.157; ruled by the user's delegation as
W30 Decision Log 1 (d), which took the *split by generation* option this entry
recommends). Everything above is left as G3b and G4 wrote it; this is the outcome
recorded beside it.

`results/matrix.json` went from **2,017 rows / 72,102,187 bytes** to **1,562 rows /
55,768,930 bytes** — every macOS 26.5 row unchanged and in its order, and per macOS
27 profile only the rows read at the four shipped documents. W29 G3's superseded
generation moved byte for byte to `results/superseded/fa872c683f3e.json` (343 rows,
12,421,699 B) and `96b36eedf1c4.json` (112 rows, 3,911,642 B), with a README and an
`index.json` lookup beside them. The naming rule the entry left open: a file is
named by the **active** document's twelve-hex hash, and a receded document never
names a file because it is a difference over its own scheme's active document; the
index maps every hash, active and receded, to its file. The split and the check are
scripts under `results/2026-09-20-w30-g1-split/`, and W30 G4 runs the split again
for the generation its own read supersedes (contract X7).

The three consumers the entry worried about: `atAShippedDocument` keeps its
byte-hash check but is now purely the guard that an edited document empties its own
bed, since over the split file it drops nothing; the demo's `capturedAt` tie-break
is **retired**, the heuristic replaced by the name the entry said belonged there;
`vibrancy.ts`'s `matrixSha256` provenance gained a lineage recording the new digest
beside the old. Two unbudgeted readings: the demo's main bundle fell 39,062.53 kB →
30,272.52 kB, because the site imports the matrix at build time; and the file's
growth rate is unchanged, so the *rate* question this entry raises is answered only
in the sense that the working file now sheds a generation each time it gains one.
**What stays open**: nothing here, but the sibling question the entry did not ask —
whether the superseded directory itself should ever be pruned, compressed or moved
out of the repository — is not decided, and the first reader who finds
`results/superseded/` uncomfortably large should raise it rather than delete a file.

**The consumer half closed 2026-09-20 by W30 G3b** (claims §5.159b; W30 Decision
Log 5 (c)). The split kept the working file from growing without bound and left
the demo importing all of it: at 66 MB the page's whole-file JSON import crossed
a hard conversion limit in the test loader's Rust bridge and
`apps/demo/test/calibration.test.ts` stopped LOADING, while `vite build` went on
succeeding because the bundler's loader is not the test runner's. `apps/demo/matrix-reduction.ts`
projects the matrix at build time onto the rows the picker's scenes carry at the
documents on disk and the seven metrics the page prints, and the main chunk goes
**35,782.95 kB → 624.83 kB** (gzip 2,771.25 → 64.21). `test/matrix-reduction.test.ts`
asserts every displayed figure against the whole-file read, in Node, so the page's
figures no longer depend on the file's size at all — which is the part of this
entry's worry that the split alone could not answer. The superseded directory's
own size question stays open and is now **59.9 MB over six files**.

---

## The fit loop's holdout drop lives in one reader, and the other reader has none

*Found 2026-09-19 by the independent review of W29 G3b (claims §5.154 §7).*

X5 says the holdout is read once per frozen configuration and nothing is fitted
after it, so a fit loop must not be able to put a holdout row in front of the
person choosing constants. G3b's shadow half cannot: `shadow-table.py` drops every
row whose set is `holdout` **in the reader** and prints how many it dropped, so a
round whose scene list names a holdout id still yields no holdout number. Its
recede half was read through `results/2026-09-19-w29-g3-refit/fit.py table`, which
has no such filter — it prints every row in the label's scratch matrices — so that
half's guarantee is the operator passing `--set calibration` or an explicit
`--scene` list on every invocation. It held: no holdout number reached a receded
constant. But it held by discipline rather than by construction, and the two
halves of one gate enforced the same contract two different ways.

**The fix shape**: the drop belongs to whatever reads a fit label's matrices, not
to one wave's script. `fit.py`'s `readings()` is the single place both readers get
their rows from; dropping there — with the count printed, as `shadow-table.py`
prints it — makes every present and future table built on that function refuse by
construction, and a `--with-holdout` flag can exist for the canonical read that is
allowed to see them. Until then, a wave that writes a new reader inherits the
weaker guarantee without being told.

---

## The macOS 27 recede's exterior is unfitted above span 96, and its contour draws no hairline

*Found 2026-09-19 by the review closure of W29 G3b, measured off that gate's own
sheets (claims §5.154 §9 (a) and (b)).*

Two residuals of the fitted 27 receded endpoints, both outside the body and
neither caught by the level fit that §5.154 §6 reports.

**The exterior halo at the largest span.** On the `1x-light-standard` inactive
sheets, strip `checkerboard__rrect-lg__inactive`, the far-exterior difference (every
pixel more than 12 CSS px outside the component's box, ×8 amplification) means
**17.42** on the WebGPU tier and **15.89** on the CSS tier, where no active strip on
either 1x light sheet exceeds **5.92**; the 2x light sheets read the same two
populations. The receded documents carry their active document's `outerShadow`
block leaf for leaf, that block's thick anchor above span 128 is derived rather than
fitted, and the cell that shows this is **holdout** — the bed declares no inactive
calibration cell above span 96 at all, which is the same gap §5.154 §9 records for
the receded body's diffusion.

**Halo half CLOSED, corrected beside at W33 G0, 2026-09-22 (§5.170).** The paragraph
above records W29's generation, not today's documents. W32 DL2 stood every receded shadow
amplitude and lift down, and W32 G2's `halo.py`, rerun here on the canonical captures, reads
**0.00 mean / 0.00 max** on both inactive scales and both tiers. No above-span96 shadow fit
remains owed by this half of the entry. The active WebGPU black-floor max137.10 is a different
residual, chartered under W33 A; the contour stroke below remains open.

**The missing contour hairline.** On the same sheets, `light-solid__capsule-button__inactive`:
the native drops one pixel to 186.4 from a backdrop of 242.4 before rising to the
body's 233.4 — a 56-level dark stroke at the contour — and vitrea's WebGPU strip
dips 1.0 while its CSS strip does not dip at all. On `photo__capsule-button__inactive`
the native dips 34.1 below the backdrop and vitrea rises monotonically through the
edge on both tiers. §5.154 §6's "where it is worst it is vitrea drawing MORE rim
than the reference" is true of the rim band the metric reads; at the contour of the
receded pose the sign is the other way and the amplitude is the whole stroke.

**The fix shape**: both want inactive cells above span 96 that are not holdout,
which is a scenes decision before it is a fit — the split is `scenes.json`'s and
moving a cell between sets is evidence-visible. The hairline additionally wants the
receded rim to be a fitted term rather than a subtraction: W27c's endpoint removes
rim, and what the 27 native does at the contour is draw a stroke the recede keeps.

**Widened 2026-09-22 (W32 G2 review closure; claims §5.169 §10, finding B2): the
hairline is on BOTH poses, and it is what the `0-3` band has been reading all
along.** This entry has scoped the missing stroke to the receded pose since it was
written, and W32's records inherited that scope — every W32 site that named the
`0-3` band's residual named it as *vitrea's body over-filling its declared contour
by 3.5–4 CSS px* on the active pose (§5.62, measured at W14 on the macOS 26.5
material through the shape axis) and the hairline on the inactive one. On the
macOS 27 bed that has the sign and the width backwards.
`packages/calibration/results/2026-09-21-w32-g2-landing/contour-stroke.py` reads
the band outward from the declared rect one DEVICE pixel at a time along the four
straight edges, on the `photo` bed at spans 44 and 160, both poses, over all six
macOS 27 profiles — 24 cells:

| offset from the declared rect | what the bytes do |
| --- | --- |
| **1 device px** | native **14 to 30 bytes darker** than the web, on **22 of 24** cells |
| **2 to 6 device px** | the two agree to a fraction of a byte on the four standard beds |
| anywhere in the band | the web is darker than the native on **0 of 24** |

**Corrected beside, W33 G0, 2026-09-22 (claims §5.170):** the existing W32 `contour-stroke.txt` reads native−web **−31.95 to −13.19 bytes** on those22 stroke cells, not14–30. The old range is retained above as the record being corrected. Its two dark active capsule exceptions concern STRAIGHT edges only; G0 reads their corner arcs too and finds a substantial residual there. The widened non-holdout offset2–6 baselines are per cell, not a universal fraction-of-a-byte promise.

At 2x the stroke is still **one DEVICE pixel**, so it is half a CSS pixel and not
three and a half of them, and it is present on the ACTIVE pose and on the two
accessibility beds as well. The two exceptions are the dark standard beds' active
capsule (`photo__capsule-button__rest`), where Apple draws no stroke at all — worth
a look of its own, since it makes the stroke conditional on something. The literal
transect that started this, `photo__rrect-lg__rest` at 1x light, row y=100: the two
captures are equal byte for byte from x=12 to x=18, at x=19 — the last exterior
pixel — the native reads (20, 124, 8) against the web's (54, 196, 25), and x=20 is
the first body pixel. **The fix shape is unchanged in kind and wider in scope**: it
is one rim term on both poses, and §5.62 is not withdrawn — it stands where it was
taken, and a silhouette wave is still free to read it there.

---

## The two tiers miss the backdrop's structure in opposite directions, and the bed only ever showed one of them

*Found 2026-09-19 by the review closure of W29 G3b, measured off that gate's sheets
(claims §5.154 §9 (c)).*

Interior standard deviation of the body, native against vitrea, on
`checkerboard__rrect-md__rest`: on `1x-dark-standard` the native reads **11.14**
against WebGPU **6.16** (0.55×) and CSS **3.62** (0.32×) — both tiers pass too
little of the checker through the body — while on `1x-light-standard` the same cell
reads native **10.22** against WebGPU **18.04** (1.77×) and CSS **10.65** (1.04×),
where WebGPU passes too much. The ledger's standing reading of this residual
(§5.153 §6's scale-selective scatter, and §5.154 §9's second bullet) is the light
bed's WebGPU sign, and the dark bed inverts it.

So the diffusion residual is conditioned on the scheme as well as on the backdrop's
spatial scale, and the CSS tier — whose single `backdrop-filter` cannot express a
two-component kernel at all — is the more attenuated of the two on the dark bed by
a factor of nearly two. Any operator wave that fits a scale-selective scatter on
the light bed alone will land on the wrong side of the dark one.

**The fix shape**: nothing here is fittable until the structure metric is read per
scheme as well as per pitch — `interiorStdDevDelta` is already in the native delta
and in the matrix, so the read is a cut of committed evidence rather than a
capture. Do that cut before the operator is chartered, and carry the CSS tier's own
attenuation into `tier-coherence.test.ts` as a measured residual rather than
discovering it at the fit.

---

## Under Reduced Transparency the GPU tier is under-opaque, and the impulse specular point is WebGPU's alone

*Found 2026-09-19 by the review closure of W29 G3b, measured off that gate's sheets
(claims §5.154 §9 (d)).*

**Reduced Transparency.** On `1x-light-reduced-transparency-glass0.5`, active,
`checkerboard__rrect-md__rest`: the native body is flat opaque white — interior mean
**253.25**, sd **0.43** — where the WebGPU tier reads mean 247.45 at sd **3.49**,
eight times the native's structure, and the checker is plainly visible through a
body the accessibility preference says should hide it. The CSS tier reads sd
**1.03** on the same cell. Both tiers sit 6–7 levels below the native's level, so
the level is a shared residual and the **structure is the GPU tier's own**. The
preference's whole purpose is that a backdrop stops showing through, which makes
this an accessibility miss rather than a fidelity one.

**The impulse specular point.** On `1x-light-standard` inactive,
`impulse__capsule-button__inactive`, the WebGPU difference carries a compact core at
the body's centre — radial mean 58.7 at r 0, 63.7 at r 3, 28.1 by r 8 — and the CSS
difference has no local maximum anywhere in the body (42.7 at the centre falling
monotonically to about 22). The point §5.154 §9 names is therefore a WebGPU
residual and not a material one, which narrows where it can come from: the optics
pass's own lens or highlight term rather than the level or the shadow.

**The fix shape**: the Reduced Transparency half is a policy question with a
measurement attached — `flatOuterShadow` already flattens the shadow under that
preference, and whether the body's opacity should be forced the same way is a
material-policy decision the ledger can put to the user with these two numbers.
The specular point is a renderer question and wants the WGSL passes read at that
cell before anything is changed.

---

## The tone stage's three bodies are not ordered by span at the curve's first anchor (W29 G4, 2026-09-20)

*Found 2026-09-20 by the reading that moved the site's tone cases (claims §5.155);
`results/2026-09-20-w29-g4-landing/tone-probe.json`.*

On the demo's tone stage at its darkest stop — a ground of 0.00212 linear — the
three plates' composite bodies read **0.2285 (40px), 0.2127 (68px), 0.2236
(112px)**. The order is wrong in the middle: the 68px plate is the darkest of the
three where the size law says it should sit between the other two.

The response law itself is ordered correctly there. The macOS 27 light document's
first anchor is at encoded 0.004 with a thin ordinate of 0.214 and a thick one of
0.242, so a thicker surface is brighter, as it is at every other anchor. What the
reading takes is the **CSS tier's composite** — `--vitrea-tint`'s colour and alpha
over the ground — which also carries `sizeOcclusionGain`'s lift and the rim, and
those do not vary monotonically with span at this level. The amplitude is 0.016
against bodies of 0.22, so it is about 7 % and invisible; what makes it worth an
entry is that the sweep's *claim* is an ordering, and an ordering that fails
anywhere is a claim with an exception in it.

Three things it is not: it is not the response law (checked above), it is not the
macOS 26.5 material (which converged at this stop, so the question did not arise),
and it is not the GPU tier (unmeasured here — the reading is CSS-tier, which is
what the page's `?renderer=css` pin selects). The site's e2e case no longer
asserts the ordering at the dark stop and says why, which is what keeps this from
being silent.

**The fix shape**: read the same three spans on both tiers off the calibration bed
rather than off the demo — `interiorLevel` per cell at the darkest `dark-solid`
scenes is already in `results/matrix.json` for every macOS 27 profile — and decide
from that whether the non-monotonicity is the CSS tier's composite alone or the
material's. If it is the tier's, it belongs beside the other cross-tier residuals
in `tier-coherence.test.ts`; if it is the material's, it is a fit question for the
operator wave.

**Sharpened 2026-09-20 by W30 G4's re-range (claims §5.160); still open.** Two
readings, both from `tone-range.ladder.json`, the same instrument over the
re-ranged control.

- **It is a BAND, not an anchor.** The old control had exactly one stop under a
  ground of 0.004 and it was the disordered one; the ladder has seven, and all
  seven are disordered. The order returns at position 7 — a ground of **0.0030** —
  and holds at all 74 stops above it. So "the curve's first anchor" understates
  it: what fails is every ground below about 0.003, and the page's own control
  now shows that rather than hiding it behind a coarse grid.
- **It is one plate's ALPHA, not three plates' composite.** Over the disordered
  band the 40px plate publishes `--vitrea-occlusion` **0.695** against
  0.648–0.656 at every stop above it, while the other two hold their trend. So
  the non-monotonicity is a step in the thin plate's own alpha at the bottom of
  the curve, not a drift in how three alphas compose — which narrows the fix
  shape above to one question about one surface, and makes it checkable without
  the demo at all.

A consequence for anything that walks this control: the 40px plate's composited
body is NOT monotone across the bottom of the range. It reads 0.2285 at the
bottom stop, dips to 0.2171 at 0.0040 and rises from there, so a continuity check
started at the bottom stop fails on this defect rather than on continuity.
`site.spec.ts` starts its sweep above the band and says so.

**Corrected beside, 2026-09-20 (W30 G4 review closure; claims §5.160 §9, finding
9). Still open, and the defect is bigger than the two readings above state.**
Recomputed off the same `tone-range.ladder.json`:

- The alpha is **0.692–0.695** over the band, not a flat 0.695, and
  **0.647–0.667** above it, not 0.648–0.656 — it rises with the ground for the
  whole of the ordered range, with **35 of those 74 stops above 0.656**. So the
  band is a step against a rising trend, which is a cleaner statement of the same
  localisation: one plate, one break, at the bottom of the curve.
- The dip quoted above belongs to the OLD control's coarse grid. On the ladder
  the 40px plate's composited body reaches its minimum over the whole range at
  **0.2057, position 7, a ground of 0.0030** — the first stop on the ordered side
  of the break — and the discontinuity is the **0.2340 → 0.2057** step at the
  alpha break, a drop of **0.0284**.

**The fix shape, restated at that number.** The amplitude to explain is 0.0284
against bodies of about 0.22 — **13 %**, not the 7 % this entry opens with, and
**2.5× the dip it records** — and it is a STEP at one ground rather than a drift
across several. That is what the calibration-bed read should be sized against:
a residual of that size on `interiorLevel` at the darkest `dark-solid` cells is
well inside what the committed rows can resolve, so the question "is this the CSS
tier's composite or the material's" is answerable from rows already on disk
rather than needing a capture.

**Deliberately kept open, 2026-09-21 (W31 Decision Log 1 (c), ruled by the user;
recorded at W31 G4, claims §5.165 §3).** The ruling that closed this entry's
SIBLING — "the site's tone stage was designed around a convergence macOS 27 does
not have", now removed, ruled keep-as-re-ranged and executed by W30 G4 — names
this entry as what survives it: *the tone stage stays as re-ranged, with the
40 px plate's band recorded in the tracker*. So the band above is not a loose end
of a decision that was pending; it is the one thing the decision left standing,
and the stage's design question is settled around it. W29's Deferred item 8
closes on the same ruling.

Nothing in W31 moved it. The wave's leaf is inert over an achromatic backdrop and
the tone stage's ground is a neutral ramp, so the 40 px plate's alpha step is
exactly where W30 G4 measured it. The fix shape above is unchanged and is still a
read of rows already on disk.

---

## The CSS tier overshoots the curve's target over a pure black backdrop, and macOS 27 exposed it (W29 G4, 2026-09-20) — first-step overshoot CLOSED W36 G1

**W36 update (§5.179): the old first-step overshoot is closed, and the original
causal explanation below is superseded.** G0 identified the black response's zero
authority fallback, not conversion quantisation. The compact black branch now makes
the same ramp start at 141.3822 then 144.1696; monotonicity includes step zero again.
The test's stale band-amplitude oracle and anchor-blind colour conversion were also
corrected to the production chain; the former had selected the wrong anchor at black.
These ramp pixels are not the native deep measurement: its registered tone texture
is not painted behind the hosts. The measured native-black CSS residual is +1/+2
codes in the active pose and zero receded, recorded under W36 below. Near-black
interpolation and the CSS boundary projection remain open, not hidden by this closure.
The following original reading is retained as history, not the current diagnosis.

*Found 2026-09-20 landing the macOS 27 selection (claims §5.155 §5), by
`platform-web/e2e/pixel/backdrop-tone-pixels.spec.ts`'s twelve-step ramp.*

Over a **pure black** backdrop the CSS tier renders the 44 px surface at an
encoded level of **187.5** where the response curve's target is 0.2147 linear,
about 129 codes — roughly 58 codes high. One grey level up, at 13, it renders
144.2 against a target of 0.2446 and tracks from there to the top of the ramp
(150.1, 156.6, 164.2, 169.5, 174.7, 179.7, 183.7, 187.5, 189.8, 192.7). So the
rendered level moves the **wrong way** across the ramp's first step, by 43 codes.

It is not the law: the curve's own target is strictly increasing across this ramp
at both spans (`results/2026-09-20-w29-g4-landing/ramp-probe.txt`). It is the
conversion — an encoded `rgba()` overlay over a backdrop with nothing in it,
which is where the linear chain's quantum is coarsest and where
`linearChainReaches` hands the solve its anchored form.

**It is newly visible rather than newly true.** On macOS 26.5 the collapse owned
everything below grey 38 — `k` reads 1.00 at greys 0, 13 and 25 — so the surface
simply became its backdrop there and the conversion was never asked for a level
it could not reach. macOS 27's adaptation band is inert, which exposes the
region.

**No committed row covers it.** The bed's darkest backdrop is `dark-solid` at
(28, 28, 30), which is step 2 of this ramp and tracks correctly, so no adopted
bound and no floor is touched by this and no matrix row is wrong. What it
affects is a page whose own backdrop is darker than anything Apple's bed
contains — a black canvas, a dark video letterbox, a page that paints `#000`.

**The fix shape**: the GPU tier is the fidelity target and should be read first —
this reading is CSS-tier only, and whether the WebGPU tier lands the same target
over pure black is unmeasured. If it does, the residual is the tier conversion's
and belongs with the other cross-tier entries; the lever is the anchored solve's
behaviour when the anchor's own level is zero. If it does not, the level law's
first anchor is extrapolating below the bed and that is a fit question. Either
way the instrument exists: the spec above sweeps it, and the reading is committed
in its own comment.

---

## The CSS tier's heavy-share band flattened to 2 codes on the macOS 27 material (W29 G4, 2026-09-20)

*Found 2026-09-20 landing the macOS 27 selection (claims §5.155 §5), by
`platform-web/e2e/pixel/css-tier-pixels.spec.ts`.*

W16 G1 gave the CSS tier's heavy layer a raster `mask-image` carrying the depth
ramp, so the heavy share rises from `1 − s₀(span)` at the contour to `kDeep(span)`
at the reach. On a 220 × 120 surface the macOS 26.5 material put **more than 8**
alpha codes between the two depths; the macOS 27 material puts **2** — 127 near
the contour against 129 at the centre.

The band's shape did not change. Of the size law's constants only
`sizeScatterFloor` differs between the two documents, **0.40 against 0.25**, and
the heavy share is clamped up to that floor (`scatterFloorAtScale`), so a lower
floor lets the deep end sit nearer the contour's own share.

Nothing is wrong: the ramp is still in the raster, which is the property that
case exists to hold, and the tier's cross-tier bound is unaffected and green.
What is weaker is the **discrimination**: the case's floor moved from 8 codes to
1, so a future regression that flattened the band the rest of the way has 2 codes
of margin to be caught in rather than 8.

*Amended 2026-09-20 (W29 G4 review closure, claims §5.155): the margin as a
number. The assertion is `> 1` and the material reads **2**, so the case stands
**one code** above its own floor — a single code of drift turns it red, and there
is no room at all between a real flattening and a false alarm. "2 codes of margin
to be caught in" above is the width of the band that remains; the headroom the
case has before it fails is 1.*

**The fix shape**: read the band at a size where it is widest under this material
rather than at the size W16 happened to choose — the ramp's reach is 80 CSS px at
1x, so a surface a little over twice that separates the two depths by the most
the law allows. That is a fixture change and a re-measurement, not a material
one, and it should be done from the law rather than by trying sizes.

---

## `GlassToolbar` opens its split at the default document's blur, whatever document its root selected (W29 G4 review closure, 2026-09-20)

*Found 2026-09-20 by the independent review of the W29 G4 landing (claims
§5.155); the seam is `packages/react/src/controls/toolbar.tsx` around the
`samplingPaddingFor` call and `packages/platform-web/src/optics.ts`'s
`defaultSamplingProfile` / `defaultSamplingMapping`.*

`samplingPaddingFor` gained two optional arguments at W29 G4, `profile` and
`cssTierMapping`, so a caller drawing a material other than the default can ask
that material's question. `GlassToolbar` is the caller the function was exported
for, and it cannot pass either: the gap is derived inside the component from
`useGlassAccessibility()` and the partitions' own props, and nothing in the React
surface tells it which **material document** the root selected. So a React app on
`macos26MaterialProfileDocument` opens its split at the macOS 27 blur.

**The error is one-directional and it is the safe direction.** The default
document's `blurSigmaScale` is 2.2 against the module's 1, and the padding is
linear in the blur it is 3σ of, so the toolbar opens exactly 2.2× what the macOS
26.5 material needs — over-padding, never under. Nothing overlaps, no diagnostic
fires and no floor is missed; what the app gets is a wider gap than its material
asks for, at the one size it is least likely to notice, and the mis-statement is
in a layout rather than in a readout.

**Not fixed in the 0.19.0 cut, deliberately.** The React surface has no accessor
for the selected document — `root.material` is the resolved IDENTITY (name,
platform, endpoint key, digest, `tuned`) and not the document's two halves — so
closing it means adding public API to a prepared, versioned cut, which is a
larger change than the defect. It is also invisible to a page on the default
document, which is every page that does not opt out.

**The fix shape**, in the order of increasing cost: carry the selected document
on `GlassRootHandle` beside `root`, `ticker` and `profile`, where the toolbar
already reads through `useGlassRootHandle()`, and pass its `active[scheme].patch`
and `cssTierMapping` through; or give `GlassRoot` a `samplingPaddingFor`-shaped
accessor so the composition lives in one place and no consumer has to hold two
halves of a document. The first is additive and local; the second is the one to
take if a second layout consumer ever appears, because it is the same argument
that made a material a document rather than two options. Either way the case to
write is a React toolbar on `macos26MaterialProfileDocument` whose gap equals the
macOS 26.5 padding rather than 2.2× it.

**CLOSED 2026-09-20 by W30 G4 (charter Decision Log 1 (f), claims §5.160), by
the first fix shape.** `GlassRootHandle` carries `materialProfileDocument` — the
document the ROOT selected, seeded from the prop and re-stated at construction,
because `createGlassRoot` reads it once and a later prop change does not move the
material the page draws — and `GlassToolbar` passes that document's active
endpoint and `cssTierMapping` through `samplingPaddingFor`. Four cases in
`packages/react/test/toolbar-partition.test.tsx`, on the `clear` variant because
on `regular` at jsdom's span 0 both materials sit under core's advisory of 24 and
the max hides the whole difference.

Three things the fix turned up that the entry did not have.

- **`samplingPaddingFor` could not express the endpoint the case needed.** The
  macOS 26.5 light active endpoint carries no `patch` at all — it IS the
  renderer's constants, which is why `GlassMaterialEndpoint.patch` is optional —
  and the function's `input.profile ?? defaultSamplingProfile()` collapsed "this
  endpoint has no patch" into "use the default document's". So the one case the
  entry names would have measured the macOS 27 material through the macOS 26.5
  mapping. The key's PRESENCE now carries the distinction, documented at the
  signature.
- **The ratio is 2.04 on the light endpoint, not 2.2.** 2.2 is
  `cssTierMapping.blurSigmaScale`, and the padding is linear in the blur only
  when the renderer profile is held: at span 0 the macOS 27 light endpoint asks
  **22.69** CSS px against the macOS 26.5 endpoint's **11.10**, and on the dark
  pair it is 24.42 against 11.10, which is 2.20. The entry's "exactly 2.2×" was
  the mapping's number standing in for the measurement.
- **The seam had a second axis, and on that one the error was UNSAFE.** One
  document's two schemes do not ask for the same room — the macOS 27 dark
  endpoint wants about 7.6 % more than the light one — and the toolbar took the
  light endpoint's number under both, which is an under-pad on a dark root. The
  resolved scheme is now an input, polled through the store beside the pose
  (`colorScheme="auto"` resolves inside the runtime, so the prop standing still
  does not mean the answer did). The pose is deliberately NOT an axis: a gap that
  changed when the window lost focus would reflow the toolbar on blur, and the
  partition is structural.

---

## The reference pair labels its native panel "macOS 26.5" beside a caption naming a macOS 27 profile (W30 G1 review closure, 2026-09-20)

*Found 2026-09-20 by the independent review of the W30 G1 generation split
(claims §5.157); stale since W29 G4 moved the pair to macOS 27. The seam is
`apps/demo/src/site/Stage.tsx` — the capture's alt text (:310), the panel's
`pair__who` line (:313) and the collapsed layout's panel switch (:338).*

The pair's native half now serves the macOS 27 fixtures and prints the resolved
profile key under the image (`data-testid="native-profile"`, which
`color-scheme.spec.ts` asserts is `apple-macos-27.0-…`). Three strings around it
still say "macOS 26.5": the screen-reader description of the capture, the
caption's *who*, and the radio label a reader uses at narrow widths. So the page
states two different provenances for one image, and the one a screen reader gets
is the wrong one.

Nothing measured moves — the fixtures, the cell and the key are all macOS 27 —
which is why this is prose debt rather than a defect in the comparison. It is
also why no test caught it: the assertions read the profile caption, which is
derived, and not the labels, which are literals.

**The fix shape**: derive all three from the same source the caption is derived
from (`nativeProfileFor(props.scheme)`, or a short display name beside it) so a
future move of the bed cannot leave one of them behind. W30's charter puts it in
G4, with the rest of the landing's page work.

**CLOSED 2026-09-20 by W30 G4 (claims §5.160).** `scenes.ts` gained
`nativePlatformFor(scheme)`, which parses the release out of the profile key the
caption already prints and throws if it cannot — so the three labels are derived
from the same string the assertion reads, and a bed that moves again carries all
three with it or fails loudly. No literal release string is left in `Stage.tsx`.

---

## `CLAUDE.md` still documents the row-reduction heuristic the generation split retired (W30 G1 review closure, 2026-09-20)

*Found 2026-09-20 by the independent review of the W30 G1 generation split
(claims §5.157). The seam is `CLAUDE.md`'s calibration section, the sentence
ending "`rm results/matrix.json` before a full rebuild, or reduce to the newest
row per key".*

Since W30 G1 the working matrix holds one generation per profile and the
superseded one is moved, byte for byte, to `results/superseded/<document-sha>.json`
by `results/2026-09-20-w30-g1-split/split-generation.py` (contract X7). "Reduce
to the newest row per key" is the timestamp heuristic that split replaced, and
`rm results/matrix.json` would delete 1,107 rows of frozen macOS 26.5 evidence —
the instruction most likely to be followed literally is the one that destroys the
most.

**The fix shape**: replace the sentence with the split — what appends, what
moves it, and the invocation — when G4 runs the script for the second time and
can state the instruction from a second application rather than from one. W30's
charter clause 7 carries it.

**CLOSED 2026-09-20 by W30 G4 (claims §5.160).** `CLAUDE.md`'s Calibration
paragraph now states the split: a read appends, `split-generation.py` moves the
generation it superseded to `results/superseded/<active-document-sha>.json`, and
`index.json` is the lookup. The destructive sentence is gone rather than
softened. The instruction is written from the THIRD application of the rule, not
the second — G1 moved W29 G3's generation, G3b moved W30 G3's, and this gate
confirmed the layout holds with nothing left to move (`plan` reporting 1,833
retained and 0 moved), which is the state the paragraph describes.

---

## A change's "checked, unchanged" sweep read the imports and not the prose (W30 G1 review closure, 2026-09-20)

**CLOSED 2026-09-21 by W31 G2 (claims §5.163 §5), on both halves.**
`matrixSchemaRefusal`'s message no longer cites wave Decision Log 15
ruling 3: re-read against what trips it today, a run reaching that predicate
got there by NAMING a target, and the three such files are a scratch matrix an
earlier `--out-matrix` wrote, one restored from a branch, and a superseded
generation under `results/superseded/` — which is what it now says, with "a
recorded number is never rewritten" as the reason none of them is a target.
`test/compare-gates.test.ts` gains two cases in place of the one that pinned
the old copy: the ruling must not be cited, and the three files must be. The
same stale claim lived in `cli/compare.ts`'s and `cli/diff.ts`'s own comments,
both corrected beside with the old reading named.

*Amended 2026-09-21 (review closure; claims §5.163 §8, finding N4): the three
files are all OLDER-schema artefacts and the message offered them in both
directions.* Each of them was written by a build of this repository that has
since been superseded. A file at a NEWER schema is none of them and cannot be —
nothing in this tree has written one — so it came from a build this checkout does
not have: a branch ahead of this one, or a working tree that bumped
`RESULT_MATRIX_SCHEMA_VERSION`. The enumeration is now in the older branch alone
and the newer branch says that instead. The pinned case for the newer branch
asserted the two words "a newer" and would have passed on the wrong sentence,
which is this entry's own failure mode one layer down; it now asserts five
substrings of its own and that the older branch's list is absent.

The RULE — *when a sweep reports a file "unchanged, checked", say what the file
CLAIMS about the thing being changed, not only whether it reads it* — is in the
root `CLAUDE.md`'s Conventions, beside "never rewrite a recorded hash". The two
homes the charter offered do not work: `packages/calibration` has no README, and
the ledger is a flat sequence of dated claims a child reads by section, so a rule
in §5.163 would be found only by whoever already knew to look. `CLAUDE.md` is
loaded before any work begins, which is when a sweep is planned rather than after
it has gone stale.

---

*The original entry, kept:*

*Found 2026-09-20 by the independent review of the W30 G1 generation split
(claims §5.157 §7). The instance: `src/report.ts`, `cli/gates.ts` and
`test/adopted-thresholds.test.ts` each described `results/matrix.json` as a
schema-4 file held there by wave Decision Log 15 ruling 3, long after the post-W8
pass closed that gap — the test asserting `toBe(5)` twice under a title saying
the two numbers differed. Corrected in the closure itself.*

The sweep that produced §5.157 §7's consumer table listed those three files as
"carry the path in strings and comments only — unchanged, checked", which was
true of what they *do* and false of what they *say*. A file that only mentions an
artefact is exactly the file whose mention goes stale, because nothing executes
it and no test reads it.

What is still open is the same error one layer out: `matrixSchemaRefusal`'s
**runtime message** still offers the operator "If that is the frozen inactive-bed
matrix, it is meant to stay frozen (wave Decision Log 15 ruling 3)", which
describes a state that ended. It is conditional and therefore harmless, and it is
user-facing copy, so it was left rather than rewritten in a closure whose subject
is the split.

**The fix shape**: re-read the refusal's wording against what a run that trips it
today would actually be — a scratch matrix, or one restored from a branch — and
say that instead; and when a sweep reports a file "unchanged, checked", have it
say what the file *claims* about the thing being changed, not only whether it
reads it.

---

## Nothing checks that a WGSL transcendental's argument stays inside f32 (W30 G3b, 2026-09-20)

**CLOSED 2026-09-21 by W31 G2 (claims §5.163) on all three fix shapes, with the
residual paragraph amended beside rather than over — the candidate it named is
refuted and the residual is re-opened.**

1. The unit case exists: `packages/renderer-webgpu/test/w31-wgsl-range.test.ts`
   over `test/wgsl-range/`, which reads every file in `src/wgsl/`, finds every
   call of `exp`, `exp2`, `pow`, `tanh`, `sinh`, `cosh`, `log`, `log2` and
   `inverseSqrt`, resolves each argument's interval through bindings, helpers
   and the bounding builtins, and requires the result to be finite in f32 or the
   argument to carry a committed range proof with a witness. **Eleven sites,
   eight clamped by the source, three proven, none STOPPED.** Run against the
   unfixed `outer_shadow_falloff` it reads UNBOUNDED at the very site of this
   entry's own defect. Bare division is outside the rule by decision, with the
   reasons in `scan.ts`'s module note and the one measurement that decided it:
   of over a thousand divisions in `src/wgsl/`, exactly one has a uniform as its
   immediate divisor. *(Corrected 2026-09-21, review closure; claims §5.163 §8,
   finding N5: both counts are wrong. There are **99** divisions once comments
   and the TypeScript import paths are out — the raw slash count is 117 and
   `index.ts` contributes 15 of them with no arithmetic at all — and **three**,
   not one, have a uniform as their immediate divisor: the viewport's own size
   in `optics.ts` and in `silhouette-tone.ts`, and the analysis reduction's
   fixed grid. None of the three is a material leaf, which is what the decision
   rested on, and the fourteen uniform divisors a leaf CAN reach are all floored
   by the shader's own `max(x, 1e-6)` idiom. `division-count.py` / `.txt` in the
   gate's evidence directory.)*
2. The `@gpu` sweeps exist: `e2e/gpu/w31-range-sweeps.spec.ts`, both halves of
   every ratio — the material axis bracketed by **550×**, which is the widest
   ratio any leaf has moved between two material generations rather than a
   number somebody liked, and the scene axis over spans 32…340 at the shipped
   material. The lens depth, the lens exponent, both scatter taps, the tone
   knots, the abscissa alone, the rim's exponent and its axis: every reading
   0 undrawn at IoU 1.0000. *(Amended 2026-09-21, review closure; claims §5.163
   §8, findings N2 and N9. The column is CONTAINMENT, not IoU — the drawn
   fraction of the declared mask, which is blind to over-draw by construction —
   and the recorded values are unchanged. And each ladder's endpoints are now
   also read at spans 32 and 340, twenty-eight CROSS readings in
   `sweeps-cross.txt`, because a pair of one-dimensional sweeps cannot see a
   defect that is a combination, and §5.159b's was.)*
3. The standing guard exists: `renderScene`'s readback refuses an enclosed
   region of zero alpha **inside the drawn silhouette**. The silhouette clause
   was earned rather than designed — the first form had only enclosure and fired
   on a single pixel of the outer shadow's quantisation tail, on two of
   forty-two `@gpu` cases (`guard-first-form.txt`). *(Amended 2026-09-21, review
   closure; claims §5.163 §8, findings N1 and N7. Two things. The wall is now
   read **per declared region** — half the peak alpha inside the region being
   read — because a raster-wide wall made a surface's sensitivity depend on what
   else was in the frame: a hole punched through a dim surface read 0 holes with
   a bright surface elsewhere and 1 without it, and `glass-over-glass` is a
   two-surface scene. And the guard is **test-time**: `renderScene` here is
   `window.vitrea.renderScene` in the e2e harness, nothing under `src/` runs it,
   so "every scene" is every scene an e2e spec renders and not a runtime
   property of the renderer.)*

**And the class had one more member than anyone had found.** `highlight.ts`'s
`angle_delta` returns `min(raw, TAU - raw)`, which goes negative past one
revolution, into a `pow` base WGSL leaves undefined. It is reachable from an
application: the sweep phase comes off a CSS custom property that nothing clamps
(`readHostChannels` clamps `materialization` and not `sweep`). Floored as an
identity; the goldens are byte-identical.

**The fix shape left open is now its own entry**, below: *"The sweep phase
reaches the uniform unwrapped"*. It was a paragraph here until 2026-09-21, which
is to say inside a CLOSED entry, where a reader looking for open work does not
go (review closure; claims §5.163 §8, finding N3).

---

## The sweep phase reaches the uniform unwrapped (W31 G2, 2026-09-21)

*Opened at W31 G2's review closure out of a paragraph inside the closed WGSL
range-class entry above (claims §5.163 §2 and §8, finding N3).*

The highlight's specular band is centred on a sweep PHASE that comes off a CSS
custom property, and nothing wraps it. `readHostChannels` in `platform-web`
clamps `materialization` and does not touch `sweep`, so `--vitrea-sweep: 3` puts
the band's centre at three τ. Before W31 G2 that reached a negative `pow` base
through `angle_delta`'s `min(raw, TAU - raw)` and was a NaN; the floor that gate
added makes it **safe** without making it **mean** anything — out of range, the
band is now centred on the pixel, which is a defensible reading of nothing in
particular.

**The fix shape**: wrap the phase where it is READ, in `platform-web`'s
`readHostChannels`, beside the clamp `materialization` already has. One line. It
belongs there rather than in the shader because a phase is periodic and a clamp
is not: wrapping is the operation that makes an out-of-range value the value the
author meant, while the shader's floor is only the operation that keeps it
finite.

**What it is worth**: the defect it would fix is cosmetic and reachable only from
an application that writes a phase outside [0, τ), which nothing vitrea ships
does. It is recorded because the next channel of this shape will have the same
gap, and because the shader floor above is easy to mistake for the whole fix.

---

*The original entry, kept:*

*Found 2026-09-20 by W30 G3b diagnosing §5.159 §6's undrawn strip (claims
§5.159b). The instance is fixed; the class is not.*

The optics pass's `outer_shadow_falloff` computes `tanh(K · (x + C·x³))` where
`x` is a distance in σ. Nothing bounded `x`, and a backend that lowers `tanh`
through `exp(2t)` — Metal's fast-math path, which is what Dawn runs on the
capture machine — overflows f32 at `t = 44.3614`, returning `Inf/Inf`. The NaN
reached the composite's alpha and left a strip of a 44 px surface undrawn. **It
had been reachable since the facet was built** and nothing found it for six
waves, because reaching it needed a σ narrower than any material the project had
shipped: it took macOS 27's span-graded blur to make a caster ten σ deep.

Two properties made it invisible rather than one. The 34 goldens render at one σ
and cannot sweep a law. And SSIM over a whole cell barely moved — 0.98217 →
0.97826 — so every perceptual row stayed green; the bound that caught it was
W20's declaration conformance, which reads the drawn COVERAGE.

**What is still open is the class.** `src/wgsl/` evaluates `exp`, `pow`, `tanh`
and several polynomials on quantities a profile document can scale, and no test
asserts that any of their arguments stays inside f32's range over the span of
inputs the bed carries — let alone over the span a future fit could produce. The
fix that landed is a clamp on one argument; the generalisation is not there.

**The fix shape**, in the order a later child would want it:

1. A unit case over the WGSL sources that finds every call to a transcendental
   and requires its argument to be clamped, or to be accompanied by a named
   proof of its range. Cheap, mechanical, and it would have caught this one.
2. A `@gpu` case in the shape of `w30-thin-sigma-coverage.spec.ts`'s second
   test — sweep a material constant over the range a fit could reach and assert
   an invariant that does not depend on it. That case exists now for σ against
   coverage; the same shape is available for the lens depth, the scatter widths
   and the tone response's knots. **Sweep the SCENE's axis too, not only the
   material's** (added 2026-09-20, review closure; claims §5.159b §10, finding
   11): what overflows here is a ratio of a caster's depth to its σ, so a sweep
   that holds the geometry fixed covers half the exposure. The third case in
   that file sweeps the depth at the macOS 26.5 σ and fails on the unfixed
   renderer at a 340 px caster — a surface class the calibration bed does not
   carry, and therefore one that no capture could ever have exposed. Every
   guard of this kind wants both halves of whatever ratio it is guarding.
3. A cheaper standing guard: `renderScene`'s readback already throws on a WebGPU
   validation error, and it could also refuse a raster whose alpha has a hole
   inside a declared silhouette. That is the signature a NaN leaves, and it is
   one pass over the bytes the harness already has in hand.

**AMENDED 2026-09-21 (W31 G2, claims §5.163 §6): the candidate below is
refuted and the residual is re-opened.** The range proof (1) asks for was run per
component per document (`falloff-reach.py`). Two independent readings. The
overflow is **one-sided**: it needs `2t > +88.7228`, so only a pixel INSIDE the
shadow's silhouette can reach it, and an exterior pixel's `t` is negative, where
the same lowering drives `exp(2t)` to zero and returns −1 without leaving f32. So
"a handful of exterior pixels at the overflow boundary" cannot be the cause of
anything. And no interior pixel of that scene reaches it either: the deepest sits
at `x = (halfSpan + spreadPx)/σ`, which is **8.3963** on the light document and
**8.4511** on the dark — both on the `over` surface at span 56 — against 10.0610,
a margin of about 6 CSS px of depth. The three texture cells therefore moved
across a change that is provably the identity on every pixel of their scene.
Their remaining candidate is the one the FOURTH cell already has, this tracker's
"The CSS tier's capture is not byte-reproducible across landings" — which would
have to be wider than that entry says, since these are texture rows — and what
would settle it is that entry's own fix shape: the three cells captured twice in
one day at one renderer, with `shadow.falloffSigmaWeb` read for whether it
reproduces to the digit.

*Beside it, from the same table: `rrect-48` clears the boundary too, at x =
10.2156 light and 10.3911 dark — 1.5 % and 3.3 % over, a thin strip. It is a
probe component, so its rows are never gated and W20's declaration conformance
could not have flagged it; it sits inside §5.159b §3's "the ladder's span-44
column WAS" and was never named separately. The fix that closed it is the same
one and nothing is owed.*

**One residual this gate measured and did not explain.** Four `glass-over-glass`
cells on the dark beds moved across the fix by up to 8·10⁻⁴ CSS px on a fitted
shadow σ whose own residual is 10⁻², with their `shape` axis not moving at all
(`results/2026-09-20-w30-g3b-thin-strip/moved-cells.txt`). The other 172 moved
cells are all span-44 casters and are exactly W20's 170 plus two. The shape of
the explanation is a handful of exterior pixels whose falloff argument sat at the
overflow boundary, and the way to settle it is (1) above: a range proof would say
whether any pixel of that scene reaches it.

*Split in two, 2026-09-20 (review closure; claims §5.159b §10, finding 2;
`moved-cells.v2.txt`).* Per cell the four are not one population. Three are
**texture** rows on the 2x-dark bed and move by at most 7.94·10⁻⁴
(`shadow.falloffSigmaWeb`) and 8.86·10⁻⁴ (`shadow.centroidOffsetXWeb`); the
paragraph above describes them, and (1) is still how they are settled. The
fourth is `checkerboard__glass-over-glass__rest` on
`apple-macos-27.0-1x-dark-standard-glass0.5`, **`dom` tier**, at **4.56·10⁻³** —
five times the others, on a tier that has no shader and never evaluated the
falloff for a pixel, so the overflow boundary cannot be its cause. **The
candidate is this tracker's own standing class**, "The CSS tier's capture is not
byte-reproducible across landings" above: a Playwright/compositor
frame-rounding difference of one code, whose recorded instances include
`checkerboard__glass-over-glass__rest` on a dark bed at W18's landing, which
flips between landings and never within a day's runs — and G3's read and G3b's
are two landings. Not settled: settling it wants that entry's own fix shape, the
page settled for two animation frames before the CSS path's screenshot, and then
a same-day control.

---

## The canonical `web-captures/` tree held no current generation, because every read ran in a worktree (W31 G4, 2026-09-21) — NARROWED 2026-09-21 (W32 G0b): the generation check landed, and it cannot see the 26.5 defect

*Found at the W31 charter's grounding read and sharpened by W31 G0 (charter
Surprises; claims §5.161 §2). **Fixed for this wave and not for the class.***

`CLAUDE.md` has said since W29 that the canonical `packages/calibration/web-captures/`
"lives on the capture machine and is what the sheets and the demo fixture are
copied from". That sentence was false for two years' worth of waves and nobody
noticed, because nothing reads the tree except a person making a sheet.

Two facts, and the second is the sharper one:

- **The tree held no macOS 27 generation at all.** It carried the six macOS 26.5
  trees, last written 2026-09-10. Every W29 and W30 read ran in an agent
  worktree, captures are gitignored, a worktree inherits none, and the worktree
  was removed after merge — so the pixels the committed rows were measured off
  were deleted as soon as the rows landed. The two surviving worktree trees were
  at earlier document hashes.
- **The macOS 26.5 tree that DID exist was a different generation from the rows
  beside it.** W31 G0 re-measured all six frozen trees with `--skip-capture` —
  no browser, today's metric on both sides — and reproduced 282 of 284 cells
  exactly. The two that miss are `photo__glass-over-glass__rest` on the two light
  profiles, `texture` tier, `interiorMeanWeb` 2.840e-03 and 2.527e-03 out, with
  the `dom` tier of the same cells reproducing to the last bit. The tree's files
  are dated 2026-09-10 and the rows were measured 2026-09-11. **So the macOS 26.5
  columns of that one scene are read off pixels the committed row was not read
  off**, and any sheet made from them carries that sentence.

**What closed the immediate problem.** W31 acceptance clause 6 makes copying the
read's tree to the canonical path part of the merge, and the parent did it at
W31 G3c's merge: the tree held all six macOS 27 profiles at the shipped
document hashes (`49490eb9ff7a` / `14c6bacf2eda`, `b5714a866288` /
`cc4ed1038996`). *(Corrected beside, 2026-09-21, W32 G1 review closure; claims
§5.168 §10: those are 0.21.0's hashes and "now" has moved on. W32 G1 sealed four
new macOS 27 documents, and the tree its read wrote — 786 captures, checked
786 / 786 match — names `d5bdd6eac432` / `45acb6d916b9` and `431cabd391c4` /
`4e68f81869f6`. Copying that tree to the canonical path is the parent's step at
the merge, which is the clause itself. A hash written as "now" in a tracker
entry ages at the next seal; what does not age is the clause.)* W31 G4's `sheets.ts`
is the first sheet script that reads the
canonical tree AND asserts, per cell, that the capture names the shipped
document bytes — receded document included — refusing rather than photographing
a stale one.

**What is NOT closed, and it is the class.** The copy is a step in a charter, not
a rule anything enforces, and the next wave that reads in a worktree and forgets
it puts the tree back where it was. **Nothing anywhere checks that the canonical
tree and `results/matrix.json` are the same generation.** The two frozen macOS
26.5 cells above are the standing proof that they can silently diverge.

**The fix shape**: a checker that walks the canonical tree's `cell__*.json`, reads
each capture's document hashes, and asserts that for every profile the tree
carries, the generation it names is the one the matrix's rows for that profile
name. It is a file walk and a string compare — no browser, no capture — and it
can run in `pnpm -r test` as a case that skips cleanly where the tree is absent,
which is what makes it usable on a machine that is not the capture machine.


**The generation half is closed by a tool.**
`packages/calibration/scripts/check-capture-tree.ts`, run as
`pnpm --filter @vitrea/calibration run check-capture-tree`, is the file walk and
string compare this entry asked for: every `cell__<renderer>.json`'s document
hashes — the receded document included — against the row the working matrix holds
for that profile, renderer and scene. It skips cleanly and exits 0 where the tree
is absent, exits 2 rather than 1 on a frozen profile so a merge gate is not made
un-passable for a fault contract X1 forbids anyone to clear, and `--superseded-ok`
demotes only a generation `results/superseded/index.json` has RECORDED — stale by
choice, which is nameable, as against stale by accident, which is not. On today's
canonical tree: 1,840 captures, 1,833 match, 0 mismatch, 0 superseded, 0
unreadable, 7 with no row, 0 rows with no capture, exit 0 (claims §5.167 §3).

**What is left is the half this entry's own evidence is made of, and the checker
is structurally blind to it.** The two macOS 26.5 cells above read as MATCHING.
They are supposed to: the frozen documents have not moved since W29, so that
divergence is a **re-capture at unmoved document bytes**, and there is no hash for
a string compare to disagree on. A document-hash checker can tell a stale
GENERATION from a current one and cannot tell one capture from another at the same
bytes.

**The narrowed fix shape**: a `compare --skip-capture` re-derivation of the
committed metrics off the tree's own PNGs, cell by cell, which is exactly how W31
G0 found those two cells. It needs no browser and no fixture beyond the tree, but
it is minutes of CPU rather than a file walk, so it belongs at a gate's read
rather than in `pnpm -r test` — and it is the only thing that can assert the tree
and the rows are the same CAPTURE and not merely the same generation.

**Also still open: the "automatic" half of this entry's own fix shape** (W32 G0b
review closure, NB3; claims §5.167 §3 beside and §8). This entry asked for a check
that "can run in `pnpm -r test` as a case that skips cleanly where the tree is
absent", and what landed is a script the PARENT runs — at every merge, and inside
G1's read by the charter's clause 5. It is in no committed `chain.sh` yet; G2's,
copied from W31 G4's, is where it becomes a recorded step of the chain. Wiring it
into the unit suite was declined for cause rather than overlooked: the canonical
tree lives on the capture machine, a gate mid-read leaves it at a generation the
split has not recorded yet, and `--superseded-ok` demotes only generations already
recorded, so the suite would be red on the one machine that holds the tree for the
duration of every read, with no flag saying why — and a test somebody switches off
during a read is this entry's own failure mode one level up. **What would close it**
is a signal a mid-read tree can carry that the suite can read: a marker the capture
driver writes into the tree naming the generation being read and the gate reading
it, so a case can pass on "this tree is mid-read at these documents" and fail on
anything else. That is a change to the capture driver, not to the checker.

**Two blind spots of the landed checker closed at the same closure**, recorded here
because this entry is what a reader comes to for what the instrument sees: a
cross-profile miscopy (a 1x capture in the 2x directory, a standard capture in the
reduced-transparency one) named the row's documents and read as a MATCH, since a
document is shared across profiles by design — the `deviceScaleFactor`,
`colorScheme` and `accessibility` clauses are now compared beside the documents as
a `misfiled` class; and exit 2 was reached by an unreadable capture whose only
company was a frozen key, which reported a fault anybody may clear as one contract
X1 forbids anyone to touch (NB2, NB5).

**Merge record 2026-09-22 (W32 G1's merge, `9c4b3bce`).** The copy was made as the merge that
landed the read: the worktree's tree (786 captures, 3,930 files, 71 MB) copied byte for byte to
the canonical `packages/calibration/web-captures/`, and the checker run on the canonical tree
afterwards reads **1,900 captures, 1,893 match, 0 mismatch, 0 misfiled, 0 superseded, 7 no-row**
(the seven are the frozen macOS 26.5 trees' known extras). The generation the copy REPLACED —
the six macOS 27 subtrees at documents `49490eb9ff7a` / `b5714a866288`, 3,630 files, 67 MB, the
pixels the rows now in `results/superseded/` were measured off — was not deleted: it was moved
on the capture machine to `packages/calibration/web-captures-superseded/<active-document-sha>/`,
named the way `results/superseded/<sha>.json` is, gitignored beside the canonical tree. Nothing
reads that sidecar yet; a sheet of a superseded generation would point `VITREA_WEB_CAPTURES` at
it and the checker would class every cell `superseded` there, which is the reading it is for.

**Merge record 2026-09-22 (W33 G1b's merge, `979c63e3`).** Same rule, second time: the worktree's
tree (786 captures, the read at the lift-stand-down documents) copied byte for byte to the canonical
`web-captures/`; the checker there reads **1,900 captures, 1,893 match, 0 mismatch, 0 misfiled,
0 superseded, 7 no-row**; gated 230 / 786. The generation it replaced — the six macOS 27 subtrees at
documents `d5bdd6eac432` (light) / `431cabd391c4` (dark), the pixels the rows now in
`results/superseded/d5bdd6eac432.json` and `431cabd391c4.json` were measured off — moved to
`web-captures-superseded/<sha>/` beside W32's pair. The sidecar now holds four generations.

**Merge record 2026-09-24 (W36 G1's merge, `daae2cb4`).** Same rule, third time: the worktree's
`packages/calibration/web-captures/` (the six macOS 27 profile directories, 786 rows read at the
sealed documents — light active file `85ad7f7e3e0d`, light receded `30fbe05986ae`, and their dark
pair) copied to the canonical path; the replaced W33 generation moved to
`web-captures-superseded/6e509c7f76cc/` (the four light-keyed profile directories) and
`web-captures-superseded/eab099cc6698/` (the two dark-keyed), named by the active document exactly
as the retired matrix rows are in `results/superseded/`; the six frozen macOS 26.5 directories
untouched; `check-capture-tree` on the canonical tree afterwards: 1,900 captures, 1,893 match,
0 mismatch, 0 misfiled, 7 no-row.

---

## A retention conditioned on the SURFACE is the operator's next form, and the same defect already shipped once as a policy bug (W31 G4, 2026-09-21)

*Deferred by W31 Decision Log 3 (b) with its evidence measured rather than
anticipated (claims §5.164 §8 (a), §13; §5.165).*

`bodyChromaRetention` is one constant per document. It restores a constant
fraction of the FULL backdrop chromaticity regardless of what the plate actually
transmits, and `1 − sizedAlpha` — what the plate leaves — falls as the span
rises. So the same constant buys a larger relative chroma gain on a larger
surface, and the operator scales the per-cell spread rather than closing it.

The numbers, all from the canonical read:

- **The fit closes the median and widens the spread.** The light active bed's
  per-cell range goes from 0.5095–0.6533 before to 0.8891–1.4417 after — a factor
  between the extremes of **1.2824 → 1.6216**, like for like over all ten cells.
- **The largest span overshoots.** `photo__rrect-lg__rest` on the WebGPU tier
  reads `R` **1.2391** (1x dark) and **1.3596** (2x), outside the 0.80–1.20 the
  median is bounded to, on a holdout cell the bound is not stated over.
- **The thinnest surfaces overshoot the other way and are now gated.** W31 G4's
  M1 records three `photo__rrect-sm` cells MISSED at 1.5155, 1.4469 and 1.4417.
- **The gain is uncorrelated with what the plate transmits**: correlation −0.39
  between transmitted chroma and gain over 56 cells.

**It has already shipped once as something else.** W31 G3's leaf was applied
unconditionally, and under an accessibility occlusion lift — where `1 − α` is a
tenth to a fiftieth of nominal — it took the body's chroma-to-structure to three
times the reference's. W31 Decision Log 3 (d) fixed that with a hard stand-down,
and the ruled smaller rule (`r · (1 − lift)`) was measured and DECLINED because
scaling a constant fraction of the full chromaticity by the plate's remaining
share still over-restores where that share is small. **The accessibility path and
the span overshoot are the same defect read at two axes**, and the stand-down is
its first policy-level instance rather than a separate fix.

**The fix shape**: make the retention a function of the plate's own alpha — as
W30 made σ a function of the casting span — so that what is restored is a
fraction of what the plate TOOK rather than of what the backdrop has. The
preconditions are named and one of them is a scenes decision: the dark bed has
four cells at one span each, which is not enough to fit a slope on, so the wave
that takes this first widens the dark bed's spans in
`apps/reference-apple/scenes.json`. A law rather than a value also has to be
mirrored on both tiers and pinned by `tier-coherence.test.ts` — except that this
tier carries none of the operator at all (entry below), so the mirror is a
recorded decline.

---

## The two accessibility documents inherit a retention nobody measured, and now stand it down entirely (W31 G4, 2026-09-21)

*Deferred by W31 Decision Log 3 (c) behind (d) (claims §5.164 §8 (b), §13).*

Reduce Transparency and Increase Contrast are the light document plus an
occlusion lift, and W31 Decision Log 2 (a) ruled that they inherit the light
document's `bodyChromaRetention`. Read at the canonical bytes with the leaf
applied, their untinted `photo` medians on the WebGPU tier were **3.0374** and
1.9923 (reduced transparency, active and inactive) and **2.9489** and **0.1381**
(increased contrast) — an inherited constant reading three times the reference on
one bed and a seventh of it on another.

W31 Decision Log 3 (d) stands the retention down under any occlusion lift, so
0.21.0 draws what 0.20.0 drew on those beds: R **0.9096 / 0.8294 / 0.8147 /
0.1552**, proven at the raster (48 of 48 PNGs identical) and re-derived at W31 G4
off the committed matrix (`accessibility-identity.txt`: 6,855 numeric readings
across every axis, none moved). So there is no regression and there is also no
measurement: **the question of what retentions those two documents should carry
is now open on a material that has none.**

Two readings that say the answer is not obviously zero:

- **The increased-contrast INACTIVE bed reads 0.1552 against a reference of 1**,
  and always has. That bed's body carries a seventh of the reference's
  chroma-to-structure with or without this wave, which is a gap the stand-down
  freezes rather than creates. W31 G4's `eye.md` §1 sees it: vitrea's plate is a
  clean white where the reference keeps a faint warm-to-green cast.
- **The declined lift rule's perceptual rows were BETTER on three of four beds.**
  Under `r · (1 − lift)`, `oklabDeltaEP95` read 0.02946 / 0.01121 / 0.00989 /
  0.03696 against 0.02882 / 0.01362 / 0.01107 / 0.03705 at 0.20.0. The choice was
  made on `R`, correctly — a body at twice the reference's chroma under a
  preference asking for less transparency is the defect whatever a whole-cell P95
  says — but it means a fitted retention for those documents is not obviously a
  retention of zero.

**The fix shape**: fit the two accessibility documents' own retentions on their
own beds, which carry sixteen and eighteen gated cells, and decide whether the
right form is a value per document or the surface-conditioned law above evaluated
at the lifted alpha. The second is the more likely answer and is why this entry
sits behind that one.

---

## The CSS tier carries none of the body's chroma operator, and on the dark scheme its one lever is inert (W31 G4, 2026-09-21)

*Measured and declined at W31 G3 (claims §5.164 §5, §8 (c)); the two `dom` rows
it costs are in `MISSED_27_ROWS`.*

The CSS tier's only operator on the body's chroma is the `saturate()` inside its
one `backdrop-filter`, which acts on the backdrop BEFORE the `rgba()` plate
covers it. A mirror of the renderer's retention was derived from the leaf — a
gain `1 + r·α′/(1 − α′)` at the converted alpha this tier solves, leaving the
authored 1.8 and 1.4 exactly where X3 froze them and exactly 1 at the identity —
written, wired through `root.ts`, rendered on the declared bed, and taken back
out on the measurement.

| bed | ratio (ii) native | before | after | reach |
| --- | ---: | ---: | ---: | ---: |
| light active (10) | 0.7891 | 0.4719 | 0.7142 | 0.764 |
| light inactive (8) | 0.7721 | 0.4990 | 0.7818 | 1.035 |
| dark active (4) | 0.9453 | 0.2024 | **0.2024** | **0.000** |
| dark inactive (4) | 0.9042 | 0.2224 | 0.2288 | 0.009 |

**On the dark scheme it is not merely insufficient, it is inert.** A probe at a
retention of **1** — the most the leaf can hold — leaves the dark active cells at
0.2024, unchanged to four decimals, which is the law's own `open ≤ 1e-3` guard
speaking: the converted alpha there leaves no backdrop for a saturation to act
on. §5.161 §6's dark ceiling is therefore unreachable rather than an upper bound.
**On the light scheme it buys a great deal and breaks both stops doing it** —
the level-growth stop on 10 of 26 cells and the structure stop on 13 — because
`saturate()` is a matrix on sRGB-ENCODED channels and stops preserving luminance
the moment one clips.

The cost is recorded rather than approximated: `photo__rrect-lg__rest ::
oklabDeltaEP95` on the two dark `dom` rows is **unmoved to the fifth decimal**
(0.20095 and 0.19474 against ≤ 0.18 and ≤ 0.19) while its `texture` siblings
cleared at the same material. W31 G4's sheets show it directly — on the dark
sheets the third panel is the flat grey body G0 described and the second one is
not.

**The fix shape, and it is the `rgba()` layer rather than the backdrop beneath
it.** A gain on `saturate()` is inert where the converted alpha covers the
backdrop and clips the level where it does not, so the reachable work is a chroma
term on the covering layer — a tint whose chromaticity is derived from the
sampled backdrop rather than authored — or a plate this tier does not solve to
full coverage. `BODY_CHROMA_RETENTION` stays exported from
`platform-web/src/optics.ts` at 0 with the measurement beside it, and
`tier-coherence.test.ts` pins it against the four SHIPPED documents' retentions
as literals, so a document that doubles its retention widens a recorded gap and
the case says so.

---

## On the receded TINTED cells vitrea's body has no chroma at all (W31 G4, 2026-09-21)

*Found by W31 G0's per-pixel instrument (charter Surprises; claims §5.161 §3
finding (b)); frozen out of W31 by X3.*

Ratio (ii) — the interior's per-pixel chroma over the raw backdrop's — reads
**0.001–0.006** on the receded tinted cells against the reference's **0.54–0.65**,
while the ACTIVE tinted cells match almost exactly (1.433 against 1.435). So on
an unfocused window vitrea's tinted body is achromatic where Apple's keeps its
colour, and the defect is specific to the recede and specific to the tint path.

**The cause is named and is not this wave's operator.** W27c's chroma collapse
acts on the tint SEED inside `if (tintK > 0.0)` and drives the paint to neutral
in the receded composition. `bodyChromaRetention` is applied BEFORE the tint
composition and is inert at `s = 1` by construction — the canonical read
confirms it, 147 of the 148 shared tinted rows at exactly zero movement — so this
wave neither caused it nor could have closed it. X3 froze the tint's chroma law
for the whole of W31.

**The fix shape**: re-read W27c's seed collapse against the macOS 27 receded
fixtures, which is a different bed from the one it was fitted on, and decide
whether the collapse is a receded behaviour Apple has at all or a macOS 26.5
reading that macOS 27 ended. The instrument to judge it on exists now: ratio (ii)
on the receded tinted cells, web against native, which is the table above.

---

## The retention under Increase Contrast ALONE is unmeasured, and the bed cannot measure it (W31 G4, 2026-09-21)

*Found by W31 G3c's independent review, folded at W31 G4 (claims §5.165).*

`bodyChromaRetentionUnderPolicy` stands the retention down on
`policy.occlusion === "increased" | "opaque"`. Only **Reduce Transparency** sets
an occlusion: `ACCESSIBILITY_BEHAVIOR_TABLE`'s `increasedContrast` row carries
`border`, `foreground` and `ambientTint` and no occlusion key, and
`media-policy.ts` matches `prefers-contrast: more` and
`prefers-reduced-transparency: reduce` independently. **So a 0.21.0 page under
Increase Contrast alone draws the retention at its full value.**

That is internally consistent — IC alone lifts no occlusion, so the plate takes
its nominal alpha and the retention is acting on the plate it was fitted against
— and it is not a regression against 0.20.0, which had no operator to stand
down. What it is, is **unmeasured**: macOS 27 decoupled the two switches
(`apps/reference-apple/scenes.json`, the `-increased-contrast-` entry: all seven
of that profile's runs attested `increaseContrast=1` with `reduceTransparency=0`),
and the profile this wave's beds actually read is the **COUPLED** one, whose
occlusion IS lifted. The decoupled macOS 27 increased-contrast bed has never been
read against vitrea at all — `compare` cannot tell the two contrast states apart
from the field it picks them off, which is this tracker's own standing entry.

**And there is a design question under it, not only a measurement gap.**
Increase Contrast's own consequence in §Accessibility is
**`ambientTint: "reduced"`**, documented as the material's colour cast picked up
from its backdrop — which is literally what this leaf restores. A preference that
asks for less ambient tint arguably asks this operator to back off, and nothing
in the runtime connects the two: `bodyChromaRetentionUnderPolicy` reads the
occlusion axis and never looks at `ambientTint`.

**The fix shape**: read the decoupled increased-contrast bed against vitrea (it
needs `compare`'s flag fixed first), then decide whether the retention should
read `ResolvedMaterialPolicy.ambientTint` as well as `occlusion`. The second half
is a policy decision and should be made on the reading rather than before it.

---

## Shared receded documents across superseded active generations — CLOSED W36 G1 (2026-09-24)

The W33-to-W36 split initially refused because W33 reused W32's receded bytes:
`45acb6d916b9` and `4e68f81869f6` already aliased W32 holders. One receded difference
can belong to several active generations, while an active hash still names one file.
The tool now records `sharedReceded` without repointing historical aliases, verifies
the prior holder's bytes and receded metadata before writing, and renders the sharing
in its generated README. Six synthetic apply tests cover sharing and refused active
or corrupt-holder collisions; all seven prior classifier tests remain green. The
13 historical entries and 24 aliases remain byte-identical. No capture is repeated.
Evidence: §5.179, `index-history-preservation.json`, `shared-receded-{red,green}.txt`.
This closes the sharing limitation, not the separate attribution-enforcement debt below.

---

## Two superseded-index entries name the reading gate as the moving one, and a third was corrected as it was written (W31 G4, 2026-09-21) — NARROWED 2026-09-21 (W32 G0b): the documentation is true, the refusal is not written

*Named by W31 G3c's Deferred list and by its review's NB5 (claims §5.164 §13).*

`results/superseded/index.json`'s own `claimsFields` note says of
`readUnderClaims` and `movedUnderClaims` that "they are never the same gate", and
`split-generation.py` **documents that rule without enforcing it**. Three entries
have been written with the two equal. One — `e2fa07589d99.json` — was corrected
by hand as it was written. Two are committed evidence and are not edited:
`880ab1e31450.json` and `d0c389d70456.json` both read `c9a §5.164` for rows W30
G3b READ under §5.159b.

The practical cost is small and real: a reader tracing where a generation came
from gets the mover's section for both halves, so the provenance chain has a
gap exactly where the split exists to record one.

**Beside it, a byte-churn note.** W31 G3c's split re-emitted the index's
pre-existing entries with `§` HTML-escaped — content-identical, so nothing
recorded changed value, but the diff shows every entry as touched, which makes a
review of a split read every line instead of the new one.

**The fix shape**: `split-generation.py` refuses `--read-claims` equal to
`--claims` (the one legitimate exception is a gate that reads and supersedes in
one run, which the rule says does not happen, so the refusal can be absolute),
and writes the index with `ensure_ascii=False` so a re-emit is a no-op on the
entries it is not changing.


**Half closed: the docstring now describes what the script enforces**, which is
that `apply` requires both `--claims` and `--read-claims` so neither can be
defaulted or inherited, and states plainly that it does NOT check they differ
(claims §5.167 §5). The two committed entries each carry a `$comment` beside their
recorded fields naming W30 G3b (§5.159b) as the reading gate and W31 G3 (§5.164)
as the mover; nothing recorded is rewritten and the diff is exactly two
insertions. `split-generation.py readme` after the annotation is a no-op and
`plan` still reports 1,833 / 1,833 / 0.

**What is left is the refusal itself**, unchanged in shape: `apply` refusing
`--read-claims` equal to `--claims`, absolutely, since the one exception the rule
contemplates is a gate that reads and supersedes in a single run and the rule says
that does not happen. W32 G0b ran no split, and a refusal first exercised on a
real split is a refusal nobody has run — so it belongs to the next gate that runs
one, together with the `ensure_ascii=False` byte-churn note below.

**And a second place the same sentence lives, which that gate must move with it.**
`split-generation.py`'s `claimsFields` LITERAL is written into `index.json`
verbatim by every `apply`, and it still says "They are never the same gate". The
docstring correction does not reach it. Whoever adds the refusal moves the literal
and the committed `index.json`'s copy of it together, or the next split writes the
claim back over the annotations.

**WIDENED 2026-09-21 (W32 G1 review closure; claims §5.168 §10, finding N-7): the
planned refusal is not enough, because the reader is per GENERATION and the flag
is per RUN.** W32 G1's split moved two generations in one invocation — 479 light
rows and 247 dark ones — and they were read by two different gates: the light by
W31 G3c under §5.164 §13 and the dark by W31 G3 under §5.164, four hours apart on
the same day, which the capture timestamps in each entry show. `apply` takes ONE
`--read-claims`, so no value of it could have been right, and the gate passed the
mover's own section for both. A refusal of `--read-claims == --claims` would have
caught that particular symptom and would not have caught the disease: a run whose
two generations were read by two gates neither of which is the mover passes the
refusal and still writes one wrong entry. **`--read-claims` has to be per
generation** — a mapping from the file being written to the section that read it,
or derived rather than passed, since the script already knows each generation's
document hashes and the ledger records which gate read at which bytes. The two
entries W32 G1 wrote were corrected in place before they merged, which is
available exactly once per entry and is not a mechanism.

---

## The two dark macOS 27 documents' `$comment-sha-history` carries a wrong parenthetical (W31 G4, 2026-09-21)

*Named by W31 G3c's Deferred list; finding N9 of its review (claims §5.164 §13).*

`seal.ts`'s history template wrote "the reading under rule 2 (the plain resolved
fingerprint)" into all four macOS 27 documents. **Rule 2 is not the plain
fingerprint** — it is the fingerprint with every identity-table entry dropped,
which is the whole content of W31 Decision Log 1 (a). The two LIGHT documents
gained a `$comment-sha-history-correction` in the same edit as W31 G3c's dated
line; the two DARK documents did not, because they were not re-read in that
branch and a correcting comment would move their file hashes and empty the dark
half of the macOS 27 bed out of every bound until rows at the new bytes exist
(contract X10).

So the defect is a sentence in two committed documents, and the cost of fixing it
in isolation is a canonical read of two profiles.

**The fix shape**: whoever next re-seals or re-reads the dark pair carries the
correction in the same merge. `seal.ts` in
`results/2026-09-21-w31-g3c-accessibility-gate/` is the corrected template and
will not write it again — it is committed and was deliberately NOT run at that
gate.

---

## The holdout configuration log is a cross-gate ledger living inside one gate's evidence directory (W31 G4, 2026-09-21) — CLOSED 2026-09-21 (W32 G0b)

*Named by W31 G3c's Deferred list (claims §5.164 §13).*

W31 Decision Log 1 (b) is enforced by artifact: `configuration.py record` refuses
a second holdout read at identical document hashes unless the source hash moved
and a non-fit reason is named. The refusal reads `configuration-log.json` — **not
the world** — which is what makes it survive a worktree, a rebase or a machine.

But every script under `results/` is copied per gate by convention, and **a copy
starts with an empty log**, which would make the refusal blind to every read
before it. W31 G3c avoided that by running W31 G3's copy in place and appending
to its log. The next gate has the same choice and no rule telling it which to
make, and the two options are not equivalent: one keeps the rule and one silently
retires it.

**The fix shape**: move the log out of any one gate's directory —
`packages/calibration/results/holdout-configuration-log.json` — and make
`configuration.py` read and append to that path wherever the script itself lives.
A cross-gate ledger should not be a file a copying convention can fork.


**Closed, and the closure took the fix shape's location and not its name.**
`packages/calibration/results/holdout-configuration/` holds `configuration.py`,
the log and a README, and it is the one location every canonical holdout read
records to (claims §5.167 §1). A directory rather than the loose
`holdout-configuration-log.json` this entry proposed, because the script and the
log have to travel together: a script reaching back to a log it does not sit
beside is the same fork with one more step in it. The log is **seeded byte for
byte** from W31 G3's, so the two reads that exist carry across unchanged, and
`test/w32-holdout-configuration.test.ts` asserts the seed field by field against
the G3 file — which stays byte-identical where it is, as that gate's witness.
Five unit cases exercise the refusal over a synthetic repository, including that
a refused read appends nothing.

---

## The holdout configuration's source list is narrower than the render by fifty files, and widening it is a ruling rather than an edit (W32 G0b, 2026-09-21)

*Measured at W32 G0b while moving the ledger; claims §5.167 §2, evidence
`results/2026-09-21-w32-g0b-evidence-tools/source-list-closure.txt`.*

W31 Decision Log 1 (b) defines a frozen configuration as *(the shipped document
bytes, the renderer's material-affecting sources)*, and the second half is an
enumerated list of 14 files — W31's charter verbatim, acceptance clause 6. It is a
list rather than a tree for a good reason: a hash over everything would move on a
comment in a test and say nothing about the material.

**It is also incomplete, and it always was.** Following the local import graph out
of the list's five TypeScript entry points reaches 50 further files, of which
around twenty can move a capture's pixels at unmoved document bytes:
`analysis.ts`, `silhouette-tone.ts`, `instances.ts`, `backdrop-fit.ts`, `color.ts`,
`pyramid.ts`, `pyramid-plan.ts`, `render-model.ts`, `css-tier-layers.ts`,
`css-tier-shadow.ts`, `backdrop-tone.ts`, `refraction.ts`, `tint.ts`,
`vibrancy.ts`, `material-document.ts`, `macos27-profile.ts`, `dark-profile.ts`,
`receded-profile.ts`, `window-activation.ts`, `media-policy.ts`. It is a lower
bound: a package-boundary import is not followed, so core's policy and tier
resolution are outside the count as well as outside the list. `renderer-bridge.ts`
holds no material constant and no material arithmetic but decides which material
reaches the renderer, so it is one of the fifty in the routing sense.

So a fit that moved a constant out of a document and into, say,
`css-tier-layers.ts` would leave the configuration hash unmoved and the artifact
would not see it. The consequence is bounded — the refusal's FIRST half, the
document hashes, catches every fit that moves a document, which is what a fit
normally does — but the second half is weaker than its name.

**Why W32 G0b did not widen it, and why the next gate should not either without a
ruling.** The refusal compares today's `sourceSha256` against a LOGGED one, and a
hash taken over a different enumeration is not a different hash but an
incomparable one. A widened list would therefore report "the sources moved" at
every later read forever, which retires the rule more thoroughly than the fork
the ledger's move just prevented. Changing what a configuration IS is Decision Log
1 (b)'s subject.

**The fix shape**, and it is a decision before it is an edit: either a declared
list that a unit case CHECKS against the import closure, so an added module is a
red test rather than a silent gap, or a closure hash with a declared ignore list.
Either way the rule's version has to be recorded on the entries taken under it —
`sourceListSha256`, added at W32 G0b, is the place for it — so the two eras of
hashes are told apart instead of compared.

---

## `interiorStdDevWeb` moves 5.69 % on a standard light cell off the declared bed, against a 2 % stop on it (W31 G4, 2026-09-21)

*Named by W31 G3c's Deferred list; finding N12 of its review (claims §5.164 §4,
§13).*

W31's structure stop bounds `interiorStdDevWeb` to within 2 % of its pre-fit
value on the declared bed's 26 cells, and it is met on all of them at a worst of
**1.317 %** — adopted at W31 G4 as `M2`. Off that bed the same quantity moves
further: the worst macOS 27 WebGPU row is 2x light
`photo__capsule-button__rest-tint-orange-half` at **−5.69 %** (0.020154 →
0.019006), on a standard light profile.

**The cause is understood and is not the operator.** The movement scales
inversely with the cell's own spread — −1.32 % at `sd` 0.0187, −0.74 % at 0.0175,
−0.04 % at `sd` 0.0680 — which is the capture's 8-bit quantisation: a chroma
change moves which bin each channel lands in, so the luma reconstructed from
three 8-bit codes jitters by a fixed fraction of a code, and a fixed absolute
jitter is a larger fraction of a smaller spread. The operator holds linear luma
to under two ULP of a double in the law and to a sixth of one code on a hardware
adapter.

What makes it an entry rather than a footnote is scope: **a stop stated over a
bed is a statement about that bed**, and M2 is now an adopted row over 26 cells.
A wave that widens the bed — the surface-conditioned retention needs more spans
on the dark side, so one will — meets this reading first, and will have to decide
whether 2 % is a bound about the material or about the raster.

**The fix shape**: state the structure clause against a floor that scales with
the cell's own spread, or read `interiorStdDev` off a higher-bit-depth capture
where the quantisation is not the signal. The first is cheaper and is probably
right; the second is what would settle whether 1.317 % is anything at all.

---

## 0.21.0's headline operator has no stage on the demo that shows it (W31 G4, 2026-09-21)

*Found by W31 G4's own sheets (claims §5.165 §4; `eye.md` §8;
`sheets/apple-macos-27.0-2x-dark-standard-glass0.5.png`).*

`bodyChromaRetention` restores the backdrop's chromaticity into the body, so it
is the exact identity over an achromatic backdrop. The demo has one stage whose
backdrop has hues in it — the material stage's multi-lobe `oklch` bloom — and on
neither scheme does it demonstrate the operator:

- **Dark: there are no lobes.** `StageBackdrop.tsx`'s `DARK_GROUND` carries
  **`field: 0`**, with the reason written beside it: the lobes composite with
  `multiply`, which is how colour is put into a LIGHT ground, and multiplying a
  light lobe onto near-black is very nearly nothing. So the dark stage is a
  near-black paper with a white graticule and no chroma at all — **and the dark
  scheme is the endpoint this wave moved most**, ratio (i) 0.3332 → 0.9994.
- **Light: the plates are in the wrong corner.** The bloom is centred right of
  the stage and the three plates are stacked at the left, over ground that is
  nearly the base `#dde6eb`. The 112 px plate picks up a faint warm-green cast at
  its right edge; the 40 px plate picks up almost nothing.

Neither is a defect in the operator and neither was a mistake when it was made:
the dark field is 0 for a measured accessibility reason that
`apps/demo/e2e/contrast.spec.ts` guards, and the plates' position is the size
sweep's own composition.

**The fix shape**, and it is a design decision before it is an implementation:
give the dark scheme a chromatic ground it can carry — lobes composited so they
ADD on a dark ground, at a chroma the contrast case still passes — or move the
sweep's surfaces over the bloom's centre, or give the operator a stage of its own
the way the tone response has one. What the site says about it today is a number
rather than a picture: the calibration readout prints the chroma-to-structure
pair per cell (claims §5.165 §4).

---

## `mid-chroma-solid`'s hue ROTATION was found before the fit and has not been looked at since (W31 G4, 2026-09-21)

*Found by W31 G0 (claims §5.161 §8); left open by W31 G3 (§5.164 §9) and by W31
G4 for the same reason.*

On `mid-chroma-solid` — sRGB (213, 2, 255), the W27c chroma anchor — G0's sheets
record the reference's body as a clean lighter pink and vitrea's as a lavender:
desaturated **and rotated toward blue**. `tintHueShift*` has never been read on
those cells.

It has not been re-read at the fitted material by anyone, and the reason is
structural rather than an oversight: **`mid-chroma-solid` is a PROBE scene**, the
canonical read is calibration + validation + the pitch ladder, and contract X1
allowed neither W31 G3 nor W31 G4 a capture of its own. So the canonical
`web-captures/` tree carries no macOS 27 `mid-chroma-solid` raster at all and the
last look anyone has taken at it is G0's, at the pre-fit material, in
`results/2026-09-21-w31-g0-chroma-cut/sheet__*__mid-chroma-solid__*.png`.

**Corrected beside, 2026-09-21 (review closure; claims §5.165 §9, finding R2):
only half of that is structural.** The canonical tree really carries no raster, so
no sheet could come from the tree. But **X1 is the freeze** and says nothing about
capture, **X5** bars NATIVE capture only, **X6** contemplates scratch captures by
name, and **G0 made this scene's sheets from a scratch web re-capture** inside the
same wave. Both gates could have run a `--set probe` capture and neither did. The
entry stands; its reason is now "declined", not "forbidden", and clause 7's
`mid-chroma-solid` sheets are a recorded miss rather than an impossibility.

**And the rotation is not the only thing wrong with this scene** (2026-09-21,
review closure; finding R4). It is also **LEVEL-broken**, which is tracked nowhere
else and is the harder half. Its 1x dark inactive cell reads `interiorMeanWeb`
**0.0761 against a native 0.2856** over a backdrop of 0.2141 — the reference's
receded body is BRIGHTER than what is behind it and vitrea's is a quarter of it —
and its 1x light rest cell reads **0.6134 against 0.3957**. Since the chroma ratio
scales as `(level)^(−2/3)` exactly, those bias it by **2.415×** and **0.75×**
(claims §5.161 §3 (b), as its own closure corrects the dark figure at N6), and the
W31 charter's Surprises rule that the anchor **"must not carry the tolerance until
its level agrees"**. A probe capture answers the rotation and does not touch this;
a wave that reads the probe set should expect the level miss still to be there,
and closing it is a separate fit on a separate lever.

What is known beside it: on the `photo` cells the restored hues sit where the
reference's do at every span and both schemes, which is **consistent with** a
rotation that was the plate's rather than a hue-mapping error. Neither G3 nor G4
claims that, because the cell that would decide it was not read.

**The fix shape**: read the probe set at the shipped documents — it is a
`--set probe` run, no new fixture and no native capture, and no contract stands in
its way — and put the sheet beside G0's. If the rotation is gone it was the
plate's and that half closes; if it survives, `tintHueShift*` is the lever and it
has never been fitted. The level half needs its own reading and does not close
with the sheet.

---

## The level stop the chroma statistic depends on is a declared number and not an adopted row (W31 G4, 2026-09-21)

*Found by W31 G4's own eye (claims §5.165 §2; `eye.md` §3).*

`R` scales as `(level)^(−2/3)` exactly, so a cell whose interior level misses the
reference's carries that miss into the chroma statistic. W31 declared a level
stop as a number — `|interiorMeanWeb − interiorMeanNative| ≤ 0.055` per cell on
both tiers, and that quantity growing by no more than 0.005 from its pre-fit
value — and W31 G4 adopted `M1` (the ratio) and `M2` (the structure) and **not
that**.

The consequence is visible before it is arithmetic. On 1x dark
`photo__capsule-button__rest`, the bed's lowest cell at `R` 0.8213, vitrea's
capsule is not only greyer than the reference's but visibly **darker**, and the
two are not separable by eye. That cell carries the bed's largest level miss
(0.0457 at 1x, 0.0493 at 2x) and is the dark bed's worst 1x-against-2x
reproducibility pair at 19.41 % — the spread is the level miss speaking through
the exponent. *(2026-09-21, review closure; claims §5.165 §9, finding N6: **19.41 %
is the PRE-fit figure**. On the same cell after the fit the pair reads **25.10 %**
normalised over the pair's mean and **28.70 %** over `R₁ₓ` — claims §5.164 §12 as
its own closure corrects it. The number above is not restated; the post-fit
readings are what a wave picking this up should size the work against, and they
make the case stronger rather than weaker.)* M1's own band was widened to absorb
it and M2 does not reach it: M2 bounds the structure, not the level.

So the material axis now has two adopted rows and the quantity that biases both
of them is gated by nothing. Nothing else gates it either:
`interiorLevelRatioGpuOverCss` is a cross-tier ratio, blind to both tiers moving
together, which is exactly why §5.161 §7 (c) had to declare a number in the first
place.

**The fix shape**: adopt the level clause as a third material-axis row, on the
same bed and in the same shape as M1 and M2 — the cut already carries
`interiorMean{Native,Web}` per cell, so it is a clause and not a capture. What has
to be decided first is the bound: 0.055 is the worst cell rounded up, so adopting
it as stated would be green today and say very little, which is the same choice
W31 Decision Log 3 (a) faced on M1's ceiling and answered by taking a number that
declares the outliers missed.

---

## `standard-row-identity-matrix.txt` has no generator committed beside it and under-reports what it enumerates (W31 G4, 2026-09-21)

*Found by W31 G3c's independent review, folded at W31 G4 (claims §5.165).*

W31 G3c's `standard-row-identity-matrix.txt` is the field-by-field evidence for
the strongest claim of that gate — that the accessibility stand-down moved
nothing on any standard row. The claim is true and the review verified it
independently and **stronger than the file states: 411 standard rows, 255,750
leaves, none moved.** The artefact that records it has four defects:

- **No generator is committed beside it.** Every other checker in that directory
  has its script; this one is output with no input.
- It enumerates **12 of the 32** moved accessibility rows with no truncation
  notice, so a reader counting from the file gets 12.
- It **under-lists the moved fields per row** — 6 where
  `texture/calibration/photo__capsule-button__inactive` moved 29.
- It prints profile keys with the **first character chopped**.

Nothing recorded is wrong; the file is committed evidence and is not edited. What
is wrong is that the artefact is weaker than the claim it supports and cannot be
regenerated to check it. W31 G4's `accessibility-identity.py` takes the same
claim by a different route with its generator committed (6,855 readings on the
two accessibility profiles, none moved), which covers one half of it.

**The fix shape**: commit the generator — or extend
`accessibility-identity.py`'s selection to the standard rows, which is a change
to one set literal — and print counts rather than a truncated enumeration.

---

## The unsampled-DOM path restores the body's chroma toward the DECLARED tone, not toward the real backdrop (W31 G4 review closure, 2026-09-21)

*Found by W31 G3c's independent review and corrected by its closure (claims
§5.164 §13, finding N7); carried here 2026-09-21 because §5.165 §9 finding R3
found it recorded in no tracker entry and no Deferred item, with its ledger
pointer aimed at a section that does not carry it.*

`body_chroma_retention` restores the composited colour's chromaticity toward the
BACKDROP's. On the unsampled-material path nothing sampled a backdrop, so the
shader is handed `dom_material_backdrop()`, which has two modes:

- **Mode 1** — a group with no declared `backdropTone` — returns a fabricated
  NEUTRAL at the declared reference luminance. The review read this and called
  the operator a desaturation. It is one in form and **the identity in effect**:
  the plate is `solvedNeutral` and the fabricated backdrop is a grey, so both
  endpoints of the mix coincide and **zero bytes move**, measured at three
  retentions up to 1.
- **Mode 2** returns `ou.toneColour.rgb`, the tone the page DECLARED, which can
  carry a chromaticity. Here the operator is live and it restores toward a colour
  the page asserted rather than toward what is actually behind the surface.
  Measured: interior chroma **0.066 → 0.334**, with the **gamut clamp already
  binding at the shipped retention**.

So a page on the unsampled path whose declared `backdropTone` is not its real
backdrop now gets a body carrying the hue it was told about, at a third of full
chroma, where before 0.21.0 it got a grey. Nothing is wrong in the shader: the
operator does what it says over the backdrop it is given, and on this path the
declared tone IS the only backdrop the runtime has. What is undecided is whether
restoring toward a declared tone is the right behaviour at all, and the gamut
clamp binding at the shipped value says the question is not academic.

`packages/renderer-webgpu/e2e/gpu/w31-unsampled-dom-chroma.spec.ts` is the
evidence and pins both modes.

**The fix shape**: decide the policy first, because the code follows it in one
line either way — stand the retention down on the unsampled path (it is already
an exhaustive switch on the occlusion axis, so a second condition is cheap), or
keep it and document that a declared tone is a colour claim and not only a level
claim. Whichever is chosen, the clamp wants a reading beside it: at the shipped
retention it binds, so the fitted fraction is not what that path draws.

## Two `MISSED_27_ROWS` entries cannot be decided at all, because the perceptual axis carries no region-restricted ΔE (W32 G0, 2026-09-21)

`MISSED_27_ROWS` holds five shadow-era rows today, and two of them are
`photo__rrect-lg__rest :: oklabDeltaEP95` on the CSS tier, 1x dark (0.20095
against ≤ 0.18) and 2x dark (0.19474 against ≤ 0.19). W32 G0 decomposed all five
for what the outer shadow could reach and could decide three of them: two of the
SSIM rows because the axis carries `ssimOutside` and `ssimOutsideWindows`, so the
share of the metric the exterior owns is a number
(`results/2026-09-21-w32-g0-exterior-cut/stops.txt` §7, claims §5.166 §6), and
the reduced-transparency row because `ssimOutside` IS the exterior. **The two ΔE
rows it could not decide, and the reason is structural rather than a shortfall of
effort: `oklabDeltaEP95` is a percentile over the WHOLE cell and the axis reports
no ΔE restricted to any region.** Whether the cell's top five per cent of colour
error lives in the exterior, in the rim or in the body is not in any committed
field, so "reachable through the shadow" has no derivation and the honest verdict
is *undecidable from the committed fields*.

What makes it worth an entry rather than a shrug: the same two rows are the ones
a shadow wave is most likely to want to claim, because their WebGPU-tier siblings
on the same scene cleared at W31 G3 and these two are the CSS tier's decline
rather than the material's (claims §5.164 §5; the comment above them in
`test/adopted-thresholds.test.ts`). A wave that claimed them through the exterior
would be claiming something nothing on this bed can check, and a wave that
declined to claim them cannot say whether it was right to.

**The fix shape**, and it is small: the perceptual axis already computes its SSIM
three ways over the silhouette, the band and the outside
(`ssimInterior` / `ssimBand` / `ssimOutside`, with window counts). The same
partition applied to the OKLab difference gives
`oklabDeltaEP95{Interior,Band,Outside}` and their pixel counts, which is one pass
over a mask the axis already has. It is a schema addition, so it costs a bump and
a re-read of the bed to populate, which is why W32 does not take it: X7 forbids a
schema change in this wave and the wave's own read is already committed to the
current one. The right moment is the next wave that re-reads the whole bed for a
different reason.

Until then: no wave claims either row through the shadow, and `MISSED_27_ROWS`
carries them as missed with the reason recorded here.

## Apple's active reach on macOS 27 depends on the backdrop, and nothing separates the material from the instrument (W32 G0 review closure, 2026-09-21)

*Found as an incidental by W32 G0's independent review and measured by its closure
(claims §5.166 §4 and §10, finding N17). Evidence:
`packages/calibration/results/2026-09-21-w32-g0-exterior-cut/extents-by-backdrop.py`
and its committed output — a read of `results/matrix.json`, no capture, no fit.*

`extentBelowNative` — the axis's walk outward from the silhouette to where Apple's
render rejoins its backdrop — varies with the BACKDROP on macOS 27 at every span,
not only at the thin ones where a luminance keying is already expected. Over
twelve backdrops on the four standard beds it reads **16.0–18.5 CSS px at span 96**
and **25.0–28.8 at span 128**, a range of 14 % of the span's own median at both,
with `light-solid` shortest and `checkerboard-lc16` longest at each — the same two
backdrops in the same order, which is what makes it a reading rather than a
scatter. Inside the thin regime the same figure is 12 % at span 44 and 41 % at 32.

What is undecided is **which of two mechanisms it is**, and the two are observationally
identical on this statistic:

- **Apple's material conditions the shadow on the backdrop**, beyond the thin
  regime's keying. Then a single falloff triple cannot describe the bed and the
  material is missing a term.
- **The estimator is conditioned on the backdrop's contrast.** An extent is a
  threshold crossing and a backdrop with less light to remove crosses sooner, so
  a shorter reach over `light-solid` would be the instrument and not the material.

Both predict the table. Separating them needs the TRANSMISSION PROFILE rather than
the extent — the per-band `a` against distance, which does not depend on a
threshold — and that is a fit, which G0 does not do.

**The fix shape**: at G1's first round, read the fitted residual per backdrop at
each span rather than pooled, on the profile and not on the extent. If the residual
is flat across backdrops the dependence was the estimator and this entry closes on
that measurement; if it tracks the backdrop's own luminance or contrast statistic —
which the analysis pass already computes per source — then the material is missing
a term and the entry becomes a charter item rather than debt. Either way the
reading is cheap once a fit exists, and G1's verdict carries the per-backdrop
residual regardless (claims §5.166 §4).

## `@vitreajs/vitrea-react`'s README documented an import that does not exist, and the capability behind it is package-internal (W32 G2, 2026-09-22)

*Found while building the `/laws/` shadow stage (claims §5.169 §4), which needed
exactly the thing the README says an app can have. Corrected in the README at
0.22.0; the export itself is not made.*

`useGlassRootHandle()` returns the `GlassRootHandle`, which carries
`materialProfileDocument` — the document the ROOT selected, available before the
mount effect has built the runtime, which is what lets `GlassToolbar` derive its
gap from its own material rather than from the package default. The React
package's README has told applications to reach it the same way since 0.20.0:

```tsx
import { useGlassRootHandle } from "@vitreajs/vitrea-react";
```

**`packages/react/src/index.ts` exports no such symbol.** It exports the
`GlassRootHandle` TYPE and `useGlassRoot`, which returns `GlassRoot | null` — the
runtime, not the handle — so that import has thrown since it was written, in the
0.20.0 and 0.21.0 READMEs as published, and the capability is reachable only from
inside the package. Nothing about `GlassToolbar` is wrong; what was wrong is the
claim that an app can do what it does.

**What an app does today**, and the `/laws/` stage is the worked example: read
what DREW rather than what was selected. `useGlassCapabilities(groupId)` gives the
group's resolved state, whose `materialDocument` carries `resolvedMaterialSha256`
over the fully resolved material, so a layout matches that digest against the
endpoints of the document it built its root with and refuses to name one when it
matches none. That is a stronger statement than the selection — it is the material
on the screen — and it is what `endpointByDigest` in `apps/demo/src/laws/law.ts`
does. What it cannot do is produce a number on the FIRST render, before a frame
has resolved a group; the toolbar's whole reason for reading the handle is that it
must.

**The shape of the work**, and why it is not done here: `export { useGlassRootHandle }`
from `packages/react/src/index.ts` is one line and makes the README's original
paragraph true. It is a public-surface addition and this release is a fidelity
one, so it belongs to a wave that can state the API and test it — with the
question that comes with it, which is whether an app should be given the
SELECTION at all when the honesty core's whole argument is that a consumer reads
what drew. The two answers are different APIs: the handle, or a
`root.material`-shaped reading available before the first frame.

---

## B3 is green by cancellation, and the wave that fits the exterior breaks it (W32 G1, 2026-09-21)

*Measured at W32 G1 (claims §5.168) across seven rendered rounds of the same bed.
Evidence: `packages/calibration/results/2026-09-21-w32-g1-shadow-fit/b3-window.py`
and its committed output, plus `departure-stat.txt` in each round's directory.*

**B3** — `|meanDepartureWeb − meanDepartureNative|`, arithmetic mean over the
calibration + validation cells of all six macOS 27 profiles, WebGPU tier,
≤ 0.00035 — is a STOP and not an adopted row (W30 Decision Log 3 (a); §5.159 §7
records that it stopped nothing). It read **0.00034** at the shipped documents
and reads **0.00072** at the fitted ones, and neither number is a statement about
the shadow, because the same statistic over the pixels C1 is stated on goes the
other way by a factor of twenty: **0.00122 → 0.00006**.

| | whole exterior — B3 as declared | over the admitted bands, 3–48 CSS px |
| --- | ---: | ---: |
| shipped documents | 0.00034 | 0.00122 |
| the recede stood down | 0.00054 | 0.00053 |
| + the outset fitted | 0.00063 | 0.00020 |
| + the anchors solved | 0.00072 | 0.00006 |

**Why the two disagree, measured rather than argued.** B3 integrates the WHOLE
exterior, which includes the `0-3` band every form of C1 excludes. In that band
two things live that are not the shadow: on the ACTIVE pose vitrea's own body
over-fills its declared contour by 3.5–4 CSS px against Apple's ≤ 1 (§5.62), so
`Δa` there runs **+0.089 to +0.151** — vitrea removing far LESS light than
Apple — while in 3–48 px it ran −0.008 to −0.019, removing MORE. The two errors
had opposite signs and comparable integrals, so B3's mean sat near zero. Fixing
the shadow removes one of them and leaves the other standing alone. On the
INACTIVE pose the same thing happens for a different reason: Apple's entire
receded exterior is one device pixel of dark stroke at the contour (§5.166 §7),
which is a rim term, and vitrea's receded exterior after Decision Log 2's
stand-down is nothing at all.

**Mechanism corrected beside, W33 G0, 2026-09-22 (§5.170; §5.169 §10 B2).** The
paragraph above and this entry's later “silhouette term” wording are superseded on the27 bed:
the positive `0–3` residual is the native's undrawn contour stroke on BOTH poses, not a
3.5–4px web-body over-fill. Its sign is native darker, and its width one DEVICE pixel. The
whole/admitted-band numbers and the cancellation argument remain the measurements they were;
§5.62's26.5 measurement is not withdrawn. The user already ruled the admitted-band form at
W32 DL3(a), as this entry's closure below records; no second re-statement is pending here.

Decomposed by pose over B3's own 166 cells: the ACTIVE half goes 0.00029 →
0.00064 and the INACTIVE half 0.00039 → 0.00080, and the inactive half moved
before a single length did — round R stands the recede down at the shipped active
material and B3 is already 0.00054 there.

**So the stop was unattainable once Decision Log 2 was ruled, and the arithmetic
says so** (added 2026-09-21, W32 G1 review closure; claims §5.168 §10, finding
N-2). The pooled mean is over **85 active and 81 inactive** cells. The inactive
half alone after the stand-down contributes 81 × 0.00080 / 166 = **0.000390**,
which is already above 0.00035 — B3 fails with a PERFECT active half. And
without the stand-down, the fitted active half beside the pre-fit inactive one
gives (85 × 0.00064 + 81 × 0.00039) / 166 = **0.000518**, also above it. Each
half breaks it alone. No choice of anchors, lengths or fit order kept this stop,
which is why the entry is a re-statement question and not a regression.

**So the stop cannot separate a shadow from a rim**, and it is measured on a bed
where one pose's whole exterior IS a rim. Both terms it now reads are outside
what W32 X3 lets that wave touch: the body's over-fill is a silhouette term and
the receded hairline is a rim term, and this wave's Deferred list names the
second by name.

**The fix shape** is a ruling and not an edit, which is why it is here and not
done: B3 is re-stated over the **admitted bands** — the same window the anchors
are solved on and C1 is read on, where the statistic reads 0.00006 — or over the
ACTIVE pose with the `0-3` band excluded, with a bound re-derived on the
generation that adopts it by the rule W32 clause 2 used for C1. Either is a
re-statement of an adopted stop and belongs to the user through a wave's Decision
Log; W32 G1 records the numbers and re-states nothing (X4). Until it is ruled,
a later wave reading B3 at 0.00072 should read `b3-window.py` beside it or it
will conclude the exterior got worse.

**RULED (a) by the user 2026-09-22 and executed at W32 G2 — this entry is
CLOSED** (W32 Decision Log 3; claims §5.169 §2). B3 is re-stated over the
**admitted bands** (3–48 CSS px, per cell per direction by W32 G0's clearance
rule), **both poses**, WebGPU tier, calibration + validation over all six macOS
27 profiles — the same 166 cells, 85 active and 81 inactive, and the same
arithmetic mean — and it stays a **STOP** in W30's sense rather than becoming an
adopted row. Its bound is W32 clause 2's rule applied to the bed at W32 G1's
read: the form reads **0.0000559626** there and rounds up to two significant
figures at **0.000056**, which is 0.07 % of headroom and is a rule's output
rather than a choice. The reader is
`packages/calibration/results/2026-09-21-w32-g2-landing/b3-stop.py`, which prints
the statistic, the bound and PASS/FAIL and exits nonzero on a fail;
`departure-stat.py` runs beside it at the same generation so the superseded
whole-exterior form keeps its last reading (**0.00072**) rather than
disappearing. Two things this closure does NOT do: it does not touch the contour
hairline — Apple's one-device-pixel stroke, un-drawn by vitrea on **both** poses,
which is the quantity the old statement was reading in the `0-3` band and which
has its own entry above and a Deferred item of its own *(re-stated 2026-09-22 at
the same closure, finding B2: this sentence first named two quantities, "the `0-3`
band's over-fill (§5.62)" and "the receded contour hairline", and
`contour-stroke.txt` reads the band's sign directly — it is one rim term on both
poses)*; and it does not make the bound spacious — 0.07 % of headroom means the
next fit gate that moves the exterior at all will have to read this number
deliberately, which is the same thing C1's 1.7 % at span 96 says one row over.
*Corrected beside, 2026-09-22 (same closure, finding N1): C1's 1.7 % is a PRE-FIT
figure and is not a live peer of this 0.07 %.* It is 2x light's span-96 reading on
the generation C1 was declared against; at the shipped bytes that cell reads
**0.00088** — 79 % of headroom — and the tightest of C1's twelve rows is 2x dark at
span 128 with 6.9 %. B3's 0.07 % is a reading at the shipped bytes. The sentence
holds of B3 alone.

---

## M2's reference generation is frozen at W31's pre-fit while its subject keeps moving (W32 G1 review closure, 2026-09-21)

*Opened by W32 G1's independent review (claims §5.168 §10, finding B-2), on the
first miss M2 has taken since adoption.*

M2 bounds `interiorStdDevWeb` to within **2 %** of the value the same cell read
on **W31's pre-fit generation** — a constant carried in W31 G4's committed
`chroma-cut.json` as `interiorStdDevWebPreFit`, one number per cell, which does
not move when the material does. The reference is therefore fixed while the
subject is not, so the delta is **cumulative across waves**: W31 spent 1.317 %
of the budget on one cell and W32 G1 spent the rest of it, reaching 2.775 %
without either wave moving the quantity by more than one and a half percent of
its own value.

That is not a defect of either wave. It is what a bound stated against a frozen
generation does: **every wave that touches the render spends from a budget that
is never refilled**, and on the cell with the smallest spread the budget is the
smallest in absolute terms. A third wave that moves this cell by half a percent
fails M2 whatever direction it moves it in, and the failure will say nothing
about that wave.

**The ruling belongs to the user**, which is why this is an entry and not a fix.
Two forms, and they are not equivalent:

1. **Re-baseline per wave** — M2 reads against the generation the previous gate
   sealed, so the bound is "this wave did not move the structure by 2 %". That
   makes the row a per-wave regression stop and gives up the cumulative claim
   entirely: eight waves of 1.9 % would pass while the structure moved 16 %.
2. **Declare the budget cumulative and say so** — keep the frozen reference,
   and state in the row's own text that a miss is the accumulated distance from
   W31's pre-fit material rather than a statement about the wave that records
   it, with the recorded-miss path carrying each cell's history.

The second is the honest one and the first is the useful one; a third form —
both rows, one bounded per wave and one recorded cumulatively — costs a second
reference per cell and is probably what a wave that has to choose should
propose. Nothing is decided here.

*See also the entry above on `interiorStdDevWeb` moving 5.69 % off the declared
bed: that one asks whether 2 % is a bound about the material or about the
raster, and this one asks what it is measured from. Both have to be answered
before M2's next miss means anything.*

**RULED at W32 Decision Log 4 by the user 2026-09-22 and executed at W32 G2 —
this entry is CLOSED, in form 1 with form 2's claim moved to the ledger** (claims
§5.169 §3). The reference is re-baselined at **each gate that adopts a material
change**: `chroma-cut.py` in that gate's directory names the generation the gate
read (here `superseded/49490eb9ff7a.json` light and `b5714a866288.json` dark,
resolved through the index), the field is `interiorStdDevWebReference` and the
guard that proved the old reference PRE-dated the chroma instrument is inverted
rather than dropped — the new reference is a generation read AT the leaf, so a
baseline row that carries no chroma field is refused. The **2 % does not move**,
and W32 G1's miss closes by re-baseline: the cell reads **−1.477 %** per wave
against **−2.775 %** cumulative, and its `MISSED_27_ROWS` entry is retired with
its reading kept in the comment where the entry stood.

What the ruling gives up is form 1's own cost, stated where it can be seen: eight
waves of 1.9 % would pass while the structure moved 16 %. What replaces it is
**not a bound but a record** — the ledger's per-wave table, first written at
§5.169 §3 from `m2-rebaseline.py`, which prints all 26 cells at three generations
with the per-wave and cumulative columns side by side. **One number in that table
is worth a later wave's attention**: 1x dark `photo__capsule-button__inactive`
reads **+1.966 % cumulative** — 0.034 of a percentage point from 2 % — and it got
there in the same two waves, so the drift the ruling stopped bounding is real and
is already at the old bound on a second cell. A wave that wants the cumulative
claim back adds the second reference per cell that the third form named; nothing
here does.

---

## The optics pass composites the outer shadow into the body's own antialiased edge, and nothing has measured what that costs an interior statistic (W32 G1 review closure, 2026-09-21)

*Opened by W32 G1's independent review (claims §5.168 §10, finding B-2), as the
CANDIDATE mechanism for M2's first miss. It is a hypothesis; the measurement
that would test it has not been run.*

**What is established.** M2's miss is not the silhouette extractor. The material
axis's mask is the NATIVE silhouette by construction (`cli/measure.ts`: `const
interior = nativeSil`), and across the 726 rows W32 G1 superseded and re-read,
`silhouetteAreaNative` moved on **0** while the shape axis's own
`silhouetteAreaWeb` moved on 80; on the miss cell the native area, the web area
and the declared region are all 2000 with an IoU of 1 before and after
(`results/2026-09-21-w32-g1-shadow-fit/b2-mask.py`). The mask is fixed and the
values under it moved.

**The hypothesis.** `packages/renderer-webgpu/src/wgsl/optics.ts` composites the
exterior shadow into the same output as the body wherever coverage is partial —
`shadowAlpha · (1 − coverage)` is added to both the colour and the alpha at the
surface's antialiased contour. Those pixels are INSIDE the declared region and
inside the native silhouette, so an interior statistic reads them. Changing the
shadow therefore changes an interior statistic through the edge ring, with no
mask movement required, and the effect should scale with the ring's share of the
region — largest on the thinnest surface, which is where the miss landed (span
32) and where every other large mover sits.

**The measurement that would test it**, and it needs no capture: re-derive
`interiorStdDevWeb` on the same committed captures over the native silhouette
ERODED by one and by two device pixels, on the miss cell and on a thick control,
at both generations. If the delta collapses as the ring is eroded away, the ring
is the mechanism; if it survives, the body's own interior moved and the shadow
fit reached further in than anything predicts. A second, cheaper check is the
ratio of the eroded count to the full count per cell — the ring's share — read
against each cell's measured move across the 726 rows.

**What the answer changes.** If it is the ring, then an interior statistic over
a mask that includes the contour cannot separate the body from the exterior on a
thin surface, and either the statistic erodes its mask or the shadow is
composited into a separate target. If it is not the ring, M2's miss is the first
evidence that an exterior fit reaches the interior, which is a finding about the
material and not about the instrument.

---

## Over a pure-black backdrop vitrea's exterior sits one byte above Apple's, and a ΔE × 8 panel makes that a mid-grey (W32 G1 review closure, 2026-09-21)

*Opened by W32 G1's independent review (claims §5.168 §10, finding B-4), which
read the gate's own sheets against the claim made about them. Evidence:
`packages/calibration/results/2026-09-21-w32-g1-shadow-fit/b4-black-floor.py`
and its committed output.*

**The measurement.** On `checkerboard-8` — black and white squares at an 8 px
pitch — Apple's macOS 27 render reads **exactly (0, 0, 0)** on the backdrop's
black squares out in the shadow band, and vitrea reads **(1, 1, 1)**. Never
more: across all twelve bed × span readings the count of exterior pixels where
the native is 0 and the web exceeds 1 is zero. The count of pixels where it is
exactly 1:

| bed | span 44 | span 128 | span 160 |
| --- | ---: | ---: | ---: |
| 1x light | 0 / 29,330 | 2,188 / 17,532 | 3,334 / 9,440 |
| 2x light | 0 / 117,416 | 9,104 / 70,156 | 14,384 / 38,244 |
| 1x dark | 0 / 29,352 | 573 / 17,566 | 577 / 9,531 |
| 2x dark | 0 / 117,436 | 2,447 / 70,447 | 2,337 / 38,335 |

Present at 128 and 160 and absent at 44 on every bed. `liftSpanMin` is **64**,
so a 44 px caster adds none of `liftAmplitude` and a 128 or 160 px one adds all
of it: the term this points at is the LIFT, which W32 did not move (X3 forbade
it and no stop in that wave reads it). It is pre-existing, not a regression of
the exterior fit. What changed is that the shadow now matches, so the floor is
the largest thing left in the exterior that the eye can see.

**Why nobody had seen it, and this half is the more general lesson.** The gate's
sheets amplify OKLab ΔE by eight. OKLab takes a cube root of linear light and
that function's derivative diverges at zero, so the distance from sRGB byte 0 to
byte 1 is **ΔE 0.0672** — two-thirds of the distance from grey 128 to grey 160
— and eight times it is byte 137, a mid-grey. The panel therefore draws a full
checkerboard where the two renders differ by one least significant bit, and
`eye.md` read that panel as showing structure it could not explain and then
recorded the opposite ("black past the rim band on every one of the four").
**A ΔE × 8 OKLab panel over a backdrop containing pure black cannot be read as a
verdict on the exterior without the LSB check**, and the check is a one-line
count: exterior pixels where the native is 0 and the web is not. Any future
sheet over `checkerboard*`, `dark-solid` or `hc-text` inherits this.

**The fix shape**, in two parts.

1. *The material question.* Sweep `liftAmplitude` and read the black-floor count
   per span and per bed against it, on the committed captures — no new capture
   is needed, because the floor is a property of the web render alone once the
   native is known to be 0. Either Apple has no lift over a black backdrop, in
   which case the leaf is conditioned on the backdrop's level and the bed
   already carries the cells to fit it; or the lift is real and vitrea is adding
   it where a premultiplied output cannot carry it, in which case the term is a
   compositing defect at the alpha floor rather than a material constant.
2. *The instrument.* The sheets should carry the LSB count beside the ΔE panel,
   or clamp the amplification so the panel's brightness is comparable across
   backdrop levels. The second changes what every past sheet means and is a
   decision; the first is additive and is what a gate making sheets should do
   next.


**Lift term closed beside,2026-09-22, W33 G1b (§5.172).** The two active macOS27
amplitudes are declared0 and the three thick anchors compensate under all stops;
232/232 non-holdout cells,13,236,229 eligible pixels, read0 under both masks.
The original statement and counts above remain their generation's evidence.
The four2x composite holdout rows retain five unchanged base-edge pixels because
G0's mask names the overlay box, not the stack. That zero-target miss is recorded
and remains an instrument task below, not a widened bound. The frozen26.5 material
keeps its lift. Every new sheet carries the LSB check;17 were viewed. Nine supplemental2x sheets were then viewed,26 total; unmeasured CSS probe panels are labelled.

---

## B2 reads 1.7622 of 1.5 at the shipped dark material while the exterior it describes improved by a factor of 9 to 24 (W32 G1 review closure, 2026-09-21)

*Read at W32 G1 (claims §5.168 §7, finding N-3). Evidence:
`results/2026-09-21-w32-g1-shadow-fit/shadow-law-at-shipped.txt` and the same
gate's `c1-forms.txt` before and after.*

**B2** — the σ law's output at span 44 against the bed's own measured thin σ,
≤ 1.5× — is a declared reading and **not an adopted row** (§5.156 §5 (b);
§5.159 records it met at 1.155–1.419 when the law was fitted). At W32 G1's
sealed dark document it reads **1.7622**: the law's thin line is 2.7220 CSS px
against a bed σ of 1.5446.

**The mechanism is the knee, not a fit that went wrong.** The joint fit dropped
the dark slope 0.1340 → 0.1215 inside B1's window, and the knee is held at 44 by
construction, so `sigmaThinOffsetPx` is re-derived −6.968 → −6.318 and the thin
line rises 2.072 → 2.722. Nothing chose that number; it is what holding the knee
costs when the slope moves.

**And the rendered thin exterior went the other way on the same bed.** 1x dark
`T` over the admitted bands reads 0.00201 → **0.00023** at span 44 and
0.00171 → **0.00007** at span 32 — better by 8.7× and 24× — at the material
whose B2 got worse. The thin stop, which is per cell on the inner bands, is met
on all 206 readings with 0 worse than the bar.

**So the two disagree in sign, and that is the point.** B2 compares a LEAF in
closed form to a fit of the native render; `T` compares two rendered exteriors
band by band. §5.162 §5 records the same confound for candidate (i), where a
green B1 sat beside a rendered σ three CSS px too wide. Here it runs the other
way: a red B2 sits beside a rendered thin exterior an order of magnitude better.

**The fix shape** is to decide what B2 is for before anyone adopts it. If it is
a guard against a thin blur collapsing to nothing, it should be stated on the
RENDERED thin exterior — which the thin stop already is — and B2 retired. If it
is a statement about the leaf, it has to be read beside the knee it depends on,
because a slope move at a held knee changes it with no exterior change at all.
Neither is this wave's; B2 is unadopted and W32 X4 forbids re-stating it. What
would settle it is one sweep: the leaf's thin line and the rendered thin `T`
against the slope, knee held and knee free, on the dark bed.

---

## The window pose is a discrete swap on the WebGPU tier, and the recede's stand-down made that visible (W32 G1 review closure, 2026-09-21)

*Opened by W32 G1's independent review (claims §5.168 §10, finding N-12), which
found four records claiming a crossfade the fitted tier does not perform.*

**What each tier does.** `platform-web/src/css-tier.ts` declares a transition on
`box-shadow` on the element that carries it, so on the CSS tier the outer shadow
really does interpolate to nothing when a window loses focus. On the WebGPU tier
it does not: `root.ts`'s scheduler participant calls `applyMaterialProfile`
with the newly posed profile the instant `resolveWindowActivation` returns a
different value, and `receded-profile.ts` states the design in as many words —
"Each scheme has exactly two fixed endpoints; this is not an interpolated pose."
The material swaps between frames.

**Why it is an entry now and was not before.** Until W32 the receded documents
carried their active document's outer-shadow anchors leaf for leaf, so the two
endpoints drew nearly the same exterior and the discreteness of the swap had
almost nothing to show. Decision Log 2 stood the receded amplitude down to 0, so
the two endpoints now differ by the whole shadow — a reach of 13 to 43 CSS px
going to zero — and on the tier that is the fidelity target it goes in one
frame. The reference fades.

**This is a motion defect and not a material one**, which is why W32 does not
touch it: the material is right at both endpoints and the wave's own acceptance
reads the two poses statically. Nothing in the ledger's verdict moves.

**The fix shape**: a pose crossfade on the WebGPU tier — interpolate between the
two resolved materials over the activation transition rather than swapping the
document, which means the renderer taking two profiles and a parameter for the
duration of the transition, or the pose resolving to a blended profile that the
existing single-profile path already accepts. The second is much the smaller
change and is probably where to start; what it costs is that a blended material
is not one of the measured endpoints, so `root.material`'s readout has to say it
is mid-transition rather than name a document — which is the honesty core's
constraint on the design, and the reason this is not a five-line fix. The
duration and curve should be read off the reference rather than chosen; nothing
in the project has measured them, and the motion-metrics harness the charter
Defers is what would.

---

## The two macOS 27 receded documents' provenance blocks describe the pre-W32 state, and no `$comment` can be added beside them without moving a recorded hash (W32 G2 review closure, 2026-09-22)

*Found 2026-09-22 by the review closure of W32 G2 (claims §5.169 §10, finding N6).
No number moves; the document bytes are deliberately left alone.*

`profiles/apple-macos-27.0-1x-light-standard-glass0.5-receded.json` and its dark
sibling carry a `measurement` block whose `status` reads *"measured — the recede no
longer removes the shadow"* and whose `previous` reads *"every amplitude leaf
zero"*. Both sentences describe the state W29 G3b left and W32 Decision Log 2
reversed: every amplitude leaf of both documents is **0** today, so the block's
`status` and `previous` are the wrong way round at the shipped bytes.

**Why it is recorded here rather than annotated in place.** The obvious fix is a
`$comment-w32-g2-provenance` key beside the block, which is the pattern those two
documents already carry three times (`$comment-w30-g3b`, `$comment-w31-g3c`,
`$comment-sha-history-correction`). It cannot be used here. Those annotations were
added at gates that **re-read the bed**, and each says so in as many words — *"the
rows read at THESE bytes"* — because a profile document's twelve-hex identity is
`sha256` over **the whole file**, provenance included:

```ts
// packages/calibration/scripts/material-profile-file.ts
// Hashed over the file, not the extracted sections: the cell should name the
// artefact a human can go and read, provenance included.
sha256: createHash("sha256").update(text).digest("hex").slice(0, 12),
```

That twelve-hex string is written into every capture's `capturePath` and therefore
into every committed row's KEY (`recededProfile=…-receded.json sha256:45acb6d916b9`).
Adding one `$comment` key moves it — measured rather than assumed: **45acb6d916b9 →
664f455a55bd** (light) and **4e68f81869f6 → de6a7e2b1808** (dark). Every inactive
row of `results/matrix.json` would then name a receded document no file on disk
has; `check-capture-tree` would report a live mismatch and exit 1; `sheets.ts`'s
per-cell assertion that a capture names the SHIPPED document bytes would refuse,
which is exactly the refusal it exists to make; and claims §5.169 §8 and the c9d
0.22.0 row would both be naming a superseded hash. `resolvedMaterialSha256` would
NOT move — the seal is over the resolved material and not over the file — which is
precisely what makes this trap quiet: the seal tests and `freeze.py verify` would
stay green while the generation the rows were read at stopped existing.

**The fix shape.** The correction belongs to the next gate that re-reads the
inactive bed, which pays for the moved content hash with the read that justifies
it — the same bargain W30 G3b and W31 G3c made. Until then this entry is where the
staleness is recorded, and claims §5.169 §10 names it. A wave that wants it sooner
has one structural option worth weighing: give a document a provenance sidecar that
is not part of the hashed file, so a record can be corrected without inventing a
generation. That is a schema decision and not a wave's.

---

## Nothing proposes re-pinning C1 at the shipped bed, where its bound is 4.8× the reading it was derived from (W32 G2 review closure, 2026-09-22)

*Found 2026-09-22 by the review closure of W32 G2 (claims §5.169 §10, finding N9).
A re-pin is the user's; what is recorded here is the rule that would produce one
and what it would cost.*

`C1`'s bound, **0.0042**, is W32 clause 2's rule applied to the generation the
clause was DECLARED against: the worst standard bed's span-96 order statistic,
0.00413, rounded up to two significant figures. At the shipped bytes that same
cell — 2x light, span 96 — reads **0.00088**. The bound is 4.8 times the number it
was derived from, and the twelve adopted rows read:

| span | 1x light | 2x light | 1x dark | 2x dark | headroom at the worst |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 96 | 0.00090 | 0.00088 | 0.00125 | 0.00115 | **70 %** |
| 128 | 0.00245 | 0.00253 | 0.00348 | 0.00391 | **6.9 %** |
| 160 | 0.00134 | 0.00132 | 0.00164 | 0.00168 | **60 %** |

So eleven of the twelve rows are loose and one is tight, and the clause's own
stated protection — *"a fit that buys span 128 by widening span 96 fails"* — is
false at the shipped bytes, because span 96 could take four and a half times its
present reading before this clause noticed (claims §5.169 §10, finding N1).

**The rule that would produce a re-pin**, stated so a later gate does not have to
re-derive it: clause 2 rounds the worst standard bed's reading UP to two
significant figures, and C1 is stated per span, so applying it per span at the
shipped generation gives **0.0013 / 0.0040 / 0.0017** at spans 96 / 128 / 160 —
tightening span 96 by 3.2×, span 160 by 2.5×, and span 128 by almost nothing. Two
things a gate has to decide before it can be adopted. First, whether a per-span
re-pin is what clause 2 means at all: the clause's text names *the span-96 order
statistic* as the source of ONE number, and the per-span form is the ruled shape of
the row rather than of the rule. Second, whether a bound with 0 % of headroom at
two of three spans is a stop or a tripwire — the same question B3's 0.07 % raises
one entry over, and the reason a re-pin is recorded as a user decision here rather
than proposed.

**The fix shape**: a gate that adopts a material change on the exterior re-derives
the three numbers from its own cut, puts them beside the readings, and asks. There
is no measurement to take: the cut is already regenerated at every adopting gate,
which is what makes this cheap.

---

## Under Reduced Transparency the macOS 27 body's LEVEL misses by 0.08 at span 44, and only the structure half is recorded on that bed (W32 G2 review closure, 2026-09-22)

*Found 2026-09-22 by the review closure of W32 G2, read off the committed matrix
and visible on `sheet__apple-macos-27.0-1x-light-reduced-transparency-glass0.5__photo__capsule-button__rest.png`
(claims §5.169 §10, finding N10). No capture; no number moves.*

On `apple-macos-27.0-1x-light-reduced-transparency-glass0.5`,
`photo__capsule-button__rest`:

| tier | `interiorMeanNative` | `interiorMeanWeb` | native − web |
| --- | ---: | ---: | ---: |
| WebGPU (`texture`) | 0.96841 | **0.88872** | **+0.07970** |
| CSS (`dom`) | 0.96841 | **0.88505** | **+0.08336** |

Apple's plate under that preference is very nearly white and vitrea's is eight
points of luminance below it, on **both** tiers — so it is the level and not one
tier's compositing. It is the largest interior-level gap at that cell on any macOS
27 profile: the four standard beds read −0.0035 to +0.0049 there and the coupled
increased-contrast bed −0.029 to −0.014.

**What is already recorded, and what is not.** The tracker's W29 G3b entry *"Under
Reduced Transparency the GPU tier is under-opaque"* is on this bed and is about the
**structure** half at a different cell (`checkerboard__rrect-md__rest`: native sd
0.43, WebGPU 3.49, CSS 1.03), with the level named only as *"both tiers sit 6–7
levels below the native's"*. Eight points of luminance at span 44 is an order
larger than that and it is at the span the accessibility documents' own
`reducedTransparencyOcclusion` was never fitted at (W32 Deferred 10). The LEVEL half
of this residual is written up on the macOS **26.5** bed (§5.73's two
reduced-transparency cells lost to the fold's level, and §5.146's 26.5 sheet
narrative, whose reduced-transparency paragraph reads the native panels as "nearly
flat" against a WebGPU body that is not) and has not been carried onto the 27 one.

**The fix shape**: it is the same work W32's Deferred item 10 already names — fit
`reducedTransparencyOcclusion` per accessibility document against the admitted-band
objective on cells the bed already holds — with this cell and this statistic added
to what that fit is judged on, because the shadow-side fit W32 left those beds with
moves the exterior and not the plate. No capture is needed: the rows are committed.


---

## W33 G0: the contour needs an orientation/colour law and a coverage ruling before a fit

*Measured 2026-09-22, claims §5.170; evidence
`packages/calibration/results/2026-09-22-w33-g0-rim-cut/`.*

The dark active photo capsule's near-zero straight-edge residual is not a whole-surface
absence:1x straight native−web−0.27 bytes, corner average−19.75. At span96 the horizontal
sides remain much shallower than the vertical ones. Scheme×pose×contour orientation is a
necessary condition of the stroke model; span or a capsule-wide off-switch is insufficient.
Eight neutral/tinted multiply/add/affine diagnostic families in encoded/linear sRGB do not
reproduce all RGB channels, even after stratification. **Next work:** settle a physically
composable, direction-aware colour law against G0's non-holdout referee before fitting any
material amplitude. Do not widen G0's per-stratum ceilings to hide the residual.

The finished-alpha experiment reads380 non-holdout captures. Outside measured-depth
source-over fails contour/IoU17/17 cells; inside2/1; outside0.49 fails113/123. Held coverage
passes every shape gate but cannot reach the exact native RGB on380/380 cells (378/380 even
with one-byte tolerance). A per-pixel colour oracle still needs alpha that fails73/59 broad
and23/24 selected contour/IoU rows. **Next decision:** W33 DL2, before G1; a contour re-pin
alone does not settle the IoU conflict. Inside placement changes the native-mask pixels in
all26 M2 cells and one selected conditioning exclusion; it also misses the measured exterior
location. No form is silently accepted as equivalent.

**Inventory qualification:** the memo's14,325,464 native-black full-exterior pixels remains
unreproduced; the declared bbox reader finds14,329,648 with the same448/264/30-held-out census
counts. Four convention attempts are in the README. Its author identified the earlier total
as an unverified helper read. Resolve only from a recoverable pixel-mask definition, never by
editing the committed count to match an expected number. The separate backdrop-black lift
census DOES reproduce, including all39/125 nonzero frozen control cells.

**Scope left explicit:**12 non-holdout27 composite scenes are outside the single-rounded-rect
stroke sampler (their names in `referee.json.declined`); the forms experiment uses their real
union geometry. A complete composite contour referee must separate the exposed contours of
group/stack members rather than assign the bbox's corners to the material. IC-alone and
dark/2x accessibility stay unmeasured. The opening proof's process-count/idle half of X6 was
unrecorded; it is not retroactively attested.


## W33 G1a: angular, radial and colour identification does not close; do not buy a fit with a shape re-pin

*Measured 2026-09-22, claims §5.171; evidence
`packages/calibration/results/2026-09-22-w33-g1a-contour-model/`.*

**Update beside the G0 entry:** DL2 is now ruled as the identification route; DL3 is the user's
remaining bound/model decision. On304 non-holdout cells,0/152 combined angular strata close
under a one-byte diagnostic comparator, against78/152 straight-only and3/152 arc-only. A
scheme/pose-conditioned isotropic+even term explains the axis contrast but not every bin;
dark active photo/md's best sampled law leaves14.762813 bytes worst-bin residual. The shipped
diagonal rim gives identical cardinal-normal values at every exponent and cannot carry that
contrast. Straight-only data cannot identify the even exponent at all.

**Colour remains open.** The angular encoded/linear multiply/add/affine families leave
multi-byte RGB residuals. The representative encoded tinted affine improves pooled ringMAE
34.9791→18.1383 but fails52/304 G0 ceilings; its coefficients are still independently diagnostic
at each scale. Exact placement costs36 contour/14 IoU failures on298 measurable cells; capping
previously sub-threshold finished coverage at127/255 keeps shape but leaves18.4324 bytes.
Do not ship this law, widen G0's ceilings, or interpret the native-colour oracle's0 MAE as a
fit. Oracle replacement needs40/45 conformance failures on380 cells, whereas G0's73/59 oracle
was source-over on the existing layer, not a lower bound over replacement layers. Both numbers
stand on their distinct definitions.

**Coverage and geometry need an identifying experiment.** Exact capsule arcs already spread
one geometric pixel into centre-distance shells[−1,0) and[1,2). The64-sample area-control grid
selects centre.5 on light-solid inactive capsules at both scales; width sensitivity is1–1.25
light/.75–1 dark, not a confidence interval. Continuous md best centre moves.5→.25 between
scales where capsule centre holds, exposing the declared circular SDF's corner confound.
The support[0,1) price touches0 M2 pixels; a full antialiased term can enter the inner ring
and must be priced again, including G0's257–1,311 inside-mask pixels/cell, rather than inherit
that zero. A one-byte encoding comparator is not the missing native repeatability bar.

**Review qualification beside, 2026-09-22 (§5.171):** one byte is an encoding-resolution
diagnostic, not a native noise bar. The 78 straight / 3 arc closures count the recorded
least-squares fits, not a proof over all coefficients. At three bytes those fits close
8/152 combined, 104/152 straight and 12/152 arc strata. The reviewer's minimax fits close
0/152, 79/152, 4/152 respectively at one byte and 16/152, 111/152, 20/152 at three bytes.
Omitted families close individual full strata at one byte: rotated axis 0/152; isotropic plus
two orthogonal even-axis terms 7/152; gradient 0/152; colour plus gradient 3/152. For example,
dark inactive 1x dark-solid capsule fits `−22.650771 + 6.304978|nx|^0.5 + 13.357469|ny|^0.5`
with max-bin residual 0.31 bytes. Thus the original no-full-closure statement is about the
recorded families and fits, not every separable law or coefficient choice.

**Review bound qualification, 2026-09-22 (§5.171):** 27.0915 bytes bounds a common cardinal
ADDITIVE response against these four means, not arbitrary retuning of the whole shader.

**Review fixed-colour check, 2026-09-22 (§5.171):** a fixed-colour blend is contained in the
affine family: `m0 = −a0`, `m1 = −a1`, `b0 = a0·c`, `b1 = a1·c`. The independent constrained
fit on light-inactive black-bearing leaves 35.40 bytes encoded / 40.81 linear (worst-channel
MAE, evaluated in encoded bytes). No fixed blend colour is identified by that fit.

**Review correction beside, 2026-09-22 (§5.171):** the circular-control interpretation above
is withdrawn. `SceneViews.swift:60` supplies `Capsule()`, whose default is `.continuous`, not
`.circular`. `capsule-geometry.swift` and its `.txt` output attest the 120×44 paths without
rendering: default equals explicit continuous and differs from explicit circular; the straight
segment starts at 33.6306 (1.528665 × 22), not 22. The independent review's curve sampling found
−0.303570…+0.043123 CSS px against the circular SDF (down to −0.607 device px at 2x), whereas
explicit circular's cubic approximation stays within +0.006 CSS px. These are path diagnostics,
not a recapture or proof of the fixture's raster alignment. The recorded shell/grid numbers stay;
pixel-area spread is possible but is NOT isolated from geometry, and capsule-vs-md is NOT a
circle-vs-continuous experiment. G0's fixed-mask ceilings remain valid non-regression measurements
because candidate and baseline use the same declared pixels; corner ceilings do not isolate
colour-law accuracy. Both supplied shapes require geometry qualification.

**Next work:** repeated same-geometry capsules over uniform grey and RGB levels, subpixel-phase
sweeps at1x/2x, then matched continuous rectangles, both schemes and poses, with a declared
split and noise bar. This requires authorisation beyond W33 X5; it was not captured here.
After a law is identified, settle the CSS dpr-aware inset/side-separated approximation by
experiment, not by assuming its corner response. Unmeasured IC-alone/dark accessibility and
composite exposed contours remain open. Candidate forecasts explicitly leave66/166 stop rows
outside their single-shape untinted domain unchanged; there is no whole-bed fit hidden in them.

**Amended next-capture plan beside, 2026-09-22 (§5.171):** capture an explicitly circular,
path-ATTESTED capsule beside the default continuous one, then matched continuous rectangles;
export the supplied geometry and alignment and include an opaque geometry/raster control.
Use matched local-colour scenes with varied backdrop-gradient direction and magnitude and a
small spatial-frequency ladder, alongside uniform-grey/RGB and subpixel-phase sweeps at both
scales, schemes and poses. No-glass references must have identical colour management. Take
enough repeats to estimate per-bin, per-channel variability BEFORE choosing a closure threshold;
declare calibration/validation/holdout membership before fitting. This is a plan requiring new
native-capture authorisation, not a capture performed here; X5 remains intact.

**Recommended decision:** stop the contour term at the finding; DL3 remains unruled. The
independent lift stand-down is still supported, but separating its seal/read from the contour
would change the parent's one-seal route and has not been done. No material gap is closed by
this identification gate.

**Third option beside the DL3 draft, 2026-09-22 (§5.171), UNRULED:** the independent reviewer
also demonstrated a gate-preserving EMPIRICAL partial correction, rather than waiting for an
identified law or relaxing conformance. It uses isotropic affine on light-active and both
inactive endpoints, `|nx|²` on dark-active, accessibility unchanged, and coefficients shared
across 1x/2x. Attenuation is sampled under every G0 ceiling with the finished-alpha cap.
Pooled ring MAE is **34.979077 → 20.599081 bytes**, with **0/0** contour/IoU failures,
zero predicate/area/body/native-mask changes, min IoU **0.998722**, and whole-exterior warning
**0.000446**. Isotropic-only leaves **23.768**; `|nx|²`-only **29.561** (dark-active
**25.649 → 12.304**). The baseline is **34.979077**, not “~20”; 20.599 is the partial result.
These are in-sample, offline, unrendered review readings: no CSS result and no identified law.
`review-partial-combined.py` and `review-partial-prices.json` preserve the review artifacts.
**Recommendation remains stop at the finding:** geometry and colour remain unseparated, and
in-sample non-regression is not identification or rendered validation. This empirical route
is the user's third alternative, not a ruling or authority to implement it; no gate moves.


---

## W33 G1b: correct the black-floor referee's composite domain before adoption

The post-seal holdout (§5.172; `holdout-composite-decomposition.json`) reads five
one-byte pixels on four2x `checkerboard__glass-over-glass` rows. All were1 before
and after. All lie inside base box[50,35]–[270,165], outside overlay box
[100,64]–[220,120]; G0's56px component surrogate calls base-edge pixels exterior.
The same mask makes dark active's count2485→1 and light active9871→1, while the
inactive counts1/2 stay. No new lift persists beyond the stack. **G2, before the
zero row is adopted:** read a union box or decline composites explicitly as the
stroke referee does; keep this held-out reading and show the corrected domain's
reading beside it, without a new capture or a fitted constant. The zero is not
widened and this is not an excuse to erase the five pixels from their first cut.

**Closed as a referee correction at W33 G2 (§5.173), not as a material fix.**
`2026-09-22-w33-g2-landing/referee-union.py` reads all12 standard-profile composite
black-bearing cells from the canonical tree. Both masks read0 >0 and0 >1 under the
union bounding box; the four holdout cells' five legacy pixels are all inside the
base and outside the overlay. Their original readings above remain. X1 DECLINES
composites rather than adopting this correction as a contour/union-of-shapes claim.
A future composite gate needs that qualified geometry and its own declared population.

## W33 G1b: CSS near-edge black pixels are not its far-exterior lift floor

`css-floor.json` (§5.172) reads pre-existing, unchanged counts under G0's integer
mask: checkerboard8/lg170,ml134,hc-text28/lg165,light impulse/md204 at1x. The mask
admits centres1.5CSSpx outside the box; analytic BOX-distance>=2 reads0 for all,
while rounded-contour distance reaches2.77CSSpx. Thus the older far-halo “no floor”
claim is true on its domain, not a proof that CSS matches the near contour. This
is not the WebGPU lift and no CSS constant moved to hide it. Carry it into the
geometry-qualified CSS contour work, with both distance conventions explicit.

## W33 G2 prose follow-up: the demo's lift-width explanation no longer names its default

`apps/demo/src/site/calibration.ts:187` and its adjacent doc comment attribute the
thin-span fitted width to the lift. W33 G1b's default macOS27 material has lift0;
its shape leaves are unread. Correct that sentence at G2's landing, keeping the
fit-versus-material-sigma distinction without attributing a zero operator's width.
The footer is flagged here, not changed as part of the material seal.

**Closed at W33 G2 (§5.173):** the calibration readout now distinguishes the
composite fitted width from the material law without attributing it to a zero
macOS27 lift. It names the retained26.5 lift and the diagnostic status of fitted σ.

## W33 G2: the closed black floor and the contour work that remains

The W32 black-floor entry above is closed on the WebGPU standard single-shape
non-holdout domain by X1:218 cells,12,681,980 integer-mask pixels, zero >0 and >1.
The analytic companion has12,593,524 pixels and also zero; span160 is probe-strength.
G0's232-cell referee remains232:10 accessibility cells and4 composites explain
its difference from X1. Accessibility reads zero too but the fold stands down the
material W33 changed, so it is not silently included in the adopted row.

Decision Log3 declined the empirical20.60-from34.98-byte contour correction: it
was in-sample, offline and unrendered, not an identified law. First next work is
§5.171's geometry-qualified native capture: path-attested circular beside default
continuous capsules, matched continuous rectangles, uniform-grey/RGB and independent
x/y subpixel phases at1x/2x, matched local colours with varied gradient direction
and magnitude and a frequency ladder, colour-managed no-glass controls, repeats
for per-bin variability before thresholds, and a split declared before fitting.
This needs the user to lift X5; no contour leaf or CSS approximation shipped.

**W34 G0 follow-up to the contour capture above (2026-09-23, §5.174).** The identifying
bed is declared, not yet captured at G1's bar. The requested fractional phase axis failed
its scratch test: on both scales, zero/quarter/joint-quarter are identical and half equals
three-quarter. Best whole-pixel translation leaves a small nonzero remainder, retained.
No window-origin workaround was attempted. If G2 needs independent phase to distinguish
coverage/body/stroke, a future authorised, pre-split experiment must demonstrate a genuinely
independent raster-phase mechanism from pixels rather than merely export fractional inputs.

The longer-settle/changed-order grey sentinel differs by one code at 18 edge pixels, while
each three-run arm is unanimous. Dwell and order remain confounded; a factored experiment is
the work that would separate them. The current quantum floor is not widened to hide the
reading, and neither arm is claimed to establish universal settledness. Both states are in
the replayable archive. The 1x radius12 rectangle also has sixteen bins below the declared
four-pixel minimum; they are unmeasured, not closures. More population or a newly declared
binning design would be needed to close that angular/radial coverage gap, not retrospective
pooling chosen after a fit.

The new native circular capsule has a circular web counterpart. The **existing continuous
native capsule still maps to vitrea's circular stadium**, unchanged in this gate; its known
geometry mismatch must not be attributed entirely to a contour-colour law. A separate
geometry-qualified comparison and any consequent runtime mapping change belong after the
identification, with canonical conformance/stops re-read rather than inherited. Supplied-path
attestation is not the window server's raster origin, and ordinary-fill coverage is not
assumed to transfer to glass. The radius22 cubic's +0.006 CSS-px qualification scales to
about +0.0131 at radius48; that larger-radius uncertainty is explicitly carried in W34.

## W34: the original Screen Recording grant must be restored at wave close

Found 2026-09-23 (§5.174; charter DL4). Original grant-before captured positively; after the
user granted the distinct-identifier side bundle, the side captured and the original was
TCC-denied. Both binary hashes were unchanged. This is an observed failure of simultaneous
availability, not proof of which internal TCC key or UI-row identity caused it. The parent
ruled to keep the side for the wave and avoid an unnecessary grant swap mid-sitting. At wave
close, restore the original by its exact protected path using the README remove/re-add
recipe and positively capture it; do not rebuild it or grant `build-probe`. Record what
happens to the side grant then. The side's first post-grant launch also failed active-pose
attestation; a later quiet launch attested and matched a canonical fixture byte-for-byte,
but the first-launch cause remains unidentified and the failed reading stays beside it.


## W34 G1: the captured repeat bar preserves the remaining identification limits

2026-09-24, §5.175; evidence `results/2026-09-23-w34-g1-contour-sitting/`.
The G0 declaration above is now captured at seven normal runs per pass, with three separate
long sentinels; 592/592 cells materialized and every run attested. This closes the absence
of a native repeat bed, not the absence of an identified contour law.

The actual 1x normal masks leave 192 under-populated arc bin/shell rows across twelve
rectangle cells, matching sixteen per cell. They remain unmeasured; a newly declared
sampling/geometry design, not retrospective bin pooling, must close that coverage gap.
The normal maximum admitted envelope is 0.5 byte; the long maximum is 0.2236842105263158
on dark-active 2x straights, with 0.17647058823529413 on arcs. Quiet strata are finite-run
observations, not zero variability. The long arm has only three runs and does not inherit
the normal arm's seven-run state-discovery convention. Which arm is settled and whether
dwell or order explains the G0 protocol dependence remain unresolved; a factored experiment
is still the work needed if G2's inference depends on them. No tolerance was widened.

The phase mechanism, ordinary-fill/glass transfer, body/coverage ambiguity, radius-scaled
cubic uncertainty and continuous-native/circular-web mismatch remain as recorded above.
G2 now has the replayable pixels and published populations to decide identification at
that resolution. Original-grant recovery remains DL4's wave-close work; G1 did not touch TCC.

## The W34 repeat archive adds 114 MiB to a 328 MiB pack, and the next sitting would add as much again (W34 G1 merge, 2026-09-24)

The charter's clause 4 asks for the run-to-run bar to re-derive from the repository without the
raw PNGs, and G1 delivered it: `results/2026-09-23-w34-g1-contour-sitting/repeat/` holds 103 MiB
of per-run, per-bin statistics and 11 MiB of compressed lossless crops for 408 glass cells over 40
runs. That is the right artefact for this wave and it is committed. It is also a third of the
pack, and a second sitting at this bed's size would double it. **Shape of the work:** decide,
before the next native sitting, whether repeat archives live in the repository, in Git LFS, or as
a release asset named by hash from the ledger — the requirement is that the bar re-derives from
what a reader can fetch by the name the ledger records, not that it sits in every clone. Nothing
here is wrong; it is weight.

**Measured beside, 2026-09-25 (the parent, after 0.24.0):** the pack is now 462.44 MiB, and the
heaviest blobs in history are not the repeat archive but `packages/calibration/results/matrix.json`
itself — every read that appends a generation commits a new 60–77 MB revision of the whole file
(the eight largest blobs in the repository are all that path, 63.0–76.6 MB), which is what GitHub's
GH001 warning on the W36 G2 push named. The repeat archive is 146 MB in the working tree. Any weight
decision therefore has two parts, not one: the archives (LFS or an external store, as above) and the
matrix's revision history (per-generation files, which `results/superseded/` already is for retired
rows; compression the readers and the demo's build-time reduction would have to learn; or LFS with
the demo build and every reader still able to read it). Not chartered; measured so the next fork
can be ruled on numbers.

**Ruled beside, 2026-09-26 (the user, W39 charter Decision Log 1):** the W39 repeat archive
(estimated 200–350 MB) is a GitHub release asset named by its SHA-256, fetched and verified by
the readers and kept out of ordinary Git, with a second owner-controlled copy on the capture
machine; W34's committed archive stays where it is (no history rewrite). And the matrix's
revision history gets its own small wave, W40, after W39 G0's merge and before W39's G3 landing:
future generations as indexed per-generation files, frozen macOS 26.5 rows untouched and still
addressable, no rewrite. Grounding for W40 requested 2026-09-26.

## W34 G2: comparer publication seams and missing curvature rows

2026-09-24, §5.176; `results/2026-09-24-w34-g2-contour-identification/`.
G1's materialized manifest omits `caveats`, while the comparer unconditionally iterates it in
its final reporter. The first G2 profile rendered and wrote its matrix, then threw. G2 keeps
that attempt and uses a provenance-recorded manifest projection adding only the caveat field;
no fixture metadata or pixels were changed. A future producer/consumer contract change should
make that schema field explicit and test a materialized probe manifest end to end, rather than
repeat this evidence-only projection. This did not justify changing shipped code in G2.

Three of 336 non-holdout captured cells produce no standard matrix row: 1x dark inactive
`gradient-90-small__circular-120`, and 1x light active `grey-255__circular-120` /
`grey-255__circular-200`. `contourCurvature` refuses their zero-length recovered contour.
All captures are preserved and the fixed-mask contour instrument reads all 336. Follow-up should
return an explicit unmeasured curvature axis while retaining independently measurable axes,
with the current failures as regression cases; it must not invent a zero curvature reading.

## W34 G2: the boundary body must be identified before an outside-only stroke can close

2026-09-24, §5.176; `results/2026-09-24-w34-g2-contour-identification/`.
The new repeat bed removes W33's missing-bar objection: the one-code resolution floor dominates
the observed normal envelopes. It does not yield a point-closed contour law. A coefficient-free
counterexample now separates two questions previously conflated: in the nominated inner shell
[−2,−1), an outside [0,1) device-pixel band has zero geometric coverage, yet the exact-body
forward model misses populated validation bins by **2–27.375 codes** on the encoded family,
with every scale/scheme/pose and both contour parts represented. Both composition spaces fail
there. No retuning of that band's alpha, target or exponent can repair those pixels. This rejects
the nominated body/path/stroke decomposition, not every possible stroke-colour mechanism.
The full witness RGB, population and bar are in `coefficient-independent-floors.json`.

The useful continuation is a declared non-holdout study of the boundary-body and radial-placement
alternatives before another expensive full sitting. It must retain the physical/effective-response
distinction and cannot recycle a spent holdout as blind evidence. A genuinely identifying new
bed would need independent glass-path coverage/registration or a defensible boundary body model,
a phase mechanism proved reachable before the full run, local-colour/gradient contrasts and
populated arc bins. Ordinary opaque fill does not identify glass coverage. More quiet repeats
alone cannot remove this structural residual; the missing contour and the continuous-native /
circular-web geometry mismatch remain unshipped fidelity work. The 192 under-populated 1x
rectangle bins remain unmeasured, not pooled after fitting. DL2 belongs to the user; no G3 leaf,
CSS approximation, conformance re-pin or material-document change follows from this entry.

## Two harness bundles never both hold Screen Recording on this machine, whatever their identifiers (W34 close, 2026-09-24)

W29 measured that a second bundle under the harness's identifier evicts the harness's grant. W34
gave its side bundle a distinct identifier (`dev.vitrea.reference-apple.w34`) and a distinct
cdhash and found the same thing twice: granting the side refused the original (G0, §5.174), and
re-adding the original refused the side (close, W34 Decision Log 4). The internal key TCC uses is
not inferred; what is established is the operational rule: one harness bundle holds the grant at
a time, each switch is one user action in System Settings, and each switch is followed by a
positive capture check on BOTH bundles. **Shape of the work:** a native wave that needs two
bundles (a canonical recapture beside a probe bed) plans the switches into its runbook and its
price; a test of whether a Developer ID signature changes the behaviour is a separate, small
experiment nobody has run.

---

## W35 G0a: the body-boundary law is not yet transferable, and a positive radial ramp alone is insufficient (2026-09-24)

Evidence: c9a §5.177 §§3–6; `results/2026-09-24-w35-g0-edge-cut/`.
The native grey128 line is one bright row at1x and two at2x (+24/+30 and
+18,+31 / +22,+39 codes in light/dark), above a shallow rise. The frozen-domain
existing-leaf candidates fail at25.50/33.75/36.00/46.57 codes; even straight-only
maxima are5–9.85 against1. These are the best tested finite-grid nominees, not a
proof against all legal parameters. Native whole nominal-body arc response differs
strongly from the inherited diagonal lit law, and scalar affine added-white light
cannot explain the chromatic validation response (dark cyan18/186/186→19/233/233).
A positive second ramp cannot by itself remove the tested bright arc overshoots.

The runtime forward model checks its own web pixels to<.88 code and synthetic
pre-composition interventions recover, but the native pre-rim field/ramp ownership
is not identified. Coefficient transfer is stopped; E1 is not adoptable and no G0b
operator is selected. Closing work needs a bounded model declaration for radial,
angular and chromatic boundary response, retaining the baseline/coverage uncertainty,
then actual prototype discrimination within an explicitly authorised operator budget.
Do not narrow the frozen arc domain after seeing these misses.

## W35 G0a: the uniform body's level/chroma gap extends beyond the memo's selected examples (2026-09-24)

c9a §5.177 §3; `level-table.json` reads every non-holdout circular solid. Web−native
is+49 codes over light black and+28 over dark black at both scales. Active saturated
channel misses reach+111 (dark yellow's blue); inactive reaches−144 (dark blue's
blue). The2x dark-red deep median is242/50/50 against160/90/90, while the previously
quoted239/51/51 is correctly reproduced at shell−12, a different estimand.

No tone/chroma leaf moved. A separate level/chroma wave is Decision Log2's user
choice. It should fit native level and colour controls across the full range rather
than allowing a boundary amplitude to compensate through g*(L_web−L_native).

## W35 G0a: the eroded M2 reading is complete for the current generation, not the old shadow before/after pair (2026-09-24)

Follow-up to the W32 contour-ring hypothesis above; c9a §5.177 §7 and
`m2-gated-attribution.json`. All26 M2 cells reproduce their un-eroded matrix values
to<1e−12 and are re-read at1/2/3-device-pixel erosions. Dark photo/capsule active
std-dev falls60.03%/48.43% after1 px at1x/2x,68.37%/58.00% after3 px. Some light
cells rise. Erosion changes both population and mean: this is sensitivity, not an
additive ring variance or proof that the outer shadow alone caused W32's miss.

The historical hypothesis still needs the same erosion at BOTH named generations.
Nor is erosion a prediction of the change from a correct future edge. Keep the2%
stop and pre-W35 reference until a viable candidate gives its actual delta; DL3
contains that unruled recommendation, not a mask change or waiver.

## W35 G0a: canonical diagnostic availability and a CSS representation limit remain explicit (2026-09-24)

c9a §5.177 §§4,8. `mid-light-solid__rrect-md__rest` is not a canonical scene;
dark light-solid/mid-chroma rrect-md are absent from those profile memberships.
Several admitted native probe solids have no canonical WebGPU capture. No other
cell or superseded generation was substituted. Reproduce them only in a separately
authorised diagnostic capture, never by silently expanding a canonical read.

One CSS px inset atDPR2 has one output over its two full straight rows; native light
grey128's213/226 imposes a6.5-code minimax lower bound and dark156/173 an8.5-code
bound. That analytic limit is not a rendered CSS decline. A viable later model must
derive, render and measure its CSS projection and pin any decline to adopted bytes.

Source-prose follow-up for the boundary owner: the inherited inner-shadow comment in
`renderer-webgpu/src/wgsl/optics.ts` says it was kept because nothing measured it wrong.
That is historical default-material provenance, not a claim that W35 found macOS27's
boundary correct. G0a is forbidden to edit src/ and leaves the comment untouched; an
adopting source change must preserve the26.5 provenance while naming the27 qualification.


---

## W36's uniform-level correction conflicts with the structured stops; no operator is identified (2026-09-24)

**Open, §5.178; W36 G0, not a newly authorised initiative.** The black fallback
is identified (181/60 from sized alpha times neutral); the shared thin/thick
three-shift middle refit is not a shippable closure. On64 deterministic scratch
captures, light photo/rrect-md level-error growth0.02937–0.03371 exceeds0.005;
dark active photo structure grows3.14–4.13%, beyond M2's2%. Twenty-four of32
non-black grey trial cells meet the one-code median tolerance. No bound moves.
A negative result for this constrained family is not a proof that every uniform
response fails. Work that could close it: a declared lower-dimensional thickness
model or a separately identified colour/structure-conditioned response, tested
jointly on the native greys and photo under the frozen stops before another seal.
No free thick black is identified: only span44 uniform black is on the fit bed.

The chroma diagnosis sharpens the existing hue/level debt without closing it.
Full-RGB inversion excludes light red/blue/magenta in both poses and dark active
blue (both scales), plus every admitted27 canonical mid-chroma cell. Native
implied q about0.86–0.93 light/0.95–1.03 dark is not the shader's r. Correctly
converted r still extrapolates outside M1 under W31's OLD-tone multiplicative
secant; full retention cannot supply the dark chromatic luma excess. Part B is
UNIDENTIFIED, not a plate-mean term waiting only for implementation. Closing
work must define spatial domain, colour space, gamut and tint placement and
predict solids AND photo at the candidate tone; no native capture is authorised.

The level-stop debt above is now **declared completely, still not adopted**:
L1 has140 standard27 WebGPU calibration/validation rows,136 measured, two named
light inactive tinted-impulse misses0.066016/0.066059 against0.055 and four
UNMEASURED dark inactive dark-solid material rows. Probe diagnostics and W34
deep medians are separate. Baseline W33 document hashes and its future superseded
paths are pinned in G0, so neither a missing row nor a changed baseline can
silently buy a pass. Adoption remains the parent's Decision Log4 and a later
successful gate. CSS's black derivation/chroma decline, the tinted candidate
shade check and full-cohort exterior/conditioning checks remain unperformed;
G0's zero exterior pixel delta is a24-cell subset witness, not their adoption.

### W36 G1's priced black branch and the gaps it leaves (§5.179, 2026-09-24)

The black-only seal closes the GPU deep medians on the eight span44 black cells:
132/133 light and32/20 dark, both scales. It does not close the grey middle, chroma,
inner line, contour or the impulse residuals named above. The branch's support ends
at encoded0.003 before every admitted packed impulse input; the interval between
black and that join is a declared interpolation, not a measured native curve.
Thick equals thin by a declared extrapolation because this bed has no thick black.
Closing those identification gaps needs independently declared near-black and thick
anchors, and native capture remains subject to X5 rather than implied by this entry.

**CSS-only boundary residual, carried rather than fitted.** The three +2-code deep
black cells are `apple-macos-27.0-1x-dark-standard-glass0.5/grey-0__circular-120__rest`
and its2x twin (34 against32), and
`apple-macos-27.0-2x-light-standard-glass0.5/grey-0__circular-120__rest` (134 against132).
The1x light counterpart is+1 (133 against132); all receded black medians are exact.
A diagnostic stand-down of CSS rimAlpha/rimLevelGain/shadowAlpha together removes
all four residuals at unchanged black ordinates. This identifies the combined
existing boundary projection, not which leaf. No diagnostic boundary constant
ships. The parent clarified that the one-code W34 referee is GPU-only; CSS keeps
its coherence gates and records what its layers cannot carry. The future shared
boundary work should price this projection too; this is not a CSS-only charter.
Evidence: §5.179's `css-boundary-isolation.json` and `price-css-greys.json`.

The dark active black coherence ratios1.991940/1.589439 are rim-only diagnostics,
excluded by the existing95%-area/body-count predicate, not new exceptions. At1x,
the native mask is374/4872px with six bodies and CSS104/4872px with eleven; its
mean cannot judge the deep body. Dark receded has no extracted native mean. The
deep-domain medians and unconditional cross-tier DeltaE (maximum0.004064) remain
measured separately. Do not quote the excluded ratio as a passing body comparison.

**The receded colour-formula nomination is declined.** Linear-luma-then-encode on
the unchanged footprint preserves74 achromatic controls but breaks16 L1 growth
rows and three M2 rows: light inactive toolbar structure+17.8049%/+16.9386% at1x/2x,
plus small inactive+3.6174% at1x, against2%. Both experimental sources are restored.
The formula's improvement on saturated solids does not authorise a structured
regression. Closure needs a jointly identified tone/chroma form under the frozen
photo and structure stops; this finding does not justify abandoning footprint locality.

The broadened scratch price also records two inherited CSS probe coherence gaps:
dark inactive `impulse__rrect-lg`, DeltaE0.071495 at1x and0.065547 at2x, above0.05.
They are outside the canonical gated population and unchanged by either the black
branch or the formula trial. Their ratios0.137263/0.173454 are predicate-excluded.
They remain diagnostic gaps, not new canonical floors and not formula-induced failures.


## W36 canonical CSS holdout: five exterior pixels differ by one code (2026-09-24)

The dark 1x `checkerboard__glass-over-glass__rest` CSS holdout differs from W33 at
five exterior grey pixels by +1 code; the alpha image and shape axis are identical.
Both group inputs are unchanged and above the black branch support. The capture
reports deterministic true and repeatNoise zero, and the adopted gates pass. The
cause is UNIDENTIFIED, not attributed to the black law or described as random noise.
No holdout retry or fit follows it. Evidence: §5.179 `holdout-difference.json` with
coordinates, before/after values, metadata and scalars. Future raster/projection work
can investigate this on a declared non-holdout control; this tiny discrepancy does
not justify spending the same frozen holdout again.


### W36 G2 adoption closes the missing level gate, not its named gaps (2026-09-24)

**Adopted, §5.180; W36 Decision Log 4 and clause 8.** The G0 paragraph above's
“still not adopted” is its historical state. L1 now independently re-derives 140 rows
from the live matrix and the named W33 superseded files: 136 measured, four dark
inactive dark-solid means UNMEASURED, two light inactive orange-tinted impulse
capsule misses 0.066016/0.066059 against 0.055, maximum growth 0 against 0.005.
The two misses are not floored; all measured rows, including those misses, obey
growth. Three scratch mutations prove the absolute, growth and unmeasured-count
clauses fail. W34's deep-median tolerance is not adopted as a canonical row.

G1 completed the broader CSS, tinted, exterior and conditioning readings that G0
left unperformed; its qualified results remain §5.179's, not newly invented passes.
M2 retains G1's W33 reference: 26 zero wave increments, cumulative drift
−2.774796% to +1.965563% against W31. The middle/chroma diagnosis, declined receded
formula, CSS boundary and probe residuals, five-pixel holdout anomaly, and unmeasured
thick/near-black intervals above all remain open. The edge returns only under a new
charter with its colour-conditioned angular form and joint body/structure prediction
declared first; W36 has not silently authorised it or another native capture.


### W36 G2: the standing Firefox morph-release timing red recurred (2026-09-24)

The first and only full React three-engine run at the 0.24.0 preparation reads
**173 passed / 3 skipped / 1 failed**. The failure is the already-recorded W30/W31
case: `morph-materialize.spec.ts` “the end that is absent is inert, and is released
when it has gone”, Firefox, destination still mounted five seconds after Escape
(line 205, expected count 0, received 1). No React source changes at this landing;
no rerun, tolerance edit or release exception is manufactured. Log and retained
error context: `results/2026-09-24-w36-g2-landing/chain-react-e2e.txt` and
`react-first-failure-context.txt` (§5.180). It remains a disclosed driver-timing
class, not a claim that this gate proved its underlying cause or fixed it.


### W36 G2: `/laws/` black endpoint and stale tone prose closed by fix (2026-09-24)

The page promised a black-to-white sweep while its slider started at0.002 linear,
above W36's compact support; its literal anchors and “unchanged byte for byte”
black-collapse sentence described the old26.5 curve. The lower stop is now0 and
prose follows the selected macOS27 four-anchor response plus separate black branch,
with grey/chroma and thick-black qualifications. The existing ground-control case
fails on fill(0) before the fix; all10 laws cases pass after. The hardware live-eye
stage repeats byte-identically and its named label-free rectangle readsRGB132.
This is a consumer/control correction, not a material refit. Evidence §5.180's
`demo-black-control-red.txt`, `demo-laws-green.txt`, `demo-black-reading.json`.

## W37 closed at the finding: the edge needs a directional term and a native experiment (2026-09-25)

§5.181–§5.182; `results/2026-09-25-w37-g0-edge-identification/`, `…-w37-g0b-edge-identification/`.
Five declared families on native pixels reach 8.13 codes at best on the greys' straight bins;
Apple's top and bottom edges differ (250 / 253 at matched depth) so no even-normal law closes.
Nothing shipped moved. **Shape of the work:** the charter's Deferred at close — a signed-normal
term declared first, a native experiment under X5 (matched top/bottom controls, a subpixel-phase
mechanism proved reachable, a second calibration span, a larger circular radius), and, cheaper and
never scored, an existing-leaf refit with the rim's axis rotated to vertical and its width narrowed
on the four macOS 27 documents. The forward model for any thin feature should area-integrate its
kernel over pixels (G0b's integrated ramp reproduces the line's rows before any fit); the runtime's
`rw`, sampled per pixel, has not been checked against that integral.

## W38 closed at the finding: the neutral rim cannot be re-aimed without a colour term; the collapsed rim is unexercised by every gate (2026-09-25)

§5.183; `results/2026-09-25-w38-g0-rim-axis-cut/`. The per-channel-bin regression veto is what
caught a 47-code whitening that every stratum aggregate called an improvement — keep it as the
acceptance shape for any future rim or edge change (E2's 212-row proposal and R1 are in the
charter). Two debts: (1) no canonical cell or named fixture resolves a collapsed rim (T = 0 on all
212 active rows), so `rimCollapsed` / `rimCollapsedTinted` are unpriced by every gate — a fixture
that resolves T > 0 is needed before any rim change is called priced there; (2) `rimLitAxis`
ships as the literal [−0.7071, −0.7071], 8.15 ppm from unit — harmless, recorded. **Shape of the
work:** the native colour-model bed of W38 Deferred at close 1, captured with the edge's
directional controls in one sitting under X5.

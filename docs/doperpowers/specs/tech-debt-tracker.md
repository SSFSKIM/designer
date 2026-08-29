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

Observed: with `reduceTransparency = 1` system-wide, seven `@vitrea/platform-web`
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

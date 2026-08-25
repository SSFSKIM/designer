# apps/reference-apple

The **native SwiftUI capture harness** for vitrea's calibration methodology —
child **C7** of `docs/doperpowers/specs/2026-08-24-vitrea-liquid-glass-design.md`
(§Calibration harness & methodology, contract X9).

It renders the canonical scene matrix with the real Liquid Glass API surface and
captures it into versioned fixture profiles. Fixture *schema* and diff *metrics*
live in `packages/calibration`; this app produces the native side.

No workspace `package.json` here on purpose — pnpm only picks up directories that
have one, so the Xcode toolchain stays out of the JavaScript graph.

## Running it

```sh
./capture.sh backgrounds     # the shared raster backgrounds (no GUI, no permission)
./capture.sh probe           # measure which capture paths work on this machine
./capture.sh capture         # the fixture matrix (ScreenCaptureKit; needs the TCC grant)
./capture.sh capture --method nsview-cachedisplay   # explicit material-free fallback
```

`VITREA_SCALE=2 ./capture.sh ...` targets the spec's canonical 2x profiles.

`build.sh` invokes `swiftc` from the Xcode toolchain **directly**, with an
explicit `-sdk`, rather than through `xcodebuild` or SwiftPM. There is no
`.xcodeproj`. Both choices are deliberate and both are recorded in `build.sh`'s
own header; the short version is that the license-gated wrappers do not currently
run on this machine (see below) while the compiler itself does, and that a
generated `pbxproj` would be a second, staler description of four source files.

## The capture wall

**Liquid Glass cannot be captured on this machine right now.** This is the
harness's most important finding, so it is stated before anything else it
produces, and every number below is measured by `./capture.sh probe`.

The material is composited by the **window server**, not by the application. The
app submits a layer tree; the glass body, its lensing, tint, rim and shadow are
resolved out of process. So no in-process rendering path can observe it, and this
is architectural rather than incidental:

| path | result | measured |
| --- | --- | --- |
| `SwiftUI.ImageRenderer` | renders **nothing** — the material is absent *and* the wrapped content is dropped | a `glassEffect` subtree vs. a bare rect of the same size differs by mad **0.0000**, max **0** |
| `NSView.cacheDisplay(in:to:)` | renders wrapped *content* but no material | captures are byte-stable on repeat; all 30 are **pixel-identical to their own background** |
| `CGWindowListCreateImage` | **API removed** — a hard compile error in the macOS 26 SDK ("Please use ScreenCaptureKit instead"), not merely deprecated | — |
| `SCScreenshotManager` (ScreenCaptureKit) | the only path that sees the real material | **blocked**: `SCStreamErrorDomain` **-3801**, TCC denied |

`-3801` persists for the app's *own* window, for an ad-hoc-signed `.app` bundle
with its own `CFBundleIdentifier`, and when launched through LaunchServices
rather than a shell — and **no permission dialog is presented**, which means a
denial is already on record for the responsible process rather than the grant
merely being unrequested.

### What is needed

Grant **Screen Recording** to this harness, then re-run `./capture.sh capture`:

1. System Settings → Privacy & Security → Screen & System Audio Recording.
2. Add `apps/reference-apple/build/VitreaReference.app` (built by `build.sh`), or
   the terminal application that runs the script, and enable it.
3. If an entry already exists and is off, remove it and re-add — a recorded denial
   suppresses the prompt.

Nothing else about the harness changes. The same command then writes the same
fixture keys with `captureMethod: "screencapturekit"` and
`materialRendered: true`, so the real captures land as a clean diff over the
provisional ones.

## What is committed today

- `fixtures/backgrounds/` — the six shared raster backgrounds, **byte-stable** and
  genuinely useful now. Both renderers composite these exact PNGs, which is the
  spec's rule that font and asset rasterisation must never reach the diff.
- `fixtures/<profile-key>/` + `fixtures/manifest.json` — the matrix captured via
  `nsview-cachedisplay`. These are **provisional and material-free**: the manifest
  marks every entry `materialRendered: false` and
  `identicalToBackground: true`, and carries the measured caveat that 30 of 30
  contributed no pixels. They exist to exercise the capture → diff → matrix
  pipeline end to end. **No fidelity claim may cite them.**
- `scenes.json` — the canonical scene matrix, read by this harness *and* by the
  web calibration page, so the two sides cannot drift on geometry.

## API-surface reality vs. what the spec assumed

The spec's assumptions held better than expected. On macOS 26.5.2 with Xcode 26.6
(SDK `MacOSX26.5.sdk`), all of these compile and are used here as written:
`glassEffect(_:in:)`, `GlassEffectContainer(spacing:)`, `Glass.regular`,
`Glass.interactive()`, `Glass.tint(_:)`, `glassEffectID(_:in:)`, plus
`GlassButtonStyle` / `GlassProminentButtonStyle`.

Two divergences are worth recording, because both changed this harness's design:

1. **Accessibility modes are not settable per view.**
   `\.accessibilityReduceTransparency`, `\.accessibilityDifferentiateWithoutColor`
   and `\.colorSchemeContrast` are **get-only** `EnvironmentValues`. Only
   `\.colorScheme` is writable. So light and dark profiles capture in one run, but
   each accessibility profile needs its own run with the matching System Settings
   toggle. The harness reads the real system state
   (`NSWorkspace.accessibilityDisplayShould…`) and **skips** any profile whose key
   claims a mode the machine is not in, rather than emitting a mislabelled
   fixture.

2. **The scale axis cannot reach 2x here.** This Mac is a Mac14,12 driving a
   1920×1080 display, so `backingScaleFactor` is **1.0** and the profile keys read
   `apple-macos-26.5-1x-…`, not the spec's canonical `-2x-`. Configuring
   ScreenCaptureKit to twice the window size would upsample, not render at 2x, so
   the harness records the real scale and files a caveat instead. A Retina display
   or a HiDPI display mode is what closes this.

## A note on the toolchain gate

The Xcode license on record is for **Xcode 16.4**
(`IDEXcodeVersionForAgreedToGMLicense` in
`/Library/Preferences/com.apple.dt.Xcode.plist`) while the installed Xcode is
**26.6**. Every license-gated wrapper — `xcodebuild -showsdks`, `xcrun`, `swift`,
and therefore SwiftPM — refuses until someone with admin rights runs
`sudo xcodebuild -license accept`. The compiler binaries are not gated, which is
why `build.sh` calls `swiftc` directly and works today. Accepting the license
changes nothing here; it would only open SwiftPM as an alternative.

## Why the scenes carry no text

The components are bare material bodies — no labels. A glyph inside the measured
region would put two different text rasterisers inside the material axis, which is
the one place the spec's raster-background rule exists to keep clean. The
`hc-text` background provides high-contrast text *structure* as geometric bars
for the same reason. Label semantics are proven separately on the web side
(parent acceptance #1); they are not part of a material measurement.

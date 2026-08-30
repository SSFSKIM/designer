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
./capture.sh tint-doctor     # what each tinted scene hands Glass.tint(_:) (no GUI, no permission)
./capture.sh capture         # the fixture matrix (ScreenCaptureKit; needs the TCC grant)
./capture.sh capture --method nsview-cachedisplay   # explicit material-free fallback
```

`tint-doctor` answers, without opening a window or capturing anything, where a
lost tint colour was lost: the `Color` each registry entry builds, what SwiftUI's
own `Color.resolve(in:)` and AppKit's `NSColor` make of it, and — because `Glass`
is `Equatable` and its equality is colour-sensitive — whether the resulting
material value still tells two hues apart. That last probe is the one that
separates "this harness dropped the seed" from "the material ignored it", and it
needs no TCC grant to answer.

`VITREA_SCALE=2 ./capture.sh ...` targets the spec's canonical 2x profiles. It
needs **both** a 2x display and `-2x-` profile entries in `scenes.json`, and
neither exists yet — see "The scale axis cannot reach 2x here" below. Run
`./capture.sh backgrounds` before `./capture.sh capture` at any scale: capture
composites the backgrounds it renders in memory and records their paths, but only
the `backgrounds` subcommand writes those files, so capture verifies each recorded
PNG is pixel-identical to what it composited and refuses if it is stale.

`capture` stages the whole bundle in `fixtures/.staging-<uuid>` and promotes each
profile directory and `manifest.json` into place with an atomic replace only at the
end, so an aborted run leaves the previously committed fixtures — and the manifest
that describes them — exactly as they were. Any failure removes its own staging
directory; a hard crash may leave one behind, and it is safe to delete.

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

- `fixtures/backgrounds/` — the seven shared raster backgrounds, **byte-stable** and
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

Compiling is a weaker claim than taking effect, and `Glass.tint(_:)` is where the
difference bit — see divergence 3.

Four divergences are worth recording, because each changed this harness's design:

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

   `VITREA_SCALE=2` is therefore only half of a 2x run. Fixture directories and
   manifest keys are the profile key verbatim, and `scenes.json` declares `-1x-`
   profiles only — so a genuine 2x capture would write 640×400 pixels under keys
   claiming 1x. The harness checks the selected profile keys against the
   scale it is actually about to capture at and refuses before writing anything;
   the 2x recapture session has to add `-2x-` profile entries to `scenes.json`
   first.

3. **`Glass.tint(_:)` compiles, is called correctly, and its hue does not reach
   the composited material.** The 2026-08-30 bed's 18 tinted cells carry the
   tint's strength and none of its colour: `systemOrange` and `systemBlue` came
   back byte-identical over three backdrops at both scales.

   `tint-doctor` localises that, and the answer is not in this harness. On macOS
   26.5.2 / Xcode 26.6 / SDK `MacOSX26.5.sdk`, for every registry tint:

   - the `Color` resolves to exactly its declared sRGB triple and alpha, under
     `Color.resolve(in:)` in both colour schemes and under
     `NSColor(_:).usingColorSpace(.sRGB)`;
   - the `Glass` value **does** carry the hue —
     `Glass.regular.tint(orange) != Glass.regular.tint(blue)`, against a control
     proving that equality is colour-sensitive (the same colour built twice
     compares equal, and one hue at two alphas compares distinct).

   So the seed reaches the material value intact and is discarded somewhere
   between there and the window server's composite. What survives is achromatic:
   measured against the untinted twins, the tint pulls the interior toward a
   neutral grey near 140/255 at an effective alpha near 0.23, uniformly across
   R/G/B, and declaring alpha 0.5 halves that. Strength honoured, hue dropped.

   The harness's own usage is the documented one — `Glass.tint(_ color: Color?)`
   applied to the `Glass` value, exactly as the SDK declares it. The fault was not
   the call but the conditions it was made under: see divergence 4.

4. **The capture window could never become key, so the whole bed recorded the
   material's INACTIVE appearance.** Apple documents `NSWindow.canBecomeKey` as
   "`true` if the window has a title bar or a resize bar, `false` otherwise" — and
   this harness captures through a **borderless** window on purpose, so that a
   window capture needs no cropping or titlebar subtraction. Measured: before the
   fix the capture window reported `canBecomeKey: false, isKeyWindow: false,
   isMainWindow: false, NSApp.isActive: false`, through every capture of every
   committed fixture. The app also took `.accessory` activation policy, which
   keeps it from becoming active at all.

   Liquid Glass has an active and an inactive appearance and the window server
   picks between them from that state, with the inactive one widely reported as
   flat and neutral. Apple defines the tint as "a range of tones that are mapped
   to content brightness underneath" — a hue mapped onto a sampled backdrop — so
   the inactive material has nothing for a hue to land on, and only the tint's
   alpha still means anything. That is exactly the bed's measurement.

   The fix is three changes, all in this harness: `Capture.CaptureWindow`
   overrides `canBecomeKey`/`canBecomeMain`; `Capture.present(_:)` activates the
   app **before** making the window key, rather than the reverse; and the app now
   takes `.regular` activation policy (`VITREA_ACTIVATION_POLICY=accessory`
   restores the old behaviour for non-capture use). `canBecomeKey` is verified
   `true`. Whether the window then actually becomes key, and whether the hue
   lands, is **not** verified — this machine's session refuses to activate the app
   at all, so that proof needs one granted capture in an interactive login
   session.

   Because it is unproven, it is also recorded: every fixture carries
   `presentedActive`, and a run that captures anything inactive says so in the
   manifest's caveats.

## The tint attestation

Every tinted capture records the colour it applied and whether any of it came out
the other side. The fixture entry carries a `tint` object — the declared sRGB and
alpha, what `Color.resolve(in:)` made of them, the resolved chroma, and the two
booleans `tint-doctor` reports — plus a `chromaShift` field on **every** fixture,
tinted or not, measuring the chroma the component added over its own backdrop.
The untinted cells are the control: untinted Liquid Glass slightly desaturates
(this bed reads −3.9…0.0), so "did a tint add colour" is only answerable against
that baseline.

At the end of a run, before anything is promoted out of staging, two tests run:

- **Identity.** Two scenes sharing a backdrop, component and state, differing only
  in which tint they declare, must not produce identical files. No threshold and
  no colour model — `systemOrange` and `systemBlue` are not the same colour. This
  is the test that condemns.
- **Response.** A tinted capture's `chromaShift` must exceed its untinted twin's
  by more than 1.0 (0…255 chroma units). Weaker, because it needs a floor, but it
  reaches the case identity cannot: a bed declaring one seed per scene has no
  identical pair to find.

A run that fails either **publishes nothing** — the committed fixtures and
manifest are left exactly as they were — and prints every offending cell.
`--allow-colourless-tints` publishes anyway with the finding recorded in the
manifest's caveats, mirroring `compare.ts`'s flag of the same name on the
consumer side. A tint that is lost *before* the API instead (a resolved colour
that has gone grey, or a `Glass` value that stops distinguishing hues) fails
immediately at the cell, because that would be a fault in this harness rather
than in the material.

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

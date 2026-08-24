# apps/reference-apple

Placeholder. This directory holds the **native SwiftUI capture harness** for
vitrea's calibration methodology — child **C7** of
`docs/doperpowers/specs/2026-08-24-vitrea-liquid-glass-design.md`.

It stays a README until Xcode is available on the capture machine, because the
harness is an Xcode project plus capture scripts, and neither can be authored
honestly without building and running them.

## What lands here (C7)

- An Xcode/SwiftUI app rendering the canonical scenes: backgrounds
  (light/dark solids, photo, high-contrast text, video, impulse, checkerboard) ×
  components × interaction states × sizes.
- Capture scripts producing versioned fixture profiles keyed as
  `apple-macos-26.5-2x-light-standard` — OS, hardware, scale, colour scheme,
  accessibility mode, capture method, refresh rate (X9).
- Identical pre-rendered raster backgrounds shared with the web renders, so
  font-rasterisation differences never pollute a diff.

Fixture *schema* and diff *metrics* live in `packages/calibration`; this app
produces the native side of the comparison. Captures are machine-local; fixtures
and thresholds are committed and CI-diffable.

No workspace `package.json` here on purpose — pnpm only picks up directories that
have one, so this stays out of the JavaScript graph.

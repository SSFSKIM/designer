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

## Where the contracts live

| contract | made true in |
| --- | --- |
| X3 — BackdropFrame protocol (this child owns its operational detail) | `src/backdrop.ts` |
| X5 — colour pipeline | `src/color.ts`, `src/wgsl/prelude.ts` |
| X8 rider 2 — concentric renders as a level set of the parent's field | `src/instances.ts`, `src/wgsl/field.ts` |
| §Core model — ≤1 pyramid rebuild per dirty source per frame | `src/rebuild-ledger.ts` |
| Decision Log #19 — the dual refraction cap | `src/material.ts` |
| Decision Log #20 — family C's f32 cross-check | `src/governor.ts` gates it; `test/f32-cross-check.test.ts` and `e2e/gpu/cross-check.spec.ts` run it |

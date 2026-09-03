# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Two artifacts, one repository

- **`designer`**, a Claude Code plugin. Everything loaded at runtime is under `skills/designer/`
  (`SKILL.md`, `references/`, `personas/`, `scripts/`). `Figma Design/`, `docs/research/` and
  `evals/` are its source material and are never loaded.
- **vitrea**, a TypeScript runtime replicating Apple's Liquid Glass on the web, under `packages/`
  and `apps/`. The plugin never loads any of it.

`docs/doperpowers/specs/` is the project's memory for both. Specs are composite: design at the top,
Decision Log, Surprises, Deferred and Revision Notes at the tail. Read the relevant spec before
changing behaviour it governs; write to it when you change or learn something.

## Commands

Workspace (pnpm, Node ≥ 24):

```bash
pnpm install
pnpm -r build && pnpm -r lint && pnpm -r test     # what CI's verify job runs (also: pnpm run ci)
pnpm --filter <package-name> test                  # one package's unit suite (vitest)
pnpm --filter @vitreajs/vitrea-web exec vitest run test/css-tier.test.ts -t "a test name"
```

Filters take the **package name**, not the directory: `@vitreajs/vitrea` (core),
`@vitreajs/vitrea-web` (platform-web), `@vitreajs/vitrea-react` (react); the private packages are
`@vitrea/renderer-webgpu`, `@vitrea/calibration`, `@vitrea/policy`, `@vitrea/geometry`,
`@vitrea/motion`; the demo is `demo`. A filter that matches nothing exits 0 and runs nothing, so
scripts and workflows pass `--fail-if-no-match`.

Browser suites (Playwright; each package has its own config):

```bash
cd packages/platform-web && npx playwright test                      # chromium, firefox, webkit, chromium-gpu
cd packages/platform-web && npx playwright test e2e/shared/proxies.spec.ts --project=chromium
pnpm --filter @vitreajs/vitrea-web test:e2e:gpu                      # e2e/gpu on a real adapter
pnpm --filter @vitreajs/vitrea-react test:e2e                        # three engines
pnpm --filter demo test:e2e
pnpm --filter @vitrea/renderer-webgpu test:golden                    # also test:gpu, test:bench
```

Pixel assertions run on Chromium only: Gecko and WebKit render `backdrop-filter` as a no-op in every
automatable capture path. Anything needing a real GPU launches the full Chromium binary
(`channel: "chromium"`); the default headless shell hands back SwiftShader and would pass everything
against a CPU rasteriser. `VITREA_ALLOW_FALLBACK_ADAPTER=1` opts into the software path
deliberately (CI does). The e2e suites inherit the machine's Reduce Transparency / Increase Contrast
settings, which Playwright cannot emulate; keep them off when running locally.

Renderer goldens: `goldens:regen` only behind the isolation proof in
`packages/renderer-webgpu/e2e/golden/isolation.spec.ts`. That spec pins hashes so that every
golden change is attributable to a named constant or law; re-record its hashes with the reason.

Demo: `pnpm --filter demo dev` (the site, plus `/playground/`). Deploys to GitHub Pages on every push
to `main`.

Plugin: `node --test skills/designer/scripts/*.test.mjs` and `claude plugin validate . --strict`.

Calibration (the fidelity harness, `packages/calibration`):

```bash
pnpm --filter @vitrea/calibration run compare -- --scene photo__rrect-md__rest
pnpm --filter @vitrea/calibration run compare -- --profile apple-macos-26.5-1x-light-standard \
  --material-profile profiles/apple-macos-26.5-1x-light-standard.json --renderer webgpu \
  --set calibration,validation --write-partial
pnpm --filter @vitrea/calibration run compare -- --set holdout    # once per frozen configuration
```

`--renderer` is one tier per run; `--set` defaults to `calibration,validation` and holdout membership
is read from `apps/reference-apple/scenes.json`, never named in code. `--out-matrix` and the
`VITREA_WEB_CAPTURES` env redirect output to scratch; the canonical `results/matrix.json` and
`web-captures/` are committed evidence. A cell's key includes the material profile document's hash,
so after the profile changes a run **appends** beside the old rows: `rm results/matrix.json`
before a full rebuild, or reduce to the newest row per key.

Release: changesets under `.changeset/` (fidelity changes are `@vitreajs/vitrea-web` minors; the
three published packages are a `fixed` group). `pnpm changeset version`, commit, then
`pnpm release` is the only sanctioned publish path — pnpm rewrites `workspace:` ranges in the
tarball and npm would not. The user publishes (npm 2FA); tag `v<version>` and push tags after.
`docs/doperpowers/specs/c9d-release-checklist.md` is the chain a release must show green.

## Architecture

**Layering.** `core` (`@vitreajs/vitrea`) is the pure runtime: the scene model (groups, surfaces,
backdrop sources, planes), capability and tier resolution, material and accessibility policy.
`platform-web` (`@vitreajs/vitrea-web`) is the **only package allowed to touch the DOM**:
`createGlassRoot`, host registration, the batched read protocol (`measure.ts`), the plane sandwich
(optics canvas → semantic host DOM → highlight canvas), one masked backdrop proxy per sampling
group, the CSS tier, the media-query policy feed and the WebGPU lifecycle through
`renderer-bridge.ts`. `react` (`@vitreajs/vitrea-react`) is bindings over that. `renderer-webgpu`,
`policy`, `geometry` and `motion` are private and bundled into `vitrea-web` at publish time.
`core`, `geometry` and `motion` compile without the DOM type library, ESLint fails on DOM globals by
name, and `packages/core/test/purity-law.test.ts` seeds a violation on every run to prove both fire.

**Two tiers, one profile.** Every group resolves to a renderer (`webgpu` or `css`) and a sampling
backend (`gpu-texture` for a registered image/canvas/video, `css-backdrop` for a DOM proxy beneath
the canvas, `none`). The resolved `GlassGroupState` is the honesty core: capture cells, readouts and
tests read what actually drew, never what was asked for. The WebGPU tier's material lives in
`packages/renderer-webgpu/src/material.ts` (`DEFAULT_MATERIAL_PROFILE`, the size law, scatter,
backdrop tone response, tint shade, lens) and its passes in `src/wgsl/` (analysis → optics →
highlight). The CSS tier derives its material from the **same profile** through
`packages/platform-web/src/optics.ts` and `css-tier.ts` (one in-place `backdrop-filter` and one
`rgba()` layer), and `packages/calibration/test/tier-coherence.test.ts` pins the two tiers to each
other. A material change is not landed until both tiers carry it. An author backdrop hint
(`hint={{ luminance }}`) takes precedence over sampling on both tiers, so a hint must state the
real backdrop level.

**Calibration.** `apps/reference-apple` is the SwiftUI harness that captures Apple's own material
(ScreenCaptureKit, macOS 26.5) into fixtures keyed `apple-macos-26.5-{1x,2x}-{light,dark}-…`;
`scenes.json` there is the single source for scenes, components, radii and the
calibration/validation/holdout split. `packages/calibration` captures the web side in real Chromium
at the fixture's pixel size, diffs per cell (silhouette, contour, SSIM, OKLab ΔE, interior level,
cross-tier coherence) and writes `results/matrix.json`. `profiles/*.json` are the material profile
documents: the light patch names every fitted constant and carries `resolvedMaterialSha256` over
the fully resolved material; the dark profile is a difference document. Adopted bounds,
regression floors and the conditioning predicate are enforced by
`packages/calibration/test/adopted-thresholds.test.ts`; its `PREDICATE_EXCLUDES` must equal the
machine's output, so a fidelity change usually moves that file too.

**The fidelity discipline.** `docs/doperpowers/specs/c9a-fidelity-claims.md` is the ledger: every
measurement, every adopted bound, every floor and why. Work runs as waves (composite specs dated
under `specs/`): declare what will be measured and what would stop the change **before** running
it, fit or fix, referee against the frozen bed, record. Floors come off by fix; re-pinning a floor is
a user decision recorded in the wave's Decision Log. Holdout is read once per frozen configuration.

**Document every gap to macOS.** The goal is the least possible gap between vitrea and Apple's
material, so every gap is future work and none is accepted silently: a metric that misses, a bound
that had to be narrowed, a claim held by decision, or a difference seen by eye that the metrics
do not catch. Record it where it belongs — a claims section, the wave's Deferred list, or
`specs/tech-debt-tracker.md` — with the evidence and the shape of the work that would close it.
Metrics are not the whole verdict: when you change the material, put the capture next to the
native fixture (and the demo next to the harness capture) and look. SSIM can score well on a
blurred interior while the eye sees the rim band, the lens curvature or the haze differ.

## Conventions

- No prettier; format by hand to the surrounding style, about 100 columns. Rationale lives in doc
  comments next to the code it explains, in full sentences; keep that when editing.
- Commit messages carry a title and an explanatory body that cites the claims section or Decision
  Log the change executes.
- Scenes, fixtures, profile documents and matrices are committed evidence; never rewrite a recorded
  hash or number to what a file "should" have had — add the correct reading beside it.

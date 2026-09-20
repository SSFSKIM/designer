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
pnpm --filter @vitrea/calibration run compare -- --profile apple-macos-27.0-1x-light-standard-glass0.5 \
  --material-profile profiles/apple-macos-27.0-1x-light-standard-glass0.5.json \
  --receded-profile profiles/apple-macos-27.0-1x-light-standard-glass0.5-receded.json \
  --renderer webgpu --set calibration,validation --write-partial
pnpm --filter @vitrea/calibration run compare -- --set holdout    # once per frozen configuration
```

`--renderer` is one tier per run; `--set` defaults to `calibration,validation` and holdout membership
is read from `apps/reference-apple/scenes.json`, never named in code. `--material-profile` also
**selects the runtime material its patch is a difference from**, by the OS token in the document's
own `profileKey`: the web page refuses a token the runtime ships no material for, because a macOS
26.5 patch composed over the macOS 27 base is neither material. `--receded-profile` poses the run's
`__inactive` scenes with a CANDIDATE document and pins the root active; omit it and the root poses
itself and applies the receded endpoint of the document it selected. `--out-matrix` and the
`VITREA_WEB_CAPTURES` env redirect output to scratch; the canonical `results/matrix.json` is
committed evidence, and the canonical `web-captures/` beside it is gitignored — it lives on the
capture machine and is what the sheets and the demo fixture are copied from.

**Generations, and where the superseded ones live.** A cell's key includes every material profile
document's twelve-hex content hash, so a refit that moves a document does not overwrite the rows
read at the old one — the next run **appends** a generation beside them, because a recorded number
is never rewritten. The working file holds **one generation per profile** and the superseded ones
are moved, byte for byte, to `results/superseded/<active-document-sha>.json`, named by the ACTIVE
document (a receded document is a difference over it and never names a file);
`results/superseded/index.json` maps every document hash, active and receded, to the file holding
its rows, and `README.md` there is generated from that index. The gate that moves them runs after
the read that superseded them:

```bash
python3 results/2026-09-20-w30-g1-split/split-generation.py plan      # what would move, and where
python3 results/2026-09-20-w30-g1-split/split-generation.py apply \
  --evidence results/<this-gate>/ --claims "c9a §5.NNN" --read-claims "c9a §5.MMM"
```

Never delete the working file and never "reduce to the newest row per key": 1,107 of its rows are
frozen macOS 26.5 evidence whose hashes `results/2026-09-16-w29-freeze/freeze.py verify` checks,
and a row of a frozen profile selected to move is refused before a byte is written. The demo reads
a build-time projection of the current generation (`apps/demo/matrix-reduction.ts`), not the file,
so the page's figures do not depend on its size.

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
other. The WebGPU tier is the fidelity target (wave Decision Log 23, 2026-09-05): a material change
lands on it, the CSS tier derives what its two layers can carry from the same profile in the same
wave, and a CSS-only residual is recorded in the ledger rather than chartered. An author backdrop hint
(`hint={{ luminance }}`) takes precedence over sampling on both tiers, so a hint must state the
real backdrop level.

**Calibration.** `apps/reference-apple` is the SwiftUI harness that captures Apple's own material
(ScreenCaptureKit) into fixtures keyed `apple-macos-<os>-{1x,2x}-{light,dark}-<a11y>` — the macOS
26.5 keys are frozen evidence and the macOS 27 keys carry a trailing `-glass0.5`, the appearance
slider's attested position (W29, X6);
`scenes.json` there is the single source for scenes, components, radii and the
calibration/validation/holdout split. `packages/calibration` captures the web side in real Chromium
at the fixture's pixel size, diffs per cell (silhouette, contour, SSIM, OKLab ΔE, interior level,
cross-tier coherence) and writes `results/matrix.json`. `profiles/*.json` are the material profile
documents: a light patch names every fitted constant and carries `resolvedMaterialSha256` over
the fully resolved material, the dark profile is a difference document over it, and a
`-receded` document is the unfocused-window difference over the active document of its own scheme.
Adopted bounds,
regression floors and the conditioning predicate are enforced by
`packages/calibration/test/adopted-thresholds.test.ts`; its `PREDICATE_EXCLUDES` must equal the
machine's output, so a fidelity change usually moves that file too.

**Which material a page draws, and how the runtime says so.** The renderer's `DEFAULT_MATERIAL_PROFILE`
is the macOS 26.5 light material and does not move (W29 Decision Log 1 (i)) — every shipped material
is a patch over it, which is what keeps the frozen macOS 26.5 documents' fingerprints green. Which
patch a root resolves is a **selection**: `packages/platform-web/src/material-document.ts` holds one
document per measured material (four patches — active and receded, per scheme — plus the CSS
crossing), `macos27MaterialProfileDocument` is the default from 0.19.0, `macos26MaterialProfileDocument`
is shipped beside it, and `createGlassRoot({ materialProfileDocument })` chooses. `src/macos27-profile.ts`
is generated from the four macOS 27 documents by `scripts/generate-macos27-profile.mjs` and pinned to
them by `packages/calibration/test/macos27-profile-export.test.ts`, as `src/dark-profile.ts` is by its
own sibling pair. `root.material` and `GlassGroupState.materialDocument` report the endpoint that
actually drew, its digest, and whether an app tuned it — the honesty core, one axis further; in
React the selected document itself is on `GlassRootHandle`, which is what lets `GlassToolbar`
derive a layout number from its own material rather than from the default one.

**Two of the material's operators are functions of the surface rather than constants** (W30, claims
§5.159). The outer shadow's blur is graded by the CASTING SPAN —
`σ(span) = sigmaPx + max(sigmaThinOffsetPx, sigmaSlopePerSpan · (span − sigmaSpanRefPx))`,
evaluated per pixel from the field pass's aux target on the WebGPU tier and per surface into one
`box-shadow` blur radius on the CSS tier, with the group clip and the scissor pad taking it at the
widest member as a BOUND. And the scatter is conditioned on the backdrop's measured spatial scale
(`sizeScatterScaleGain` / `sizeScatterScaleRef`, keyed on the analysis pass's per-source statistic),
adopted on the dark document and declined on the light one with both declines recorded as
measurements. A leaf that is a law rather than a value has to be mirrored on both tiers and pinned
by `tier-coherence.test.ts`; `w30-inert-laws.test.ts` holds each law's identity and the reach's
monotonicity.

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

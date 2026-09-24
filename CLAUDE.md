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

**And a capture tree is only that if somebody copies it there.** That last sentence was false from
W29 to W31: every canonical read ran in an agent worktree, captures are gitignored, a worktree
inherits none, and the worktree was removed after merge — so the pixels each generation of rows was
measured off were deleted as the rows landed, and the macOS 26.5 tree that did survive turned out to
be a DIFFERENT generation from the rows beside it (two cells of one scene disagree; W31 charter
Surprises, claims §5.161 §2). **Copying the read's tree to the canonical path is part of the merge
that lands the read**, and a sheet script reads that tree and asserts per cell that the capture names
the shipped document bytes — the receded document included — rather than trusting the path
(`results/2026-09-21-w31-g4-landing/sheets.ts`). **And since W32 G0b a tool checks the tree against
the matrix**: `pnpm --filter @vitrea/calibration run check-capture-tree` compares every capture's
document hashes — the receded document included — against the row beside it and reports match,
mismatch, misfiled, superseded, unreadable, no-row and rows-with-no-capture, exiting 0 clean, 1 on
a live mismatch and 2 on a generation difference under a FROZEN key alone. Run it on the canonical
tree at every merge that lands a read; it is deliberately not wired into `pnpm -r test`, because
the tree is not in the repository and an absent tree is one line and exit 0. What it checks is a
GENERATION and not a capture: the frozen macOS 26.5 tree reads as MATCHING because those documents
have not moved, so a re-capture at unmoved bytes is invisible to any string compare (W32 G0b, claims
§5.167 §3; the narrowed tracker entry). **The generation a read supersedes moves to
`packages/calibration/web-captures-superseded/<active-document-sha>/`**, named by the ACTIVE
document exactly as the superseded matrix rows are, so the pixels a retired row was measured off
stay findable by the same name the rows are.

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
machine's output, so a fidelity change usually moves that file too. That file's header argues the
MATERIAL axis is not gateable on this fixture set, and since W31 it carries rows that are —
`M1` on the body's chroma-to-structure ratio, `M2` on the structure it is read over, since W32
`C1` on the outer shadow's exterior SHAPE per span, and since W33 `X1` on its native-black floor —
macOS 27 standard profiles and the WebGPU tier only, each with an amendment beside the header
saying why it clears both of the argument's grounds.
`C1`'s amendment also says why the sub-metric §6.1 calls unidentifiable is STILL not gated: the
fitted-σ candidate was declared beside `C1`, halved by W32's fit and is outside its window on all
twelve bed × span rows, so it stays a one-wave reading, and the adopted row is the one that reads
the falloff's shape without fitting a σ to it. All four read a cut **regenerated at the gate that
adopts them**. M1/M2/C1 are re-derived from `results/matrix.json`; X1 re-derives every pixel
count from its matrix-named captures and reports UNMEASURED when that tree is absent. X1 covers
218 non-holdout standard-profile single-shape cells in both poses, including probe-strength span
160; composites and accessibility are declined. This is how a cut avoids becoming a frozen
snapshot a bound can never fail against (claims §5.162 §9, §5.165 §1, §5.169 §1, §5.173).
`M2` is a regression stop rather than a fidelity bound and its reference generation is
**re-baselined at each gate that adopts a material change** (W32 Decision Log 4, ruled), so it
bounds one wave's change and the cumulative drift is tabled in the ledger instead of bounded
(§5.169 §3).

**A leaf at its declared identity moves no document's digest** (W31 Decision Log 1 (a), ruled; claims
§5.161 §7b, §5.164 §2). `resolvedMaterialSha256` is taken over the fully resolved material, so before
W31 adding an operator moved every document's fingerprint whatever that operator held, and a wave had
to spend an exemption to add one. **Rule 2** drops, before hashing, every entry of
`MATERIAL_IDENTITY_TABLE` — an append-only constant beside `DEFAULT_MATERIAL_PROFILE` in
`packages/renderer-webgpu/src/material.ts` — whose gate leaves all hold their declared identity
values. An entry with no gated leaves is a plain value drop; an entry WITH them is a **gate-group**
and goes as one unit, because a gated leaf has no identity of its own to be at. `materialDigestInput`
is the one implementation of the drop and is imported by all three sorted-key SHA-256 copies; the
rule's version is recorded in every document sealed under it, so a recorded digest names the function
that produced it. Two consequences to know before touching a digest: the identity table makes a
post-seal leaf's default **its identity, forever**, and the two frozen macOS 26.5 documents' own
recorded fields are the live pin again — `profiles/digest-supersessions.json` is HISTORY, kept, with
a test that reproduces both halves of every record and nothing reading it as a pin.
`w31-identity-table.test.ts` pins the table to W31 G0's declaration by SHA-256 and each gate's
identity as a literal, and `w31-gate-groups.test.ts` proves each group's drop by sweeping the gated
leaf off its value with the gate held.

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
derive a layout number from its own material rather than from the default one. **Since 0.22.0 an
app reaches that same handle through `useGlassRootHandle`** (W32 Decision Log 5, ruled; the README
had promised the hook since 0.20.0 while the package exported only the TYPE and `useGlassRoot`). What
it hands an app is the SELECTION; a reading of what DREW that is available before the first frame
is a deferred item, and a page that wants the drawn endpoint resolves it by matching the digest
`GlassGroupState.materialDocument` reports against the document's endpoints — with `tuned` read
beside it, because that digest is the endpoint's and cannot see a tune — which is what the demo's
`/laws/` shadow stage does (W32 G2 and its review closure; a tracker entry).

**The body carries the backdrop's hue, on the WebGPU tier only** (W31, claims §5.164). After
`colour = mix(backdrop, adapted, presentAlpha)` the composited colour's CHROMATICITY is restored
toward the blurred backdrop's by `bodyChromaRetention ∈ [0, 1]` — inert identity 0, fitted per colour
scheme and per window pose in the four macOS 27 documents. It is **luma-preserving by construction
rather than by correction**: both endpoints of that mix carry the same linear luma, so the mix lands
on it in exact arithmetic and the renormalisation is an f32 guard; gamut is taken by scaling chroma
toward the neutral at a held luma, never by clipping a channel. It sits before the tint composition,
so an author's tint still displaces the result, and it is the identity wherever the backdrop is
achromatic — which is why there is no `toneAdapt` gate and why a neutral backdrop draws
bit-identically to 0.20.0. **It stands down entirely under an accessibility OCCLUSION lift**
(`bodyChromaRetentionUnderPolicy`, an exhaustive switch on that axis, folded on the CPU at the
uniform's pack site because the optics uniform carries no policy): Reduce Transparency raises the
occlusion and stands it down, `forced-colors` draws no body at all, and **Increase Contrast alone
does not** — it carries no occlusion key, and that combination is unmeasured (tracker). **The CSS
tier carries none of this**: a mirror was derived from the leaf, rendered on the bed and declined on
the measurement — 0.000 of the gap on the dark scheme at every retention, both stops broken on the
light one — so `BODY_CHROMA_RETENTION` in `platform-web/src/optics.ts` is 0 with the measurement
beside it, and `tier-coherence.test.ts` pins it against the SHIPPED documents' retentions so a
document that moves one re-opens the decline instead of inheriting it.

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

**The shadow's other two lengths are fitted values, and what bounds them is a SHAPE** (W32, claims
§5.168, §5.169). Beside that σ law the outer shadow has an outset and an offset, and until W32 both
were inherited from the macOS 26.5 default and had never been fitted on the macOS 27 bed. They are
now: `spreadPx` **0.50** on the light document and **1.80** on the dark one, from 3.10, and
`offsetPx` **7.95**, refitted to itself — one leaf, the outset, moved the admitted-band objective
by a factor of three and took the shape clause from four of twelve bed × span rows to ten on its
own. Nothing in the repository pins either leaf as a NUMBER, deliberately: what bounds them is `C1`
in `adopted-thresholds.test.ts`, the exterior's shape per span at ≤ 0.0042, which is a statement
against Apple's own render rather than about a constant. The rendered σ is still 1.27–2.77 CSS px
wider than Apple's fitted σ after all of it, which is halved and not closed and is recorded, not
gated.

**The macOS 27 lift is zero by measurement, not a fitted positive floor** (W33, §5.172–§5.173).
All four endpoints hold `liftAmplitude: 0`; the frozen macOS 26.5 active documents keep
0.01 / 0.0051 because their native material has a lift. The leaf's “exactly zero over black”
is a UNIFORM-backdrop statement: its sigma-40 blurred source can carry light onto a locally black
pixel of a structured backdrop. The three active thick anchors compensate the stand-down under
C1; the near 3–6 band trades rather than staying identical. No contour leaf was added.

**And the receded documents cast no outer shadow at all** (W32 Decision Log 2, ruled on the
measurement): their six amplitude anchors, `liftAmplitude` and `reducedTransparencyOcclusion` are
**0**, because Apple's unfocused window removes no light from 3 CSS px outward on any of the 121
non-holdout inactive rows the bed carries — the native transmission reads exactly 1.000000 in every
band and the capture is byte-identical to the backdrop from 2 device px out. Their lengths stay the
active document's and are recorded as unread, since nothing draws at zero amplitude. What Apple's
macOS 27 material does have, in both poses, is a contour term vitrea does not draw. W33 found
its angular/colour/coverage law unidentified on this bed, not absent (Decision Log 3, ruled).
The next identifying capture is §5.171's path-attested circular capsules beside continuous ones,
matched continuous rectangles, uniform and gradient/frequency controls, independent x/y subpixel
phases at 1x/2x, colour-managed no-glass references and repeats before thresholds, with the split
declared before fitting; native capture needs the user to lift X5. **W34 ran that capture
(§5.174–§5.176, 2026-09-23/24):** a 592-cell probe bed with the run-to-run bar measured (≤ 0.5
code) and 672 fitted configurations, and no law closes at one code — the decisive finding is that
the declared BODY model already misses by 2–27 codes in the shell just inside the edge, where an
outside stroke has no reach, so the next question is the body's boundary behaviour, not the
stroke's colour (W34 Deferred-at-close 1). The wave's bed, archive and instrument are committed
and replayable; its holdout is spent. **W35 (§5.177) then read the body's own edge on that bed**: in
the active pose Apple's body carries a one-CSS-px bright inner line, 24–53 codes above the deep
body, that lifts the body's own saturated channels and is bright at vertical normals and faint at
horizontal — not a white band along a diagonal axis, which is what vitrea's rim is — and the
existing rim leaves cannot draw it (best 25–47 codes against one). It also read that the deep
body's LEVEL misses by 28–49 codes on blacks and over 100 on saturated channels, which is the next
wave (W36); the edge returns after it with a colour-conditioned angular law declared first. On the
CSS tier the
window-activation transition therefore fades the shadow OUT, which is what the reference does;
on the WebGPU tier the posed profile is swapped the instant the resolved
activation changes and the shadow leaves in one frame (a tracker entry). The frozen macOS 26.5
receded material draws **no outer shadow either, and never did**: `receded-profile.ts`'s shared
block sets all eight `outerShadow` leaves to 0, so the 26.5 recede has removed no light since W27c.
The macOS 27 endpoints are the ones this wave moved, from their active document's anchors to zero.

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
- When a change's sweep reports a file **"unchanged, checked"**, say what that file *claims* about
  the thing being changed, not only whether it reads it. A file that merely mentions an artefact is
  the one whose mention goes stale, because nothing executes a comment and no test reads it — a
  runtime message, a doc comment or a consumer table can describe a state that ended waves ago and
  still be "unchanged". (W30 G1 review closure and W31 G2; c9a §5.163 §5, tech-debt-tracker.)

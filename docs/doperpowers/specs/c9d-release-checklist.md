# C9d — release checklist

Child of [the vitrea composite spec](./2026-08-24-vitrea-liquid-glass-design.md).
Binding: Decision Log #30 (the release path), #31 (the gate procedure), #32 (the
K5 flow-back rulings), §What "done" looks like.

This file exists because the last few steps of a release are not code. Everything
an agent can verify is verified and checked below; everything that needs a human
at a keyboard, a real retail browser, or a second-factor device is unchecked and
says exactly what to do. **Nothing here is checked on the strength of an
expectation** — a box is ticked only where this document can name the run that
produced it.

Branch: `c9d-release`, since merged to `main`. **v1 (0.1.0) published 2026-08-26**;
of the human items only 2.1 (the labeled per-engine manual pass) remains open,
and it gates conformance-table rows, not the release — the runtime fails closed
on `"unverified"`.

---

## 1. Done and verified

### The three K5-ruled fixes (Decision Log #32(b)–(d))

- [x] **GPU-tier foreground audited, then fixed.** The audit ran first, as ruled.
      The defect reproduced in a shape K5 had not predicted — the GPU tier
      published no foreground token at all, so an app following the documented
      `var(--vitrea-foreground, …)` pattern fell back to its own ink. Measured
      verbatim on a dark-hinted surface over dark page content:
      `ink rgb(255, 255, 255) (published foreground: none) against the rendered
      surface; ratios 1.57, 1.57, 1.57, 1.57` against a 4.5 floor. After the fix:
      10.81. `packages/platform-web/e2e/gpu/foreground-audit.spec.ts`.
- [x] **The dom tier's `box-shadow` is gone**, and the gain is measured over all
      30 dom-tier cells rather than the sweep's subset: silhouette IoU
      0.7138 → 0.9446, contour p95 18.29 px → 2.72 px, OKLab ΔE 0.01661 → 0.01453,
      SSIM 0.9553 → 0.9589. Cross-tier coherence followed: ΔE 0.0080 → 0.0063 over
      the fitted sets, and the CSS tier's own ΔE against Apple 0.0116 → 0.0099.
- [x] **The reduced-transparency occlusion floor is relative**, so it cannot
      silently die again: `nominal + 0.4722 × (1 − nominal)`, the pre-C9a lift
      restored as a fraction of the headroom it closed. 0.62 → 0.799 on the
      renderer's material, 0.781 → 0.884 on the CSS tier's converted alpha, and
      it lifts at every nominal below 1 — asserted at 0, 0.05, 0.28, 0.62, 0.9
      and 0.999 on both tiers, and pinned across the tier boundary by
      `packages/calibration/test/tier-coherence.test.ts`.

### Golden regeneration behind the isolation proof (Decision Log #31(a))

- [x] **Isolation proof: nine of nine byte-identical, zero residual.** Every
      golden scene re-rendered with the pre-C9a constants injected through the
      `materialProfile` seam reproduced the committed golden exactly —
      `maxChannelDelta=0`, `differingBytes=0` on all nine. The whole visual delta
      is attributable to `tintAlpha` 0.28 → 0.62 and the old `adaptiveTintLight`,
      and nothing else that landed since those goldens were baked moved a pixel.
      The proof is kept in the suite as nine recorded hashes
      (`packages/renderer-webgpu/e2e/golden/isolation.spec.ts`) rather than
      expiring with the PNGs it replaced.
- [x] **Eyeball pass on the new renders**, one line per scene, in the
      regeneration commit. Eight goldens moved; `highlight-press-glow` did not,
      and it is exactly the one golden that was still passing — it captures the
      highlight canvas, which the tint does not reach.

### Demo fixes over the final material (Decision Log #31(b), #32(e))

- [x] **Segment labels: 1.24 → 10.54.** The token now reads
      `--vitrea-foreground`.
- [x] **Control labels: 3.57 → 5.27.** The disabled control was fading its own
      material with `opacity`; it now dims its content and keeps the material.
      No assertion loosened — two were made **stricter**, because the contrast
      harness could see neither an ink's alpha nor a label held in a child
      element, and both blind spots could only ever flatter.
- [x] **The reference-pair readout names the primary cell** —
      `apple-macos-26.5-1x-light-standard`, texture tier — checked on every scene
      the picker offers rather than on the opening one.
- [x] **The Firefox motion-timing intermittents are stabilized, not loosened.**
      Two of them, both failing on bridge latency rather than on motion, and
      neither the product's fault. The morph reversal read its mid-flight box over
      a round trip; it now records the whole trajectory in the page, one sample per
      frame, and asserts that *no* frame of the reversal is a cut rather than only
      the frame after it. The press re-press had two causes stacked — a
      window-shaped wait a long frame could step over (now a crossing, which
      cannot be), and a round trip between observing and interrupting a 260 ms
      spring (now one frame in the page, on a handle resolved up front so the
      arming is a single message). Both continuity tests print their samples on
      failure, which is what identified the second cause: the loop's first
      observation was already past the release's undershoot, with the ten frames
      after it climbing cleanly. **Eight consecutive three-engine runs green.**

### The full chain

Run on `c9d-release`, in this order, all green:

| step | result |
| --- | --- |
| `pnpm -r build` | exit 0 |
| `pnpm -r lint` | exit 0 |
| `npx eslint .` (root) | exit 0 |
| `pnpm -r test` | **1089 passed**, 0 failed (motion 162, geometry 143, renderer-webgpu 224, core 249, platform-web 129, react 70, calibration 112) |
| `@vitrea/platform-web` Playwright | **256 passed**, 0 failed (Chromium / Firefox / WebKit + the real-adapter GPU project) |
| `@vitreajs/vitrea-react` Playwright | **90 passed**, 3 skipped, 0 failed (three engines) |
| `demo` Playwright | **17 passed**, 0 failed |
| `@vitrea/renderer-webgpu` Playwright | **29 passed**, 0 failed (goldens, isolation proof, GPU runtime, benchmark) |

The ten pre-existing failures Decision Log #30(d) recorded are closed: eight
stale goldens re-baselined behind the isolation proof, and the demo's contrast
and readout defects fixed at the token. The Firefox intermittent that was not in
that count is closed too.

### The chain since, per release

This section is the chain **of record** rather than a log of every run, so each
later cut names where its own run is written down rather than copying the table.
Every one of them ran the same nine steps in the same order, serially, with each
browser step preceded by a machine-settings reading that refuses under an
accessibility policy Playwright cannot record.

| version | where the run is recorded |
| --- | --- |
| 0.18.0 | `packages/calibration/results/2026-09-15-w28-g4-landing/` (`chain.sh`, `chain-*.txt`, `chain-status.txt`); the counts are in claims §5.148 §6 and the W28 spec's Outcomes clause 5 |
| 0.19.0 | `packages/calibration/results/2026-09-20-w29-g4-landing/`, same shape; the counts are in claims §5.155 §6. Its machine reading gained a third value — `NSGlassTintAmount`, macOS 27's appearance slider, which did not exist when this checklist was written and which drives the native material with no GUI (claims §5.149 §4). It is recorded rather than refused on, because no browser suite renders the native material; what it makes is a record of the machine each run was taken on |
| 0.20.0 | `packages/calibration/results/2026-09-20-w30-g4-landing/` (`chain-status.txt`, `chain-*.txt`, `browser-runs.txt`, `dry-run.txt`); the counts are in claims §5.160 §7. **The React suite is red at this cut and is recorded rather than rerun**: two cases of the tracker's standing driver-timing class, `presence.spec.ts`'s elapsed window on chromium and `morph-materialize.spec.ts`'s release timing on firefox, neither in code the wave touched. 0.17.0, 0.18.0 and 0.19.0 each published with this class disclosed and the acceptance is the user's, as §Status of each wave records. **Amended beside 2026-09-20 (W30 G4 review closure; claims §5.160 §9, finding 5):** two of the nine steps had no committed output at that cut — root `npx eslint .`, which the landing's table omits entirely, and the demo Playwright suite, whose row reads "58 passed (run before the cut)" rather than naming a log. Both are run at the closure's head and committed as `chain-eslint-root.txt` and `chain-demo-e2e.txt`, and `chain.sh` beside them is the script the earlier cuts used, writing `chain-status.v2.txt` so the MACHINE's exit codes sit beside the hand-typed table rather than over it. The version does not move: 0.20.0 is still prepared and unpublished, and no changeset was added |
| 0.21.0 | `packages/calibration/results/2026-09-21-w31-g4-landing/` (`chain.sh`, `chain-status.v2.txt`, `chain-*.txt`, `browser-runs.txt`, `dry-run.sh`, `dry-run.txt`); the counts are in claims §5.165 §7. **Green end to end, and the React suite is green with it** — 174 passed, 3 skipped, 0 failed on three engines, where 0.17.0 through 0.20.0 each published with the tracker's standing driver-timing class disclosed. Nothing was done to that class here; it is a run that did not hit it rather than a fix, and the entry stands. The chain ran all twelve steps `chain.sh` names, which is the checklist's nine plus the two evidence reads every gate of W31 has run — `freeze.py verify` at open and close (**1,818 intact**) and the macOS 27 gated-cell count (**230 cells / 726 rows**, contract X10's pin) — and the `test:golden` and `test:gpu` steps this table had folded into one renderer row (**34** byte-identical with no regen, **48** on a hardware adapter). **The four shipped macOS 27 document digests this release carries** are `3dc24a74f17fd87e` (light), `8a43f54162606db4` (dark), `ab3ed65aa02869b1` (light receded) and `e1f42c5656ef392f` (dark receded) — added here because claims §5.164 §13 finding F6 found they appeared in no ledger section, charter row or changeset, and this row is the release record that should carry them. **And two of them are a different KIND of number from before**: 0.21.0 changes the fingerprint's own definition, so a leaf at its declared inert identity is dropped before hashing and the two frozen macOS 26.5 documents report `b2b570e4adcea8fb` and `874be66ea501621b` — the numbers they were sealed at — while drawing exactly what they drew. An app comparing a digest against a literal recorded under 0.19.0 or 0.20.0 has to re-record it. Prepared and unpublished; `pnpm release` is the user's hand and the tag `v0.21.0` follows it. **Published 2026-09-21 on `c87b5493`, tag `v0.21.0` pushed; cold install verified (core 44 / web 258 / react 37 exports, ranges `^0.21.0`, the 26.5 light digest reading its own `b2b570e4adcea8fb`); the registry listed web 127 s after core and served its tarball five minutes after that (W31 charter §Outcomes).** **Amended beside 2026-09-21 (W31 G4 review closure; claims §5.165 §9, finding N10): the rehearsal does not rehearse the publish command.** `dry-run.sh` runs `pnpm publish --dry-run` per package and inspects the packed tarballs — which is the `workspace:` rewrite, the failure this project actually hit — but `pnpm release` is `pnpm -r build && changeset publish`, and **`changeset publish` has not been invoked since 0.1.0**. It is the step that decides which packages go, in which order, and that the `fixed` group moves together, and `@changesets/cli` offers no dry mode for it at the version in use. The tool has not moved under the gap: **3.0.1**, pinned in `pnpm-workspace.yaml`'s catalog and installed, is what 0.1.0 published through. Recorded rather than closed — closing it means publishing |
| 0.22.0 | `packages/calibration/results/2026-09-21-w32-g2-landing/` (`chain.sh`, `chain-status.v2.txt`, `chain-*.txt`, `chain-run-1/`, `browser-runs.txt`, `dry-run.sh`, `dry-run.txt`); the counts are in claims §5.169 §7. **Prepared, unpublished.** **The chain ran twice and both runs are committed**: the first was RED on `pnpm -r lint` — `apps/demo/src/laws/law.ts` named `ResolvedMaterialPolicy`, which is core's type and which no published package re-exports, so the `/laws/` shadow stage could not import a type it needs — and is kept whole under `chain-run-1/` with a README, because a step that fails is a record and not a reason to re-run until it is green. The second, at the head after the fix, is **thirteen steps of thirteen at exit 0** and agrees with the first on every count, `vite` stripping types so nothing the type-check refused reaches a pixel: freeze **1,818** at open and close; the capture-tree checker's **first run as a step of the chain** (W32 G0b's own record said a landing is where it joins) at **1,900 captures, 1,893 match, 0 mismatch, 0 misfiled, 7 no-row**; build, lint and root eslint exit 0; unit **2,698 over 186 files** (policy 23, motion 164, geometry 170, renderer-webgpu 561, core 302, platform-web 631, react 169, calibration **632**, demo 46 — calibration's +14 is C1's fourteen cases); goldens **34** byte-identical; `test:gpu` **48**; platform-web Playwright **410**; React **174 passed / 3 skipped / 0 failed** on three engines, **green as at 0.21.0**, a run that did not hit the standing driver-timing class rather than a fix; demo **61** against 0.21.0's 59, the two new ones being the `/laws/` shadow stage's pin; the macOS 27 bed **230 gated cells / 786 rows** and the frozen bed **229 / 1,107**, `PREDICATE_EXCLUDES` unmoved at 67. X6 read before every browser run, **fourteen readings**, all RT 0 / IC 0 / `NSGlassTintAmount` 0.5. `dry-run.txt` is clean with `workspace:^` rewritten to **`^0.22.0`** in both dependents, `LICENSE` / `NOTICE` / `README.md` in each, core **583,443 B**, web **567,784 B**, react **187,860 B**. **The four macOS 27 document digests this release carries** are W32 G1's seal — `40a6dec2dc34c748` (light), `bd1814fac34f9b30` (dark), `f34dcc03e2774db3` (light receded), `6b6237b7ae241638` (dark receded) — over files whose own twelve-hex content hashes are `d5bdd6eac432`, `431cabd391c4`, `45acb6d916b9` and `4e68f81869f6`; the two frozen macOS 26.5 documents report their own recorded fields `b2b570e4adcea8fb` and `874be66ea501621b`, unchanged. An app comparing a digest against a literal recorded under 0.21.0 has to re-record the four macOS 27 ones; the 26.5 pair has not moved since rule 2. **The 0.21.0 row's rehearsal amendment applies unchanged and is not re-stated**: `changeset publish` is still never invoked, its last live exercise is **0.1.0**, and `@changesets/cli` is still pinned and installed at **3.0.1**. `pnpm release` is the user's hand and the tag `v0.22.0` follows it. **Amended beside 2026-09-22 (W32 G2 review closure; claims §5.169 §10, Decision Log 5 as RULED by the user): the React package carries a SOURCE change after this cut, and the rehearsal was re-run for it.** `useGlassRootHandle` is exported from `@vitreajs/vitrea-react` — the hook the README has told applications to import since 0.20.0 and which was internal in the 0.20.0 and 0.21.0 READMEs as published, so that import threw — with a five-case unit test, the README restored to the direct route with G2's correction kept beside it, and a **hand-written CHANGELOG entry under 0.22.0 (Minor Changes)**: the version was already cut by `changeset version` and a new changeset file would re-bump the fixed group. The rehearsal re-run is clean and agrees with the first on everything but react's tarball: core **583,443 B** and web **567,784 B** byte-identical, react **188,179 B** against 187,860, and the package's **export count 37 → 38** read off the built `dist/index.js` — 37 being what 0.21.0's cold install verified in the row above. `dry-run.txt` holds the second run; the first is quoted in this row and in claims §5.169 §8 and neither is rewritten. The unit total moves with it, **2,698 → 2,703 over 187 files** **Published 2026-09-22 on `c46eeba3`, tag `v0.22.0` pushed; cold install verified (core 44 / web 258 / react 38 exports, ranges `^0.22.0`, the four macOS 27 digests and the 26.5 pair reading their own fields, `spreadPx` 0.5 / 1.8 in the web bundle); the registry listed the whole group in 23.6 s (core 04:42:00Z, web 04:42:22Z, react 04:42:24Z) and served the web tarball on the first install, so 0.21.0's two-layer window did not recur (W32 charter Status).** |

| 0.23.0 | **Prepared, unpublished; complete chain recorded at §5.173.** Evidence `packages/calibration/results/2026-09-22-w33-g2-landing/`: `chain.sh`, `chain-resume.sh`, `chain-status.txt`, per-step logs, `browser-runs.txt`, `dry-run.sh`/`.txt`. Six non-browser steps completed before a temporary eye stop; raw two-axis pixels falsified the apparent stripe defect and only the unrun browser tail resumed. Freeze **1,818** open/close; tree **1,900 /1,893 match /0 mismatch /7 no-row**; build/lint/root eslint green; units **2,719 /189 files** (calibration648, including four X1 cases and its live pixel derivation); goldens **34**, byte-identical; GPU **48**; platform **410**; React **174 pass /3 skip**, first and only run, no timing-red rerun. The normal demo command ran **zero tests**, setup exit1: an orphaned Vite from the removed W32 G2 worktree occupied5177. The parent stopped it after the single isolated-port continuation had started, so the suite uses `demo-isolated.config.ts` on5197 with normal tests/projects and no server reuse; it passed **61/61 in9.9min**, including all10 `/laws/` cases; final freeze **1,818** after it. Gated **230/786**, frozen **229/1,107**, predicate67. X1 adopts zero >0 fraction and >1 count on **218** standard single-shape non-holdout cells; G0's232 remains the broader referee. M2 **26/26**, unchanged2% bound. X6's **10 readings** preserve one refused own-shell false positive before launch and nine eligible attempts, all RT0/IC0/slider0.5/foreign0, idle≥60.065s. Version generated by `pnpm changeset version`, every changeset consumed. Rehearsal clean: packed0.23.0, ranges **^0.23.0**, required files and dist verified; core **583,802 B**, web **568,292 B**, React **188,179 B**. Four resolved digest prefixes **dcbccbd9feac9881 /e59f9106bcd7c966 /f34dcc03e2774db3 /6b6237b7ae241638**, file SHA prefixes **6e509c7f76cc /eab099cc6698 /45acb6d916b9 /4e68f81869f6** in light-active/dark-active/light-receded/dark-receded order; both frozen26.5 digests remain **b2b570e4adcea8fb /874be66ea501621b**. No material or document reseal at G2. The rehearsal does NOT invoke `changeset publish`; its last live exercise stays0.1.0 with CLI3.0.1. Review, merge and the user's `pnpm release`, then tag, remain later actions. |

### Artifacts

- [x] `pnpm changeset version` → both packages at **0.1.0**, the `fixed` pair
      holding them together.
- [x] `pnpm publish --dry-run` clean on both packages at 0.1.0.
- [x] **The workspace protocol is rewritten in the tarball, verified rather than
      assumed:** `@vitreajs/vitrea-react`'s dependency reads `workspace:^` in the
      repo and
      `^0.1.0` in the packed artifact. This is Decision Log #30(a)'s reason for
      forbidding bare `npm publish`, re-confirmed at 0.1.0. Also in each tarball:
      `LICENSE` and `NOTICE` (Apache-2.0 §4), a README, one self-contained
      `index.d.ts`, and no `@vitrea/*` runtime dependency. `@vitreajs/vitrea`
      250 kB / `@vitreajs/vitrea-react` 251 kB packed.
- [x] **Demo static build verified under a path prefix.** Served from
      `/designer/`: the entry document, its hashed asset, the `/playground/`
      route, that route's own `../assets/` reference, and a native fixture all
      resolve. 2.0 MB including `dist/fixtures/` (the native captures, whose
      public distribution the user approved — Decision Log #30(e)).
- [x] **GitHub Pages workflow written** (`.github/workflows/pages.yml`): builds
      `apps/demo/dist` and deploys on push to `main`.

---

## 2. Remaining human items

### [~] 2.1 The labeled per-engine manual-page pass — WebKit done 2026-08-28, Gecko still open

**WebKit half closed by the user's labeled retail-Safari run of 2026-08-28 —
on Safari 18.6 / macOS 15.7.7** (their screenshots are committed beside the
record; the run the checklist asked for named Safari 26, and the row is keyed
at the measured 18.6, claiming forward per the table's convention — a retail
Safari 26 spot-check stays cheap and optional)
(verbatim record: `spikes/s1-proxy-topology/manual-evidence/2026-08-28-d1-webkit-labeled.md`).
Three of the four fields moved on it — `rasterisesBackdropFilter: "yes"`,
`backdropRootTriggers: "normative"` (D1's labeled set is exactly the Filter
Effects 2 normative membership), `transform3dHazard` confirmed staying
`"perspective-preserve3d"` — as a new `webkit / minVersion: 18.6` row;
`edgeMode` stays `"unverified"` because section C measures mask extent, not
the sampling edge mode. **The Firefox run has not happened**; the gecko row is
unchanged and fails closed.

**Why an agent cannot do this.** Gecko and WebKit render `backdrop-filter` as a
complete no-op in every automatable capture path — Playwright headless and headed,
retail `--screenshot`, WebDriver BiDi, WKWebView `takeSnapshot` — while rendering
it correctly live (S1's environmental blocker, Decision Log #17). A screenshot
comparison on those engines measures a blank. The self-scoring page is the only
oracle, and it needs a human looking at a real retail browser.

**What to run.** Open `spikes/s1-proxy-topology/pages/manual-check.html` in
**retail Safari 26** and in **retail Firefox**, and work through sections A to G.
The page scores itself; each section says what a pass looks like.

**What this run adds over the one already done.** The user closed S1's headline
verdicts this way on 2026-08-25 (evidence archived in
`spikes/s1-proxy-topology/manual-evidence/`), and those verdicts stand. What is
still open is the **labeled per-engine** reading of section **D1** — the
backdrop-root breaker tiles. The earlier pass observed a per-engine asymmetry
there (`will-change: opacity` breaks the proxy, `will-change: transform` does not)
without recording which engine did which, and that distinction is the one the
conformance table needs.

**Where the answers go.** `packages/platform-web/src/probe/conformance-table.ts`,
the `gecko` and `webkit` rows. Four fields are currently `"unverified"` on both
and this run is what can move them:

| field | what section answers it |
| --- | --- |
| `rasterisesBackdropFilter` | A1 — does the portaled masked proxy render at all |
| `edgeMode` | C1 — does the padding show as a halo (mirror vs something else) |
| `transform3dHazard` | D1 — the ancestor `perspective` / `preserve-3d` tiles |
| `backdropRootTriggers` | D1 — which ancestor styles actually re-root, per engine |

The module documents the update rule and a test enforces it: **every row must cite
its evidence**, so a field may only move with a citation to this run. Leaving a
field `"unverified"` is a legitimate outcome — the runtime fails closed on it, so
a stale table under-promises rather than over-promises. `"unverified"` is not
`"no"`.

### [x] 2.2 Adopt (or amend) the proposed fidelity thresholds

**Adopted 2026-08-26 as proposed, without amendment; enforced by
`packages/calibration/test/adopted-thresholds.test.ts`** over the 48 light-profile
cells of the committed matrix (the cross-tier ΔE row excepted — it needs the
uncommitted captures, and the test carries a tripwire saying so).

Parent acceptance #7 says the calibration metrics must be "inside declared
thresholds", and the thresholds in `c9a-fidelity-claims.md` §5 are **proposals,
not adopted**. C9a set them, K5 added the dom tier's perceptual and coherence
rows, and C9d added the dom tier's shape rows now that the axis measures geometry
rather than a `box-shadow`. Every one is bounded by the *holdout* numbers rather
than the calibration ones, deliberately: a gate that calibration passes and
holdout fails would certify overfitting rather than prevent it.

Adopting them is a human judgement about what "close enough to Apple" means for
this library's public claim. It is the last thing standing between acceptance #7
and closed, and no amount of further measurement decides it.

### [x] 2.3 Turn on GitHub Pages, once — done; `pages.yml` deploys green and the
live demo was verified at DPR 1 and 2 after the #40 fix

Repository settings → **Pages** → Build and deployment → Source: **GitHub
Actions**. Until this is set, `pages.yml` fails at the deploy step with "Pages
site not found" rather than deploying somewhere unexpected. One click, once.

### [x] 2.4 Publish — done 2026-08-26

**Published by the user (the second-factor holder) on 2026-08-26**; registry
`time.modified` 2026-08-26T14:54:25.932Z, both packages at 0.1.0. Verified at
recomposition by a cold scratch install outside the workspace:
`npm install @vitreajs/vitrea @vitreajs/vitrea-react react react-dom` resolves,
both entry points import under native ESM in node (41 and 33 exports), and
`@vitreajs/vitrea-react`'s registry metadata carries `react`/`react-dom` as
`>=19.0.0` peers — the review round's inlining defect (Decision Log #41(b))
confirmed absent from the shipped bytes.

The working tree had to be clean first: `pnpm publish` refuses on an unclean
tree (`ERR_PNPM_GIT_UNCLEAN`); the untracked `tmp/` directory that would have
tripped it is `.gitignore`d. It holds two design-review notes that are not this
branch's and were deliberately left alone.

Then, from the repository root, after the branch is merged to `main`:

```
pnpm release
```

That is `pnpm -r build && changeset publish`, and it is the **only** sanctioned
path (Decision Log #30(a)). Verified rather than assumed on two counts:

- `changeset publish` resolves its publish tool from the workspace and returns
  pnpm's for a `pnpm-workspace.yaml` repo, so it shells out to `pnpm publish` and
  not to `npm publish`. Checked in the installed `@changesets/cli@3.0.1`
  (`getPublishTool` → `pnpm_exports`).
- That distinction is the whole reason for the rule: npm would ship
  `@vitreajs/vitrea-react`'s dependency as the literal, unresolvable
  `"@vitreajs/vitrea":
  "workspace:^"`, while pnpm rewrites it to `^0.1.0`. Confirmed on the packed
  tarball at 0.1.0 (§1).

**npm will demand a one-time password.** `changeset publish` prompts for it; a
non-interactive run needs `pnpm changeset publish --otp=<code>` instead. Either
way a human holds the second factor, which is why this box is unchecked and why
no agent should tick it.

Publishing is irreversible for a version number: `@vitreajs/vitrea@0.1.0` and
`@vitreajs/vitrea-react@0.1.0` can never be re-published with different bytes.

---

## 3. Open and *not* release-blocking

Recorded so their absence is legible rather than forgotten. Each is an external
gate on a *claim's scope*, not on the release.

- **The 2× (Retina) capture run.** Every committed fixture is keyed `-1x-`. The
  spec's canonical `-2x-` profiles are unreachable on this machine — a Mac14,12
  driving a 1920×1080 panel reports `backingScaleFactor` 1.0, and asking
  ScreenCaptureKit for twice the window size upsamples rather than rendering at
  2×. Needs a Retina display; the user's MacBook is the candidate.
- **The two accessibility-profile capture runs.** macOS exposes reduce-transparency
  and increase-contrast as read-only environment values, so each profile needs its
  own capture run with the matching System Settings toggle on (Accessibility →
  Display). The harness refuses to emit a fixture whose key claims a mode the
  machine is not in, which is why these are absent rather than mislabelled.
- **Motion metrics.** No frame sequences were captured on the native side, and the
  still `pressed` fixtures cannot substitute — they are byte-identical to their
  rest counterparts, because `Glass.interactive(true)` opts the material into
  responding to press input rather than posing it pressed, and Apple exposes no
  declarative pressed pose. No press or motion claim is made anywhere.

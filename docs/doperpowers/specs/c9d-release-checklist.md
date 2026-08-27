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

### [ ] 2.1 The labeled per-engine manual-page pass — EXTERNAL

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

The 0.25.0 release chain — prepared, unpublished

What was released: branch rel-0.25.0 = origin/main 0868784c + the --no-ff merge of PR #2
(demand-driven frames, spec 2026-09-28-demand-driven-frames.md) as b13bc625 + the parent's
`pnpm changeset version` as 175d0130 (fixed group at 0.25.0; version.txt). Every step ran at
175d0130. No material, profile, matrix, generation or golden path differs from origin/main
(audit.py asserts it). `pnpm release`, the tag and publication are the user's.

The chain (chain.sh): W36 G2's 0.24.0 chain in the same order, with four adaptations the
script's header names — a digest step after the build, a golden byte check after test:golden,
the gated count read through W40's matrix_store (results/matrix.json holds only the frozen
26.5 rows since W40 G0), and an X6 preflight that WAITS for idle instead of refusing
(run-browser.py). It also checks every browser suite's server port at launch, because the
ordinary configs reuse an existing server and the main checkout is shared; and it halts at the
first non-zero step, so a failure is diagnosed before anything else runs. chain-status.txt is
the machine's exit codes; chain-invocations.txt shows each invocation and what it skipped.

Readings (audit.py re-derives each from its log into audit.json):
- freeze.py verify 1,818 at open and close.
- capture tree 1,900 captures / 1,893 match / 0 mismatch / 0 misfiled / 7 no-row.
- digests: live rule-2 fingerprint = recorded field = runtime endpoint = expected, for
  be13dae45098fc89 / 2a4323f33df8d799 / b0d0d8dacc6a03af / 7c454858a3cbad5b (macOS 27 light,
  dark, light receded, dark receded; files 85ad7f7e3e0d / 0eac5b294cc2 / 30fbe05986ae /
  5cec8c961201) and b2b570e4adcea8fb / 874be66ea501621b (frozen 26.5 light / dark).
- build, lint, root eslint exit 0. Units 3,029 over 214 files (policy 23, motion 164,
  geometry 170, renderer 651, core 304, platform 651, React 180, calibration 776, demo 110).
- goldens 34 passed; the 13 golden PNGs byte-identical to v0.24.0 and HEAD. GPU 49.
- platform-web: FIRST RUN RED, kept (chain-platform-web.txt): 165 passed, 246 failed, every
  failure `browserType.launch: Executable doesn't exist` for firefox-1538 / webkit-2336, which
  the shared Playwright cache no longer held (0.24.0 ran all three engines here on 09-24; the
  pin is still @playwright/test 1.62.1). No test body ran on either engine and every Chromium
  and chromium-gpu case passed, so it is environmental and not the frame-loop change
  (platform-web-run1-diagnosis.txt). The two builds were installed and nothing else
  (browsers-install.txt); chain-resume.sh ran the suite once more under its own X6 preflight:
  411 passed (chain-platform-web-run2.txt). No other step was re-run.
- React 174 passed / 3 skipped / 0 failed on three engines, first and only run. The skips
  are 0.24.0's three. The standing Firefox morph-release timing case did not recur. That is a
  run that did not hit it, not a fix.
- demo 83 passed (0.24.0's 61 plus the 22 gallery cases added since), first and only run, on
  isolated port 5197 (isolated-demo.config.ts), because the main checkout's own Vite (cwd
  apps/demo there) held 5177 at launch (ports.txt). Every other suite found its port free
  and ran its ordinary config.
- gated: macOS 27 230 cells / 786 rows, frozen 26.5 229 / 1,107.
- X6: six preflights (browser-runs.txt), all RT 0 / IC 0 / NSGlassTintAmount 0.5 / Button
  Shapes 0, zero foreign capture processes, idle >= 3,322.9 s. No wait was needed: each was
  admitted on its first poll (0.08 s). x6-waits.txt was never created.

Rehearsal (dry-run.sh, dry-run.txt, pack-check.py/json): `pnpm publish --dry-run` exit 0 per
package, LICENSE / NOTICE / README.md and dist in each tarball, no `workspace:` left,
dependents at ^0.25.0. Sizes: core 598,568 B, web 586,295 B, React 192,247 B. The exports are
counted off the packed bytes in a scratch consumer: core 44, web 261, React 38.
exports-diff.txt compares these with the published 0.24.0 tarballs, fetched back at 586,228 /
569,814 / 188,606 B. The web package gains three names: backdropReadingDue,
backdropTextureIsLive and silhouetteSourceWindow. They are module helpers from the frame-loop
change that reach the public entry through existing `export *` lines, and no CHANGELOG entry
names them. Tarballs stay in the worktree's ignored .vitrea-tmp/. `changeset publish` was not
invoked.

CI (ci.txt): main was green at 0868784c and at da08f377 (a W42 charter document commit that
landed after the cut and touches no code), and PR #2's head was green. The checklist's
"CI green on main at the release commit" row belongs to the merge of this branch.

Replay: the runners write exclusive outputs and refuse a label that already has a log. chain.sh
skips recorded steps rather than re-running them, and a refused X6 preflight writes no log.
Playwright's test-results/ stay in each package, which is gitignored.

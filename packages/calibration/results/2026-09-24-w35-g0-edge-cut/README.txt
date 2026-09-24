W35 G0a operational evidence index — c9a §5.177

This file is plain text because the worker's instructions forbid Markdown reports.
The declaration is domain.json; its digest will be pinned by the calibration test.
All native W34 reads use the unchanged wave.Reader calibration/validation roles.
The new sibling w35_readers.py is the only web pixel entry point. Canonical native
reads use its separate role guard (parent-directed): calibration/validation/probe
are admitted; holdout and recorded and bare paths refuse before payload opening.
Probe is a diagnostic role, not a new gated set (W25 DL3(e)).

Replay without capture:
  python3.12 test-readers.py
  python3.12 test-instrument.py
  python3.12 edge.py           Produces profiles and deep bars; refuses overwrite.
  pnpm --filter @vitrea/calibration exec tsx results/2026-09-24-w35-g0-edge-cut/canonical.ts
  pnpm --filter @vitrea/calibration exec tsx results/2026-09-24-w35-g0-edge-cut/identity-proof.ts

Run in a fresh evidence copy for replay; never remove a recorded result to rerun it.
Canonical web tree is the MAIN checkout, read-only, after its recorded generation
check. W34 web captures are G2/web-captures, checked against non-holdout provenance.
No W34 holdout payload or spent receipt path is read or edited. No native capture.
The first browser preflight refused nine foreign processes before launch. The
parent directed coexistence with that unrelated College session; the following
opening isolation passed once. Foreign PIDs remain recorded, not terminated.

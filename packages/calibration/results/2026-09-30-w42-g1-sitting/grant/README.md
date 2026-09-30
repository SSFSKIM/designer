# W42 G1 phase 2 — the grant switch and the positive pose checks (c9a §5.195)

**The switch (Decision Log 6; the user's hand, X5 lifted for this sitting only).** The parent
read the system TCC rows back after it: `dev.vitrea.reference-apple.w39` ScreenCapture auth **2**,
last modified 2026-09-30 10:44:55Z (the user switched it on), and **no ScreenCapture row** for the
original `dev.vitrea.reference-apple`: the parent removed it with `tccutil reset`, and it is
restored after the sitting. The original's Accessibility row (auth 2, 2026-08-28) is untouched.
System Settings and the cua helper were quit; Chrome and ChatGPT stayed closed.

**The side's positive pose check** (`grant-check.py side-pose-check-1`: the canonical 27-only 2x
light checkerboard capsule at mode 68, the sitting's gates, raw under
`~/vitrea-w42/g1/grant-checks/`). One of the three W34 Decision Log 4 allows was needed:

| Attempt | Outcome | presentedActive | materialRendered / deterministic / repeatNoise | Frame |
| --- | --- | --- | --- | --- |
| `side-pose-check-1` | **captured-active** | true | true / true / 0 | `204f21f0…`, the cell's second recorded state (115 px, ≤ 2 codes from the fixture) |

The side bundle's pin held (binary `02052b17…`, cdhash `be258cbf…`), the opening and closing
machine reads agree, and no window appeared but the Window Server one at level 2147483630. Unlike
W34's and W39's side bundles, the first launch after the grant attested active. The frame is a
known state (`../prechecks/two-states.json`), and the cursor-window hypothesis holds a fifth time:
the launch began without that window and it appeared during the launch.

**The original is not launched.** It has no ScreenCapture row, and a launch would raise an
unattended prompt that writes an auth-0 row and blocks every later launch
(`../prechecks/rehearsal/attempt-1/prompt.txt`). Its check is the read-only TCC read
(`side-pose-check-1/tcc-before.json`, `tcc-after.json`): no ScreenCapture row for
`dev.vitrea.reference-apple`, so not granted, and the side holds the only vitrea Screen Recording
grant. This is W39 G1's ruling, applied the same way.

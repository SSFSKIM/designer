# W42 G1 phase 1 — the pre-grant checks (c9a §5.195)

Charter: `docs/doperpowers/specs/2026-09-29-w42-body-spatial-structure.md`, G1 and Decision Log 6.
Runbook: `../../2026-09-29-w42-g0-declaration/bed/sitting/README.md`. Worktree `w42-g1-sitting`
at `19db06ec`; `sitting.py pin-check` passed against the hashed declaration `f04ae95b…`
(scenes `4aa06af9…`, bed `53870f47…`); `freeze.py verify` reads 1,818. Raw captures stay under
`~/vitrea-w42/g1/prechecks/` and are never committed.

## Check 1 — the ORIGINAL granted bundle's positive capture: STOPPED (not byte-identical)

`original-positive.py original-positive-1` (W39 G1's `wave-close/grant-check-close.py` with the
W42 driver's gates). The original bundle `dev.vitrea.reference-apple` (binary `bd3092e8…`,
cdhash `88cbbb5b…`, the same binary W39 closed on, not rebuilt) captured the canonical 27-only
2x light checkerboard capsule at mode 68. It waited 1 h 27 min without launching, until
Google Chrome and ChatGPT had been quit by the user, then for 75 s of HID idle
(`original-positive-1/wait.txt`; the script writes `<attempt>-wait.log`, renamed here because
`*.log` is gitignored, as is `backgrounds.txt`). It launched with zero foreign processes and
ChatGPT gone (`command.json`), and the opening and closing machine reads agree.

| Condition | Read |
| --- | --- |
| outcome | `captured-active` |
| `materialRendered`, `presentedActive`, `deterministic` | true, true, true |
| `repeatNoise` | 0 |
| byte-identical to the committed fixture (`6c15311b…`) | **no**: frame `204f21f0…`, 115 px differ, 114 by 1 code and 1 by 2, all inside the capsule body (x 200–440, y 155–254), slightly brighter |

The brief requires byte identity, so the check stops here and **check 2 (the TCC-refusal
rehearsal of the side bundle) was not run**.

**The frame is a known second state, not a drift** (`two-states.py` → `two-states.json`). It is
byte-identical to W39 G1's step-0 capture of the same bundle (`204f21f0…`, 2026-09-25), which
W39's README recorded as "115 pixels by ≤ 2 codes" and did not gate on. The committed fixture's
state `6c15311b…` is what W39's side pose check 2 and W39's close check produced. Every one of
the four stored checks attests active, material rendered, deterministic and repeat noise 0, so
the cell takes one of two states per launch, each stable within its launch. A correlate in all
four, two per state: the `204f21f0` launches began with no Window Server window at level
2147483630 (kCGCursorWindowLevel) on screen, and one appeared during the launch. The
`6c15311b` launches had it on screen before they started. This correlation is observed, not
established as a cause.

## Machine state at the stop

Display mode 68 on `7709FD0F-…`, never changed. Reduce Transparency 0, Increase Contrast 0,
`NSGlassTintAmount` 0.5, Show Borders 0. The system TCC rows, read read-only before, after and
at the stop, are unchanged. `dev.vitrea.reference-apple` has Screen Recording auth 2
(2026-09-27 05:08:28Z) and Accessibility auth 2. `dev.vitrea.reference-apple.w39` has **no
row**, and the only other row is `dev.vitrea.tccprobe` at 0. No harness process remains, and no
permission prompt was ever on screen.

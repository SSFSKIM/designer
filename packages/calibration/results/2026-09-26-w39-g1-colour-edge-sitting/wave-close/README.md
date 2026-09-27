# W39 wave close — the original bundle's grant restored (Decision Log 4)

Executed 2026-09-27 after G2's merge (`2899071e`) and Decision Log 2's ruling (the negative).

**The user's hand.** A first attempt to add the original and switch the sitting bundle off did
not land as intended: the system TCC database then read the original `dev.vitrea.reference-apple`
at auth 0, `.w39` still at auth 2 and `.w34` touched, because all three entries carry the same
display name. The user then removed every VitreaReference entry and re-added the original alone,
enabled. Read-only system TCC read afterwards (`attempt-2/tcc-before.json`, `tcc-after.json`):
**`dev.vitrea.reference-apple` auth 2 and no other `dev.vitrea.reference*` row.** The sitting
bundle `dev.vitrea.reference-apple.w39` therefore has NO row: it is retired and must never be
launched again without re-adding it, because a launch with no row raises an unattended prompt.

**The positive check** (`grant-check-close.py`, G1's `grant/grant-check.py` with only `REPO`
pointed at the main checkout since the G1 worktree is removed; the diff is that one line):
- `attempt-1-refused/`: the machine gate refused before launch, 7 foreign capture processes
  (Google Chrome, launched by the user). Nothing launched.
- `attempt-2/`: after Chrome was quit and 75 s of idle, the ORIGINAL bundle captured the
  27-only 2x light checkerboard capsule: outcome **`captured-active`**, `materialRendered`,
  `presentedActive`, `deterministic` all true, `repeatNoise` 0, no new window, opening and
  closing machine reads agree. The PNG is **byte-identical to the committed canonical fixture**
  (`canonical-comparison.json`, SHA-256 `6c15311b…`), as the side bundle's pose check was in G1.
  The PNG itself stays under `~/vitrea-w39/run/grant-checks/wave-close-2/` (X12).

The side bundle's state is the TCC read (no row), not a launch, by the same ruling G1 applied to
the original while it had no row. Nothing under `apps/reference-apple/build` was rebuilt.

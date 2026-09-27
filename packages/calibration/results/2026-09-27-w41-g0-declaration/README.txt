W41 G0 — declaration and instrument, in progress (§5.191)

Findings for the parent

1. STOP before declaration, resolved by charter v2.1 (9762ef9c).
Charter v2 clause 7 named the active top straight as a shadow-only control
without conditioning on scheme. Memo B and its shadow-reading.json show that
light-active top shell 0 carries -20 codes at grey128 and grey255, both scales,
while the held shadow is below 0.0003 code. Dark-active top is the observed zero.
The parent corrected the charter; the worker did not amend it. The declaration
will retain light-active top as a stroke bin and use the corrected control set.
The full copied numerical witness is stop-witness.json. These are existing
exploratory readings, not a new fit or a WGSL proof. The tiny modelled dark-active
shadow reaches 0.024649 code at 2x grey255; the charter's “below 0.02” shorthand
is the 1x reading, not a bound at both scales. This does not change the control.

Reading provenance

readings/ preserves the two grounding memos and all their available scratch
scripts and outputs. reading-provenance.json records their original byte hashes.
The large stroke reading is losslessly gzipped, mtime 0; its recorded SHA names
the decompressed original bytes. No copied script has been executed here.
The copies contain historical absolute paths and are not yet a G0 replay tool.

Workspace preparation

Branch w41-g0-declaration at /Users/new/vitrea-w41/g0, cut from main 55511a72,
then fast-forwarded to the parent's charter correction 9762ef9c.
The EnterWorktree session-switch tool refused this subagent; all work uses
absolute worktree paths and explicit command working directories instead.
pnpm install --silent and pnpm -r build passed. workspace-build.txt records build.
freeze-verify.txt: 26.5 freeze intact, 1818 entries.
No native payload, validation or holdout read; no fit, exposure, browser,
web/native capture, matrix CLI, or shipped file change in this preparation.

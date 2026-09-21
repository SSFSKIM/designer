# The holdout configuration ledger

**Every canonical holdout read of the macOS 27 bed records here, and nowhere else.**

W31 Decision Log 1 (b), ruled: a frozen configuration is *(the shipped document bytes, the
renderer's material-affecting sources)*; the holdout is read once per configuration; no fitted
constant may change between two holdout reads of the same document bytes. A renderer fix after a
read may be re-read once and disclosed as such; a fit may not.

The rule is enforced by an artifact rather than by a reviewer's memory, because the thing it guards
against — a second read of the holdout at the same material, which turns the anti-overfitting split
into a second validation set — leaves no trace in any number. `configuration.py record` reads
`configuration-log.json`, not the world, which is what lets the refusal survive a worktree, a
rebase or a different machine.

```bash
python3 packages/calibration/results/holdout-configuration/configuration.py show
python3 packages/calibration/results/holdout-configuration/configuration.py record \
    --claims "c9a §5.NNN"
python3 …/configuration.py record --claims "…" --source-moved-because "<a non-fit reason>"
```

`show` prints the configuration and changes nothing. `record` appends, and refuses a second entry
at document hashes already in the log unless the source hash has moved **and**
`--source-moved-because` names a reason — both halves, because a reason without a moved source is a
fit being called a fix, and a moved source without a reason is a change nobody wrote down.

## Why this directory exists

W31 G3 wrote the script into its own evidence directory, and W31 G3c ran that copy in place. That
worked, and it was not a rule. Every script under `results/` is copied per gate by convention, and
**a copy starts with an empty log** — so the next gate had the same choice with nothing telling it
which to make, and the two options are not equivalent: one keeps the rule and one silently retires
it (W31 Deferred item 14; tracker, "The holdout configuration log is a cross-gate ledger living
inside one gate's evidence directory"; claims §5.167).

So the ledger is a directory named for what it holds rather than for the gate that first needed it,
and **it is not copied**. A gate reaches back to this path. W32 G0b moved it.

## What did not move

`results/2026-09-21-w31-g3-chroma-fit/configuration.py` and its `configuration-log.json` are
**byte-identical to what W31 G3 committed** and stay where they are: they are that gate's witness,
and a committed witness is never edited. The log here was seeded from that file byte for byte, so
the two reads it records — W31 G3's at `bca47c4c` and W31 G3c's at `33ed2672` — carry across the
move unchanged. `test/w32-holdout-configuration.test.ts` asserts that, field by field, so the claim
that history is unbroken is machine-checked rather than asserted here.

The two seeded entries predate `sourceListSha256`. The first `record` taken at this location also
brings the log's own `$comment` header current; the entries above it do not move.

## What the configuration is, and what it does not see

The four macOS 27 profile documents' **file** hashes, and one SHA-256 over an enumerated list of
material-affecting sources, path-qualified and order-stable. The list is W31's charter verbatim
(acceptance clause 6): `packages/renderer-webgpu/src/wgsl/` (every file), `src/material.ts`,
`src/renderer.ts`, `src/passes.ts`, and `packages/platform-web/src/{optics,css-tier}.ts`.

It is a list rather than a tree so the hash does not move on a comment in a test. W32 G0b measured
the cost of that choice instead of asserting it: the local import graph out of those five
TypeScript entry points reaches **50 further files**, of which around twenty can move a capture's
pixels at unmoved document bytes (`results/2026-09-21-w32-g0b-evidence-tools/source-list-closure.txt`).
The list was **not** widened, for a reason recorded in the script's docstring and in the tracker: a
`sourceSha256` taken over a different enumeration is not a different hash but an incomparable one,
so widening would make the refusal's second half fire at every later read forever. `sourceListSha256`
is recorded beside it from W32 G0b so a later widening is visible in the record.

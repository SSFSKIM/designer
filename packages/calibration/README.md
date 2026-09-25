# Calibration: measuring and publishing a generation

The harness measures Apple's native fixtures against the web tiers. For canonical evidence,
declare the complete generation first, measure into scratch, read holdout once after the
configuration is frozen, then publish once. The union of frozen and current indexed files is
the matrix; no measurement command writes the frozen file or an existing generation.

## Commands

```bash
# Run from packages/calibration; declare the complete LIGHT generation before any read.
# Use the newly sealed documents, never change them inside an existing stage.
STAGE=/tmp/vitrea-light-seal
PROFILES=apple-macos-27.0-1x-light-standard-glass0.5,apple-macos-27.0-2x-light-standard-glass0.5,apple-macos-27.0-1x-light-reduced-transparency-glass0.5,apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5
ACTIVE=profiles/apple-macos-27.0-1x-light-standard-glass0.5.json
RECEDED=profiles/apple-macos-27.0-1x-light-standard-glass0.5-receded.json
pnpm run matrix -- stage "$STAGE" --profile "$PROFILES" --renderer webgpu,css \
  --set calibration,validation,holdout,recorded,probe \
  --material-profile "$ACTIVE" --receded-profile "$RECEDED"
# A single-scene diagnosis is scratch, not an attempted canonical publication.
pnpm run compare -- --stage "$STAGE" --profile "$PROFILES" --scene photo__rrect-md__rest \
  --material-profile "$ACTIVE" --receded-profile "$RECEDED"
for tier in webgpu css; do
  pnpm run compare -- --stage "$STAGE" --profile "$PROFILES" --renderer "$tier" \
    --material-profile "$ACTIVE" --receded-profile "$RECEDED" \
    --set calibration,validation,recorded,probe --write-partial
done
# After the configuration is frozen, read holdout once per tier into the SAME stage.
for tier in webgpu css; do
  pnpm run compare -- --stage "$STAGE" --profile "$PROFILES" --renderer "$tier" \
    --material-profile "$ACTIVE" --receded-profile "$RECEDED" --set holdout
done
pnpm run matrix -- status "$STAGE"
pnpm run matrix -- publish "$STAGE"   # one act, only after all declared cells are present
```

These commands run from `packages/calibration`. The stage path must be new. Use a separate stage
for the dark document pair and both dark profiles. Each stage declares one document pair; all
profiles of the previous generation must move together. Document paths and twelve-hex content
hashes are recorded in `membership.json` before measurement. Fixture membership is expanded from
the canonical `scenes.json` split and fixture manifest, so one row does not stand in for a set.
The optional recorded/probe sets in this full-bed recipe preserve those readings; wave-local
identification beds never enter this path. The document pair must be newly sealed: publishing
another reading of an already published identity is refused rather than inventing a reseal.

`compare --stage` selects `<stage>/matrix.json`; an explicit `--out-matrix` must name that file.
A single scene is a diagnostic contribution, not completion. `--write-partial` preserves successful
scratch measurements when some cells fail and still exits 1. Repair missing cells there; the
publisher refuses incomplete membership (including holdout when declared), foreign rows and
changed document hashes. Separate exploratory `compare --out-matrix /tmp/exploration.json`
remains ordinary schema-5 scratch. `diff --stage <dir>` contributes one cell with the same row
checks; `diff --matrix <scratch>` remains available. Neither can write canonical destinations.

`matrix status <stage>` reports declared/present/missing counts. `matrix publish <stage>` prints
the new file, bytes and SHA-256 after installation. It refuses existing serialized keys anywhere
in recorded history, duplicate generation identities, colliding filenames, alias repointing,
and replacement of only part of a previous generation's profile membership. It preserves raw
row byte slices in key order. Retired files stay immutable in `results/generations/`; there is
no `retire` verb, because publication changes the prior entry's index status. The historical
splitter's `apply` stays refused and `results/superseded/` stays untouched.

Publication serialises with an exclusive lock, fsyncs temporary generation/index files and
renames the index last. A caught failure before that commit point rolls back the new file;
old authoritative bytes remain unchanged. A process crash may leave a complete unindexed
orphan and stale lock; inspect them before cleanup. A failure after index rename is already a
committed publication, so do not retry as an append. No published file receives a later holdout
row, and a new stage name cannot bypass that rule.

Use `results/2026-09-26-w40-g1-writers/append-check.py` to take a before witness and verify the
landing against its stage. At the seal merge also copy the capture tree, preserve the prior
tree, run `pnpm run check-capture-tree` on the canonical captures and run the unchanged freeze
verifier. Recorded digests and W30/W36 append witnesses remain history, never rewritten pins.

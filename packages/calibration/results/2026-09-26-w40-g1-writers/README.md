# W40 G1 — staged, once-only generation publication

Executes W40 charter clauses 4–5 and the MARKED writer contract; claims §5.190.
This gate adds a writer, not a material read. No real generation was published or retired.
The frozen matrix, published files, archive, freeze pin and recorded numbers stay unchanged.

## Tool index

- `../../src/generation-stage.ts`: declaration, canonical fixture expansion, document and row
  checks, status and publication preflight. `../../cli/matrix.ts` exposes `stage`, `status`,
  `publish`; `../../cli/compare.ts` and `diff.ts` accept `--stage`.
- `../../src/matrix-write-guard.ts`: the sole `publishGeneration` entry. Measurement guards
  stay closed to frozen/indexed/archive paths and filesystem aliases.
- `../../src/matrix-store.ts`: exposes its existing raw-row/index/document readers and a raw
  splitter-envelope constructor; existing legacy-envelope digest and recorded pins do not move.
- `../../test/generation-stage.test.ts`: copied-source disposable repository tests; no test
  publishes against the real evidence. Real frozen/generation/archive bytes are hashed before
  and after. `stage-red.txt` is the missing-CLI red observation; `stage-tests.txt` the focused
  passing suite. Tests cover complete/incomplete membership, declaration drift, row/document
  drift, aliases, duplicate keys/identities, receded-only reseal, retirement, filename collision,
  staged compare preflight, partial-write failure, index-rename rollback and W39 path identity.
  `frozen-alias-red.txt` records an extra boundary: an indexed alias must not shadow the frozen
  file's document lookup. That refusal is now tested even when the new row key differs.
  The final 15 tests also validate a real recorded row against copied active/receded documents
  and the external-document absolute-path convention, not only synthetic labels.
- `append-check.py`: `snapshot <results> <witness.json>` BEFORE a future read; then
  `verify <results> <witness.json> <stage/matrix.json> <published-filename>` AFTER publication.
  Frozen and every old file must remain byte-identical, the archive is inventoried completely,
  index history/aliases must persist, and new rows must equal the stage's raw byte slices.
  W30's `append-check.py` and W36's witnesses stay unchanged history.
- `publisher-demo.py`, `publisher-append-demo.txt`: actual CLI publication followed by the
  append checker on a separate disposable source copy. All four staged raw slices match,
  including the non-canonical numeric spelling `1.000e-7`; real canonical bytes stay unchanged.
  `publisher-demo-before-path-fix.txt` preserves the earlier 2,084-byte synthetic result; the
  current 2,168-byte result uses capture-compatible repository-relative document clauses.
- `test-append-check.py`, `append-check-synthetic.txt`: one synthetic publication and thirteen
  tamper/refusal cases on disposable repositories, including JSON-equivalent reserialization.
- `../../scripts/check-capture-tree.ts`, `../../test/w32-capture-tree.test.ts`: exact retired
  active/receded identities classify as superseded. A current-only identity, or hashes combined
  from unrelated entries, does not become a retired generation. Historical archive treatment
  is retained. The test retires a synthetic indexed generation and covers a shared active hash.
- `w39-guard-red.txt`, `w39-wave-test.txt`: the launcher originally omitted `generations/`;
  it now refuses directory/index/files, including symlink/case aliases and hardlinks. The
  W39 evidence README records this beside the change; no scenes, split, preflight or pin changed.
- `declaration-smoke.txt`: the documented light declaration on canonical fixture metadata in
  the disposable copy: 780 declared, zero present, 780 missing; no capture or publication.
  The earlier package-relative label reading remains in `declaration-smoke-before-path-fix.txt`.
- `test-first-timeouts.txt`: first full run reached only two default 5-second timeouts: the
  pre-existing G0 multi-process refusal loop (6.39 s) and W35's 238,292-bin population check
  (5.13 s). Each now has an explicit 30-second budget; every assertion is retained.
  `test-second-timeout.txt` records W37's existing score-reconstruction test exceeding 60 s
  at 66.3 s; its budget is now 120 s, with every native-pixel reconstruction assertion retained.
- `verification.txt`: final chain exit 0; 207 test files, 2,837 passing tests, 1 existing
  capture-dependent skip; demo build exit 0.
- `build.txt`, `lint.txt`, `test.txt`, `demo-build.txt`: workspace and demo verification from
  a disposable full repository copy, not a writer experiment on this checkout's evidence.
- `freeze.txt`: unchanged verifier, 1,818 intact entries, exit 0.
- `capture-tree.txt`: read-only canonical tree in the original checkout, 1,893 matches,
  seven no-row captures, zero mismatches, exit 0.
- `protected-before.json`, `protected-after.txt`: hashes of the protected paths in this
  worktree AND the original checkout; before/after identity including W39 recorded artifacts.

## Publication contract and failure boundary

Declare a new scratch directory with `matrix stage` before measuring. Membership names one
active/receded pair, its paths and twelve-hex hashes, profiles, tiers and sets. Every fixture
in each declared combination is expanded from canonical scenes/manifest; editing the cell
list cannot narrow it. Compare checks invocation documents before capture and rows before
writing; diff checks measured rows before writing. Status counts required versus present
cells. Ordinary schema-5 scratch remains available for exploration.

Publish only when every declared fixture is present, including holdout when declared. It
checks every authoritative generation, including retired/archive rows, before writing anything.
An existing key or identity is refused, not appended to or silently resealed. Filename and alias
collisions are preflighted; shared aliases retain all owners. A receded-only reseal has a compound
filename. Replacing a generation requires its whole prior profile membership.

The exclusive publication lock encloses preflight and installation. Complete temporary generation
and index files are fsynced; the generation is installed, directory synced, then index renamed
last and directory synced. Caught pre-commit failures remove the unindexed file; injected partial
write and index-rename failures leave authoritative bytes unchanged. A crash may leave a complete
unindexed orphan and stale lock, never an authoritative partially written generation. Inspect
these before cleanup/retry. A failure after index rename is already committed and must not be
retried as an append. There is no cross-process database transaction or automatic crash recovery.

Retirement is index status over immutable files. There is no separate `retire` verb: publishing
changes the prior entry to retired without moving its file. The old splitter's `apply` remains
refused; `superseded/` remains history, never a destination for new retirement.

## Recipes and unchanged claims

`CLAUDE.md`'s single-scene/default, partial-run and holdout recipes now declare a complete light
stage, make diagnostic/full/tier reads there, read holdout into that same stage once after the
seal, inspect status and publish once. `packages/calibration/README.md` documents the same sequence
(the package previously had no README). A separate dark stage has its two dark profiles and
own pair. W39 G3 now explicitly stages its whole membership and publishes once at the seal merge.

Unchanged, checked: the archive README describes the historical splitter and alias ownership,
not a route for new generations; it stays history. W30/W36 witnesses still identify their reads,
not this indexed layout. The freeze verifier claims unchanged frozen evidence and still checks
1,818 entries. The capture-tree recipe still requires copying captures at landing; this gate
creates no captures. G0's evidence remains its historical account of the then-closed writer.
No browser, native capture, material fit, holdout measurement, golden, bound or floor moved.
Independent review and merge belong to the parent.

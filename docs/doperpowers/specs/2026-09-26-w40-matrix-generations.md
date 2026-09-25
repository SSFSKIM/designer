# W40 — the matrix's generations as files: a frozen-only `matrix.json` and indexed, immutable macOS 27 generation files, no history rewrite (2026-09-26)

**Status: G0 MERGED `4658dfee` (2026-09-26, §5.189); G1 implemented on `w40-g1-writers`, independent review pending.**
Chartered by the parent under the user's ruling of 2026-09-26 (W39 charter Decision Log 1): a
small housekeeping wave after W39 G0's merge (`ba38ebbf`), to land before W39's conditional G3
landing, moving FUTURE generations of `packages/calibration/results/matrix.json` to indexed
per-generation files with no history rewrite. Grounded by a read-only memo (2026-09-26) that
inventoried every reader and writer and measured the layouts.

## Purpose

Every canonical read commits a new 60–77 MB revision of one file. The eight largest blobs in
the repository's history are that path; GitHub warned (GH001) on the W36 G2 push. The memo
measured the next hazard exactly: today's file is 69,569,261 bytes with 1,893 rows, of which
1,107 frozen macOS 26.5 rows are 39,150,416 bytes (56.27 %); a two-scheme read that appends
both macOS 27 generations before the splitter retires the old ones transiently writes
**99,988,190 bytes — 11,810 bytes under GitHub's 100 MB refusal**, before W39 adds a row. The
purpose is that a read never again re-commits the frozen bed or the other scheme's rows, that
every recorded row stays byte-identical and addressable by the same document hashes, and that
nothing in Git history moves.

## Parent-Level Acceptance

1. **The frozen bed does not move.** `results/matrix.json` becomes a frozen-only schema-5
   envelope holding exactly the 1,107 macOS 26.5 rows as their original byte slices in their
   original order; `results/2026-09-16-w29-freeze/freeze.py verify` reads **1,818** against the
   unchanged `sha256.txt`; no frozen row's bytes change.
2. **Generations are files, immutable after landing.** Today's two macOS 27 generations (active
   85ad7f7e3e0d + receded 30fbe05986ae, 509 rows; active 0eac5b294cc2 + receded 5cec8c961201,
   277 rows) are byte-sliced into `results/generations/<active-sha>.json` (compound
   `<active>-<receded>.json` when only the receded document changes), with
   `results/generations/index.json` mapping every active and receded hash to its file, naming
   the current generation per profile, and carrying document paths and digests, rowCount, bytes
   and file SHA-256. A resealed read adds new files and changes only the index's "current"
   selection; the previous file stays in `generations/` as retired. **A generation's identity
   is the pair (active, receded-or-none)**; a document-hash alias enumerates EVERY owner across
   both indexes (the archive's `sharedReceded` owners included), `loadGeneration(active)` refuses
   an ambiguous active hash unless the receded qualifier is supplied (after `(A,R1)` in `A.json`
   and a receded-only reseal `(A,R2)` in `A-R2.json`, both own A), and selecting the CURRENT
   generation is a separate explicit operation from resolving one. `results/superseded/` (15
   files, 26 aliases) is untouched and its historical aliases are never repointed.
3. **The union is the matrix, row for row and byte for byte.** After migration, the key-sorted
   union of the frozen file and the current generation files equals the pre-migration matrix
   row-for-row (1,893 cells, the same serialized keys) and byte-for-byte per row; no key appears
   in two authoritative files; the 786 macOS 27 rows appear only in the new files. The proof is
   the STRONGER one the review verified is available: the union of the raw `{…}` row slices in
   key order, with the splitter's original prefix, separator and suffix, reconstructs the
   pre-migration file bit-identically (SHA-256 7df96c9246bc9b964fd6e173e742f49dcf493ccb360f7df505a0157240eaf0de);
   a JSON reserialisation is not that proof.
4. **Every reader reads the union; every writer publishes a generation.** One loader
   (`packages/calibration/src/matrix-store.ts`: `loadCurrentRows`, `loadCurrentProfile`,
   `loadGeneration(active, receded?)`, opt-in `iterateRecordedRows`) with a Python adapter for
   the evidence readers; the 14 maintained readers/writers the memo tabled are ported: compare
   and diff (scratch `--out-matrix` / `VITREA_MATRIX_PATH` stay ordinary schema-5 JSON; the
   canonical route stages in scratch and publishes each COMPLETE generation once, refusing a
   replaced row or a colliding file name; `--write-partial` belongs to scratch only — and
   **invocation success is not publication**: a generation declares its membership (profiles,
   tiers, sets) up front, every run of that membership — calibration and validation, both tiers,
   and the one holdout read after the configuration is frozen — is staged into the same scratch
   generation, and the generation is published canonically ONCE when the declared membership is
   complete; a request to publish calibration/validation canonically and append the holdout to
   that same generation later is refused, because an immutable file admits no later rows and a
   reseal would misrepresent an unchanged configuration), the
   splitter's future retirement as an index status over immutable files, the freeze verifier
   pointed at the frozen file, `check-capture-tree` on the union with archived hashes still
   classified, the adopted-thresholds rows M1/M2/C1/X1/L1 and tier-coherence on the union, the
   demo's build-time reduction and its independent oracle with identical figures, order and
   count, the W32/W36/W38 tests on the union or their named generations.
5. **Recorded digests are history, not pins to rewrite.** W36 L1's whole-matrix SHA-256, W38
   E2's pre-W38 whole-file SHA (`e2.py` and `w38-e2.test.ts`), `vibrancy.ts`'s provenance SHA,
   and every W30–W38 evidence script's recorded whole-file digest keep their recorded values as
   historical identifiers, and they stay CHECKABLE by a **streaming legacy-envelope digest**:
   the loader can hash the key-ordered raw row slices with the legacy prefix, separator and
   suffix without writing a file, so W38 E2 checks its recorded pre-W38 SHA against the envelope
   of its NAMED input generations (and `e2.py`'s whole-declaration reconstruction keeps that
   SHA), and W36 L1's freshness check hashes the CURRENT union's envelope (so it still certifies
   the live input, and a new cut re-pins a new envelope digest beside the old); raw-file hashing
   is retained for scratch overrides. No recorded number is rewritten and no historical script is
   bulk-edited — a pre-W40 script replays against the Git revision it read.
6. **Nothing else moves.** No scene, fixture, profile document, golden, adopted bound, floor,
   capture tree or W39 artifact changes; W39's wave-owned probe matrices are never imported into
   the canonical index; no Git attribute (`-delta`, `merge=ours`) is set; no LFS.
7. **Verified in a fresh checkout.** `pnpm -r build && pnpm -r lint && pnpm -r test` green; the
   demo builds with the identical projection; CI and Pages need no new step.

## Grounding Baseline (main at `ba38ebbf`)

Memo facts: 14 direct maintained readers/writers (three write); 125 historical W30–W38 files
mention the path, many executable; the row key is profile | scene | engine | version | renderer
| backend | adapter | colourSpace | capturePath, and capturePath carries each document's path and
12-hex SHA so a reseal appends rather than overwrites; `superseded/index.json` has non-injective
receded aliases (two historical owners each for 45acb6d916b9 and 4e68f81869f6); the four
current document groups slice to 15,223,541 / 23,926,917 (26.5 dark/light) and 10,630,441 /
19,788,488 (27 dark/light) bytes; pack 471.76 MiB in five packs; per two-scheme read the layout
saves 39,150,332 logical bytes (56.27 %).

## Design (MARKED where the layout is fixed)

- **Layout (c), MARKED**: frozen-only `matrix.json`; `generations/<active>.json` (compound name
  for receded-only reseals); `generations/index.json`; `superseded/` untouched; retired 27
  files stay in `generations/` with status in the index (no rename blob, no alias reopening).
- **Loader contract, MARKED**: schema, metadata bytes and SHA, active/receded clause
  completeness, row ownership, unique serialized keys across current files, no double presence
  in frozen and generation files — all checked on load; an ambiguous receded-only lookup returns
  every owner or requires the active qualifier.
- **Writer contract, MARKED**: stage in scratch, publish a complete generation once, refuse
  replacement of a published row and any file-name collision, preflight every target name and
  alias before touching a file; an intermediate revision is never committed.
- Migration script committed and reproducible (`results/2026-09-26-w40-g0-generations/migrate.py`),
  with a snapshot of the 1,893 source row byte spans, serialized-key digest and the demo
  reduction taken BEFORE the move and compared AFTER.

## Children

### G0: The store, the migration and the readers — one merge

Branch `w40-g0-generations`; evidence `packages/calibration/results/2026-09-26-w40-g0-generations/`;
ledger **§5.189**. Delivers clauses 1–5 for READERS and the migration: the loader with synthetic
fixture tests (both layouts, a repeated receded SHA, active-only and receded-only reseal, a
missing file, an altered hash, a duplicate row, the scratch override), the byte-slice
migration with its before/after equality proof, the ported readers and tests, the demo's
reduction and oracle, the freeze at 1,818, the capture-tree check on the union (the canonical
tree if present), `CLAUDE.md`'s "Generations" paragraph rewritten beside its history. **Every
canonical write route fails closed in G0**: `compare` (its default AND any explicitly named
authoritative destination), `diff --matrix` pointed at the frozen file or at any generation
file, and the old splitter's `apply` once the layout has moved, all REFUSE with a message naming
G1's publisher; genuinely separate scratch JSON stays writable; tests cover the default, an
explicitly named authoritative path and a scratch path for each CLI. The publication
implementation is G1's. Independent review, then merge.

### G1: The writers and the retirement route — one merge

Branch `w40-g1-writers`; evidence `…/2026-09-26-w40-g1-writers/`; ledger **§5.190**. Delivers
clause 4's writer contract for `compare` and `diff`, the splitter's index-status retirement
over immutable files (the old `apply` refuses once the layout has moved), a new append-checker
manifest for indexed reads (W30's and W36's byte witnesses retained as history), the
staging/publication invocations with their partial-failure behaviour written into `CLAUDE.md`'s
actual commands (the single-scene default, `--write-partial`, the holdout read) and the
calibration README, and the W39 charter's G3 recipe note (G3 stages its whole membership and
publishes once at the seal). Independent review, then merge.

## Cross-Child Contracts

- **X1 — the freeze, intact** (1,818; frozen bytes unchanged). **X2 — no history rewrite**, no
  recorded digest or number rewritten (corrections beside). **X3 — equality by proof**: the
  row-for-row and byte-for-byte comparison is a committed artifact, not a statement. **X4 —
  scratch stays a matrix**: `--out-matrix` / `VITREA_MATRIX_PATH` remain ordinary schema-5 JSON
  so every W3x recipe that materialises a scratch file keeps working. **X5 — W39's boundary**:
  wave-owned probe matrices never enter the index; W39 G3, if it runs, publishes through G1's
  writer. **X6 — routing and hygiene** as W39 X9: `astra`/`sol` workers, `doperpowers:reviewer-*`
  reviews, `--no-ff -F` merges, no attribution trailers, no browser run needed (unit suites and
  builds only; the demo e2e only if site wording changes, under X6's machine facts).

## Ordering & Dependency Map

W39 G0 merged → W40 G0 → W40 G1 → (W39 G1/G2 may run in between; they touch no canonical
matrix) → W39 G3 only after W40 G1.

## Risks & Mitigations

- **A reader missed.** The memo's inventory is the checklist; the fresh-checkout `pnpm run ci`
  and the demo build are the net; any script found later that opens the old path by default is
  ported in a follow-up commit, never by regenerating a monolith.
- **A historical pin fails on layout** (W38 E2's whole-file SHA does exactly this). Converted to
  the generation digests with the old value kept as history — clause 5.
- **Pack size does not shrink.** Stated; the objective is the per-read growth, not the past.

## Decision Log

### Decision Log 1 — the layout (the parent's, under the user's ruling): (c), as MARKED. Ruled 2026-09-26.
### Decision Log 2 — retired 27 files stay in `generations/` with index status; no move to `superseded/` (the parent's). Ruled 2026-09-26.
### Decision Log 3 — recorded whole-file digests are history; freshness checks convert to generation digests (the parent's). Ruled 2026-09-26.

## Tracking Map

| child | status |
| --- | --- |
| G0 | MERGED 2026-09-26 as `4658dfee` (§5.189): frozen-only matrix 39,150,416 B, generations 19,788,488 / 10,630,441 B, equality proof exact (envelope 7df96c92…), freeze 1,818, canonical capture tree 1,893 matches exit 0; review 1 P1 (case-alias identity bypass) fixed, re-review clean |
| G1 | MERGED 2026-09-26 (§5.190): stage/status/publish, retirement as index status, recipes rewritten, W39 wave.py boundary; review 1 P1 / 1 P2 fixed, re-review clean |

## Surprises & Discoveries

- The transient 99,988,190-byte hazard: the append-then-split order of today's read is what
  puts the next two-scheme read 11,810 bytes under GitHub's refusal.

- G0's byte-slice proof reconstructs all 1,893 rows and the original whole-file SHA without
  materializing a union. Frozen-only matrix bytes are 39,150,416; the light/dark generation
  files are 19,788,488 / 10,630,441. The unchanged freeze verifier reads 1,818 (§5.189).
- A red-state CLI test briefly mutated the worktree matrix, restored exactly from HEAD before
  migration. The snapshot was independently checked against the original Git blob. Final CLI
  integration tests use disposable copied-source repositories; the incident and SHAs are in
  G0's evidence README. No frozen or measured row changed in the migrated layout.
- The grounding memo's W34 `browser.py` example is wave-owned, not canonical. G0's README
  records the corrected historical-reader inventory beside the memo, not by rewriting it.
- G1's retirement integration must extend capture-tree's `superseded` classification to hashes
  in retired `generations/` entries before introducing one. G0 retains archived classification
  exactly and creates only current entries; the store itself resolves retired generations.

## Revision Notes

- 2026-09-26 (G1's merge, the parent): merged after an independent review (one P1: identical
  active and receded hashes published an unreadable index entry, now refused at membership
  validation; one P2: the capture checker lost the union through an external symlink or
  hardlink alias, now resolved by canonical identity) and a clean re-review; freeze 1,818;
  canonical capture tree 1,893 matches / 7 no-row / exit 0; nothing recorded rewritten. The
  worker's Revision Note below is kept as written. Merged together with the `ci-linux-replays`
  branch (the W35–W38 evidence replays on CI's BLAS; tracker entry), which W40 G1's timeout
  budgets complete. Worktrees removed.
- 2026-09-26 (G1): implemented the declaration → scratch runs → once-only publication route,
  with document/fixture checks, raw row envelopes, every-owner aliases, index-last installation
  and rollback proofs. Retirement leaves old files untouched. The classifier recognizes exact
  retired pairs; the recipes now include holdout in the original stage. W39's launcher itself
  lacked the generations directory in its refusal list (the downstream compare guard already
  refused it); the identity-aware boundary is now direct, with W39's pins/evidence unchanged.
  Claims §5.190 and the G1 evidence directory record implementation and verification. Independent
  review and merge remain the parent's.
- 2026-09-26 (the user, routing): "prefer opus over sol" — from here, children, fix waves and
  grounding run on the default `opus` worker or on `astra` at medium/high; `sol` is no longer
  the default rung named in X9's carry-over. Reviews still route through the review-code
  agents (`reviewer-high` for gate merges).

- 2026-09-26 (G0's merge, the parent): merged `4658dfee` after an independent review (one P1:
  canonical paths classified by spelling, bypassed by a differently cased alias on this
  case-insensitive filesystem in the guard and both adapters; fixed by filesystem identity) and a
  clean re-review; freeze 1,818; `check-capture-tree` on the canonical tree 1,893 matches / 7
  no-row / exit 0; nothing recorded rewritten. The worker's Surprises entries (the proof without
  a materialised union, the restored red-state incident, the memo's `browser.py` correction, the
  G1 classifier follow-up) are kept as written. Worktree removed.

- 2026-09-26 (G0): store, byte-preserving migration, readers and fail-closed write routes
  implemented and verified on `w40-g0-generations`; 206 test files, 2,817 tests passed, one
  existing capture-tree-dependent skip. Equality, freeze and canonical capture-tree check
  pass. Independent review/merge remain the parent's; publication and retirement remain G1.

- 2026-09-26 (v2, the parent): one adversarial round folded — P1 every canonical write route
  (compare's named destinations, `diff --matrix`, the old splitter) fails closed in G0, not only
  compare's default; P2 the two digest pins are served by a streaming legacy-envelope digest the
  review verified reconstructs the current file bit-identically, so neither recorded SHA changes
  meaning; P2 generation identity is (active, receded-or-none) with every-owner aliases and
  refused ambiguity; P2 publication is one act after the declared membership including the
  holdout read is complete, never an append to a published generation. G0 dispatched.
- 2026-09-26 (v1, the parent): chartered from the W40 memo; adversarial review requested.

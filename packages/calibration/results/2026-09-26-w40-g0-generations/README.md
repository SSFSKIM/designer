# W40 G0 — indexed matrix generations

Claims §5.189; charter `docs/doperpowers/specs/2026-09-26-w40-matrix-generations.md`,
clauses 1–7. This is a byte-preserving storage migration, not a new material read.

## Tool index

All paths below are relative to this directory unless stated otherwise. Use Python 3.12.

- `snapshot.py` → `snapshot.json`: original row offsets, serialized keys, per-row raw-byte
  hashes, key-order digest, document groups and the exact demo projection. It refuses to
  overwrite a witness with different source bytes. Reproduce on the pre-migration revision,
  not against the frozen-only file.
- `source-proof.txt`: independent hash verification of every snapshot span against the original
  `559bd1ca` Git blob, including its whole-file SHA and size.
- `demo-before.json`: the pre-migration `reduceMatrix()` result: 1,893 source rows and 411
  projected cells, including their order and exact figures. The demo test compares the whole
  result, in addition to its independent direct-file union oracle.
- `migrate.py`: one-time migration, derived from W30's raw brace-walk/envelope. Preflights
  every source slice, shipped document, count and destination; refuses after the index exists.
  Reproduce on the pre-migration source with the saved snapshot and demo witness in place.
- `matrix_store.py`: read-only Python adapter. Current reads are the frozen/current union;
  named reads resolve frozen, current, retired and archived document identities. Raw slices
  permit streaming legacy-envelope hashing without materializing a monolith.
- `verify-migration.py` → `equality.json`, `equality.txt`: compares every key and raw-slice hash
  against the before snapshot, checks ownership/order and reconstructs the legacy digest.
- `adapter-test.py`, `adapter-test.txt`: Python adapter contracts, including the four named
  groups' complete legacy-envelope reconstruction.
- `../../src/matrix-store.ts`, `../../test/matrix-store.test.ts`: TypeScript store and synthetic
  contracts. Shared receded aliases enumerate every owner; an active hash retained with two
  receded hashes requires the qualifier. Explicit `null` (Python `None`) selects the no-receded member;
  omission remains an unqualified lookup. History is opt-in, never mixed into current rows.
- `../../src/matrix-write-guard.ts`, `../../test/matrix-write-guard.test.ts`,
  `../../test/split-generation-guard.test.ts`: canonical write refusals and separate scratch
  writes. CLI integration tests execute copied sources in a disposable repository, never
  against canonical evidence. The actual canonical file is checked unchanged after the suite.
- `build.txt`, `lint.txt`, `test.txt`, `demo-build.txt`: workspace and demo verification.
  `store-test.txt` covers explicit no-receded identity and canonical read aliases;
  `store-lint.txt` is the intermediate store integration typecheck.
  Earlier full-suite timeout logs are retained separately; no metric or evidence pin moved.
- `scratch-read.txt`: adopted thresholds against an ordinary pre-migration scratch JSON.
- `freeze.txt`: unchanged W29 verifier and pin, 1,818 intact entries.
- `capture-tree.txt`: read-only check against the original checkout's canonical tree via
  `VITREA_WEB_CAPTURES`; exit 0, 1,893 matches and seven captures without rows, no mismatches.
- `scope.txt`: protected tracked paths unchanged, and all 15 archived file metadata records
  verified; 26 archive aliases retained.

## Physical layout and equality

Before: `results/matrix.json`, 69,569,261 bytes, 1,893 rows,
SHA-256 `7df96c9246bc9b964fd6e173e742f49dcf493ccb360f7df505a0157240eaf0de`.
After, relative to `results/`:

| file | rows | bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `matrix.json` | 1,107 | 39,150,416 | `a0b9720b079dc28980d097ddd47cd2d005e79dc011aa8c81f8bf887353d57843` |
| `generations/85ad7f7e3e0d.json` | 509 | 19,788,488 | `39ac0ba98ca200b10b194f6b45af54df8bf8b2dcbe6b98946a1c8b8aed58356e` |
| `generations/0eac5b294cc2.json` | 277 | 10,630,441 | `f72429653e29fd760123a7273436aaaeebc332311c4a53c677b03c004468f979` |

All 1,893 original raw row slices match; zero altered/missing/extra/duplicate authoritative
keys. The 786 macOS 27 rows live only in generation files. The key-sorted union's legacy
prefix, separator and suffix reconstruct the original SHA-256, without writing that union.
The frozen row order is unchanged. `generations/index.json` records each document pair,
file bytes/hash, profile counts, current selection and aliases. `superseded/` is untouched.

## Maintained readers and unchanged claims

| reader | what it reads now |
| --- | --- |
| capture-tree checker | current union; archive hashes remain classified; exit codes 0/1/2 unchanged |
| adopted thresholds | current union or explicit scratch; M1/M2/C1/X1/L1 populations and bounds unchanged; named archive baselines; L1 hashes current legacy envelope, scratch raw file |
| tier coherence | current union, the same twelve macOS 27 readings |
| W32 exterior referee | temporary schema-5 projection of union or qualified historical generation; historical flags retained |
| W36 level test | exact named baseline pair through the store, whether current or archived |
| W38 E2 test and `e2.py` | four named input groups, including frozen light/dark, with the unchanged pre-W38 SHA reconstructed from raw slices |
| vibrancy | named frozen 26.5 light generation; recorded provenance lineage retained; new provenance uses current envelope |
| demo reduction | key-sorted current union; independent direct-file oracle and exact before projection; 1,893 source rows, 411 displayed cells |
| compare/diff | canonical destination refused before I/O; named scratch remains ordinary schema-5 JSON |

Unchanged, checked: `apps/demo/src/site/Site.tsx` says "one generation per profile". That
remains true of the current union, selected by `currentByProfile`, rather than a claim about
one physical file. `freeze.py` claims identity of 26.5 evidence and ordered frozen rows, not
identity of the old whole matrix: its unchanged 1,818-entry pin still holds. The archive
README describes the historical single-file/split layout; it stays untouched history, with
W40's current layout documented here and in `CLAUDE.md`. Capture-tree paragraphs still require
preserving/copying the pixels at a read's landing; this gate creates no captures.

## Writer boundary and remaining work

`compare` refuses its default, explicitly named frozen/generation files and aliases.
`diff --matrix` refuses those files too; its separate `--out` report route is also guarded.
The old splitter's `apply` refuses once the generation index exists. Diagnostics name G1's
publisher. Separate scratch JSON stays writable, including partial runs. No publisher or
index-status retirement route is implemented here: G1 publishes a complete declared
membership once, including its frozen-configuration holdout read. W39's wave matrices were
not imported. No browser, native capture, material, fixture, golden, bound or floor moved.

## Test incident and restoration

An initial red-state `diff --matrix` integration test ran before its guard existed and
briefly appended one synthetic row to the worktree's canonical matrix. The accidental SHA
was `9b2b99ef076eab5e68fa62caa298851c8f81079126f6f1601f1462942ec36971`.
The worker restored that path from the exact HEAD blob with
`git show HEAD:packages/calibration/results/matrix.json > <worktree>/packages/calibration/results/matrix.json`,
not a hand edit, and verified an empty path diff and the original
`7df96c9246bc9b964fd6e173e742f49dcf493ccb360f7df505a0157240eaf0de` SHA before migration.
The coordinator subsequently requested `git checkout --` as the restore form; that redundant
restore was not run after migration had begun, to avoid erasing the migrated layout.
The snapshot was reverified against HEAD's exact source bytes. All final CLI integration
refusal/write tests use a disposable repository mirror, so removing a guard cannot mutate
real evidence. The equality proof and frozen verifier certify the final bytes independently.

## Historical readers left at their recorded revision

These executable defaults open the old whole working/current matrix, sometimes through a
shared reader or as a baseline beside a scratch input. Their meaning is the bed **at their
recorded revision**, sometimes the before-split interval, not W40's frozen-only file. Replay
at that revision, or explicitly port a reused gate to the current union/named generation.
No historical measurements or witnesses were bulk-edited. Paths are under `results/`;
braces enumerate individual filenames.

- W30 `2026-09-20-w30-g0-cut/{departure-stat,shadow-cut,structure-cut}.py`;
  `2026-09-20-w30-g1-split/{split-generation,append-check}.py`;
  `2026-09-20-w30-g3-operators/{departure-stat,gate-diff,read-sigma,structure,verdict}.py`;
  `2026-09-20-w30-g3b-thin-strip/{departure-stat,moved-cells,precheck}.py`;
  `2026-09-20-w30-g4-landing/demo-figures.py`.
- W31 `2026-09-21-w31-g0-chroma-cut/cut.py`;
  `2026-09-21-w31-g1-exterior-instrument/{exterior-instrument,support-rule-check}.py`;
  `2026-09-21-w31-g3-chroma-fit/{append-check,departure-stat,read-append-check,verdict}.py`;
  `2026-09-21-w31-g3c-accessibility-gate/{accessibility-read,append-check,gated-count,read-append-check,verdict}.py`;
  `2026-09-21-w31-g4-landing/{accessibility-identity,chroma-cut,chroma-mean-after,demo-figures,gated-count}.py`.
- W32 `2026-09-21-w32-g0-exterior-cut/{clearance,departure-stat,exterior-cut,extents-by-backdrop,model-fit,recede-26.5,stops}.py`;
  `2026-09-21-w32-g1-shadow-fit/{append-check,b2-mask,chroma-cut,clearance,departure-stat,exterior-cut,gated-count,model-fit,read-append-check,repro,stops,verdict}.py`;
  `2026-09-21-w32-g2-landing/{chroma-cut,departure-stat,exterior-cut,gated-count,m2-rebaseline}.py`.
- W33 `2026-09-22-w33-g0-rim-cut/{forms.ts,referee.py}`;
  `2026-09-22-w33-g1a-contour-model/{model.py,prices.ts}`;
  `2026-09-22-w33-g1b-rim-fit/{append-check,canonical-verdict,chroma-cut,exterior-cut,read-append-check,refresh-read-witnesses}.py`;
  `2026-09-22-w33-g2-landing/{black-cut,chroma-cut,gated-count,referee-union,referee}.py`.
- W35 `2026-09-24-w35-g0-edge-cut/canonical.ts`.
- W36 `2026-09-24-w36-g0-level-cut/matrix-cut.py`;
  `2026-09-24-w36-g1-black-branch/{append-witness,black-cut,chroma-cut,exterior-cut,formula-read,holdout-difference,l1-cut,price-closure,price-css,price,read-append-check,read-witness}.py`;
  `2026-09-24-w36-g2-landing/{confirm-evidence,discriminate,gated-count,l1-cut,sheets}.py`.
- W37 `2026-09-25-w37-g0-edge-identification/{canonical,declare}.py`;
  `2026-09-25-w37-g0b-edge-identification/canonical.py`.
- W38 `2026-09-25-w38-g0-rim-axis-cut/preflight.py`. Its `e2.py` is the explicit maintained
  exception ported in this gate, not an old-path reader anymore.

Correction beside the grounding memo: W34 `browser.py` reads its **wave-owned**
`HERE/matrix.json`, not the canonical matrix; `wave.py` names the canonical path only in its
denial list. Neither belongs to the inventory. Scratch-only render/browser/round scripts,
explicit-input scripts, synthetic self-tests and comments are likewise not canonical opens.

G1 integration note: capture-tree's `superseded` classification currently names hashes in
`superseded/index.json`, as it did before W40. Before G1 introduces the first `retired`
`generations/` entry, extend that classifier to its hashes and test `--superseded-ok`; otherwise
such a tree is conservatively reported as a mismatch. G0 publishes no retired entry.

## Verification notes

`test-initial.txt` preserves the first full run's only failure: W38's Python self-test now
streams raw envelopes and took 8.595 seconds under the suite, exceeding that test's implicit
five-second timeout. Its explicit timeout is now 60 seconds (the subprocess already had a
180-second bound); its four targeted tests passed. `test-contention.txt` preserves the next
run's unrelated W35 population assertion at 5.107 seconds against five. No W35 test, criterion
or dataset was changed; final verification runs without overlapping worker checks.

Builds retain the existing large-chunk warning; Vite additionally warns that the store's
extensionless imports, like existing tooling imports, will need attention if its future
native config loader is selected. The production build succeeds with the configured loader.
Unit DOM emulation emits its existing canvas-getContext diagnostics; no browser suite ran.

Final result: ordered workspace build, lint and tests **pass**: 206 files, 2,817 passed,
one existing X1 skip (no local capture tree). Calibration: 57 files, 737 passed / one skipped;
demo: six files, 47 passed. The separate demo production build passes. `freeze.txt` records
1,818 intact and `capture-tree.txt` records exit 0 against the original canonical tree.

## Independent review correction — P1 filesystem identity

The review of `b648834b` found one blocking issue: on this case-insensitive filesystem,
`realpathSync()` could preserve a caller's case. Spelling comparison therefore accepted
`results/MATRIX.JSON` and a case-aliased generation destination even though each named the
same authoritative inode. The reviewer reproduced a successful `diff --matrix` write in a
disposable copy. Both reader adapters also misclassified a case-aliased frozen pathname as
scratch, returning 1,107 rows instead of the 1,893-row union. The original verification
counts above are retained as the results of that implementation, not rewritten as evidence
that this alias boundary was already protected.

The correction resolves actual filesystem casing with `realpathSync.native()` on the longest
existing prefix, then compares device/inode for existing frozen, generation, index and archive
files. This protects hardlinks as well as casing and symlinks, and still refuses future JSON
files under a case-aliased authoritative directory. The TypeScript reader shares the same
file-identity predicate; Python uses `os.path.samefile`. Missing generation/archive directories
are allowed during module initialization, preserving monolithic and scratch-only layouts.

Regressions exercise upper-cased matrix, generation, index and superseded destinations,
future targets and hardlinks in disposable copied-source repositories. Every real canonical
JSON file's SHA is checked unchanged. Both adapters prove that frozen aliases return the full
union; an old-layout source mirror catches premature dependence on generation directories.
`review-identity.txt` establishes that the four case-alias branches actually execute on this
filesystem rather than silently taking the case-sensitive-platform fallback.

Review verification logs are separate: `review-build.txt`, `review-lint.txt`, `review-test.txt`,
`review-adapter-test.txt`, `review-freeze.txt`, `review-demo-test.txt`, and
`review-demo-build.txt`. No original result, row, digest, freeze pin or archive was rewritten.

Correction verification passes: calibration build and lint/typechecks; **57 calibration files,
740 tests passed / one existing X1 skip**; Python adapter parity and original legacy-envelope
SHA; unchanged freeze **1,818 intact**; demo **six files / 47 passed** and production build.
No canonical JSON changed relative to the reviewed commit. These are the correction's results,
not replacements for the original totals above.

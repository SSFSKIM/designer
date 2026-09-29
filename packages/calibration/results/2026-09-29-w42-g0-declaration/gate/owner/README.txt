W42 G0 gate — the owner test on a candidate's scratch union, against its base (charter clause 10)
===================================================================================================

Clause 10 reads "the owner test (adopted-thresholds.test.ts) on the candidate's scratch union over
all six gated macOS 27 profiles" at the bar "no failure that the base's own scratch union at the
same membership does not show". The test gates only rows whose documents are the files in
profiles/ and reads committed cuts, and clause 12 forbids moving its bytes for this. run-owner.py
runs it UNMODIFIED, once on the base's stages and once on the candidate's, each as the seal would
see it, and compares the two. Nothing here writes the repository: all scratch, both runs and the
disposable worktree live under --out, outside it.

Files
-----
  run-owner.py      the runner (python3.12; its internal _union / _cut modes run inside the
                    disposable worktree so that referee_source resolves every path there).
  proof-inputs.py   builds the proof's stages, identity documents, seeds and capture root.
  proof.txt         the proof: what was run, what each run read and showed.

What one invocation does
------------------------
 1. A detached worktree at --commit (default this branch's HEAD) under --out/worktree,
    `pnpm install --frozen-lockfile`; removed at the end unless --keep. Every file a run writes
    into it is restored from the commit before the next run, and `git status` must read as it
    did after the install.
 2. Per run (base, then candidate): each --candidate / --base-candidate document is installed as
    profiles/<basename>, the file it replaces at the seal. A basename that no current row names
    is refused, as is a candidate no stage declares or a declared scratch document with no
    --candidate. Each stage is copied with every document clause naming a candidate's scratch
    path relocated to profiles/<basename>, hash unchanged; the copy must differ from the stage
    in those clauses and nothing else.
 3. The scratch union, composed from W41 G2's own referee_source._stage per stage (its document,
    membership and completeness checks: every declared non-holdout cell of a held pair present),
    one stage per scheme with no overlap. W41's port takes ONE stage; two schemes need two, so
    the union is composed here and the port's cut scripts read it with referee_source.load
    replaced (below), everything after the rows being the port's own.
    Kept rows: a current row whose (profile, tier) no stage replaces — the whole CSS tier, and
    any WebGPU pair not rendered — was drawn at the document a candidate now overwrites. It is
    relocated to a side copy of that document's committed bytes,
    profiles/<stem>.kept-<sha12>.json, so it stays gated at what drew it and reads identically
    in both runs. Without this every kept row drops out of the candidate run alone and the bar
    cannot be met by any candidate that moves an ACTIVE document (proof.txt, ablation).
    Holdout carry (default; --no-carry-holdout for W41's rule exactly): a held pair's holdout
    cell that the stage holds no row for is carried at its current row, relocated the same way.
    A G2 stage renders no holdout before the exposure, and the table cases assert their cell
    count before any per-cell bound, so under W41's rule six cases fail in both runs and read
    nothing for the candidate: the four standard texture tables, the profile counts and the
    conditioning predicate (proof.txt, g2-texture-no-carry). A broken table bound still
    surfaces there, through the MISSED_27_ROWS owner case, which derives every macOS 27 miss
    independently of the counts; what the six hide is the rest of their assertions (the
    shape-axis presence per cell, the applicable-cell counts, a predicate list whose membership
    changes at an unchanged length). The cuts drop holdout themselves, so the carry changes only
    what the owner test's tables and counts read.
    The union is one schema-5 legacy envelope; its SHA-256 is the L1 cut's matrixSha256.
 4. A capture tree for X1 (VITREA_WEB_CAPTURES and black-cut.py's --captures): for every macOS 27
    WebGPU union row in a calibration, validation or probe role, the stage's capture (from the
    --captures root whose cell__webgpu.json names the row's pre-relocation capturePath) or the
    canonical tree's, with cell__webgpu.json re-named as the row was. Copied, not linked:
    w35_readers.confined() resolves a link and refuses a payload outside its root. A staged cell
    in X1's domain with no capture refuses. Holdout and recorded captures are never opened.
 5. The cuts the test reads, regenerated in the worktree by the port (default
    results/2026-09-29-w41-g2-landing/referees, --referees to change): chroma-cut.json and
    exterior-cut.json written over the two fixed paths the test at the commit names (found by
    parsing it, refused unless exactly one each), l1-cut.json and black-cut.json passed through
    VITREA_L1_CUT / VITREA_X1_CUT. M2's reference is the generation current at the commit, per
    scheme, from generations/index.json (W32 Decision Log 4). black-cut.py asserts X1 after it
    writes its cut; its exit is recorded and the test reads the failure.
 6. M2 named misses as the seal would record them (Decision Log 5a; on by default,
    --no-m2-named-misses to disable). Every M2 miss on the regenerated cut is classed as the
    test's structureVerdict classes it and reported (summary.json m2Misses); a NAMED miss is
    inserted into the worktree's copy of MISSED_27_ROWS as
      "<tier> / <set> / <scene> / <profile> :: interiorStdDevStructureDelta":
          { measured: <|Δ|>, bound: "≤ 0.02", native: <interiorStdDevNative> },
    each line logged in <run>/m2-insertions.txt. Only when the test at the commit carries the
    derivation (MissedRow.native and chromaStructureNamedMisses, landed at 0ce4294e); the
    owner case then checks every insertion against its own derivation, and a FAILURE-class miss
    is never inserted.
 7. `pnpm exec vitest run test/adopted-thresholds.test.ts --reporter=json` with
    VITREA_MATRIX_PATH, VITREA_WEB_CAPTURES, VITREA_L1_CUT and VITREA_X1_CUT set.
 7a. Closures (default on; --no-closures for evidence), the parent's ruling of 2026-09-30: a
    CLOSING named miss is a pass and its list shrinks at the seal. Before the test's two
    named-miss assertions (MISSED_27_ROWS, L1's MISSES) the worktree copy logs the derived and
    recorded lists (one added line each, no assertion changed); every recorded entry no longer
    derived is a closure, dropped from the copy as the seal would drop it, and the test runs
    again: that run is the run's result. Closures are reported (summary.json closures) and never
    block; a closure never excuses a new miss (proof.txt, "Closures").
 8. The comparison, case by case, on each failure's message with stack frames and the worktree
    path removed (inserted lines move line numbers): new (fails in the candidate only), changed
    (fails in both, differently), unmeasuredInCandidate (skipped where the base passed), and,
    non-blocking, fixed and shared. The base and candidate unions must hold the same replaced
    pairs, staged members and kept rows, or the run refuses. Exit 0 only when new, changed and
    unmeasuredInCandidate are all empty; 1 otherwise; 2 on a refusal.

Outputs (--out): summary.json (the verdict), manifest.json (the commit, runner and referee
hashes, the test's committed SHA-256 and fixed cut paths, M2's references, the shipped documents,
and per run: stages, relocated stages, candidate documents with full SHA-256, union SHA-256 and
membership, side copies used, capture-tree counts and listing hash, each cut's SHA-256 and exit,
the test's SHA-256 as run, the M2 lines inserted, vitest's JSON SHA-256), and per run union.json,
union-report.json, stages/, captures/ + captures-listing.txt, cuts/ (JSON, stdout, stderr),
m2-insertions.txt, vitest.json (raw) and vitest.log.

Run command
-----------
  cd packages/calibration/results/2026-09-29-w42-g0-declaration/gate/owner
  python3.12 -B run-owner.py \
    --stage LIGHT_STAGE --stage DARK_STAGE \
    --candidate CAND/apple-macos-27.0-1x-light-standard-glass0.5.json ... (one per document) \
    --captures CANDIDATE_CAPTURE_ROOT \
    --base-stage BASE_LIGHT --base-stage BASE_DARK --base-captures BASE_CAPTURE_ROOT \
    --out /tmp/w42-gate-owner/<name>
A base at the shipped documents needs no --base-candidate. Clause 10 wants the candidate stages to
hold the WebGPU pair of all six gated profiles; summary.json keptWebgpuPairsOfGatedProfiles names
any it does not (those pairs are then read at their current rows in both runs).

What it cannot see
------------------
- A case failing in both runs with the same message is shared, and vitest stops a case at its
  first failed assertion, so anything later in that case is unread in both runs. Read
  summary.json shared: every entry there is a case that gated nothing for the candidate.
- Kept and carried rows say nothing about the candidate: the CSS tier, any unrendered pair and
  the holdout cells are gated at the rows and documents that drew them, identically in both
  runs. The side copies appear in SHIPPED_DOCUMENT_HASHES and in the chroma cut's
  shippedDocuments record.
- The capture tree is matched by capturePath, not by pixel hash: a stage capture that names the
  row's capturePath is read as the candidate's.
- B1 reads the installed documents' σ leaves against W30's committed native snapshot
  (results/2026-09-20-w30-g0-cut/shadow-cut.json), which no port regenerates; it holds only
  native σ, so that is the seal's reading too.
- E2, the two directional stops, the eye sheets and the CSS tier are other clause-10 referees.

Where this departs from the brief it was built to, and why
----------------------------------------------------------
- Kept-row relocation and holdout carry are additions. Without the first the bar cannot be met
  by any candidate that moves an active document (ablation-no-kept-relocation: 11 new failures
  on an identity candidate); without the second a G2-shaped stage leaves six cases failing in
  both runs and reading nothing for the candidate (g2-texture-no-carry). Both switches remain,
  for evidence.
- Captures are copied, not symlinked (w35_readers.confined, above).
- The port runs from results/2026-09-29-w41-g2-landing/referees, by design. The owner test
  refuses a cut whose atDocuments is not "shipped", so the cuts it reads must be the verbatim
  port's over relocated rows, not the candidate-admission mode's (which stamps "candidate").
  --referees names another directory only if it keeps W41's referee_source API
  (_stage(stage, partial), Source(rows, label, stage), load). Separately, the verbatim copy as
  committed under ../referees/ at 5b3712f7 cannot import: its scripts take the package root as
  HERE.parents[2], one level short at gate/referees/.
- W41's --stage takes one stage; one per scheme needs two, so the union is composed here from
  the port's own _stage per stage and the cut scripts read it through a replaced
  referee_source.load, rather than through --stage itself.

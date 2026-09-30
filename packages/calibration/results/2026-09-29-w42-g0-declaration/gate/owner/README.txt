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
  run-closure.sh, run-fixgate.sh  the batches behind proof.txt's closure and fix-wave sections.

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
 6. Named misses added as the seal would add them, and ONLY through the two ruled paths.
    M2's (Decision Log 5a; on by default, --no-m2-named-misses to disable): every M2 miss on
    the regenerated cut is classed as the test's structureVerdict classes it and reported
    (summary.json m2Misses); a NAMED miss is inserted into the worktree's copy of MISSED_27_ROWS as
      "<tier> / <set> / <scene> / <profile> :: interiorStdDevStructureDelta":
          { measured: <|Δ|>, bound: "≤ 0.02", native: <interiorStdDevNative> },
    each line logged in <run>/m2-insertions.txt. Only when the test at the commit carries the
    derivation (MissedRow.native and chromaStructureNamedMisses, landed at 0ce4294e); the
    owner case then checks every insertion against its own derivation, and a FAILURE-class miss
    is never inserted.
    L1 growth's (Decision Log 5d; the fix wave's item A1; --no-l1-growth-named-misses to
    disable): a growth miss (> 0.005) on the regenerated L1 cut at one of the ruling's four
    cell-profiles (light photo__rrect-md__inactive-tint-orange and dark
    photo__capsule-button__inactive-tint-orange, 1x and 2x) is inserted into GROWTH_MISSES as
      "<profile>/<scene>": { measured: <growth>, bound: "≤ 0.005" },
    logged in <run>/l1-growth-insertions.txt (summary.json l1GrowthNamedMisses). Only when the
    test at the commit carries the path (GROWTH_RULED, growthVerdict, GROWTH_MISSES); its owner
    case checks every insertion, and a growth miss on any other cell is never inserted, so it
    fails the growth case as a new failure.
 7. `pnpm exec vitest run test/adopted-thresholds.test.ts --reporter=json` with
    VITREA_MATRIX_PATH, VITREA_WEB_CAPTURES, VITREA_L1_CUT and VITREA_X1_CUT set.
 7a. The seal's recording edits (default on; --no-closures for evidence): the parent's closing-
    miss ruling of 2026-09-30, extended by the gate review of b151aff4, finding 2. The test
    compares three named-miss lists with the lists it derives in both directions
    (MISSED_27_ROWS, L1's MISSES, L1's GROWTH_MISSES) and pins each entry's reading to five
    decimals, so a candidate that closes a named miss, or moves one that still misses, fails the
    owner case as a new miss would, and vitest stops the case there. Before each of the three
    assertions the worktree copy logs the derived list, the recorded list, each derived entry's
    pinned readings (a table row's reading, an M1 miss's R, an M2 miss's |Δ| and Apple's
    reading, an L1 growth miss's growth) and the recorded entries: one added line each, no
    assertion changed. Then, as the seal would:
      - every recorded entry no longer derived is a CLOSURE and is dropped (a MISSED_27_ROWS or
        GROWTH_MISSES line deleted; a MISSES member filtered where it is asserted and logged);
      - every recorded entry still derived whose reading no longer pins (|Δ| >= 5e-6) is
        RE-RECORDED at its new reading, in its own line; a field the entry does not carry is
        never added;
      - nothing is added: an entry derived and not recorded still fails, unless one of step 6's
        two paths inserted it.
    The test runs again, and that run is the run's result; it must show no closure and no
    unpinned reading, or the runner stops. Every edit, step 6's insertions included, is logged
    in <run>/edits.txt. Closures (summary.json closures, one list per run) and re-records
    (summary.json reRecorded) never block (proof.txt, "Closures" and "The fix wave").
 8. The comparison, case by case, on each failure's message with stack frames and the worktree
    path removed (inserted lines move line numbers): new (fails in the candidate only), changed
    (fails in both, differently), unmeasuredInCandidate (skipped where the base passed), and,
    non-blocking, fixed and shared. The base and candidate unions must hold the same replaced
    pairs, staged members and kept rows, or the run refuses. Exit 0 only when new, changed and
    unmeasuredInCandidate are all empty; 1 otherwise; 2 on a refusal.
    Two refusals added by the fix wave (the gate review of b151aff4):
      - finding 1: before either run, a run whose candidate documents replace a document that one
        of the six gated profiles' WebGPU pairs was drawn at, and whose stages do not render that
        pair, refuses. Unstaged, those rows are read at a side copy of the old document in both
        runs and gate nothing for the candidate. (keptWebgpuPairsOfGatedProfiles no longer counts
        carried holdout rows as kept, which made it name every staged pair.)
      - finding 8: after both runs, a base that fails any case refuses, with summary.json written
        (refused, the verdict for evidence). A case failing in both runs is compared on vitest's
        message, which truncates arrays ("[ …(30) ] to deeply equal [ …(31) ]"), so two different
        failures could read as one shared failure that blocks nothing.

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
hold the WebGPU pair of all six gated profiles: a light candidate's light stage holds 1x and 2x
standard, reduced transparency and increased contrast. A pair drawn at a replaced document and
not staged refuses (step 8); summary.json keptWebgpuPairsOfGatedProfiles names the gated pairs
kept at documents the run does not replace (a dark-only candidate keeps the light ones).

What it cannot see
------------------
- vitest stops a case at its first failed assertion, so anything later in a failing case is
  unread. A base that fails any case now refuses (step 8), so no case is "shared" in a passing
  verdict. Evidence runs whose base fails (--no-carry-holdout on a G2-shaped stage, a seeded
  base) exit 2 with their verdict written.
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

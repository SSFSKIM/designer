W41 G1 step 10 — offline standing-sheet adapter PREPARATION ONLY

No real sheet rendered yet. No native payload, canonical PNG, candidate PNG,
browser, capture, exposure receipt or matrix writer was opened by preparation.
G0/sheets/sheets.ts and export-png.py remain unchanged and own the existing
Native | Shipped | Candidate panels and OKLab ΔE × 8 encoding. Missing candidate
panels retain their explicit EMPTY label; no shipped bytes become a candidate.

preparation-inventory.json was made from the read-only current matrix union,
W39 public launch-plan metadata and G1 baseline/preparation.json. It contains
330 canonical calibration/validation cells and 544 W39 declared memberships:
536 admitted plus eight explicit UNMEASURED entries. No holdout belongs to this
adapter. It does not inventory or reread the whole canonical capture tree.

From packages/calibration:
  pnpm exec tsx results/2026-09-27-w41-g1-identification/sheets/adapter.ts inventory
  python3.12 results/2026-09-27-w41-g1-identification/sheets/test_native.py
  pnpm exec tsx --test results/2026-09-27-w41-g1-identification/sheets/adapter.test.ts

Only after the G1 owner signals committed freeze hashes and candidate availability:
  pnpm exec tsx results/2026-09-27-w41-g1-identification/sheets/adapter.ts render /tmp/sheet-options.json

Options JSON fields:
  baselineFreeze: {path: absolute committed frozen-baseline.json, sha256: full hash}
  baselineRoot: absolute completed baseline capture tree
  archiveRoot: the guarded release-archive root (not producer raw or probe PNGs)
  repeat: explicit integer 0..6, choosing that ordinal of lexically sorted normal runs
  outputRoot: a NEW run directory under /Users/new/vitrea-w41/g1-captures/sheets/
  canonicalRoot: /Users/new/Developer/GitHub/designer/packages/calibration/web-captures
Optional candidate and independently optional canonicalCandidate each contain:
  captureRoot: separate completed web capture root
  documents: {profileKey: [{kind: materialProfile or recededProfile,
                           path: checkout-relative document path, sha256: twelve hex}, ...]}
  freeze: {path: absolute committed freeze JSON, sha256: full hash}
A freeze contains captures keyed profile/scene, with png (absolute path),
pngSha256, cellSha256 and reportSha256 (full SHA-256 strings), matching baseline's
schema. A candidate must have actual frozen captures for the cells requested;
no candidatecanonical tree exists at preparation, so OMIT canonicalCandidate.
No capture command is provided or invoked. Document paths must be inside this
checkout and renderCell checks their actual bytes, complete pairs and pose.

The native bridge constructs the W39 Reader with calibration/validation roles,
checks its inventory generation against preparation, then opens crop bytes ONLY
through Reader.read. It requires seven distinct admitted normal repeats. A native
panel is exactly the selected run's rgb frame, losslessly PNG-encoded, never a
median image. Every record retains selected run/state, the complete all-runs
protocol/admission/attestation/source mapping, crop hash, inventory hash, selected
payload metadata and resulting PNG hash. The repeat ordinal is recorded too.
The six other repeats are provenance, not silently collapsed into a synthetic
native image. Unadmitted cells never invoke the bridge.

Each admitted sheet is HTML plus the existing Pillow PNG export, without a
browser. Scratch inventory binds input and output hashes. Actual representative
exports and their selected inventory entries will be copied into a new examples
subdirectory only after the authorized run; none are claimed now. Do not overwrite
preparation-inventory.json with a rendered inventory. Native holdout remains closed.

Tests use only synthetic pixels and a temporary synthetic Reader archive. They
cover real-repeat selection, seven-run/normal admission, native role and digest
refusals, full selected/all-run provenance, unadmitted no-read, canonical role
forgery, stale document refusal before native access and honest absent candidates.
The unchanged G0 sheet tests separately pin existing panel/diff/export behavior.

Baseline provenance names its own frozen capture/source epoch. Integration of a
zero-gated operator into the current checkout does not recast that epoch: this
adapter checks frozen web PNG/descriptor hashes and material documents, not an
assertion that the current renderer source is still the baseline renderer.

Focused review found that the first exported renderAdmitted wrapper trusted W39
caller role/admission fields, although the normal batch plan and native Reader
were independently guarded. A separate fix wave removed the caller admission
argument and derives W39 profile/scene membership and role from cached w39Plan,
with admission from baseline preparation. The forged-W39-holdout regression was
observed failing before that fix and now rejects before any callback. A wrong
profile is also rejected; a declared but excluded member stays UNMEASURED.
adapter-review-fixed.txt records 13/13 TypeScript checks including unchanged G0;
native-review-fixed.txt records 3/3 Python checks, typecheck-review-fixed.txt the
strict TypeScript pass, and freeze-review-fixed.txt the intact 1,818-entry freeze.
All 177 tracked G0 files were compared byte-for-byte with HEAD and are unchanged.
The initial red logs record absent modules, not a behavioral regression witness;
the forged-role red/green check is the behavioral review-closure witness.
Independent narrow closure review confirmed the fix with no material findings,
rerunning the two adapter and three Python synthetic tests without real pixels.

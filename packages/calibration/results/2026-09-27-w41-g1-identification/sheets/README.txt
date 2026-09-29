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

Additional step10 authorization is prepared separately in ../canonical-diagnostic/:
330cal/val WebGPU diagnostic candidate captures, direct capture only, scratch,
no matrix/native read, each launch X6-checked after the owner's browser handoff.
No such capture is claimed yet. Its committed frozen.json is the optional
canonicalCandidate input here. This adapter requires its diagnostic label and
carries that label into the HTML/PNG title and candidate inventory metadata:
"diagnostic candidate WEB for EYE; not a canonical read or G2 material".
The canonical holdout remains excluded. G0 styles/difference encoding stay intact.

W39 candidate metadata conversion (after the original candidate freeze is committed):
  python3.12 results/2026-09-27-w41-g1-identification/sheets/manifest.py attempt-1 \
    results/2026-09-27-w41-g1-identification/sheets/candidate-calval-freeze.json
Run from packages/calibration. The converter reads only committed JSON and candidate
material documents, never any PNG. It binds the original frozen-envelope, raw
inventory and seal hashes, selects precisely baseline preparation's536calval cells,
retains each primaryCapture under attempt/calval/profile/scene, verifies every
selected payload hash belongs to the frozen envelope and keeps actual candidate
scratch document paths. Blind entries are not converted or dereferenced. Commit
the new derived manifest before passing its full hash to adapter.ts. This does
not modify the candidate capture driver, its frozen files or any candidate pixels.
Focused converter review confirmed schema compatibility and no pixel opens. Its
small scope-binding/test gaps were closed by a separate fix wave: preparation's
committed hash must equal the original candidate seal's input pin. A temporary
Git repository tests the complete536-cell derivation, changed scope/documents,
broken frozen/raw/seal links, count/uniqueness, selected blind-phase refusal and
confined no-overwrite output. The new scope regression failed before the fix;
manifest-review-fixed.txt records9/9passing, freeze-manifest.txt1818intact.
No conversion of the actual candidate attempt has run yet.

First actual offline run: transport stall, outputs preserved
After canonical freeze65bd9fbe, the original adapter rendered125canonical HTML
files and124PNGexports in approximately30seconds, then stalled on the125th PNG.
The bounded health snapshot at11:48:15Z found no progress for36m39s, both the Node
parent and Python exporter at0%CPU, and no native.py process: W39 reading had not
begun. Python's stack was blocked in stdin readall; Node's was blocked in
SyncProcessRunner/uv_run/kevent. This establishes a synchronous-pipe EOF wait,
not expensive archive reading or Pillow image computation; the underlying
Node/libuv failure was not separately isolated. Stack, descriptor and health
records are retained. partial-output-preservation.json binds all249files.

The owner authorized a bounded additive recovery (recovery-ruling.json). Only our
own background task was stopped, via TaskStop; no known process remained, and all
249file hashes still matched (stalled-job-stop.json). No finished image was
regenerated, native input reopened or pinned source edited during diagnosis.
Recovery must bind new reviewed/committed runner bytes to the original inputs,
freezes, selection and preservation witness. It will use regular-file exporter
stdin/stdout, preserve124PNGs/125HTML, export thepending125PNG and render only
remaining741admittedcells. The125completed native records will be explicitly
recovered from saved HTML and the committed G0fixture inventory, not claimed as
new native reads. All536W39 native reads still go through the unchanged guard.

Recovery preparation and review closure
The additive recovery runner now uses file descriptors, bounded120-second child
timeouts and immutable per-cell checkpoints before export.14synthetic tests and
strict TypeScript pass. Independent review caught unbound recovered shipped-file
provenance: a same-document recapture could differ from the saved HTML. The fix
compares every embedded Shipped panel RGBA byte with the claimed current capture,
and explicitly distinguishes display/current hashes from the unknown original
encoded-file hash. Narrow independent re-review closed the finding.
Metadata-only preparation then safely refused a stale authority.json pathname;
the new wrapper now binds the actual frozen authority-v2.json, not a fallback.
Its digest and linkage were independently confirmed against committed metadata.
The failed preparation log remains. No pinned original source or seal moved.

recovery-declaration.json SHA2565abe634b794d41b95455cacdb58fcdbff302acbf0d3493a8e3dd1a2d9ca65d5c
binds44source/input pins, the125/124preserved prefix and full866+8scope. It pins the
committed1818-entry frozen hash witness and cross-checks all125original native
fixture hashes against G0metadata without reopening those native fixtures.
Actual continuation still requires this declaration and every pin to be committed,
then the unchanged canonical driver verifier and recovery verifier to pass.

Completed standing sheets — recovered without changing scientific scope
Recovery b5054fca passed both the unchanged original seal verifier and the new
recovery guard, then completed with exit0. Final874memberships:866RENDERED
(330canonicalcal/val,536W39cal/val) and8explicitUNMEASURED. All866have actual
Native/Shipped/Candidate columns,866HTML and866PNG files; every output hash was
verified. The original125HTML/124PNG remain byte-identical (all249witnesses pass).
Only one pending PNG plus741newHTML/PNG were produced.125native provenance records
are explicitly recovered/notnewreads; the remaining741native reads comprise205
canonicalcal/val fixtures and536guardedW39cells. Every W39 row preserves actual
normalrepeat ordinal0 of7 and the complete run protocol/state/hash provenance.
No native holdout, probe, browser or matrix operation occurred in the sheet run.

The primary complete inventory is retained at:
/Users/new/vitrea-w41/g1-captures/sheets/run-1/inventory-recovered.json
SHA256 f52dbcb03a9b164fbafb916a400c14e79c8d8405d1ae4a6b83a487e62064f44e
83,939,696bytes. render-inventory.json.gz is its exact lossless3,068,451-byte archive,
SHA25694be7f7023736712219e4d0c6a5fa3c789ee72c43f5a5c97056d9c0452b8aa02;
decompression was checked against the primary byte hash, not re-serialized JSON.
completion-audit.json records counts, preservation and source distinctions.
verify-completed-recovery.txt records the final original/recovery guard pass;
my source-pin hold was released only after these source-bound reads/checks ended.
The runtime may move subsequently; none of these historical seals is repointed.

examples/ carries all9predeclared PNGs and their standalone HTML companions,
byte-identical to primaryscratch; selection.json binds paths and full hashes.
All9were opened directly after export, with no browser or native reread. Layout,
labels, aligned panels and the numerical grayscale legend remain intact. Canonical
titles explicitly say diagnostic candidate WEB for EYE, not a canonical read/G2.

Visual gaps, not a new numerical verdict (visual-inspection.json)
The selected light-inactive uniform body improves visibly in the interior; its
bright difference outline persists because native's dark contour is still absent
from the web rendering. The light-active identity case retains interior/edge
residuals. Dark uniform native material carries more olive hue than the greyer
web body in both poses; the contour/boundary treatment remains different. The
selected gradient's broad residual bands darken with the candidate, but its outline
remains and this one view does not pass the all-cell structured veto. Both photo
scales retain structured interior and perimeter differences: the1x candidate
reduces the prominent bright right-side residual, yet mottling remains, and the2x
residual is redistributed rather than eliminated. The dark and frozen26.5identity
controls retain native body/edge or chroma differences. These9examples do not
replace866-cell coverage or claim that every sheet was visually inspected; no
fit, threshold, material adoption, survival or G2 acceptance is inferred from them.

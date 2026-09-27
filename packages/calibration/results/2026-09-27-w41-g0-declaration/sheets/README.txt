W41 standing eye sheets — clause 9, claims §5.191

G0 ships a metadata-only inventory command, an HTML sheet renderer, and a strictly
canonical calibration/validation reread command. The original inventory-only
assignment was amended by the G0 owner after the coordinator clarified that these
committed, already-read cal/val fixtures may be rendered without a new capture.
The first inventory witnesses remain unchanged. Every canonical HOLDOUT pixel,
every W39 pixel, and all browser/native-capture runs remain closed in this gate.
Candidate panels stay EMPTY until a caller supplies G2 document clauses and a
separate candidate capture root. Synthetic tests cover the instrument first;
the later render inventory and representative sheets witness the permitted reread.

From packages/calibration:
  pnpm exec tsx results/2026-09-27-w41-g0-declaration/sheets/sheets.ts inventory \
    --capture-root /Users/new/Developer/GitHub/designer/packages/calibration/web-captures
  pnpm exec tsx --test results/2026-09-27-w41-g0-declaration/sheets/*.test.ts
  pnpm exec tsx results/2026-09-27-w41-g0-declaration/sheets/render-calval.ts \
    --capture-root /Users/new/Developer/GitHub/designer/packages/calibration/web-captures \
    --output-root /tmp/a-new-w41-sheet-directory

The command emits JSON to stdout; redirect only to scratch or new gate evidence.
Do not point it at a matrix/generation output. It has no matrix-path CLI option.
It refuses VITREA_MATRIX_PATH rather than silently enumerating a scratch matrix.
--repository-root selects the checkout whose actual material document bytes are
verified (default: this script's checkout). It does not change the union source:
loadCurrentRows() reads the script checkout's current union through matrix-store.
--capture-root selects canonical WebGPU captures; the default is this checkout's
web-captures tree, which is absent in the G0 worktree. --w39-capture-root selects a
separate later W39 WebGPU capture tree; default is explicitly absent. No environment
variable silently substitutes a different capture tree.

Enumeration and meanings

All 1,893 current matrix rows (frozen macOS 26.5 plus selected macOS 27 generations)
become 1,003 unique profile × scene sheets. Tier duplicates collapse because each
sheet asks for Shipped WebGPU, not CSS. CSS-only matrix cells remain enumerated.
W39 membership comes from default_wave().launch_plan(calibration,validation), not
a native payload or the old web-plan snapshot. Its 138 unique scene IDs yield 544
profile × scene cells after the declared scale membership is respected, not 552.
The planner constructor reads only pinned scenes/split/preflight metadata. No
Reader is constructed; no native archive or bundle path is supplied.

inventory-main-tree.json records 1,003 canonical MATCH, 0 canonical UNMEASURED;
W39 has 0 MATCH, 544 UNMEASURED. inventory-worktree.json records the genuinely
absent local tree: 0 MATCH, 1,003 canonical UNMEASURED and 544 W39 UNMEASURED.
MATCH means WebGPU PNG presence plus matching active/receded document provenance,
NOT a decoded PNG, a pixel-byte hash, or evidence of an unchanged capture session.
Inventory never opens a PNG, including canonical holdout PNGs. Native presence and
native pixels are not assessed by inventory. There is no candidate in either run.

Every present cell__webgpu.json must name the requested scene, WebGPU and sRGB,
its matrix row's scale, colour scheme and accessibility pose, exactly the current
cell's active/receded document pair, and the actual twelve-hex
SHA-256 hashes of those documents in the selected checkout. Missing or extra
receded clauses, stale documents and malformed clauses refuse the operation.
Absent metadata or PNG is UNMEASURED; present stale metadata still refuses even
when its PNG is absent. These checks extend W31 G4's document-bytes check with
explicit pair completeness. They do not prove pixel identity or re-attest capture
hardware; that is the capture instrument's job.

Renderer API for the authorized later gate

  enumerateCells(rows, plannedCells) -> all sheet Cell objects
  inspectCell(cell, repositoryRoot, captureRoot) -> MATCH | UNMEASURED or throws
  renderCell(cell, {
    repositoryRoot, captureRoot,
    readNative: async (cell) => authorizedNativePNGBytesOrUndefined,
    candidate?: { documents: [{kind, path, sha256}, ...], captureRoot }
  }) -> Promise<string> (standalone HTML)

A later exposure runner calls renderCell for each enumerated cell, using its
role-guarded/receipt-bound native reader and explicit repeat selection. The core
CLI stays inventory-only. The separate render-calval.ts command reads the split
from canonical scenes.json, admits only calibration/validation, and never opens
any W39/native-archive path. It writes new HTML files only (refusing overwrite),
plus an inventory with input PNG and output HTML hashes. Its fixture-root option
selects canonical committed fixtures, not a new experiment or archive. The general
callback owns native identity, role authorization, and repeat provenance; do not
substitute an unguarded filesystem reader. Shipped/candidate
metadata is checked before the callback is invoked. Candidate document paths must
resolve inside repositoryRoot, just like shipped documents. The G2 caller must
supply both endpoints when the capture names both. No document or declaration is
edited by this script.

The HTML gives Native | Shipped WebGPU | Candidate, with shipped/native and
candidate/native ΔE × 8 below their respective panels. Missing native or capture
bytes say UNMEASURED; a missing candidate declaration says EMPTY — awaiting G2
document. All images are embedded at original dimensions. Unequal dimensions
refuse rather than resample. The sequential achromatic diagnostic matches W31:
black = zero; white = OKLab Euclidean ΔE >= 0.125, clipped after multiplication by
8. This is not an RGB difference or a color-category chart. Headers and the
numeric scale explain it without hue; no categorical palette is used. G0 first tested
output structure, PNG encoding, equality, amplification, clipping and dimension
refusal synthetically. The authorized canonical cal/val reread then exercises
those paths on real already-read material, with representative PNGs inspected
directly rather than through a browser. W39 and candidate visual readings remain
later-gate work.

Test evidence

Tests were written first against explicit unimplemented operations: tests-red.txt
records 0/5 passing, and tests-green.txt records the first 5/5 passing. The focused
TypeScript command initially needed TS's --ignoreConfig switch (retained in
typecheck-initial.txt), then exposed PNG input typings (typecheck.txt). Those were
fixed without changing behavior; typecheck-final.txt records exit 0. Tests are
standalone node:test through tsx, not silently outside a claimed vitest run.

dataviz-check.txt separately records the skill's applicable numeric checks:
18.8831:1 text contrast and strictly monotonic lightness across all 256 output
grays. Its categorical hue validator does not apply to this achromatic sequential
field. The W31 orientation (black zero, white high/clipped) and scale labels are
retained rather than silently inverting the established diagnostic.


Review closure and canonical holdout rule

Independent review found that document hashes alone cannot reject a capture copied
between profiles sharing a material. The fix wave carries scale, colour scheme
and accessibility from the current rows, rejects missing or mismatching clauses,
and refuses ambiguous profile-pose inheritance for W39. pose-tests-red.txt records
four new failures before that fix; pose-tests-green.txt records all eight passing.
pose-typecheck.txt records the repository's strict typecheck flags passing.

renderCell does not trust caller-provided canonical role labels. If a candidate
is requested for a scene scenes.json puts in holdout, it refuses BEFORE any pixel
read unless the standing configuration-log.json records the exact four full
material-document hashes, renderer-source hash and source-list hash. The state is
recomputed by importing the existing configuration.py read functions; no copied
hash definition, log write, record CLI, or caller-supplied approval flag is used.
The supplied candidate document clauses must also belong to that recorded state.
Source-list-less historical entries do not authorize a new candidate. This is a
configuration check, not a capture-pixel/source attestation: capture provenance
still depends on the later gate's capture/receipt chain.

Shipped-only holdout is supported by the core rendering API for an appropriately
authorized later reader; G0's batch command excludes it regardless. The synthetic
holdout tests use only a temporary invented scene and synthetic PNGs: no actual
canonical holdout scene is rendered. holdout-tests-red.txt shows the pre-guard
failure; holdout-tests-green.txt shows 10/10. batch-tests-red.txt and
batch-tests-green.txt prove that G0's narrower cal/val runner never opens holdout,
probe or W39 pixels, even when those paths contain invalid-image sentinels.
expanded-typecheck.txt records the enlarged instrument's strict TypeScript pass.

Authorized canonical reread result

render-calval-run.txt and render-inventory.json record 330 rendered comparisons:
266 calibration and 64 validation. All selected native/shipped PNGs were present,
decoded successfully and had matching dimensions. The 92 canonical holdout cells
and 581 probe cells were SKIPPED before native-path access; all 544 W39 cells stay
UNMEASURED. No candidate exists. No browser or capture process was started.

The full 330 HTML files were written to /tmp/w41-canonical-calval-sheets. The
committed examples/ retains three, selected to exercise light photo at 1x, light
thin-photo validation at 2x, and dark solid at 1x. examples/selection.json maps
them to the render inventory's full input-PNG/output-HTML SHA-256s. Those hashes
record this reread's bytes; they do not retroactively prove that historical matrix
numbers were measured from these same captures. inventory-final.json is the
post-review, pose-aware metadata-only sweep: all 1,003 canonical captures MATCH;
544 W39 memberships remain UNMEASURED.

The independent review's second pass found no material issues: the wrong-profile
pose refusal is closed, canonical cal/val-only admission is authoritative, and
candidate holdout rendering is gated by the exact ledger configuration. That
review ran all 11 TypeScript synthetic tests without opening real pixels. It did
not inspect the optional PNG exporter, which is checked separately.


Optional PNG export

Add --png to render-calval.ts to write labeled PNGs beside the HTML, or export an
already-rendered HTML without reopening any fixture/capture file:
  python3.12 results/2026-09-27-w41-g0-declaration/sheets/export-png.py \
    < saved-sheet.html > saved-sheet.png

The exporter uses Python 3.12, the existing Pillow installation and macOS system
Helvetica/Arial fonts; it does not start a browser or load external image URLs.
Each embedded PNG stays at its original pixel dimensions and RGB bytes. The
footer retains the numeric ΔE scale. The PNG option is checked end-to-end in the
batch's synthetic test; all-tests-final.txt records 11/11 TypeScript tests passing
with it, and png-tests-green.txt records the initial 28 exporter tests passing.
The exporter's first red log failed because the not-yet-created module was absent;
the separate alignment regression below is a behavioral red/green witness.

Direct visual inspection initially caught a comparison-layout defect that the
first synthetic suite missed: per-label ink bounding boxes put Native and Shipped
images on different vertical origins (three pixels apart). This was not a native
or WebGPU pixel difference, and the computed ΔE fields were unaffected. It was
corrected by reserving a common label line-height from the font metrics. The original PNGs and
png-exports.json remain the initial witness rather than having their hashes
silently replaced; corrected exports are named separately.


Final direct visual check

The three __aligned.png files named in examples/png-exports-aligned.json were each
opened directly after the fix (no browser). Native and Shipped images now share
the same top origin, labels and titles are unclipped, native-scale pixels remain
unresampled, the ΔE × 8 field sits below Shipped, and both candidate slots plainly
say EMPTY. The numeric grayscale legend is readable. The initial unsuffixed PNGs
are retained only as the pre-alignment witness; use __aligned.png for the sheets.

Visible material gaps are not confused with that fixed layout bug. In the light
photo rrect-md sheet, the native contour and the shipped boundary differ, and the
ΔE field carries both a bright perimeter and structured interior differences.
The light 2x thin-photo sheet likewise retains a visible native dark contour that
is less distinct in the shipped panel, with perimeter residuals in the difference
field. The dark-solid capsule has a subtler native body gradient than the flatter
shipped body; its difference image emphasizes the outline and curved ends. These
are visual observations of existing cal/val evidence, not a new fitted law or a
numerical closure claim. They remain body/boundary work for the W41 referee chain;
no material, fixture, matrix, bound or document was changed by this instrument.

png-alignment-red.txt records the real-label synthetic origins [90,93,90] before
the fix; png-alignment-green.txt passes both the common-origin and pixel-preserving
regressions. png-tests-final.txt records all 30 exporter tests passing, and
aligned-tests-final.txt records all 11 integrated TypeScript tests passing after
the alignment change. The original red/green logs and PNG hashes remain intact.

The PNG-only reviewer independently reproduced the initial alignment defect,
then verified its closure in the shared-line-height implementation and reran all
30 synthetic exporter tests: final scoped verdict correct, no remaining material
finding. This closes the review; no material-fit or exposure work is implied.

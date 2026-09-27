W41 G1 stopped-sheet recovery — additive, offline, explicit continuation

The original adapter.ts, native.py, G0 sheets.ts/export-png.py and canonical driver
remain unchanged. This runner does not assemble or capture anything. It only
continues the original 866 admitted / eight UNMEASURED sheet job in run-1.

Preparation is metadata/source-only. It binds the exact render-options JSON,
representative ordinal/selection, preserved-output inventory, the full baseline,
W39 original+derived and canonical freeze/input seals, current sheet plan and
material documents, G0 fixture inventory and frozen 26.5 witness, pinned original
sources and all additive recovery*.ts / recovery*.txt files. The canonical seal
retains its full original input/source map. The baseline's historical source epoch
is retained inside its seal, not falsely compared to today's integration sources.

prepare deliberately does NOT open the 249 preserved files. Their existing
preservation inventory is the declared witness. verify checks their actual bytes,
and the committed declaration plus every source/input pin, before any continuation.
The unchanged canonical driver verify verb is mandatory inside verify AND run;
there is no skip flag. That verifier checks source and web-background bytes, not
completed-cell native fixtures. Do not run freeze.py verify as part of this recovery:
it would reread native fixtures that the recovery explicitly promises not to read.
The committed frozen hash inventory is instead cross-checked against G0's native
fixture hashes for all 125 preserved cells.

All 125 preserved HTML files remain byte-identical, as do the 124 completed PNGs.
The one HTML-only cell is exported without rendering or a native read. A recovered
record cites the Native panel's embedded PNG hash and the original native fixture
hash from committed G0 metadata separately: renderCell re-encodes PNGs, so those
hashes need not equal. It is explicitly recovered provenance, not a new native read.
Existing candidate and shipped provenance is checked with inspectCell, and the
candidate freeze's PNG/report/cell hashes; no candidate column is fabricated.
For preserved sheets, the embedded Shipped WebGPU panel must also match the current
shipped capture's dimensions and every decoded RGBA byte. Same-metadata recaptures
with different pixels refuse; different lossless encodings of identical pixels pass.
Recovered records carry shippedDisplay with separate display/current-capture hashes
and an explicitly unknown original capture-file hash, not shippedPngSha256 inferred
from today's file. No native fixture is reopened for this comparison.
Only the remaining 741 admitted cells call unchanged renderAdmitted/renderCell and,
for W39, unchanged native.py. Eight excluded memberships never call either.

Every cell saves HTML and a hash-companioned provenance checkpoint BEFORE export.
Exporter stdin/stdout and native.py stdout/stderr are regular files. Children have
120-second timeouts and SIGKILL termination. Failed exports preserve stdout, stderr,
and a hashed result; the same run command resumes with a fresh numbered attempt,
without rendering the HTML or reading native again. Unknown/changed files, missing
companions, or a different declaration/options binding are refused before work.
A crash before a complete checkpoint/result, or a failed native/render step, is
intentionally NOT silently retried: preserve that directory for explicit inspection.
A crash lock also refuses; inspect the process and evidence before any cleanup.
No evidence file is overwritten. Completed PNG installation is a no-clobber hard
link from the successful export. Final output is inventory-recovered.json plus its
hash companion, not a replacement for the original missing inventory.json.

Workflow (not authorization to execute a render)

1. Run synthetic tests and strict typecheck from any directory:

pnpm --dir /Users/new/vitrea-w41/g1/packages/calibration exec tsx --test results/2026-09-27-w41-g1-identification/sheets/recovery.test.ts
pnpm --dir /Users/new/vitrea-w41/g1/packages/calibration exec tsc --ignoreConfig --noEmit --target es2022 --module esnext --moduleResolution bundler --strict --skipLibCheck --esModuleInterop --types node results/2026-09-27-w41-g1-identification/sheets/recovery-core.ts results/2026-09-27-w41-g1-identification/sheets/recovery.ts results/2026-09-27-w41-g1-identification/sheets/recovery.test.ts

2. After source review, prepare the metadata-only declaration (fresh file required):

pnpm --dir /Users/new/vitrea-w41/g1/packages/calibration exec tsx results/2026-09-27-w41-g1-identification/sheets/recovery.ts prepare /Users/new/vitrea-w41/g1/packages/calibration/results/2026-09-27-w41-g1-identification/sheets/recovery-declaration.json

3. Review the declaration. Commit it, all recovery sources/tests/this text, the
   unchanged render-options.json and partial-output-preservation.json, and any
   still-uncommitted original inputs. verify refuses uncommitted or changed pins.
   Re-review/redeclare if the source bytes change; do not silently reseal a prior
   declaration. No continuation before this commit and the owner's authorization.

4. Verify without sheet rendering/native reads (it does hash preserved outputs):

pnpm --dir /Users/new/vitrea-w41/g1/packages/calibration exec tsx results/2026-09-27-w41-g1-identification/sheets/recovery.ts verify /Users/new/vitrea-w41/g1/packages/calibration/results/2026-09-27-w41-g1-identification/sheets/recovery-declaration.json

5. Only after the reviewed, committed recovery is cleared for continuation:

pnpm --dir /Users/new/vitrea-w41/g1/packages/calibration exec tsx results/2026-09-27-w41-g1-identification/sheets/recovery.ts run /Users/new/vitrea-w41/g1/packages/calibration/results/2026-09-27-w41-g1-identification/sheets/recovery-declaration.json

The same command resumes a checkpointed exporter failure. There is no automatic
retry loop. No holdout, probe, browser, matrix writer, capture command or source
amendment is part of this workflow. Representative copying remains a separate
owner action using the unchanged committed nine-cell selection.

Tests use temporary synthetic outputs and pixels only, including the actual pinned
G0 exporter with a synthetic >67,100-byte candidate sheet. Temporary Git repositories
exercise committed-byte refusal; they do not commit to the project repository.

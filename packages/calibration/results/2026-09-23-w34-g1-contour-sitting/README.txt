W34 G1 native contour sitting — operational evidence index
Governed by c9a §5.175, W34 clauses 3, 4 and 7, and Decision Log 1.

The native sitting is complete. Raw runs remain at /Users/new/vitrea-w34/run/.
The side bundle was not rebuilt or re-granted. The display returned to mode 68.
No browser, vitrea render, native model fit or holdout receipt ran in this gate.

Records
  sitting.json                   Final structured sitting record, bars, checks and hashes.
  sitting-capture-complete.json   Immutable capture checkpoint and eight pass wall clocks.
                                 G0 rehearsal intervals are explicitly distinguished from
                                 process wall clocks; no new G1 dry rehearsal was run.
  provenance.json                All 40 run paths, manifest hashes, capture times and
                                 attestation digests.
  attest/                        Opening/closing machine reads, per-run session reads,
                                 portable attestations and display readbacks.
  logs/*-driver.txt               Driver admission output, not raw capture diagnostics.
  logs/passes/                   Hashes, times, inventory and admission distilled per run.
  publication-check.json         Public-manifest membership and payload-hash checks.

Evidence and access boundary
  repeat/                        All admitted states BEFORE plurality, with full lossless
                                 RGB dependency closure. Its inventory names 40 manifests.
  probe/                         Materialized bed, partitioned by identification role.
  bar.json                       Normal seven-run calibration/validation bar.
  sentinel-bar.json              Long-protocol three-run calibration/validation bar.
  archive-only-replay.json        Instrument replay with raw-root access forbidden.
  archive-alignment-replay.json   Alignment fits independently recomputed from archived inputs.
  holdout/                       Producer-only precomputed held bars, never analytically
                                 exposed by G1. Bulk producer files are retained beside
                                 per-cell, receipt-compatible payloads under holdout/bars/.
  inventory.json                 Guarded inventory for those per-cell held bars.
  sealed-bars-inventory.json      Integrity inventory of the bulk sealed producer outputs.
  sealed-bars-boundary-check.json Unauthorised access to every per-cell bar was refused.

Raw capture output can carry held-out state diagnostics. It was not copied into public
logs. Full materializer diagnostics and metadata remain under probe/holdout/. Integrity
hashing and declared inventory are not analytical exposure. No wave receipt was spent.

Reproduction from the repository (no raw PNGs required)
  E=<checkout>/packages/calibration/results/2026-09-23-w34-g0-contour-bed
  G1=<checkout>/packages/calibration/results/2026-09-23-w34-g1-contour-sitting
  python3.12 "$E/report-bars.py" "$G1/repeat" --protocol normal > /tmp/w34-normal.json
  python3.12 "$E/report-bars.py" "$G1/repeat" --protocol long > /tmp/w34-long.json
  python3.12 "$E/replay-archive.py" "$G1/repeat" \
    --deny-raw-root /Users/new/vitrea-w34 > /tmp/w34-replay.json

Do not replace committed output with a later run; compare a fresh result or add it beside.
The archive and materializer commands are preserved under logs/*-command.json.

G2 exposure
  Use G0's guarded wave reader and launcher, not bare compare --set probe.
  Freeze repeat/inventory.json and probe/inventory.json in the once-only G2 receipt.
  If G2 will read G1's precomputed held bars, ALSO pass --inventory "$G1/inventory.json"
  before exposure. Read them as reader.read(cell, 'normal-bar') or 'long-bar' with the
  receipt-authorised holdout reader rooted at G1. Alternatively rederive the bars from
  the authorised repeat reader. Do not open the bulk sealed files as an access shortcut.

Original Screen Recording grant recovery remains the wave-close obligation under DL4,
not a G1 operation. The normal and long protocols are separate: their own quiet repeat
bars would not prove that the protocols produce identical pixels or universal settledness.

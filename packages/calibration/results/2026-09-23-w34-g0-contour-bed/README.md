# W34 contour-bed tooling

Operational entry points for the declaration governed by claims §5.174 and the W34 charter.
The readings are in the JSON artifacts and ledger; this file describes how to use the tools.
G1 does not open until the parent rules Decision Log 1 and the declaration is reviewed/merged.

## Identity and roots

Use the existing side binary at `~/vitrea-w34/side/VitreaReference.app`, not `capture.sh`.
`bundle-pin.json` names its binary hash, cdhash and Swift build-input revision. Any rebuild
requires a new grant and a fresh positive check. The later case-insensitive build-output guard
changes no compiler input, compiler flag, bundle identifier or binary byte.

The binary's compiled `#filePath` root is the G0 worktree. Removing the worktree removes that
fallback source/spec/fixture location, **not** the external binary or its TCC identity. Every
invocation must supply `VITREA_SCENES` and `VITREA_FIXTURES`; the sitting supplies both for
`backgrounds`, `capture` and the non-dry `rehearse-tints` branch. Its scripts resolve the
checkout containing themselves after merge, rather than retaining a G0 worktree path.

DL4 keeps the side grant for this wave. Restore the original protected bundle's grant only at
wave close, by the harness README's remove-and-re-add recipe, then positively check it. The
original denial is not evidence of a particular internal TCC key. GUI actions follow the
standing companion-first rule; the user's hand is the fallback. Never grant `build-probe`.

`read-session.swift` is a non-GUI HID/frontmost/lock reader. Compile it outside the repository,
for example to `~/vitrea-w34/scratch/read-session`, using the same explicit SDK/toolchain
pattern as the harness. It needs no Screen Recording grant and never activates an application.
`VITREA_SESSION_READER` can name that executable. An unreadable session is not “unlocked”.

## Declaration and selection

- `scenes-w34-contour.json`: native fixture roles are all `probe`.
- `split.json`: identification roles, independently pinned by `pins.json`.
- `semantic-twin-audit.json`: declaration-only comparison, including canonical holdout twins
  that differ in tint or pose. The dark-solid capsule bridge is identification-holdout-only.
- `pass-plan.json`: complete cell lists, seven-run prices, long-sentinel cost and exact trim.
- `closure.json`: forward algebra, body constraints, uncertainty, statistic and resolution rule.

The phase axis is absent by measurement, not because the JSON cannot express it. Do not add a
window-origin workaround or re-cut the split. `declare-bed.py` is the reproducible generator of
this declaration, not a tuning command to run after evidence is captured.

Use the wave launcher, **never bare `compare --set probe`**. A non-capturing plan is:

```bash
python3 "$E/wave.py" plan --roles calibration,validation \
  --fixtures "$G1/probe" --out-matrix "$G2/matrix.json" --captures "$G2/web-captures"
```

`E` is this directory in the accepted checkout. The command prints the explicit scene allowlist
and output seams; native-only controls are excluded. `--execute` belongs to G2, after that
child's browser preflight. The command refuses holdout selection without the receipt and
refuses canonical fixture/output locations. Circular cells map to vitrea's actual circular
stadium; existing continuous native capsules retain their older web counterpart unchanged.

## Sitting

The driver enforces macOS 27.0/26A428, RT0/IC0/slider0.5/Show Borders0, display identity/mode,
pinned side identity and opening/closing agreement. G1 also requires zero foreign capture
processes; the user's G0 exception does not silently authorise G1. Dry runs report that refusal
but may present because they capture no pixels. Every real launch requires at least sixty
seconds HID idle, also checked by the harness. Do not retry noisy runs until they look quiet.

```bash
# Mode 68 (2x), then mode 69 (1x), through the attested displayplacer seam.
DRY=1 bash "$E/run-sitting-w34.sh" active 2
bash "$E/run-sitting-w34.sh" active 2
bash "$E/run-sitting-w34.sh" inactive 2
# Switch and read back mode 69 before the 1x passes; restore/read 68 afterwards.
bash "$E/run-sitting-w34.sh" active 1
bash "$E/run-sitting-w34.sh" inactive 1

# Three longer-settle/order-seed sentinels per pass, kept separate from the seven.
bash "$E/run-sitting-w34.sh" active 2 --sentinel
# Repeat --sentinel for inactive 2, active 1 and inactive 1 at the matching mode.
```

Each normal pass defaults to runs 1–7 under `~/vitrea-w34/run/<pose>-<scale>x/`.
Sentinels default to 1–3 under the corresponding `-sentinel/` directory. Optional first/last
arguments narrow a planned continuation; existing run directories refuse rather than overwrite.
A completed run failing membership, pose, repeat or closing state is quarantined. An opening
refusal retains its attempted directory too; preserve/rename it before a deliberate continuation.
Every successful real run has the materializer's `attest.read` alongside the full JSON reads.

The four `dry-*-v2.txt` logs and `dry-attestations/` are real no-pixel rehearsals.
`test-sitting.py` mutates every gate for each pass. `non-dry-inactive-rehearsal.txt` is explicitly
**not a capture**: machine/launcher stubs exercise that branch, while the side binary's actual
`rehearse-tints` reads the explicit canonical root. W34 declares no tints, so that branch opens
no canonical PNG and measures zero tint pairs.

## Archive before plurality

Collect all 28 normal run roots and 12 sentinel roots as repeated `--run PATH` arguments.
Sentinel-only runs take their captured no-glass/fill dependencies from the matching normal run;
the pixel arrays and hashes travel in the archive, so replay never needs that source tree.

```bash
python3.12 "$E/archive-producer.py" --run "$RUN/active-1x/run-1" ... --out "$G1/repeat"
python3 "$E/materialize-producer.py" \
  --pass active-1x="$RUN/active-1x" --pass inactive-1x="$RUN/inactive-1x" \
  --pass active-2x="$RUN/active-2x" --pass inactive-2x="$RUN/inactive-2x" \
  --archive-inventory "$G1/repeat/inventory.json" --out "$G1/probe"
python3.12 "$E/report-bars.py" "$G1/repeat" --protocol normal > "$G1/bar.json"
python3.12 "$E/report-bars.py" "$G1/repeat" --protocol long > "$G1/sentinel-bar.json"
```

The ellipsis above means the complete explicit run list, not a literal CLI argument. Producers
may process holdout but expose only inventory, integrity hashes and admission. The archive
contains all admitted states before plurality, including losing states, as role-separated,
deduplicated lossless RGB crops with original coordinates/dimensions and all sampled inputs.
G0 used full-canvas crops for dependency closure; the 71 measured scratch captures have alpha255
everywhere, and no varying alpha input was omitted. Normal and long protocols are separate bars.
Materialization requires the archived source-manifest hashes before it can run. Its state
frequency logs and full holdout metadata stay in `holdout/`, not in G1's public manifest/report.

The G0 replay can run without the capture machine's raw files:

```bash
python3.12 "$E/replay-archive.py" "$E/scratch-repeat-archive" \
  --declaration "$E/scratch-archive-declaration" --deny-raw-root "$HOME/vitrea-w34"
```

The enforced raw-root ban is the proof, not a comparison of two stored spread tables.
`inventory-initial.json` preserves the first prototype header; the current inventory adds its
declaration binding without changing a payload hash or statistic. Other initial/draft artifacts
are retained with corrections beside them, not substituted for the final pinned declaration.

## One identification exposure, not the canonical material receipt

Commit the G2 candidate families/coefficients and the analysis runner before exposure:

```bash
python3.12 "$E/wave.py" expose --inventory "$G1/repeat/inventory.json" \
  --candidate "$G2/candidates.json" --runner "$G2/read-holdout.py"
```

The runner receives `W34_WAVE` and `W34_AUTHORIZATION` globals. It obtains a reader with
`roles=["holdout"], authorization=W34_AUTHORIZATION`; the same token authorises
`W34_WAVE.launch_scenes(...)` for its held-out web allowlist. Read through that reader, not
`Path.read_bytes`. A begin record is durable before payload access, a failed attempt is spent,
and changed candidates or a second exposure refuse. The digest covers declaration hashes,
evidence generation, instrument/closure bytes and committed candidate coefficients. This is
procedural sealing, not encryption of committed plaintext. The canonical G3 receipt is untouched.

## Verification

`pnpm --filter @vitrea/calibration test` exercises the pins, semantic-twin exclusion, native-only
CLI refusal, split/access/receipt and sitting gates. Numeric tests run when Python3.12/PIL/numpy
are present. Native decoding self-check runs from TypeScript on this Mac when the pinned side
binary exists; other CI hosts skip that native-only check explicitly. Do not rebuild the side
merely to make a test reachable. Independent declaration/code review remains the parent's gate.

W48 G0 (ledger §5.212; charter 2026-10-06-w48-dark-operators-fit.md; branch w48-g0-declaration off 78d0211e0).
Declaration only: no render, no ladder, no document moved. One sequence, each step committed before the next:
(a) W47's ladder evidence archived, replayed and pinned; (b) the tools, the reader and the draft; (c) part 1
hashed; (d) the verdicts; (e) part 2 validated against them and hashed. What is here, by directory.

archive/         X71: w47_ladders_archive.py (produce / pack / fetch / verify-tree, W42's form), the bundle's
                 per-file manifest inventory.json, archive.json (release w47-ladders-archive, asset digest,
                 round trip, second copy), test_archive.py.
replay/          replay.py: W47's read.py and reread.py run UNCHANGED from the fetched archive, the raw ladder
                 root and the live canonical tree denied by audit hook, inputs and outputs redirected; out/ holds
                 the replayed readings (byte-equal to W47's), captures.json (every capture by SHA-256), replay.json.
ladders/         evidence.json (W47's readings, protocol, both part-1 hashes and amendment record, pinned);
                 protocol.json (Decision Log 3's corrected bars and decision kinds over W47's rungs); verdicts.py
                 and test_verdicts.py (the reader; synthetic and control-row tests); verdicts.json/.txt after (c).
bindings.py      W48's pins, scratch, lock, snapshots, refusals of W44-W47; INHERITED pins W47's tools.
inherit.py       installs W48's bindings as `bindings` so W47's tools run BY PATH under them; REBIND.
documents/       the four 0.25 snapshots at 78d0211e0 (equal to W47's).
fit/, seal/      W48 copies of W47's build-candidate.ts and seal.ts (compiled-in bindings only); W48 tests.
tools/           run_inherited.py (a W47 test under W48's bindings) and its transcripts under inherited/.
cuts/ stage/ sheets/ referees/ level/ rehearsal/
                 W48 tests of the inherited tools, the rule rehearsal, X60 by evidence, the level re-proof.
census-gate.py, with-gpu.sh   W48 copies (lock /tmp/w48-gpu.lock).
declare.py, assemble.py, test_declare.py, declaration-inputs.json, fit-declaration-draft.json
                 the two-part declaration: hold beside strike, no precedence kind, check-fit on verdicts.json,
                 empty ops refused; part 1's inputs; the narrowed part-2 draft.

The archive's bytes are on the release and, as owner copies, at ~/.cache/vitrea-archives/<sha256>/ and
~/vitrea-w48/archive-copy/<sha256>/. W47's scratch tree ~/vitrea-w47/g0-ladders is kept, untouched.

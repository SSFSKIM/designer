W47 G0 (ledger §5.211; charter 2026-10-06-w47-span-graded-dark-transmission.md; branch w47-g0-operators).
The tools (G0 (c)-(e)) are W46's, ported by copy with W46's text beneath a W47 header; bindings.py is the one
place W47 is bound. What is here, by directory.

bindings.py      W47's pins, scratch, lock, snapshots (X62), X64 and X67's admitted keys (ADMITTED), X68's
                 domains (DOMAINS, in_domain), the shared inputs X69 freezes, the refusals of W44-W46.
documents/       the four 0.25 snapshots at the charter's merge c1f9bf84c (X62).
referees/        the X69 loader: w46-referees-1 by hash, never re-derived from W47's ladders; W46's adapter
                 run only on W46's frozen ladder list; membership, disjointness, withholding (red cases).
cuts/            W46's bed, cuts and rule (W45's growth-only rule as W46 bound it, verbatim).
rehearsal/       the rule on d0219cd684bf against itself and on W46's point A by its committed gate cut
                 (16/8 and 17/10 reproduced); the cuts port proof against W46's d0219 cut (0 of 56,289 differ).
fit/, seal/      the builder (exactly ADMITTED per dark slot, X68 refused), the fit driver and search, the seal.
                 The builder and the seal also refuse a leaf the runtime does not know: withMaterialOverrides
                 silently drops an unknown patch key, so in W46's form an operator leaf named at 0 before the
                 operators merged would have "reproduced" the digest while proving nothing (the silent-drop
                 hazard, closed in the port).
stage/           the dark stage and X60; stage/rehearsal/ the strict-mode rehearsal (132/132 rows, 264/264
                 captures identical); stage/x60/ X60 by evidence at G0, IDENTICAL.
level/           the level check, taught operator 1 (alphaBase before the occlusion term and the W9 solve);
                 level/identity/ the shipped rung on every ladder (i) cell, 130/130 identical.
sheets/          the eye sheets, populations per phase.
ladders/         cells.json (Design "The ladders" (i)-(iv)), protocol.json (41 rungs, clause 5's bars and
                 decisions), the runner with X70's requested/planned/measured check, the reader, part2.py.
diagnostic/      G0 (f)'s depth-split diagnostic: record.json (the body form chosen).
targets/         the targets' predictions from point A (the parent's).
declare.py, assemble.py, declaration-inputs.json, fit-declaration-draft.json
                 the two-part declaration with W46's content-amendment form; part 1's inputs; the part-2 draft.
census.jsonl, census-gate.py, with-gpu.sh   the classifying census, the browser pin and the GPU lock.

Scratch on the capture machine: ~/vitrea-w47/g0-tools-scratch/{stage-rehearsal,level}/.

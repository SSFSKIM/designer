# W31 G2 — the WGSL range class and the refusal's wording

Evidence for claims `c9a §5.163`. Nothing here is a capture: this gate takes no
native pixel (X5) and its browser runs are the two named specs plus the golden
and GPU suites (X6), each bracketed by a machine read in `machine.txt`.

| file | what it is |
| --- | --- |
| `call-sites.txt`, `.json` | every transcendental call in `packages/renderer-webgpu/src/wgsl/`, its resolved argument intervals, and whether it is clamped by the source or bounded by a committed proof — plus two MUTATIONS, each re-introducing a defect a gate fixed, to show the instrument can go red |
| `scan-report.mjs` | generates the above from `packages/renderer-webgpu/test/wgsl-range/` |
| `sweeps.txt` | every `@gpu` range sweep's reading: the material axis over ±550x and the scene axis over spans 32…340 |
| `leaf-moves.py`, `.txt` | where the 550x bracket comes from — the widest ratio any leaf has moved between two material generations, read off the documents' own `entries[].previous` |
| `falloff-reach.py`, `.txt` | the outer shadow's falloff argument at the deepest pixel of every bed component, against the overflow boundary of 10.0610 — the range proof W30 G3b's residual was waiting on |
| `guard-first-form.txt` | what the readback guard's first form caught, and why the predicate gained its silhouette clause |
| `machine.txt` | RT, IC and `NSGlassTintAmount` before and after every browser run (X6) |
| `test-golden.txt`, `goldens-git-status.txt` | 34/34, no regen, `e2e/goldens` clean |
| `test-gpu.txt` | 42 passed |
| `unit-tests.txt` | `pnpm -r test` |
| `freeze-open.txt`, `freeze-close.txt` | `freeze.py verify` at the gate's open and close |
| `record-machine.sh` | the X6 reader; it refuses rather than records a run taken at the wrong machine state |

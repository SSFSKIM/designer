# W32 G2 — the chain's FIRST run, kept because it found something

*Claims §5.169 §7.* This directory is the chain run at the head before commit
`f6aadcdb`. **It is red on one step and the red is the point**: `pnpm -r lint`
exit 2, on `apps/demo`'s type-check refusing
`import type { ResolvedMaterialPolicy } from "@vitreajs/vitrea-web"` — that
interface is core's and no published package re-exports it, so the `/laws/`
shadow stage named a type it could not import. A step that fails is a record and
not a reason to re-run until it is green, which is what `chain.sh`'s own header
has said since W30 G4; the defect is fixed in the commit after this run and the
chain is re-run at that head, beside this one rather than over it.

Every other step of this run is green and its counts are the same as the second
run's, because `vite` strips types and nothing the type-check refused reaches a
rendered pixel: freeze 1,818 at open and close, the capture tree 1,900 / 1,893
match / 0 mismatch / 0 misfiled, build and root eslint exit 0, **2,698 unit tests
over 186 files**, goldens **34** byte-identical, gpu **48**, platform-web **410**,
React **174 passed / 3 skipped / 0 failed**, demo **61**, the macOS 27 bed
**230 gated / 786** and the frozen bed **229 / 1,107**.

"""M2's past-Apple clause, mutated (W42 G0 review of b151aff4, finding 6): red / green.

Two mutants of `structureVerdict`'s past-Apple clause, each applied to two copies of
test/adopted-thresholds.test.ts: the committed file (with finding 6's two seeds) and the file at
9a695ec0 (the seeds before them). Copies go to packages/calibration/.scratch-w42-m2-mutants/,
outside vitest's `test/**` include and tsc's globs; the committed file is never edited. From
packages/calibration:

    python3.12 -B <this file>
    for f in .scratch-w42-m2-mutants/*.test.ts; do
      pnpm exec vitest run --config .scratch-w42-m2-mutants/vitest.config.ts "$f"; done
    rm -r .scratch-w42-m2-mutants

mutants.txt beside this file records what each showed.
"""
import pathlib
import subprocess

PKG = pathlib.Path(__file__).resolve().parents[4]
REPO = PKG.parent.parent
OUT = PKG / ".scratch-w42-m2-mutants"
OUT.mkdir(exist_ok=True)
CLAUSE = "Math.abs(web - native) / native <= CHROMA_STRUCTURE_TOLERANCE"
MUTANTS = {
    "no-abs": "(web - native) / native <= CHROMA_STRUCTURE_TOLERANCE",
    "over-r": "Math.abs(web - native) / reference <= CHROMA_STRUCTURE_TOLERANCE",
}
SOURCES = {
    "seeds-now": (PKG / "test" / "adopted-thresholds.test.ts").read_text(),
    "seeds-9a695ec0": subprocess.run(
        ["git", "show", "9a695ec0:packages/calibration/test/adopted-thresholds.test.ts"],
        cwd=REPO, check=True, capture_output=True, text=True).stdout,
}
for source, text in SOURCES.items():
    assert text.count(CLAUSE) == 1, source
    (OUT / f"{source}--unmutated.test.ts").write_text(text)
    for mutant, clause in MUTANTS.items():
        (OUT / f"{source}--{mutant}.test.ts").write_text(text.replace(CLAUSE, clause))
(OUT / "vitest.config.ts").write_text(
    'import { defineConfig } from "vitest/config";\n'
    'export default defineConfig({ test: { include: [".scratch-w42-m2-mutants/*.test.ts"] } });\n')
print("\n".join(sorted(p.name for p in OUT.glob("*.test.ts"))))

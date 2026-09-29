"""Generate throwaway red scenarios from the committed adopted-thresholds.test.ts.

Each scenario is a scratch copy under packages/calibration/.scratch-w42-m2-red/ that seeds ONE
live cut cell and its matrix row (1x light photo__rrect-sm__inactive, validation; r = w =
0.018154, Apple 0.026761) and optionally adds an M2 entry to MISSED_27_ROWS. The committed file is never edited. Run each
copy with `pnpm exec vitest run --config .scratch-w42-m2-red/vitest.config.ts <copy>` from
packages/calibration, then delete .scratch-w42-m2-red/. red-green.txt records what each showed.
"""
import pathlib
# packages/calibration, from results/2026-09-29-w42-g0-declaration/gate/m2-named-miss/.
PKG = pathlib.Path(__file__).resolve().parents[4]
SRC = (PKG / "test" / "adopted-thresholds.test.ts").read_text()
OUT = PKG / ".scratch-w42-m2-red"
OUT.mkdir(exist_ok=True)
KEY = ("texture / validation / photo__rrect-sm__inactive / "
       "apple-macos-27.0-1x-light-standard-glass0.5 :: interiorStdDevStructureDelta")

ANCHOR = '  resolve(PACKAGE_ROOT, "results", "2026-09-24-w36-g1-black-branch", "chroma-cut.json"),\n);\n'
assert SRC.count(ANCHOR) == 1
LIST_END = "  // span, which is where it landed. The tracker carries the measurement.\n};\n"
assert SRC.count(LIST_END) == 1

def seed(web_expr):
    return ANCHOR + f"""{{
  // RED SCRATCH: seed one live cut cell.
  const seeded = CHROMA_CUT.cells.find(
    (c) => c.profile === "apple-macos-27.0-1x-light-standard-glass0.5" &&
      c.scene === "photo__rrect-sm__inactive",
  ) as unknown as Record<string, number>;
  const r = seeded["interiorStdDevWebReference"] as number;
  const n = 0.026761377891451815;
  seeded["interiorStdDevWeb"] = {web_expr};
  seeded["structureDeltaFraction"] = ((seeded["interiorStdDevWeb"] as number) - r) / r;
  // And the matrix row the cut re-derives from, so the cut stays backed by it.
  const rows = MATRIX_FILE.cells.filter(
    (c) => c.key.profileKey === "apple-macos-27.0-1x-light-standard-glass0.5" &&
      c.key.sceneId === "photo__rrect-sm__inactive" && c.key.web.renderer === "webgpu" &&
      c.fixtureSet === "validation",
  );
  if (rows.length !== 1) throw new Error(`RED SCRATCH: ${{rows.length}} matrix rows`);
  (rows[0]!.material!["interiorStdDevWeb"] as {{ value: number }}).value =
    seeded["interiorStdDevWeb"] as number;
}}
"""

def entry(measured, native):
    tail = "" if native is None else f", native: {native}"
    return LIST_END.replace("};\n", f'  "{KEY}": {{ measured: {measured}, bound: "≤ 0.02"{tail} }},\n}};\n')

SCENARIOS = {
    # name: (web expression, entry or None)
    "a-away-unlisted":        ("r * 0.95", None),
    "a2-away-listed":         ("r * 0.95", entry(0.05, 0.02676)),
    "b-toward-unlisted":      ("r * 1.10", None),
    "b2-toward-listed":       ("r * 1.10", entry(0.1, 0.02676)),
    "b3-toward-listed-no-native": ("r * 1.10", entry(0.1, None)),
    "c-past-by-5pct-listed":  ("n * 1.05", entry(0.54783, 0.02676)),
    "d-past-by-1pct-listed":  ("n * 1.01", entry(0.48887, 0.02676)),
}
for name, (web, ent) in SCENARIOS.items():
    s = SRC.replace(ANCHOR, seed(web))
    if ent is not None:
        s = s.replace(LIST_END, ent)
    (OUT / f"{name}.test.ts").write_text(s)
(OUT / "vitest.config.ts").write_text(
    'import { defineConfig } from "vitest/config";\n'
    'export default defineConfig({ test: { include: [".scratch-w42-m2-red/*.test.ts"] } });\n')
print("\n".join(SCENARIOS))

"""L1 growth's named-miss path (W42 G0; charter Decision Log 5d): red and green scenarios.

Each scenario is a throwaway copy of the committed test/adopted-thresholds.test.ts under
packages/calibration/.scratch-w42-l1-red/ (outside vitest's `test/**` include and tsc's globs).
It seeds the growth of one or more L1 population cells in the matrix the test loads, and the
same cells in the L1 cut beside it (web, error, growth, and the cut's growthFailures and
absoluteMisses), so "re-derives every recorded mean" stays green and the seed reaches only the
growth clause and its owner. Some scenarios also add GROWTH_MISSES entries. The committed file
is never edited. From packages/calibration:

    python3.12 -B <this file>
    for f in .scratch-w42-l1-red/*.test.ts; do
      pnpm exec vitest run --config .scratch-w42-l1-red/vitest.config.ts "$f"; done
    rm -r .scratch-w42-l1-red

red-green.txt beside this file records what each showed.
"""
import pathlib

PKG = pathlib.Path(__file__).resolve().parents[4]
SRC = (PKG / "test" / "adopted-thresholds.test.ts").read_text()
OUT = PKG / ".scratch-w42-l1-red"
OUT.mkdir(exist_ok=True)

SEED_ANCHOR = '    return verdict === "within" ? [] : [{ cell: key(c), growth: e - before, verdict }];\n  });\n'
LIST_ANCHOR = "  const GROWTH_MISSES: Readonly<Record<string, GrowthMiss>> = {\n"
assert SRC.count(SEED_ANCHOR) == 1 and SRC.count(LIST_ANCHOR) == 1


def cell(scale, scheme, scene):
    return f"apple-macos-27.0-{scale}x-{scheme}-standard-glass0.5/{scene}"


LIGHT_TINT = "photo__rrect-md__inactive-tint-orange"
DARK_TINT = "photo__capsule-button__inactive-tint-orange"
#: Decision Log 5d's four cell-profiles at round 3's r3-2pgb growths (declaration item
#: l1TintedReceded): light +0.0108 / +0.0100, dark +0.0138 / +0.0133 (1x / 2x).
RULED = {cell(1, "light", LIGHT_TINT): 0.0108, cell(2, "light", LIGHT_TINT): 0.0100,
         cell(1, "dark", DARK_TINT): 0.0138, cell(2, "dark", DARK_TINT): 0.0133}
L1X = cell(1, "light", LIGHT_TINT)
TWIN = cell(1, "light", "photo__rrect-md__inactive")


def seeded(seeds):
    calls = "".join(f'    seedGrowth("{k}", {g});\n' for k, g in seeds.items())
    return SEED_ANCHOR + f"""  {{
    // RED SCRATCH: seed each cell's growth in the matrix row and in the L1 cut beside it.
    const seedGrowth = (cellKey: string, g: number): void => {{
      const c = population.find(p => key(p) === cellKey);
      const b = old.find(p => key(p) === cellKey);
      if (c === undefined || b === undefined) throw new Error(`RED SCRATCH: ${{cellKey}}`);
      const n = value(c, "interiorMeanNative")!, w = value(c, "interiorMeanWeb")!;
      const before = error(b)!;
      const moved = n + (w >= n ? 1 : -1) * (before + g);
      (c.material!["interiorMeanWeb"] as {{ value: number }}).value = moved;
      const row = (CUT.cells as unknown as Record<string, unknown>[])
        .find(r => r["cell"] === cellKey)!;
      row["web"] = moved;
      row["error"] = Math.abs(moved - n);
      row["growth"] = Math.abs(moved - n) - before;
    }};
{calls}    const cut = CUT as unknown as Record<string, unknown>;
    cut["growthFailures"] = CUT.cells.filter(r => r.growth !== null && r.growth > 0.005);
    cut["absoluteMisses"] = CUT.cells.filter(r => r.error !== null && r.error > 0.055);
  }}
"""


def listed(entries):
    return LIST_ANCHOR + "".join(f'    "{k}": {{ measured: {m}, bound: "≤ 0.005" }},\n'
                                 for k, m in entries.items())


SCENARIOS = {
    # name: (seeds {cell: growth}, entries {cell: measured})
    "a-ruled-unlisted": ({L1X: 0.0108}, {}),
    "b-ruled-listed": ({L1X: 0.0108}, {L1X: 0.0108}),
    "b2-ruled-listed-wrong-measured": ({L1X: 0.0108}, {L1X: 0.0100}),
    "c-closed-listed": ({}, {L1X: 0.0108}),
    "d-unruled-unlisted": ({TWIN: 0.0108}, {}),
    "d2-unruled-listed": ({TWIN: 0.0108}, {TWIN: 0.0108}),
    "e-four-ruled-listed": (RULED, RULED),
    "f-four-ruled-listed-plus-unruled": ({**RULED, TWIN: 0.0108}, RULED),
}
for name, (seeds, entries) in SCENARIOS.items():
    s = SRC
    if seeds:
        s = s.replace(SEED_ANCHOR, seeded(seeds))
    if entries:
        s = s.replace(LIST_ANCHOR, listed(entries))
    (OUT / f"{name}.test.ts").write_text(s)
(OUT / "vitest.config.ts").write_text(
    'import { defineConfig } from "vitest/config";\n'
    'export default defineConfig({ test: { include: [".scratch-w42-l1-red/*.test.ts"] } });\n')
print("\n".join(SCENARIOS))

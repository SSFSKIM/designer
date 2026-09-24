/** A surviving receded difference must not force rewriting a historical alias (§5.179). */
import { spawnSync } from "node:child_process";
import { resolve } from "node:path";
import { expect, it } from "vitest";

for (const name of ["shared-receded-selftest.py", "classifier-selftest.py"]) {
  it(`runs the split's ${name} against synthetic generations`, () => {
    const result = spawnSync("python3", [resolve(import.meta.dirname,
      "../results/2026-09-20-w30-g1-split", name)], { encoding: "utf8" });
    expect(result.status, result.stdout + result.stderr).toBe(0);
  });
}

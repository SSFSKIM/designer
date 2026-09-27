import { spawnSync } from "node:child_process";
import { join, resolve } from "node:path";
import { expect, it } from "vitest";

const root = resolve(import.meta.dirname, "../../..");
const evidence = join(root, "packages/calibration/results/2026-09-27-w41-g0-declaration");
const pythonAvailable = spawnSync("python3.12", ["-B", "-c", "import numpy, PIL"], {
  encoding: "utf8",
}).status === 0;

// These are the instrument's original red/green synthetic behaviors, wired into
// the suite without a native archive, SciPy, a GPU, a browser or an exposure.
for (const script of ["instrument/test-instrument.py", "instrument/test-shadow.py",
  "instrument/test-rendered.py", "exposure/test_runner.py"]) {
  it.skipIf(!pythonAvailable)(`executes W41 synthetic behavior: ${script}`, () => {
    const result = spawnSync("python3.12", ["-B", join(evidence, script)], {
      encoding: "utf8", timeout: 90_000,
      env: { ...process.env, PYTHONDONTWRITEBYTECODE: "1" },
    });
    expect(result.status, result.stderr || result.stdout).toBe(0);
  }, 100_000);
}

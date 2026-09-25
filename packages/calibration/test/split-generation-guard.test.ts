import { spawnSync } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { expect, it } from "vitest";

const SPLITTER = resolve(import.meta.dirname, "..", "results", "2026-09-20-w30-g1-split", "split-generation.py");

it("retired splitter cannot apply after the generation index appears", () => {
  const root = mkdtempSync(join(tmpdir(), "w40-old-splitter-"));
  try {
    const script = join(root, "packages/calibration/results/2026-09-20-w30-g1-split/split-generation.py");
    const index = join(root, "packages/calibration/results/generations/index.json");
    const evidence = join(root, "evidence");
    mkdirSync(resolve(script, ".."), { recursive: true });
    mkdirSync(resolve(index, ".."), { recursive: true });
    copyFileSync(SPLITTER, script);
    writeFileSync(index, JSON.stringify({ current: {} }));
    const child = spawnSync("python3", [script, "apply", "--evidence", evidence,
      "--claims", "test", "--read-claims", "test"], { encoding: "utf8" });
    expect(child.status).toBe(1);
    expect(child.stdout + child.stderr).toMatch(/G1.*publish/i);
    expect(existsSync(evidence)).toBe(false);
  } finally { rmSync(root, { recursive: true, force: true }); }
});

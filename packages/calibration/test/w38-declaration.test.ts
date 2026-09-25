import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { describe, expect, it } from "vitest";

const evidence = new URL("../results/2026-09-25-w38-g0-rim-axis-cut/", import.meta.url);
describe("W38 pre-score declaration", () => {
  it("pins the candidate budget, baseline generation and all three E2 estimators", () => {
    const pins = JSON.parse(readFileSync(new URL("declaration-pins.json", evidence), "utf8")) as Record<string, string>;
    expect(pins["bounds-declaration.txt"]).toBe("4ceecfb9c8adb8193c02e36a5aaef70c04275a8678435c302dc4a1317f8be818");
    for (const [name, sha] of Object.entries(pins)) {
      expect(createHash("sha256").update(readFileSync(new URL(name, evidence))).digest("hex")).toBe(sha);
    }
  });
  it("proves literal held-top and native pre-composition recovery", () => {
    expect(() => execFileSync("python3.12", [new URL("test-model.py", evidence).pathname],
      { stdio: "pipe" })).not.toThrow();
  });
});

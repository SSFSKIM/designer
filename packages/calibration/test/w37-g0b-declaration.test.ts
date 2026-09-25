import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

describe("W37 G0b pre-score budget", () => {
  it("pins the independently declared budget before scoring", () => {
    const bytes = readFileSync(new URL(
      "../results/2026-09-25-w37-g0b-edge-identification/bounds-declaration.txt",
      import.meta.url,
    ));
    expect(createHash("sha256").update(bytes).digest("hex")).toBe(
      "0ddc766612ab8f84143b7cef665e889c80437c423fc39e8253564d51b4f769bd",
    );
  });
});

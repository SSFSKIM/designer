import { describe, expect, it } from "vitest";

import { FIXTURE_SETS, METRIC_AXES, parseProfileKey } from "../src/index";

describe("profile keys (X9)", () => {
  it("parses the spec's canonical v1 profile key", () => {
    expect(parseProfileKey("apple-macos-26.5-2x-light-standard")).toEqual({
      platform: "macos",
      osVersion: "26.5",
      scale: 2,
      colorScheme: "light",
      a11yMode: "standard",
    });
  });

  it("refuses a key that omits an axis rather than defaulting it", () => {
    expect(parseProfileKey("apple-macos-26.5-2x-light")).toBeNull();
    expect(parseProfileKey("macos-26.5-2x-light-standard")).toBeNull();
  });

  it("keeps a holdout set and reports every metric axis", () => {
    expect(FIXTURE_SETS).toContain("holdout");
    expect(METRIC_AXES).toEqual(["shape", "material", "motion", "perceptual"]);
  });
});

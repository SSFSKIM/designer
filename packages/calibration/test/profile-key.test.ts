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

  it("parses a 26.5 key with no slider axis at all, not with a defaulted one", () => {
    // The axis is absent from 26.x, not unspecified: `NSGlassTintAmount` exists
    // in no 26.x preference store (W29 G0 (d)). A 0.5 read out of a 26.5 key
    // would claim the bed was captured at the 27 centre, which is the one thing
    // nobody can know about it.
    expect(parseProfileKey("apple-macos-26.5-2x-light-standard")).not.toHaveProperty("glass");
  });

  it("parses the 27 bed's key with the appearance slider in it", () => {
    expect(parseProfileKey("apple-macos-27.0-2x-light-standard-glass0.5")).toEqual({
      platform: "macos",
      osVersion: "27.0",
      scale: 2,
      colorScheme: "light",
      a11yMode: "standard",
      glass: 0.5,
    });
    // Both ends of the slider's range, and an accessibility key, since the two
    // 27 accessibility profiles carry the token like every other 27 key (X6).
    expect(parseProfileKey("apple-macos-27.0-1x-dark-standard-glass0")?.glass).toBe(0);
    expect(parseProfileKey("apple-macos-27.0-1x-dark-standard-glass1")?.glass).toBe(1);
    expect(
      parseProfileKey("apple-macos-27.0-1x-light-increased-contrast-glass0.5"),
    ).toMatchObject({ a11yMode: "increased-contrast", glass: 0.5 });
    // The machine's as-found position, which Decision Log 3 (a) records as a
    // reading rather than a bed: the grammar must be able to say it.
    expect(parseProfileKey("apple-macos-27.0-2x-light-standard-glass0.5459057")?.glass)
      .toBeCloseTo(0.5459057, 7);
  });

  it("refuses a slider token that states no amount, and one before the a11y mode", () => {
    // A key ending `-glass` names the axis and not its position, which is worse
    // than omitting it: it looks attested.
    expect(parseProfileKey("apple-macos-27.0-2x-light-standard-glass")).toBeNull();
    expect(parseProfileKey("apple-macos-27.0-2x-light-standard-glass0.5-extra")).toBeNull();
    // The token is last. A mid-key spelling parses as nothing rather than as a
    // key whose scale or scheme moved position, so the placement is a grammar
    // rule and not a convention (see PROFILE_KEY_PATTERN).
    expect(parseProfileKey("apple-macos-27.0-glass0.5-2x-light-standard")).toBeNull();
  });

  it("keeps a holdout set and reports every metric axis", () => {
    expect(FIXTURE_SETS).toContain("holdout");
    expect(METRIC_AXES).toEqual(["shape", "material", "motion", "perceptual"]);
  });
});

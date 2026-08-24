import { describe, expect, it } from "vitest";

import { BACKDROP_FILTER_PROPERTIES, checkSupportGate } from "../src/probe/support-gate";

const supporting = (...properties: readonly string[]) => (property: string) =>
  properties.includes(property);

describe("probe layer 1 — the support gate (necessary, never sufficient)", () => {
  it("tests both the unprefixed and the -webkit- property", () => {
    // WebKit answers true for the prefixed form and false unprefixed; Chromium
    // and Gecko do the reverse. Both must be asked, and both must be emitted.
    expect(BACKDROP_FILTER_PROPERTIES).toEqual(["backdrop-filter", "-webkit-backdrop-filter"]);
  });

  it("passes when either form is supported", () => {
    expect(checkSupportGate(supporting("backdrop-filter")).supported).toBe(true);
    expect(checkSupportGate(supporting("-webkit-backdrop-filter")).supported).toBe(true);
  });

  it("fails only when the property is absent altogether", () => {
    expect(checkSupportGate(supporting()).supported).toBe(false);
  });

  it("records which form answered, because the CSS has to emit that one", () => {
    expect(checkSupportGate(supporting("-webkit-backdrop-filter")).properties).toEqual([
      "-webkit-backdrop-filter",
    ]);
  });

  it("states its own reach, so a caller cannot read it as a conformance verdict", () => {
    // CSS.supports returns true in builds that render nothing at all — measured
    // in Firefox 154 and WebKit 26.5 (S1 §Environmental blocker). The gate says
    // so about itself rather than leaving the caller to remember.
    expect(checkSupportGate(supporting("backdrop-filter")).reach).toBe("property-presence-only");
  });
});

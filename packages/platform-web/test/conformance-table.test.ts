import { describe, expect, it } from "vitest";

import {
  CONFORMANCE_TABLE,
  conformanceRowFor,
  CONSERVATIVE_ROW,
  detectEngine,
} from "../src/probe/conformance-table";

const CHROME_151 =
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36";
const FIREFOX_154 =
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.7; rv:154.0) Gecko/20100101 Firefox/154.0";
const SAFARI_26 =
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.5 Safari/605.1.15";
const EDGE_151 = `${CHROME_151} Edg/151.0.0.0`;

describe("engine detection", () => {
  it("names the three engine families", () => {
    expect(detectEngine(CHROME_151)).toEqual({ family: "chromium", version: 151 });
    expect(detectEngine(FIREFOX_154)).toEqual({ family: "gecko", version: 154 });
    expect(detectEngine(SAFARI_26)).toEqual({ family: "webkit", version: 26.5 });
  });

  it("reads a Chromium derivative as Chromium, not as WebKit", () => {
    expect(detectEngine(EDGE_151).family).toBe("chromium");
  });

  it("falls back to unknown rather than guessing", () => {
    expect(detectEngine("Wget/1.21").family).toBe("unknown");
    expect(detectEngine("").family).toBe("unknown");
  });
});

describe("the per-engine conformance table (S1 probe layer 3)", () => {
  it("fails closed: an unrecognised engine gets the conservative row", () => {
    expect(conformanceRowFor({ family: "unknown", version: 0 })).toBe(CONSERVATIVE_ROW);
  });

  it("fails closed on a version below every recorded range", () => {
    // A table entry is a claim about versions that were measured. Nothing was
    // measured about Chromium 42, so it gets the conservative row.
    expect(conformanceRowFor({ family: "chromium", version: 42 })).toBe(CONSERVATIVE_ROW);
  });

  it("carries the measured Chromium row", () => {
    const row = conformanceRowFor({ family: "chromium", version: 151 });

    expect(row.rasterisesBackdropFilter).toBe("yes");
    expect(row.referenceFilterInBackdrop).toBe(true);
    expect(Number.isFinite(row.maxProxyAreaDevicePx)).toBe(true);
  });

  it("records Gecko and WebKit as unverified rather than as failing", () => {
    // S1 could neither confirm nor narrow them: backdrop-filter renders as a
    // no-op in every automated capture path on this machine while rendering
    // live. Capture blindness is not feature breakage (Decision Log #17).
    for (const engine of [
      { family: "gecko", version: 154 },
      { family: "webkit", version: 26.5 },
    ] as const) {
      expect(conformanceRowFor(engine).rasterisesBackdropFilter).toBe("unverified");
    }
  });

  it("records the reference-filter gap that CSS.supports cannot see", () => {
    // CSS.supports('backdrop-filter','url(#x)') is true in all three engines
    // and only Chromium renders it (WebKit 245510, Gecko 1887451). The table is
    // the only place that fact can live.
    expect(conformanceRowFor({ family: "gecko", version: 154 }).referenceFilterInBackdrop).toBe(false);
    expect(conformanceRowFor({ family: "webkit", version: 26.5 }).referenceFilterInBackdrop).toBe(false);
  });

  it("records the 3D-transform hazard where WPT and the engine bugs put it", () => {
    expect(conformanceRowFor({ family: "gecko", version: 154 }).transform3dHazard).not.toBe("none");
    expect(conformanceRowFor({ family: "webkit", version: 26.5 }).transform3dHazard).not.toBe("none");
  });

  it("makes every row cite its evidence — the documented update path in one assertion", () => {
    for (const row of [...CONFORMANCE_TABLE, CONSERVATIVE_ROW]) {
      expect(row.evidence.length).toBeGreaterThan(0);
    }
  });

  it("keeps the conservative row conservative on every axis", () => {
    expect(CONSERVATIVE_ROW.rasterisesBackdropFilter).toBe("unverified");
    expect(CONSERVATIVE_ROW.referenceFilterInBackdrop).toBe(false);
    expect(CONSERVATIVE_ROW.transform3dHazard).toBe("unverified");
    for (const row of CONFORMANCE_TABLE) {
      expect(CONSERVATIVE_ROW.maxProxyAreaDevicePx).toBeLessThanOrEqual(row.maxProxyAreaDevicePx);
    }
  });
});

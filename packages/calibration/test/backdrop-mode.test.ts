import { describe, expect, it } from "vitest";
import {
  BACKDROP_LEVELS_ENV,
  BACKDROP_MODE_ENV,
  backdropProbeLabel,
  backdropProbeRequested,
  parseBackdropLevel,
  parseBackdropMode,
  probeCanonicalOutputRefusal,
} from "../src/backdrop-probe";
import { resolveScene } from "../web/scenes";

describe("page-content calibration mode", () => {
  it("changes only texture-backed groups, preserving the native stack relationship", () => {
    for (const id of ["photo__rrect-md__rest", "checkerboard__toolbar-group__rest",
      "photo__glass-over-glass__rest"]) {
      const sampled = resolveScene(id);
      const page = resolveScene(id, "dom");
      expect(page.surfaces).toEqual(sampled.surfaces);
      expect(page.groups).toEqual(sampled.groups.map((group) => ({ ...group, source: "dom" })));
      expect(sampled.groups[0]?.source).toBe("texture");
    }
    expect(resolveScene("photo__glass-over-glass__rest").groups[1]?.source).toBe("dom");
  });
});

describe("the probe's requested axes", () => {
  it("reads the canonical request from an absent one, and refuses an unknown route", () => {
    expect(parseBackdropMode(null)).toBe("texture");
    expect(parseBackdropMode("dom")).toBe("dom");
    expect(() => parseBackdropMode("page")).toThrow(/texture or dom/);
  });

  it("takes an authored level only as a measured fraction", () => {
    expect(parseBackdropLevel(null)).toBeNull();
    expect(parseBackdropLevel("0.21404114048223255")).toBe(0.21404114048223255);
    expect(parseBackdropLevel("0")).toBe(0);
    for (const bad of ["1.5", "-0.1", "dark", "NaN"]) {
      expect(() => parseBackdropLevel(bad)).toThrow(/measured fraction/);
    }
  });

  it("adds nothing to a canonical capture's key, and names both axes on a probe's", () => {
    // The whole point of the label: every shipped cell's `capturePath` is
    // unchanged to the byte, and no probe cell can be read as one of them.
    expect(backdropProbeLabel("texture", null)).toBe("");
    expect(backdropProbeLabel("dom", null)).toBe(", backdrop=dom, authoredBackdropLevel=none");
    expect(backdropProbeLabel("texture", 0.5)).toBe(", backdrop=texture, authoredBackdropLevel=0.5");
    // A hinted page capture and an unhinted one over the same raster differ here
    // and nowhere else in the key.
    expect(backdropProbeLabel("dom", 0.5)).not.toBe(backdropProbeLabel("dom", null));
  });

  it("sees either environment axis as a probe run", () => {
    expect(backdropProbeRequested({})).toBe(false);
    expect(backdropProbeRequested({ [BACKDROP_MODE_ENV]: "dom" })).toBe(true);
    expect(backdropProbeRequested({ [BACKDROP_LEVELS_ENV]: "/tmp/levels.json" })).toBe(true);
  });
});

describe("the probe's canonical-output refusal", () => {
  const captures = {
    what: "captures", path: "/repo/web-captures", canonical: "/repo/web-captures", tree: true,
  };
  const matrix = { what: "matrix", path: "/tmp/probe.json", canonical: "/repo/results/matrix.json" };

  it("leaves a canonical run alone", () => {
    expect(probeCanonicalOutputRefusal(false, [captures, matrix])).toBeUndefined();
  });

  it("refuses a probe writing a canonical destination, or not redirecting one at all", () => {
    expect(probeCanonicalOutputRefusal(true, [captures])).toMatch(/canonical captures/);
    expect(probeCanonicalOutputRefusal(true, [{ ...matrix, path: undefined }]))
      .toMatch(/no scratch matrix/);
    // Every refused destination is named, so a run is redirected once rather
    // than one error at a time.
    expect(probeCanonicalOutputRefusal(true, [captures, { ...matrix, path: matrix.canonical }]))
      .toMatch(/captures.*matrix/s);
  });

  it("lets a probe write scratch paths", () => {
    expect(probeCanonicalOutputRefusal(true, [{ ...captures, path: "/tmp/w27f/captures" }, matrix]))
      .toBeUndefined();
  });

  it("refuses a profile directory inside the canonical capture tree", () => {
    // Where a run's PNGs actually land, and the destination equality alone would
    // have waved through.
    const inside = { ...captures, path: "/repo/web-captures/apple-macos-26.5-1x-light-standard" };
    expect(probeCanonicalOutputRefusal(true, [inside])).toMatch(/inside the canonical captures/);
    expect(probeCanonicalOutputRefusal(true, [{ ...captures, path: "/repo/web-captures/x/y" }]))
      .toMatch(/inside the canonical captures/);
  });

  it("takes containment by segment, so a sibling scratch directory is allowed", () => {
    expect(probeCanonicalOutputRefusal(true, [{ ...captures, path: "/repo/web-captures-scratch" }]))
      .toBeUndefined();
    // Only a tree contains anything: a matrix is one file.
    expect(probeCanonicalOutputRefusal(true, [{ ...matrix, path: `${matrix.canonical}/inner` }]))
      .toBeUndefined();
  });
});

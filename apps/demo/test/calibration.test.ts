/**
 * Which cell the page speaks with — `reportsFor`'s head, over the matrix the page
 * actually imports.
 *
 * The figure beside a live surface is a claim about the material that surface is made
 * of, so the head of this list is the page's answer and everything about it is a
 * claim: the profile of the resolved colour scheme, the tier the page draws, and —
 * since W30 G1's review closure — the generation, meaning the reading taken at the
 * material profile documents that are on disk rather than one a refit superseded.
 *
 * The dark scheme is where the first two were least protected. `Stage.tsx` renders a
 * report only where a native capture exists, so on the page the light path is exercised
 * over the 32 scenes the picker offers and the dark path over the 12 of them the dark
 * bed carries a capture for. The assertions below read every scene in the file instead,
 * which is what makes them a statement about the rule rather than about today's fixture
 * coverage.
 */

import { describe, expect, it } from "vitest";

import { primacy, REPORTS_BY_SCENE, reportsFor, type CellReport } from "../src/site/calibration";

const DARK_27 = "apple-macos-27.0-1x-dark-standard-glass0.5";
const DARK_26 = "apple-macos-26.5-1x-dark-standard";

describe("reportsFor names one cell in the dark scheme", () => {
  const carriesBoth = [...REPORTS_BY_SCENE.entries()].filter(
    ([, reports]) =>
      reports.some((report) => report.profileKey === DARK_27) &&
      reports.some((report) => report.profileKey === DARK_26),
  );

  it("has scenes measured under both the macOS 27 and the macOS 26.5 dark profiles", () => {
    // The fixture for the case below: the matrix holds macOS 26.5 rows beside the
    // macOS 27 ones, and a scene carrying both is where "which cell" has a wrong
    // answer available to it. If the file ever stopped holding both, the assertion
    // below would pass vacuously and stop meaning anything.
    expect(carriesBoth.length).toBeGreaterThan(0);
  });

  it("puts the macOS 27 texture cell first for every one of them", () => {
    for (const [sceneId] of carriesBoth) {
      const head = reportsFor(sceneId, "dark")[0];
      expect(head?.profileKey, sceneId).toBe(DARK_27);
      expect(head?.tier, sceneId).toBe("texture");
      // And it is the shipped reading of that cell, which is the term `capturedAt`
      // used to stand in for.
      expect(head?.atShippedDocument, sceneId).toBe(true);
    }
  });

  it("heads every scene it can with a reading at the documents on disk", () => {
    for (const scheme of ["light", "dark"] as const) {
      for (const [sceneId, reports] of REPORTS_BY_SCENE) {
        if (!reports.some((report) => report.atShippedDocument)) continue;
        expect(reportsFor(sceneId, scheme)[0]?.atShippedDocument, `${scheme} / ${sceneId}`).toBe(
          true,
        );
      }
    }
  });
});

describe("primacy ranks profile, then tier, then generation", () => {
  const report = (over: Partial<CellReport>): CellReport => ({
    sceneId: "scene",
    profileKey: DARK_27,
    engine: "chromium",
    engineVersion: "0",
    renderer: "webgpu",
    samplingBackend: "gpu-texture",
    gpuAdapter: "adapter",
    tier: "texture",
    fixtureSet: "calibration",
    capturedAt: "2026-09-19T00:00:00.000Z",
    atShippedDocument: true,
    figures: [],
    ...over,
  });

  it("prefers the shipped generation where profile and tier agree", () => {
    // The state the split has not caught up with yet: a wave's capture has appended
    // a generation and the superseded one is still in the working file. Without this
    // term the head is whichever the file lists first, which is the older one.
    expect(primacy(report({}), "dark")).toBeLessThan(
      primacy(report({ atShippedDocument: false }), "dark"),
    );
  });

  it("keeps a superseded reading of this tier ahead of a current reading of another", () => {
    // The precedence, stated as an ordering rather than as three weights: the tier
    // half of the rule is about what was measured, the generation about which
    // reading of it, and a `dom` figure is the engine's `backdrop-filter` rather
    // than vitrea's shader math whatever its capture date.
    expect(primacy(report({ atShippedDocument: false }), "dark")).toBeLessThan(
      primacy(report({ tier: "dom" }), "dark"),
    );
    expect(primacy(report({ tier: "dom" }), "dark")).toBeLessThan(
      primacy(report({ profileKey: DARK_26 }), "dark"),
    );
  });

  it("reads the other scheme's profile as a foreign cell", () => {
    expect(primacy(report({}), "light")).toBeGreaterThan(primacy(report({}), "dark"));
  });
});

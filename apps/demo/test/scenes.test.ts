/**
 * `REFERENCE_SCENES` is what the picker actually offers a visitor — the
 * resolved, filtered array, not `scenes.json`'s raw scene list. Asserting
 * against the source file's text (grepping for `"state": "inactive"`, say)
 * would pass even if the filter that is supposed to withhold those rows from
 * the module's own OUTPUT silently broke, because the source file's text never
 * changes; only reading `REFERENCE_SCENES` itself, the way `Site.tsx` does,
 * catches that.
 */

import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import matrix from "../../reference-apple/scenes.json";
import { GLASS_POSITIONS } from "../src/glass-position";
import { nativeCaptureFor, nativePlatformFor, REFERENCE_SCENES } from "../src/site/scenes";

describe("REFERENCE_SCENES withholds the recovered-inactive pose", () => {
  it("declares at least one inactive scene in the source matrix", () => {
    // The fixture for this test: if scenes.json ever stopped declaring the
    // recovered-inactive pose, the assertion below would pass vacuously and
    // stop meaning anything. This keeps that failure mode visible.
    const inactiveInSource = (matrix.scenes as readonly { readonly state: string }[]).filter(
      (scene) => scene.state === "inactive",
    );
    expect(inactiveInSource.length).toBeGreaterThan(0);
  });

  it("puts none of them in the resolved picker list", () => {
    // W27c G0/G1 (claims §5.128) recovered 37 inactive scenes into the shared
    // scene matrix; `Stage` has no inactive-root wiring to show them with yet
    // (W27c G3). Selecting one from the picker before that lands would pair a
    // live active `GlassSurface` against a native capture of a receded window
    // — read as a vitrea fidelity gap that is actually a missing feature.
    const inactiveIds = new Set(
      (matrix.scenes as readonly { readonly id: string; readonly state: string }[])
        .filter((scene) => scene.state === "inactive")
        .map((scene) => scene.id),
    );
    const leaked = REFERENCE_SCENES.filter((scene) => inactiveIds.has(scene.id));
    expect(leaked.map((scene) => scene.id)).toEqual([]);
  });

  it("still shows the inactive scenes' active twins (this withholds a pose, not a background/component pair)", () => {
    // The guard is specific to the pose. An active scene sharing the same
    // background and component as a withheld inactive one must still be
    // selectable — nothing here should read as "hide the checkerboard capsule
    // button", only "hide its receded state".
    const active = REFERENCE_SCENES.find(
      (scene) => scene.id === "checkerboard__capsule-button__rest",
    );
    expect(active).toBeDefined();
  });
});

/**
 * The pair at each glass position (W43 G3 (iii), charter clause 13; claims §5.201). The page
 * builds `fixtures/<profile>/<scene>.png` paths for the position it was opened at and the build
 * copies those directories; a path with no file behind it would be a broken image where the page
 * claims a comparison, so every path the picker can produce is checked against the committed
 * captures it names.
 */
describe("the pair has a committed capture at every position it offers", () => {
  const fixtures = fileURLToPath(new URL("../../reference-apple/", import.meta.url));

  it("resolves every light scene at every position to a file that exists", () => {
    for (const glass of GLASS_POSITIONS) {
      for (const scene of REFERENCE_SCENES) {
        const path = nativeCaptureFor(scene, "light", glass);
        expect(path, `${glass} / ${scene.id}`).toMatch(new RegExp(`-glass${glass}/`));
        expect(existsSync(`${fixtures}${path ?? ""}`), `${glass} / ${scene.id}`).toBe(true);
      }
    }
  });

  it("withdraws the same dark scenes at both positions, and finds the rest", () => {
    const darkAt = (glass: (typeof GLASS_POSITIONS)[number]): readonly string[] =>
      REFERENCE_SCENES.filter((scene) => nativeCaptureFor(scene, "dark", glass) !== undefined)
        .map((scene) => scene.id);
    expect(darkAt(0.5).length).toBeGreaterThan(0);
    expect(darkAt(0.25)).toEqual(darkAt(0.5));
    for (const scene of REFERENCE_SCENES) {
      const path = nativeCaptureFor(scene, "dark", 0.25);
      if (path !== undefined) expect(existsSync(`${fixtures}${path}`), scene.id).toBe(true);
    }
  });

  it("names the position on the native panel's label", () => {
    expect(nativePlatformFor("light")).toBe("macOS 27.0, glass 0.5");
    expect(nativePlatformFor("dark", 0.25)).toBe("macOS 27.0, glass 0.25");
  });
});

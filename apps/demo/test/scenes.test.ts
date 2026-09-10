/**
 * `REFERENCE_SCENES` is what the picker actually offers a visitor — the
 * resolved, filtered array, not `scenes.json`'s raw scene list. Asserting
 * against the source file's text (grepping for `"state": "inactive"`, say)
 * would pass even if the filter that is supposed to withhold those rows from
 * the module's own OUTPUT silently broke, because the source file's text never
 * changes; only reading `REFERENCE_SCENES` itself, the way `Site.tsx` does,
 * catches that.
 */

import { describe, expect, it } from "vitest";

import matrix from "../../reference-apple/scenes.json";
import { REFERENCE_SCENES } from "../src/site/scenes";

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

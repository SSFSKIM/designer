/**
 * §Material tint — the author-facing colour axis.
 *
 * What these pin is the *composition*, not a look: the tint is a seed core
 * carries and hands on, its strength is the author's alpha, a zero-strength
 * tint is no tint at all, and the two ways a surface can be untinted (never
 * declared, or explicitly cleared) are distinguishable all the way down.
 */

import { describe, expect, it } from "vitest";

import {
  checkTintMixing,
  createDiagnosticsChannel,
  createGlassScene,
  glassTint,
  resolveMaterial,
  type GlassTint,
  type PlatformProbe,
} from "../src/index";

const orange: GlassTint = glassTint([1, 0.584, 0]);
const blue: GlassTint = glassTint([0, 0.478, 1]);

describe("glassTint", () => {
  it("defaults to fully tinted, because a colour with no alpha is an opaque colour", () => {
    expect(glassTint([1, 0, 0]).strength).toBe(1);
  });

  it("clamps every channel and the strength into range", () => {
    expect(glassTint([2, -1, 0.5], 3)).toEqual({ color: [1, 0, 0.5], strength: 1 });
    expect(glassTint([0, 0, 0], -2).strength).toBe(0);
  });
});

describe("resolveMaterial with a tint", () => {
  it("carries the seed through on both variants", () => {
    expect(resolveMaterial({ variant: "regular", tint: orange }).tint).toEqual(orange);
    expect(
      resolveMaterial({
        variant: "clear",
        dimming: { scrim: 0.3, direction: "darken" },
        tint: orange,
      }).tint,
    ).toEqual(orange);
  });

  it("leaves an untinted material with no tint key at all", () => {
    expect(resolveMaterial({ variant: "regular" })).toEqual({
      variant: "regular",
      adaptation: "adaptive",
    });
  });

  it("treats a zero-strength tint as no tint, so the untinted path stays untouched", () => {
    const resolved = resolveMaterial({ variant: "regular", tint: glassTint([1, 0, 0], 0) });
    expect(resolved.tint).toBeUndefined();
    expect(resolved).toEqual({ variant: "regular", adaptation: "adaptive" });
  });

  it("treats null as untinted — Glass.tint(nil), not inheritance", () => {
    expect(resolveMaterial({ variant: "regular", tint: null }).tint).toBeUndefined();
  });

  it("clamps a seed handed in out of range rather than trusting the caller", () => {
    expect(resolveMaterial({ variant: "regular", tint: { color: [4, 0, 0], strength: 9 } }).tint)
      .toEqual({ color: [1, 0, 0], strength: 1 });
  });

  it("keeps the tint independent of the dimming refusal, which changes the variant", () => {
    const diagnostics = createDiagnosticsChannel();
    const resolved = resolveMaterial({ variant: "clear", tint: orange, diagnostics });
    expect(resolved.variant).toBe("regular");
    expect(resolved.tint).toEqual(orange);
    expect(diagnostics.reported[0]?.code).toBe("clear-variant-needs-dimming");
  });
});

describe("checkTintMixing", () => {
  it("says nothing about untinted members, which are the ordinary case", () => {
    expect(
      checkTintMixing({
        groupId: "toolbar",
        members: [{ nodeId: "a" }, { nodeId: "b", tint: orange }, { nodeId: "c" }],
      }),
    ).toBe(false);
  });

  it("says nothing when two members ask for the same seed", () => {
    expect(
      checkTintMixing({
        groupId: "toolbar",
        members: [{ nodeId: "a", tint: orange }, { nodeId: "b", tint: { ...orange } }],
      }),
    ).toBe(false);
  });

  it("warns on two different seeds in one group, and names the fix", () => {
    const diagnostics = createDiagnosticsChannel();
    expect(
      checkTintMixing({
        groupId: "toolbar",
        members: [{ nodeId: "a", tint: orange }, { nodeId: "b", tint: blue }],
        diagnostics,
      }),
    ).toBe(true);
    const reported = diagnostics.reported[0];
    expect(reported?.code).toBe("tint-mixing");
    expect(reported?.severity).toBe("warning");
    expect(reported?.message).toContain("GlassGroup");
  });

  it("counts a strength difference as a different seed — it is a different material", () => {
    expect(
      checkTintMixing({
        groupId: "toolbar",
        members: [
          { nodeId: "a", tint: orange },
          { nodeId: "b", tint: glassTint(orange.color, 0.4) },
        ],
      }),
    ).toBe(true);
  });
});

const probe: PlatformProbe = {
  webgpu: "not-requested",
  backdropFilter: true,
  backdropProxyConformance: "pass",
  deviceHealth: "ok",
};

function sceneWith(
  nodes: readonly { readonly id: string; readonly tint?: GlassTint | null }[],
  groupTint?: GlassTint,
) {
  const diagnostics = createDiagnosticsChannel();
  const scene = createGlassScene({ platform: probe, diagnostics });
  scene.registerBackdropSource({
    id: "src",
    kind: "texture",
    probe: { taint: "clean", textureCompatibility: "compatible" },
  });
  scene.registerGlassGroup({
    id: "g",
    backdropSourceId: "src",
    material: { variant: "regular", ...(groupTint === undefined ? {} : { tint: groupTint }) },
  });
  for (const node of nodes) {
    scene.registerGlassNode({
      id: node.id,
      groupId: "g",
      shapeFamily: "fixed-rounded-rect",
      shape: { center: [0, 0], size: [40, 40], radii: [8, 8, 8, 8], smoothing: 0, thickness: 8 },
      zSlot: { plane: "base", order: 0 },
      ...(node.tint === undefined ? {} : { tint: node.tint }),
    });
  }
  return { scene, diagnostics };
}

describe("tint inheritance in the scene", () => {
  it("inherits the group's seed where a node declares none", () => {
    const { scene } = sceneWith([{ id: "a" }], orange);
    const resolved = scene.resolve().nodes.find((node) => node.nodeId === "a");
    expect(resolved?.material.tint).toEqual(orange);
  });

  it("lets a node override the group's seed", () => {
    const { scene } = sceneWith([{ id: "a", tint: blue }], orange);
    expect(scene.resolve().nodes[0]?.material.tint).toEqual(blue);
  });

  it("lets a node clear an inherited seed with null, which is not the same as absent", () => {
    const { scene } = sceneWith([{ id: "a", tint: null }], orange);
    expect(scene.resolve().nodes[0]?.material.tint).toBeUndefined();
  });

  it("reports a mixed group through the scene's own dev-mode pass", () => {
    const { scene, diagnostics } = sceneWith([
      { id: "a", tint: orange },
      { id: "b", tint: blue },
    ]);
    scene.resolve();
    expect(diagnostics.reported.map((entry) => entry.code)).toContain("tint-mixing");
  });

  it("does not report a group where one member is tinted and the rest are not", () => {
    const { scene, diagnostics } = sceneWith([
      { id: "a", tint: orange },
      { id: "b" },
      { id: "c" },
    ]);
    scene.resolve();
    expect(diagnostics.reported.map((entry) => entry.code)).not.toContain("tint-mixing");
  });
});

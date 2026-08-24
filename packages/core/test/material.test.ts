/**
 * §Material variants — `regular | clear` as a first-class axis, clear's
 * dimming-policy requirement, and the same-group mixing warning that mirrors
 * Apple's guidance.
 */

import { describe, expect, it } from "vitest";

import {
  DEFAULT_CLEAR_DIMMING,
  MATERIAL_VARIANTS,
  checkVariantMixing,
  createDiagnosticsChannel,
  resolveMaterial,
  type DimmingPolicy,
} from "../src/index";

const dimming: DimmingPolicy = { scrim: 0.3, direction: "darken" };

describe("variant vocabulary", () => {
  it("makes both variants first-class", () => {
    expect([...MATERIAL_VARIANTS]).toEqual(["regular", "clear"]);
  });

  it("ships an advisory clear dimming default, so satisfying the requirement is one line", () => {
    expect(DEFAULT_CLEAR_DIMMING.scrim).toBeGreaterThan(0);
    expect(DEFAULT_CLEAR_DIMMING.scrim).toBeLessThan(1);
    expect(DEFAULT_CLEAR_DIMMING.direction).toBe("darken");
  });
});

describe("resolveMaterial", () => {
  it("makes regular the adaptive default", () => {
    expect(resolveMaterial({ variant: "regular" })).toEqual({
      variant: "regular",
      adaptation: "adaptive",
    });
  });

  it("gives clear constrained adaptation and carries its dimming policy through", () => {
    expect(resolveMaterial({ variant: "clear", dimming })).toEqual({
      variant: "clear",
      adaptation: "constrained",
      dimming,
    });
  });

  it("ignores a dimming policy on a regular surface — it has nothing to dim", () => {
    expect(resolveMaterial({ variant: "regular", dimming })).toEqual({
      variant: "regular",
      adaptation: "adaptive",
    });
  });

  it("refuses clear without a dimming policy rather than shipping illegible glass", () => {
    const diagnostics = createDiagnosticsChannel();
    const resolved = resolveMaterial({ variant: "clear", nodeId: "n1", diagnostics });

    expect(resolved).toEqual({ variant: "regular", adaptation: "adaptive" });
    expect(diagnostics.reported[0]).toMatchObject({
      code: "clear-variant-needs-dimming",
      severity: "error",
      subjects: ["n1"],
    });
    expect(diagnostics.reported[0]?.message).toContain("DEFAULT_CLEAR_DIMMING");
  });

  it("reports the missing dimming policy once per node", () => {
    const diagnostics = createDiagnosticsChannel();

    for (let frame = 0; frame < 4; frame += 1) {
      resolveMaterial({ variant: "clear", nodeId: "n1", diagnostics });
    }

    expect(diagnostics.reported).toHaveLength(1);
  });

  it("accepts the exported default as a satisfying policy", () => {
    const diagnostics = createDiagnosticsChannel();
    const resolved = resolveMaterial({
      variant: "clear",
      dimming: DEFAULT_CLEAR_DIMMING,
      diagnostics,
    });

    expect(resolved.variant).toBe("clear");
    expect(diagnostics.reported).toHaveLength(0);
  });
});

describe("same-group variant mixing", () => {
  it("says nothing when a group is all regular", () => {
    const diagnostics = createDiagnosticsChannel();
    const mixed = checkVariantMixing({
      groupId: "toolbar",
      members: [
        { nodeId: "a", variant: "regular" },
        { nodeId: "b", variant: "regular" },
      ],
      diagnostics,
    });

    expect(mixed).toBe(false);
    expect(diagnostics.reported).toHaveLength(0);
  });

  it("says nothing when a group is all clear", () => {
    const diagnostics = createDiagnosticsChannel();
    const mixed = checkVariantMixing({
      groupId: "platter",
      members: [
        { nodeId: "a", variant: "clear" },
        { nodeId: "b", variant: "clear" },
      ],
      diagnostics,
    });

    expect(mixed).toBe(false);
    expect(diagnostics.reported).toHaveLength(0);
  });

  it("warns — not errors — when variants are mixed, naming the group and its nodes", () => {
    const diagnostics = createDiagnosticsChannel();
    const mixed = checkVariantMixing({
      groupId: "toolbar",
      members: [
        { nodeId: "a", variant: "regular" },
        { nodeId: "b", variant: "clear" },
      ],
      diagnostics,
    });

    expect(mixed).toBe(true);
    expect(diagnostics.reported[0]).toMatchObject({
      code: "variant-mixing",
      severity: "warning",
      subjects: ["toolbar"],
    });
    expect(diagnostics.reported[0]?.message).toContain("a");
    expect(diagnostics.reported[0]?.message).toContain("b");
  });

  it("does not coerce the mixed nodes — the author's intent survives the warning", () => {
    const members = [
      { nodeId: "a", variant: "regular" },
      { nodeId: "b", variant: "clear" },
    ] as const;

    checkVariantMixing({ groupId: "toolbar", members });

    expect(members.map((member) => member.variant)).toEqual(["regular", "clear"]);
  });

  it("warns once per group, however many frames the mixing survives", () => {
    const diagnostics = createDiagnosticsChannel();
    const members = [
      { nodeId: "a", variant: "regular" },
      { nodeId: "b", variant: "clear" },
    ] as const;

    for (let frame = 0; frame < 3; frame += 1) {
      checkVariantMixing({ groupId: "toolbar", members, diagnostics });
    }

    expect(diagnostics.reported).toHaveLength(1);
  });

  it("handles a group with nothing in it, and one with a single member", () => {
    expect(checkVariantMixing({ groupId: "g", members: [] })).toBe(false);
    expect(checkVariantMixing({ groupId: "g", members: [{ nodeId: "a", variant: "clear" }] })).toBe(
      false,
    );
  });
});

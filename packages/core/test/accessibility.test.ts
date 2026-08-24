/**
 * §Accessibility policy — the behavior table, read back as tests.
 *
 * The spec states four rows in prose. Each row below quotes that prose in its
 * test name, so a reader can diff this file against §Accessibility line by line
 * and see whether the table still says what the spec says.
 */

import { describe, expect, it } from "vitest";

import {
  ACCESSIBILITY_BEHAVIOR_TABLE,
  ACCESSIBILITY_FLAGS,
  ACCESSIBILITY_PRECEDENCE,
  NOMINAL_ACCESSIBILITY_POLICY,
  OVERRIDABLE_ACCESSIBILITY_FLAGS,
  resolveAccessibilityPolicy,
  type AccessibilityOverride,
  type AccessibilityOverrides,
  type OverridableAccessibilityFlag,
  type ResolvedMotionPolicy,
  type SystemAccessibilityPreferences,
} from "../src/accessibility";
import { createDiagnosticsChannel } from "../src/diagnostics";

/** Nothing detected, and this platform can answer every query it is asked. */
const NOTHING_DETECTED: SystemAccessibilityPreferences = {
  reducedTransparency: false,
  reducedMotion: false,
  increasedContrast: false,
  forcedColors: false,
  reducedTransparencySupported: true,
};

const systemOf = (
  detected: Partial<SystemAccessibilityPreferences>,
): SystemAccessibilityPreferences => ({ ...NOTHING_DETECTED, ...detected });

/**
 * A one-flag override object. Built by assignment rather than a computed key so
 * the union-typed flag keeps its literal key type.
 */
const overrideOne = (
  flag: OverridableAccessibilityFlag,
  value: AccessibilityOverride,
): AccessibilityOverrides => {
  const overrides: { -readonly [K in OverridableAccessibilityFlag]?: AccessibilityOverride } = {};
  overrides[flag] = value;
  return overrides;
};

/** All 2^4 combinations of what a platform can detect. */
const everyFlagCombination = (): readonly SystemAccessibilityPreferences[] =>
  Array.from({ length: 1 << ACCESSIBILITY_FLAGS.length }, (_unused, mask) =>
    systemOf({
      reducedTransparency: (mask & 0b0001) !== 0,
      reducedMotion: (mask & 0b0010) !== 0,
      increasedContrast: (mask & 0b0100) !== 0,
      forcedColors: (mask & 0b1000) !== 0,
    }),
  );

const label = (system: SystemAccessibilityPreferences): string => {
  const on = ACCESSIBILITY_FLAGS.filter((flag) => system[flag]);
  return on.length === 0 ? "nothing detected" : on.join(" + ");
};

const REDUCED_MOTION_CONSEQUENCES: ResolvedMotionPolicy = {
  overshoot: "none",
  deformation: "none",
  shimmer: "none",
  morph: "non-elastic",
  crossfade: "large-plane-shifts",
  positionalContinuity: true,
};

describe("the §Accessibility behavior table, row by row", () => {
  it("reduced transparency → more frosted, less refraction, higher occlusion", () => {
    const { material } = resolveAccessibilityPolicy(systemOf({ reducedTransparency: true }));

    expect(material.frost).toBe("increased");
    expect(material.refraction).toBe("reduced");
    expect(material.occlusion).toBe("increased");
    // "less refraction", not "no refraction", and the glass body survives:
    // the spec frosts the material, it does not remove it.
    expect(material.glass).toBe("material");
    expect(material.colorSource).toBe("material");
  });

  it("increased contrast → stronger borders, near-monochrome foregrounds, reduced ambient tint", () => {
    const { material } = resolveAccessibilityPolicy(systemOf({ increasedContrast: true }));

    expect(material.border).toBe("strong");
    expect(material.foreground).toBe("near-monochrome");
    expect(material.ambientTint).toBe("reduced");
    // Contrast says nothing about frosting or lensing — those axes stay nominal.
    expect(material.frost).toBe("nominal");
    expect(material.refraction).toBe("nominal");
    expect(material.glass).toBe("material");
  });

  it("forced-colors → system colors, borders, no glass", () => {
    const { material } = resolveAccessibilityPolicy(systemOf({ forcedColors: true }));

    expect(material.colorSource).toBe("system");
    expect(material.border).toBe("strong");
    expect(material.glass).toBe("none");
    // No glass leaves nothing to frost, lens, or tint, and the flat system fill
    // hides the backdrop completely.
    expect(material.frost).toBe("none");
    expect(material.refraction).toBe("none");
    expect(material.ambientTint).toBe("none");
    expect(material.occlusion).toBe("opaque");
    expect(material.foreground).toBe("near-monochrome");
  });

  it("reduced motion → removes elastic overshoot, deformation, and shimmer travel; keeps direct-manipulation positional continuity; shortens morphs to non-elastic interpolation; reserves crossfade for large plane shifts", () => {
    const { motion, material } = resolveAccessibilityPolicy(systemOf({ reducedMotion: true }));

    expect(motion.overshoot).toBe("none");
    expect(motion.deformation).toBe("none");
    expect(motion.shimmer).toBe("none");
    expect(motion.positionalContinuity).toBe(true);
    expect(motion.morph).toBe("non-elastic");
    expect(motion.crossfade).toBe("large-plane-shifts");
    // Reduced Motion is a motion row: the material is untouched.
    expect(material).toEqual(NOMINAL_ACCESSIBILITY_POLICY.material);
  });
});

describe("the table's shape", () => {
  it("has exactly one row per flag, and no fifth flag", () => {
    expect(Object.keys(ACCESSIBILITY_BEHAVIOR_TABLE).sort()).toEqual(
      [...ACCESSIBILITY_FLAGS].sort(),
    );
  });

  it("keeps reduced motion the only motion row and the other three material-only", () => {
    expect(ACCESSIBILITY_BEHAVIOR_TABLE.reducedMotion.motion).toBeDefined();
    expect(ACCESSIBILITY_BEHAVIOR_TABLE.reducedMotion.material).toBeUndefined();

    for (const flag of ["reducedTransparency", "increasedContrast", "forcedColors"] as const) {
      expect(ACCESSIBILITY_BEHAVIOR_TABLE[flag].material).toBeDefined();
      expect(ACCESSIBILITY_BEHAVIOR_TABLE[flag].motion).toBeUndefined();
    }
  });

  it("orders every flag exactly once, forced-colors last so it wins", () => {
    expect([...ACCESSIBILITY_PRECEDENCE].sort()).toEqual([...ACCESSIBILITY_FLAGS].sort());
    expect(new Set(ACCESSIBILITY_PRECEDENCE).size).toBe(ACCESSIBILITY_PRECEDENCE.length);
    expect(ACCESSIBILITY_PRECEDENCE.at(-1)).toBe("forcedColors");
  });
});

describe("every system flag combination", () => {
  for (const system of everyFlagCombination()) {
    it(`holds every invariant with ${label(system)}`, () => {
      const policy = resolveAccessibilityPolicy(system);

      // The resolved booleans mirror what the platform detected.
      expect({
        reducedTransparency: policy.reducedTransparency,
        reducedMotion: policy.reducedMotion,
        increasedContrast: policy.increasedContrast,
        forcedColors: policy.forcedColors,
      }).toEqual({
        reducedTransparency: system.reducedTransparency,
        reducedMotion: system.reducedMotion,
        increasedContrast: system.increasedContrast,
        forcedColors: system.forcedColors,
      });

      // (a) Reduced Motion keeps direct-manipulation positional continuity
      // (§Motion), so it is an invariant of every row, not a setting.
      expect(policy.motion.positionalContinuity).toBe(true);

      // (b) forced-colors is the strongest row: no glass and system colors
      // whatever else is on.
      if (system.forcedColors) {
        expect(policy.material).toEqual({
          glass: "none",
          colorSource: "system",
          frost: "none",
          refraction: "none",
          occlusion: "opaque",
          border: "strong",
          ambientTint: "none",
          foreground: "near-monochrome",
        });
      } else {
        // (c) reduced transparency and increased contrast touch disjoint axes,
        // so both sets of consequences apply together.
        expect(policy.material).toEqual({
          glass: "material",
          colorSource: "material",
          frost: system.reducedTransparency ? "increased" : "nominal",
          refraction: system.reducedTransparency ? "reduced" : "nominal",
          occlusion: system.reducedTransparency ? "increased" : "nominal",
          border: system.increasedContrast ? "strong" : "nominal",
          ambientTint: system.increasedContrast ? "reduced" : "nominal",
          foreground: system.increasedContrast ? "near-monochrome" : "adaptive",
        });
      }

      // Motion follows reduced motion alone — no material row reaches into it.
      expect(policy.motion).toEqual(
        system.reducedMotion ? REDUCED_MOTION_CONSEQUENCES : NOMINAL_ACCESSIBILITY_POLICY.motion,
      );
    });
  }
});

describe("override precedence", () => {
  for (const flag of OVERRIDABLE_ACCESSIBILITY_FLAGS) {
    it(`${flag}: explicit false suppresses a system true, explicit true forces a system false`, () => {
      for (const system of everyFlagCombination()) {
        expect(resolveAccessibilityPolicy(system, overrideOne(flag, false))[flag]).toBe(false);
        expect(resolveAccessibilityPolicy(system, overrideOne(flag, true))[flag]).toBe(true);
        expect(resolveAccessibilityPolicy(system, overrideOne(flag, "system"))[flag]).toBe(
          system[flag],
        );
        expect(resolveAccessibilityPolicy(system)[flag]).toBe(system[flag]);
      }
    });
  }

  it("carries an override through to the material and motion consequences", () => {
    expect(
      resolveAccessibilityPolicy(NOTHING_DETECTED, { reducedTransparency: true }).material.frost,
    ).toBe("increased");
    expect(
      resolveAccessibilityPolicy(systemOf({ reducedMotion: true }), { reducedMotion: false }).motion,
    ).toEqual(NOMINAL_ACCESSIBILITY_POLICY.motion);
    expect(
      resolveAccessibilityPolicy(systemOf({ increasedContrast: true }), {
        increasedContrast: false,
      }).material,
    ).toEqual(NOMINAL_ACCESSIBILITY_POLICY.material);
  });

  it("has no forced-colors override — an OS mandate is not an app's to overrule", () => {
    const overrides: AccessibilityOverrides = {
      // @ts-expect-error forcedColors is deliberately absent from AccessibilityOverrides (§Accessibility policy).
      forcedColors: false,
    };

    expect(
      resolveAccessibilityPolicy(systemOf({ forcedColors: true }), overrides).forcedColors,
    ).toBe(true);
    expect([...OVERRIDABLE_ACCESSIBILITY_FLAGS]).not.toContain("forcedColors");
  });
});

describe("the undetectable-reduced-transparency diagnostic", () => {
  const undetectable = systemOf({ reducedTransparencySupported: false });

  it("warns when the prop is left on the system a platform cannot query", () => {
    const diagnostics = createDiagnosticsChannel();

    resolveAccessibilityPolicy(undetectable, undefined, diagnostics);

    expect(diagnostics.reported).toHaveLength(1);
    expect(diagnostics.reported[0]?.code).toBe("reduced-transparency-undetectable");
    expect(diagnostics.reported[0]?.severity).toBe("warning");
    expect(diagnostics.reported[0]?.message).toContain("reducedTransparency");
  });

  it('warns the same way for the explicit "system" override', () => {
    const diagnostics = createDiagnosticsChannel();

    resolveAccessibilityPolicy(undetectable, { reducedTransparency: "system" }, diagnostics);

    expect(diagnostics.reported).toHaveLength(1);
  });

  it("stays silent for an explicit boolean override — the app already did the right thing", () => {
    for (const value of [true, false] as const) {
      const diagnostics = createDiagnosticsChannel();

      resolveAccessibilityPolicy(undetectable, { reducedTransparency: value }, diagnostics);

      expect(diagnostics.reported).toEqual([]);
    }
  });

  it("stays silent when the platform says the query is supported", () => {
    for (const system of everyFlagCombination()) {
      const diagnostics = createDiagnosticsChannel();

      resolveAccessibilityPolicy(system, undefined, diagnostics);

      expect(diagnostics.reported).toEqual([]);
    }
  });

  it("warns whatever the detected value is — the finding is about the configuration", () => {
    for (const detected of [true, false] as const) {
      const diagnostics = createDiagnosticsChannel();

      resolveAccessibilityPolicy(
        systemOf({ reducedTransparency: detected, reducedTransparencySupported: false }),
        undefined,
        diagnostics,
      );

      expect(diagnostics.reported).toHaveLength(1);
    }
  });

  it("resolves the same policy with or without a channel — reporting is a side channel", () => {
    const diagnostics = createDiagnosticsChannel();

    expect(resolveAccessibilityPolicy(undetectable, undefined, diagnostics)).toEqual(
      resolveAccessibilityPolicy(undetectable),
    );
  });
});

describe("determinism", () => {
  it("resolves the nominal policy when nothing is detected", () => {
    expect(resolveAccessibilityPolicy(NOTHING_DETECTED)).toEqual(NOMINAL_ACCESSIBILITY_POLICY);
  });

  it("returns a deep-equal but fresh policy for the same inputs", () => {
    const overrides: AccessibilityOverrides = { reducedMotion: "system", increasedContrast: true };

    for (const system of everyFlagCombination()) {
      const first = resolveAccessibilityPolicy(system, overrides);
      const second = resolveAccessibilityPolicy(system, overrides);

      expect(first).toEqual(second);
      expect(first).not.toBe(second);
    }
  });

  it("never mutates the nominal policy it folds over", () => {
    const before = structuredClone(NOMINAL_ACCESSIBILITY_POLICY);

    for (const system of everyFlagCombination()) {
      resolveAccessibilityPolicy(system, {
        reducedTransparency: true,
        reducedMotion: true,
        increasedContrast: true,
      });
    }

    expect(NOMINAL_ACCESSIBILITY_POLICY).toEqual(before);
  });
});

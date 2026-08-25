/**
 * The seam between a recorded measurement and a running renderer.
 *
 * §Calibration's rule is that the delegated unknowns are "named here, answered
 * by the harness, recorded into calibration profiles". C9a's answers live in
 * `profiles/apple-macos-26.5-1x-*.json`, and the whole point of recording them
 * is that the runtime carries the same numbers. Nothing enforces that on its
 * own: the renderer's defaults are TypeScript and the profile is JSON, so the two
 * can drift apart in either direction with nothing to notice.
 *
 * These tests are what notices. They deliberately do NOT make the runtime read
 * the JSON at run time — a published package that loads a calibration file would
 * be shipping a data dependency for a number that never changes between releases,
 * and X7 keeps the published surface to two packages with bundled internals.
 * Instead the profile is the authority, the renderer's default mirrors the one
 * profile it targets, and the mirror is pinned here.
 *
 * The other thing pinned here is the shape of the patches: they have to remain
 * applicable to the real `withMaterialOverrides`, because a profile that no
 * longer type-checks against the renderer is a recorded measurement nobody can
 * apply.
 */

import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import {
  DEFAULT_MATERIAL_PROFILE,
  withMaterialOverrides,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

interface TunedProfile {
  readonly profileKey: string;
  readonly colorSpace: string;
  readonly patch: MaterialProfilePatch;
  readonly identityWithRuntimeDefault?: boolean;
  readonly measurement: {
    readonly objectiveBefore: number;
    readonly objectiveAfter: number;
    readonly cellsUsedForFitting: number;
  };
  readonly entries: Readonly<Record<string, { readonly status: string }>>;
}

const PROFILES = resolve(import.meta.dirname, "..", "profiles");

function load(key: string): TunedProfile {
  return JSON.parse(readFileSync(resolve(PROFILES, `${key}.json`), "utf8")) as TunedProfile;
}

const LIGHT = load("apple-macos-26.5-1x-light-standard");
const DARK = load("apple-macos-26.5-1x-dark-standard");

describe("tuned calibration profiles", () => {
  it("carry the profile key they are named for, in the locked colour space", () => {
    expect(LIGHT.profileKey).toBe("apple-macos-26.5-1x-light-standard");
    expect(DARK.profileKey).toBe("apple-macos-26.5-1x-dark-standard");
    // X5 locks v1 calibration to sRGB; a number measured in another space is not
    // comparable to anything else in the pipeline.
    expect(LIGHT.colorSpace).toBe("srgb");
    expect(DARK.colorSpace).toBe("srgb");
  });

  it("pins the runtime default to the light-standard profile", () => {
    // The claim the light profile makes about itself. If someone retunes the
    // renderer's defaults without re-recording, or re-records without retuning,
    // this is the test that fails.
    expect(LIGHT.identityWithRuntimeDefault).toBe(true);
    const applied = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, LIGHT.patch);
    expect(applied).toEqual(DEFAULT_MATERIAL_PROFILE);
  });

  it("records the measured light-scheme tint alpha, not the advisory one", () => {
    // Named explicitly rather than only through the identity above, so the one
    // number C9a actually moved is legible in the test as well as in the profile.
    expect(LIGHT.patch.optics?.regular?.tintAlpha).toBe(0.62);
    expect(DEFAULT_MATERIAL_PROFILE.optics.regular.tintAlpha).toBe(0.62);
  });

  it("leaves the backdrop tint crossover inert by default", () => {
    // The measured finding: the reference keys its tint on the colour scheme, not
    // on the backdrop behind it. Both ends equal means the crossover cannot fire.
    expect(DEFAULT_MATERIAL_PROFILE.adaptiveTintDark).toEqual(
      DEFAULT_MATERIAL_PROFILE.adaptiveTintLight,
    );
  });

  it("applies the dark patch as a real change, and only where it claims to", () => {
    const dark = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, DARK.patch);
    expect(dark).not.toEqual(DEFAULT_MATERIAL_PROFILE);
    expect(dark.optics.regular.tintAlpha).toBe(0.97);
    expect(dark.optics.regular.tint).toEqual([0.05, 0.05, 0.05]);
    expect(dark.adaptiveTintDark).toEqual(dark.adaptiveTintLight);

    // A patch names leaves; it must not quietly drop their siblings. These are
    // the constants the dark profile explicitly declines to retune, and they have
    // to survive the merge for that declining to mean anything.
    expect(dark.optics.regular.blurSigma).toBe(DEFAULT_MATERIAL_PROFILE.optics.regular.blurSigma);
    expect(dark.optics.regular.rimAlpha).toBe(DEFAULT_MATERIAL_PROFILE.optics.regular.rimAlpha);
    expect(dark.optics.regular.specularGain).toBe(
      DEFAULT_MATERIAL_PROFILE.optics.regular.specularGain,
    );
    expect(dark.optics.clear).toEqual(DEFAULT_MATERIAL_PROFILE.optics.clear);
  });

  it("states an improvement on the objective it was fitted against", () => {
    for (const profile of [LIGHT, DARK]) {
      expect(profile.measurement.objectiveAfter).toBeLessThan(profile.measurement.objectiveBefore);
      expect(profile.measurement.cellsUsedForFitting).toBeGreaterThan(0);
    }
  });

  it("gives every entry a status from the closed set the profiles use", () => {
    // An entry with an unrecognised status is a number whose provenance nobody
    // has to read — which is the failure the seed profile's status field exists
    // to prevent. `declined` and `not-discriminating` are outcomes, not gaps.
    const allowed = new Set([
      "measured",
      "measured-with-a-caveat",
      "unchanged-deliberately",
      "not-discriminating",
      "not-discriminable",
      "not-retuned",
      "unmeasurable-as-specified",
      "declined",
    ]);
    for (const profile of [LIGHT, DARK]) {
      for (const [name, entry] of Object.entries(profile.entries)) {
        expect(allowed, `${profile.profileKey} / ${name}`).toContain(entry.status);
      }
    }
  });
});

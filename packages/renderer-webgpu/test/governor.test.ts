/**
 * The governor's knobs, and the one refusal in them.
 *
 * Decision Log #20 makes family C — the un-normalised `rsup` field, the ladder's
 * first step — conditional on C6 running the f32 cross-check on its WGSL. A knob
 * that shipped an unverified family because nobody said no would be the exact
 * failure the condition exists to prevent, so the refusal is default-on and has
 * to be unlocked explicitly.
 */

import { describe, expect, it } from "vitest";

import { createGovernor, GOVERNOR_LADDER, NOMINAL_GOVERNOR } from "../src/governor";

describe("the governor's knobs", () => {
  it("starts at full fidelity and core's advisory readback ceiling", () => {
    const governor = createGovernor();
    expect(governor.knobs).toEqual(NOMINAL_GOVERNOR);
    // 15 Hz is §Foreground adaptation's cap, ratified as Decision Log #19.
    expect(governor.knobs.adaptationCadenceHz).toBe(15);
    expect(governor.knobs.refractionResolutionScale).toBe(1);
  });

  it("refuses family C until the f32 cross-check is recorded", () => {
    const governor = createGovernor();

    expect(governor.familyCVerified).toBe(false);
    expect(governor.set({ fieldFamily: "rsup" }).fieldFamily).toBe("rsupn");

    governor.recordFamilyCVerified();
    expect(governor.set({ fieldFamily: "rsup" }).fieldFamily).toBe("rsup");
  });

  it("accepts family C when the caller states the check already passed", () => {
    const governor = createGovernor({ familyCVerified: true });
    expect(governor.set({ fieldFamily: "rsup" }).fieldFamily).toBe("rsup");
  });

  it("walks the suggested ladder, weakest visual cost first", () => {
    const governor = createGovernor({ familyCVerified: true });

    // Step 1 is the field family alone: one uniform and one pipeline, no
    // resolution change, so nothing resamples as it engages.
    const step1 = governor.setLevel(1);
    expect(step1.fieldFamily).toBe("rsup");
    expect(step1.refractionResolutionScale).toBe(1);

    const step2 = governor.setLevel(2);
    expect(step2.refractionResolutionScale).toBeLessThan(1);
    expect(step2.adaptationCadenceHz).toBeLessThan(15);
  });

  it("clamps a ladder index instead of returning undefined knobs", () => {
    const governor = createGovernor({ familyCVerified: true });
    expect(governor.setLevel(-5)).toEqual(GOVERNOR_LADDER[0]);
    expect(governor.setLevel(99)).toEqual(GOVERNOR_LADDER[GOVERNOR_LADDER.length - 1]);
  });

  it("keeps the resolution scale inside a range that still renders", () => {
    const governor = createGovernor();
    expect(governor.set({ refractionResolutionScale: 4 }).refractionResolutionScale).toBe(1);
    expect(governor.set({ refractionResolutionScale: 0 }).refractionResolutionScale).toBeGreaterThan(0);
  });

  it("treats a zero cadence as 'no adaptation', not as an error", () => {
    const governor = createGovernor();
    expect(governor.set({ adaptationCadenceHz: 0 }).adaptationCadenceHz).toBe(0);
    expect(governor.set({ adaptationCadenceHz: -3 }).adaptationCadenceHz).toBe(0);
  });

  it("reports every change, so core's policy can log what it turned", () => {
    const seen: string[] = [];
    const governor = createGovernor({
      familyCVerified: true,
      onChange: (knobs) => seen.push(knobs.fieldFamily),
    });

    governor.setLevel(1);
    governor.reset();

    expect(seen).toEqual(["rsup", "rsupn"]);
  });

  it("has a ladder whose every rung is a real change from the one before", () => {
    for (let i = 1; i < GOVERNOR_LADDER.length; i += 1) {
      expect(GOVERNOR_LADDER[i]).not.toEqual(GOVERNOR_LADDER[i - 1]);
    }
    expect(GOVERNOR_LADDER[0]).toEqual(NOMINAL_GOVERNOR);
  });
});

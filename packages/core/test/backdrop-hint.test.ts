/**
 * X6 — the hint contract. One mechanism (an author-declared `backdrop` or an
 * estimator provider), never implied to be pixel analysis.
 */

import { describe, expect, it } from "vitest";

import {
  createDiagnosticsChannel,
  resolveBackdropHint,
  type BackdropEstimatorProvider,
  type BackdropHint,
} from "../src/index";

const estimator = (hint: BackdropHint | undefined): BackdropEstimatorProvider => ({
  kind: "estimator",
  id: "test-estimator",
  estimate: () => hint,
});

describe("resolveBackdropHint (X6)", () => {
  it("reports no hint mechanism when the app configured neither", () => {
    expect(resolveBackdropHint({ groupId: "g1" })).toEqual({ availability: "none" });
  });

  it("takes an author-declared hint", () => {
    const resolved = resolveBackdropHint({ groupId: "g1", backdrop: { tone: "dark" } });

    expect(resolved).toEqual({ availability: "author-hint", hint: { tone: "dark" } });
  });

  it("takes an estimator's hint and labels it as an estimate, not analysis", () => {
    const resolved = resolveBackdropHint({
      groupId: "g1",
      estimator: estimator({ tone: "light", luminance: 0.9 }),
    });

    expect(resolved.availability).toBe("estimator");
    expect(resolved.hint).toEqual({ tone: "light", luminance: 0.9 });
  });

  it("falls back to no hint when an estimator declines to estimate", () => {
    const resolved = resolveBackdropHint({ groupId: "g1", estimator: estimator(undefined) });

    expect(resolved).toEqual({ availability: "none" });
  });

  it("passes the group id to the estimator, so one provider can serve many groups", () => {
    const seen: string[] = [];
    resolveBackdropHint({
      groupId: "toolbar",
      estimator: {
        kind: "estimator",
        id: "spy",
        estimate: (groupId) => {
          seen.push(groupId);
          return { tone: "mixed" };
        },
      },
    });

    expect(seen).toEqual(["toolbar"]);
  });

  it("lets an explicit hint win over an estimator, and says so once", () => {
    const diagnostics = createDiagnosticsChannel();
    const resolved = resolveBackdropHint({
      groupId: "g1",
      backdrop: { tone: "dark" },
      estimator: estimator({ tone: "light" }),
      diagnostics,
    });

    expect(resolved.availability).toBe("author-hint");
    expect(resolved.hint).toEqual({ tone: "dark" });
    expect(diagnostics.reported).toHaveLength(1);
    expect(diagnostics.reported[0]).toMatchObject({
      code: "backdrop-hint-redundant-estimator",
      severity: "warning",
      subjects: ["g1"],
    });
  });

  it("clamps an out-of-range luminance and complexity, reporting each group once", () => {
    const diagnostics = createDiagnosticsChannel();
    const resolved = resolveBackdropHint({
      groupId: "g1",
      backdrop: { tone: "light", luminance: 1.4, complexity: -0.2 },
      diagnostics,
    });

    expect(resolved.hint).toEqual({ tone: "light", luminance: 1, complexity: 0 });
    expect(diagnostics.reported).toHaveLength(1);
    expect(diagnostics.reported[0]).toMatchObject({
      code: "backdrop-hint-out-of-range",
      severity: "warning",
    });
  });

  it("leaves an in-range hint untouched and reports nothing", () => {
    const diagnostics = createDiagnosticsChannel();
    const resolved = resolveBackdropHint({
      groupId: "g1",
      backdrop: { tone: "mixed", luminance: 0, complexity: 1 },
      diagnostics,
    });

    expect(resolved.hint).toEqual({ tone: "mixed", luminance: 0, complexity: 1 });
    expect(diagnostics.reported).toHaveLength(0);
  });

  it("drops a non-finite number rather than clamping a meaningless one", () => {
    const diagnostics = createDiagnosticsChannel();
    const resolved = resolveBackdropHint({
      groupId: "g1",
      backdrop: { tone: "dark", luminance: Number.NaN },
      diagnostics,
    });

    expect(resolved.hint).toEqual({ tone: "dark" });
    expect(diagnostics.reported[0]?.code).toBe("backdrop-hint-out-of-range");
  });

  it("maps cleanly onto the capability resolver's hint axis", () => {
    expect(resolveBackdropHint({ groupId: "g" }).availability).toBe("none");
    expect(resolveBackdropHint({ groupId: "g", backdrop: { tone: "dark" } }).availability).toBe(
      "author-hint",
    );
    expect(
      resolveBackdropHint({ groupId: "g", estimator: estimator({ tone: "dark" }) }).availability,
    ).toBe("estimator");
  });
});

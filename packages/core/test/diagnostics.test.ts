import { describe, expect, it, vi } from "vitest";

import { DIAGNOSTIC_CODES, createDiagnosticsChannel, type Diagnostic } from "../src/index";

const overlap = (subjects: readonly string[]): Diagnostic => ({
  code: "same-plane-overlap",
  severity: "error",
  subjects,
  message: `overlap: ${subjects.join(" and ")}`,
});

describe("diagnostics channel", () => {
  it("forwards every diagnostic to the host sink", () => {
    const sink = vi.fn();
    const channel = createDiagnosticsChannel({ sink });

    channel.report(overlap(["a", "b"]));

    expect(sink).toHaveBeenCalledTimes(1);
    expect(sink.mock.calls[0]?.[0]).toMatchObject({
      code: "same-plane-overlap",
      severity: "error",
    });
  });

  it("retains what it reported so a host can read it after the fact", () => {
    const channel = createDiagnosticsChannel();

    channel.report(overlap(["a", "b"]));

    expect(channel.reported).toHaveLength(1);
    expect(channel.reported[0]?.message).toBe("overlap: a and b");
  });

  it("reports a repeated diagnostic once — a per-frame check must not spam", () => {
    const sink = vi.fn();
    const channel = createDiagnosticsChannel({ sink });

    channel.report(overlap(["a", "b"]));
    channel.report(overlap(["a", "b"]));
    channel.report(overlap(["a", "b"]));

    expect(sink).toHaveBeenCalledTimes(1);
    expect(channel.reported).toHaveLength(1);
  });

  it("treats a different subject set as a different diagnostic", () => {
    const channel = createDiagnosticsChannel();

    channel.report(overlap(["a", "b"]));
    channel.report(overlap(["a", "c"]));

    expect(channel.reported).toHaveLength(2);
  });

  it("re-reports after clear(), so a fixed-then-broken condition is visible again", () => {
    const sink = vi.fn();
    const channel = createDiagnosticsChannel({ sink });

    channel.report(overlap(["a", "b"]));
    channel.clear();
    channel.report(overlap(["a", "b"]));

    expect(sink).toHaveBeenCalledTimes(2);
    expect(channel.reported).toHaveLength(1);
  });

  it("can keep every repeat when a host asks for the raw stream", () => {
    const channel = createDiagnosticsChannel({ dedupe: false });

    channel.report(overlap(["a", "b"]));
    channel.report(overlap(["a", "b"]));

    expect(channel.reported).toHaveLength(2);
  });

  it("enumerates the codes core can emit, with no duplicates", () => {
    expect(new Set(DIAGNOSTIC_CODES).size).toBe(DIAGNOSTIC_CODES.length);
    expect([...DIAGNOSTIC_CODES]).toContain("variant-mixing");
    expect([...DIAGNOSTIC_CODES]).toContain("frame-phase-violation");
  });
});

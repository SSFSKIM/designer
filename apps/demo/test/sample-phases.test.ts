/**
 * What a sample phase actually records, held to tests that need no browser.
 *
 * The stamp a phase carries is easy to over-read. One phase drives a whole batch
 * of labels — a scenario's families are measured one after another inside a single
 * `atSamplePhases` callback — and every row of that batch is handed the same phase
 * object. So the stamp is the moment the batch *began*, not the moment each label
 * was captured; the last label of a slow batch is read some way after it. These
 * tests pin that reading, because a field called something else would invite a
 * record to claim a per-label precision the instrument does not have.
 */

import { afterEach, describe, expect, it, vi } from "vitest";
import type { Page } from "@playwright/test";

import { SAMPLE_DELAYS, atSamplePhases, type SamplePhase } from "../e2e/glass-contrast";

/**
 * A page that only knows how to wait, and waits by moving the fake clock — so the
 * arithmetic under test is exercised against time rather than against a stub of it.
 */
const clockPage = (): Page =>
  ({
    waitForTimeout: (ms: number): Promise<void> => {
      vi.advanceTimersByTime(ms);
      return Promise.resolve();
    },
  }) as unknown as Page;

afterEach(() => {
  vi.useRealTimers();
});

const collect = async (spend: (index: number) => number = () => 0): Promise<SamplePhase[]> => {
  vi.useFakeTimers();
  const seen: SamplePhase[] = [];
  await atSamplePhases(clockPage(), (phase) => {
    seen.push(phase);
    vi.advanceTimersByTime(spend(seen.length - 1));
    return Promise.resolve();
  });
  return seen;
};

describe("the phases a scenario is sampled at", () => {
  it("visits every declared offset, in the order they were declared", async () => {
    const seen = await collect();
    expect(seen.map((phase) => phase.scheduledMs)).toEqual(SAMPLE_DELAYS);
  });

  it("stamps the offset the batch began at, which on an idle page is the one asked for", async () => {
    const seen = await collect();
    expect(seen.map((phase) => phase.batchStartedMs)).toEqual(SAMPLE_DELAYS);
  });

  it("stamps a batch's start, not its end, so a slow batch does not backdate the next", async () => {
    // The first batch spends 600 ms reading its labels. The second still begins at
    // its own absolute offset, and says so.
    const seen = await collect((index) => (index === 0 ? 600 : 0));
    expect(seen[0]?.batchStartedMs).toBe(400);
    expect(seen[1]?.batchStartedMs).toBe(2_200);
  });

  it("reports the start really reached once measuring has overrun the offset", async () => {
    // A batch that takes three seconds pushes the next one past the offset it names.
    // The stamp is the reading, not the schedule: nothing here rounds back to 2,200.
    const seen = await collect((index) => (index === 0 ? 3_000 : 0));
    expect(seen[1]?.scheduledMs).toBe(2_200);
    expect(seen[1]?.batchStartedMs).toBe(3_400);
  });
});

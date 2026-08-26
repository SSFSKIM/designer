/**
 * The startup conformance probe, in three layers — and one honest gap.
 *
 * S1's Q5 is the reason this file has the shape it has: **no pixel oracle for
 * `backdrop-filter` exists in any engine, by any interoperable means.** Four
 * candidate oracles were measured closed (`CSS.supports` answers true where
 * rendering is a no-op; computed-style readback round-trips unrenderable values
 * unchanged in all three engines; the offscreen SVG/`foreignObject` construction
 * rasterises and reads back but structurally cannot see the host page's
 * backdrop; every other readback path is closed by spec or by permission). So:
 *
 * | layer | what it sees | what it cannot |
 * | --- | --- | --- |
 * | 1 support gate | the property is absent altogether | anything about rendering |
 * | 2 backdrop-root audit | app CSS re-rooting the proxy's backdrop | engine behaviour |
 * | 3 conformance table | known engine/version behaviour | unknown versions, and per-environment suppression |
 *
 * The gap is stated rather than papered over. A blocklisted GPU, forced software
 * rasterisation, a remote-desktop pipeline or an OS transparency setting can
 * suppress `backdrop-filter` on an engine and version that otherwise supports
 * it, invisibly from inside the page — S1 measured this machine as a live
 * instance of exactly that class. Two things follow, and both are honoured
 * elsewhere in this package: the CSS tier must stay presentable so a *missed*
 * demotion is a fidelity loss and not a broken UI (`css-tier.ts`), and the
 * probe's **reach** is reported alongside its verdict, so an app can tell
 * "probed and passed" from "not probeable here".
 *
 * Layer 2 re-runs on every registration and whenever the audited chain's
 * computed styles change: its inputs are application CSS, which mutates at
 * runtime (hover states, animations, theme switches), so a startup-only probe
 * under-detects.
 */

import { auditBackdropRootChain, type BackdropRootBreak } from "./backdrop-root";
import {
  conformanceRowFor,
  detectEngine,
  type EngineConformanceRow,
  type EngineIdentity,
} from "./conformance-table";
import { checkSupportGate, type SupportGateResult, type SupportsPredicate } from "./support-gate";
import { readComputedStyle, type LayoutReadMeter } from "../measure";

export * from "./backdrop-root";
export * from "./conformance-table";
export * from "./support-gate";

/**
 * How far the probe's answer reaches. Reported to apps beside the verdict,
 * because "passed" and "could not be checked" are different facts.
 */
export const PROBE_REACH = [
  /** Every layer answered, and the engine's own behaviour is recorded as verified. */
  "verified",
  /** The structure is sound, but this engine's rendering was never measured. */
  "structure-only",
  /** The property is absent; nothing further was checked. */
  "unsupported",
] as const;

export type ProbeReach = (typeof PROBE_REACH)[number];

export interface PlatformProbeReport {
  readonly support: SupportGateResult;
  readonly engine: EngineIdentity;
  readonly conformance: EngineConformanceRow;
  readonly reach: ProbeReach;
}

export interface GroupProbeReport {
  readonly groupId: string;
  readonly verdict: "pass" | "fail";
  /** Empty on a pass. Each entry names an element and the property that re-roots. */
  readonly breaks: readonly BackdropRootBreak[];
  readonly reach: ProbeReach;
}

export interface ProbeOptions {
  readonly meter: LayoutReadMeter;
  /** Injected so the platform probe is testable without a browser. */
  readonly supports?: SupportsPredicate;
  readonly userAgent?: string;
}

/** The page-level half: layers 1 and 3, which are the same for every group. */
export function probePlatform(options: ProbeOptions): PlatformProbeReport {
  const supports =
    options.supports ?? ((property: string) => CSS.supports(property, "blur(1px)"));
  const support = checkSupportGate(supports);
  const engine = detectEngine(options.userAgent ?? navigator.userAgent);
  const conformance = conformanceRowFor(engine);

  const reach: ProbeReach = !support.supported
    ? "unsupported"
    : conformance.rasterisesBackdropFilter === "yes"
      ? "verified"
      : "structure-only";

  return { support, engine, conformance, reach };
}

export interface GroupProbeInput {
  readonly groupId: string;
  /** The group's proxy element — the thing whose backdrop can be re-rooted. */
  readonly proxy: Element;
  /** Where to stop the walk, exclusive. The document element is the correct root. */
  readonly stopAt?: Element | null;
  /**
   * The window whose computed styles the walk reads. Threaded rather than taken
   * from the module scope, and required rather than defaulted: the audited chain
   * belongs to the proxy's own document, which is not necessarily the ambient
   * one, and a silent fallback to the ambient window would read a different
   * window's styles for a chain in this one.
   */
  readonly window: Window;
}

/** Layer 2, per group. Deterministic, synchronous, allocation-light. */
export function probeGroup(
  input: GroupProbeInput,
  platform: PlatformProbeReport,
  meter: LayoutReadMeter,
): GroupProbeReport {
  if (!platform.support.supported) {
    return { groupId: input.groupId, verdict: "fail", breaks: [], reach: "unsupported" };
  }

  const breaks = auditBackdropRootChain({
    from: input.proxy,
    stopAt: input.stopAt ?? null,
    readStyle: (element) => {
      const style = readComputedStyle(meter, element, input.window);
      return (property) => style.getPropertyValue(property);
    },
  });

  return {
    groupId: input.groupId,
    verdict: breaks.length === 0 ? "pass" : "fail",
    breaks,
    reach: platform.reach,
  };
}

/** A dev-mode message worth its space: the offending element, and the one-line fix. */
export function describeProbeFailure(report: GroupProbeReport): string {
  if (report.breaks.length === 0) {
    return `Group "${report.groupId}" has no backdrop-filter support in this engine, so its proxy cannot sample anything.`;
  }

  const named = report.breaks
    .map(
      (broken) =>
        `${broken.describe} (${broken.triggers.map((trigger) => `${trigger.property}: ${trigger.value}`).join("; ")})`,
    )
    .join(", then ");

  return `Group "${report.groupId}" sits under an element that forms a Backdrop Root, so its proxy samples nothing and the group demoted to the CSS tier: ${named}. Filter Effects 2 makes filter, opacity below 1, mask, clip-path, mix-blend-mode and a will-change naming any of them re-root the backdrop — a visually inert value like filter: blur(0px) re-roots just as thoroughly as a real one. Remove the property from that element, or move the GlassRoot out from under it.`;
}

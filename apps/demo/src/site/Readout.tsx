/**
 * The runtime, quoting itself.
 *
 * Every row is read straight from `useGlassCapabilities()` and never derived or
 * summarised, because the pairing is the point: a demoted group shows what the app
 * *configured* alongside what is actually drawing it, with the reason named. A
 * readout that collapsed those into "GPU" or "not GPU" would be throwing away the
 * thing X2's state model exists to expose. This is the honesty core made visible,
 * and on this page it is a feature rather than debug chrome.
 */

import { useGlassCapabilities, useGlassDiagnostics } from "@vitreajs/vitrea-react";
import type { ReactNode } from "react";

const AXES = [
  ["configuredSource", "What the page declared"],
  ["activeRenderer", "What is drawing"],
  ["samplingBackend", "Where the backdrop comes from"],
  ["refraction", "Refraction"],
  ["analysis", "Backdrop analysis"],
  ["health", "Health"],
  ["demotionReason", "Demotion reason"],
] as const;

export function GroupReadout(props: { readonly id: string; readonly label: string }): ReactNode {
  const state = useGlassCapabilities(props.id);

  return (
    <dl className="readout">
      <div className="readout__head">
        <dt>Group</dt>
        <dd>{props.label}</dd>
      </div>
      {AXES.map(([axis, label]) => {
        const value = state?.[axis];
        return (
          <div className="readout__row" key={axis}>
            <dt>{label}</dt>
            <dd
              data-health={axis === "health" ? String(value) : undefined}
              data-empty={value === undefined ? "" : undefined}
            >
              {value ?? "none"}
            </dd>
          </div>
        );
      })}
    </dl>
  );
}

/**
 * The dev-mode checks, reported rather than hidden, and split by whose fault a
 * finding would be.
 *
 * `devMode` is left on in the shipped build, so X1's same-plane overlap check, the
 * proxy-overlap check, the variant rules and the startup probe all run on this page
 * in front of the reader. But the channel carries two unlike things, and collapsing
 * them would make the page dishonest in one direction or useless in the other:
 *
 *  - **Authoring findings** are this page's own mistakes: two surfaces overlapping
 *    in one plane, two groups' proxies meeting, a host outside its plane, a clear
 *    variant with no dimming policy. `DESIGN.md` §9 exists so this list is empty,
 *    and it is empty on every browser, because it is a property of the layout.
 *  - **Environment findings** are what this browser could not offer. A machine with
 *    no WebGPU adapter reports `webgpu-unavailable` here, and that is the honesty
 *    core working rather than failing. It belongs on the page as a fact, not as a
 *    defect.
 */
const AUTHORING_CODES = new Set([
  "same-plane-overlap",
  "group-proxy-overlap",
  "merge-distance-below-padding",
  "variant-mixing",
  "clear-variant-needs-dimming",
  "foreground-mode-illegal",
  "foreground-rate-clamped",
  "backdrop-hint-out-of-range",
  "backdrop-hint-redundant-estimator",
  "frame-phase-violation",
  "host-outside-plane",
  "sampling-padding-below-3-sigma",
  "merge-distance-below-effective-padding",
  "proxy-area-over-cap",
  "proxy-overlap-after-enforcement",
  "redundant-promotion",
  "glass-inside-glass",
  "glass-in-content-layer",
]);

export function DiagnosticsReadout(): ReactNode {
  const diagnostics = useGlassDiagnostics();
  const authoring = diagnostics.filter((entry) => AUTHORING_CODES.has(entry.diagnostic.code));
  const environment = diagnostics.filter((entry) => !AUTHORING_CODES.has(entry.diagnostic.code));

  return (
    <>
      {authoring.length === 0 ? (
        <p className="note" data-testid="authoring-clean">
          Authoring checks: no findings. Overlap, proxy overlap, variant rules,
          padding floors and plane containment are all being checked in this build,
          on this layout.
        </p>
      ) : (
        <ul className="findings" data-testid="authoring-findings">
          {authoring.slice(-4).map((entry) => (
            <li key={entry.seq} data-severity={entry.diagnostic.severity}>
              <strong>{entry.diagnostic.code}</strong> {entry.diagnostic.message}
            </li>
          ))}
        </ul>
      )}

      {environment.length === 0 ? null : (
        <ul className="findings findings--environment" data-testid="environment-findings">
          {environment.slice(-3).map((entry) => (
            <li key={entry.seq} data-severity={entry.diagnostic.severity}>
              <strong>{entry.diagnostic.code}</strong> {entry.diagnostic.message}
            </li>
          ))}
        </ul>
      )}
    </>
  );
}

/**
 * The readout: what the runtime actually resolved, in the runtime's own words.
 *
 * This panel is the honesty core made visible (§Backdrop & analysis contracts).
 * Every row is read straight from `useGlassCapabilities()` — never derived, never
 * summarised — so a demoted group shows both what the app *configured* and what
 * it *got*, together with the reason. That pairing is the whole point of X2's
 * state model, and a panel that collapsed it into "GPU / not GPU" would be
 * throwing away the thing worth showing.
 */

import {
  useGlassAccessibility,
  useGlassCapabilities,
  useGlassDiagnostics,
  type AccessibilityOverride,
} from "@vitrea/react";
import type { ReactNode } from "react";

export interface OverrideState {
  readonly reducedMotion: AccessibilityOverride;
  readonly reducedTransparency: AccessibilityOverride;
  readonly increasedContrast: AccessibilityOverride;
}

export interface CapabilitiesPanelProps {
  readonly groups: readonly { readonly id: string; readonly label: string }[];
  readonly overrides: OverrideState;
  readonly onOverridesChange: (next: OverrideState) => void;
  readonly variantMixed: boolean;
  readonly onVariantMixedChange: (next: boolean) => void;
}

const AXES = [
  "configuredSource",
  "activeRenderer",
  "samplingBackend",
  "refraction",
  "analysis",
  "health",
  "demotionReason",
] as const;

function GroupState(props: { readonly id: string; readonly label: string }): ReactNode {
  const state = useGlassCapabilities(props.id);

  return (
    <table className="state-table">
      <caption>{props.label}</caption>
      <tbody>
        {AXES.map((axis) => {
          const value = state?.[axis];
          return (
            <tr key={axis}>
              <th scope="row">{axis}</th>
              <td className={axis === "health" ? `state--${String(value)}` : undefined}>
                {value ?? "—"}
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

function OverrideToggle(props: {
  readonly label: string;
  readonly value: AccessibilityOverride;
  readonly onChange: (next: AccessibilityOverride) => void;
}): ReactNode {
  return (
    <label className="toggle">
      <select
        value={String(props.value)}
        onChange={(event) => {
          const raw = event.target.value;
          props.onChange(raw === "system" ? "system" : raw === "true");
        }}
      >
        <option value="system">system</option>
        <option value="true">on</option>
        <option value="false">off</option>
      </select>
      {props.label}
    </label>
  );
}

export function CapabilitiesPanel(props: CapabilitiesPanelProps): ReactNode {
  const policy = useGlassAccessibility();
  const diagnostics = useGlassDiagnostics();

  return (
    <aside className="panel" aria-label="Runtime readout">
      <div>
        <h1>vitrea playground</h1>
        <p className="panel__note">
          Glass over two backdrops: an arbitrary-DOM region and a registered texture. Every value
          below is read from the runtime, not from what the page asked for.
        </p>
      </div>

      <section>
        <h2>Resolved group state (X2)</h2>
        {props.groups.map((group) => (
          <GroupState key={group.id} id={group.id} label={group.label} />
        ))}
      </section>

      <section>
        <h2>Renderer</h2>
        <p className="panel__note">
          This root asks for <code>renderer=&quot;webgpu&quot;</code>, and the rows above say what
          it got. Where a device and the renderer are both had, glass bodies are drawn by the WebGPU
          optical engine onto the plane&rsquo;s own canvas, and a texture-backed group samples the
          registered source directly — <code>samplingBackend: gpu-texture</code>, with true
          refraction rather than a blur. Where either is missing, every group resolves to the CSS
          tier and says so by name.
        </p>
        <p className="panel__note">
          Asking is not getting, and the panel never smooths over the difference: a demoted group
          keeps its <code>configuredSource</code> alongside the renderer that is actually painting
          it, so what the app declared and what the browser could do stay separately readable.
        </p>
      </section>

      <section>
        <h2>Accessibility (acceptance #6)</h2>
        <div className="toggles">
          <OverrideToggle
            label="reducedMotion"
            value={props.overrides.reducedMotion}
            onChange={(next) => props.onOverridesChange({ ...props.overrides, reducedMotion: next })}
          />
          <OverrideToggle
            label="reducedTransparency"
            value={props.overrides.reducedTransparency}
            onChange={(next) =>
              props.onOverridesChange({ ...props.overrides, reducedTransparency: next })
            }
          />
          <OverrideToggle
            label="increasedContrast"
            value={props.overrides.increasedContrast}
            onChange={(next) =>
              props.onOverridesChange({ ...props.overrides, increasedContrast: next })
            }
          />
        </div>
        <table className="state-table">
          <tbody>
            <tr>
              <th scope="row">forcedColors</th>
              <td>{String(policy?.forcedColors ?? "—")}</td>
            </tr>
            <tr>
              <th scope="row">glass</th>
              <td>{policy?.material.glass ?? "—"}</td>
            </tr>
            <tr>
              <th scope="row">frost</th>
              <td>{policy?.material.frost ?? "—"}</td>
            </tr>
            <tr>
              <th scope="row">refraction cap</th>
              <td>{policy?.material.refraction ?? "—"}</td>
            </tr>
            <tr>
              <th scope="row">overshoot</th>
              <td>{policy?.motion.overshoot ?? "—"}</td>
            </tr>
            <tr>
              <th scope="row">deformation</th>
              <td>{policy?.motion.deformation ?? "—"}</td>
            </tr>
          </tbody>
        </table>
        <p className="panel__note">
          <code>forced-colors</code> has no override and never will: it is an operating-system
          accessibility mandate, so core&rsquo;s type excludes it from the prop set.
        </p>
      </section>

      <section>
        <h2>Dev-mode findings</h2>
        <label className="toggle">
          <input
            type="checkbox"
            checked={props.variantMixed}
            onChange={(event) => props.onVariantMixedChange(event.target.checked)}
          />
          mix regular and clear in one group
        </label>
        {diagnostics.length === 0 ? (
          <p className="panel__note diagnostics__empty">Nothing reported.</p>
        ) : (
          <ul className="diagnostics">
            {diagnostics.slice(-6).map((entry) => (
              <li key={entry.seq} data-severity={entry.diagnostic.severity}>
                <strong>{entry.diagnostic.code}</strong>
                <br />
                {entry.diagnostic.message}
              </li>
            ))}
          </ul>
        )}
      </section>
    </aside>
  );
}

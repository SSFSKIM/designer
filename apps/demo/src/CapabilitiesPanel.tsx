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
  useGlassWindowActivation,
  type AccessibilityOverride,
  type GlassColorScheme,
  type GlassWindowActivation,
} from "@vitreajs/vitrea-react";
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
  readonly windowActivation: GlassWindowActivation;
  readonly onWindowActivationChange: (next: GlassWindowActivation) => void;
  readonly colorScheme: GlassColorScheme;
  readonly onColorSchemeChange: (next: GlassColorScheme) => void;
  readonly variantMixed: boolean;
  readonly onVariantMixedChange: (next: boolean) => void;
}

const ACTIVATIONS: readonly GlassWindowActivation[] = ["auto", "active", "inactive"];
const SCHEMES: readonly GlassColorScheme[] = ["light", "dark", "auto"];

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
  const material = state?.materialDocument;

  return (
    <table className="state-table">
      <caption>{props.label}</caption>
      <tbody>
        {/*
          Which measured material drew, first, because every row under it is
          read against the body this one describes (W29 G4). It joined the
          resolved state when the material became a selection: a page draws
          macOS 27's by default from 0.19.0 and can pin macOS 26.5's, so it is
          exactly as much a resolved fact as the tier. The endpoint's key is
          shown rather than the family's name — the colour-scheme pin and the
          activation pin above each select a different one, and watching this
          row follow them is the point.
        */}
        <tr key="materialDocument">
          <th scope="row">materialDocument</th>
          <td data-testid="material-document">
            {material === undefined
              ? "\u2014"
              : `${material.profileKey ?? material.name}${material.tuned ? " (tuned)" : ""}`}
          </td>
        </tr>
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
  const activation = useGlassWindowActivation();
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
        <p className="panel__note">
          Add <code>?renderer=css</code> to compare the tiers. Note what that does{" "}
          <em>not</em> say: a root that chose the CSS tier reads <code>health: ok</code> with no
          demotion reason, because choosing is not failing — labelling intent as fault would invert
          the whole point of these rows.
        </p>
      </section>

      <section>
        <h2>Window activation</h2>
        <p className="panel__note">
          Apple&rsquo;s glass recedes when its window loses focus, so the pose belongs to the root:
          one window is active or it is not, and no individual surface carries the answer. Leave
          the pin on <code>auto</code> and click away from this window &mdash; to another window,
          and every surface on the page drops its outer shadow and its
          bright rim together. The row below is the runtime&rsquo;s own answer, with{" "}
          <code>auto</code> already folded against the window&rsquo;s focus.
        </p>
        <label className="toggle">
          <select
            value={props.windowActivation}
            onChange={(event) =>
              props.onWindowActivationChange(event.target.value as GlassWindowActivation)
            }
          >
            {ACTIVATIONS.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
          windowActivation pin
        </label>
        <table className="state-table">
          <tbody>
            <tr>
              <th scope="row">windowActivation</th>
              <td>{activation ?? "—"}</td>
            </tr>
          </tbody>
        </table>
        <p className="panel__note">
          Pinning wins over the window, in both directions: <code>inactive</code> holds the recede
          while this window has focus, which is what a preview or a capture harness needs, and{" "}
          <code>active</code> holds the live material while it does not.
        </p>
        <p className="panel__note">
          The recede is fitted per colour scheme &mdash; a material document carries a light
          receded endpoint and a dark one &mdash; so the pin below selects which of the two the
          pose above resolves to. It moves this page&rsquo;s own ground with it, and it moves the{" "}
          <code>materialDocument</code> row in each group&rsquo;s table, which names the endpoint
          that actually drew.
        </p>
        <label className="toggle">
          <select
            value={props.colorScheme}
            onChange={(event) =>
              props.onColorSchemeChange(event.target.value as GlassColorScheme)
            }
          >
            {SCHEMES.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
          colorScheme pin
        </label>
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
        <p className="panel__note">
          The band below styles something with{" "}
          <code>--vitrea-foreground-quaternary</code>, so every surface in this page under the
          material&rsquo;s thin/thick knee reports the fourth level&rsquo;s advisory once. That is
          the finding working: the scan is of the document, not of the element, and the playground
          is full of thin controls.
        </p>
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

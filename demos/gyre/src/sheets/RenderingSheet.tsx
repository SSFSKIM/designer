/**
 * Rendering: what the runtime actually resolved, printed rather than claimed.
 * `useGlassCapabilities` reports the state each group is drawing in, a demoted
 * group names its reason, and the accessibility overrides are the root's own
 * props, so changing one here changes the material everywhere.
 */

import {
  useGlassAccessibility,
  useGlassCapabilities,
  useGlassDiagnostics,
  type AccessibilityOverride,
} from "@vitreajs/vitrea-react";
import { useId, type ReactNode } from "react";

import { Readout, Sheet } from "./Sheet";

export interface Overrides {
  readonly reducedMotion: AccessibilityOverride;
  readonly reducedTransparency: AccessibilityOverride;
  readonly increasedContrast: AccessibilityOverride;
}

export interface RenderingSheetProps {
  readonly requestedRenderer: "css" | "webgpu";
  readonly fieldFallback: boolean;
  readonly overrides: Overrides;
  readonly onOverridesChange: (next: Overrides) => void;
  readonly onClose: () => void;
}

const GROUPS = [
  { id: "nav", label: "Nav" },
  { id: "probe", label: "Probe" },
  { id: "transport", label: "Transport" },
  { id: "layers", label: "Layers" },
  { id: "menu", label: "Menu" },
] as const;

function GroupRow(props: { readonly id: string; readonly label: string }): ReactNode {
  const state = useGlassCapabilities(props.id);
  if (state === undefined) {
    return (
      <div className="readout__row">
        <dt>{props.label}</dt>
        <dd>not registered</dd>
      </div>
    );
  }
  return (
    <div className="readout__row">
      <dt>{props.label}</dt>
      <dd>
        {state.activeRenderer}, {state.samplingBackend}, refraction {state.refraction}, analysis{" "}
        {state.analysis}
        {state.health === "demoted" ? `, demoted: ${state.demotionReason ?? "unknown"}` : ""}
      </dd>
    </div>
  );
}

const OVERRIDE_OPTIONS: readonly { readonly value: AccessibilityOverride; readonly label: string }[] = [
  { value: "system", label: "System" },
  { value: true, label: "On" },
  { value: false, label: "Off" },
];

function OverrideField(props: {
  readonly label: string;
  readonly value: AccessibilityOverride;
  readonly onChange: (next: AccessibilityOverride) => void;
}): ReactNode {
  const id = useId();
  return (
    <div className="form__field form__field--row">
      <label htmlFor={id}>{props.label}</label>
      <select
        id={id}
        value={String(props.value)}
        onChange={(event) => {
          const raw = event.target.value;
          props.onChange(raw === "system" ? "system" : raw === "true");
        }}
      >
        {OVERRIDE_OPTIONS.map((option) => (
          <option key={String(option.value)} value={String(option.value)}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}

export function RenderingSheet(props: RenderingSheetProps): ReactNode {
  const policy = useGlassAccessibility();
  const diagnostics = useGlassDiagnostics();
  const otherRenderer = props.requestedRenderer === "webgpu" ? "css" : "webgpu";
  const otherHref = `?renderer=${otherRenderer}`;

  return (
    <Sheet id="rendering" title="Rendering" onClose={props.onClose}>
      <p className="sheet__lead">
        Asking for a tier is not getting it. Each group below reports what it is actually drawing
        with, and a demoted group names why.
      </p>
      <dl className="readout">
        <div className="readout__row">
          <dt>Requested</dt>
          <dd>{props.requestedRenderer}</dd>
        </div>
        {GROUPS.map((group) => (
          <GroupRow key={group.id} id={group.id} label={group.label} />
        ))}
        <div className="readout__row">
          <dt>Field</dt>
          <dd>{props.fieldFallback ? "static fallback, no WebGL2" : "WebGL2, live"}</dd>
        </div>
        <div className="readout__row">
          <dt>Diagnostics</dt>
          <dd>
            {diagnostics.length === 0
              ? "none"
              : `${diagnostics.length}: ${[...new Set(diagnostics.map((d) => d.diagnostic.code))].join(", ")}`}
          </dd>
        </div>
      </dl>
      <p>
        <a className="link" href={otherHref}>
          Reload asking for the {otherRenderer} tier
        </a>
      </p>

      <h3 className="sheet__h3">Accessibility</h3>
      <p>
        Each preference resolves to a declared change in the material. System follows the media
        query; on and off overrule it for this page.
      </p>
      <OverrideField
        label="Reduced motion"
        value={props.overrides.reducedMotion}
        onChange={(next) => props.onOverridesChange({ ...props.overrides, reducedMotion: next })}
      />
      <OverrideField
        label="Reduced transparency"
        value={props.overrides.reducedTransparency}
        onChange={(next) =>
          props.onOverridesChange({ ...props.overrides, reducedTransparency: next })
        }
      />
      <OverrideField
        label="Increased contrast"
        value={props.overrides.increasedContrast}
        onChange={(next) =>
          props.onOverridesChange({ ...props.overrides, increasedContrast: next })
        }
      />
      {policy === undefined ? null : (
        <Readout
          rows={[
            { label: "Reduced motion", value: policy.reducedMotion ? "active" : "off" },
            { label: "Reduced transparency", value: policy.reducedTransparency ? "active" : "off" },
            { label: "Increased contrast", value: policy.increasedContrast ? "active" : "off" },
            { label: "Forced colours", value: policy.forcedColors ? "active, no glass" : "off" },
          ]}
        />
      )}
    </Sheet>
  );
}

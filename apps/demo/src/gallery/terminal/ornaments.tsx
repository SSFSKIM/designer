/**
 * The window's ornaments, each attached outside one of its edges in the overlay plane and each its
 * own sampling group: the sessions' tabs and the new-session button above, and below, the two
 * choices that make a profile — which glass, which appearance — and the page's Reduce
 * transparency setting. Plain buttons on glass; the selected tab is a lighter child fill,
 * concentric with its capsule. vitrea's segmented control takes no `present`, so the two profile
 * choices cannot materialise: the page mounts them once its glass is present, and they appear at
 * once where the other groups materialise.
 */

import { GlassGroup, GlassSegmentedControl, GlassSurface, type BackdropHint } from "@vitreajs/vitrea-react";
import { useRef, type KeyboardEvent, type ReactNode } from "react";

import { DESIGN } from "./layout";
import { boxStyle, ENVIRONMENT_BACKDROP, ORNAMENT_THICKNESS, type Box, type GroupMaterial } from "./shared";
import type { GlassKind, Scheme } from "./shell/types";
import type { SessionSpec } from "./terminal-view";

interface GroupProps {
  readonly box: Box;
  readonly hint: BackdropHint | undefined;
  readonly material: GroupMaterial;
  readonly present: boolean;
}

/** A segmented control's group: it takes no `present`, having no way to materialise. */
type ControlProps = Omit<GroupProps, "present">;

const CAPSULE = DESIGN.ornament / 2;

export function SessionTabs(
  props: GroupProps & {
    readonly sessions: readonly SessionSpec[];
    readonly active: string;
    /** Too narrow for names: each tab shows its number, and its name only to assistive tech. */
    readonly compact: boolean;
    /** An arrow, Home or End key selected a tab; focus stays on it. */
    readonly onSelect: (id: string) => void;
    /** A tab was clicked (or pressed with Enter or Space); the page hands focus to its terminal. */
    readonly onOpen: (id: string) => void;
  },
): ReactNode {
  const { box, hint, material, present, sessions, active, compact, onSelect, onOpen } = props;
  const list = useRef<HTMLDivElement>(null);
  // Tabs keep one tab stop and move by arrow keys, the ARIA tabs pattern with automatic activation.
  const onKeyDown = (event: KeyboardEvent<HTMLDivElement>): void => {
    const index = sessions.findIndex((s) => s.id === active);
    const step = event.key === "ArrowRight" ? 1 : event.key === "ArrowLeft" ? -1 : 0;
    const to = event.key === "Home" ? 0 : event.key === "End" ? sessions.length - 1 : (index + step + sessions.length) % sessions.length;
    if (step === 0 && event.key !== "Home" && event.key !== "End") return;
    event.preventDefault();
    const next = sessions[to];
    if (next === undefined) return;
    onSelect(next.id);
    list.current?.querySelector<HTMLElement>(`#tab-${next.id}`)?.focus();
  };
  return (
    <GlassGroup id="sessions" backdrop={ENVIRONMENT_BACKDROP} hint={hint} {...material}>
      <GlassSurface asChild plane="overlay" radius={CAPSULE} thickness={ORNAMENT_THICKNESS} interactive foreground="vibrant" present={present}>
        <div ref={list} role="tablist" aria-label="Sessions" data-glass-role="ornament" className={compact ? "ornament tabs tabs-compact" : "ornament tabs"} style={boxStyle(box)} onKeyDown={onKeyDown}>
          {sessions.map((session, n) => {
            const selected = session.id === active;
            return (
              <button
                key={session.id}
                id={`tab-${session.id}`}
                type="button"
                role="tab"
                aria-selected={selected}
                aria-controls={`panel-${session.id}`}
                tabIndex={selected ? 0 : -1}
                className="tab"
                onClick={() => onOpen(session.id)}
              >
                <span className="tab-index">{n + 1}</span>
                <span className={compact ? "tab-name visually-hidden" : "tab-name"}>{session.name}</span>
              </button>
            );
          })}
        </div>
      </GlassSurface>
    </GlassGroup>
  );
}

export function NewSession(props: GroupProps & { readonly disabled: boolean; readonly onNew: () => void }): ReactNode {
  const { box, hint, material, present, disabled, onNew } = props;
  return (
    <GlassGroup id="new-session" backdrop={ENVIRONMENT_BACKDROP} hint={hint} {...material}>
      <GlassSurface asChild plane="overlay" radius={CAPSULE} thickness={ORNAMENT_THICKNESS} interactive foreground="vibrant" present={present}>
        <button
          type="button"
          data-glass-role="control"
          className="ornament icon-button"
          style={boxStyle(box)}
          aria-label="New session"
          title={disabled ? `Four sessions is this page’s limit` : "New session"}
          disabled={disabled}
          onClick={onNew}
        >
          <svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true">
            <path d="M8 2.5v11M2.5 8h11" />
          </svg>
        </button>
      </GlassSurface>
    </GlassGroup>
  );
}

export function GlassSwitch(props: ControlProps & { readonly value: GlassKind; readonly onChange: (value: GlassKind) => void }): ReactNode {
  return (
    <GlassGroup id="glass" backdrop={ENVIRONMENT_BACKDROP} hint={props.hint} {...props.material}>
      <GlassSegmentedControl
        style={boxStyle(props.box)}
        groupId="glass"
        plane="overlay"
        aria-label="Glass"
        data-glass-role="ornament"
        radius={CAPSULE}
        thickness={ORNAMENT_THICKNESS}
        items={[
          { value: "clear", label: "Clear" },
          { value: "regular", label: "Regular" },
        ]}
        value={props.value}
        onChange={props.onChange}
        className="ornament segmented"
        indicatorClassName="segmented-indicator"
        segmentClassName="segment"
      />
    </GlassGroup>
  );
}

export function AppearanceSwitch(props: ControlProps & { readonly value: Scheme; readonly onChange: (value: Scheme) => void }): ReactNode {
  return (
    <GlassGroup id="appearance" backdrop={ENVIRONMENT_BACKDROP} hint={props.hint} {...props.material}>
      <GlassSegmentedControl
        style={boxStyle(props.box)}
        groupId="appearance"
        plane="overlay"
        aria-label="Appearance"
        data-glass-role="ornament"
        radius={CAPSULE}
        thickness={ORNAMENT_THICKNESS}
        items={[
          { value: "dark", label: "Dark" },
          { value: "light", label: "Light" },
        ]}
        value={props.value}
        onChange={props.onChange}
        className="ornament segmented"
        indicatorClassName="segmented-indicator"
        segmentClassName="segment"
      />
    </GlassGroup>
  );
}

export function TransparencyToggle(props: GroupProps & { readonly value: boolean; readonly onChange: (value: boolean) => void }): ReactNode {
  const { box, hint, material, present, value, onChange } = props;
  return (
    <GlassGroup id="transparency" backdrop={ENVIRONMENT_BACKDROP} hint={hint} {...material}>
      <GlassSurface asChild plane="overlay" radius={CAPSULE} thickness={ORNAMENT_THICKNESS} interactive foreground="vibrant" present={present}>
        <button
          type="button"
          role="switch"
          aria-checked={value}
          data-glass-role="control"
          className="ornament switch-button"
          style={boxStyle(box)}
          onClick={() => onChange(!value)}
        >
          <span className="switch-label">Reduce transparency</span>
          <span className="switch-track" aria-hidden="true">
            <span className="switch-thumb" />
          </span>
        </button>
      </GlassSurface>
    </GlassGroup>
  );
}

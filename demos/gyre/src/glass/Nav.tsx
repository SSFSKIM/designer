/**
 * The nav: one `GlassToolbar`, top-left, start-aligned. Every member is a real
 * `<button>` because every member does something: the wordmark closes whatever
 * sheet is open, the three links toggle sheets, and the one tinted action opens
 * the access sheet. The toolbar container itself is plain DOM; the platter the
 * reader sees is its members' fields merging.
 *
 * The wordmark is deliberately *not* glass. A morph's closed platter spends its
 * first frame as a collapsed point at the viewport's origin before it pins, and
 * vitrea warns when two sampling groups come within a padding of each other, so
 * the origin corner stays clear of glass (the library's own demo records the same
 * rule). Ink on the field is legible everywhere by construction (DESIGN.md §1),
 * so the mark needs no platter.
 */

import { GlassButton, GlassSurface, GlassToolbar, useToolbarItem } from "@vitreajs/vitrea-react";
import { useMemo, type ReactNode } from "react";

import { FIELD_TEXTURE_ID } from "../field/Field";
import type { SheetId } from "../sheets/Sheet";

export interface NavProps {
  readonly sheet: SheetId | null;
  readonly narrow: boolean;
  readonly onSheet: (sheet: SheetId | null) => void;
}

const LINKS: readonly { readonly id: SheetId; readonly label: string }[] = [
  { id: "stations", label: "Stations" },
  { id: "method", label: "Method" },
  { id: "rendering", label: "Rendering" },
];

function Wordmark(props: { readonly onClick: () => void }): ReactNode {
  const item = useToolbarItem();
  return (
    <button {...item} type="button" className="wordmark" onClick={props.onClick}>
      Gyre
    </button>
  );
}

/**
 * The tinted action. `GlassSurface asChild` over a `<button>` rather than
 * `GlassButton`, because the tint is a surface prop and the button sugar does not
 * forward it. The seed is the accent token, read from the stylesheet so the
 * colour has one home.
 */
function TintedAction(props: {
  readonly pressed: boolean;
  readonly onClick: () => void;
  readonly children: ReactNode;
}): ReactNode {
  const item = useToolbarItem();
  const tint = useMemo(
    () => getComputedStyle(document.documentElement).getPropertyValue("--accent-hex").trim(),
    [],
  );
  return (
    <GlassSurface asChild capsule thickness={8} interactive tint={tint}>
      <button
        {...item}
        type="button"
        className="control control--tinted"
        aria-pressed={props.pressed}
        onClick={props.onClick}
      >
        {props.children}
      </button>
    </GlassSurface>
  );
}

export function Nav(props: NavProps): ReactNode {
  const toggle = (id: SheetId): void => props.onSheet(props.sheet === id ? null : id);

  return (
    <GlassToolbar
      aria-label="Gyre"
      className="nav"
      groupProps={{ id: "nav", backdrop: { kind: "texture", id: FIELD_TEXTURE_ID } }}
    >
      <Wordmark onClick={() => props.onSheet(null)} />
      {props.narrow
        ? null
        : LINKS.map((link) => (
            <GlassButton
              key={link.id}
              className="control"
              capsule
              thickness={8}
              aria-pressed={props.sheet === link.id}
              onClick={() => toggle(link.id)}
            >
              {link.label}
            </GlassButton>
          ))}
      <TintedAction pressed={props.sheet === "access"} onClick={() => toggle("access")}>
        Request access
      </TintedAction>
    </GlassToolbar>
  );
}

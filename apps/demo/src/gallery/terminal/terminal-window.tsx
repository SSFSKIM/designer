/**
 * The Terminal window: the page's one window, a real task unit. Its title line names the session
 * and the grid's size and is where the window is taken to move it; its lower-right corner resizes
 * it. The sessions' terminals sit on the glass as its content, the runtime's ink on the title and
 * the page's own on the terminal (`palette.ts`). The host stays still while the terminal scrolls
 * inside its own box.
 */

import { GlassGroup, GlassSurface, type BackdropHint } from "@vitreajs/vitrea-react";
import type { GlassHostHandle } from "@vitreajs/vitrea-web";
import { useRef, type PointerEvent, type ReactNode } from "react";

import { boxStyle, ENVIRONMENT_BACKDROP, WINDOW_RADIUS, WINDOW_THICKNESS, type Box, type GroupMaterial } from "./shared";

type Gesture = { readonly kind: "move" | "size"; readonly x: number; readonly y: number; readonly from: Box };

export function TerminalWindow(props: {
  readonly box: Box;
  readonly hint: BackdropHint | undefined;
  readonly material: GroupMaterial;
  readonly present: boolean;
  readonly title: string;
  readonly detail: string;
  /**
   * A box the person asked for by dragging, and which gesture asked: a move keeps the size and
   * the page clamps the position, a resize keeps the top-left corner and the page clamps the size.
   */
  readonly onBox: (box: Box, gesture: Gesture["kind"]) => void;
  readonly onHost: (handle: GlassHostHandle | null) => void;
  readonly children: ReactNode;
}): ReactNode {
  const { box, hint, material, present, title, detail, onBox, onHost, children } = props;
  const gesture = useRef<Gesture | null>(null);

  const begin = (kind: Gesture["kind"]) => (event: PointerEvent<HTMLElement>) => {
    if (event.button !== 0) return;
    event.preventDefault();
    event.currentTarget.setPointerCapture(event.pointerId);
    gesture.current = { kind, x: event.clientX, y: event.clientY, from: box };
  };
  const follow = (event: PointerEvent<HTMLElement>, done: boolean): void => {
    const g = gesture.current;
    if (g === null) return;
    const dx = event.clientX - g.x;
    const dy = event.clientY - g.y;
    const next =
      g.kind === "move"
        ? { ...g.from, x: g.from.x + dx, y: g.from.y + dy }
        : { ...g.from, width: g.from.width + dx, height: g.from.height + dy };
    if (done) gesture.current = null;
    onBox(next, g.kind);
  };
  const handlers = (kind: Gesture["kind"]) => ({
    onPointerDown: begin(kind),
    onPointerMove: (event: PointerEvent<HTMLElement>) => follow(event, false),
    onPointerUp: (event: PointerEvent<HTMLElement>) => follow(event, true),
    onPointerCancel: (event: PointerEvent<HTMLElement>) => follow(event, true),
  });

  return (
    <GlassGroup id="terminal" backdrop={ENVIRONMENT_BACKDROP} hint={hint} {...material}>
      <GlassSurface asChild radius={WINDOW_RADIUS} thickness={WINDOW_THICKNESS} foreground="vibrant" present={present} onHost={onHost}>
        <section aria-label="Terminal" data-glass-role="window" className="terminal-window" style={boxStyle(box)}>
          <div className="window-inner">
            <header className="title-line" {...handlers("move")}>
              <span className="title-name">{title}</span>
              <span className="title-detail">{detail}</span>
            </header>
            <div className="sessions">{children}</div>
            <div className="grip" aria-hidden="true" {...handlers("size")}>
              <svg viewBox="0 0 12 12" width="12" height="12">
                <path d="M11 4 4 11M11 8 8 11" />
              </svg>
            </div>
          </div>
        </section>
      </GlassSurface>
    </GlassGroup>
  );
}

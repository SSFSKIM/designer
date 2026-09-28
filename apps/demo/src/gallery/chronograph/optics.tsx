/**
 * The two optical objects: the crystal over the dial and the loupe on the bench.
 *
 * Neither carries content. The crystal is one circle of glass in the base plane, exactly over the
 * painted bezel's inner edge; the loupe is a dome in the overlay plane, so it can pass over the
 * crystal, and the page paints the enlarged image under it (scene.ts).
 */

import { GlassGroup, GlassSurface } from "@vitreajs/vitrea-react";
import type { GlassHostHandle } from "@vitreajs/vitrea-web";
import { useCallback, useEffect, useRef, type KeyboardEvent, type PointerEvent, type ReactNode } from "react";

import type { Circle, Layout } from "./layout";
import { BENCH_BACKDROP, LOUPE_THICKNESS } from "./shared";

/**
 * The crystal. It is glass over the content rather than a control over it, so where the material
 * would thicken to protect a control's legibility, Reduce Transparency, forced colours and an
 * unfocused window's receded pose, it steps aside instead (`present` false): a fogged crystal
 * would hide the one thing the page is about.
 */
export function Crystal(props: {
  readonly circle: Circle;
  readonly thickness: number;
  readonly present: boolean;
}): ReactNode {
  const { circle, thickness } = props;
  return (
    <GlassGroup id="crystal" backdrop={BENCH_BACKDROP}>
      <GlassSurface asChild capsule thickness={thickness} present={props.present}>
        <div
          className="crystal"
          data-glass-role="lens"
          aria-hidden="true"
          style={{
            left: circle.cx - circle.r,
            top: circle.cy - circle.r,
            width: circle.r * 2,
            height: circle.r * 2,
          }}
        />
      </GlassSurface>
    </GlassGroup>
  );
}

/**
 * The loupe. It rests on the bench and can be picked up and moved anywhere over the watch and
 * the mat: dragged with a pointer, or with the arrow keys once it has focus (Shift for a larger
 * step, Home to set it back on its rest). It steps aside as the crystal does, and the page then
 * draws its edge as a ring round the enlarged image, which stays. It stays out of the controls' column, because it is
 * above them in the overlay plane and would show the bench where their labels are.
 */
export function Loupe(props: {
  readonly layout: Layout;
  readonly circle: Circle;
  readonly present: boolean;
  readonly onMove: (circle: Circle) => void;
}): ReactNode {
  const { layout, circle, onMove } = props;
  const handle = useRef<GlassHostHandle | null>(null);
  const drag = useRef<{ dx: number; dy: number; id: number } | null>(null);

  const place = useCallback(
    (cx: number, cy: number) => {
      const next = constrainLoupe(layout, { cx, cy, r: circle.r });
      onMove(next);
    },
    [layout, circle.r, onMove],
  );

  // A same-sized host moved by its own style keeps its cached box until told otherwise.
  useEffect(() => {
    handle.current?.invalidateGeometry();
  }, [circle.cx, circle.cy]);

  const onPointerDown = (event: PointerEvent<HTMLButtonElement>): void => {
    event.currentTarget.setPointerCapture(event.pointerId);
    drag.current = { dx: event.clientX - circle.cx, dy: event.clientY - circle.cy, id: event.pointerId };
  };
  const onPointerMove = (event: PointerEvent<HTMLButtonElement>): void => {
    const d = drag.current;
    if (d === null || d.id !== event.pointerId) return;
    place(event.clientX - d.dx, event.clientY - d.dy);
  };
  const onPointerUp = (event: PointerEvent<HTMLButtonElement>): void => {
    if (drag.current?.id === event.pointerId) drag.current = null;
  };
  const onKeyDown = (event: KeyboardEvent<HTMLButtonElement>): void => {
    const step = event.shiftKey ? 48 : 12;
    const moves: Record<string, [number, number]> = {
      ArrowLeft: [-step, 0],
      ArrowRight: [step, 0],
      ArrowUp: [0, -step],
      ArrowDown: [0, step],
    };
    if (event.key === "Home") {
      event.preventDefault();
      onMove(layout.loupeRest);
      return;
    }
    const move = moves[event.key];
    if (move === undefined) return;
    event.preventDefault();
    place(circle.cx + move[0], circle.cy + move[1]);
  };

  return (
    <GlassGroup id="loupe" backdrop={BENCH_BACKDROP}>
      <GlassSurface
        asChild
        capsule
        plane="overlay"
        interactive
        present={props.present}
        thickness={LOUPE_THICKNESS}
        onHost={(h) => {
          handle.current = h;
        }}
      >
        <button
          type="button"
          className="loupe"
          data-glass-role="lens"
          aria-label="Loupe. Drag it, or use the arrow keys, to look closer at the dial. Home puts it back."
          style={{
            left: circle.cx - circle.r,
            top: circle.cy - circle.r,
            width: circle.r * 2,
            height: circle.r * 2,
          }}
          onPointerDown={onPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={onPointerUp}
          onPointerCancel={onPointerUp}
          onDoubleClick={() => onMove(layout.loupeRest)}
          onKeyDown={onKeyDown}
        />
      </GlassSurface>
    </GlassGroup>
  );
}

/** Keep the loupe on the bench, inside the window, and clear of the controls. */
export function constrainLoupe(layout: Layout, c: Circle): Circle {
  const gap = 20;
  let cx = Math.min(layout.width - c.r - 4, Math.max(c.r + 4, c.cx));
  let cy = Math.min(layout.height - c.r - 4, Math.max(c.r + 4, c.cy));
  if (layout.mode === "wide") {
    cx = Math.min(cx, layout.timing.x - gap - c.r);
  } else {
    cy = Math.min(cy, layout.timing.y - gap - c.r);
    cy = Math.max(cy, layout.dial.y + layout.dial.height + gap + c.r);
  }
  return { cx, cy, r: c.r };
}

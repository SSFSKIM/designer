/**
 * A group's declared backdrop, measured rather than typed.
 *
 * Every few frames this reads the group's members' measured bounds from the runtime's own scene
 * (the boxes it drew, not the boxes the layout asked for, which matters while a morph is in
 * flight) and asks `plane.measure` what is displayed under their union. The answer is quantised
 * so a scroll does not re-patch the group on every frame; the runtime low-passes its own
 * adaptation on top of that.
 *
 * A declared hint overrides the runtime's own tone reading on both tiers, so this number is what
 * the body's tone and the ink follow on every group, texture groups included: on the CSS tier and
 * on the DOM path (the open route menu) it is the only reading there is, and on the WebGPU tier a
 * texture group still hands the lens and the blur the photograph's own pixels (`analysis:
 * "exact"` says where the pixels come from) while its measured local tone stands down for the
 * declaration (platform-web `root.ts`, the declared luminance; renderer-webgpu `renderer.ts`,
 * `backdropToneHint`). vitrea.md §2's "the pixels win" is wrong on that point. Hence the
 * measurement is of what is displayed, sheet ink included, and never a typed constant.
 */

import { useGlassRootHandle, type BackdropHint } from "@vitreajs/vitrea-react";
import { useEffect, useState } from "react";

import { measure, type Measured } from "./plane";

const EVERY_NTH_FRAME = 3;

export interface MeasuredHint {
  readonly hint: BackdropHint | undefined;
  readonly measured: Measured | undefined;
}

const quantise = (value: number, step: number): number => Math.round(value / step) * step;

export function useMeasuredHint(groupId: string): MeasuredHint {
  const { root, ticker } = useGlassRootHandle();
  const [state, setState] = useState<MeasuredHint>({ hint: undefined, measured: undefined });

  useEffect(() => {
    if (root === null) return;
    let frame = 0;
    let lastKey = "";
    return ticker.subscribe(() => {
      frame += 1;
      if (frame % EVERY_NTH_FRAME !== 0) return;
      const nodes = root.scene.nodesOfGroup(groupId);
      let x0 = Number.POSITIVE_INFINITY;
      let y0 = Number.POSITIVE_INFINITY;
      let x1 = Number.NEGATIVE_INFINITY;
      let y1 = Number.NEGATIVE_INFINITY;
      for (const node of nodes) {
        const bounds = node.bounds;
        if (bounds === undefined || bounds.width < 4 || bounds.height < 4) continue;
        x0 = Math.min(x0, bounds.x);
        y0 = Math.min(y0, bounds.y);
        x1 = Math.max(x1, bounds.x + bounds.width);
        y1 = Math.max(y1, bounds.y + bounds.height);
      }
      if (!Number.isFinite(x0)) return;
      const measured = measure({ x: x0, y: y0, width: x1 - x0, height: y1 - y0 });
      if (measured === undefined) return;
      const hint: BackdropHint = {
        tone: measured.tone,
        luminance: quantise(measured.luminance, 0.01),
        complexity: quantise(measured.complexity, 0.05),
      };
      const key = `${hint.tone}:${String(hint.luminance)}:${String(hint.complexity)}`;
      if (key === lastKey) return;
      lastKey = key;
      setState({ hint, measured });
    });
  }, [groupId, root, ticker]);

  return state;
}

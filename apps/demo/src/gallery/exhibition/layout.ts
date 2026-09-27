/**
 * Where the window and its ornaments sit, derived once, in one place.
 *
 * The window is a column at the viewport's leading edge; the two ornaments hang below its bottom
 * edge, the rooms ornament at its leading side and the guide at its trailing side, together no
 * wider than the window. The two gaps, window to ornament row and ornament to ornament, are not
 * chosen: each is the larger of core's advisory group padding (24) and the sampling padding the
 * material asks for at these boxes, under the resolved policy and the selected document's active
 * endpoint for the resolved scheme (`samplingPaddingFor`, the same composition `GlassToolbar` opens
 * its split with). Reduce Transparency thickens the frost and the gap follows it.
 *
 * The same numbers place the hosts and describe the footprints the environment grades and
 * measures, so the painted wash and the glass above it cannot disagree about where the glass is.
 */

import { DEFAULT_GROUP_SAMPLING, NOMINAL_ACCESSIBILITY_POLICY } from "@vitreajs/vitrea";
import {
  useGlassAccessibility,
  useGlassRootHandle,
} from "@vitreajs/vitrea-react";
import { samplingPaddingFor } from "@vitreajs/vitrea-web";
import { useEffect, useMemo, useState } from "react";

import type { Footprint, Scheme } from "./painter";

/** The page's outer margin: the viewport edge is the frame, square, at this inset. */
export const MARGIN = 32;
/** The window corner, the page's concentric anchor. */
export const WINDOW_RADIUS = 32;
export const ORNAMENT_HEIGHT = 52;
export const ORNAMENT_RADIUS = ORNAMENT_HEIGHT / 2;
/** Three 44 px buttons' worth: previous, the room index, next, inside a 4 px inset. */
export const ROOMS_WIDTH = 176;
export const THICKNESS = 8;

export interface Box {
  readonly left: number;
  readonly top: number;
  readonly width: number;
  readonly height: number;
}

export interface Layout {
  readonly viewport: { readonly width: number; readonly height: number };
  readonly window: Box;
  readonly rooms: Box;
  readonly guide: Box;
  /** The two derived gaps, for the record and the readout. */
  readonly rowGap: number;
  readonly ornamentGap: number;
  readonly footprints: Readonly<Record<string, Footprint>>;
}

export const GROUP = {
  window: "label-window",
  rooms: "rooms-ornament",
  guide: "guide-ornament",
} as const;

function useViewport(): { width: number; height: number } {
  const [viewport, setViewport] = useState(() => ({
    width: window.innerWidth,
    height: window.innerHeight,
  }));
  useEffect(() => {
    const update = (): void =>
      setViewport((current) =>
        current.width === window.innerWidth && current.height === window.innerHeight
          ? current
          : { width: window.innerWidth, height: window.innerHeight },
      );
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, []);
  return viewport;
}

export function useLayout(scheme: Scheme): Layout {
  const viewport = useViewport();
  const accessibility = useGlassAccessibility();
  const { materialProfileDocument } = useGlassRootHandle();
  const material = (accessibility ?? NOMINAL_ACCESSIBILITY_POLICY).material;
  const endpoint = materialProfileDocument.active[scheme];

  return useMemo(() => {
    const padding = (box: readonly [number, number]): number =>
      Math.max(
        DEFAULT_GROUP_SAMPLING.samplingPadding,
        samplingPaddingFor({
          members: [box],
          material,
          // Always present, `undefined` included: an endpoint with no patch IS the renderer's
          // constants, and omitting the key would ask for the default document's instead.
          profile: endpoint.patch,
          cssTierMapping: materialProfileDocument.cssTierMapping,
        }),
      );

    const windowWidth = Math.round(Math.min(468, Math.max(400, viewport.width * 0.32)));
    // The guide's width depends on the ornament gap and the gap on the guide's box; the law is
    // monotone in span and every candidate box is 52 tall, so the rooms box bounds the guide's.
    const ornamentGap = Math.ceil(padding([ROOMS_WIDTH, ORNAMENT_HEIGHT]));
    const guideWidth = windowWidth - ROOMS_WIDTH - ornamentGap;
    const provisionalHeight = viewport.height - MARGIN * 2 - ORNAMENT_HEIGHT - 24;
    const rowGap = Math.ceil(
      Math.max(
        padding([windowWidth, provisionalHeight]),
        padding([ROOMS_WIDTH, ORNAMENT_HEIGHT]),
        padding([guideWidth, ORNAMENT_HEIGHT]),
      ),
    );
    const windowHeight = Math.max(320, viewport.height - MARGIN * 2 - ORNAMENT_HEIGHT - rowGap);
    const ornamentTop = MARGIN + windowHeight + rowGap;

    const windowBox: Box = { left: MARGIN, top: MARGIN, width: windowWidth, height: windowHeight };
    const rooms: Box = {
      left: MARGIN,
      top: ornamentTop,
      width: ROOMS_WIDTH,
      height: ORNAMENT_HEIGHT,
    };
    const guide: Box = {
      left: MARGIN + windowWidth - guideWidth,
      top: ornamentTop,
      width: guideWidth,
      height: ORNAMENT_HEIGHT,
    };
    const footprint = (
      kind: Footprint["kind"],
      box: Box,
      radius: number,
      feather: number,
    ): Footprint => ({
      kind,
      x: box.left,
      y: box.top,
      width: box.width,
      height: box.height,
      radius,
      feather,
    });
    return {
      viewport,
      window: windowBox,
      rooms,
      guide,
      rowGap,
      ornamentGap,
      footprints: {
        [GROUP.window]: footprint("window", windowBox, WINDOW_RADIUS, 28),
        [GROUP.rooms]: footprint("ornament", rooms, ORNAMENT_RADIUS, 12),
        [GROUP.guide]: footprint("ornament", guide, ORNAMENT_RADIUS, 12),
      },
    };
  }, [endpoint, material, materialProfileDocument.cssTierMapping, viewport]);
}

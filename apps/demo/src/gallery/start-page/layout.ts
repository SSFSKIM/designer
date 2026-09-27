/**
 * Where the three windows and two ornaments stand, from the viewport and the runtime's gap.
 *
 * The hosts are portalled into the glass root's plane, so they cannot take part in a layout of
 * this page's own DOM; every host is `position: fixed` at a box computed here. The widths and
 * heights are the design's (`DESIGN.md`, windows); the GAP is not a design number at all. It is
 * the larger of the sampling paddings of the groups it separates, which the runtime derives from
 * the blur it actually draws — so it moves with the colour scheme and rises under Reduce
 * Transparency — and every column, the search ornament's lift above Places and the Photograph
 * ornament's drop below Now are that one number.
 */

import {
  DEFAULT_GROUP_SAMPLING,
  NOMINAL_ACCESSIBILITY_POLICY,
  type ResolvedMaterialPolicy,
} from "@vitreajs/vitrea";
import { samplingPaddingFor, type GlassMaterialProfileDocument } from "@vitreajs/vitrea-web";

import type { Box } from "./environment";

/** The design's boxes at full size, CSS px. Columns scale down together below 1440 wide. */
export const DESIGN = {
  now: { width: 320, height: 332 },
  places: { width: 496, height: 404 },
  today: { width: 376, height: 600 },
  search: { height: 56, inset: 28 },
  photograph: { width: 248, height: 48 },
  platter: { width: 320, height: 232 },
} as const;

const MIN_MARGIN = 40;

export interface Layout {
  readonly gap: number;
  /** The Now column is narrower than the Photograph ornament's full face (under ~1200 wide). */
  readonly compact: boolean;
  readonly now: Box;
  readonly places: Box;
  readonly today: Box;
  readonly search: Box;
  /** Where the Photograph ornament's closed end stands; its width is its own content's. */
  readonly photograph: Box;
}

/**
 * The gap two groups need, from the material this root selected, the scheme it resolved and the
 * accessibility policy in force. Each group is passed a box that CONTAINS its member, so the
 * answer is an upper bound (the law is monotone in a member's extents), rounded up to a whole
 * pixel so that a gap equal to the padding is strictly clear rather than level with it.
 *
 * Two floors under it. The scene's own advisory padding, which a group keeps even where the
 * material draws no blur (forced colours) — the overlap check reads it. And the nominal policy's
 * answer: a preference that REMOVES blur must not pull the windows together, so the composition
 * only ever opens (Reduce Transparency) and never closes; that is still the runtime's number,
 * taken at the larger of two policies, not a constant.
 */
export function derivedGap(
  document: GlassMaterialProfileDocument,
  scheme: "light" | "dark",
  material: ResolvedMaterialPolicy,
): number {
  const members: readonly (readonly [number, number])[] = [
    [DESIGN.now.width, DESIGN.now.height],
    [DESIGN.places.width, DESIGN.places.height],
    [DESIGN.today.width, DESIGN.today.height],
    [DESIGN.places.width - 2 * DESIGN.search.inset, DESIGN.search.height],
    [DESIGN.platter.width, DESIGN.platter.height],
  ];
  const endpoint = document.active[scheme];
  let widest: number = DEFAULT_GROUP_SAMPLING.samplingPadding;
  for (const policy of [material, NOMINAL_ACCESSIBILITY_POLICY.material]) {
    for (const member of members) {
      widest = Math.max(
        widest,
        samplingPaddingFor({
          members: [member],
          material: policy,
          profile: endpoint.patch,
          cssTierMapping: document.cssTierMapping,
        }),
      );
    }
  }
  return Math.ceil(widest);
}

export function computeLayout(viewport: { width: number; height: number }, gap: number): Layout {
  const designed = DESIGN.now.width + DESIGN.places.width + DESIGN.today.width;
  const available = viewport.width - 2 * MIN_MARGIN - 2 * gap;
  const scale = Math.min(1, available / designed);
  const nowWidth = Math.round(DESIGN.now.width * scale);
  const placesWidth = Math.round(DESIGN.places.width * scale);
  const todayWidth = Math.round(DESIGN.today.width * scale);
  const left = Math.round((viewport.width - (nowWidth + placesWidth + todayWidth + 2 * gap)) / 2);

  const top = viewport.height >= 820 ? 48 : 32;
  const windowsTop = top + DESIGN.search.height + gap;
  const bottomBand = viewport.height >= 820 ? 112 : 40;

  const placesX = left + nowWidth + gap;
  const todayX = placesX + placesWidth + gap;
  const searchWidth = placesWidth - 2 * DESIGN.search.inset;
  // Below full width the module's date and conditions wrap; it takes the extra line's height.
  const nowHeight = DESIGN.now.height + (scale < 0.85 ? 44 : 0);

  return {
    gap,
    compact: nowWidth < DESIGN.photograph.width,
    now: { x: left, y: windowsTop, width: nowWidth, height: nowHeight },
    places: { x: placesX, y: windowsTop, width: placesWidth, height: DESIGN.places.height },
    today: {
      x: todayX,
      y: windowsTop,
      width: todayWidth,
      height: Math.max(320, Math.min(DESIGN.today.height, viewport.height - windowsTop - bottomBand)),
    },
    search: {
      x: placesX + DESIGN.search.inset,
      y: top,
      width: searchWidth,
      height: DESIGN.search.height,
    },
    photograph: {
      x: left,
      y: windowsTop + nowHeight + gap,
      width: nowWidth,
      height: DESIGN.photograph.height,
    },
  };
}

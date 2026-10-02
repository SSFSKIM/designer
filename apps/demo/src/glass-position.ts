/**
 * Which macOS 27 glass position a page draws (W43 G3 (iii), charter clause 13 and X45; claims
 * §5.201).
 *
 * macOS 27's Glass appearance slider is a material axis: Apple's own pixels move with it, so the
 * project measures each position it ships as a material of its own, and every macOS 27 profile key
 * ends in the position it was captured at (`-glass0.5`, `-glass0.25`). The runtime ships two:
 * `macos27MaterialProfileDocument` at the system default, 0.5, and
 * `macos27Glass025MaterialProfileDocument` at 0.25, the clearer glass. A root selects one at
 * construction, so a page that offers both offers them the way it offers the renderer: one query
 * parameter, `?glass=0.25`, read once before the root is built, and a reload to change it.
 *
 * This module holds only what is pure, because `scenes.ts` and `calibration.ts` read the position
 * and both are evaluated in Node (the build's reduction and the unit suite) where the runtime's
 * documents do not resolve. The documents themselves are paired with these positions in
 * `glass-document.tsx`, which only the browser pages import.
 */

/** The positions the runtime ships a macOS 27 document for, the default first. */
export const GLASS_POSITIONS = [0.5, 0.25] as const;

export type GlassPosition = (typeof GLASS_POSITIONS)[number];

/** The system default, and what a page draws when the query names no position. */
export const DEFAULT_GLASS: GlassPosition = 0.5;

/** What a control or a caption calls a position. */
export const GLASS_LABELS: Readonly<Record<GlassPosition, string>> = {
  0.5: "0.5, the system default",
  0.25: "0.25, the clearer glass",
};

/**
 * The position a page's query asks for. Anything other than a shipped position is the default,
 * because a query is a request: the page draws, and its readouts name, the position it got.
 */
export function glassPositionFrom(search: string): GlassPosition {
  const asked = Number(new URLSearchParams(search).get("glass"));
  return GLASS_POSITIONS.find((position) => position === asked) ?? DEFAULT_GLASS;
}

/**
 * The position a profile key names, by its trailing token; `undefined` for a key with none, which
 * is every macOS 26.5 key (that release has no slider).
 */
export function glassOfProfileKey(profileKey: string): number | undefined {
  const token = /-glass(\d+(?:\.\d+)?)(?:-receded)?$/.exec(profileKey)?.[1];
  return token === undefined ? undefined : Number(token);
}

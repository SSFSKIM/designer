/**
 * The glass position a browser page was opened at, the document it builds its root with, and the
 * control that changes it (W43 G3 (iii), charter clause 13 and X45; claims §5.201).
 *
 * Read once, at module scope, from `?glass=`: `createGlassRoot` selects its material document at
 * construction, so the site, `/laws/` and the playground each pass `PAGE_DOCUMENT` to their one
 * `GlassRoot` and a different position is a reload, exactly as a different renderer is. The
 * readouts that name what drew (`GlassGroupState.materialDocument`) are the check on this: they
 * report the endpoint the runtime resolved, never the position the query asked for.
 */

import {
  macos27Glass025MaterialProfileDocument,
  macos27MaterialProfileDocument,
  type GlassMaterialProfileDocument,
} from "@vitreajs/vitrea-web";
import type { ReactNode } from "react";

import {
  DEFAULT_GLASS,
  GLASS_LABELS,
  GLASS_POSITIONS,
  glassPositionFrom,
  type GlassPosition,
} from "./glass-position";

/** The shipped macOS 27 document at each position. */
export const MATERIAL_DOCUMENT_BY_GLASS: Readonly<
  Record<GlassPosition, GlassMaterialProfileDocument>
> = {
  0.5: macos27MaterialProfileDocument,
  0.25: macos27Glass025MaterialProfileDocument,
};

export const PAGE_GLASS: GlassPosition = glassPositionFrom(window.location.search);

export const PAGE_DOCUMENT: GlassMaterialProfileDocument = MATERIAL_DOCUMENT_BY_GLASS[PAGE_GLASS];

/** Reloads at another position, leaving every other query parameter as it was. */
export function reloadAtGlass(glass: GlassPosition): void {
  const url = new URL(window.location.href);
  if (glass === DEFAULT_GLASS) url.searchParams.delete("glass");
  else url.searchParams.set("glass", String(glass));
  window.location.assign(url.toString());
}

/**
 * The site's and `/laws/`'s control, in the idiom of their renderer field: a select whose hint
 * says that it reloads and why. The hint's second sentence is the page's own, because what
 * follows the position differs from page to page.
 */
export function GlassPositionField(props: { readonly hint: string }): ReactNode {
  return (
    <label className="field">
      <span className="field__label">Glass position</span>
      <select
        value={String(PAGE_GLASS)}
        onChange={(event) => reloadAtGlass(glassPositionFrom(`?glass=${event.target.value}`))}
        data-testid="glass-select"
      >
        {GLASS_POSITIONS.map((glass) => (
          <option key={glass} value={String(glass)}>
            {GLASS_LABELS[glass]}
          </option>
        ))}
      </select>
      <span className="field__hint">
        macOS 27&rsquo;s Glass appearance slider, measured at each position the runtime ships.
        Reloads the page: a root selects its material once, at construction. {props.hint}
      </span>
    </label>
  );
}

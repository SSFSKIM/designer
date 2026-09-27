/**
 * The Search ornament: the page's lead. A search form on a capsule of glass, in the overlay
 * plane and its own group, hung above the Places window — centred on it, narrower than it, and
 * outside its edge by the runtime-derived gap, so on the texture path it samples the environment
 * it actually stands over rather than straddling the window's glass.
 *
 * Search and places are one act, "go": as the person types, the first place whose name starts
 * with the query is lifted in the window below and named at the ornament's end, and Return goes
 * there; an address goes to the address; anything else is a web search.
 */

import { GlassGroup, GlassSurface, type BackdropHint } from "@vitreajs/vitrea-react";
import type { GlassHostHandle } from "@vitreajs/vitrea-web";
import { useEffect, useRef, type FormEvent, type ReactNode } from "react";

import type { Place } from "./data";
import type { Box } from "./environment";
import { ReturnGlyph, SearchGlyph } from "./icons";
import { ENVIRONMENT_BACKDROP, THICKNESS, boxStyle, type GroupMaterial } from "./shared";

function destination(query: string, match: Place | undefined): string | undefined {
  const text = query.trim();
  if (text === "") return undefined;
  if (match !== undefined) return match.href;
  if (/^[\w-]+(\.[\w-]+)+(\/\S*)?$/.test(text)) return `https://${text}`;
  if (/^https?:\/\//.test(text)) return text;
  return `https://duckduckgo.com/?q=${encodeURIComponent(text)}`;
}

export function SearchOrnament(props: {
  readonly box: Box;
  readonly hint: BackdropHint | undefined;
  readonly material: GroupMaterial;
  readonly query: string;
  readonly match: Place | undefined;
  readonly onQuery: (query: string) => void;
  readonly onHost: (handle: GlassHostHandle | null) => void;
}): ReactNode {
  const { box, hint, material, query, match, onQuery, onHost } = props;
  const input = useRef<HTMLInputElement>(null);

  /*
   * The field takes focus on arrival, and a ring there at rest would be a second edge on the
   * lead for nobody's benefit; so the focus ring appears once the person is navigating by keys
   * (Tab, `/`) and goes when they point. The caret marks the field either way.
   */
  useEffect(() => {
    const root = document.documentElement;
    const keys = (event: KeyboardEvent): void => {
      if (event.key === "Tab" || event.key === "/") root.dataset.navigation = "keys";
    };
    const pointer = (): void => {
      delete root.dataset.navigation;
    };
    window.addEventListener("keydown", keys, true);
    window.addEventListener("pointerdown", pointer, true);
    return () => {
      window.removeEventListener("keydown", keys, true);
      window.removeEventListener("pointerdown", pointer, true);
    };
  }, []);

  // `/` from anywhere on the page returns to the search, the way a start page is used.
  useEffect(() => {
    const onKey = (event: KeyboardEvent): void => {
      if (event.key !== "/" || event.metaKey || event.ctrlKey || event.altKey) return;
      const target = event.target as HTMLElement | null;
      if (target !== null && (target.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName))) return;
      event.preventDefault();
      input.current?.focus();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const submit = (event: FormEvent): void => {
    event.preventDefault();
    const url = destination(query, match);
    if (url !== undefined) window.location.assign(url);
  };

  return (
    <GlassGroup id="search" backdrop={ENVIRONMENT_BACKDROP} hint={hint} {...material}>
      <GlassSurface
        asChild
        plane="overlay"
        capsule
        interactive
        thickness={THICKNESS}
        foreground="vibrant"
        onHost={onHost}
      >
        <form
          role="search"
          aria-label="Search the web or go to a place"
          data-glass-role="ornament"
          className="glass ornament search"
          style={boxStyle(box)}
          onSubmit={submit}
        >
          <div className="search-inner">
          <SearchGlyph size={20} className="search-glyph" />
          <input
            ref={input}
            className="search-field"
            type="search"
            name="q"
            value={query}
            onChange={(event) => onQuery(event.target.value)}
            placeholder="Search or type an address"
            aria-label="Search the web or type an address"
            autoComplete="off"
            spellCheck={false}
            // A start page opens to be typed into: the lead takes focus on arrival.
            autoFocus
          />
          <span className="search-target" aria-live="polite">
            {match === undefined ? null : (
              <>
                <ReturnGlyph size={16} />
                <span>
                  <span className="visually-hidden">Return goes to </span>
                  {match.name}
                </span>
              </>
            )}
          </span>
          </div>
        </form>
      </GlassSurface>
    </GlassGroup>
  );
}

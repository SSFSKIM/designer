/**
 * The floating layer: one row of three groups over the still.
 *
 * `nav` and `days` read the still as a texture, because the scroll edge guarantees that only the
 * still is ever behind the bar. `tickets` samples the DOM: its platter opens over the programme
 * sheet whenever the page is scrolled, and a texture group there would refract the film where the
 * reader sees paper. Every group's hint is measured by the page off what it displays under the
 * group's footprint (`beneath.ts`) and handed in here.
 *
 * The row is portalled once into the base plane's host layer, so its three groups lay out as one
 * flex row. The Tickets morph portals its own platter so it can be promoted to the overlay plane,
 * and leaves a spacer in this row that holds its footprint.
 */

import {
  GlassGroup,
  GlassMorph,
  GlassSegmentedControl,
  GlassSurface,
  PlanePortal,
  useGlassAccessibility,
  type BackdropHint,
} from "@vitreajs/vitrea-react";
import { useRef, type KeyboardEvent, type ReactNode, type Ref } from "react";

import type { Ink } from "./beneath";
import { DAYS, FESTIVAL, PASSES, type DayId, type PassId } from "./data";
import { STILL_SOURCE_ID } from "./Still";

const STILL = { kind: "texture", id: STILL_SOURCE_ID } as const;

/**
 * The Tickets morph's geometry, shared with the page, which measures what lies under the open
 * platter before it grows there: the capsule's radius, the platter's, and the gap that puts the
 * platter's top edge where the capsule's was (below-end, so the two share their right edge).
 */
export const TICKETS_RADIUS = 24;
export const PLATTER_RADIUS = 28;
export const PLATTER_GAP = -48;

/** The red of the "50" sign's ring, lifted from its overcast reading of rgb(156 32 40). */
export const TICKETS_TINT = "#c42233";

export const SECTIONS = [
  { id: "programme", label: "Programme" },
  { id: "strands", label: "Strands" },
  { id: "passes", label: "Passes" },
  { id: "visit", label: "Visit" },
] as const;

export type SectionId = (typeof SECTIONS)[number]["id"];

export interface BarProps {
  readonly barRef: Ref<HTMLElement>;
  readonly current: SectionId | null;
  readonly day: DayId;
  readonly onDay: (day: DayId) => void;
  readonly ticketsOpen: boolean;
  readonly onTickets: (open: boolean) => void;
  readonly onPass: (pass: PassId) => void;
  /** The day labels' pole, chosen by the page from measurement (styles.css, the day control). */
  readonly daysInk: "dark" | "light";
  /** The Tickets label's pole, chosen by the page the same way. */
  readonly ticketsInk: "dark" | "light";
  /** Called when the tickets morph reaches the end it was sent to. */
  readonly onTicketsSettled: (open: boolean) => void;
  /**
   * Each group's backdrop, measured by the page under its footprint. A declared hint overrides the
   * runtime's own tone reading on both tiers, the texture groups included: on the WebGPU tier they
   * still refract the still's own pixels (`analysis: "exact"` names where the pixels come from),
   * but the body's tone and the ink follow these numbers. Undefined until the still has painted.
   */
  readonly navHint: BackdropHint | undefined;
  /**
   * The navigation's and the platter's labels' own poles, chosen by the page from each label's
   * ground (`beneath.ts`, `inkOver`), keyed by link and by pass (the platter's head is `head`). A
   * label without one takes the surface's ink.
   */
  readonly navInks: Readonly<Record<string, Ink>>;
  readonly platterInks: Readonly<Record<string, Ink>>;
  readonly daysHint: BackdropHint | undefined;
  readonly ticketsHint: BackdropHint | undefined;
}

export function Bar(props: BarProps): ReactNode {
  const { barRef, current, day, onDay, daysInk, ticketsInk, ticketsOpen, onTickets, onPass } = props;
  const { onTicketsSettled, navHint, daysHint, ticketsHint, navInks, platterInks } = props;

  /*
   * Remount the morph when Reduce Motion changes. In vitrea-react 0.24.0 GlassMorph memoises its
   * geometry springs on the root's motion profile, so a preference flipped mid-session rebuilds
   * them at zero, and its first-placement guard never places them again: the Tickets capsule
   * collapsed to a 0 x 0 box at the origin and stayed there (measured both ways; DESIGN.md).
   */
  const motionKey = useGlassAccessibility()?.reducedMotion === true ? "reduced" : "full";

  return (
    <PlanePortal plane="base">
      <header ref={barRef} className="ff-bar" aria-label="Festival controls">
        <GlassGroup id="nav" backdrop={STILL} hint={navHint}>
          <GlassSurface asChild capsule interactive thickness={8} foreground="vibrant">
            <nav className="ff-nav" aria-label="Festival">
              <a className="ff-wordmark" href="#top" data-ink={navInks["#top"]}>
                {FESTIVAL.name}
              </a>
              {SECTIONS.map((section) => (
                <a
                  key={section.id}
                  className="ff-nav-link"
                  href={`#${section.id}`}
                  data-ink={navInks[`#${section.id}`]}
                  aria-current={current === section.id ? "true" : undefined}
                >
                  {section.label}
                </a>
              ))}
            </nav>
          </GlassSurface>
        </GlassGroup>

        <GlassGroup id="days" backdrop={STILL} hint={daysHint}>
          <GlassSegmentedControl
            aria-label="Festival day"
            className="ff-days"
            data-ink={daysInk}
            segmentClassName="ff-day"
            indicatorClassName="ff-day-indicator"
            items={DAYS.map((d) => ({ value: d.id, label: d.short, "aria-label": d.long }))}
            value={day}
            onChange={onDay}
            radius={24}
            thickness={8}
            indicatorInset={4}
          />
        </GlassGroup>

        <div className="ff-tickets-slot">
          <GlassGroup id="tickets" hint={ticketsHint} tint={ticketsOpen ? null : TICKETS_TINT}>
            <GlassMorph
              key={motionKey}
              open={ticketsOpen}
              groupId="tickets"
              radius={TICKETS_RADIUS}
              openRadius={PLATTER_RADIUS}
              thickness={8}
              openThickness={8}
              placement="below-end"
              // The platter grows from the capsule in place rather than dropping below it: a
              // negative gap of the capsule's own height puts the open end's top edge where the
              // capsule's was, so "Tickets" stays where the reader pressed it.
              gap={PLATTER_GAP}
              className="ff-tickets"
              onMorphEnd={onTicketsSettled}
            >
              {({ open }) =>
                open ? (
                  <TicketsMenu
                    inks={platterInks}
                    onClose={() => onTickets(false)}
                    onPass={onPass}
                  />
                ) : (
                  <button
                    type="button"
                    className="ff-tickets-trigger"
                    data-ink={ticketsInk}
                    aria-haspopup="menu"
                    aria-expanded="false"
                    onClick={() => onTickets(true)}
                  >
                    Tickets
                    <svg aria-hidden="true" viewBox="0 0 12 12" width="12" height="12">
                      <path d="M2.5 4.5 6 8l3.5-3.5" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </button>
                )
              }
            </GlassMorph>
          </GlassGroup>
        </div>
      </header>
    </PlanePortal>
  );
}

interface TicketsMenuProps {
  readonly inks: Readonly<Record<string, Ink>>;
  readonly onClose: () => void;
  readonly onPass: (pass: PassId) => void;
}

/**
 * The platter's content: a menu of the four ways in. Details and conditions live on the plane,
 * in the Passes section; the platter carries one label and a price per row.
 */
function TicketsMenu(props: TicketsMenuProps): ReactNode {
  const { inks, onClose, onPass } = props;
  const menuRef = useRef<HTMLDivElement>(null);

  const onKeyDown = (event: KeyboardEvent<HTMLDivElement>): void => {
    const items = [...(menuRef.current?.querySelectorAll<HTMLElement>("[role=menuitem]") ?? [])];
    const index = items.indexOf(document.activeElement as HTMLElement);
    let next: HTMLElement | undefined;
    if (event.key === "Escape") {
      event.preventDefault();
      onClose();
      return;
    }
    if (event.key === "ArrowDown") next = items[(index + 1) % items.length];
    else if (event.key === "ArrowUp") next = items[(index - 1 + items.length) % items.length];
    else if (event.key === "Home") next = items[0];
    else if (event.key === "End") next = items[items.length - 1];
    else if (event.key === "Tab") {
      onClose();
      return;
    }
    if (next !== undefined) {
      event.preventDefault();
      next.focus();
    }
  };

  return (
    <div className="ff-platter" ref={menuRef} onKeyDown={onKeyDown}>
      <div className="ff-platter-head" data-ink={inks.head}>
        <span id="ff-tickets-label" className="ff-platter-title">
          Tickets
        </span>
        <button type="button" className="ff-platter-close" aria-label="Close tickets" onClick={onClose}>
          <svg aria-hidden="true" viewBox="0 0 12 12" width="12" height="12">
            <path d="M3 3l6 6M9 3l-6 6" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
          </svg>
        </button>
      </div>
      <div role="menu" aria-labelledby="ff-tickets-label" className="ff-platter-menu">
        {PASSES.map((pass) => (
          <button
            key={pass.id}
            type="button"
            role="menuitem"
            tabIndex={-1}
            className="ff-platter-row"
            data-pass={pass.id}
            data-ink={inks[pass.id]}
            onClick={() => onPass(pass.id)}
          >
            <span>{pass.name}</span>
            <span className="ff-platter-price">£{pass.price}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

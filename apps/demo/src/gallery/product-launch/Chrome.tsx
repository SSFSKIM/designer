/**
 * The floating layer: the two bars, and nothing else that is glass.
 *
 * Top: the section navigation capsule (group `nav`) centred, and the display toggle (group
 * `display`) at the trailing edge, where a view setting lives. Bottom: finish, lens and order,
 * three groups because they are three acts (choose, choose, commit) and because a text button may
 * not share a group with a segmented control's body or with the lens platter's morph.
 *
 * Every group reads the one texture, the plane canvas. `hints` is empty on the WebGPU tier and
 * carries a measured declaration per group on the CSS tier (see `DESIGN.md`, groups).
 *
 * Both bars are portalled once into the base plane's host layer by `PlanePortal`, so their
 * surfaces render in place inside the landmark this file writes (`<nav>`, a named region) rather
 * than scattering to the plane root. The wrappers are layout only: no background, no transform,
 * no opacity, nothing the runtime forbids above a host.
 */

import {
  GlassButton,
  GlassGroup,
  GlassIconButton,
  GlassSegmentedControl,
  GlassSurface,
  PlanePortal,
  type BackdropHint,
  type GlassTextureBackdrop,
} from "@vitreajs/vitrea-react";
import { useEffect, type ReactNode, type Ref, type WheelEvent } from "react";

import {
  BODY_PRICE,
  FINISHES,
  formatPrice,
  lensById,
  type FinishId,
  type LensId,
} from "./content";
import { LensMenu, type LensMenuHandle } from "./LensMenu";

export type GroupId = "nav" | "display" | "finish" | "lens" | "order";
export type SectionId = "sensor" | "lenses" | "body" | "price";

export const PLANE_BACKDROP: GlassTextureBackdrop = { kind: "texture", id: "plane" };

export const SECTIONS: readonly { readonly id: SectionId; readonly label: string }[] = [
  { id: "sensor", label: "Sensor" },
  { id: "lenses", label: "Lenses" },
  { id: "body", label: "Body" },
  { id: "price", label: "Price" },
];

interface ChromeProps {
  readonly hints: Partial<Record<GroupId, BackdropHint>>;
  readonly section: SectionId | null;
  readonly finish: FinishId;
  readonly lens: LensId;
  readonly onFinish: (finish: FinishId) => void;
  readonly onLens: (lens: LensId) => void;
  readonly onOrder: () => void;
  readonly onTop: () => void;
  readonly reduceTransparency: boolean;
  readonly onReduceTransparency: (on: boolean) => void;
  /** The runtime-derived distance between two groups in one bar, in CSS px. */
  readonly groupGap: number;
  readonly lensMenuRef: Ref<LensMenuHandle>;
  /** Wheel over a bar scrolls the page beneath it, as it would over a native toolbar. */
  readonly onWheel: (event: WheelEvent) => void;
}

function TransparencyIcon(props: { readonly on: boolean }): ReactNode {
  // A disc half filled: the glass as it is (half the page through it) or, pressed, full: the
  // glass made opaque. The symbol carries the state; aria-pressed says it to assistive tech.
  return (
    <svg viewBox="0 0 20 20" width="19" height="19" aria-hidden="true">
      <circle cx="10" cy="10" r="7.25" fill="none" stroke="currentColor" strokeWidth="1.6" />
      {props.on ? (
        <circle cx="10" cy="10" r="4.6" fill="currentColor" />
      ) : (
        <path d="M10 2.75a7.25 7.25 0 0 1 0 14.5Z" fill="currentColor" />
      )}
    </svg>
  );
}

const TABBABLE =
  'a[href], button:not([disabled]), input:not([disabled]), select, textarea, [tabindex]:not([tabindex="-1"])';

function tabbables(): HTMLElement[] {
  return [...document.querySelectorAll<HTMLElement>(TABBABLE)].filter(
    (element) => element.tabIndex >= 0 && element.getClientRects().length > 0,
  );
}

/** The bottom bar's fixed stops: the checked finish radio (its group's one tab stop), and order. */
const finishStop = (): HTMLElement | null =>
  document.querySelector<HTMLElement>('.finish [role="radio"][tabindex="0"]');
const orderStop = (): HTMLElement | null => document.querySelector<HTMLElement>(".order");

/** Where Tab lands when it leaves the open lens platter: the stops either side of the lens slot. */
function focusBesideLens(direction: "forward" | "backward"): void {
  (direction === "forward" ? orderStop() : finishStop())?.focus();
}

/**
 * Sequential focus through the bottom bar in the order it is drawn: finish, lens, order.
 *
 * The lens chooser's host is a morph, which portals itself to the end of the plane's host layer so
 * that it can be promoted to the overlay plane as a unit; document order therefore puts the lens
 * trigger after the order button. Six hand-offs restore the visual order and nothing else is
 * touched: the trigger's own keys and every other stop keep their defaults. While the platter is
 * open the trigger is not in the document and these hand-offs stand down; the platter routes its
 * own Tab through `focusBesideLens`.
 */
function useBottomBarTabOrder(): void {
  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent): void => {
      if (event.key !== "Tab" || event.altKey || event.ctrlKey || event.metaKey) return;
      const target = event.target instanceof HTMLElement ? event.target : null;
      const finish = finishStop();
      const lens = document.querySelector<HTMLElement>(".lens .lens__trigger");
      const order = orderStop();
      if (target === null || finish === null || lens === null || order === null) return;
      const all = tabbables();
      const afterLens = all[all.indexOf(lens) + 1];
      const route = (next: HTMLElement | undefined): void => {
        if (next === undefined) return;
        event.preventDefault();
        next.focus();
      };
      if (!event.shiftKey) {
        if (target === finish) route(lens);
        else if (target === lens) route(order);
        else if (target === order) route(afterLens);
      } else {
        if (target === lens) route(finish);
        else if (target === order) route(lens);
        else if (target === afterLens) route(order);
      }
    };
    document.addEventListener("keydown", onKeyDown, true);
    return () => document.removeEventListener("keydown", onKeyDown, true);
  }, []);
}

export function Chrome(props: ChromeProps): ReactNode {
  const lens = lensById(props.lens);
  const total = BODY_PRICE + lens.price;
  useBottomBarTabOrder();

  return (
    <PlanePortal plane="base">
      <div className="bar bar--top" onWheel={props.onWheel}>
        <GlassGroup id="nav" backdrop={PLANE_BACKDROP} hint={props.hints.nav}>
          {/* Interactive, so a press on any link lights and flexes the housing the way a glass
              button does; the links stay plain DOM inside it, with no press state of their own. */}
          <GlassSurface asChild capsule thickness={8} foreground="vibrant" interactive>
            <nav className="nav" aria-label="Alder One">
              <a
                className="nav__brand"
                href="#top"
                onClick={(event) => {
                  event.preventDefault();
                  props.onTop();
                }}
              >
                Alder One
              </a>
              <span className="nav__rule" aria-hidden="true" />
              {SECTIONS.map((section) => (
                <a
                  key={section.id}
                  className="nav__link"
                  href={`#${section.id}`}
                  aria-current={props.section === section.id ? "true" : undefined}
                >
                  {section.label}
                </a>
              ))}
            </nav>
          </GlassSurface>
        </GlassGroup>
      </div>

      <div className="corner" onWheel={props.onWheel}>
        <GlassGroup id="display" backdrop={PLANE_BACKDROP} hint={props.hints.display}>
          <GlassIconButton
            className="toggle"
            thickness={8}
            aria-label="Reduce transparency"
            aria-pressed={props.reduceTransparency}
            title={props.reduceTransparency ? "Transparency reduced" : "Reduce transparency"}
            onClick={() => props.onReduceTransparency(!props.reduceTransparency)}
          >
            <TransparencyIcon on={props.reduceTransparency} />
          </GlassIconButton>
        </GlassGroup>
      </div>

      <div
        className="bar bar--bottom"
        role="region"
        aria-label="Configure and order"
        style={{ gap: `${props.groupGap}px` }}
        onWheel={props.onWheel}
      >
        <GlassGroup id="finish" backdrop={PLANE_BACKDROP} hint={props.hints.finish}>
          <GlassSegmentedControl<FinishId>
            aria-label="Finish"
            className="finish"
            indicatorClassName="finish__indicator"
            segmentClassName="finish__segment"
            radius={28}
            thickness={8}
            indicatorInset={5}
            value={props.finish}
            onChange={props.onFinish}
            items={FINISHES.map((finish) => ({
              value: finish.id,
              label: (
                <>
                  <span
                    className="swatch"
                    aria-hidden="true"
                    style={{ background: finish.swatch }}
                  />
                  {finish.name}
                </>
              ),
            }))}
          />
        </GlassGroup>

        <GlassGroup id="lens" backdrop={PLANE_BACKDROP} hint={props.hints.lens}>
          <LensMenu
            value={props.lens}
            onChange={props.onLens}
            handleRef={props.lensMenuRef}
            onTabOut={focusBesideLens}
          />
        </GlassGroup>

        <GlassGroup id="order" backdrop={PLANE_BACKDROP} hint={props.hints.order}>
          <GlassButton
            capsule
            thickness={8}
            className="order"
            aria-label={`Order the Alder One, ${formatPrice(total)}`}
            onClick={props.onOrder}
          >
            <span className="order__verb">Order</span>
            <span className="order__price">{formatPrice(total)}</span>
          </GlassButton>
        </GlassGroup>
      </div>
    </PlanePortal>
  );
}

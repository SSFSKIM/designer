/**
 * The trip planner: the page's whole floating layer.
 *
 * One `GlassToolbar` at the top leading margin, split into three bodies of material by
 * `GlassToolbarSpacer`, each its own sampling group because each is a different job and reads a
 * different stretch of the ridge band (DESIGN.md, inventory and groups):
 *
 *   route    a GlassMorph: the capsule carries the route and its distance; open, it is the
 *            route menu, the page's one platter
 *   weather  a GlassButton: the capsule carries today's weather at the route's high point and
 *            takes the reader to the forecast on the sheet, which reads for the route. The
 *            forecast is a table, and a table is content: it stays on paper (SKILL.md §3, 1)
 *   permits  a GlassButton that takes the reader to the permit steps for the planned route
 *
 * Closed, every capsule sits inside the scroll-edge band, where the sheet is masked away at every
 * scroll position, so what is behind it is the photograph and nothing else: it reads the texture.
 * The route menu opens over the sheet, which the texture does not hold, so from the frame it
 * starts opening until the frame it has finished closing its group samples the DOM instead, and
 * declares what it measured.
 */

import {
  APPLE_LIKE_SMOOTHING,
  GlassButton,
  GlassMorph,
  GlassToolbar,
  GlassToolbarSpacer,
  PlanePortal,
  useToolbarItem,
  type GlassBackdrop,
  type GlassToolbarItemProps,
} from "@vitreajs/vitrea-react";
import { useButton, useMenu, useMenuItem, useMenuSection, useMenuTrigger } from "react-aria";
import type { AriaMenuProps } from "react-aria";
import { Item, Section, useMenuTriggerState, useTreeState } from "react-stately";
import type { Node as CollectionNode, TreeState } from "react-stately";
import {
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
  type Key,
  type ReactNode,
  type RefObject,
} from "react";

import {
  CORRIDORS,
  FORECAST,
  forecastAt,
  formatFt,
  formatMi,
  STATUS_LABEL,
  TRAILS,
  type Trail,
} from "./data";
import { PARK_TEXTURE_ID } from "./ParkPlane";
import { SkyGlyph, RouteGlyph, Chevron } from "./glyphs";
import { useMeasuredHint } from "./useMeasuredHint";

const TEXTURE: GlassBackdrop = { kind: "texture", id: PARK_TEXTURE_ID };
const DOM: GlassBackdrop = { kind: "dom" };

/** The route menu's morph geometry (DESIGN.md, family). */
const MORPH = {
  profile: APPLE_LIKE_SMOOTHING,
  openProfile: APPLE_LIKE_SMOOTHING,
  radius: 24,
  openRadius: 28,
  thickness: 8,
  openThickness: 8,
  placement: "below-start",
  gap: 10,
} as const;

/*
 * The gap between the three bodies. Its minimum is the runtime's own (GlassToolbarSpacer writes
 * the sampling padding as `min-width`), and that minimum moves with the scheme and with Reduce
 * Transparency: 24 / 41 CSS px light, 27 / 48 dark, measured at this span. A member that moves
 * because its neighbour's gap grew is not re-measured by the runtime (no observer sees a host
 * move without resizing), so its glass stays where it was while its label walks out of it.
 * `.pt-planner__gap` therefore gives every state the room of the largest, one capsule height,
 * and the planner's layout never depends on an accessibility preference (DESIGN.md, decisions).
 */

/**
 * Which backdrop a morph's group reads: the texture while it rests in the band, the DOM from the
 * moment it starts opening until the moment it has finished closing.
 */
function useMorphSampling(open: boolean): {
  backdrop: GlassBackdrop;
  onMorphEnd: (open: boolean) => void;
} {
  const [overSheet, setOverSheet] = useState(open);
  if (open && !overSheet) setOverSheet(true);
  return {
    backdrop: overSheet ? DOM : TEXTURE,
    onMorphEnd: (ended) => {
      if (!ended) setOverSheet(false);
    },
  };
}

export interface PlannerProps {
  readonly trail: Trail;
  readonly routeOpen: boolean;
  readonly onRouteOpenChange: (open: boolean) => void;
  readonly onChooseRoute: (id: string) => void;
  readonly onForecast: () => void;
  readonly onPermits: () => void;
}

export function Planner(props: PlannerProps): ReactNode {
  const { trail } = props;
  const route = useMeasuredHint("route");
  const weather = useMeasuredHint("weather");
  const permits = useMeasuredHint("permits");
  const routeSampling = useMorphSampling(props.routeOpen);
  const today = FORECAST[0];
  const now = today === undefined ? undefined : forecastAt(today, trail.highFt);

  /*
   * The toolbar is portalled into the base plane, outside every landmark the page wrote, so the
   * planner re-establishes one of its own around it (SKILL.md, accessibility; vitrea.md §8.9).
   */
  return (
    <PlanePortal plane="base">
      <section className="pt-banner" aria-label="Trip planner">
        <GlassToolbar id="pt-planner" aria-label="Plan a trip" className="pt-planner">
          <RouteMenu
            sharedBackground="hidden"
            groupProps={{
              id: "route",
              backdrop: routeSampling.backdrop,
              ...(route.hint === undefined ? {} : { hint: route.hint }),
            }}
            trail={trail}
            open={props.routeOpen}
            onOpenChange={props.onRouteOpenChange}
            onChoose={props.onChooseRoute}
            onMorphEnd={routeSampling.onMorphEnd}
          />
          <GlassToolbarSpacer kind="fixed" className="pt-planner__gap" />
          <GlassButton
            sharedBackground="hidden"
            groupProps={{
              id: "weather",
              backdrop: TEXTURE,
              ...(weather.hint === undefined ? {} : { hint: weather.hint }),
            }}
            capsule
            className="pt-control pt-control--weather"
            onClick={props.onForecast}
            aria-label={
              now === undefined
                ? `Forecast for ${trail.name}`
                : `Weather at ${trail.name}'s high point today: ${String(now.highF)} degrees, ` +
                  `${now.word}. Go to the forecast`
            }
          >
            <WeatherFace trail={trail} />
          </GlassButton>
          <GlassToolbarSpacer kind="fixed" className="pt-planner__gap" />
          <GlassButton
            sharedBackground="hidden"
            groupProps={{
              id: "permits",
              backdrop: TEXTURE,
              ...(permits.hint === undefined ? {} : { hint: permits.hint }),
            }}
            capsule
            className="pt-control"
            onClick={props.onPermits}
            aria-label={`Permit steps for ${trail.name}`}
          >
            <span className="pt-control__label">Permits</span>
          </GlassButton>
        </GlassToolbar>
      </section>
    </PlanePortal>
  );
}

/* ── Route menu ──────────────────────────────────────────────────────────── */

interface RouteMenuProps extends GlassToolbarItemProps {
  readonly trail: Trail;
  readonly open: boolean;
  readonly onOpenChange: (open: boolean) => void;
  readonly onChoose: (id: string) => void;
  readonly onMorphEnd: (open: boolean) => void;
}

function RouteMenu(props: RouteMenuProps): ReactNode {
  const { trail } = props;
  const state = useMenuTriggerState({ isOpen: props.open, onOpenChange: props.onOpenChange });
  const triggerRef = useRef<HTMLButtonElement>(null);
  const menuRef = useRef<HTMLUListElement>(null);
  const { menuTriggerProps, menuProps } = useMenuTrigger<object>({}, state, triggerRef);
  const { buttonProps } = useButton(menuTriggerProps, triggerRef);
  const toolbarItem = useToolbarItem();
  useReturnFocus(state.isOpen, triggerRef);
  useClaimFocus(state.isOpen, menuRef);
  useDismiss(state.isOpen, menuRef, () => state.close());

  return (
    <span className="pt-slot">
      <span className="pt-control pt-slot__sizer" aria-hidden="true">
        <RouteFace trail={trail} />
      </span>
      <GlassMorph
        {...MORPH}
        open={state.isOpen}
        groupId="route"
        className="pt-platter"
        aria-label="Route"
        onMorphEnd={props.onMorphEnd}
      >
        {({ open }) =>
          open ? (
            <RouteList
              {...menuProps}
              menuRef={menuRef}
              aria-label="Choose a route"
              autoFocus={state.focusStrategy ?? "first"}
              selected={trail.id}
              onChoose={(key) => {
                props.onChoose(String(key));
                state.close();
              }}
              onClose={() => state.close()}
            >
              {CORRIDORS.map((corridor) => (
                <Section key={corridor.id} title={corridor.name}>
                  {TRAILS.filter((candidate) => candidate.corridor === corridor.id).map((candidate) => (
                    <Item key={candidate.id} textValue={candidate.name}>
                      <span className="pt-option__name">{candidate.name}</span>
                      <span className="pt-option__meta">
                        {formatMi(candidate.distanceMi)} · ↑ {formatFt(candidate.gainFt)}
                        {candidate.status === "open" ? "" : ` · ${STATUS_LABEL[candidate.status]}`}
                      </span>
                    </Item>
                  ))}
                </Section>
              ))}
            </RouteList>
          ) : (
            <button
              {...buttonProps}
              {...toolbarItem}
              ref={triggerRef}
              type="button"
              className="pt-control pt-control--route"
              aria-label={
                `Route: ${trail.name}, ${formatMi(trail.distanceMi)} ${trail.shape}, ` +
                `${formatFt(trail.gainFt)} of climbing. Change route`
              }
            >
              <RouteFace trail={trail} />
            </button>
          )
        }
      </GlassMorph>
    </span>
  );
}

/*
 * The capsules' faces stack every label they can ever show in one grid cell, the current one
 * visible, so a capsule's width is its widest label from the first layout onward. That is what
 * lets the morph measure its closed end once and never be wrong about it, and what keeps a
 * registered neighbour from being pushed along when a route with a longer name is chosen.
 */
function RouteFace(props: { readonly trail: Trail }): ReactNode {
  return (
    <>
      <RouteGlyph />
      <span className="pt-stack">
        {TRAILS.map((candidate) => (
          <span
            key={candidate.id}
            className="pt-stack__item"
            data-current={candidate.id === props.trail.id || undefined}
          >
            <span className="pt-control__strong">{candidate.name}</span>
            <span className="pt-control__quiet">
              {formatMi(candidate.distanceMi)} · ↑ {formatFt(candidate.gainFt)}
            </span>
          </span>
        ))}
      </span>
      <Chevron />
    </>
  );
}

/** No chevron: a chevron promises a menu, and this capsule goes somewhere instead. */
function WeatherFace(props: { readonly trail: Trail }): ReactNode {
  const today = FORECAST[0];
  if (today === undefined) return null;
  const current = forecastAt(today, props.trail.highFt);
  return (
    <>
      <SkyGlyph sky={current.sky} />
      <span className="pt-stack">
        {TRAILS.map((candidate) => {
          const point = forecastAt(today, candidate.highFt);
          return (
            <span
              key={candidate.id}
              className="pt-stack__item"
              data-current={candidate.id === props.trail.id || undefined}
            >
              <span className="pt-control__strong">{point.highF}°</span>
              <span className="pt-control__quiet">{point.word}</span>
            </span>
          );
        })}
      </span>
    </>
  );
}

type RouteListProps = AriaMenuProps<object> & {
  readonly menuRef: RefObject<HTMLUListElement | null>;
  readonly selected: string;
  readonly onChoose: (key: Key) => void;
  readonly onClose: () => void;
};

function RouteList(props: RouteListProps): ReactNode {
  const state = useTreeState({
    ...props,
    selectionMode: "single",
    selectedKeys: [props.selected],
    disallowEmptySelection: true,
  });
  const { menuProps } = useMenu(props, state, props.menuRef);

  return (
    <ul
      {...menuProps}
      ref={props.menuRef}
      className="pt-menu"
      onKeyDownCapture={(event) => {
        menuProps.onKeyDownCapture?.(event);
        if (event.key !== "Escape") return;
        event.stopPropagation();
        props.onClose();
      }}
    >
      {[...state.collection].map((section) => (
        <RouteSection key={section.key} section={section} state={state} onChoose={props.onChoose} />
      ))}
    </ul>
  );
}

function RouteSection(props: {
  readonly section: CollectionNode<object>;
  readonly state: TreeState<object>;
  readonly onChoose: (key: Key) => void;
}): ReactNode {
  const { section, state } = props;
  const { itemProps, headingProps, groupProps } = useMenuSection({ heading: section.rendered });
  return (
    <li {...itemProps} className="pt-menu__section">
      <span {...headingProps} className="pt-menu__heading">
        {section.rendered}
      </span>
      <ul {...groupProps} className="pt-menu__group">
        {[...(state.collection.getChildren?.(section.key) ?? section.childNodes)].map((node) => (
          <RouteOption key={node.key} item={node} state={state} onChoose={props.onChoose} />
        ))}
      </ul>
    </li>
  );
}

function RouteOption(props: {
  readonly item: CollectionNode<object>;
  readonly state: TreeState<object>;
  readonly onChoose: (key: Key) => void;
}): ReactNode {
  const ref = useRef<HTMLLIElement>(null);
  const { menuItemProps, isFocused, isSelected } = useMenuItem(
    { key: props.item.key, onAction: props.onChoose },
    props.state,
    ref,
  );
  return (
    <li
      {...menuItemProps}
      ref={ref}
      className="pt-option"
      data-focused={isFocused || undefined}
      data-selected={isSelected || undefined}
    >
      <span className="pt-option__check" aria-hidden="true">
        {isSelected ? "✓" : ""}
      </span>
      <span className="pt-option__text">{props.item.rendered}</span>
    </li>
  );
}

/* ── Focus and dismissal ─────────────────────────────────────────────────── */

/**
 * When the platter closes, focus goes back to the trigger the morph re-renders in place, but only
 * if focus went down with the platter (it was inside, and has fallen to the body). A close that is
 * a dismissal or a choice lands there; a close that sent focus somewhere on purpose, a navigation
 * to a section of the sheet or a press on a control outside, keeps it where it went.
 */
function useReturnFocus(open: boolean, trigger: RefObject<HTMLButtonElement | null>): void {
  const wasOpen = useRef(open);
  useLayoutEffect(() => {
    if (wasOpen.current && !open) {
      const active = document.activeElement;
      if (active === null || active === document.body) {
        trigger.current?.focus({ preventScroll: true });
      }
    }
    wasOpen.current = open;
  }, [open, trigger]);
}

/**
 * Put focus inside the platter once the press that opened it is over. The trigger has already
 * become the platter, so a focus React Aria hands back to the trigger on release would fall to
 * the body; the same composition the demo's own actions menu writes.
 */
function useClaimFocus(open: boolean, target: RefObject<HTMLElement | null>): void {
  useEffect(() => {
    if (!open) return;
    const claim = (): void => {
      requestAnimationFrame(() => {
        const element = target.current;
        if (element === null) return;
        if (element.contains(element.ownerDocument.activeElement)) return;
        element.focus({ preventScroll: true });
      });
    };
    claim();
    document.addEventListener("pointerup", claim);
    return () => document.removeEventListener("pointerup", claim);
  }, [open, target]);
}

/** A press outside the platter closes it, the way a popover does. */
function useDismiss(open: boolean, panel: RefObject<HTMLElement | null>, close: () => void): void {
  const closeRef = useRef(close);
  closeRef.current = close;
  useEffect(() => {
    if (!open) return;
    const onPointerDown = (event: PointerEvent): void => {
      const host = panel.current?.closest("[data-vitrea-morph]");
      const target = event.target;
      if (host instanceof HTMLElement && target instanceof Node && host.contains(target)) return;
      closeRef.current();
    };
    document.addEventListener("pointerdown", onPointerDown, true);
    return () => document.removeEventListener("pointerdown", onPointerDown, true);
  }, [open, panel]);
}

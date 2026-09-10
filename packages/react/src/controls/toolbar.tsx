/**
 * `GlassToolbar` — the group container, with the WAI-ARIA toolbar pattern.
 *
 * Two things at once, and they are the same thing seen from two sides:
 *
 * - **A sampling group.** Members of one `GlassGroup` share a backdrop source and
 *   a proxy, and their fields union with bounded smooth-min proximity, which is
 *   what makes a row of buttons read as one piece of material rather than several.
 *   That is Apple's `GlassEffectContainer`, and it is why a toolbar creates a
 *   group by default.
 * - **A toolbar.** `role="toolbar"` with one tab stop: Tab reaches the toolbar,
 *   arrows move within it. A row of ten buttons that each take a tab stop is the
 *   thing this pattern exists to prevent.
 *
 * ## Splitting the shared background
 *
 * Apple gives a toolbar two ways to break its glass into separate bodies —
 * `ToolbarSpacer`, a gap at a position, and `sharedBackgroundVisibility(.hidden)`,
 * a single item stepping out — and both reduce to one rule here: **the children
 * are partitioned into sampling groups at each `GlassToolbarSpacer` and at each
 * item that declares `sharedBackground="hidden"`.** The result is one
 * `role="toolbar"` with N groups, never N toolbars (W27 §Design, X5).
 *
 * That the split changes grouping and *nothing else* is a property of what a
 * group is, not a promise this file keeps by hand: `GlassGroup` renders no DOM,
 * so the toolbar's flex row is untouched, and `membersOf` below orders the
 * roving tab stop over the whole document by plane anchors, so it never saw the
 * grouping in the first place. Union and proxies were already per group.
 *
 * The partition is **structural, not animated**. Moving a boundary at runtime —
 * rendering a spacer conditionally, flipping an item's `sharedBackground` —
 * moves the members that changed partition between two providers, and React
 * remounts an element that changes parent: the groups re-derive correctly and
 * nothing leaks, but that member's DOM node is rebuilt, so focus and any
 * uncontrolled DOM state in it do not survive the change. Decide a toolbar's
 * partition the way its item set is decided, not per frame.
 *
 * The one thing a partition must buy is room. Two adjacent groups each sample a
 * padded region around their own shapes, and where one group's padded box covers
 * the other's shapes the backdrop filter applies twice over the overlap
 * (`proxy-overlap-after-enforcement`, and core's own `group-proxy-overlap`). So
 * a spacer's minimum is derived rather than written down: the sampling padding
 * the material actually requires under the resolved accessibility policy, and
 * never less than the advisory core checks against. A constant of this file's
 * own would be wrong under Reduce Transparency, which is exactly the preference
 * that enlarges the blur.
 *
 * The toolbar is deliberately **not** a glass surface. X1 forbids two glass
 * surfaces overlapping inside one plane — the sandwich cannot put one surface's
 * body above another surface's label — so a glass platter wrapping glass buttons
 * would be a checked dev-mode error. The container is plain DOM; the material
 * comes from its members' union.
 *
 * Tab stops are managed on the DOM rather than through props. An item declares
 * itself with a data attribute and nothing else, so a custom control in a toolbar
 * joins the roving order by rendering `useToolbarItem()`'s props — no index, no
 * registration order, and nothing to keep in sync when children reorder.
 */

import {
  DEFAULT_GROUP_SAMPLING,
  NOMINAL_ACCESSIBILITY_POLICY,
  type GlassPlane,
} from "@vitreajs/vitrea";
import { samplingPaddingFor } from "@vitreajs/vitrea-web";
import {
  Children,
  createContext,
  isValidElement,
  useCallback,
  useContext,
  useEffect,
  useId,
  useMemo,
  useState,
  type CSSProperties,
  type FocusEvent as ReactFocusEvent,
  type HTMLAttributes,
  type KeyboardEvent as ReactKeyboardEvent,
  type ReactNode,
} from "react";

import { GlassGroup, type GlassGroupProps } from "../group";
import { PlanePortal, PLANE_ANCHOR_ATTRIBUTE } from "../plane-portal";
import { useGlassAccessibility } from "../root";

/**
 * The attribute a toolbar item marks itself with, carrying its toolbar's id.
 *
 * The id matters because membership is not containment. A control that portals
 * itself — a morph platter that will be promoted to the overlay plane, for
 * instance — is not a DOM descendant of the toolbar, and it is still one of its
 * items: it is reachable with the arrows, it holds the single tab stop when it is
 * the active one, and a screen reader should read it inside the toolbar. Marking
 * the owner lets the toolbar find its items wherever they ended up.
 */
export const TOOLBAR_ITEM_ATTRIBUTE = "data-vitrea-toolbar-item";

export type ToolbarItemProps = { readonly "data-vitrea-toolbar-item"?: string };

export type ToolbarOrientation = "horizontal" | "vertical";

/**
 * What the surrounding toolbar tells its items and its spacers.
 *
 * The gap is here rather than on the spacer because it is a property of the
 * toolbar's material and layout, not of any one spacer: every spacer in one
 * toolbar opens the same minimum, and it moves for all of them at once when an
 * accessibility preference moves the blur.
 */
interface ToolbarScope {
  readonly id: string;
  readonly orientation: ToolbarOrientation;
  /** The minimum a spacer opens between two partitions, in CSS px. */
  readonly gap: number;
}

const ToolbarContext = createContext<ToolbarScope | null>(null);

/** Props that opt a control into the toolbar's roving tab order. `{}` outside one. */
export function useToolbarItem(): ToolbarItemProps {
  const toolbarId = useContext(ToolbarContext)?.id ?? null;
  return useMemo(
    () => (toolbarId === null ? {} : { [TOOLBAR_ITEM_ATTRIBUTE]: toolbarId }),
    [toolbarId],
  );
}

/** Apple's `sharedBackgroundVisibility`: whether this item joins the toolbar's glass. */
export type ToolbarSharedBackground = "shared" | "hidden";

/**
 * The two props `GlassToolbar` reads off its own children, and never passes on.
 *
 * They are declared on the controls rather than on the toolbar because that is
 * where Apple puts them and where an author looks for them: a primary action
 * says it is not part of the shared background, in place, beside its label.
 * Outside a toolbar — or on a child that is not a *direct* child of one — both
 * are inert, and the control that declares them drops them rather than passing
 * an unknown attribute to the DOM.
 */
export interface GlassToolbarItemProps {
  /**
   * `"hidden"` gives this item a sampling group of its own, so its glass is a
   * separate body from the toolbar's — Apple's `sharedBackgroundVisibility(.hidden)`.
   * Put a `GlassToolbarSpacer` beside it: the split is what separates the two
   * bodies logically, and the spacer is what leaves room for the two proxies.
   */
  readonly sharedBackground?: ToolbarSharedBackground | undefined;
  /**
   * The group props for *this item's* own group, merged over the toolbar's.
   * Only read on a `sharedBackground="hidden"` item, which is the only partition
   * that is one item's to configure.
   *
   * This is how two tints coexist in one toolbar: one group carries one seed
   * (`tint-mixing` fires on two), so a tinted primary action is a tinted group
   * of one — `groupProps={{ tint: "…" }}` on the item that stepped out. An `id`
   * here is taken as written, since it names one group and not a series.
   */
  readonly groupProps?: Omit<GlassGroupProps, "children"> | undefined;
}

/** The keys above, as data: what a control has to drop before it reaches an element. */
const TOOLBAR_ITEM_KEYS = ["sharedBackground", "groupProps"] as const;

/**
 * A control's props with the toolbar-protocol pair removed.
 *
 * A control declaring them has to drop them — `sharedBackground` would reach the
 * DOM as an unknown attribute and `groupProps` as `[object Object]` — and the
 * removal lives here, beside the declaration, so a second control does not
 * arrive at its own spelling of the same list.
 */
export function withoutToolbarItemProps<T extends GlassToolbarItemProps>(
  props: T,
): Omit<T, keyof GlassToolbarItemProps> {
  const rest = { ...props } as Record<string, unknown>;
  for (const key of TOOLBAR_ITEM_KEYS) delete rest[key];
  return rest as Omit<T, keyof GlassToolbarItemProps>;
}

/** `.fixed` holds the minimum; `.flexible` also takes whatever room is going. */
export type ToolbarSpacerKind = "fixed" | "flexible";

export interface GlassToolbarSpacerProps
  extends Omit<HTMLAttributes<HTMLDivElement>, "children"> {
  readonly kind?: ToolbarSpacerKind | undefined;
}

/**
 * `GlassToolbarSpacer` — Apple's `ToolbarSpacer`: a gap that is also a split.
 *
 * The gap is a **minimum**, written as `min-width` (or `min-height` in a
 * vertical toolbar) so that the toolbar's own `gap`, or a margin, or a width the
 * author gives it, all add to it rather than fight it. The number is the
 * sampling padding the surrounding toolbar derived — see `GlassToolbar` — and it
 * is what keeps the two partitions' padded proxies off each other's shapes.
 *
 * An author's own `style` still wins, and deliberately: a number someone wrote
 * is a statement about their geometry, and the runtime overruling it would be a
 * worse defect than the one this prevents — the same reading `resolveSamplingGeometry`
 * takes of an authored `samplingPadding`. `proxy-overlap-after-enforcement` is
 * the backstop either way, and it names the fix.
 *
 * Outside a toolbar the element is still a spacer, with no minimum: there is no
 * partition to separate, so there is no padding to clear.
 */
export function GlassToolbarSpacer(props: GlassToolbarSpacerProps): ReactNode {
  const { kind = "fixed", style, ...rest } = props;
  const scope = useContext(ToolbarContext);
  const gap = scope?.gap ?? 0;

  const sizing: CSSProperties =
    scope?.orientation === "vertical" ? { minHeight: gap } : { minWidth: gap };

  return (
    <div
      aria-hidden="true"
      data-vitrea-toolbar-spacer={kind}
      {...rest}
      style={{ flex: kind === "flexible" ? "1 1 auto" : "0 0 auto", ...sizing, ...style }}
    />
  );
}

/**
 * One partition of a toolbar's children: the run that shares a sampling group.
 *
 * `own` is the group props of a `sharedBackground="hidden"` item, which is the
 * only partition whose configuration belongs to a single child.
 */
interface ToolbarPartition {
  readonly kind: "partition";
  readonly children: readonly ReactNode[];
  readonly own: Omit<GlassGroupProps, "children"> | undefined;
}

type ToolbarSlot = ToolbarPartition | { readonly kind: "spacer"; readonly node: ReactNode };

const itemPropsOf = (child: ReactNode): GlassToolbarItemProps | undefined =>
  isValidElement<GlassToolbarItemProps>(child) ? child.props : undefined;

/** The id partition `index` registers: the base as written, then `-1`, `-2`, … */
const idAt = (base: string, index: number): string => (index === 0 ? base : `${base}-${index}`);

/**
 * The children, cut into partitions at the two boundaries Apple names.
 *
 * A boundary that would produce an empty partition produces none: two spacers in
 * a row, or a spacer at either end, are layout and nothing more, and a group
 * with no members would register a proxy over nothing. A toolbar whose children
 * are *all* spacers keeps one partition all the same, so that asking for a group
 * and getting one does not depend on what is in the row this render.
 *
 * Boundaries are read off the toolbar's own children, which is what
 * `Children.toArray` hands back: an array from a `map` is flattened into it and a
 * `{cond && <GlassToolbarSpacer />}` resolves into it, but a spacer inside a
 * fragment or a wrapper element is that element's child and not the toolbar's,
 * so it spaces without splitting. Nesting a boundary is not a way of hiding one;
 * it is the same rule every toolbar API has about what its items are.
 */
function partitionChildren(children: ReactNode): readonly ToolbarSlot[] {
  const slots: ToolbarSlot[] = [];
  let run: ReactNode[] = [];

  const flush = (): void => {
    if (run.length === 0) return;
    slots.push({ kind: "partition", children: run, own: undefined });
    run = [];
  };

  for (const child of Children.toArray(children)) {
    if (isValidElement(child) && child.type === GlassToolbarSpacer) {
      flush();
      slots.push({ kind: "spacer", node: child });
      continue;
    }
    if (itemPropsOf(child)?.sharedBackground === "hidden") {
      flush();
      slots.push({ kind: "partition", children: [child], own: itemPropsOf(child)?.groupProps });
      continue;
    }
    run.push(child);
  }
  flush();

  if (!slots.some((slot) => slot.kind === "partition")) {
    slots.push({ kind: "partition", children: [], own: undefined });
  }

  return slots;
}

export interface GlassToolbarProps
  extends Omit<HTMLAttributes<HTMLDivElement>, "role" | "onKeyDown"> {
  readonly children?: ReactNode | undefined;
  readonly "aria-label"?: string | undefined;
  readonly orientation?: ToolbarOrientation | undefined;
  readonly plane?: GlassPlane | undefined;
  /**
   * Create a `GlassGroup` for the members. `false` puts them in the group already
   * in scope, which is what two adjacent toolbars sharing one proxy would want —
   * and it switches the partition off with it: a spacer in such a toolbar is a
   * gap, because there is one group and nothing to split.
   */
  readonly group?: boolean | undefined;
  /**
   * The props every partition's group takes. A `sharedBackground="hidden"` item
   * merges its own over these for its own group.
   *
   * `id` is the one that cannot simply be shared, since two groups cannot carry
   * one id: the first partition takes it as written and each later partition
   * takes it suffixed with its index — `toolbar`, `toolbar-1`, `toolbar-2` — so
   * an unsplit toolbar keeps exactly the id it has always registered.
   */
  readonly groupProps?: Omit<GlassGroupProps, "children"> | undefined;
}

/**
 * Where an item sits in the author's sequence: itself, or the placeholder it
 * left behind when it was hoisted out of the toolbar.
 *
 * The anchor is only trusted while it is inside this toolbar. An anchor
 * elsewhere in the document is not a position in *this* sequence, and following
 * it would be worse than the DOM order it replaced.
 */
const logicalNodeOf = (toolbar: HTMLElement, item: HTMLElement): HTMLElement => {
  // Upwards from the item, not off the item itself: an app marks whichever
  // element it likes as the toolbar item, at whatever depth inside the hoisted
  // subtree, and the marker belongs to the subtree's root.
  const hoisted = item.closest(`[${PLANE_ANCHOR_ATTRIBUTE}]`);
  const anchorId = hoisted?.getAttribute(PLANE_ANCHOR_ATTRIBUTE);
  if (anchorId === undefined || anchorId === null || anchorId === "") return item;
  const anchor = toolbar.ownerDocument.getElementById(anchorId);
  return anchor !== null && toolbar.contains(anchor) ? anchor : item;
};

/**
 * This toolbar's items, in the order the author wrote them, wherever they live.
 *
 * Searched from the document rather than from the toolbar element, because a
 * portalled or promoted item is still a member — see `TOOLBAR_ITEM_ATTRIBUTE`.
 *
 * What `querySelectorAll` hands back is *document* order, and for an item that
 * has been hoisted into a plane's host layer that is the author's order only by
 * luck: where the mount lands among the layer's children depends on effect
 * order, on how many commits the tree took to settle, and on promotion history,
 * since opening and closing a morph re-appends its mount at the end. Measured
 * both ways — a toolbar that portals itself puts a nested morph's platter
 * *first*, and that is the tab stop the consumer reported; the demo's
 * playground, whose app portals the whole `<nav>`, happens to put it *last*.
 * So each item is placed by its anchor (`PLANE_ANCHOR_ATTRIBUTE`) where it has one,
 * and items still inside the toolbar come first — which is also the order the
 * accessibility tree reports, since `aria-owns` appends owned elements after an
 * element's DOM children. The arrows, the tab stop and a screen reader then
 * agree, which the ordering before this did not manage.
 */
const membersOf = (toolbar: HTMLElement, toolbarId: string): HTMLElement[] => {
  const selector = `[${TOOLBAR_ITEM_ATTRIBUTE}="${CSS.escape(toolbarId)}"]`;
  const found = [...toolbar.ownerDocument.querySelectorAll<HTMLElement>(selector)];
  const placed = found.map((item) => ({ item, at: logicalNodeOf(toolbar, item) }));

  return placed
    .sort((a, b) => {
      const inside = Number(!toolbar.contains(a.at)) - Number(!toolbar.contains(b.at));
      if (inside !== 0) return inside;
      if (a.at === b.at) return 0;
      const relation = a.at.compareDocumentPosition(b.at);
      return (relation & Node.DOCUMENT_POSITION_FOLLOWING) === 0 ? 1 : -1;
    })
    .map((entry) => entry.item);
};

const isEnabled = (item: HTMLElement): boolean =>
  !item.hasAttribute("disabled") && item.getAttribute("aria-disabled") !== "true";

/** The members the arrows and the tab stop can land on. */
const itemsOf = (toolbar: HTMLElement, toolbarId: string): HTMLElement[] =>
  membersOf(toolbar, toolbarId).filter(isEnabled);

export function GlassToolbar(props: GlassToolbarProps): ReactNode {
  const {
    children,
    orientation = "horizontal",
    plane = "base",
    group = true,
    groupProps,
    ...rest
  } = props;

  const [toolbar, setToolbar] = useState<HTMLDivElement | null>(null);
  const generatedId = useId();
  const toolbarId = `vitrea-toolbar${generatedId}`;

  /** Exactly one item is reachable by Tab; the rest are reached by arrows. */
  const roveTo = useCallback(
    (target: HTMLElement | null) => {
      if (toolbar === null) return;
      const members = membersOf(toolbar, toolbarId);
      const items = members.filter(isEnabled);
      const active = target !== null && items.includes(target) ? target : (items[0] ?? null);
      // Cleared across *every* member, not only the reachable ones. An item that
      // has just disabled itself is out of `items` while its `tabIndex` is still
      // the one this toolbar handed it — two tab stops, one of them on a control
      // that no longer takes activation.
      for (const item of members) item.tabIndex = -1;
      if (active !== null) active.tabIndex = 0;

      /*
       * `aria-owns` for the items that are not descendants.
       *
       * Membership is not containment here, and the accessibility tree has to
       * agree with the arrows: an item a screen reader hears outside the toolbar
       * while Tab and the arrows treat it as inside is worse than either
       * behaviour alone. `aria-owns` is the platform's own answer to that, and
       * an id is assigned where the item has none because that is what it takes.
       */
      const external = items.filter((item) => !toolbar.contains(item));
      for (const item of external) {
        if (item.id === "") item.id = `${toolbarId}-item-${external.indexOf(item)}`;
      }
      const owns = external.map((item) => item.id).join(" ");
      if (owns === "") toolbar.removeAttribute("aria-owns");
      else toolbar.setAttribute("aria-owns", owns);
    },
    [toolbar, toolbarId],
  );

  useEffect(() => {
    if (toolbar === null) return;
    roveTo(null);
    /*
     * Items come and go — a menu opening, a control disabling itself, a platter
     * promoted to another plane — and the tab stop has to survive all of it.
     * Watching the whole document is what membership-without-containment costs;
     * it is filtered to the mutations that can change the item set, and it costs
     * nothing until one happens.
     */
    const observer = new MutationObserver(() => {
      const items = itemsOf(toolbar, toolbarId);
      const current = items.find((item) => item.tabIndex === 0);
      roveTo(current ?? null);
    });
    observer.observe(toolbar.ownerDocument.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ["disabled", "aria-disabled", TOOLBAR_ITEM_ATTRIBUTE],
    });
    return () => observer.disconnect();
  }, [roveTo, toolbar, toolbarId]);

  const onFocus = useCallback(
    (event: ReactFocusEvent<HTMLDivElement>) => {
      const target = event.target;
      if (target instanceof HTMLElement && target.getAttribute(TOOLBAR_ITEM_ATTRIBUTE) === toolbarId) {
        roveTo(target);
      }
    },
    [roveTo, toolbarId],
  );

  const onKeyDown = useCallback(
    (event: ReactKeyboardEvent<HTMLDivElement>) => {
      if (toolbar === null) return;
      const items = itemsOf(toolbar, toolbarId);
      if (items.length === 0) return;

      const next = orientation === "horizontal" ? "ArrowRight" : "ArrowDown";
      const previous = orientation === "horizontal" ? "ArrowLeft" : "ArrowUp";

      const active = document.activeElement;
      const index = active instanceof HTMLElement ? items.indexOf(active) : -1;

      let target: HTMLElement | undefined;
      if (event.key === next) target = items[(index + 1 + items.length) % items.length];
      else if (event.key === previous) target = items[(index - 1 + items.length) % items.length];
      else if (event.key === "Home") target = items[0];
      else if (event.key === "End") target = items[items.length - 1];
      else return;

      if (target === undefined) return;
      event.preventDefault();
      roveTo(target);
      target.focus();
    },
    [orientation, roveTo, toolbar, toolbarId],
  );

  /*
   * The minimum a spacer opens, derived rather than chosen.
   *
   * `samplingPaddingFor` is the runtime's own composition — the shipped optics
   * for this group's variant, folded by the resolved policy, through the scatter
   * law, times 3σ — so this number moves with Reduce Transparency the moment the
   * policy does, and it is the same number `root.ts` will resolve for these
   * groups. The toolbar's own box stands in for the members it has not measured:
   * the law is monotone in a member's span and extents, and no member of a
   * toolbar is larger than the toolbar, so a box that contains them yields an
   * upper bound on their padding rather than a guess at it.
   *
   * Before the first measurement — the first render, and a jsdom tree that lays
   * nothing out — the box is empty, which is the projection at span 0: the floor
   * every group starts at, and the honest answer for a toolbar with no extent.
   */
  const accessibility = useGlassAccessibility();
  const [box, setBox] = useState<readonly [number, number]>([0, 0]);

  useEffect(() => {
    if (toolbar === null) return;
    const observer = new ResizeObserver(() => {
      const rect = toolbar.getBoundingClientRect();
      setBox((current) =>
        current[0] === rect.width && current[1] === rect.height
          ? current
          : [rect.width, rect.height],
      );
    });
    observer.observe(toolbar);
    return () => observer.disconnect();
  }, [toolbar]);

  /*
   * ...and it clears BOTH of the paddings a split is checked against, because
   * there are two and they are allowed to differ.
   *
   * `platform-web` resolves what the group actually samples with — the derived
   * 3σ above, or the author's own number — and `proxy-overlap-after-enforcement`
   * fires on that. core's scene model runs its own overlap check
   * (`group-proxy-overlap`) against the *descriptor's* padding, which is the
   * author's number or core's public advisory of 24, and that advisory
   * deliberately did not follow σ down when the material was refitted: lowering
   * a published default for tidiness would change behaviour for every consumer
   * that never reaches the derivation. So at today's material the advisory is
   * the larger of the two for a control-sized row, and the material's own
   * requirement overtakes it on a taller bar or under Reduce Transparency. A
   * layout with clearance to spare has to satisfy whichever is in front.
   *
   * And it is taken over **every group this toolbar registers**, not over the
   * toolbar's own props alone. A hidden item's `groupProps` may name a different
   * material, and the variants are not close: `clear` samples at σ 4 against the
   * regular material's 1.25, so a clear partition wants about 40 CSS px where a
   * regular one wants 12. A gap derived from the row's material would be a third
   * of what the item beside it needs.
   */
  const slots = group ? partitionChildren(children) : undefined;

  const gap = ((): number => {
    const material = (accessibility ?? NOMINAL_ACCESSIBILITY_POLICY).material;
    const members = box[0] > 0 && box[1] > 0 ? [box] : [];
    // The groups that will exist, and only those. Folding the toolbar's own
    // props in as a floor would size the gap for a material nothing draws —
    // a clear row every one of whose partitions stepped out and declared
    // `regular` would still be spaced for clear. There is always at least one
    // partition to read (see `partitionChildren`), and `group={false}` leaves
    // none at all, which is a toolbar that registers nothing and so has nothing
    // to hold apart.
    const registered = (slots ?? []).flatMap((slot) =>
      slot.kind === "partition" ? [{ ...groupProps, ...slot.own }] : [],
    );
    return registered.reduce(
      (widest, props) =>
        Math.max(
          widest,
          props?.samplingPadding ?? DEFAULT_GROUP_SAMPLING.samplingPadding,
          samplingPaddingFor({
            members,
            material,
            ...(props?.variant === undefined ? {} : { variant: props.variant }),
          }),
        ),
      0,
    );
  })();

  const scope: ToolbarScope = useMemo(
    () => ({ id: toolbarId, orientation, gap }),
    [gap, orientation, toolbarId],
  );

  /*
   * The partitions, each wrapped in its own group — and the groups are INSIDE
   * the toolbar element, which is the whole shape of X5: one `role="toolbar"`,
   * N sampling groups. `GlassGroup` renders no DOM, so the flex row the author
   * wrote is the flex row the browser lays out, split or not.
   */
  let partitionIndex = -1;
  const body =
    slots === undefined
      ? children
      : slots.map((slot) => {
          if (slot.kind === "spacer") return slot.node;
          partitionIndex += 1;
          const merged = { ...groupProps, ...slot.own };
          // An id the *item* wrote is its own and is taken as written; only the
          // one inherited from the toolbar has to be made unique per partition.
          const id =
            slot.own?.id ??
            (groupProps?.id === undefined ? undefined : idAt(groupProps.id, partitionIndex));
          // Keyed by the partition rather than by the slot, so a spacer appearing
          // or moving does not renumber the groups below it and re-register them.
          return (
            <GlassGroup
              key={`partition-${partitionIndex}`}
              {...merged}
              {...(id === undefined ? {} : { id })}
            >
              {slot.children}
            </GlassGroup>
          );
        });

  return (
    <PlanePortal plane={plane}>
      <div
        {...rest}
        ref={setToolbar}
        role="toolbar"
        aria-orientation={orientation}
        onFocus={onFocus}
        onKeyDown={onKeyDown}
      >
        <ToolbarContext.Provider value={scope}>{body}</ToolbarContext.Provider>
      </div>
    </PlanePortal>
  );
}

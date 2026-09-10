/**
 * `GlassButton` and `GlassIconButton` — real `<button>`s with glass on them.
 *
 * Both are `GlassSurface asChild` over a `<button>`, which is the whole point of
 * the `asChild` seam: parent acceptance #1 asks for a control VoiceOver announces
 * as a button, whose label is selectable, focusable, IME-capable DOM. A wrapper
 * element would put a `<div>` between the semantics and the box; a role attribute
 * on a `<div>` would lose form participation, the disabled semantics, and the
 * platform's own activation keys. Rendering the element the platform already
 * defines costs nothing and gets all of it.
 *
 * `disabled` is passed straight through to the element — the attribute, not an
 * `aria-disabled` imitation — and separately to the material, where it collapses
 * to the kernel's `disabled` interaction state.
 *
 * `GlassIconButton` differs in exactly two ways: it is a capsule by default, and
 * it *requires* a label, because an icon-only control with no accessible name is
 * the single most common way a toolbar becomes unusable with a screen reader. The
 * requirement is in the type, so it is a compile error rather than an audit
 * finding.
 */

import type { ComponentPropsWithRef, ReactNode } from "react";

import { GlassSurface, type GlassSurfaceOwnProps } from "../surface";
import { useToolbarItem, withoutToolbarItemProps, type GlassToolbarItemProps } from "./toolbar";

/**
 * `ComponentPropsWithRef` rather than `ButtonHTMLAttributes`, so `ref` is part of
 * the contract: an accessibility primitive composed over this button — a menu
 * trigger, a tooltip anchor — needs the element, and React 19 passes `ref` as an
 * ordinary prop that has to be declared to be accepted.
 */
type ButtonAttributes = Omit<ComponentPropsWithRef<"button">, "color">;

/**
 * The surface props a button forwards.
 *
 * An explicit list rather than the whole of `GlassSurfaceOwnProps`, because a
 * button owns some of them itself: `asChild` and `interactive` are what makes it
 * a button, and `disabled` reaches the element as well as the material. What is
 * left is material and placement, and all of it belongs to the author —
 * including `tint` and `foreground`, which were missing until W27a. A tinted
 * emphasised control is the *canonical* use of Apple's `Glass.tint(_:)` ("apply
 * color to the background… one emphasised control"), and it was the one surface
 * in the library that could not be tinted.
 *
 * Each is forwarded only when it is not `undefined`, and for `tint` that
 * distinction is load-bearing: `null` is a value — the author clearing a tint
 * inherited from the group, the way `Glass.tint(nil)` does — while `undefined`
 * is the inheritance the surface must not be told about.
 */
type ForwardedSurfaceProps = Pick<
  GlassSurfaceOwnProps,
  | "plane"
  | "order"
  | "variant"
  | "tint"
  | "profile"
  | "radius"
  | "capsule"
  | "thickness"
  | "foreground"
  | "groupId"
  | "nodeId"
  | "morphing"
  | "onHost"
>;

export interface GlassButtonProps
  extends ButtonAttributes,
    ForwardedSurfaceProps,
    GlassToolbarItemProps {
  readonly children?: ReactNode | undefined;
}

/** Advisory defaults: a control-sized corner and a control-sized material depth. */
const BUTTON_RADIUS = 14;
const BUTTON_THICKNESS = 8;

export function GlassButton(props: GlassButtonProps): ReactNode {
  const {
    plane,
    order,
    variant,
    tint,
    profile,
    radius = BUTTON_RADIUS,
    capsule,
    thickness = BUTTON_THICKNESS,
    foreground,
    groupId,
    nodeId,
    morphing,
    onHost,
    children,
    disabled = false,
    type = "button",
    ...rest
  } = props;

  /*
   * `sharedBackground` and `groupProps` are read by the surrounding
   * `GlassToolbar` off this element and are never the button's own: they say
   * which sampling group the button belongs to, which is the toolbar's to
   * decide. Dropped here so a button carrying them outside a toolbar hands the
   * DOM nothing it cannot use.
   */
  const buttonProps = withoutToolbarItemProps(rest);

  const toolbar = useToolbarItem();

  return (
    <GlassSurface
      asChild
      interactive
      disabled={disabled}
      radius={radius}
      thickness={thickness}
      {...(plane === undefined ? {} : { plane })}
      {...(order === undefined ? {} : { order })}
      {...(variant === undefined ? {} : { variant })}
      {...(tint === undefined ? {} : { tint })}
      {...(profile === undefined ? {} : { profile })}
      {...(capsule === undefined ? {} : { capsule })}
      {...(foreground === undefined ? {} : { foreground })}
      {...(groupId === undefined ? {} : { groupId })}
      {...(nodeId === undefined ? {} : { nodeId })}
      {...(morphing === undefined ? {} : { morphing })}
      {...(onHost === undefined ? {} : { onHost })}
    >
      <button {...buttonProps} {...toolbar} type={type} disabled={disabled}>
        {children}
      </button>
    </GlassSurface>
  );
}

export interface GlassIconButtonProps extends Omit<GlassButtonProps, "aria-label"> {
  /**
   * Required. An icon-only control with no accessible name is announced as
   * "button" and nothing else, which is the fastest way to make a toolbar
   * unusable with a screen reader.
   */
  readonly "aria-label": string;
}

export function GlassIconButton(props: GlassIconButtonProps): ReactNode {
  const { capsule = true, ...rest } = props;
  return <GlassButton {...rest} capsule={capsule} />;
}

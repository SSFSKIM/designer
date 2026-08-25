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

import type { ButtonHTMLAttributes, ReactNode } from "react";

import { GlassSurface, type GlassSurfaceOwnProps } from "../surface";
import { useToolbarItem } from "./toolbar";

type ButtonAttributes = Omit<ButtonHTMLAttributes<HTMLButtonElement>, "color">;

export interface GlassButtonProps
  extends ButtonAttributes,
    Pick<
      GlassSurfaceOwnProps,
      "plane" | "order" | "variant" | "profile" | "radius" | "capsule" | "thickness" | "groupId" | "nodeId" | "morphing" | "onHost"
    > {
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
    profile,
    radius = BUTTON_RADIUS,
    capsule,
    thickness = BUTTON_THICKNESS,
    groupId,
    nodeId,
    morphing,
    onHost,
    children,
    disabled = false,
    type = "button",
    ...buttonProps
  } = props;

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
      {...(profile === undefined ? {} : { profile })}
      {...(capsule === undefined ? {} : { capsule })}
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

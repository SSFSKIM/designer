/**
 * `asChild` — the React half of platform-web's host-registration seam.
 *
 * platform-web's contract is that the app authors the element and vitrea only
 * *registers* it: never creates it, never wraps it, never replaces its content
 * (`host.ts`). `asChild` is what makes that expressible in JSX — `<GlassSurface
 * asChild><button/></GlassSurface>` renders exactly one `<button>`, and the glass
 * is registered against it.
 *
 * That is not a convenience. A wrapper element would put a `<div>` between a
 * control's semantics and its box, and parent acceptance #1 is precisely that the
 * label text stays real DOM: selectable, focusable, IME-capable, announced as a
 * button. The only way to keep a `<button>` a button is to hand vitrea the
 * author's own `<button>`.
 *
 * Merge rules, which follow Radix's Slot because app code already expects them:
 * event handlers chain (the surface's first, then the child's), `style` and
 * `className` compose, refs compose, and every other prop the child declares
 * wins over the surface's.
 */

import {
  cloneElement,
  isValidElement,
  type CSSProperties,
  type ReactElement,
  type ReactNode,
  type Ref,
  type RefCallback,
} from "react";

/** Props a slot merges into its child. Loose by necessity: the child is arbitrary. */
export type SlotProps = Record<string, unknown> & {
  readonly ref?: Ref<HTMLElement> | undefined;
  readonly style?: CSSProperties | undefined;
  readonly className?: string | undefined;
};

/**
 * Chain two refs into one.
 *
 * React 19 passes `ref` as an ordinary prop, so a child's own ref arrives in
 * `props` and both have to be honoured — dropping the child's would silently
 * break whatever the app was measuring or focusing.
 */
export function composeRefs<T>(...refs: readonly (Ref<T> | undefined)[]): RefCallback<T> {
  return (value: T | null) => {
    const cleanups: (() => void)[] = [];
    for (const ref of refs) {
      if (typeof ref === "function") {
        const cleanup = ref(value);
        if (typeof cleanup === "function") cleanups.push(cleanup);
      } else if (ref !== null && ref !== undefined) {
        ref.current = value;
      }
    }
    // React 19 ref callbacks may return a cleanup; returning one keeps that
    // contract intact for every ref in the chain rather than only the last.
    return cleanups.length === 0 ? undefined : () => {
      for (const cleanup of cleanups) cleanup();
    };
  };
}

const isEventHandlerName = (name: string): boolean =>
  name.startsWith("on") && name.length > 2 && name[2] === name[2]?.toUpperCase();

export function mergeSlotProps(
  slotProps: SlotProps,
  childProps: Record<string, unknown>,
): Record<string, unknown> {
  const merged: Record<string, unknown> = { ...slotProps, ...childProps };

  for (const [name, slotValue] of Object.entries(slotProps)) {
    const childValue = childProps[name];

    if (isEventHandlerName(name)) {
      if (typeof slotValue === "function" && typeof childValue === "function") {
        merged[name] = (...args: unknown[]) => {
          (slotValue as (...a: unknown[]) => void)(...args);
          (childValue as (...a: unknown[]) => void)(...args);
        };
      } else {
        merged[name] = childValue ?? slotValue;
      }
      continue;
    }

    if (name === "style") {
      merged.style = { ...(slotValue as CSSProperties), ...(childValue as CSSProperties) };
      continue;
    }

    if (name === "className") {
      merged.className = [slotValue, childValue].filter(Boolean).join(" ") || undefined;
      continue;
    }

    if (name === "ref") {
      merged.ref = composeRefs(slotValue as Ref<HTMLElement>, childValue as Ref<HTMLElement>);
    }
  }

  return merged;
}

/**
 * Render `children` as the slot: exactly one element, with `slotProps` merged in.
 *
 * The refusal is deliberate and dev-facing. A fragment or a text node has no
 * element to register a host against, and discovering that as "the glass never
 * appeared" costs far more than the throw does.
 */
export function renderAsChild(children: ReactNode, slotProps: SlotProps): ReactElement {
  if (!isValidElement(children)) {
    throw new Error(
      "@vitrea/react: `asChild` needs exactly one React element as its child — vitrea registers " +
        "the element you authored rather than creating one (platform-web's host contract), so " +
        "there has to be one to register.",
    );
  }
  const childProps = children.props as Record<string, unknown>;
  return cloneElement(children, mergeSlotProps(slotProps, childProps));
}

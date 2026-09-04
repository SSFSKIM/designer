/**
 * The sheet: the one content panel (DESIGN.md §5). Ordinary DOM with a
 * translucent white fill, never glass. Non-modal: the field and its controls
 * stay live beside it. Escape closes it and focus lands on its heading when it
 * opens, so a keyboard reader arrives where the content starts.
 */

import { useEffect, useId, useRef, type ReactNode } from "react";

export type SheetId = "stations" | "method" | "rendering" | "access";

export interface SheetProps {
  readonly id: SheetId;
  readonly title: string;
  readonly onClose: () => void;
  readonly children: ReactNode;
}

export function Sheet(props: SheetProps): ReactNode {
  const headingId = useId();
  const headingRef = useRef<HTMLHeadingElement>(null);
  const { onClose } = props;

  useEffect(() => {
    headingRef.current?.focus({ preventScroll: true });
  }, [props.id]);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent): void => {
      if (event.key === "Escape" && !event.defaultPrevented) onClose();
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [onClose]);

  return (
    <section className="sheet" aria-labelledby={headingId} data-sheet={props.id}>
      <header className="sheet__header">
        <h2 id={headingId} ref={headingRef} tabIndex={-1} className="sheet__title">
          {props.title}
        </h2>
        <button type="button" className="sheet__close" onClick={onClose}>
          Close
        </button>
      </header>
      <div className="sheet__body">{props.children}</div>
    </section>
  );
}

export interface ReadoutRow {
  readonly label: string;
  readonly value: ReactNode;
}

/** The one key/value pattern for any data. */
export function Readout(props: { readonly rows: readonly ReadoutRow[] }): ReactNode {
  return (
    <dl className="readout">
      {props.rows.map((row) => (
        <div className="readout__row" key={row.label}>
          <dt>{row.label}</dt>
          <dd>{row.value}</dd>
        </div>
      ))}
    </dl>
  );
}

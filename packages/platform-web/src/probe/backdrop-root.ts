/**
 * Probe layer 2 — the structural backdrop-root audit. The load-bearing layer.
 *
 * The dominant real-world failure of the proxy topology is not an engine defect:
 * it is application CSS putting a backdrop-root-forming style on an ancestor of
 * the plane root, which silently re-roots the proxy's backdrop so the filter
 * sees nothing. That is statically detectable from computed styles, and it is
 * the only thing about `backdrop-filter` that is — no pixel oracle exists in any
 * engine (S1 Q5, four measured negative results).
 *
 * ## The list is pinned to the spec, and that is the whole finding
 *
 * S1's prototype used the *intuitive* property list — the one a developer writes
 * from memory — and scored 11 of 13 against measured ground truth: **no false
 * negatives, two false positives**, `contain: paint` and `isolation: isolate`,
 * both of which look like isolation boundaries and neither of which re-roots the
 * backdrop. The fix is to carry [Filter Effects 2's normative trigger
 * list](https://drafts.csswg.org/filter-effects-2/#BackdropRoot) and nothing
 * more. The measurements are what license dropping those two: the spec is
 * silent on `contain` and no WPT test covers it, so without the pixels it would
 * have been a guess.
 *
 * Excluded deliberately, each measured harmless in Chromium and retail Chrome:
 * `contain`, `isolation`, `transform` (including a 3D-promoting `translate3d` —
 * byte-identical, and Filter Effects 2 says so explicitly), `will-change:
 * transform`, `z-index`. Also excluded: `content-visibility`, which the
 * prototype flagged and the normative list does not name.
 *
 * ## Reach
 *
 * Catches app-induced re-rooting. Sees nothing about engine behaviour. It
 * *over*-triggers on engines that do not implement `mask`/`clip-path` as
 * triggers — WPT's `backdrop-filter-backdrop-root-mask.html` fails in Firefox
 * 154 and Safari 26.6 — which is the fail-safe direction, and which the layer-3
 * table records so it can eventually be relaxed per engine.
 */

/** Reads one CSS property off a computed style. All that is needed, and testable. */
export type StyleLookup = (property: string) => string;

export interface BackdropRootTriggerSpec {
  readonly property: string;
  /** True when this value re-roots the backdrop. */
  readonly triggers: (value: string) => boolean;
}

const notNone = (value: string): boolean => value !== "" && value !== "none";

/**
 * `will-change` re-roots when it names a property that re-roots. `transform` and
 * `contain` are not on that list — S1 measured `will-change: transform` harmless
 * and `will-change: opacity` breaking, in the same run.
 */
const WILL_CHANGE_TRIGGERS = [
  "filter",
  "backdrop-filter",
  "opacity",
  "mask",
  "mask-image",
  "mask-border",
  "clip-path",
  "mix-blend-mode",
];

export const BACKDROP_ROOT_TRIGGERS: readonly BackdropRootTriggerSpec[] = [
  // A visually inert filter re-roots exactly as thoroughly as a real one, and
  // real application CSS emits these as animation start states all the time.
  { property: "filter", triggers: notNone },
  { property: "backdrop-filter", triggers: notNone },
  { property: "-webkit-backdrop-filter", triggers: notNone },
  { property: "opacity", triggers: (value) => value !== "" && Number.parseFloat(value) < 1 },
  { property: "mask-image", triggers: notNone },
  { property: "-webkit-mask-image", triggers: notNone },
  { property: "mask-border-source", triggers: notNone },
  { property: "clip-path", triggers: notNone },
  { property: "mix-blend-mode", triggers: (value) => value !== "" && value !== "normal" },
  {
    property: "will-change",
    triggers: (value) =>
      value
        .split(",")
        .map((named) => named.trim())
        .some((named) => WILL_CHANGE_TRIGGERS.includes(named)),
  },
];

export interface BackdropRootTrigger {
  readonly property: string;
  readonly value: string;
}

/** Every normative trigger this style carries. Empty means "does not re-root". */
export function backdropRootTriggers(style: StyleLookup): readonly BackdropRootTrigger[] {
  const found: BackdropRootTrigger[] = [];
  for (const spec of BACKDROP_ROOT_TRIGGERS) {
    const value = style(spec.property);
    if (spec.triggers(value)) found.push({ property: spec.property, value });
  }
  return found;
}

export interface BackdropRootBreak {
  readonly element: Element;
  /** A stable-ish label for a dev-mode message: id, then classes, then tag. */
  readonly describe: string;
  readonly triggers: readonly BackdropRootTrigger[];
}

/**
 * Describe an element well enough that a developer can find it in their own
 * source. The fix is one CSS line in the host app, so this string is most of
 * the probe's value.
 */
export function describeElement(element: Element): string {
  const id = element.id === "" ? "" : `#${element.id}`;
  const classes =
    element.classList.length === 0 ? "" : `.${[...element.classList].join(".")}`;
  return `${element.tagName.toLowerCase()}${id}${classes}`;
}

export interface AuditOptions {
  /** Where to start. The proxy element itself, whose own filter is not a break. */
  readonly from: Element;
  /**
   * Where to stop, exclusive. The document element is *always* a Backdrop Root
   * and that is the correct one — the proxy is supposed to sample everything
   * below it.
   */
  readonly stopAt: Element | null;
  readonly readStyle: (element: Element) => StyleLookup;
}

/**
 * Walk the proxy's ancestor chain and report every element that re-roots its
 * backdrop.
 *
 * **Deviation from S1's proposal, deliberate.** The spike proposed walking "from
 * every member host and from the group's proxy up to their lowest common
 * ancestor". Only the proxy's own chain can re-root the *proxy's* backdrop: a
 * trigger below the common ancestor on a host's side changes how that host
 * paints, not what the proxy samples. So this walks the proxy's chain to the
 * document element, which is a superset of the shared segment and strictly
 * simpler. The per-group requirement is preserved, and it is the requirement
 * that mattered: different groups sit under different ancestors, so the audit is
 * per group and not per document.
 */
export function auditBackdropRootChain(options: AuditOptions): readonly BackdropRootBreak[] {
  const { from, stopAt, readStyle } = options;
  const breaks: BackdropRootBreak[] = [];

  // The proxy carries backdrop-filter itself; it is a Backdrop Root only for its
  // own descendants, and it has none. Start at its parent.
  let element = from.parentElement;

  while (element !== null && element !== stopAt && element !== document.documentElement) {
    const triggers = backdropRootTriggers(readStyle(element));
    if (triggers.length > 0) {
      breaks.push({ element, describe: describeElement(element), triggers });
    }
    element = element.parentElement;
  }

  return breaks;
}

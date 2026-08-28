/**
 * The layer model, as a check rather than as prose.
 *
 * Liquid Glass is a **controls-layer** material. Apple states the rule twice and
 * from two directions: "Don't use Liquid Glass in the content layer… including
 * it in the content layer can result in unnecessary complexity and a confusing
 * visual hierarchy" (HIG Materials), and "Stacking Liquid Glass elements on top
 * of each other can quickly make the interface feel cluttered and confusing…
 * avoid applying the material to both layers. Instead, use fills, transparency,
 * and vibrancy for the top elements" (WWDC25 219). S356 says the same thing as
 * an instruction: "make sure to apply the material directly to the control, not
 * its inner views."
 *
 * vitrea stated this in prose and enforced nothing: `GlassSurface asChild` will
 * glass any element an app hands it, including a table row, and will happily
 * register one host inside another host's content. This module is the contract.
 *
 * ## What is checked, and what is deliberately not
 *
 * Two compositions, both decidable from structure alone at registration time:
 *
 *  1. **`glass-inside-glass`** — a registered host that is a DOM descendant of
 *     another registered host. This is "applying the material to both layers"
 *     exactly, and it is the one composition that is wrong in every arrangement
 *     of planes, sizes and orders. Note this is *not* the same finding as core's
 *     `same-plane-overlap`: that one is geometric, per-frame, and speaks about
 *     X1's paint sandwich; this one is structural, fires once at registration,
 *     names the design rule, and still fires when nesting is cross-plane (where
 *     the overlap check is silent by design, because cross-plane stacking is
 *     vitrea's calibrated morph case).
 *  2. **`glass-in-content-layer`** — a host whose resolved ARIA role is a
 *     list-or-table structure role. Apple names this case by name — "Consider
 *     this tableview: making it Liquid Glass would make it compete with other
 *     elements and muddy the hierarchy. So keep it in the content layer instead"
 *     — and the coverage matrix calls it the single most likely thing for a web
 *     glass library to get wrong. An **explicit** `role` wins over the tag's
 *     implicit one, so a `<ul role="menu">` or a `<div role="toolbar">` is a
 *     controls-layer container and says nothing; that escape is named in the
 *     message.
 *
 * Deliberately left out, with reasons, because each would cost more honesty
 * than it buys:
 *
 *  - **"Nothing scrolling underneath, so nothing to refract"** (WWDC26's
 *    mechanical restatement of the rule). vitrea does track a backdrop dirty
 *    epoch, so this is knowable — but only by watching it over time, which is a
 *    per-frame observation, and a page that is merely *at rest* is
 *    indistinguishable from one that never scrolls. It would fire on every
 *    static landing page.
 *  - **"Controls sit on a material, never directly on content"** and the four
 *    standard materials. There is nothing to check against: vitrea ships one
 *    material and no content-layer alternative. That is a missing feature, not
 *    an unenforced rule.
 *  - **"Non-interactive items should not be on glass"** (WWDC25 310). Would fire
 *    on every legitimate glass container — a bar, a platter, a plate — which
 *    Apple itself glasses. Separating a decorative label from a controls-layer
 *    container needs a distinction vitrea does not model.
 *  - **Glass-over-content intersection at rest.** Geometric, per-frame, and it
 *    needs a notion of "content" that vitrea has no way to identify.
 *
 * ## Cost
 *
 * Everything here runs from `registerHost`, under `devMode`, and never from a
 * frame. The nesting check is one pass over the registered hosts using native
 * `Node.contains`; the role check is one attribute read and a map lookup. v1's
 * benchmark scene is eight surfaces. In production the caller does not call in
 * at all.
 */

import type { PlatformDiagnostic } from "./diagnostics";

/** Enough of a registered host for the structural checks. */
export interface LayerModelHost {
  readonly nodeId: string;
  readonly host: HTMLElement;
}

/**
 * Tag → implicit ARIA role, for the list and table structures Apple names.
 *
 * `<menu>` is absent on purpose. Its implicit role is `list`, but it is HTML's
 * own element for a toolbar of commands, so flagging it would contradict the
 * rule this check exists to state.
 */
const IMPLICIT_CONTENT_ROLES: Readonly<Record<string, string>> = {
  ul: "list",
  ol: "list",
  li: "listitem",
  table: "table",
  thead: "rowgroup",
  tbody: "rowgroup",
  tfoot: "rowgroup",
  tr: "row",
  td: "cell",
  th: "columnheader",
};

/** Explicit roles that put an element in the content layer. */
const CONTENT_ROLES: ReadonlySet<string> = new Set([
  "list",
  "listitem",
  "table",
  "rowgroup",
  "row",
  "cell",
  "gridcell",
  "columnheader",
  "rowheader",
  "grid",
  "treegrid",
]);

/**
 * The content-layer role this element carries, or `undefined`.
 *
 * An explicit `role` is authoritative even when it is not a content role: that
 * is how an author says "this `<ul>` is a menu" and how the check stands down.
 * ARIA allows a fallback list, so the first token wins, as the platform does it.
 */
export function contentLayerRole(element: Element): string | undefined {
  const declared = element.getAttribute("role")?.trim().split(/\s+/)[0];
  if (declared !== undefined && declared !== "") {
    return CONTENT_ROLES.has(declared) ? declared : undefined;
  }
  const implicit = IMPLICIT_CONTENT_ROLES[element.tagName.toLowerCase()];
  return implicit === undefined ? undefined : implicit;
}

/**
 * The registered host `candidate` nests inside, or the one that nests inside it.
 *
 * Both directions, because registration order is the app's business: a surface
 * can mount inside an already-registered one, and a container can mount around
 * already-registered children. `Node.contains` is true for self, and the
 * candidate is not yet in `registered` when this runs, so no host matches itself.
 */
export function findNesting(
  candidate: LayerModelHost,
  registered: Iterable<LayerModelHost>,
): { readonly inner: LayerModelHost; readonly outer: LayerModelHost } | undefined {
  for (const other of registered) {
    if (other.host === candidate.host) continue;
    if (other.host.contains(candidate.host)) return { inner: candidate, outer: other };
    if (candidate.host.contains(other.host)) return { inner: other, outer: candidate };
  }
  return undefined;
}

/**
 * Run both checks for one newly registered host and report what they find.
 *
 * The caller gates on `devMode`; this function does not, so a test can drive it
 * directly. `registered` must not yet contain `candidate`.
 */
export function checkLayerModel(
  candidate: LayerModelHost,
  registered: Iterable<LayerModelHost>,
  report: (diagnostic: PlatformDiagnostic) => void,
): void {
  const nesting = findNesting(candidate, registered);
  if (nesting !== undefined) {
    const { inner, outer } = nesting;
    report({
      code: "glass-inside-glass",
      severity: "error",
      // Inner first, so the pair is one finding whichever order they registered in.
      subjects: [inner.nodeId, outer.nodeId],
      message: `Glass surface "${inner.nodeId}" is registered inside glass surface "${outer.nodeId}"'s content. Liquid Glass is a controls-layer material and Apple names this composition a failure — "avoid applying the material to both layers" — because the two blurs read as one muddy plane instead of two. Apply the material to the control, not to its container as well: keep the glass on whichever of the two is the control, and give the other a fill, a translucency or a vibrant foreground instead.`,
    });
  }

  const role = contentLayerRole(candidate.host);
  if (role !== undefined) {
    report({
      code: "glass-in-content-layer",
      severity: "warning",
      subjects: [candidate.nodeId],
      message: `Glass surface "${candidate.nodeId}" is a <${candidate.host.tagName.toLowerCase()}> — an element in the content layer (role "${role}"). Apple's rule is "don't use Liquid Glass in the content layer": a glassed row or cell competes with the controls above it and muddies the hierarchy. Move the glass onto the control this element contains and leave the row itself plain — or, if this really is a controls-layer container, give it the role it means (role="menu", role="toolbar", role="group") and this check stands down.`,
    });
  }
}

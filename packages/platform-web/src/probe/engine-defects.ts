/**
 * Probe layer 3's second half: engine defects vitrea's own construction can walk
 * into.
 *
 * The conformance table records what an engine *can* do. This records what a
 * named engine version does **wrong**, in a shape vitrea builds by default —
 * which is a different fact and needs a different treatment. A conformance field
 * is answered once per session and feeds tier resolution; a defect is answered
 * per group, because whether it bites depends on where the application mounted
 * the plane root, and it is reported rather than acted on: the runtime cannot
 * repair another engine's bug and must not pretend the shape is unsupported.
 *
 * It follows the table's discipline exactly. Every defect cites its evidence, so
 * one cannot be added on a hunch; every defect names at least one workaround, so
 * the diagnostic tells an author what to do rather than only what is wrong; and
 * a version range that no defect covers reports nothing, which is the fail-quiet
 * direction that the *conformance* fields deliberately do not take. A defect is
 * a claim that something is broken, and an unevidenced one is noise in a channel
 * whose whole value is that it only speaks when it has something.
 *
 * ## The one defect on the books
 *
 * Chromium 152 renders `backdrop-filter` as a complete no-op on an element with
 * `clip-path: path()` under an ancestor carrying both `overflow` other than
 * `visible` and a `border-radius`. All three ingredients are required and every
 * basic-shape `clip-path` is unaffected — a 12-cell × 2-build matrix in
 * `spikes/s1-proxy-topology/chrome152-regression/REPORT.md`.
 *
 * vitrea's backdrop proxies are exactly `clip-path: path()` + `backdrop-filter`
 * elements (`backdrop-proxy.ts`), so the shape is the product's, not a user's
 * mistake. Under the **default** mount they are immune: the plane root is
 * `position: fixed` under `body`, with no rounded-overflow ancestor above it. A
 * custom `container` mount can put it under one, and then every proxy on the
 * page silently loses its frost with no console message and no devtools warning
 * in the engine itself. That is the entire reason this advisory exists — the
 * failure is invisible from every direction except this one.
 */

import type { StyleLookup } from "./backdrop-root";

/**
 * What must be true of a proxy's ancestor chain before a defect bites.
 *
 * A closed set, deliberately: a defect whose precondition this cannot express
 * does not get a hand-rolled predicate smuggled in beside the data — it gets a
 * member here, with the reader that answers it below.
 */
export type DefectPrecondition = "rounded-overflow-ancestor";

export interface EngineDefect {
  readonly id: string;
  /** Names the regression in one line. Becomes the diagnostic's opening. */
  readonly summary: string;
  readonly precondition: DefectPrecondition;
  /** Ordered, cheapest first. Each is something an author can actually do. */
  readonly workarounds: readonly string[];
  /** Where the verified repro and the bug report live, as a repo path or a URL. */
  readonly report: string;
  /** Why this row says what it says. Non-empty by test, as the table's rows are. */
  readonly evidence: readonly string[];
}

export const CHROMIUM_152_PATH_CLIP_NO_OP: EngineDefect = {
  id: "chromium-152-clip-path-path-backdrop-filter",
  summary:
    "Chromium 152 drops backdrop-filter entirely on an element with clip-path: path() when an ancestor has overflow other than visible together with a border-radius. vitrea's backdrop proxies are exactly that shape, so every proxy under such an ancestor renders unfrosted — silently, with no console message in the engine.",
  precondition: "rounded-overflow-ancestor",
  workarounds: [
    "Mount the GlassRoot at its default — no `container` — so the plane root is a position: fixed child of <body> and sits above any rounded, clipping ancestor.",
    "Or remove either ingredient from that ancestor: the border-radius, or the overflow. Either one alone is harmless in 152.",
    "Or give the group a geometry a basic shape can express (a plain rounded rectangle), which the proxy clips with inset() instead of path() — every basic-shape clip-path is unaffected.",
  ],
  report: "spikes/s1-proxy-topology/chrome152-regression/REPORT.md",
  evidence: [
    "Verified repro, spikes/s1-proxy-topology/chrome152-regression/repro.html: 151.0.7922.34 filter-on/filter-off pixel diff 31.37 (live), 152.0.7977.64 diff 0.00 (no-op) with the inset() control at 31.38 in the same build.",
    "The trigger set is the whole 12-cell x 2-build matrix in that directory's REPORT.md: path() only — inset(0 round 22px), inset(0), circle(45%), polygon() and no clip-path are all live in 152 — and only with both overflow: hidden and border-radius on an ancestor; removing either restores the filter.",
    "Found 2026-08-26 through vitrea's own S1 manual-check page in retail Chrome 152; bisected to the three-ingredient shape and re-measured 2026-08-28 for the bug report draft (parent Decision Log #39).",
    "No upper bound is claimed: the report is drafted and unfiled, so no fixed version is known and the row stays open at 152 and above until one is measured.",
    "Scope of the ancestor test, stated: the matrix measured overflow: hidden. The scan also accepts clip, auto and scroll, which produce the same rounded clip on the same element and were not measured — over-triggering on the fail-safe side, as layer 2 already does for unmeasured engine trigger sets. Narrowing it is a measurement, not a judgement call.",
  ],
};

/** Chromium versions the defect above is known to affect. Open-ended by evidence. */
export const CHROMIUM_PATH_CLIP_DEFECT_MIN_VERSION = 152;

/**
 * One ancestor of a proxy, as the defect scan sees it.
 *
 * `describe` matches layer 2's, because a developer reading the advisory has to
 * find the same element in their own source that a backdrop-root break would
 * have named.
 */
export interface AncestorClip {
  readonly element: Element;
  readonly describe: string;
  /** The clipping value found, verbatim, so the message can quote it. */
  readonly overflow: string;
  readonly borderRadius: string;
}

/**
 * Any token other than `visible` clips — `hidden`, `clip`, `auto`, `scroll`.
 *
 * The regression matrix measured `hidden` specifically. Every other clipping
 * value produces the same rounded clip on the same ancestor, so they are
 * included on the fail-safe side, the way layer 2 already over-triggers where an
 * engine's trigger set is unmeasured: an advisory that names its workarounds
 * costs an author a paragraph, and a missed one costs them an unfrosted page
 * they cannot diagnose. Narrowing this is a measurement, not a guess.
 */
function clipsContent(value: string): boolean {
  return value
    .split(/\s+/)
    .filter((token) => token !== "")
    .some((token) => token !== "visible");
}

/** Any positive length or percentage in the value rounds the corner. */
function roundsCorners(value: string): boolean {
  return value
    .split(/[\s/]+/)
    .filter((token) => token !== "")
    .some((token) => Number.parseFloat(token) > 0);
}

const OVERFLOW_PROPERTIES = ["overflow", "overflow-x", "overflow-y"];
const RADIUS_PROPERTIES = [
  "border-radius",
  "border-top-left-radius",
  "border-top-right-radius",
  "border-bottom-right-radius",
  "border-bottom-left-radius",
];

/**
 * The clipping `overflow` value on this element, verbatim, or `undefined` if it
 * does not clip.
 *
 * The shorthand *and* the longhands are read, because environments disagree
 * about which of the two a computed style resolves: browsers expand
 * `overflow: hidden` into both axes, jsdom reports the shorthand and leaves the
 * longhands at their initial values. Reading both is what makes one reader
 * correct in a browser and in the tests that fabricate a chain without one.
 *
 * Exported for the geometry clip chain (Decision Log #41(k)), which asks the
 * same question about the same ancestors and would otherwise define "clips" a
 * second time. That the two definitions must agree is not a coincidence to be
 * preserved by discipline: an ancestor that crops a surface geometrically is an
 * ancestor that crops it optically.
 */
export function clipsContentOf(style: StyleLookup): string | undefined {
  return OVERFLOW_PROPERTIES.map((property) => style(property)).find(clipsContent);
}

/**
 * Whether this element clips with rounded corners, and the values that say so.
 *
 * The *rounded* half is what layer 3 needs: Chromium ≥152 drops
 * `backdrop-filter` under a rounded clipping ancestor specifically, and a
 * square-cornered one is not the hazard.
 */
export function roundedClipOf(style: StyleLookup): { overflow: string; borderRadius: string } | undefined {
  const overflow = clipsContentOf(style);
  if (overflow === undefined) return undefined;

  const borderRadius = RADIUS_PROPERTIES.map((property) => style(property)).find(roundsCorners);
  if (borderRadius === undefined) return undefined;

  return { overflow, borderRadius };
}

/**
 * Which recorded defects this chain actually walks into.
 *
 * Empty is the common answer and the cheap one: a chain with no rounded,
 * clipping ancestor satisfies no precondition on the books, and the default
 * mount never produces one.
 */
export function defectsOnChain(
  defects: readonly EngineDefect[],
  chain: readonly AncestorClip[],
): readonly { readonly defect: EngineDefect; readonly ancestor: AncestorClip }[] {
  if (defects.length === 0 || chain.length === 0) return [];

  const found: { defect: EngineDefect; ancestor: AncestorClip }[] = [];
  for (const defect of defects) {
    // One member today; the switch is what keeps a second one from arriving as
    // an untyped predicate.
    if (defect.precondition !== "rounded-overflow-ancestor") continue;
    const ancestor = chain[0];
    if (ancestor !== undefined) found.push({ defect, ancestor });
  }
  return found;
}

/**
 * The advisory, as an author reads it: what breaks, where, what to do, and where
 * the evidence is.
 */
export function describeEngineDefect(
  groupId: string,
  defect: EngineDefect,
  ancestor: AncestorClip,
): string {
  const numbered = defect.workarounds.map((fix, index) => `(${index + 1}) ${fix}`).join(" ");
  return `Group "${groupId}" builds its backdrop proxy under ${ancestor.describe}, which has overflow: ${ancestor.overflow} together with border-radius: ${ancestor.borderRadius} — the shape of a known engine defect (${defect.id}). ${defect.summary} Nothing here is measurable from inside the page, so this is an advisory rather than a demotion: vitrea cannot tell whether the pixels arrived. Workarounds, cheapest first: ${numbered} The verified repro and the bug report are at ${defect.report}.`;
}

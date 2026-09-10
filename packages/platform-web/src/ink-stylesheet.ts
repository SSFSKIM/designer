/**
 * The runtime's ink, delivered at a precedence an application can beat.
 *
 * The runtime decides what colour is readable on the material it is drawing —
 * that decision is real and it is the library's (Decision Log #32(b)). What was
 * wrong was *how* it arrived: `platform-web` wrote the resolved colour as an
 * inline `color` on the host, and an inline declaration outranks every
 * application rule short of `!important`. So an app that wrote
 * `.my-panel { color: … }` on a glass host watched the declaration parse,
 * cascade, and silently never apply — while the very token it was told to build
 * on, `--vitrea-foreground`, was published on that same element. The seam was
 * real and unusable at the same time (Decision Log #34(c)).
 *
 * The fix separates the two things that were fused. The **token** stays where it
 * was, inline on the host: it is data, an app reads it, nothing in CSS
 * cascades against a custom property it does not declare. The **ink** moves
 * here, into one static rule at `:where()` specificity:
 *
 * ```css
 * :where([data-vitrea-node]) { color: var(--vitrea-foreground); }
 * ```
 *
 * Two consequences, both wanted. The runtime's `color` is now *defined as* the
 * published token rather than merely equal to it, so the documented seam is the
 * mechanism instead of a parallel copy of it. And the declaration sits at
 * specificity 0,0,0, so any application selector that names the host at all —
 * a class, an id, an attribute, even a bare tag — wins outright.
 *
 * **The one rule an app cannot outrank this way** is a selector that is also
 * exactly 0,0,0 (`*`, or its own `:where()`), where source order decides. The
 * sheet is therefore *prepended* to `<head>` rather than adopted: a constructed
 * stylesheet in `document.adoptedStyleSheets` sorts after every document sheet
 * and would win that tiebreak, which is the wrong way round. Prepended, every
 * application sheet — already in the document or added later — comes after this
 * one, and the app wins there too.
 *
 * Where a host is registered but no frame has written the token yet, the
 * `var()` is invalid at computed-value time, which makes `color` compute to
 * `unset` — for an inherited property, `inherit`. That is exactly the state the
 * element was in before vitrea touched it.
 */

import { HOST_ATTRIBUTES } from "./host";

/**
 * The whole stylesheet. Static: it names no colour, only the indirection, so it
 * is written once per document and never rewritten no matter how many hosts,
 * groups or roots the page carries.
 */
export const INK_RULE = `:where([${HOST_ATTRIBUTES.node}]) { color: var(--vitrea-foreground); }`;

/** Marks the element so a second root finds it instead of adding another. */
export const INK_STYLESHEET_ATTRIBUTE = "data-vitrea-ink-stylesheet";

/**
 * Whether this document's own CSS names a token — the cheapest honest way to
 * tell that an app has opted into one of the published ink levels (W27a).
 *
 * There is no mechanism that observes a custom property being *read*: a `var()`
 * resolves during style computation and leaves no trace an author's code, or
 * ours, can query. What can be observed is the text of the rules the document
 * carries, and for a dev-mode finding that is enough — the question being asked
 * is "is this page using the quaternary level anywhere, on a page that also has
 * a surface too thin to carry it", which is a question about the document.
 *
 * **Both sheet lists**, because a document has two. `document.styleSheets` is
 * the parsed `<style>` and `<link>` elements; `document.adoptedStyleSheets` is
 * where a constructed `CSSStyleSheet` goes, and that is how every framework
 * shipping CSS-in-JS with `CSSStyleSheet.replaceSync` puts its rules on the
 * page. Reading only the first would have made the finding silent on exactly the
 * apps most likely to be styling against a token vocabulary. (The property is
 * absent in some non-browser DOM implementations, so it is read defensively —
 * a missing list is an empty one, not a throw.)
 *
 * What it cannot see, stated rather than implied: a cross-origin stylesheet
 * (reading `cssRules` throws and the sheet is skipped), a token written into an
 * inline `style` attribute, and a rule edited in place inside a sheet the page
 * already had. All three are false negatives, which is the right direction for
 * an advisory to be wrong in. The one false positive it can produce is a rule
 * that names the token and never matches a glass surface — and the finding is
 * phrased as the pair it actually found, not as a claim about one element.
 *
 * Cached per document and per token, and the cache is valid exactly while the
 * sheet **list** is the one the answer was taken over — both lists, concatenated,
 * compared by identity element by element rather than by count. A count would be
 * cheaper and wrong in the case an app actually produces: one sheet leaving as
 * another arrives is what a theme swap is, and it holds the count still.
 *
 * That comparison is a few object identities per call, against a scan that walks
 * every rule in the page. Doing it on the way in is why this needs no
 * `MutationObserver` on the head — a subscription every page would pay for, to
 * answer a question almost none of them ask.
 */
interface TokenScan {
  readonly sheets: readonly CSSStyleSheet[];
  readonly found: boolean;
}

const tokenScans = new WeakMap<Document, Map<string, TokenScan>>();

const sameSheets = (a: readonly CSSStyleSheet[], b: readonly CSSStyleSheet[]): boolean =>
  a.length === b.length && a.every((sheet, index) => sheet === b[index]);

export function documentStylesNameToken(document: Document, token: string): boolean {
  const cache = tokenScans.get(document) ?? new Map<string, TokenScan>();
  tokenScans.set(document, cache);
  const sheets = [
    ...Array.from(document.styleSheets),
    // Absent in some non-browser DOM implementations, and an absent list is an
    // empty one rather than a reason to throw inside a dev-mode advisory.
    ...(document.adoptedStyleSheets ?? []),
  ];
  const prior = cache.get(token);
  if (prior !== undefined && sameSheets(prior.sheets, sheets)) return prior.found;

  let found = false;
  for (const sheet of sheets) {
    let rules: CSSRuleList | undefined;
    try {
      rules = sheet.cssRules;
    } catch {
      // A cross-origin sheet. Not readable, and not this package's to complain
      // about — the app is entitled to load one.
      continue;
    }
    // A grouping rule's `cssText` carries its children's, so `@media` and
    // `@supports` blocks need no descent of their own.
    for (const rule of Array.from(rules)) {
      if (rule.cssText.includes(token)) {
        found = true;
        break;
      }
    }
    if (found) break;
  }

  cache.set(token, { sheets, found });
  return found;
}

export interface InkStylesheetHandle {
  /** The element carrying the rule — exposed so a test can read it back. */
  readonly element: HTMLStyleElement;
  /** Drops this root's claim; the last one out removes the element. */
  dispose(): void;
}

interface Installation {
  readonly element: HTMLStyleElement;
  refs: number;
}

/**
 * One installation per document, reference-counted.
 *
 * Two roots on one page is a supported shape (the demo runs one per section),
 * and the rule is identical for all of them, so a second copy would be dead
 * weight in the cascade rather than a second opinion.
 */
const installations = new WeakMap<Document, Installation>();

export function installInkStylesheet(document: Document): InkStylesheetHandle {
  const existing = installations.get(document);
  if (existing !== undefined && existing.element.isConnected) {
    existing.refs += 1;
    return handleFor(document, existing);
  }

  const element = document.createElement("style");
  element.setAttribute(INK_STYLESHEET_ATTRIBUTE, "");
  element.textContent = INK_RULE;

  // First in the head, so the app's own sheets — this document's and any it
  // adds later — sort after it and win the 0,0,0 tiebreak. `documentElement` is
  // the fallback for a document assembled without a head, which no browser
  // produces but a fixture can.
  const parent = document.head ?? document.documentElement;
  parent.prepend(element);

  const installation: Installation = { element, refs: 1 };
  installations.set(document, installation);
  return handleFor(document, installation);
}

function handleFor(document: Document, installation: Installation): InkStylesheetHandle {
  let released = false;
  return {
    element: installation.element,
    dispose() {
      // Idempotent: `destroy()` is allowed to be called twice, and a
      // double-decrement would evict the sheet from under a live sibling root.
      if (released) return;
      released = true;
      installation.refs -= 1;
      if (installation.refs > 0) return;
      installation.element.remove();
      installations.delete(document);
    },
  };
}

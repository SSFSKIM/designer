/**
 * Probe layer 1 — the support gate.
 *
 * Necessary, never sufficient. `CSS.supports('backdrop-filter','blur(1px)')`
 * returns `true` in Firefox 154 and WebKit 26.5 builds that S1 measured
 * rendering *nothing at all*, and it returns `true` for
 * `backdrop-filter: url(#x)` in all three engines although only Chromium
 * renders reference filters inside `backdrop-filter`. So this layer catches
 * exactly one thing: the total absence of the property. It says so about itself
 * — `reach` travels with the verdict — so a caller cannot mistake it for a
 * conformance answer.
 *
 * Both spellings are tested and both must be emitted in CSS: WebKit reports
 * `true` for the prefixed form and `false` unprefixed, Chromium and Gecko the
 * reverse.
 */

export const BACKDROP_FILTER_PROPERTIES = [
  "backdrop-filter",
  "-webkit-backdrop-filter",
] as const;

export type BackdropFilterProperty = (typeof BACKDROP_FILTER_PROPERTIES)[number];

/** The one value worth asking about: a minimal blur. */
const PROBE_VALUE = "blur(1px)";

/** Asked one property at a time; the value is always `PROBE_VALUE`. */
export type SupportsPredicate = (property: BackdropFilterProperty) => boolean;

export interface SupportGateResult {
  readonly supported: boolean;
  /** The spellings that answered yes — the ones the emitted CSS must carry. */
  readonly properties: readonly BackdropFilterProperty[];
  /** What this layer can see. Not decoration: the honesty core turns on it. */
  readonly reach: "property-presence-only";
}

export function checkSupportGate(supports: SupportsPredicate): SupportGateResult {
  const properties = BACKDROP_FILTER_PROPERTIES.filter(supports);

  return { supported: properties.length > 0, properties, reach: "property-presence-only" };
}

/** The live gate. Wrapped so the pure form above stays testable without a browser. */
export function checkSupportGateInBrowser(): SupportGateResult {
  return checkSupportGate((property) => CSS.supports(property, PROBE_VALUE));
}

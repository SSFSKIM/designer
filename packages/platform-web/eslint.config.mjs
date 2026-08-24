import { browser } from "../../eslint.config.mjs";

/**
 * The steady-state-zero-layout-reads guarantee (§Geometry) is only as true as
 * the instrumentation behind it, and instrumentation only counts what routes
 * through it. So every layout and style read in this package goes through
 * `src/measure.ts`, and this rule is what keeps that from decaying into a
 * comment: a stray `getBoundingClientRect` anywhere else is an uncounted read,
 * which would make the meter — and the test that asserts zero — lie.
 */
const UNMETERED_READS = [
  {
    selector: "MemberExpression > Identifier.property[name='getBoundingClientRect']",
    message:
      "Layout reads go through src/measure.ts so the read meter counts them. An unmetered read makes the zero-steady-state-reads assertion untrue.",
  },
  {
    selector: "MemberExpression > Identifier.property[name='getClientRects']",
    message: "Layout reads go through src/measure.ts so the read meter counts them.",
  },
  {
    selector: "CallExpression > Identifier[name='getComputedStyle']",
    message:
      "Computed-style reads go through src/measure.ts so the read meter counts them — the backdrop-root audit is a read like any other.",
  },
];

export default [
  ...browser,
  {
    files: ["src/**/*.ts"],
    ignores: ["src/measure.ts"],
    rules: { "no-restricted-syntax": ["error", ...UNMETERED_READS] },
  },
];

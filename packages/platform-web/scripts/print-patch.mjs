/**
 * Print a profile document's `patch` block as TypeScript source.
 *
 * Shared by the generators that mirror a calibration profile document into this
 * package (`generate-dark-profile.mjs`, `generate-macos27-profile.mjs`). It is
 * one function in one file because the two generators have to agree character
 * for character: each is gated by a test in `@vitrea/calibration` that
 * deep-equals the generated module against the document it came from, and a
 * second printer drifting from this one would make "regenerate and commit"
 * produce a diff that is formatting rather than measurement.
 */

const IDENTIFIER = /^[A-Za-z_$][A-Za-z0-9_$]*$/;

/**
 * Print one JSON value as TypeScript. Numeric arrays stay on one line because a
 * colour or an anchor triple is one leaf of the material and reads as one — the
 * patch type takes them as fixed-length tuples for the same reason.
 */
export function print(value, indent) {
  if (Array.isArray(value)) return `[${value.map((entry) => print(entry, indent)).join(", ")}]`;
  if (value !== null && typeof value === "object") {
    const inner = `${indent}  `;
    const lines = Object.entries(value).map(([key, entry]) => {
      const name = IDENTIFIER.test(key) ? key : JSON.stringify(key);
      return `${inner}${name}: ${print(entry, inner)},`;
    });
    return `{\n${lines.join("\n")}\n${indent}}`;
  }
  return JSON.stringify(value);
}

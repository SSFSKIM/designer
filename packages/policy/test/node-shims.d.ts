/**
 * The five Node functions this package's purity test needs, declared by hand
 * instead of by depending on `@types/node` — the same trade `@vitrea/geometry`
 * makes, and for the same reason.
 *
 * Adding `@types/node` would declare ~2000 ambient globals including `process`,
 * `navigator` and `setTimeout`, and every one of them would become visible to
 * `src/` too, at which point X4's "no DOM, no Node, no clocks" would rest on the
 * ESLint layer alone. Declaring the *modules* rather than the globals keeps the
 * ambient global scope empty, and `purity.test.ts` asserts that `src/` imports
 * nothing non-relative anyway.
 */

declare module "node:fs" {
  export function readFileSync(path: string, encoding: "utf8"): string;
  export function readdirSync(path: string): string[];
}

declare module "node:path" {
  export function join(...parts: string[]): string;
  export function dirname(path: string): string;
}

declare module "node:url" {
  export function fileURLToPath(url: string): string;
}

interface ImportMeta {
  readonly url: string;
}

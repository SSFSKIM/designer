/**
 * The five Node functions the test tree needs, declared by hand instead of by
 * depending on `@types/node`.
 *
 * This is not squeamishness, it is the point of `purity.test.ts`. Adding
 * `@types/node` would declare ~2000 ambient globals including `process`,
 * `navigator` and `setTimeout`, and every one of them would become visible to
 * `src/` too — at which case X4's "no DOM, no Node, no clocks" would rest on the
 * ESLint layer alone. (Core made that trade for its tooling tests and documented
 * it; geometry does not have to.)
 *
 * Declaring the modules rather than the globals keeps the ambient global scope
 * empty. `src/` still cannot reach these: the shared `pure` ESLint config bans
 * importing Node built-ins outright, and nothing in `src/` imports anything
 * non-relative — which `purity.test.ts` also asserts.
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

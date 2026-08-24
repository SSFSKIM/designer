/**
 * Reading one environment flag, without pulling `@types/node` into the package.
 *
 * `tsconfig.base.json` sets `types: []`, and geometry deliberately keeps it that
 * way: with no ambient Node or DOM types, X4's "no DOM" and "no Node built-ins"
 * are enforced by the type system in `src/` and not only by lint. (Core had to
 * add `types: ["node"]` for its tooling tests, which declares `navigator` and so
 * moves half of its X4 guarantee onto the ESLint layer.) One module-scoped
 * ambient declaration buys the test tree the single global it needs and gives up
 * nothing.
 */

declare const process: { readonly env: Readonly<Record<string, string | undefined>> };

export function envFlag(name: string): boolean {
  return typeof process !== "undefined" && process.env[name] === "1";
}

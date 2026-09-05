/**
 * Writing a line to the run's output, without pulling `@types/node` into the
 * package — `env.ts`'s pattern, for the other global a reporting test needs.
 *
 * `tsconfig.base.json` sets `types: []` and geometry deliberately keeps it that
 * way, so X4's "no DOM, no Node built-ins" is enforced by the type system in
 * `src/` rather than only by lint. One module-scoped ambient declaration buys
 * the test tree the global it needs and gives up nothing.
 *
 * A test that REPORTS rather than only asserts is why this exists: W20 G0's
 * conformance table is the deliverable, and a table nobody can read is a table
 * that gets re-derived by hand the next time someone needs it.
 */

declare const process: { readonly stdout: { write(text: string): void } };

export function say(text: string): void {
  process.stdout.write(`${text}\n`);
}

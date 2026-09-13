import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { expect, it } from "vitest";
// Through the package entry, like dark-profile-export.test.ts: `@vitreajs/vitrea-web`
// resolves to `dist/`, so what is pinned is the artifact a consumer installs. The
// relative source path also dragged DOM-typed platform-web sources into this
// package's DOM-free project, which `tsc --noEmit` refuses by design.
import { recededMaterialProfile } from "@vitreajs/vitrea-web";

it("keeps the exported inactive endpoints equal to the frozen fitting declaration", () => {
  // This is an evidence pin, like dark-profile-export.test.ts: a material change
  // must publish its new declaration rather than silently keeping old claims.
  // It follows the LIVE declaration, which W27c G1c's fit made
  // `2026-09-13-w27c-g1c-fit/fitted-endpoint.json` (claims §5.141); §5.130's
  // corrected declaration stays on disk unchanged and is pinned below as the
  // endpoint that one superseded, so the pin says what moved as well as what is.
  const declaration = JSON.parse(readFileSync(resolve(import.meta.dirname,
    "../results/2026-09-13-w27c-g1c-fit/fitted-endpoint.json"), "utf8")) as { patch: unknown };
  expect(recededMaterialProfile).toEqual(declaration.patch);
});

it("moved exactly the two fields W27c G1c's fit declares, and only in the light entry", () => {
  // The claim the ledger makes about this fit is that it is two fields of one
  // scheme entry, so it is the claim the suite checks rather than a prose line
  // nobody can fail. T1's term was refused on its controls (§5.141 §3), which is
  // why the DARK entry has to be byte-identical to the endpoint it supersedes.
  const superseded = JSON.parse(readFileSync(resolve(import.meta.dirname,
    "../results/2026-09-10-w27c-g1-corrected-declaration.json"), "utf8")) as {
      patch: Record<"light" | "dark", Record<string, unknown>> };
  expect(recededMaterialProfile.dark).toEqual(superseded.patch.dark);
  const moved = Object.keys({ ...superseded.patch.light, ...recededMaterialProfile.light })
    .filter((key) => JSON.stringify((recededMaterialProfile.light as Record<string, unknown>)[key])
      !== JSON.stringify(superseded.patch.light[key]));
  expect(moved.sort()).toEqual(["increasedOcclusionLift", "refractionScale"]);
});

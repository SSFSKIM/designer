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
  const declaration = JSON.parse(readFileSync(resolve(import.meta.dirname,
    "../results/2026-09-10-w27c-g1-declaration.json"), "utf8")) as { patch: unknown };
  expect(recededMaterialProfile).toEqual(declaration.patch);
});

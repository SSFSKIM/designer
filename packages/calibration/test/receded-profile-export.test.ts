import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { expect, it } from "vitest";
// Through the package entry: this pins the artifact a consumer installs.
import { recededMaterialProfile } from "@vitreajs/vitrea-web";

it("keeps the exported inactive endpoints equal to the frozen W28 declaration", () => {
  const declaration = JSON.parse(readFileSync(resolve(import.meta.dirname,
    "../results/2026-09-14-w28-g1-silhouette/fitted-endpoint.json"), "utf8")) as { patch: unknown };
  expect(recededMaterialProfile).toEqual(declaration.patch);
});

it("changes only the abscissa and response rows beyond G1d", () => {
  const superseded = JSON.parse(readFileSync(resolve(import.meta.dirname,
    "../results/2026-09-14-w27c-g1d/fitted-endpoint.json"), "utf8")) as {
      patch: Record<"light" | "dark", Record<string, unknown>> };
  const allowed = new Set([
    "backdropToneAbscissa", "backdropToneAnchorX",
    "backdropToneResponseThin", "backdropToneResponseThick",
  ]);
  for (const scheme of ["light", "dark"] as const) {
    const current = recededMaterialProfile[scheme] as Record<string, unknown>;
    const changed = Object.keys({ ...superseded.patch[scheme], ...current })
      .filter((key) => JSON.stringify(current[key]) !== JSON.stringify(superseded.patch[scheme][key]));
    expect(changed).toContain("backdropToneAbscissa");
    expect(changed.filter((key) => !allowed.has(key))).toEqual([]);
  }
});

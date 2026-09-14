import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { expect, it } from "vitest";
// Through the package entry: this pins the artifact a consumer installs.
import { recededMaterialProfile } from "@vitreajs/vitrea-web";

it("keeps the exported inactive endpoints equal to the frozen G1d declaration", () => {
  const declaration = JSON.parse(readFileSync(resolve(import.meta.dirname,
    "../results/2026-09-14-w27c-g1d/fitted-endpoint.json"), "utf8")) as { patch: unknown };
  expect(recededMaterialProfile).toEqual(declaration.patch);
});

it("moves exactly Decision Logs 18 and 19's fields beyond G1c", () => {
  const superseded = JSON.parse(readFileSync(resolve(import.meta.dirname,
    "../results/2026-09-13-w27c-g1c-fit/fitted-endpoint.json"), "utf8")) as {
      patch: Record<"light" | "dark", Record<string, unknown>> };
  const moved = (scheme: "light" | "dark"): string[] =>
    Object.keys({ ...superseded.patch[scheme], ...recededMaterialProfile[scheme] })
      .filter((key) => JSON.stringify(
        (recededMaterialProfile[scheme] as Record<string, unknown>)[key],
      ) !== JSON.stringify(superseded.patch[scheme][key]))
      .sort();
  expect(moved("light")).toEqual(["increasedOcclusionLiftByPolicy"]);
  expect(moved("dark")).toEqual([
    "backdropToneAnchorX",
    "backdropToneResponseThick",
    "backdropToneResponseThin",
  ]);
});

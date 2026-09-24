/** The live demo's digest lookup at all four sealed endpoints (§5.180 clause 8). */
import assert from "node:assert/strict";
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { endpointByDigest, LAWS_DOCUMENT, toneLaw } from "../../../../apps/demo/src/laws/law";

const here = import.meta.dirname;
const seal = JSON.parse(readFileSync(resolve(
  here, "../2026-09-24-w36-g1-black-branch/sealed-manifest.json",
), "utf8")) as { documents: Record<string, { resolvedMaterialSha256: string }> };
const endpoints = Object.entries(seal.documents).map(([name, record]) => {
  const endpoint = endpointByDigest(LAWS_DOCUMENT, record.resolvedMaterialSha256);
  assert(endpoint);
  assert.equal(endpoint.scheme, name.includes("-dark-") ? "dark" : "light");
  assert.equal(endpoint.pose, name.includes("-receded") ? "receded" : "active");
  assert.equal(endpoint.patch?.backdropToneBlackStrength, 1);
  return { document: name, digest: record.resolvedMaterialSha256,
    profileKey: endpoint.profileKey, pose: endpoint.pose, scheme: endpoint.scheme,
    blackThin: endpoint.patch?.backdropToneBlackThin,
    blackThick: endpoint.patch?.backdropToneBlackThick };
});
const black = toneLaw(0);
const expected = ((132 / 255 + 0.055) / 1.055) ** 2.4;
assert.equal(black.encoded, 0);
assert.equal(black.small, expected);
assert.equal(black.large, expected);
const result = { endpoints, black, smallSpan: 40, largeSpan: 112,
  qualification: "The page's spans differ from the measured span44; thick black is extrapolated." };
writeFileSync(resolve(here, "laws-reference.json"), JSON.stringify(result, null, 2) + "\n", { flag: "wx" });
console.log(JSON.stringify(result, null, 2));

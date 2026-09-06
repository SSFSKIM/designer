/**
 * Generate `src/dark-profile.ts` from the calibration profile document.
 *
 * X7 of the W21 spec asks for ONE source: the shipped dark patch and
 * `packages/calibration/profiles/apple-macos-26.5-1x-dark-standard.json` must be
 * the same numbers. There are two honest ways to hold that — mirror the document
 * by hand and pin the mirror with a test, or generate the mirror and keep the
 * test as the guard — and this is the second, because the published bundle must
 * not carry a runtime edge to the calibration package. `@vitrea/calibration` is
 * private and Node-shaped; importing its JSON from `platform-web` would put a
 * data dependency into a published tarball for numbers that never move between
 * releases (the same argument `tuned-profiles.test.ts` opens with).
 *
 * So the JSON crosses the package boundary exactly once, here, at author time.
 * Run it after a wave re-records the document:
 *
 *     pnpm --filter @vitreajs/vitrea-web run profile:dark
 *
 * and commit the regenerated module.
 * `packages/calibration/test/dark-profile-export.test.ts` fails until you do.
 */

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
// Imported rather than taken off the global, so this file needs no environment
// declaration to lint inside a package whose own rules are the browser's.
import process from "node:process";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const documentPath = join(
  here,
  "..",
  "..",
  "calibration",
  "profiles",
  "apple-macos-26.5-1x-dark-standard.json",
);
const modulePath = join(here, "..", "src", "dark-profile.ts");

const IDENTIFIER = /^[A-Za-z_$][A-Za-z0-9_$]*$/;

/**
 * Print one JSON value as TypeScript. Numeric arrays stay on one line because a
 * colour or an anchor triple is one leaf of the material and reads as one — the
 * patch type takes them as fixed-length tuples for the same reason.
 */
function print(value, indent) {
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

const profileDocument = JSON.parse(readFileSync(documentPath, "utf8"));

const source = `/**
 * The dark-standard material, as a published package carries it.
 *
 * GENERATED — do not edit. \`scripts/generate-dark-profile.mjs\` writes this file
 * from \`packages/calibration/profiles/${profileDocument.profileKey}.json\`,
 * whose \`patch\` block is the authority for every number below;
 * \`packages/calibration/test/dark-profile-export.test.ts\` deep-equals the two in
 * both directions, so a wave that re-records the document and forgets to
 * regenerate this module fails there.
 *
 * ## What it is, and what it is not
 *
 * A **patch** over the renderer's \`DEFAULT_MATERIAL_PROFILE\`, exactly like the
 * one an app passes as \`createGlassRoot({ materialProfile })\` — not a second
 * material. Only one colour scheme's numbers can be the runtime default and the
 * default is light-standard, so this document holds the difference: what
 * measurement found the dark reference does differently. The light scheme needs
 * no counterpart, because the light profile document IS the identity with the
 * runtime default (\`identityWithRuntimeDefault\`, pinned by
 * \`tuned-profiles.test.ts\`) — "light" is the absence of a patch, not another one.
 *
 * Reach for it through \`createGlassRoot({ colorScheme: "dark" | "auto" })\`, which
 * selects it and merges an app's own \`materialProfile\` over the top. It is
 * exported by name as well, because an app that resolves its scheme somewhere
 * vitrea cannot see should be able to hand the patch over directly.
 *
 * A backdrop \`hint\` and this are different things: the hint states the tone of
 * what is BEHIND the surface, and the scheme states which material the surface
 * is made of.
 */

import type { RendererMaterialProfile } from "./renderer-bridge";

export const darkMaterialProfile: RendererMaterialProfile = ${print(profileDocument.patch, "")};
`;

writeFileSync(modulePath, source);
process.stdout.write(`wrote ${modulePath} from ${profileDocument.profileKey}\n`);

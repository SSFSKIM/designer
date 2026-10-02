/**
 * Generate `src/macos27-glass025-profile.ts` from the four sealed `-glass0.25` profile documents.
 *
 * The sibling of `generate-macos27-profile.mjs`, under the same rule: the numbers a published
 * package draws with must be the numbers a calibration document records, so the boundary is
 * crossed once, here, at author time. The four documents are Apple's macOS 27 material at the
 * Glass appearance slider's 0.25 position (`NSGlassTintAmount` 0.25, the clearer glass), sealed by
 * W43 G3 (ii) (claims §5.201) and each a patch over the same unmoved `DEFAULT_MATERIAL_PROFILE`
 * as the 0.5 documents, naming exactly their leaves (W43 X44).
 *
 * The module exists one step before the rest of W43 Decision Log 1 (RULED (a): a second set of
 * documents through the existing `materialProfileDocument` option, the default staying 0.5)
 * because the generation's PUBLICATION needs it: a stage reads a shipped material in strict mode,
 * selected by the (OS, glass) pair, so the 0.25 documents must be in the registry before their
 * canonical read. The default document, the README and the position readout are unchanged here.
 *
 * Run it after a wave re-records any of the four:
 *
 *     pnpm --filter @vitreajs/vitrea-web run profile:macos27-glass025
 *
 * and commit the regenerated module. `packages/calibration/test/macos27-profile-export.test.ts`
 * fails until you do.
 */

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
// Imported rather than taken off the global, so this file needs no environment
// declaration to lint inside a package whose own rules are the browser's.
import process from "node:process";
import { fileURLToPath } from "node:url";

import { print } from "./print-patch.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const profiles = join(here, "..", "..", "calibration", "profiles");
const modulePath = join(here, "..", "src", "macos27-glass025-profile.ts");

const read = (key) => {
  const document = JSON.parse(readFileSync(join(profiles, `${key}.json`), "utf8"));
  if (document.profileKey !== key) {
    throw new Error(`${key}.json declares profileKey ${document.profileKey}`);
  }
  if (typeof document.resolvedMaterialSha256 !== "string") {
    throw new Error(`${key}: no resolvedMaterialSha256 in the document`);
  }
  return document;
};

const light = read("apple-macos-27.0-1x-light-standard-glass0.25");
const dark = read("apple-macos-27.0-1x-dark-standard-glass0.25");
const recededLight = read("apple-macos-27.0-1x-light-standard-glass0.25-receded");
const recededDark = read("apple-macos-27.0-1x-dark-standard-glass0.25-receded");

// One crossing per material family: the light document records the mapping, the dark document
// names the subset it shares, and a disagreement stops the script (as for 0.5).
const mapping = { ...light.cssTierMapping };
for (const [key, value] of Object.entries(dark.cssTierMapping ?? {})) {
  const held = mapping[key];
  if (held !== undefined && JSON.stringify(held) !== JSON.stringify(value)) {
    throw new Error(
      `cssTierMapping.${key}: the light document says ${JSON.stringify(held)} and the dark ` +
        `document says ${JSON.stringify(value)} — one material family cannot have two crossings`,
    );
  }
  mapping[key] = value;
}

for (const receded of [recededLight, recededDark]) {
  const over = receded.resolvedOverActiveDocument;
  const expected = receded.profileKey.replace(/-receded$/, "");
  if (over !== `${expected}.json`) {
    throw new Error(`${receded.profileKey} applies over ${over}, not over ${expected}.json`);
  }
}

const source = `/**
 * The macOS 27 material at the Glass appearance slider's 0.25 position (the clearer glass), as a
 * published package carries it.
 *
 * GENERATED — do not edit. \`scripts/generate-macos27-glass025-profile.mjs\` writes this file from
 * the four documents named below, whose \`patch\` blocks are the authority for every number in it;
 * \`packages/calibration/test/macos27-profile-export.test.ts\` deep-equals each pair in both
 * directions, so a wave that re-records a document and forgets to regenerate this module fails
 * there.
 *
 * Four **patches** over the renderer's \`DEFAULT_MATERIAL_PROFILE\`, exactly as the 0.5 material's
 * are, measured at \`NSGlassTintAmount\` 0.25 (W43, claims §5.199 to §5.201): the active material
 * per colour scheme (\`${light.profileKey}\`, \`${dark.profileKey}\`), each serving both scales, and
 * the receded difference per colour scheme, applied OVER the active patch of the same scheme
 * (\`${recededLight.profileKey}\`, \`${recededDark.profileKey}\`). They name exactly the 0.5
 * material's leaves, so the two are points in one space.
 *
 * Not the default: a page chooses it through \`createGlassRoot({ materialProfileDocument })\`.
 */

import type { CssTierMapping } from "./optics";
import type { RendererMaterialProfile } from "./renderer-bridge";

/** The macOS 27 light-standard material, measured at \`NSGlassTintAmount\` 0.25. */
export const macos27Glass025LightMaterialProfile: RendererMaterialProfile = ${print(light.patch, "")};

/** The macOS 27 dark-standard material at 0.25, in the same relation to the default. */
export const macos27Glass025DarkMaterialProfile: RendererMaterialProfile = ${print(dark.patch, "")};

/**
 * The macOS 27 receded endpoints at 0.25: a difference over the ACTIVE 0.25 patch of the same
 * scheme, not a second material. They cast no exterior shadow, as at 0.5 (W32 Decision Log 2).
 */
export const macos27Glass025RecededMaterialProfile: Readonly<
  Record<"light" | "dark", RendererMaterialProfile>
> = {
  light: ${print(recededLight.patch, "  ")},
  dark: ${print(recededDark.patch, "  ")},
};

/** The CSS tier's crossing for the 0.25 material: the 0.5 one, unchanged by the refit. */
export const macos27Glass025CssTierMapping: Partial<CssTierMapping> = ${print(mapping, "")};

/**
 * Each endpoint's resolved-material digest, the documents' own \`resolvedMaterialSha256\` under
 * digest rule 2; the receded two over the composition the page performs (the receded difference
 * over the active 0.25 patch of the same scheme over the renderer's default).
 */
export const MACOS_27_GLASS025_RESOLVED_MATERIAL_SHA256 = {
  light: ${JSON.stringify(light.resolvedMaterialSha256)},
  dark: ${JSON.stringify(dark.resolvedMaterialSha256)},
  recededLight: ${JSON.stringify(recededLight.resolvedMaterialSha256)},
  recededDark: ${JSON.stringify(recededDark.resolvedMaterialSha256)},
} as const;
`;

writeFileSync(modulePath, source);
process.stdout.write(`wrote ${modulePath} from four macOS 27 glass 0.25 documents\n`);

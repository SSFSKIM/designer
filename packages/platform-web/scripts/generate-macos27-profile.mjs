/**
 * Generate `src/macos27-profile.ts` from the four macOS 27 profile documents.
 *
 * The sibling of `generate-dark-profile.mjs`, for the same reason and under the
 * same rule: the numbers a published package draws with must be the numbers a
 * calibration document records, and the honest way to hold that without putting
 * a runtime edge from `@vitreajs/vitrea-web` into the private, Node-shaped
 * calibration package is to cross the boundary once, here, at author time.
 *
 * Four documents rather than one, because macOS 27's material is measured on
 * four axes this runtime selects between — the active material per colour
 * scheme, and the receded (unfocused-window) difference per colour scheme —
 * and each is its own fitted document with its own `resolvedMaterialSha256`.
 * The light document additionally carries the `cssTierMapping` the same
 * material costs to express as one `backdrop-filter` plus an overlay; the dark
 * document names the one key of it that is scheme-independent, and this script
 * refuses to write a module where the two disagree.
 *
 * Run it after a wave re-records any of the four:
 *
 *     pnpm --filter @vitreajs/vitrea-web run profile:macos27
 *
 * and commit the regenerated module.
 * `packages/calibration/test/macos27-profile-export.test.ts` fails until you do.
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
const modulePath = join(here, "..", "src", "macos27-profile.ts");

const read = (key) => {
  const document = JSON.parse(readFileSync(join(profiles, `${key}.json`), "utf8"));
  if (document.profileKey !== key) {
    throw new Error(`${key}.json declares profileKey ${document.profileKey}`);
  }
  return document;
};

const light = read("apple-macos-27.0-1x-light-standard-glass0.5");
const dark = read("apple-macos-27.0-1x-dark-standard-glass0.5");
const recededLight = read("apple-macos-27.0-1x-light-standard-glass0.5-receded");
const recededDark = read("apple-macos-27.0-1x-dark-standard-glass0.5-receded");

/*
 * The CSS tier's mapping is one per document family, not one per scheme: it is
 * the crossing from the material to `backdrop-filter` plus an overlay, and the
 * root resolves a scheme after that crossing's constants are fixed. The light
 * document is where the whole mapping is recorded; the dark document names the
 * subset that was refit with it. Any key they both name and disagree on would
 * make "which mapping is the 27 mapping" unanswerable, so it stops the script.
 */
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
 * The macOS 27 material, as a published package carries it.
 *
 * GENERATED — do not edit. \`scripts/generate-macos27-profile.mjs\` writes this
 * file from the four documents named below, whose \`patch\` blocks are the
 * authority for every number in it;
 * \`packages/calibration/test/macos27-profile-export.test.ts\` deep-equals each
 * pair in both directions, so a wave that re-records a document and forgets to
 * regenerate this module fails there.
 *
 * ## What these are
 *
 * Four **patches** over the renderer's \`DEFAULT_MATERIAL_PROFILE\`, which W29
 * Decision Log 1 (i) holds still at the macOS 26.5 light material so that the
 * frozen 26.5 documents keep their identity pin. "macOS 27 is the default" is
 * therefore a **selection** — \`material-document.ts\` assembles these four into
 * the document a root resolves when an app asks for nothing — and not a moved
 * constant.
 *
 * - the active material per colour scheme (\`${light.profileKey}\`,
 *   \`${dark.profileKey}\`), each serving both scales;
 * - the receded difference per colour scheme, applied OVER the active patch of
 *   the same scheme when the window loses focus (\`${recededLight.profileKey}\`,
 *   \`${recededDark.profileKey}\`).
 *
 * The light document also records what this material costs to express on the
 * CSS tier, and that mapping is one per family rather than one per scheme.
 *
 * Reach for any of it through \`createGlassRoot({ materialProfileDocument })\`;
 * the constants are exported by name as well, for an app composing a material
 * of its own over one of them.
 */

import type { CssTierMapping } from "./optics";
import type { RendererMaterialProfile } from "./renderer-bridge";

/** The macOS 27 light-standard material, measured at \`NSGlassTintAmount\` 0.5. */
export const macos27LightMaterialProfile: RendererMaterialProfile = ${print(light.patch, "")};

/** The macOS 27 dark-standard material, in the same relation to the default. */
export const macos27DarkMaterialProfile: RendererMaterialProfile = ${print(dark.patch, "")};

/**
 * The macOS 27 receded endpoints: a difference over the ACTIVE patch of the same
 * scheme, not a second material. The largest single change from macOS 26.5 is
 * that a receded surface keeps its outer shadow, where the 26.5 endpoint removes
 * it (claims §5.154 §6).
 */
export const macos27RecededMaterialProfile: Readonly<
  Record<"light" | "dark", RendererMaterialProfile>
> = {
  light: ${print(recededLight.patch, "  ")},
  dark: ${print(recededDark.patch, "  ")},
};

/**
 * What the macOS 27 material costs to express as one \`backdrop-filter\` plus an
 * \`rgba()\` overlay. \`blurSigmaScale\` is the constant that carries the CSS
 * tier's whole share of the 27 diffusion refit (claims §5.153 §2).
 */
export const macos27CssTierMapping: Partial<CssTierMapping> = ${print(mapping, "")};

/**
 * Each document's \`resolvedMaterialSha256\` — the digest over the material it
 * resolves to, not over the patch. Reported by the root's material readout so a
 * capture, a test or the demo's capabilities panel can say which document drew,
 * and pinned document-side by \`packages/calibration/test/tuned-profiles.test.ts\`.
 */
export const MACOS_27_RESOLVED_MATERIAL_SHA256 = {
  light: ${JSON.stringify(light.resolvedMaterialSha256)},
  dark: ${JSON.stringify(dark.resolvedMaterialSha256)},
  recededLight: ${JSON.stringify(recededLight.resolvedMaterialSha256)},
  recededDark: ${JSON.stringify(recededDark.resolvedMaterialSha256)},
} as const;
`;

writeFileSync(modulePath, source);
process.stdout.write(`wrote ${modulePath} from four macOS 27 documents\n`);

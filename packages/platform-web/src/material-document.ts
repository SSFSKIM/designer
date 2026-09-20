/**
 * A material profile **document**, as a root selects one (W29 G4, Decision Logs
 * 2 and 7 (b)).
 *
 * ## Why a document rather than two options
 *
 * A measured material has halves that have to travel together, and until this
 * module they did not. `patch` is the renderer's material; `cssTierMapping` is
 * what that same material costs to express as one `backdrop-filter` plus an
 * `rgba()` overlay; and the **receded** difference is what the same measurement
 * says the material becomes when the window loses focus. `createGlassRoot` took
 * the first two as two unrelated options and imported the third as a constant,
 * so the natural reading — "a document is a value `materialProfile` accepts" —
 * silently gave a page the macOS 27 material on the GPU tier, a CSS tier still
 * blurring at the macOS 26.5 scale, and a macOS 26.5 recede. All three are one
 * seam, and this is it.
 *
 * A document is therefore four patches and one mapping: the active material per
 * colour scheme, the receded difference per colour scheme, and the crossing to
 * the CSS tier. The root resolves a scheme and a pose and reads the right leaf;
 * the two older options still merge over whatever the document selected, for an
 * app tuning one tier by hand.
 *
 * ## What ships, and what draws
 *
 * Two documents ship. `macos27MaterialProfileDocument` is the default — every
 * Mac that took the macOS 27 update draws that material and a web page has no
 * operating system to follow, so matching the platform's current material is
 * what "no option passed" should mean. `macos26MaterialProfileDocument` is the
 * previous reference, kept shipped and selectable by name so that a page pinned
 * to the material it was designed against can stay there.
 *
 * Neither is the renderer's `DEFAULT_MATERIAL_PROFILE`, which W29 Decision Log
 * 1 (i) holds still at the macOS 26.5 light material: every document here is a
 * patch over it, and "macOS 27 by default" is a selection between patches. That
 * is what keeps the frozen macOS 26.5 documents' `resolvedMaterialSha256` pins
 * green while the material a page draws moves.
 */

import type { ResolvedColorScheme } from "./color-scheme";
import { darkMaterialProfile } from "./dark-profile";
import {
  macos27CssTierMapping,
  macos27DarkMaterialProfile,
  macos27LightMaterialProfile,
  macos27RecededMaterialProfile,
  MACOS_27_RESOLVED_MATERIAL_SHA256,
} from "./macos27-profile";
import type { CssTierMapping } from "./optics";
import { recededMaterialProfile } from "./receded-profile";
import type { RendererMaterialProfile } from "./renderer-bridge";

/**
 * One measured endpoint of a document: one colour scheme, one window pose.
 *
 * `profileKey` and `resolvedMaterialSha256` are the endpoint's provenance, and
 * both are optional because one shipped endpoint has neither. The macOS 26.5
 * receded difference predates the receded profile document — it was fitted in
 * W27c and refit in W28 G1 straight into `receded-profile.ts` — so there is no
 * document key to name and no digest to quote. Saying so is the honest answer;
 * inventing a key for a document that is not on disk is not.
 */
export interface GlassMaterialEndpoint {
  /** The calibration profile document this patch is generated from, where there is one. */
  readonly profileKey?: string;
  /**
   * The patch itself, `undefined` where the endpoint IS the renderer's defaults.
   * That is what the macOS 26.5 light active endpoint is: the light 26.5 document
   * is the identity with the runtime default, so "light 26.5" is the absence of a
   * patch rather than a second name for an empty one.
   */
  readonly patch?: RendererMaterialProfile;
  /** The document's digest over the material it resolves to, not over the patch. */
  readonly resolvedMaterialSha256?: string;
}

/** A whole measured material: both schemes, both poses, and the CSS crossing. */
export interface GlassMaterialProfileDocument {
  /** What a readout calls this material. The profile-key stem it was measured under. */
  readonly name: string;
  /** Which macOS release the material was measured on, for a readout to state. */
  readonly platform: string;
  readonly active: Readonly<Record<ResolvedColorScheme, GlassMaterialEndpoint>>;
  /** Applied OVER the active endpoint of the same scheme, never instead of it. */
  readonly receded: Readonly<Record<ResolvedColorScheme, GlassMaterialEndpoint>>;
  readonly cssTierMapping: Partial<CssTierMapping>;
}

/**
 * The macOS 27 material, measured at the appearance slider's shipped position
 * (`NSGlassTintAmount` 0.5) — W29, claims §5.150 through §5.154.
 *
 * The default. Its four patches are generated from the four calibration
 * documents by `scripts/generate-macos27-profile.mjs` and pinned to them by
 * `packages/calibration/test/macos27-profile-export.test.ts`.
 */
export const macos27MaterialProfileDocument: GlassMaterialProfileDocument = {
  name: "apple-macos-27.0-glass0.5",
  platform: "macOS 27.0",
  active: {
    light: {
      profileKey: "apple-macos-27.0-1x-light-standard-glass0.5",
      patch: macos27LightMaterialProfile,
      resolvedMaterialSha256: MACOS_27_RESOLVED_MATERIAL_SHA256.light,
    },
    dark: {
      profileKey: "apple-macos-27.0-1x-dark-standard-glass0.5",
      patch: macos27DarkMaterialProfile,
      resolvedMaterialSha256: MACOS_27_RESOLVED_MATERIAL_SHA256.dark,
    },
  },
  receded: {
    light: {
      profileKey: "apple-macos-27.0-1x-light-standard-glass0.5-receded",
      patch: macos27RecededMaterialProfile.light,
      resolvedMaterialSha256: MACOS_27_RESOLVED_MATERIAL_SHA256.recededLight,
    },
    dark: {
      profileKey: "apple-macos-27.0-1x-dark-standard-glass0.5-receded",
      patch: macos27RecededMaterialProfile.dark,
      resolvedMaterialSha256: MACOS_27_RESOLVED_MATERIAL_SHA256.recededDark,
    },
  },
  cssTierMapping: macos27CssTierMapping,
};

/**
 * The macOS 26.5 material — every measurement this project made before W29, and
 * what the package drew by default through 0.18.0.
 *
 * Shipped and selectable rather than retired: a page designed and reviewed
 * against this material can pin it with one option, and the calibration harness
 * reads the frozen macOS 26.5 bed through the same seam an application uses.
 *
 * Its `cssTierMapping` is empty, and that is a statement rather than a gap: the
 * two keys the macOS 26.5 light document records are `CSS_TIER_MAPPING`'s own
 * shipped values, so this material's crossing IS the module default and naming
 * it again would create a second place for one number to live.
 */
export const macos26MaterialProfileDocument: GlassMaterialProfileDocument = {
  name: "apple-macos-26.5",
  platform: "macOS 26.5",
  /*
   * **The two digests below are the CURRENT ones, not the documents' own** (W30
   * G2; W30 Decision Log 1 (a), claims §5.158).
   *
   * `root.material` names what actually drew, so the digest this endpoint
   * reports has to be the fingerprint of the material the renderer is handed
   * today. W30's operator wave added eight leaves to
   * `DEFAULT_MATERIAL_PROFILE` at values that are algebraic identities, which
   * moved every document's resolved digest while moving no pixel — the one-time
   * X1 exemption W29 Decision Log 7 (a) granted.
   *
   * The two frozen macOS 26.5 documents stay BYTE-IDENTICAL through that, so
   * their own `resolvedMaterialSha256` still reads `b2b570e4adcea8fb` and
   * `874be66ea501621b` — the readings they were sealed at, and still the
   * readings. What the pin resolves to now is recorded beside them, once, in
   * `packages/calibration/profiles/digest-supersessions.json`, and
   * `macos26-document-selection.test.ts` asserts both halves: the document's
   * field equals the record's `recordedSha256`, and the material a root selects
   * fingerprints to the record's `currentSha256`, which is what these two
   * literals are. A page pinned to macOS 26.5 draws exactly what 0.18.0 drew;
   * only the name of that material's digest gained one indirection.
   */
  active: {
    light: {
      profileKey: "apple-macos-26.5-1x-light-standard",
      resolvedMaterialSha256: "b340a4dee871633c",
    },
    dark: {
      profileKey: "apple-macos-26.5-1x-dark-standard",
      patch: darkMaterialProfile,
      resolvedMaterialSha256: "93ab090705c43f1f",
    },
  },
  receded: {
    light: { patch: recededMaterialProfile.light },
    dark: { patch: recededMaterialProfile.dark },
  },
  cssTierMapping: {},
};

/**
 * What a root resolves when an app asks for no document.
 *
 * Moved from the macOS 26.5 material to the macOS 27 material in 0.19.0, on the
 * user's ruling (W29 Decision Log 2), after the macOS 27 bed was captured, the
 * change to Apple's material measured cell by cell, and vitrea refit to it.
 */
export const DEFAULT_MATERIAL_PROFILE_DOCUMENT: GlassMaterialProfileDocument =
  macos27MaterialProfileDocument;

/** Both shipped documents, for a readout or a picker that wants to name them. */
export const SHIPPED_MATERIAL_PROFILE_DOCUMENTS: readonly GlassMaterialProfileDocument[] = [
  macos27MaterialProfileDocument,
  macos26MaterialProfileDocument,
];

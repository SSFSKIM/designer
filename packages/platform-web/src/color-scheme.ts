/**
 * Which colour scheme's material a root draws, and how that choice becomes a
 * material profile (W21 G3; the wave spec's "What ships" and Decision Log 1).
 *
 * The material is measured per colour scheme. Only one scheme's numbers can be
 * the renderer's defaults, and those are the light-standard profile's — so the
 * dark scheme ships as a patch (`darkMaterialProfile`) and this module is the
 * one place that decides when it applies.
 *
 * Three settings, and the default is `"light"`: an existing host's material must
 * not move because it upgraded. `"dark"` is a host that has resolved its own
 * scheme somewhere vitrea cannot see, and `"auto"` follows the operating
 * system's own answer through `prefers-color-scheme`, on the same
 * `MediaMatcher` seam the accessibility feed and the device-ratio feed already
 * take (`media-policy.ts`) — one browser fact, delivered as plain data, and the
 * root re-derives both tiers from it exactly as it does on a device-ratio change.
 *
 * **The scheme is not a backdrop hint.** A hint (`GlassHostOptions.hint`) states
 * the tone of what is BEHIND the surface, which is what the adaptation reads;
 * the scheme states which material the surface is made of. A dark page can hand
 * a light-tone hint to a surface sitting over a white card, and both are true at
 * once.
 */

import { darkMaterialProfile } from "./dark-profile";
import type { MediaMatcher, MediaQueryHandle } from "./media-policy";
import type { RendererMaterialProfile } from "./renderer-bridge";

/** What an app asks for. `"auto"` is the media query; the other two are answers. */
export type GlassColorScheme = "light" | "dark" | "auto";

/** What `"auto"` resolves to — the scheme the material is actually drawn for. */
export type ResolvedColorScheme = "light" | "dark";

/** The query `"auto"` rides. `planes.ts` already declares `color-scheme: light dark`. */
export const COLOR_SCHEME_MEDIA_QUERY = "(prefers-color-scheme: dark)";

/**
 * The base patch a resolved scheme selects.
 *
 * `undefined` for light rather than an empty object, because that is what light
 * *is*: the light profile document is the identity with the renderer's defaults
 * (`identityWithRuntimeDefault`, pinned by calibration's `tuned-profiles.test.ts`),
 * so there is no light patch to ship and an empty one would be a second name for
 * "no patch". Everything downstream already takes `RendererMaterialProfile |
 * undefined`.
 */
export function colorSchemeMaterialProfile(
  scheme: ResolvedColorScheme,
): RendererMaterialProfile | undefined {
  return scheme === "dark" ? darkMaterialProfile : undefined;
}

type PatchRecord = Readonly<Record<string, unknown>>;

const isRecord = (value: unknown): value is PatchRecord =>
  value !== null && typeof value === "object" && !Array.isArray(value);

/**
 * Compose two profile patches: `over` wins, leaf by leaf.
 *
 * A scheme's patch and an app's own patch are both *differences* from the
 * renderer's defaults, so composing them is not `{ ...base, ...over }`: a patch
 * naming `optics.regular.tintAlpha` must not drop the scheme's
 * `optics.regular.tint` beside it, which is the same per-field merge
 * `withMaterialOverrides` performs one level down when the resolved patch finally
 * meets the defaults. Arrays are leaves for the reason the patch type states —
 * a colour is one leaf, not three, and two channels of a fitted colour and one
 * of another is a colour nobody measured.
 *
 * The cast at the end is the one place this module leaves the type system: the
 * merge is structural and recursive, and `RendererMaterialProfile` is derived
 * across the renderer's dynamic-import seam, so there is no way to write the
 * recursion in its terms. Both inputs are that type, every leaf comes from one
 * of them, and no key is invented.
 */
export function mergeMaterialProfiles(
  base: RendererMaterialProfile | undefined,
  over: RendererMaterialProfile | undefined,
): RendererMaterialProfile | undefined {
  if (base === undefined) return over;
  if (over === undefined) return base;

  const merge = (left: PatchRecord, right: PatchRecord): PatchRecord => {
    const result: Record<string, unknown> = { ...left };
    for (const [key, value] of Object.entries(right)) {
      const held = result[key];
      result[key] = isRecord(held) && isRecord(value) ? merge(held, value) : value;
    }
    return result;
  };

  return merge(base as PatchRecord, over as PatchRecord) as RendererMaterialProfile;
}

export interface ColorSchemeFeedOptions {
  readonly matcher: MediaMatcher;
  readonly onChange: (prefersDark: boolean) => void;
}

export interface ColorSchemeFeed {
  /** What `prefers-color-scheme: dark` says right now. */
  readonly prefersDark: boolean;
  stop(): void;
}

/**
 * The operating system's own answer, as a feed.
 *
 * Shaped like `observeAccessibilityPreferences` and taking the same injectable
 * matcher, because it is the same kind of thing. It is armed on every root, not
 * only on an `"auto"` one: one `matchMedia` call is cheaper than the branch, and
 * a root whose scheme is switched to `"auto"` after construction then already
 * knows the answer rather than having to arm a query and wait for the next flip.
 *
 * An engine that cannot parse the query reports `matches: false` and gets the
 * light scheme, which is this option's default anyway — there is no preference
 * to lose here, unlike `prefers-reduced-transparency`, so support detection is
 * not part of this contract.
 */
export function observeColorScheme(options: ColorSchemeFeedOptions): ColorSchemeFeed {
  const handle: MediaQueryHandle = options.matcher(COLOR_SCHEME_MEDIA_QUERY);
  let prefersDark = handle.matches;

  const listener = (): void => {
    if (handle.matches === prefersDark) return;
    prefersDark = handle.matches;
    options.onChange(prefersDark);
  };

  handle.addEventListener("change", listener);

  return {
    get prefersDark() {
      return prefersDark;
    },
    stop() {
      handle.removeEventListener("change", listener);
    },
  };
}

/** The setting and the system's answer, folded into the scheme actually drawn. */
export function resolveColorScheme(
  setting: GlassColorScheme,
  prefersDark: boolean,
): ResolvedColorScheme {
  if (setting === "auto") return prefersDark ? "dark" : "light";
  return setting;
}

/**
 * Accessibility policy (§Accessibility policy, plus the Reduced Motion
 * paragraph of §Motion).
 *
 * The spec puts this in `core` as *policy*: what an accessibility preference
 * means for the material and for motion. `platform-web` reads the media queries
 * and hands the answers in as plain booleans (X4 — core never touches a media
 * query, a `window`, or anything else browser-shaped), and `@vitrea/react`'s
 * `GlassRoot` supplies the per-root prop overrides. The decision itself is one
 * pure fold, so the same inputs always yield the same policy and a test can
 * enumerate every input there is.
 *
 * §Accessibility states four consequences in prose. They are encoded here as a
 * **table**, one row per preference, each row a partial override of the nominal
 * policy — so the table can be diffed against the spec paragraph line by line
 * instead of being reverse-engineered out of branching code. The resolver folds
 * the active rows over `NOMINAL_ACCESSIBILITY_POLICY` in a fixed precedence
 * order; adding a preference means adding a row, not editing a resolver.
 *
 * Every consequence is a small closed union rather than a number. The numbers —
 * blur radii, tint strengths, spring constants, morph durations — are
 * calibration-delegated unknowns owned by `@vitrea/geometry` and
 * `@vitrea/motion` (§Calibration harness). Core's job is to say *which regime*
 * applies; it would be inventing fidelity it has not measured if it said by how
 * much.
 */

import type { Diagnostic, DiagnosticsChannel } from "./diagnostics";

/**
 * What the platform detected. `platform-web` fills this from media queries;
 * core never reads one (X4).
 */
export interface SystemAccessibilityPreferences {
  readonly reducedTransparency: boolean;
  readonly reducedMotion: boolean;
  readonly increasedContrast: boolean;
  readonly forcedColors: boolean;
  /**
   * Whether `prefers-reduced-transparency` is even queryable here. It is not
   * Baseline, which is exactly why the explicit override is load-bearing rather
   * than a courtesy (§Accessibility policy). Where this is `false`,
   * `reducedTransparency` above is an absence of evidence, not evidence of
   * absence — and the resolver says so through the diagnostics channel.
   */
  readonly reducedTransparencySupported: boolean;
}

/** The preferences the policy reasons about, and the table's row keys. */
export const ACCESSIBILITY_FLAGS = [
  "reducedTransparency",
  "reducedMotion",
  "increasedContrast",
  "forcedColors",
] as const;

export type AccessibilityFlag = (typeof ACCESSIBILITY_FLAGS)[number];

/**
 * The three preferences a `GlassRoot` may overrule (§Accessibility policy names
 * exactly this prop set). `forcedColors` is absent by design: a forced-colors
 * mandate comes from an operating-system accessibility setting that exists to
 * override author styling, so it is not an app's to switch off. The type — not
 * a runtime guard — is what makes that impossible to express.
 */
export type OverridableAccessibilityFlag = Exclude<AccessibilityFlag, "forcedColors">;

export const OVERRIDABLE_ACCESSIBILITY_FLAGS = [
  "reducedTransparency",
  "reducedMotion",
  "increasedContrast",
] as const satisfies readonly OverridableAccessibilityFlag[];

/** `"system"` defers to the platform; a boolean states the answer outright. */
export type AccessibilityOverride = "system" | boolean;

/** Per-`GlassRoot` overrides. An absent key means `"system"`. */
export type AccessibilityOverrides = {
  readonly [K in OverridableAccessibilityFlag]?: AccessibilityOverride;
};

/**
 * How the material is allowed to behave.
 *
 * The axes are named for what §Accessibility talks about, and each carries the
 * nominal regime, the regime its preference asks for, and — where forced-colors
 * removes the glass entirely — the degenerate regime that leaves.
 *
 * `refraction` here is an *accessibility* ceiling, not the capability-derived
 * `RefractionQuality` of X2 (state.ts). A group can be capped by either; the
 * renderer honours whichever is lower.
 */
export interface ResolvedMaterialPolicy {
  /** Whether a glass body is drawn at all, or a flat system-coloured surface replaces it. */
  readonly glass: "material" | "none";
  /** Where colour comes from: the adaptive material, or the platform's forced palette. */
  readonly colorSource: "material" | "system";
  /** Backdrop diffusion. Reduced transparency asks for *more* frosted, so `increased`. */
  readonly frost: "nominal" | "increased" | "none";
  /** Edge lensing. Reduced transparency asks for *less* refraction — reduced, not removed. */
  readonly refraction: "nominal" | "reduced" | "none";
  /**
   * How much of the backdrop the surface hides. Reduced transparency raises it;
   * forced-colors' flat system fill hides the backdrop completely, which is
   * `opaque` rather than `none` — no glass means maximal occlusion, not minimal.
   */
  readonly occlusion: "nominal" | "increased" | "opaque";
  /**
   * Nominal glass is bounded by a rim highlight; `strong` is a drawn border.
   * Increased contrast asks for stronger borders, and forced-colors needs a
   * border because a flattened palette leaves nothing else to define the shape.
   */
  readonly border: "nominal" | "strong";
  /** The material's colour cast picked up from the backdrop. */
  readonly ambientTint: "nominal" | "reduced" | "none";
  /**
   * `adaptive` is the sampled/hinted light-dark foreground of §Foreground
   * adaptation. `near-monochrome` is a flat high-contrast foreground — which is
   * also what forced-colors gets, since adapting to a glass body that no longer
   * exists is not available there; `colorSource` records that the flat colour
   * comes from the system palette.
   */
  readonly foreground: "adaptive" | "near-monochrome";
}

/**
 * How motion is allowed to behave (§Motion, Reduced Motion).
 *
 * Reduced Motion "shortens morphs to non-elastic interpolation": the shortening
 * is a property of the driver kind, so `morph: "non-elastic"` carries both
 * halves and `@vitrea/motion` owns the calibrated duration for each kind.
 */
export interface ResolvedMotionPolicy {
  /** Spring overshoot past the target. */
  readonly overshoot: "elastic" | "none";
  /** Press compression and lensing deformation of the surface. */
  readonly deformation: "nominal" | "none";
  /** Travelling specular shimmer across the rim. */
  readonly shimmer: "travel" | "none";
  /** Morph driver family: an elastic spring, or plain shortened interpolation. */
  readonly morph: "elastic" | "non-elastic";
  /**
   * Crossfading one *surface transition* into another. Nominal glass never
   * does it — a morph is one continuous material transition, not two surfaces
   * dissolving. Reduced Motion reserves it for large plane shifts. (The
   * foreground light/dark crossfade of §Motion's driver table is a different,
   * unconditional channel and is not governed here.)
   */
  readonly crossfade: "never" | "large-plane-shifts";
  /**
   * Reduced Motion "keeps direct-manipulation positional continuity": a surface
   * being dragged still tracks the pointer. That holds under every preference,
   * so it is an invariant of the model, typed as the literal `true` — there is
   * no combination of inputs that can turn it off.
   */
  readonly positionalContinuity: true;
}

/**
 * What renderers consume. The four resolved booleans travel with the
 * consequences so a consumer (or `useGlassCapabilities()`) can see *what* was
 * decided and *why*, in the same spirit as X2's `configuredSource` surviving a
 * demotion.
 */
export interface ResolvedAccessibilityPolicy {
  readonly reducedTransparency: boolean;
  readonly reducedMotion: boolean;
  readonly increasedContrast: boolean;
  readonly forcedColors: boolean;
  readonly material: ResolvedMaterialPolicy;
  readonly motion: ResolvedMotionPolicy;
}

/**
 * One table row: the axes a preference changes, and nothing else.
 *
 * `positionalContinuity` is excluded from the motion partial so no row can
 * reach the invariant, whatever a future editor intends.
 */
export interface AccessibilityConsequences {
  readonly material?: Partial<ResolvedMaterialPolicy>;
  readonly motion?: Partial<Omit<ResolvedMotionPolicy, "positionalContinuity">>;
}

/** Full-fidelity glass: no preference detected, nothing capped. */
export const NOMINAL_ACCESSIBILITY_POLICY: ResolvedAccessibilityPolicy = {
  reducedTransparency: false,
  reducedMotion: false,
  increasedContrast: false,
  forcedColors: false,
  material: {
    glass: "material",
    colorSource: "material",
    frost: "nominal",
    refraction: "nominal",
    occlusion: "nominal",
    border: "nominal",
    ambientTint: "nominal",
    foreground: "adaptive",
  },
  motion: {
    overshoot: "elastic",
    deformation: "nominal",
    shimmer: "travel",
    morph: "elastic",
    crossfade: "never",
    positionalContinuity: true,
  },
};

/**
 * §Accessibility, encoded. Each row is that paragraph's sentence for one
 * preference and carries only the axes the sentence names:
 *
 * - "Reduced transparency → more frosted, less refraction, higher occlusion."
 * - "Increased contrast → stronger borders, near-monochrome foregrounds,
 *   reduced ambient tint."
 * - "`forced-colors` → system colors, borders, no glass."
 * - "Reduced Motion removes elastic overshoot, deformation, and shimmer travel;
 *   keeps direct-manipulation positional continuity; shortens morphs to
 *   non-elastic interpolation; reserves crossfade for large plane shifts."
 *   (§Motion)
 *
 * Reduced Motion is the only motion row, and the other three are the only
 * material rows — the spec draws no line between a colour preference and a
 * motion one, so neither does the table.
 */
export const ACCESSIBILITY_BEHAVIOR_TABLE: {
  readonly [K in AccessibilityFlag]: AccessibilityConsequences;
} = {
  reducedTransparency: {
    material: { frost: "increased", refraction: "reduced", occlusion: "increased" },
  },
  increasedContrast: {
    material: { border: "strong", foreground: "near-monochrome", ambientTint: "reduced" },
  },
  reducedMotion: {
    motion: {
      overshoot: "none",
      deformation: "none",
      shimmer: "none",
      morph: "non-elastic",
      crossfade: "large-plane-shifts",
    },
  },
  forcedColors: {
    // "system colors, borders, no glass" — and with the glass gone, every
    // optical axis follows it: nothing to frost, lens, or tint, and a flat
    // system fill that hides the backdrop entirely.
    material: {
      glass: "none",
      colorSource: "system",
      frost: "none",
      refraction: "none",
      occlusion: "opaque",
      border: "strong",
      ambientTint: "none",
      foreground: "near-monochrome",
    },
  },
};

/**
 * Fold order, weakest first.
 *
 * `reducedMotion` touches only motion axes, and `reducedTransparency` and
 * `increasedContrast` touch disjoint material axes — those three commute, so
 * two preferences at once compose instead of one silently erasing the other.
 * `forcedColors` is the one row that spans every material axis, and it is last
 * because a platform-level colour mandate outranks every softening an app or a
 * softer preference asked for.
 */
export const ACCESSIBILITY_PRECEDENCE = [
  "reducedMotion",
  "reducedTransparency",
  "increasedContrast",
  "forcedColors",
] as const satisfies readonly AccessibilityFlag[];

/** An explicit boolean answers for the platform; `"system"` and absence defer to it. */
const resolveFlag = (detected: boolean, override: AccessibilityOverride | undefined): boolean =>
  override === undefined || override === "system" ? detected : override;

/**
 * No `subjects`: this is a root-level policy finding, not a finding about a
 * group, node, or source id. An empty subject list also makes the channel's
 * dedupe key the code alone, so one misconfigured root reports once.
 */
const REDUCED_TRANSPARENCY_UNDETECTABLE: Diagnostic = {
  code: "reduced-transparency-undetectable",
  severity: "warning",
  subjects: [],
  message:
    'This platform cannot query `prefers-reduced-transparency`, so leaving `reducedTransparency` on "system" silently resolves it to false and the preference is lost. Set the GlassRoot `reducedTransparency` prop to an explicit boolean (§Accessibility policy).',
};

/**
 * Resolve one `GlassRoot`'s accessibility policy.
 *
 * Purely functional: no state, no I/O, no clock. `diagnostics` is a side
 * channel — passing one never changes the policy that comes back.
 */
export function resolveAccessibilityPolicy(
  system: SystemAccessibilityPreferences,
  overrides: AccessibilityOverrides = {},
  diagnostics?: DiagnosticsChannel,
): ResolvedAccessibilityPolicy {
  const active = {
    reducedTransparency: resolveFlag(system.reducedTransparency, overrides.reducedTransparency),
    reducedMotion: resolveFlag(system.reducedMotion, overrides.reducedMotion),
    increasedContrast: resolveFlag(system.increasedContrast, overrides.increasedContrast),
    // Deliberately not overridable — see OverridableAccessibilityFlag.
    forcedColors: system.forcedColors,
  } satisfies Record<AccessibilityFlag, boolean>;

  // The finding is about the *configuration*, not the resolved value: on a
  // platform that cannot answer the query, "system" always resolves to false,
  // so the app has no way to honour the preference until it states one. An app
  // that supplied an explicit boolean has already done that.
  const leftToTheSystem =
    overrides.reducedTransparency === undefined || overrides.reducedTransparency === "system";
  if (leftToTheSystem && !system.reducedTransparencySupported) {
    diagnostics?.report(REDUCED_TRANSPARENCY_UNDETECTABLE);
  }

  let material: ResolvedMaterialPolicy = NOMINAL_ACCESSIBILITY_POLICY.material;
  let motion: ResolvedMotionPolicy = NOMINAL_ACCESSIBILITY_POLICY.motion;

  for (const flag of ACCESSIBILITY_PRECEDENCE) {
    if (!active[flag]) continue;
    const row = ACCESSIBILITY_BEHAVIOR_TABLE[flag];
    if (row.material !== undefined) material = { ...material, ...row.material };
    if (row.motion !== undefined) motion = { ...motion, ...row.motion };
  }

  return { ...active, material, motion };
}

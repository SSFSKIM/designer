/**
 * The probe-only backdrop axes — the sampling ROUTE a capture was asked for, and
 * the author backdrop level it was asked to state — as one vocabulary.
 *
 * The canonical bed has exactly one setting of each: every raster-backed group
 * samples the registered raster as a texture — the stack overlay is `dom` there
 * because it must sample rendered glass — and no capture authors a backdrop hint.
 * W27f's page-content probe varies both, and neither variation is legible in a
 * PNG: a DOM-sourced group draws the same geometry a texture-sourced one does,
 * and a hint replaces the sampled tone with one scalar, which can move the body
 * anywhere from imperceptibly to a whole scheme away. Until these travelled in
 * the report and in the cell's `capturePath`, the only thing separating them was
 * the directory a run happened to write to — which is not evidence, because the
 * matrix's key does not contain it.
 *
 * So the axes are parsed here, reported by the page, and appended to the cell's
 * `capturePath` from what the page REPORTED rather than from what the driver's
 * environment asked for. The canonical request — texture, no authored level —
 * appends nothing, so the shipped bed's keys are unchanged to the byte.
 */

/** How a group was asked to reach its backdrop. */
export type BackdropMode = "texture" | "dom";

/** What the canonical bed asks for, and what an absent request means. */
export const DEFAULT_BACKDROP_MODE: BackdropMode = "texture";

/** The capture driver's environment channel for the route axis. */
export const BACKDROP_MODE_ENV = "VITREA_BACKDROP_MODE";

/** The capture driver's environment channel for the per-scene authored levels. */
export const BACKDROP_LEVELS_ENV = "VITREA_BACKDROP_LEVELS";

/** Is either probe axis being requested through the environment? */
export function backdropProbeRequested(
  env: Readonly<Record<string, string | undefined>>,
): boolean {
  return env[BACKDROP_MODE_ENV] !== undefined || env[BACKDROP_LEVELS_ENV] !== undefined;
}

/** One output a run would write, and the canonical path it may not be. */
export interface ProbeOutputTarget {
  /** How the refusal names this output to whoever has to redirect it. */
  readonly what: string;
  /** Where the run would write, resolved; `undefined` where it was not redirected. */
  readonly path: string | undefined;
  readonly canonical: string;
  /**
   * Whether the canonical path is a TREE rather than a file.
   *
   * A capture directory is a tree: the profile directories under it are where a
   * run's PNGs actually land, so `--out web-captures/apple-macos-26.5-1x-…` is
   * writing the canonical bed as surely as `--out web-captures` is, and equality
   * alone would wave it through. Containment is by path segment, so a sibling
   * that merely starts with the same characters — `web-captures-scratch` — stays
   * a legitimate scratch destination. A matrix is a file and stays exact.
   */
  readonly tree?: boolean;
}

/**
 * Is this path the canonical one, or — for a tree — somewhere inside it?
 *
 * Both separators are tested rather than `node:path`'s: the scene page imports
 * this module for the two parsers, and a `node:` import would follow it into the
 * browser bundle. Callers pass already-resolved paths, so this is a segment
 * comparison and not a path implementation.
 */
function withinCanonical(target: ProbeOutputTarget, path: string): boolean {
  if (path === target.canonical) return true;
  if (target.tree !== true) return false;
  return ["/", "\\"].some((separator) => path.startsWith(`${target.canonical}${separator}`));
}

/**
 * Why a probe run may not write these outputs, or `undefined` where it may.
 *
 * The canonical capture directory and the canonical matrix are the shipped bed:
 * the sheets, the demo fixture and the next canonical run all read them, and
 * their rows carry no probe axis, so a probe landing in either is indistinguish-
 * able from evidence. Named paths rather than a policy, and checked at every door
 * that can write them — `cli/compare.ts` and `scripts/capture-web.ts` are two
 * commands, and the second is the one a probe reaches for when it wants a single
 * scene. This is a rejection of known destinations, not a containment sandbox: a
 * run that deliberately points somewhere else is a run that meant to.
 */
export function probeCanonicalOutputRefusal(
  requested: boolean,
  targets: readonly ProbeOutputTarget[],
): string | undefined {
  if (!requested) return undefined;
  const refused = targets.filter(
    (target) => target.path === undefined || withinCanonical(target, target.path),
  );
  if (refused.length === 0) return undefined;
  return (
    `${BACKDROP_MODE_ENV}/${BACKDROP_LEVELS_ENV} are probe-only axes and this run would write ` +
    `${refused
      .map((target) =>
        target.path === undefined
          ? `no scratch ${target.what}`
          : target.path === target.canonical
            ? `the canonical ${target.what} (${target.canonical})`
            : `inside the canonical ${target.what} (${target.path})`,
      )
      .join(", ")}. Point each one at a scratch path.`
  );
}

/** The route axis, refusing an unknown word rather than falling back to the default. */
export function parseBackdropMode(raw: string | null | undefined): BackdropMode {
  if (raw === null || raw === undefined || raw === "") return DEFAULT_BACKDROP_MODE;
  if (raw !== "texture" && raw !== "dom") {
    throw new Error(`backdrop mode takes texture or dom, not '${raw}'`);
  }
  return raw;
}

/**
 * The authored backdrop level, or `null` where the capture authors none.
 *
 * A hint overrides sampling on both tiers, so a hint that is not a measured
 * fraction of the real backdrop is a fabricated material input; the range is
 * checked here rather than trusted from a command line.
 */
export function parseBackdropLevel(raw: string | null | undefined): number | null {
  if (raw === null || raw === undefined || raw === "") return null;
  const level = Number(raw);
  if (!Number.isFinite(level) || level < 0 || level > 1) {
    throw new Error(`backdrop level must be a measured fraction in 0..1, not '${raw}'`);
  }
  return level;
}

/**
 * What the cell's `capturePath` says about these axes.
 *
 * Empty for the canonical request, which is what keeps every shipped cell's key
 * byte-identical; a probe cell names both axes so it can never be read as the
 * canonical capture of the same scene.
 */
export function backdropProbeLabel(mode: BackdropMode, level: number | null): string {
  if (mode === DEFAULT_BACKDROP_MODE && level === null) return "";
  return `, backdrop=${mode}, authoredBackdropLevel=${level === null ? "none" : level}`;
}

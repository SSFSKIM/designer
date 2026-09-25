/**
 * G0 cannot publish canonical generations. Refuse their write targets before a
 * capture or measurement, including paths reached through existing symlinks.
 */
import { existsSync, realpathSync } from "node:fs";
import { dirname, extname, isAbsolute, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const PACKAGE_ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..");
const FROZEN_MATRIX = resolve(PACKAGE_ROOT, "results/matrix.json");
const GENERATIONS_DIR = resolve(PACKAGE_ROOT, "results/generations");
const SUPERSEDED_DIR = resolve(PACKAGE_ROOT, "results/superseded");

/** Canonicalize the longest existing prefix, including symlinked parent directories. */
function destinationPath(path: string): string {
  const absolute = resolve(path);
  if (existsSync(absolute)) return realpathSync(absolute);
  const parent = dirname(absolute);
  if (parent === absolute) return absolute;
  return resolve(destinationPath(parent), relative(parent, absolute));
}

function insideJsonDirectory(directory: string, path: string): boolean {
  const within = relative(directory, path);
  return within !== "" && within !== ".." && !within.startsWith(`..${sep}`)
    && !isAbsolute(within) && extname(path) === ".json";
}

function isCanonicalJson(path: string): boolean {
  return path === FROZEN_MATRIX || insideJsonDirectory(GENERATIONS_DIR, path)
    || insideJsonDirectory(SUPERSEDED_DIR, path);
}

/** Throw before any write to the frozen matrix or immutable recorded generation JSON. */
export function assertScratchDestination(path: string): void {
  const absolute = resolve(path);
  if (isCanonicalJson(absolute) || isCanonicalJson(destinationPath(absolute))) {
    throw new Error(
      `${absolute} is canonical, immutable matrix evidence; G1's publisher must publish ` +
      "complete generations. G0 accepts only a separate scratch JSON destination.",
    );
  }
}

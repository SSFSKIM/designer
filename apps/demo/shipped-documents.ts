/**
 * The material profile documents that are on disk right now, hashed at build time.
 *
 * `packages/calibration/results/matrix.json` keys every cell by the `capturePath` its
 * capture was written to, and that path names each material profile document the run
 * was driven from together with twelve hex characters of SHA-256 over the document's
 * bytes. A refit moves those bytes, so the next canonical run appends a generation of
 * rows beside the old ones rather than overwriting them — which is the project's rule
 * about recorded numbers, and the reason the matrix can hold two readings of one cell.
 *
 * `calibration.ts` therefore has to know which generation is the shipped one, and the
 * honest answer is the documents' own bytes. This plugin derives them the way
 * `packages/calibration/test/adopted-thresholds.test.ts` derives `SHIPPED_DOCUMENT_HASHES`
 * — read the directory, hash each file, take twelve hex characters — so the page and
 * the gate cannot disagree about which reading counts. Derived rather than transcribed
 * for the reason every hash in that file is derived: a hash a person retypes after a
 * refit is a hash that goes stale silently.
 *
 * It is a build-time module because the hash is over the file's BYTES: importing the
 * documents as JSON and hashing the parse would hash a re-printing of them, and a
 * browser has no synchronous digest to do it with. The plugin is wired into both
 * `vite.config.ts` (dev server, build, the Playwright suite's server) and
 * `vitest.config.ts` (the unit suite), because a module the unit suite resolved
 * differently from the page would be a fixture rather than a reading. Vite evaluates
 * it once per process, so an edit to a profile document lands at the next restart.
 */

import { createHash } from "node:crypto";
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

import type { Plugin } from "vite";

const MODULE_ID = "virtual:vitrea-shipped-documents";

/** Vite's convention: a resolved virtual module id is prefixed with a NUL byte. */
const RESOLVED_ID = `\0${MODULE_ID}`;

const PROFILES = fileURLToPath(new URL("../../packages/calibration/profiles/", import.meta.url));

/** `packages/calibration/profiles/<file>` → twelve hex characters of SHA-256. */
export function shippedDocumentHashes(): Record<string, string> {
  const out: Record<string, string> = {};
  for (const file of readdirSync(PROFILES).filter((name) => name.endsWith(".json")).sort()) {
    out[`packages/calibration/profiles/${file}`] = createHash("sha256")
      .update(readFileSync(join(PROFILES, file)))
      .digest("hex")
      .slice(0, 12);
  }
  return out;
}

export function shippedDocuments(): Plugin {
  return {
    name: "vitrea-shipped-documents",
    resolveId(id) {
      return id === MODULE_ID ? RESOLVED_ID : null;
    },
    load(id) {
      if (id !== RESOLVED_ID) return null;
      return `export const SHIPPED_DOCUMENT_HASHES = ${JSON.stringify(
        shippedDocumentHashes(),
        null,
        2,
      )};\n`;
    },
  };
}

/**
 * X41's manifest: the macOS 27 `-glass0.5` generation is frozen for the whole of W43
 * (charter `2026-10-01-w43-glass-0-25-generation.md`, G0 (a), X41, acceptance clause 11).
 *
 *   cd packages/calibration && npx tsx results/2026-10-01-w43-g0-declaration/x41/x41.ts verify
 *
 * `write` records the manifest (`sha256.txt`) and the document projection beside it;
 * `verify` re-derives both and exits non-zero on any difference, naming it. Run it at every
 * W43 merge, beside `results/2026-09-16-w29-freeze/freeze.py verify`.
 *
 * ## Two kinds of protection
 *
 * **Bytes.** Every file of the seven `apple-macos-27.0-*-glass0.5` fixture trees (the four
 * standard keys and the three 1x light accessibility keys), the four `-glass0.5` profile
 * documents, the generated `packages/platform-web/src/macos27-profile.ts`, and the two
 * generation files the index holds for the 0.5 profiles. A file added to a 0.5 tree, or a
 * new document named `-glass0.5`, fires as well as a changed one.
 *
 * **Entries, where the 0.25 generation has to be added to the same file.** The fixtures
 * manifest and the generation index are the files G1a's publication and G3's seal append
 * the 0.25 bed and generation to, so a whole-file hash could only ever report that a second
 * generation arrived. They are decomposed the way `freeze.py` decomposes the manifest for
 * the 26.5 bed (its 2026-09-19 amendment): each 0.5 unit serialised canonically and hashed on
 * its own. The units are the manifest's profile entries for a `-glass0.5` key and every
 * `bedProvenance` block naming one; and the index's `schemaVersion`, its `files` entries
 * whose rows or documents are 0.5, the `byDocumentSha256` entries pointing at those files,
 * and the `currentByProfile` entries for a `-glass0.5` key. A 0.25 unit appended beside them
 * changes nothing here. A 0.5 unit rewritten, dropped or newly added fires, and that
 * includes a provenance block that mixes 0.25 and 0.5 profiles, because X5′ files no 0.5 key.
 *
 * **A projection of the default document.** `macos27MaterialProfileDocument` is a TypeScript
 * value assembled from the generated module, so its bytes are not the thing to protect: what
 * X41 freezes is its optical content (the four endpoint patches and their resolved digests),
 * its endpoint identities (name, platform, profile keys) and its CSS mapping. The projection
 * is the whole document, canonically serialised (keys sorted at every depth, no whitespace),
 * with one exemption: Decision Log 1's ruled readout, `glassTintAmount`, may appear at the
 * document's top level and only as exactly 0.5. Any other field added, removed or moved
 * fails. `DEFAULT_MATERIAL_PROFILE_DOCUMENT` is projected the same way and must read the
 * same hash, since Decision Log 1 keeps the default at 0.5.
 *
 * The projection is read from the platform-web SOURCE module, not from `dist/`, so the check
 * needs no build and cannot pass against a stale bundle. `macos27-document-projection.json`
 * beside the manifest is the recorded projection, pretty-printed; on a mismatch `verify`
 * names the paths that differ from it.
 *
 * What this does not cover, deliberately: the 26.5 evidence and `backgrounds/` (the freeze),
 * `DEFAULT_MATERIAL_PROFILE` and the goldens (X1 and their own tests), and the four 0.5
 * digests as computed rather than recorded (`macos27-profile-export.test.ts`).
 */

import { createHash } from "node:crypto";
import { readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  DEFAULT_MATERIAL_PROFILE_DOCUMENT,
  macos27MaterialProfileDocument,
} from "../../../../platform-web/src/material-document";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, "../../../../..");
const FIX = join(ROOT, "apps/reference-apple/fixtures");
const PROFILES = join(ROOT, "packages/calibration/profiles");
const GENERATIONS = join(ROOT, "packages/calibration/results/generations");
const MODULE = join(ROOT, "packages/platform-web/src/macos27-profile.ts");
const OUT = join(HERE, "sha256.txt");
const PROJECTION_OUT = join(HERE, "macos27-document-projection.json");

/** A `-glass0.5` profile key or document stem, and nothing at another position. */
const IS_05_KEY = /^apple-macos-27\.0-.*-glass0\.5$/;
const IS_05_DOCUMENT = /^apple-macos-27\.0-.*-glass0\.5(-[a-z-]+)?\.json$/;
/** The one field Decision Log 1 adds, and the one value it may hold. */
const RULED_READOUT = "glassTintAmount";
const RULED_POSITION = 0.5;

const sha = (bytes: Buffer | string): string => createHash("sha256").update(bytes).digest("hex");

/**
 * One JSON value with only its content deciding its bytes. A value JSON cannot carry
 * faithfully (a function, a non-finite number, `undefined` inside an array) is refused
 * rather than silently dropped, because a projection that loses a leaf protects nothing.
 */
function canonical(value: unknown, path = "$"): unknown {
  if (value === null || typeof value === "string" || typeof value === "boolean") return value;
  if (typeof value === "number") {
    if (!Number.isFinite(value)) throw new Error(`${path}: non-finite number ${value}`);
    return value;
  }
  if (Array.isArray(value)) {
    return value.map((item, i) => {
      if (item === undefined) throw new Error(`${path}[${i}]: undefined array element`);
      return canonical(item, `${path}[${i}]`);
    });
  }
  if (typeof value === "object") {
    const out: Record<string, unknown> = {};
    for (const key of Object.keys(value).sort()) {
      const v = (value as Record<string, unknown>)[key];
      if (v === undefined) continue;
      out[key] = canonical(v, `${path}.${key}`);
    }
    return out;
  }
  throw new Error(`${path}: ${typeof value} has no JSON form`);
}

const canon = (value: unknown): string => JSON.stringify(canonical(value));

function filesUnder(dir: string): string[] {
  const out: string[] = [];
  for (const name of readdirSync(dir).sort()) {
    const path = join(dir, name);
    if (statSync(path).isDirectory()) out.push(...filesUnder(path));
    else out.push(path);
  }
  return out;
}

/**
 * The document with the ruled readout taken out, refusing it anywhere but the top level
 * and at any value but the ruled one. The refusal is a hard error rather than a diff line,
 * because it is the one change X41 names and so the one a reader must not misread.
 */
function projectDocument(document: object, label: string): unknown {
  const { [RULED_READOUT]: readout, ...rest } = document as Record<string, unknown>;
  if (readout !== undefined && readout !== RULED_POSITION) {
    throw new Error(`${label}.${RULED_READOUT} is ${String(readout)}; X41 admits only 0.5`);
  }
  const projected = canonical(rest, label);
  const below = (v: unknown, path: string): void => {
    if (v === null || typeof v !== "object") return;
    for (const [k, child] of Object.entries(v)) {
      if (k === RULED_READOUT) throw new Error(`${path}.${k}: X41 admits the readout only at the top`);
      below(child, `${path}.${k}`);
    }
  };
  below(projected, label);
  return projected;
}

function* byteEntries(): Generator<string> {
  const files: string[] = [];
  for (const name of readdirSync(FIX).sort()) {
    if (IS_05_KEY.test(name) && statSync(join(FIX, name)).isDirectory()) {
      files.push(...filesUnder(join(FIX, name)));
    }
  }
  files.push(...readdirSync(PROFILES).sort().filter((n) => IS_05_DOCUMENT.test(n))
    .map((n) => join(PROFILES, n)));
  files.push(MODULE);
  for (const path of files) {
    yield `${sha(readFileSync(path))}  ${relative(ROOT, path)}`;
  }
}

interface FixtureManifest {
  readonly profiles: readonly { readonly profileKey: string }[];
  readonly bedProvenance?: readonly { readonly profiles?: readonly string[] }[];
}

function* manifestEntries(): Generator<string> {
  const m = JSON.parse(readFileSync(join(FIX, "manifest.json"), "utf8")) as FixtureManifest;
  const profiles = m.profiles.filter((p) => IS_05_KEY.test(p.profileKey))
    .sort((a, b) => (a.profileKey < b.profileKey ? -1 : 1));
  for (const p of profiles) yield `${sha(canon(p))}  manifest:profile:${p.profileKey}`;
  // Hashed by content and sorted, as the freeze hashes its own blocks: an appended block
  // for another bed changes nothing, and a 0.5 block dropped or rewritten fires.
  const blocks = (m.bedProvenance ?? []).filter((b) => (b.profiles ?? []).some((k) => IS_05_KEY.test(k)));
  for (const digest of blocks.map((b) => sha(canon(b))).sort()) {
    yield `${digest}  manifest:bedProvenance:glass0.5`;
  }
}

interface GenerationIndex {
  readonly schemaVersion: number;
  readonly files: Record<string, {
    readonly documents: readonly { readonly path: string }[];
    readonly rowsByProfileKey: Record<string, number>;
  }>;
  readonly byDocumentSha256: Record<string, readonly string[]>;
  readonly currentByProfile: Record<string, string>;
}

function* generationEntries(): Generator<string> {
  const index = JSON.parse(readFileSync(join(GENERATIONS, "index.json"), "utf8")) as GenerationIndex;
  yield `${sha(canon(index.schemaVersion))}  generations:index:schemaVersion`;
  const is05File = (name: string): boolean => {
    const f = index.files[name]!;
    return Object.keys(f.rowsByProfileKey).some((k) => IS_05_KEY.test(k))
      || f.documents.some((d) => IS_05_DOCUMENT.test(d.path.split("/").pop()!));
  };
  const files = Object.keys(index.files).filter(is05File).sort();
  for (const name of files) {
    yield `${sha(readFileSync(join(GENERATIONS, name)))}  ${relative(ROOT, join(GENERATIONS, name))}`;
    yield `${sha(canon(index.files[name]))}  generations:index:files:${name}`;
  }
  for (const doc of Object.keys(index.byDocumentSha256).sort()) {
    if (index.byDocumentSha256[doc]!.some((n) => files.includes(n))) {
      yield `${sha(canon(index.byDocumentSha256[doc]))}  generations:index:byDocumentSha256:${doc}`;
    }
  }
  for (const key of Object.keys(index.currentByProfile).sort()) {
    if (IS_05_KEY.test(key)) {
      yield `${sha(canon(index.currentByProfile[key]))}  generations:index:currentByProfile:${key}`;
    }
  }
}

function projection(): { readonly lines: string[]; readonly projected: unknown } {
  const projected = projectDocument(macos27MaterialProfileDocument, "macos27MaterialProfileDocument");
  const fallback = projectDocument(DEFAULT_MATERIAL_PROFILE_DOCUMENT, "DEFAULT_MATERIAL_PROFILE_DOCUMENT");
  return {
    projected,
    lines: [
      `${sha(JSON.stringify(projected))}  projection:macos27MaterialProfileDocument`,
      `${sha(JSON.stringify(fallback))}  projection:DEFAULT_MATERIAL_PROFILE_DOCUMENT`,
    ],
  };
}

/** Every leaf path at which two JSON values differ, for a mismatch a reader can act on. */
function differingPaths(a: unknown, b: unknown, path = "$"): string[] {
  if (a !== null && b !== null && typeof a === "object" && typeof b === "object") {
    const keys = new Set([...Object.keys(a), ...Object.keys(b)]);
    return [...keys].sort().flatMap((k) =>
      differingPaths((a as Record<string, unknown>)[k], (b as Record<string, unknown>)[k], `${path}.${k}`));
  }
  return JSON.stringify(a) === JSON.stringify(b) ? [] : [`${path}: ${JSON.stringify(a)} -> ${JSON.stringify(b)}`];
}

function main(): number {
  const mode = process.argv[2] ?? "verify";
  const { lines: projectionLines, projected } = projection();
  const lines = [...byteEntries(), ...manifestEntries(), ...generationEntries(), ...projectionLines];
  if (mode === "write") {
    writeFileSync(OUT, `${lines.join("\n")}\n`);
    writeFileSync(PROJECTION_OUT, `${JSON.stringify(projected, null, 2)}\n`);
    console.log(`wrote ${lines.length} entries to ${relative(ROOT, OUT)}`);
    return 0;
  }
  if (mode !== "verify") throw new Error(`unknown mode ${mode}; use write or verify`);
  const want = readFileSync(OUT, "utf8").split("\n").filter(Boolean);
  if (want.length === lines.length && want.every((l, i) => l === lines[i])) {
    console.log(`X41 0.5 generation intact: ${lines.length} entries`);
    return 0;
  }
  const ws = new Set(want);
  const ls = new Set(lines);
  for (const m of want.filter((l) => !ls.has(l)).slice(0, 20)) console.log("MISSING/CHANGED:", m);
  for (const a of lines.filter((l) => !ws.has(l)).slice(0, 20)) console.log("NEW/CHANGED:    ", a);
  const recorded = JSON.parse(readFileSync(PROJECTION_OUT, "utf8")) as unknown;
  for (const d of differingPaths(recorded, projected).slice(0, 20)) console.log("PROJECTION:     ", d);
  console.log(`THE FROZEN 0.5 GENERATION DIFFERS: recorded ${want.length}, now ${lines.length}`);
  return 1;
}

process.exitCode = main();

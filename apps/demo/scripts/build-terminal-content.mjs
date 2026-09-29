#!/usr/bin/env node
/* global process, console, Buffer, performance -- a build-time script, run by Node, never shipped */
/**
 * The terminal page's snapshot of this repository: what its simulated shell lists, reads, logs
 * and replays, since a page on GitHub Pages has no machine to ask.
 *
 *   node apps/demo/scripts/build-terminal-content.mjs
 *
 * Writes `src/gallery/terminal/shell/content.json` (run from anywhere; paths resolve from this
 * file). It records:
 *
 * - **The file tree**, from `git ls-files --cached --others --exclude-standard`, so it is the
 *   working tree as git sees it: nothing ignored (node_modules, dist, test-results, tmp) and
 *   nothing git would not commit. A directory is listed in full when it holds at most
 *   `FULL_LISTING` files; a larger one still lists its own entries down to `LISTED_DEPTH`, and
 *   below that it is recorded as elided, with its file, directory and byte counts, so the shell can
 *   say what it is not showing instead of pretending the directory is empty. That rule is what
 *   keeps the calibration evidence (tens of thousands of captures and rows) from being the
 *   snapshot. Sizes are the working tree's bytes. A file's date is the committer date of the last
 *   commit that touched it, read from one `git log --name-only` pass (per-file `git log -1` is
 *   minutes on this repository); a file no commit has touched yet takes its filesystem mtime. A
 *   directory's date is its newest entry's. Dates are indices into one sorted table.
 * - **The text of a few files worth reading** (`READABLE`); every other file is listed, and `cat`
 *   says it is not in the snapshot.
 * - **The last `LOG_LENGTH` commits**: hash, parents (so `HEAD~3` walks first parents across the
 *   merges rather than counting rows), author name (no email: the page has no reason to publish
 *   one), author date with its own offset, decorations, subject, body cut to `BODY_LINES`,
 *   and the `--shortstat` line, which is all `git show` has to stand in for a diff. Decorations
 *   keep HEAD, the current branch, `origin/*` and tags; the local branches agent worktrees leave
 *   behind are dropped, since the shell's `git branch` lists the current branch only.
 * - **One real `pnpm test` run** of `@vitreajs/vitrea` (packages/core), line by line with the
 *   millisecond each line arrived, for the shell to replay at the recorded pace. Vitest 4 swaps its
 *   reporter for a terse, colourless one when it detects an AI agent's environment, so the run is
 *   made without those markers and with `FORCE_COLOR=1`: what is recorded is what a person at a
 *   terminal sees. Its colour is then rewritten into the page's palette (below).
 * - **The versions** of node, pnpm and git that made the snapshot.
 *
 * The recorded paths are rewritten from this checkout's absolute path to `/Users/guest/vitrea`,
 * where the shell mounts the snapshot. The script fails rather than writes a file over `BUDGET`.
 */
import { execFileSync, spawn } from "node:child_process";
import { existsSync, lstatSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const repo = resolve(here, "../../..");
const out = resolve(here, "../src/gallery/terminal/shell/content.json");
const OUT_RELATIVE = "apps/demo/src/gallery/terminal/shell/content.json";
const MOUNT = "/Users/guest/vitrea";

const FULL_LISTING = 100;
const LISTED_DEPTH = 3;
const LOG_LENGTH = 60;
const BODY_LINES = 24;
const BUDGET = 400_000;
/** Skipped wherever they appear, even if a future .gitignore forgets one. */
const SKIPPED = new Set(["node_modules", "dist", "test-results", "tmp", ".git", ".DS_Store"]);
const READABLE = [
  "README.md",
  "package.json",
  "pnpm-workspace.yaml",
  "apps/demo/README.md",
  "apps/demo/package.json",
  "apps/demo/src/gallery/terminal/DESIGN.md",
];
const TESTED = { cwd: "packages/core", name: "@vitreajs/vitrea" };

const git = (...args) =>
  execFileSync("git", ["-c", "core.quotePath=false", ...args], {
    cwd: repo,
    encoding: "utf8",
    maxBuffer: 512 << 20,
  });

// ---------------------------------------------------------------------------------------------
// The tree.

const executable = new Set();
for (const record of git("ls-files", "-s", "-z").split("\0")) {
  const [meta, path] = record.split("\t");
  if (path !== undefined && meta.startsWith("100755")) executable.add(path);
}

const paths = git("ls-files", "-z", "--cached", "--others", "--exclude-standard")
  .split("\0")
  .filter((path) => path !== "" && path !== OUT_RELATIVE)
  .filter((path) => !path.split("/").some((part) => SKIPPED.has(part)));

/** Last commit to touch each path, newest first, so the first sighting wins. */
const committed = new Map();
let commitTime = 0;
for (const line of git("log", "--format=@@%ct", "--name-only", "HEAD").split("\n")) {
  if (line.startsWith("@@")) commitTime = Number(line.slice(2));
  else if (line !== "" && !committed.has(line)) committed.set(line, commitTime);
}

const root = { dirs: new Map(), files: new Map() };
for (const path of paths) {
  let stat;
  try {
    stat = lstatSync(resolve(repo, path));
  } catch {
    continue; // Deleted in the working tree but not yet from the index.
  }
  const parts = path.split("/");
  let dir = root;
  for (const part of parts.slice(0, -1)) {
    let next = dir.dirs.get(part);
    if (next === undefined) dir.dirs.set(part, (next = { dirs: new Map(), files: new Map() }));
    dir = next;
  }
  const date = committed.get(path) ?? Math.floor(stat.mtimeMs / 1000);
  const exec = executable.has(path) || (!committed.has(path) && (stat.mode & 0o111) !== 0);
  dir.files.set(parts.at(-1), { size: stat.size, date, exec });
}

/** Totals for every directory, bottom up: files, directories, bytes, newest date. */
function total(dir) {
  dir.total = { files: dir.files.size, dirs: dir.dirs.size, bytes: 0, date: 0 };
  for (const file of dir.files.values()) {
    dir.total.bytes += file.size;
    dir.total.date = Math.max(dir.total.date, file.date);
  }
  for (const sub of dir.dirs.values()) {
    const t = total(sub);
    dir.total.files += t.files;
    dir.total.dirs += t.dirs;
    dir.total.bytes += t.bytes;
    dir.total.date = Math.max(dir.total.date, t.date);
  }
  return dir.total;
}
total(root);

const dateSet = new Set();
const collectDates = (dir, depth) => {
  dateSet.add(dir.total.date);
  if (elided(dir, depth)) return;
  for (const file of dir.files.values()) dateSet.add(file.date);
  for (const sub of dir.dirs.values()) collectDates(sub, depth + 1);
};
const elided = (dir, depth) => depth > LISTED_DEPTH && dir.total.files > FULL_LISTING;
collectDates(root, 0);
const dates = [...dateSet].sort((a, b) => a - b);
const dateIndex = new Map(dates.map((date, i) => [date, i]));

/**
 * The encoding the shell decodes (`snapshot.ts`), as nested arrays so the JSON stays small and its
 * inferred type stays cheap: a file is `[name, size, date]` (a fourth element `1` when it is
 * executable), a directory `[name, date, entries]`, and an elided directory
 * `[name, date, { entries, files, dirs, bytes }]`.
 */
function encode(dir, depth) {
  const entries = [];
  for (const [name, sub] of dir.dirs) {
    const date = dateIndex.get(sub.total.date);
    if (elided(sub, depth + 1)) {
      const { files, dirs, bytes } = sub.total;
      entries.push([name, date, { entries: sub.dirs.size + sub.files.size, files, dirs, bytes }]);
    } else {
      entries.push([name, date, encode(sub, depth + 1)]);
    }
  }
  for (const [name, file] of dir.files) {
    const entry = [name, file.size, dateIndex.get(file.date)];
    if (file.exec) entry.push(1);
    entries.push(entry);
  }
  return entries.sort((a, b) => (a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0));
}
const tree = encode(root, 0);

// ---------------------------------------------------------------------------------------------
// Files worth reading.

const files = {};
const packageManifests = [...(root.dirs.get("packages")?.dirs.keys() ?? [])]
  .map((name) => `packages/${name}/package.json`)
  .sort();
for (const path of [...READABLE, ...packageManifests]) {
  const absolute = resolve(repo, path);
  if (existsSync(absolute)) files[path] = readFileSync(absolute, "utf8");
}

// ---------------------------------------------------------------------------------------------
// The log.

const FIELD = "\x1f";
const RECORD = "\x1e";
const FORMAT = ["%H", "%P", "%an", "%aI", "%D", "%s", "%b"].join(FIELD);
const log = git("log", `-${LOG_LENGTH}`, `--format=${FORMAT}${RECORD}`)
  .split(RECORD)
  .map((record) => record.replace(/^\n/, ""))
  .filter((record) => record.includes(FIELD))
  .map((record) => {
    const [hash, parents, author, date, allRefs, subject, rawBody] = record.split(FIELD);
    const refs = allRefs
      .split(", ")
      .filter((ref) => /^(HEAD|HEAD -> .*|main|origin\/.*|tag: .*)$/.test(ref))
      .join(", ");
    const lines = rawBody.replace(/\s+$/, "").split("\n");
    const body = rawBody.trim() === "" ? [] : lines;
    return {
      hash,
      parents: parents === "" ? [] : parents.split(" "),
      author,
      date,
      refs,
      subject,
      body: body.slice(0, BODY_LINES).join("\n"),
      omitted: Math.max(0, body.length - BODY_LINES),
      stat: "",
    };
  });
const stats = git("log", `-${LOG_LENGTH}`, `--format=${RECORD}%H`, "--shortstat").split(RECORD);
for (const block of stats) {
  const [hash, ...rest] = block.trim().split("\n");
  const commit = log.find((entry) => entry.hash === hash);
  if (commit !== undefined) commit.stat = rest.join(" ").trim();
}

const count = (range) => {
  try {
    return Number(git("rev-list", "--count", range).trim());
  } catch {
    return 0;
  }
};
const head = {
  branch: git("rev-parse", "--abbrev-ref", "HEAD").trim(),
  abbrev: git("log", "-1", "--format=%h").trim().length,
  commits: count("HEAD"),
  ahead: count("origin/main..HEAD"),
  remote: git("remote", "get-url", "origin").trim(),
  date: git("log", "-1", "--format=%cI").trim(),
};

// ---------------------------------------------------------------------------------------------
// The recorded test run.

/**
 * Rewrites the run's SGR into what the page allows: the sixteen foreground colours and bold.
 * Dim becomes bright black (and is dropped where a colour is already set, since vitest dims a
 * coloured slow-test tick to soften it, not to change its hue); a background badge (vitest's
 * black-on-cyan ` RUN `, red ` FAIL `) keeps its colour as bold text in that colour; every
 * non-SGR control sequence is dropped. The state carries across lines, but each line is written
 * self-contained, opening with the colour it inherits and closing any it leaves open, so a replay
 * interrupted after any line leaves the terminal at its default.
 */
function sanitize(lines) {
  const state = { bold: false, dim: false, fg: undefined, bg: undefined };
  const effective = () => {
    let fg = state.fg;
    if (state.bg !== undefined) fg = state.bg - 10;
    else if (fg === undefined && state.dim) fg = 90;
    return { bold: state.bold || state.bg !== undefined, fg };
  };
  const sgr = (from, to) => {
    const codes = [];
    if (from.bold !== to.bold) codes.push(to.bold ? 1 : 22);
    if (from.fg !== to.fg) codes.push(to.fg ?? 39);
    return codes.length === 0 ? "" : `\x1b[${codes.join(";")}m`;
  };
  const DEFAULT = { bold: false, fg: undefined };
  const apply = (params) => {
    const codes = params === "" ? [0] : params.split(";").map(Number);
    for (let i = 0; i < codes.length; i++) {
      const code = codes[i];
      if (code === 0) {
        Object.assign(state, { bold: false, dim: false, fg: undefined, bg: undefined });
      }
      else if (code === 1) state.bold = true;
      else if (code === 2) state.dim = true;
      else if (code === 22) state.bold = state.dim = false;
      else if ((code >= 30 && code <= 37) || (code >= 90 && code <= 97)) state.fg = code;
      else if (code === 39) state.fg = undefined;
      else if ((code >= 40 && code <= 47) || (code >= 100 && code <= 107)) state.bg = code;
      else if (code === 49) state.bg = undefined;
      else if (code === 38 || code === 48) {
        // An extended colour: 5;n or 2;r;g;b. Only 5;n inside the sixteen survives, as its code.
        const kind = codes[i + 1];
        const n = codes[i + 2];
        if (kind === 5 && n !== undefined && n < 16) {
          const mapped = n < 8 ? 30 + n : 82 + n;
          if (code === 38) state.fg = mapped;
          else state.bg = mapped + 10;
        }
        i += kind === 5 ? 2 : 4;
      }
    }
  };
  // A colour is written only in front of the text it applies to, so a run of sequences that
  // cancel out (the badge's `49m 39m 22m`) writes nothing.
  return lines.map(([ms, raw]) => {
    let text = "";
    let shown = DEFAULT;
    const visible = (piece) => {
      // eslint-disable-next-line no-control-regex -- stripping control characters is the point.
      const clean = piece.replace(/[\x00-\x08\x0b-\x1f\x7f]/g, "");
      if (clean === "") return;
      const next = effective();
      text += sgr(shown, next) + clean;
      shown = next;
    };
    // eslint-disable-next-line no-control-regex -- an escape sequence begins with ESC.
    const pattern = /\x1b\[([0-9;?]*)([@-~])|\x1b[^[]?/g;
    let last = 0;
    for (let match; (match = pattern.exec(raw)) !== null; ) {
      visible(raw.slice(last, match.index));
      last = pattern.lastIndex;
      if (match[2] === "m" && !match[1].startsWith("?")) apply(match[1]);
    }
    visible(raw.slice(last));
    return [ms, text + sgr(shown, DEFAULT)];
  });
}

async function record() {
  const env = { ...process.env, FORCE_COLOR: "1" };
  for (const marker of ["AI_AGENT", "CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "CI", "NO_COLOR"]) {
    delete env[marker];
  }
  const started = performance.now();
  const lines = [];
  let partial = "";
  const child = spawn("pnpm", ["test"], { cwd: resolve(repo, TESTED.cwd), env });
  const take = (chunk) => {
    const at = Math.round(performance.now() - started);
    const pieces = (partial + chunk.toString("utf8")).split("\n");
    partial = pieces.pop() ?? "";
    for (const piece of pieces) lines.push([at, piece.replace(/\r$/, "")]);
  };
  child.stdout.on("data", take);
  child.stderr.on("data", take);
  const code = await new Promise((done) => child.on("close", done));
  if (partial !== "") lines.push([Math.round(performance.now() - started), partial]);
  if (code !== 0) throw new Error(`The recorded run of ${TESTED.name} failed (exit ${code}).`);
  while (lines.length > 0 && lines.at(-1)[1].trim() === "") lines.pop();
  // Times are from the spawn, so the pause before pnpm's first line is part of the replay too.
  const rooted = lines.map(([ms, text]) => [ms, text.split(repo).join(MOUNT)]);
  return {
    cwd: TESTED.cwd,
    package: TESTED.name,
    recorded: new Date().toISOString(),
    durationMs: rooted.at(-1)?.[0] ?? 0,
    lines: sanitize(rooted),
  };
}

const test = await record();
const versions = {
  node: process.version,
  pnpm: execFileSync("pnpm", ["-v"], { cwd: repo, encoding: "utf8" }).trim(),
  git: git("--version").trim(),
};

// ---------------------------------------------------------------------------------------------
// Written one top-level key per line, so a diff of the snapshot says which part moved.

const content = { version: 1, head, versions, dates, tree, files, log, test };
const json =
  "{\n" +
  Object.entries(content)
    .map(([key, value]) => `${JSON.stringify(key)}:${JSON.stringify(value)}`)
    .join(",\n") +
  "\n}\n";
const bytes = Buffer.byteLength(json);
if (bytes > BUDGET) {
  throw new Error(`content.json would be ${bytes} bytes, over ${BUDGET}: tighten FULL_LISTING.`);
}
writeFileSync(out, json);

let listed = 0;
let elidedDirs = 0;
const walk = (entries) => {
  for (const entry of entries) {
    listed++;
    if (Array.isArray(entry[2])) walk(entry[2]);
    else if (typeof entry[2] === "object") elidedDirs++;
  }
};
walk(tree);
console.warn(
  `${bytes} bytes: ${listed} entries listed of ${root.total.files} files ` +
    `(${elidedDirs} directories ` +
    `elided), ${Object.keys(files).length} readable files, ${log.length} commits, ` +
    `${test.lines.length} recorded lines over ${test.durationMs} ms`,
);

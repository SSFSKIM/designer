/**
 * The snapshot the shell runs over: a read-only filesystem, the log and the recorded test run,
 * decoded from `content.json` (written by `scripts/build-terminal-content.mjs`, whose header says
 * what is recorded and how).
 *
 * The filesystem is mounted where a person's checkout would be: the repository at
 * `/Users/guest/vitrea`, inside a home directory that holds nothing else. A directory the
 * snapshot elided (the calibration evidence runs to tens of thousands of files) is still a
 * directory, with its counts, so a command that reaches it can say what it is not showing; a path
 * below one is `elided`, neither found nor missing.
 */

import raw from "./content.json";

export const HOME = "/Users/guest";
export const REPO = `${HOME}/vitrea`;
export const USER = "guest";
export const HOST = "vitrea";

export interface Elision {
  /** The directory's own entries, files and directories, which `ls -l` sizes it by. */
  readonly entries: number;
  readonly files: number;
  readonly dirs: number;
  readonly bytes: number;
}

export interface FileNode {
  readonly kind: "file";
  readonly name: string;
  readonly path: string;
  readonly size: number;
  /** Epoch milliseconds. */
  readonly date: number;
  readonly executable: boolean;
  /** The file's text when the snapshot carries it; every other file is listed only. */
  readonly text: string | undefined;
}

export interface DirNode {
  readonly kind: "dir";
  readonly name: string;
  readonly path: string;
  readonly date: number;
  /** Undefined when the snapshot elided the directory's contents. */
  readonly entries: ReadonlyMap<string, Node> | undefined;
  readonly elision: Elision | undefined;
}

export type Node = FileNode | DirNode;

export type Lookup =
  | { readonly kind: "found"; readonly node: Node }
  | { readonly kind: "missing" }
  | { readonly kind: "not-a-directory" }
  /** The path runs through a directory whose contents the snapshot does not list. */
  | { readonly kind: "elided"; readonly dir: DirNode };

export interface Commit {
  readonly hash: string;
  /** Full hashes, the first parent first; some may be older than the snapshot reaches. */
  readonly parents: readonly string[];
  readonly author: string;
  /** ISO 8601 with the author's own offset, which `git log` prints the date in. */
  readonly date: string;
  /** `%D`: "HEAD -> main, origin/main", or empty. */
  readonly refs: string;
  readonly subject: string;
  readonly body: readonly string[];
  /** Body lines past the snapshot's cut. */
  readonly omitted: number;
  /** The `--shortstat` line, empty for a merge. */
  readonly stat: string;
}

export interface RecordedRun {
  /** The package directory the run was made in, relative to the repository. */
  readonly cwd: string;
  readonly package: string;
  readonly recorded: string;
  readonly durationMs: number;
  /** Each line with the millisecond after the spawn it arrived at, colour already in palette. */
  readonly lines: readonly (readonly [number, string])[];
}

type RawFile = [string, number, number] | [string, number, number, 1];
type RawDir = [string, number, RawEntry[] | Elision];
type RawEntry = RawFile | RawDir;

interface RawContent {
  readonly head: {
    readonly branch: string;
    readonly abbrev: number;
    readonly commits: number;
    readonly ahead: number;
    readonly remote: string;
    readonly date: string;
  };
  readonly versions: { readonly node: string; readonly pnpm: string; readonly git: string };
  readonly dates: readonly number[];
  readonly tree: RawEntry[];
  readonly files: Readonly<Record<string, string>>;
  readonly log: readonly (Omit<Commit, "body"> & { readonly body: string })[];
  readonly test: RecordedRun;
}

const content = raw as unknown as RawContent;

export const head = content.head;
export const versions = content.versions;
export const recordedRun: RecordedRun = content.test;
export const commits: readonly Commit[] = content.log.map((commit) => ({
  ...commit,
  body: commit.body === "" ? [] : commit.body.split("\n"),
}));

const snapshotDate = Date.parse(head.date);
const dateOf = (index: number): number => (content.dates[index] ?? 0) * 1000;

function decode(entries: readonly RawEntry[], parent: string): Map<string, Node> {
  const map = new Map<string, Node>();
  for (const entry of entries) {
    const name = entry[0];
    const path = `${parent}/${name}`;
    if (entry.length === 3 && typeof entry[2] === "object") {
      const [, date, inner] = entry;
      const listed = Array.isArray(inner);
      map.set(name, {
        kind: "dir",
        name,
        path,
        date: dateOf(date),
        entries: listed ? decode(inner, path) : undefined,
        elision: listed ? undefined : inner,
      });
    } else {
      const [, size, date] = entry as RawFile;
      const relative = path.slice(REPO.length + 1);
      map.set(name, {
        kind: "file",
        name,
        path,
        size,
        date: dateOf(date),
        executable: entry.length === 4,
        text: content.files[relative],
      });
    }
  }
  return map;
}

const dir = (path: string, name: string, entries: Map<string, Node>): DirNode => ({
  kind: "dir",
  name,
  path,
  date: snapshotDate,
  entries,
  elision: undefined,
});

const repository = dir(REPO, "vitrea", decode(content.tree, REPO));
const repositoryDate = Math.max(
  ...[...(repository.entries?.values() ?? [])].map((node) => node.date),
);
const mounted: DirNode = { ...repository, date: repositoryDate };
const home = dir(HOME, USER, new Map([["vitrea", mounted]]));
const users = dir("/Users", "Users", new Map([[USER, home]]));
export const root = dir("/", "/", new Map([["Users", users]]));

/**
 * Resolves `path` against `cwd` into a normalised absolute path. `~` is the shell's to expand
 * before this, as zsh does, so here it is an ordinary name.
 */
export function resolvePath(cwd: string, path: string): string {
  const parts = (path.startsWith("/") ? path : `${cwd}/${path}`).split("/");
  const out: string[] = [];
  for (const part of parts) {
    if (part === "" || part === ".") continue;
    if (part === "..") out.pop();
    else out.push(part);
  }
  return `/${out.join("/")}`;
}

export function lookup(path: string): Lookup {
  let node: Node = root;
  for (const part of path.split("/")) {
    if (part === "") continue;
    if (node.kind === "file") return { kind: "not-a-directory" };
    if (node.entries === undefined) return { kind: "elided", dir: node };
    const next: Node | undefined = node.entries.get(part);
    if (next === undefined) return { kind: "missing" };
    node = next;
  }
  return { kind: "found", node };
}

/** `path` with the home directory written as `~`, as zsh prints a directory. */
export function tildePath(path: string): string {
  if (path === HOME) return "~";
  return path.startsWith(`${HOME}/`) ? `~${path.slice(HOME.length)}` : path;
}

export function insideRepository(path: string): boolean {
  return path === REPO || path.startsWith(`${REPO}/`);
}

/** Byte-order comparison, which is how `ls` and `tree` sort in a UTF-8 locale on macOS. */
export function byName(a: string, b: string): number {
  return a < b ? -1 : a > b ? 1 : 0;
}

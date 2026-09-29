/**
 * The commands that read the snapshot's files: `ls`, `tree`, `cat`, `head`, `tail`, `grep`, `wc`,
 * `cd` and `pwd`, in the shapes the macOS tools print.
 *
 * `ls -l` is BSD's long format on APFS, where a directory's link count and size both follow from
 * its entry count ((entries + 2) links, 32 bytes each), and `total` counts 512-byte blocks of 4 KiB
 * allocations. Dates are shown in the reader's own time zone, as `ls` shows them, the time for
 * anything in the last six months and the year for anything older. Options are accepted in any
 * position, as GNU tools do; BSD's stop at the first operand, which only ever surprises.
 *
 * Where the snapshot does not reach (a file listed without its text, a directory elided for
 * size), the command says so on standard error in yellow, with the counts, rather than erring
 * like a missing file or printing nothing like an empty one.
 */

import {
  columns,
  count,
  cyan,
  directory,
  green,
  grey,
  humanSize,
  magenta,
  padStart,
  red,
  yellow,
} from "./ansi";
import type { Io } from "./io";
import {
  byName,
  HOME,
  lookup,
  resolvePath,
  tildePath,
  USER,
  type DirNode,
  type Elision,
  type Lookup,
  type Node,
} from "./snapshot";

interface Options {
  readonly flags: ReadonlySet<string>;
  readonly values: ReadonlyMap<string, string>;
  readonly operands: readonly string[];
}

/**
 * Splits `-abc` flags and `-n 5` / `-n5` values from operands. An unknown flag prints the tool's
 * complaint and its usage line and gives undefined, which the command returns as status 1.
 */
function options(io: Io, allowed: string, withValue: string, usage: string): Options | undefined {
  const flags = new Set<string>();
  const values = new Map<string, string>();
  const operands: string[] = [];
  const args = [...io.args];
  for (let i = 0; i < args.length; i++) {
    const arg = args[i] as string;
    if (arg === "--") {
      operands.push(...args.slice(i + 1));
      break;
    }
    if (!arg.startsWith("-") || arg === "-" || arg.startsWith("--")) {
      if (!arg.startsWith("--")) operands.push(arg);
      continue;
    }
    for (let j = 1; j < arg.length; j++) {
      const flag = arg[j] as string;
      if (withValue.includes(flag)) {
        const value = arg.length > j + 1 ? arg.slice(j + 1) : args[++i];
        if (value === undefined) {
          io.err(red(`${io.name}: option requires an argument -- ${flag}`) + `\n${usage}\n`);
          return undefined;
        }
        values.set(flag, value);
        break;
      }
      if (!allowed.includes(flag)) {
        io.err(red(`${io.name}: invalid option -- ${flag}`) + `\n${usage}\n`);
        return undefined;
      }
      flags.add(flag);
    }
  }
  return { flags, values, operands };
}

/** `-5` is `-n 5` to head and tail, as it has been since before POSIX. */
function lineCountShorthand(args: readonly string[]): string[] {
  return args.flatMap((arg) => (/^-\d+$/.test(arg) ? ["-n", arg.slice(1)] : [arg]));
}

function locate(io: Io, arg: string): Lookup {
  return lookup(resolvePath(io.session.cwd, arg));
}

/** The complaint for an operand that did not resolve to what the command needed. */
function complain(io: Io, shown: string, found: Lookup): void {
  const say = (paint: (s: string) => string, what: string): void => {
    io.err(paint(`${io.name}: ${shown}: ${what}`) + "\n");
  };
  if (found.kind === "missing") say(red, "No such file or directory");
  else if (found.kind === "not-a-directory") say(red, "Not a directory");
  else if (found.kind === "elided") say(yellow, "not in the snapshot");
}

function elisionNote(elision: Elision): string {
  const dirs = elision.dirs === 0 ? "" : ` in ${count(elision.dirs)} directories`;
  return `${count(elision.files)} files${dirs}, ${humanSize(elision.bytes)}`;
}

function entriesOf(dir: DirNode): Node[] {
  return [...(dir.entries?.values() ?? [])];
}

function entryCount(dir: DirNode): number {
  return dir.entries?.size ?? dir.elision?.entries ?? 0;
}

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const HALF_YEAR = 182.5 * 24 * 3600 * 1000;

/** `ls -l`'s date: `Sep 29 09:05` within six months, `Mar  2  2025` beyond or in the future. */
export function lsDate(ms: number, nowMs: number): string {
  const d = new Date(ms);
  const day = `${MONTHS[d.getMonth()]} ${String(d.getDate()).padStart(2)}`;
  const recent = ms <= nowMs && nowMs - ms < HALF_YEAR;
  if (recent) {
    const hh = String(d.getHours()).padStart(2, "0");
    const mm = String(d.getMinutes()).padStart(2, "0");
    return `${day} ${hh}:${mm}`;
  }
  return `${day}  ${d.getFullYear()}`;
}

const LS_USAGE =
  "usage: ls [-@ABCFGHILOPRSTUWabcdefghiklmnopqrstuvwxy1%,] [--color=when] [-D format] [file ...]";

interface Listed {
  readonly name: string;
  readonly node: Node;
}

export function ls(io: Io): number {
  const parsed = options(io, "aAlh1FrtSdCG@", "", LS_USAGE);
  if (parsed === undefined) return 1;
  const flag = (f: string): boolean => parsed.flags.has(f);
  const now = io.session.host.now().getTime();
  const width = io.session.columns();

  const name = (entry: Listed): string => {
    const isDir = entry.node.kind === "dir";
    const shown = isDir && io.tty ? directory(entry.name) : entry.name;
    if (!flag("F")) return shown;
    return shown + (isDir ? "/" : entry.node.kind === "file" && entry.node.executable ? "*" : "");
  };
  const sort = (entries: Listed[]): Listed[] => {
    const sorted = entries.sort((a, b) => {
      if (flag("t") && a.node.date !== b.node.date) return b.node.date - a.node.date;
      if (flag("S")) {
        const size = (n: Node): number => (n.kind === "file" ? n.size : (entryCount(n) + 2) * 32);
        if (size(a.node) !== size(b.node)) return size(b.node) - size(a.node);
      }
      return byName(a.name, b.name);
    });
    return flag("r") ? sorted.reverse() : sorted;
  };
  const print = (entries: Listed[], withTotal: boolean): void => {
    if (entries.length === 0) {
      if (flag("l") && withTotal) io.out("total 0\n");
      return;
    }
    if (flag("l")) {
      const rows = entries.map(({ node }) => {
        const dir = node.kind === "dir";
        const links = dir ? entryCount(node) + 2 : 1;
        const bytes = dir ? links * 32 : node.size;
        const mode = dir ? "drwxr-xr-x" : node.executable ? "-rwxr-xr-x" : "-rw-r--r--";
        return { mode, links: String(links), size: flag("h") ? humanSize(bytes) : String(bytes) };
      });
      const linkWidth = Math.max(...rows.map((r) => r.links.length));
      const sizeWidth = Math.max(...rows.map((r) => r.size.length));
      if (withTotal) {
        const blocks = entries.reduce(
          (sum, { node }) => sum + (node.kind === "file" ? Math.ceil(node.size / 4096) * 8 : 0),
          0,
        );
        io.out(`total ${blocks}\n`);
      }
      entries.forEach((entry, i) => {
        const row = rows[i] as (typeof rows)[number];
        io.out(
          `${row.mode}  ${padStart(row.links, linkWidth)} ${USER}  staff  ` +
            `${padStart(row.size, sizeWidth)} ${lsDate(entry.node.date, now)} ${name(entry)}\n`,
        );
      });
    } else if (flag("1") || (!io.tty && !flag("C"))) {
      for (const entry of entries) io.out(`${name(entry)}\n`);
    } else {
      for (const line of columns(entries.map(name), width)) io.out(`${line}\n`);
    }
  };

  const operands = parsed.operands.length > 0 ? [...parsed.operands].sort(byName) : ["."];
  const files: Listed[] = [];
  const dirs: { shown: string; dir: DirNode }[] = [];
  let status = 0;
  for (const shown of operands) {
    const found = locate(io, shown);
    if (found.kind !== "found") {
      complain(io, shown, found);
      status = 1;
    } else if (found.node.kind === "dir" && !flag("d")) dirs.push({ shown, dir: found.node });
    else files.push({ name: shown, node: found.node });
  }
  print(sort(files), false);
  dirs.forEach(({ shown, dir }, i) => {
    if (files.length > 0 || i > 0) io.out("\n");
    if (operands.length > 1) io.out(`${shown}:\n`);
    if (dir.entries === undefined) {
      const elision = dir.elision as Elision;
      io.err(yellow(`ls: ${shown}: not in the snapshot (${elisionNote(elision)})`) + "\n");
      return;
    }
    const all = flag("a") || flag("A");
    const entries: Listed[] = entriesOf(dir)
      .filter((node) => all || !node.name.startsWith("."))
      .map((node) => ({ name: node.name, node }));
    if (flag("a")) {
      const parent = lookup(resolvePath(dir.path, ".."));
      entries.push({ name: ".", node: dir });
      entries.push({ name: "..", node: parent.kind === "found" ? parent.node : dir });
    }
    print(sort(entries), true);
  });
  return status;
}

export function tree(io: Io): number {
  const parsed = options(io, "adf", "L", "usage: tree [-adf] [-L level] [directory ...]");
  if (parsed === undefined) return 1;
  const levelText = parsed.values.get("L");
  const level = levelText === undefined ? Infinity : Number(levelText);
  if (levelText !== undefined && (!Number.isInteger(level) || level < 1)) {
    io.err(red("tree: Invalid level, must be greater than 0.") + "\n");
    return 1;
  }
  const all = parsed.flags.has("a");
  const dirsOnly = parsed.flags.has("d");
  const fullPath = parsed.flags.has("f");
  let dirCount = 0;
  let fileCount = 0;
  const lines: string[] = [];
  const label = (node: Node, shown: string): string => {
    if (node.kind === "file") return shown;
    const drawn = io.tty ? directory(shown) : shown;
    if (node.entries !== undefined) return drawn;
    const note = `[${elisionNote(node.elision as Elision)} not in the snapshot]`;
    return `${drawn} ${io.tty ? grey(note) : note}`;
  };
  const walk = (dir: DirNode, shownPath: string, prefix: string, depth: number): void => {
    const children = entriesOf(dir)
      .filter((node) => (all || !node.name.startsWith(".")) && (!dirsOnly || node.kind === "dir"))
      .sort((a, b) => byName(a.name, b.name));
    children.forEach((child, i) => {
      const last = i === children.length - 1;
      const path = `${shownPath}/${child.name}`;
      const branch = last ? "└── " : "├── ";
      lines.push(`${prefix}${branch}${label(child, fullPath ? path : child.name)}`);
      if (child.kind === "dir") {
        dirCount++;
        if (depth < level) walk(child, path, `${prefix}${last ? "    " : "│   "}`, depth + 1);
      } else fileCount++;
    });
  };
  const operands = parsed.operands.length > 0 ? parsed.operands : ["."];
  let status = 0;
  for (const shown of operands) {
    const found = locate(io, shown);
    if (found.kind !== "found" || found.node.kind !== "dir") {
      lines.push(`${shown} [error opening dir]`);
      status = 1;
      continue;
    }
    lines.push(label(found.node, shown));
    walk(found.node, shown, "", 1);
  }
  const dirWord = dirCount === 1 ? "directory" : "directories";
  const summary = dirsOnly
    ? `${dirCount} ${dirWord}`
    : `${dirCount} ${dirWord}, ${fileCount} ${fileCount === 1 ? "file" : "files"}`;
  io.out(`${lines.join("\n")}\n\n${summary}\n`);
  return status;
}

/**
 * The text an operand names, or undefined after saying why there is none. `-` and no operand at
 * all read the pipe, and with no pipe there is nothing to read: a terminal's keyboard is not a
 * stream this shell can hand a command.
 */
function readText(io: Io, shown: string | undefined): string | undefined {
  if (shown === undefined || shown === "-") {
    if (io.stdin !== undefined) return io.stdin;
    const line = `${io.name}: reading from the keyboard is not simulated here; name a file`;
    io.err(yellow(line) + "\n");
    return undefined;
  }
  const found = locate(io, shown);
  if (found.kind !== "found") {
    complain(io, shown, found);
    return undefined;
  }
  if (found.node.kind === "dir") {
    io.err(red(`${io.name}: ${shown}: Is a directory`) + "\n");
    return undefined;
  }
  if (found.node.text === undefined) {
    const line = `${io.name}: ${shown}: not in the snapshot (${count(found.node.size)} bytes)`;
    io.err(yellow(line) + "\n");
    return undefined;
  }
  return found.node.text;
}

/** A text's lines, without the empty string after its final newline. */
function linesOf(text: string): string[] {
  const lines = text.split("\n");
  if (lines.at(-1) === "") lines.pop();
  return lines;
}

export function cat(io: Io): number {
  const parsed = options(io, "n", "", "usage: cat [-n] [file ...]");
  if (parsed === undefined) return 1;
  const sources = parsed.operands.length > 0 ? parsed.operands : [undefined];
  let status = 0;
  let number = 0;
  for (const shown of sources) {
    const text = readText(io, shown);
    if (text === undefined) {
      status = 1;
      continue;
    }
    if (parsed.flags.has("n")) {
      for (const line of linesOf(text)) io.out(`${String(++number).padStart(6)}\t${line}\n`);
    } else io.out(text);
  }
  return status;
}

function headOrTail(io: Io, which: "head" | "tail"): number {
  const shorthand = { ...io, args: lineCountShorthand(io.args) };
  const parsed = options(shorthand, "", "n", `usage: ${which} [-n lines] [file ...]`);
  if (parsed === undefined) return 1;
  const n = Number(parsed.values.get("n") ?? 10);
  if (!Number.isInteger(n) || n < 0) {
    io.err(red(`${which}: illegal line count -- ${parsed.values.get("n")}`) + "\n");
    return 1;
  }
  const sources = parsed.operands.length > 0 ? parsed.operands : [undefined];
  let status = 0;
  sources.forEach((shown, i) => {
    const text = readText(io, shown);
    if (text === undefined) {
      status = 1;
      return;
    }
    if (sources.length > 1) io.out(`${i > 0 ? "\n" : ""}==> ${shown} <==\n`);
    const lines = linesOf(text);
    const kept = which === "head" ? lines.slice(0, n) : n === 0 ? [] : lines.slice(-n);
    if (kept.length > 0) io.out(`${kept.join("\n")}\n`);
  });
  return status;
}

export const head = (io: Io): number => headOrTail(io, "head");
export const tail = (io: Io): number => headOrTail(io, "tail");

/** Every file under `dir` that the snapshot reaches, depth first in name order. */
function* walkFiles(dir: DirNode, shown: string): Generator<{ shown: string; node: Node }> {
  for (const node of entriesOf(dir).sort((a, b) => byName(a.name, b.name))) {
    const path = shown === "." ? node.name : `${shown}/${node.name}`;
    if (node.kind === "dir") yield* walkFiles(node, path);
    else yield { shown: path, node };
  }
}

/**
 * grep over the text the snapshot carries, in grep's colours on a terminal (file magenta, line
 * number green, separators cyan, the match bold red). A file listed without its text is
 * complained about when named, and counted when a recursive search passes it.
 */
export function grep(io: Io): number {
  const usage = "usage: grep [-cEFHhilnrRv] pattern [file ...]";
  const parsed = options(io, "cEFHhilnrRv", "e", usage);
  if (parsed === undefined) return 2;
  const flag = (f: string): boolean => parsed.flags.has(f);
  const operands = [...parsed.operands];
  const pattern = parsed.values.get("e") ?? operands.shift();
  if (pattern === undefined) {
    io.err(`${usage}\n`);
    return 2;
  }
  const flags = flag("i") ? "giu" : "gu";
  const literal = pattern.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  let regex: RegExp;
  try {
    regex = new RegExp(flag("F") ? literal : pattern, flags);
  } catch {
    regex = new RegExp(literal, flags);
  }

  const recursive = flag("r") || flag("R");
  const sources: { shown: string | undefined; text: string | undefined }[] = [];
  let unread = 0;
  if (operands.length === 0 && !recursive) {
    sources.push({ shown: undefined, text: readText(io, undefined) });
  }
  for (const shown of operands.length > 0 ? operands : recursive ? ["."] : []) {
    const found = locate(io, shown);
    if (!recursive || (found.kind === "found" && found.node.kind === "file")) {
      sources.push({ shown, text: readText(io, shown) });
    } else if (found.kind !== "found") {
      complain(io, shown, found);
      sources.push({ shown, text: undefined });
    } else if (found.node.kind === "dir") {
      for (const file of walkFiles(found.node, shown)) {
        if (file.node.kind === "file" && file.node.text !== undefined) {
          sources.push({ shown: file.shown, text: file.node.text });
        } else unread++;
      }
    }
  }

  const named = !flag("h") && (flag("H") || recursive || sources.length > 1);
  const paint = (f: (s: string) => string, s: string): string => (io.tty ? f(s) : s);
  const prefix = (shown: string | undefined): string =>
    named && shown !== undefined ? paint(magenta, shown) + paint(cyan, ":") : "";
  const highlight = (line: string): string =>
    line.replace(regex, (m) => (m === "" ? m : `\x1b[1;31m${m}\x1b[0m`));
  let matched = false;
  let errored = false;
  for (const { shown, text } of sources) {
    if (text === undefined) {
      errored = true;
      continue;
    }
    let matches = 0;
    linesOf(text).forEach((line, i) => {
      regex.lastIndex = 0;
      if (regex.test(line) === flag("v")) return;
      matches++;
      if (flag("c") || flag("l")) return;
      const number = flag("n") ? paint(green, String(i + 1)) + paint(cyan, ":") : "";
      io.out(`${prefix(shown)}${number}${flag("v") || !io.tty ? line : highlight(line)}\n`);
    });
    matched ||= matches > 0;
    if (flag("l") && matches > 0) io.out(`${paint(magenta, shown ?? "(standard input)")}\n`);
    else if (flag("c")) io.out(`${prefix(shown)}${matches}\n`);
  }
  if (unread > 0) {
    const files = unread === 1 ? "1 file" : `${count(unread)} files`;
    io.err(yellow(`grep: ${files} not in the snapshot were not searched`) + "\n");
  }
  return errored ? 2 : matched ? 0 : 1;
}

export function wc(io: Io): number {
  const parsed = options(io, "clmw", "", "usage: wc [-clmw] [file ...]");
  if (parsed === undefined) return 1;
  const picked = ["l", "w", "c", "m"].filter((f) => parsed.flags.has(f));
  const shown = picked.length > 0 ? picked : ["l", "w", "c"];
  const sources = parsed.operands.length > 0 ? parsed.operands : [undefined];
  const totals = new Map<string, number>();
  let status = 0;
  const row = (counts: Map<string, number>, name: string | undefined): string => {
    const numbers = shown.map((f) => String(counts.get(f) ?? 0).padStart(8)).join("");
    return `${numbers}${name === undefined ? "" : ` ${name}`}\n`;
  };
  for (const source of sources) {
    const text = readText(io, source);
    if (text === undefined) {
      status = 1;
      continue;
    }
    const counts = new Map([
      ["l", (text.match(/\n/g) ?? []).length],
      ["w", text.split(/\s+/).filter((w) => w !== "").length],
      ["c", new TextEncoder().encode(text).length],
      ["m", [...text].length],
    ]);
    for (const [f, n] of counts) totals.set(f, (totals.get(f) ?? 0) + n);
    io.out(row(counts, source));
  }
  if (sources.length > 1) io.out(row(totals, "total"));
  return status;
}

export function cd(io: Io): number {
  const session = io.session;
  if (io.args.length > 2) {
    io.err(red("cd: too many arguments") + "\n");
    return 1;
  }
  if (io.args.length === 2) {
    io.err(red(`cd: string not in pwd: ${io.args[0]}`) + "\n");
    return 1;
  }
  let target = io.args[0] ?? HOME;
  if (target === "-") {
    if (session.previousCwd === undefined) {
      io.err(red("cd: OLDPWD not set") + "\n");
      return 1;
    }
    target = session.previousCwd;
    io.out(`${tildePath(target)}\n`);
  }
  const path = resolvePath(session.cwd, target);
  const found = lookup(path);
  if (found.kind === "found" && found.node.kind === "dir") {
    session.previousCwd = session.cwd;
    session.cwd = path;
    return 0;
  }
  if (found.kind === "elided") io.err(yellow(`cd: ${target}: not in the snapshot`) + "\n");
  else if (found.kind === "missing") io.err(red(`cd: no such file or directory: ${target}`) + "\n");
  else io.err(red(`cd: not a directory: ${target}`) + "\n");
  return 1;
}

export function pwd(io: Io): number {
  io.out(`${io.session.cwd}\n`);
  return 0;
}

/** For completion: the names a directory offers, directories marked. */
export function listing(dir: DirNode): { name: string; dir: boolean }[] {
  return entriesOf(dir)
    .map((node) => ({ name: node.name, dir: node.kind === "dir" }))
    .sort((a, b) => byName(a.name, b.name));
}

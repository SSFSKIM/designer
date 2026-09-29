/**
 * `git`, over the commits the snapshot recorded.
 *
 * `log` and `show` print git's own default formats (the full hash, `Author:`, the date in the
 * author's offset, the message indented four spaces), `--oneline` its abbreviated one at the
 * length git chose for this repository. The colours follow the page's roles rather than git's
 * defaults: hashes in cyan, refs in magenta. The author line carries no email, because the
 * snapshot records none. Past the recorded commits the log says where the snapshot ends, and
 * `show` has the `--shortstat` line in place of a diff and says so. `status` is the snapshot's:
 * nothing to commit, since nothing here can change. Every subcommand that would change the
 * repository or reach a remote says which of those it would need, in one line.
 */

import { bold, boldMagenta, count, cyan, grey, magenta, red, yellow } from "./ansi";
import type { Io } from "./io";
import { commits, head, insideRepository, versions, type Commit } from "./snapshot";

const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

/** git's default date, `Tue Sep 29 09:11:46 2026 +0900`, in the offset the commit carries. */
export function gitDate(iso: string): string {
  const m = /^(\d{4})-(\d\d)-(\d\d)T(\d\d:\d\d:\d\d)(?:Z|([+-]\d\d):?(\d\d))$/.exec(iso);
  if (m === null) return iso;
  const [, y, mo, d, time, oh, om] = m as unknown as string[];
  const weekday = new Date(Date.UTC(Number(y), Number(mo) - 1, Number(d))).getUTCDay();
  const offset = oh === undefined ? "+0000" : `${oh}${om}`;
  return `${WEEKDAYS[weekday]} ${MONTHS[Number(mo) - 1]} ${Number(d)} ${time} ${y} ${offset}`;
}

function decoration(refs: string, tty: boolean): string {
  if (refs === "") return "";
  if (!tty) return ` (${refs})`;
  const painted = refs.split(", ").map((ref) => {
    const pointer = /^HEAD -> (.*)$/.exec(ref);
    if (pointer !== null) return `${boldMagenta("HEAD ->")} ${boldMagenta(pointer[1] as string)}`;
    return ref === "HEAD" ? boldMagenta(ref) : magenta(ref);
  });
  return ` ${cyan("(")}${painted.join(cyan(", "))}${cyan(")")}`;
}

function fullEntry(commit: Commit, tty: boolean): string {
  const paint = (f: (s: string) => string, s: string): string => (tty ? f(s) : s);
  let out = `${paint(cyan, `commit ${commit.hash}`)}${decoration(commit.refs, tty)}\n`;
  if (commit.parents.length > 1) {
    out += `Merge: ${commit.parents.map((p) => p.slice(0, head.abbrev)).join(" ")}\n`;
  }
  out += `Author: ${commit.author}\nDate:   ${gitDate(commit.date)}\n\n    ${commit.subject}\n`;
  if (commit.body.length > 0) {
    out += "\n" + commit.body.map((line) => (line === "" ? "\n" : `    ${line}\n`)).join("");
  }
  if (commit.omitted > 0) {
    const lines = commit.omitted === 1 ? "1 more line" : `${commit.omitted} more lines`;
    out += `    ${paint(grey, `[${lines} of this message not in the snapshot]`)}\n`;
  }
  return out;
}

function onelineEntry(commit: Commit, tty: boolean): string {
  const hash = commit.hash.slice(0, head.abbrev);
  return `${tty ? cyan(hash) : hash}${decoration(commit.refs, tty)} ${commit.subject}\n`;
}

const ENDS = (): string =>
  `the snapshot records the last ${commits.length} of the repository's ` +
  `${count(head.commits)} commits`;

function log(io: Io, args: readonly string[]): number {
  let oneline = false;
  let limit = Infinity;
  for (let i = 0; i < args.length; i++) {
    const arg = args[i] as string;
    const short = /^-(\d+)$/.exec(arg) ?? /^-n(\d+)$/.exec(arg) ?? /^--max-count=(\d+)$/.exec(arg);
    if (arg === "--oneline") oneline = true;
    else if (short !== null) limit = Number(short[1]);
    else if (arg === "-n") limit = Number(args[++i]);
    else if (arg === "--decorate" || arg === "--no-color" || arg === "--color") continue;
    else {
      const line = `git log: ${arg} is not simulated; this log takes --oneline, -n N and -N`;
      io.err(yellow(line) + "\n");
      return 128;
    }
  }
  if (Number.isNaN(limit)) {
    io.err(red("fatal: '-n' requires an integer") + "\n");
    return 128;
  }
  const shown = commits.slice(0, Math.max(0, limit));
  shown.forEach((commit, i) => {
    if (oneline) io.out(onelineEntry(commit, io.tty));
    else io.out((i > 0 ? "\n" : "") + fullEntry(commit, io.tty));
  });
  if (shown.length === commits.length && commits.length < head.commits) {
    io.err(grey(`(${ENDS()})`) + "\n");
  }
  return 0;
}

const byHash = new Map(commits.map((c) => [c.hash, c]));

/** `HEAD`, `@`, a branch, or a hash prefix of four or more, among the recorded commits. */
function resolveBase(base: string): Commit | "ambiguous" | undefined {
  if (base === "HEAD" || base === "@") return commits[0];
  const names = (c: Commit): string[] =>
    c.refs.split(", ").map((ref) => ref.replace(/^HEAD -> /, ""));
  const branch = commits.find((c) => names(c).includes(base));
  if (branch !== undefined) return branch;
  if (!/^[0-9a-f]{4,40}$/.test(base)) return undefined;
  const matching = commits.filter((c) => c.hash.startsWith(base));
  return matching.length > 1 ? "ambiguous" : matching[0];
}

/**
 * A revision with git's ancestry steps: `~N` follows N first parents and `^N` takes the Nth
 * parent, through the parents each commit recorded, so `HEAD~3` crosses a merge the way git does
 * rather than counting rows of the log. A step that leaves the recorded commits resolves to
 * nothing, and `show` says the snapshot ends there.
 */
function resolve(rev: string): Commit | "ambiguous" | undefined {
  const match = /^(.+?)((?:~\d*|\^\d*)*)$/.exec(rev);
  if (match === null) return undefined;
  let commit = resolveBase(match[1] as string);
  for (const step of (match[2] as string).match(/~\d*|\^\d*/g) ?? []) {
    if (commit === undefined || commit === "ambiguous") return commit;
    const n = step.length === 1 ? 1 : Number(step.slice(1));
    if (step[0] === "~") {
      for (let i = 0; i < n && commit !== undefined; i++) {
        const parent: string | undefined = commit.parents[0];
        commit = parent === undefined ? undefined : byHash.get(parent);
      }
    } else if (n > 0) {
      const parent = commit.parents[n - 1];
      commit = parent === undefined ? undefined : byHash.get(parent);
    }
  }
  return commit;
}

function show(io: Io, args: readonly string[]): number {
  const revs = args.filter((arg) => !arg.startsWith("-"));
  let status = 0;
  for (const rev of revs.length > 0 ? revs : ["HEAD"]) {
    const commit = resolve(rev);
    if (commit === "ambiguous") {
      io.err(red(`error: short object ID ${rev} is ambiguous`) + "\n");
      status = 128;
      continue;
    }
    if (commit === undefined) {
      const fatal = `fatal: ambiguous argument '${rev}': unknown revision or path not in the ` +
        "working tree.";
      io.err(`${red(fatal)}\n${grey(`(${ENDS()})`)}\n`);
      status = 128;
      continue;
    }
    io.out(fullEntry(commit, io.tty));
    if (commit.stat !== "") io.out(`\n ${commit.stat}\n`);
    io.err(grey("(the diff is not in the snapshot)") + "\n");
  }
  return status;
}

function status(io: Io): number {
  io.out(`On branch ${head.branch}\n`);
  if (head.ahead > 0) {
    const n = head.ahead === 1 ? "1 commit" : `${head.ahead} commits`;
    io.out(`Your branch is ahead of 'origin/${head.branch}' by ${n}.\n`);
    io.out(`  (use "git push" to publish your local commits)\n`);
  } else io.out(`Your branch is up to date with 'origin/${head.branch}'.\n`);
  io.out("\nnothing to commit, working tree clean\n");
  return 0;
}

function branch(io: Io, args: readonly string[]): number {
  const verbose = args.some((a) => /^-[a-z]*v/.test(a));
  const remotes = args.some((a) => /^-[a-z]*[ar]/.test(a));
  const local = !args.some((a) => /^-[a-z]*r/.test(a) && !/a/.test(a));
  const paint = (f: (s: string) => string, s: string): string => (io.tty ? f(s) : s);
  const tip = commits[0];
  const detail =
    verbose && tip !== undefined
      ? ` ${paint(cyan, tip.hash.slice(0, head.abbrev))} ${tip.subject}`
      : "";
  if (local) io.out(`* ${paint(magenta, head.branch)}${detail}\n`);
  if (remotes) {
    io.out(`  ${paint(magenta, "remotes/origin/HEAD")} -> origin/${head.branch}\n`);
    io.out(`  ${paint(magenta, `remotes/origin/${head.branch}`)}\n`);
  }
  return 0;
}

const READ_ONLY = new Set([
  "add", "am", "apply", "bisect", "checkout", "cherry-pick", "clean", "commit", "gc", "init",
  "merge", "mv", "rebase", "reset", "restore", "revert", "rm", "stash", "switch", "tag",
]);
const NETWORK = new Set(["clone", "fetch", "pull", "push"]);
const OTHER = new Set(["blame", "describe", "grep", "reflog", "rev-parse", "shortlog", "worktree"]);

export function git(io: Io): number {
  const [sub, ...args] = io.args;
  if (sub === "--version" || sub === "version") {
    io.out(`${versions.git}\n`);
    return 0;
  }
  if (sub === undefined || sub === "help" || sub === "--help") {
    io.out(
      "usage: git <command> [<args>]\n\n" +
        `The snapshot answers ${bold("log")}, ${bold("show")}, ${bold("status")}, ` +
        `${bold("branch")}, ${bold("remote")} and ${bold("diff")}.\n`,
    );
    return sub === undefined ? 1 : 0;
  }
  if (!insideRepository(io.session.cwd)) {
    io.err(red("fatal: not a git repository (or any of the parent directories): .git") + "\n");
    return 128;
  }
  switch (sub) {
    case "log":
      return log(io, args);
    case "show":
      return show(io, args);
    case "status":
      return status(io);
    case "branch":
      return branch(io, args);
    case "remote":
      if (!args.includes("-v")) io.out("origin\n");
      else io.out(`origin\t${head.remote} (fetch)\norigin\t${head.remote} (push)\n`);
      return 0;
    case "diff":
      return 0;
  }
  const declined = READ_ONLY.has(sub)
    ? "this repository is a read-only snapshot; nothing here can change it"
    : NETWORK.has(sub)
      ? "a simulated shell in a web page has no network to reach a remote with"
      : OTHER.has(sub)
        ? "not simulated here; the snapshot answers log, show, status and branch"
        : undefined;
  if (declined !== undefined) {
    io.err(yellow(`git ${sub}: ${declined}`) + "\n");
    return 1;
  }
  io.err(red(`git: '${sub}' is not a git command. See 'git --help'.`) + "\n");
  return 1;
}

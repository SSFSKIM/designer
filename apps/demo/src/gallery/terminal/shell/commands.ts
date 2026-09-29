/**
 * Every command the shell knows, and `help`, which lists them from the same table so the two
 * cannot disagree.
 *
 * Three kinds of name are not in `help`, and each answers in one honest line: the write
 * operations (the filesystem is a read-only snapshot), the tools that need a machine (an editor,
 * a network, a package manager, a runtime; a page has none of them), and everything else, which
 * zsh would not find either.
 */

import { bold, green, grey, pad, red, width, yellow } from "./ansi";
import { cat, cd, grep, head, ls, pwd, tail, tree, wc } from "./files";
import { git } from "./git";
import { CLEAR, type CommandFn, type Io, type Outcome } from "./io";
import { replay } from "./replay";
import { commits, HOST, insideRepository, recordedRun, USER, versions } from "./snapshot";
import type { ProfileId } from "./types";

type Section = "Files" | "Project" | "This window" | "Shell";

const MACHINE = [
  "brew", "bun", "cargo", "code", "curl", "deno", "docker", "emacs", "go", "htop", "kill",
  "make", "man", "nano", "npm", "npx", "nvim", "open", "ping", "pip", "pip3", "ps", "python",
  "python3", "ruby", "scp", "ssh", "su", "sudo", "top", "vi", "vim", "wget", "yarn",
];
const WRITES = ["chmod", "chown", "cp", "ln", "mkdir", "mv", "rm", "rmdir", "touch"];

function machine(io: Io): number {
  const line = `${io.name}: this terminal is a simulation in a web page and cannot run ${io.name}`;
  io.err(yellow(line) + "\n");
  return 1;
}

function readOnly(io: Io): number {
  const operand = io.args.find((arg) => !arg.startsWith("-"));
  const target = operand === undefined ? "" : `${operand}: `;
  io.err(red(`${io.name}: ${target}Read-only file system`) + "\n");
  return 1;
}

function help(io: Io): number {
  const usageWidth = Math.max(...LISTED.map((entry) => width(entry[3]))) + 2;
  io.out(`${bold("vitrea's simulated shell")}, over a read-only snapshot of the repository.\n`);
  for (const section of ["Files", "Project", "This window", "Shell"] as const) {
    io.out(`\n${bold(section)}\n`);
    for (const [name, , inSection, usage, summary] of LISTED) {
      if (inSection !== section) continue;
      const args = usage.slice(name.length);
      io.out(`  ${pad(name + (io.tty ? grey(args) : args), usageWidth)}${summary}\n`);
    }
  }
  io.out(
    `\nPipes, ${bold(";")}, ${bold("&&")} and ${bold("||")} work, and so does ${bold("*")}; ` +
      "Tab completes, Up and Down walk the history.\n",
  );
  return 0;
}

/**
 * zsh's echo: `-n` drops the newline, and backslash escapes are read as zsh reads them, `\c`
 * ending the output there.
 */
function echo(io: Io): number {
  let args = [...io.args];
  let newline = true;
  while (args[0] === "-n" || args[0] === "-e" || args[0] === "-E") {
    if (args[0] === "-n") newline = false;
    args = args.slice(1);
  }
  const joined = args.join(" ");
  const cut = joined.indexOf("\\c");
  const escapes: Readonly<Record<string, string>> = { n: "\n", t: "\t", "\\": "\\" };
  const text = (cut < 0 ? joined : joined.slice(0, cut)).replace(
    /\\([nt\\])/g,
    (_, c: string) => escapes[c] ?? c,
  );
  io.out(text + (newline && cut < 0 ? "\n" : ""));
  return 0;
}

const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

/** `Tue Sep 29 09:05:12` in the reader's zone, as `date` and `Last login:` open. */
export function clockText(date: Date, utc = false): string {
  const get = (local: () => number, universal: () => number): number =>
    utc ? universal() : local();
  const day = get(() => date.getDay(), () => date.getUTCDay());
  const month = get(() => date.getMonth(), () => date.getUTCMonth());
  const dd = String(get(() => date.getDate(), () => date.getUTCDate())).padStart(2);
  const two = (n: number): string => String(n).padStart(2, "0");
  const time = [
    get(() => date.getHours(), () => date.getUTCHours()),
    get(() => date.getMinutes(), () => date.getUTCMinutes()),
    get(() => date.getSeconds(), () => date.getUTCSeconds()),
  ].map(two);
  return `${WEEKDAYS[day]} ${MONTHS[month]} ${dd} ${time.join(":")}`;
}

function date(io: Io): number {
  const utc = io.args.includes("-u");
  if (io.args.some((arg) => arg !== "-u")) {
    io.err(yellow("date: this shell prints the date and sets nothing; it takes only -u") + "\n");
    return 1;
  }
  const now = io.session.host.now();
  const zone = utc
    ? "UTC"
    : (new Intl.DateTimeFormat("en-US", { timeZoneName: "short" })
        .formatToParts(now)
        .find((part) => part.type === "timeZoneName")?.value ?? "");
  io.out(`${clockText(now, utc)} ${zone} ${utc ? now.getUTCFullYear() : now.getFullYear()}\n`);
  return 0;
}

/**
 * `uname`, honestly: there is no kernel under this shell, so it names what there is instead of
 * claiming Darwin.
 */
function uname(io: Io): number {
  const fields = {
    s: "Simulated",
    n: HOST,
    r: "1.0",
    v: "a shell simulated in a web page, over a snapshot of the vitrea repository",
    m: "browser",
  };
  const flags = io.args.join("").replace(/-/g, "");
  const unknown = flags.replace(/[asnrvm]/g, "");
  if (unknown !== "") {
    io.err(red(`uname: illegal option -- ${unknown[0]}`) + "\nusage: uname [-amnrsv]\n");
    return 1;
  }
  const order = ["s", "n", "r", "v", "m"] as const;
  const picked = flags.includes("a")
    ? order
    : flags === ""
      ? (["s"] as const)
      : order.filter((f) => flags.includes(f));
  io.out(picked.map((f) => fields[f]).join(" ") + "\n");
  return 0;
}

function env(io: Io): number {
  const names = ["HOME", "LANG", "LOGNAME", "OLDPWD", "PWD", "SHELL", "TERM", "USER"];
  for (const name of names) {
    const value = io.session.variable(name);
    if (value !== "") io.out(`${name}=${value}\n`);
  }
  return 0;
}

function which(io: Io): number {
  let status = 0;
  for (const name of io.args) {
    const run = COMMANDS.get(name);
    if (run !== undefined && run !== machine && run !== readOnly) {
      io.out(`${name}: shell built-in command\n`);
    } else {
      io.out(`${name} not found\n`);
      status = 1;
    }
  }
  return status;
}

function history(io: Io): number {
  const past = io.session.history.slice(0, -1);
  const first = Math.max(0, past.length - 16);
  past.slice(first).forEach((line, i) => {
    io.out(`${String(first + i + 1).padStart(5)}  ${line}\n`);
  });
  return 0;
}

function glass(io: Io): number {
  const rows = io.session.host.glassReport();
  if (rows === undefined) {
    io.err(yellow("glass: the runtime has not drawn a frame yet; try again in a moment") + "\n");
    return 1;
  }
  const labelWidth = Math.max(0, ...rows.map((row) => width(row.label))) + 3;
  io.out(`${bold("This window's glass")}\n`);
  for (const row of rows) {
    io.out(`  ${pad(io.tty ? grey(row.label) : row.label, labelWidth)}${row.value}\n`);
  }
  return 0;
}

function profile(io: Io): number {
  const host = io.session.host;
  const profiles = host.profiles();
  const [id, ...rest] = io.args;
  if (id === undefined) {
    const idWidth = Math.max(...profiles.map((p) => width(p.id))) + 3;
    const nameWidth = Math.max(...profiles.map((p) => width(p.name))) + 3;
    for (const p of profiles) {
      const mark = p.active ? (io.tty ? green("*") : "*") : " ";
      const shownId = p.active && io.tty ? bold(p.id) : p.id;
      const note = io.tty ? grey(p.note) : p.note;
      io.out(`${mark} ${pad(shownId, idWidth)}${pad(p.name, nameWidth)}${note}\n`);
    }
    return 0;
  }
  if (rest.length > 0) {
    io.err(red("profile: too many arguments") + "\nusage: profile [id]\n");
    return 1;
  }
  const target = profiles.find((p) => p.id === id);
  if (target === undefined) {
    io.err(red(`profile: no such profile: ${id}`) + "\n");
    io.err(`valid ids: ${profiles.map((p) => p.id).join(", ")}\n`);
    return 1;
  }
  if (target.active) {
    io.out(`Already ${bold(target.name)}.\n`);
    return 0;
  }
  if (!host.setProfile(id as ProfileId)) {
    io.err(red(`profile: could not switch to ${id}`) + "\n");
    return 1;
  }
  io.out(`Switched to ${bold(target.name)}.\n`);
  return 0;
}

function tahoe(io: Io): number {
  const notes = io.session.host.environmentNotes();
  if (notes.length > 0) io.out(notes.join("\n") + "\n");
  return 0;
}

const COLOURS = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"];

/** HSL to RGB, for the one picture on this terminal that is not drawn in the sixteen. */
function hsl(h: number, s: number, l: number): [number, number, number] {
  const f = (n: number): number => {
    const k = (n + h / 30) % 12;
    return Math.round(255 * (l - s * Math.min(l, 1 - l) * Math.max(-1, Math.min(k - 3, 9 - k, 1))));
  };
  return [f(0), f(8), f(4)];
}

function colors(io: Io): number {
  const nameWidth = Math.max(...COLOURS.map((c) => c.length)) + 4;
  COLOURS.forEach((name, i) => {
    const normal = `\x1b[${30 + i}m${name}\x1b[0m`;
    const bright = `\x1b[${90 + i}mbright ${name}\x1b[0m`;
    io.out(`  ${grey(String(30 + i))} ${pad(normal, nameWidth)}`);
    io.out(`${grey(String(90 + i))} ${bright}\n`);
  });
  const cells = Math.max(8, Math.min(io.session.columns() - 4, 72));
  let ramp = "";
  for (let i = 0; i < cells; i++) {
    const [r, g, b] = hsl((i / cells) * 360, 0.75, 0.55);
    ramp += `\x1b[38;2;${r};${g};${b}m█`;
  }
  io.out(`\n  ${ramp}\x1b[0m\n`);
  return 0;
}

function node(io: Io): number {
  if (io.args[0] === "-v" || io.args[0] === "--version") {
    io.out(`${versions.node}\n`);
    return 0;
  }
  return machine(io);
}

/** The package names and directories `--filter` accepts for the one recorded run. */
const RECORDED_FILTERS = [recordedRun.package, `./${recordedRun.cwd}`, recordedRun.cwd];

function pnpm(io: Io): Outcome {
  const args = [...io.args];
  if (args[0] === "-v" || args[0] === "--version") {
    io.out(`${versions.pnpm}\n`);
    return 0;
  }
  if (!insideRepository(io.session.cwd)) {
    io.err(
      red(" ERR_PNPM_NO_IMPORTER_MANIFEST_FOUND ") +
        ` No package.json (or package.yaml, or package.json5) was found in "${io.session.cwd}".\n`,
    );
    return 1;
  }
  const filter = args[0] === "--filter" || args[0] === "-F" ? args.splice(0, 2)[1] : undefined;
  const script = args.join(" ");
  const isTest = script === "test" || script === "t" || script === "run test";
  if (isTest && (filter === undefined || RECORDED_FILTERS.includes(filter))) {
    return replay(io.session.host);
  }
  io.err(
    yellow(
      `pnpm: this shell cannot run pnpm; it replays the one run recorded with the snapshot, ` +
        `pnpm test in ${recordedRun.cwd}`,
    ) + "\n",
  );
  return 1;
}

const exit: CommandFn = (io) => (io.session.exit(), 0);

/** What `help` lists, in its order: the name, the command, its section, usage and summary. */
const LISTED: readonly (readonly [string, CommandFn, Section, string, string])[] = [
  ["ls", ls, "Files", "ls [-alhtS1F] [path ...]", "list a directory"],
  ["cd", cd, "Files", "cd [dir]", "change directory: a path, ~, .. or -"],
  ["pwd", pwd, "Files", "pwd", "print the working directory"],
  ["tree", tree, "Files", "tree [-ad] [-L n] [dir]", "draw a directory as a tree"],
  ["cat", cat, "Files", "cat file ...", "print a file"],
  ["head", head, "Files", "head [-n N] file ...", "the first lines of a file"],
  ["tail", tail, "Files", "tail [-n N] file ...", "the last lines of a file"],
  ["grep", grep, "Files", "grep [-inr] pattern [file ...]", "search the files the snapshot has"],
  ["wc", wc, "Files", "wc [-lwc] [file ...]", "count lines, words and bytes"],
  ["git", git, "Project", "git log|show|status|branch", `the last ${commits.length} commits`],
  ["pnpm", pnpm, "Project", "pnpm test", "replay the recorded test run"],
  ["node", node, "Project", "node -v, pnpm -v", "the versions the snapshot was taken with"],
  ["glass", glass, "This window", "glass", "what this window's glass is drawing now"],
  ["profile", profile, "This window", "profile [id]", "list the profiles, or switch to one"],
  ["tahoe", tahoe, "This window", "tahoe", "the place behind the window"],
  ["colors", colors, "This window", "colors", "the sixteen colours, and a 24-bit ramp"],
  ["help", help, "Shell", "help", "this list"],
  ["clear", (io) => (io.out(CLEAR), 0), "Shell", "clear", "clear the screen (Ctrl-L keeps a line)"],
  ["history", history, "Shell", "history", "what this tab has run"],
  ["echo", echo, "Shell", "echo [-n] text ...", "print text; $HOME, $USER, $PWD expand"],
  ["date", date, "Shell", "date [-u]", "the date and time"],
  ["whoami", (io) => (io.out(`${USER}\n`), 0), "Shell", "whoami", "who you are here"],
  ["hostname", (io) => (io.out(`${HOST}\n`), 0), "Shell", "hostname", "this machine's name"],
  ["uname", uname, "Shell", "uname [-a]", "what this system is"],
  ["exit", exit, "Shell", "exit", "close this tab (or Ctrl-D)"],
];

/** Every name the shell answers to, the listed ones first. */
export const COMMANDS: ReadonlyMap<string, CommandFn> = new Map<string, CommandFn>([
  ...LISTED.map(([name, run]): [string, CommandFn] => [name, run]),
  ["logout", exit],
  ["less", cat],
  ["more", cat],
  ["env", env],
  ["printenv", env],
  ["which", which],
  ...MACHINE.map((name): [string, CommandFn] => [name, machine]),
  ...WRITES.map((name): [string, CommandFn] => [name, readOnly]),
]);

/** The names Tab offers in a command's place: the ones that do something. */
export const COMPLETABLE: readonly string[] = [...COMMANDS]
  .filter(([, run]) => run !== machine && run !== readOnly)
  .map(([name]) => name)
  .sort();

export function commandNotFound(io: Io): number {
  io.err(red(`zsh: command not found: ${io.name}`) + "\n");
  return 127;
}

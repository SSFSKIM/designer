/**
 * The terminal page's simulated shell, driven the way the page drives it: xterm's `onData`
 * strings in, escape sequences out, time through the host's `after`.
 *
 * The writes go into a real xterm (the one the page draws with, headless: the core runs without
 * a DOM), so a redraw is asserted by what the terminal shows and where its cursor is, including
 * what xterm does to wrapped rows on a resize and how cursor-up stops at the top of a short
 * screen. xterm parses writes asynchronously, so every look at the screen goes through `view()`,
 * which waits for the writes so far. The clock is virtual: `advance` runs whatever the shell
 * scheduled, in order, so pacing, interruption and the intro are exact.
 */

import { Terminal } from "@xterm/xterm";
import { describe, expect, it } from "vitest";

import { stripAnsi } from "../src/gallery/terminal/shell/ansi";
import { createShell, REPO } from "../src/gallery/terminal/shell/index";
import { CAP } from "../src/gallery/terminal/shell/replay";
import { commits, lookup, recordedRun } from "../src/gallery/terminal/shell/snapshot";
import type {
  GlassReportRow,
  ProfileId,
  ProfileSummary,
  ShellHost,
} from "../src/gallery/terminal/shell/types";

// eslint-disable-next-line no-control-regex -- the palette audit reads every SGR written.
const SGR = /\x1b\[([0-9;]*)m/g;

/** What the terminal shows once it has parsed everything written to it. */
interface View {
  /** Every row from the top of the scrollback to the cursor's row or the last written one. */
  readonly lines: readonly string[];
  /** The cursor, its row counted from the top of the scrollback. */
  readonly cursor: { readonly x: number; readonly y: number };
  /** The cursor's row and the `n - 1` above it. */
  tail(n?: number): readonly string[];
}

const PROFILES: readonly Omit<ProfileSummary, "active">[] = [
  { id: "clear-dark", name: "Clear Dark", note: "clear glass, the night behind it" },
  { id: "clear-light", name: "Clear Light", note: "clear glass, the day behind it" },
  { id: "regular-dark", name: "Regular Dark", note: "regular glass, dark" },
  { id: "regular-light", name: "Regular Light", note: "regular glass, light" },
];

interface Options {
  readonly columns?: number;
  readonly rows?: number;
  readonly reduced?: boolean;
  readonly intro?: readonly string[];
  readonly cwd?: string;
  readonly glass?: readonly GlassReportRow[];
}

function harness(options: Options = {}) {
  let now = 0;
  let order = 0;
  let columns = options.columns ?? 80;
  let rows = options.rows ?? 24;
  const timers: { at: number; order: number; run: () => void }[] = [];
  const writes: { at: number; data: string }[] = [];
  const term = new Terminal({ cols: columns, rows, scrollback: 10_000, allowProposedApi: true });
  let parsed: Promise<void> = Promise.resolve();
  let active: ProfileId = "clear-dark";
  const switched: string[] = [];
  let closed = 0;
  const host: ShellHost = {
    write(data) {
      writes.push({ at: now, data });
      parsed = new Promise((done) => term.write(data, done));
    },
    columns: () => columns,
    rows: () => rows,
    now: () => new Date(Date.UTC(2026, 8, 30, 3, 0, 0) + now),
    after(ms, run) {
      const timer = { at: now + ms, order: order++, run };
      timers.push(timer);
      return () => {
        const i = timers.indexOf(timer);
        if (i >= 0) timers.splice(i, 1);
      };
    },
    reducedMotion: () => options.reduced ?? false,
    glassReport: () => options.glass,
    profiles: () => PROFILES.map((p) => ({ ...p, active: p.id === active })),
    setProfile(id) {
      if (!PROFILES.some((p) => p.id === id)) return false;
      active = id;
      switched.push(id);
      return true;
    },
    environmentNotes: () => ["Lake Tahoe from the east shore, at dusk.", "Relief: USGS 3DEP."],
    closeSession: () => {
      closed++;
    },
  };
  const shell = createShell(host, { name: "vitrea", cwd: options.cwd ?? REPO, intro: options.intro ?? [] });
  const advance = (ms: number): void => {
    const until = now + ms;
    for (;;) {
      timers.sort((a, b) => a.at - b.at || a.order - b.order);
      const next = timers[0];
      if (next === undefined || next.at > until) break;
      timers.shift();
      now = next.at;
      next.run();
    }
    now = until;
  };
  const view = async (): Promise<View> => {
    await parsed;
    const buffer = term.buffer.active;
    const cursor = { x: buffer.cursorX, y: buffer.baseY + buffer.cursorY };
    const lines: string[] = [];
    for (let i = 0; i < buffer.length; i++) lines.push(buffer.getLine(i)?.translateToString(true) ?? "");
    while (lines.length > cursor.y + 1 && lines.at(-1) === "") lines.pop();
    return { lines, cursor, tail: (n = 1) => lines.slice(cursor.y - n + 1, cursor.y + 1) };
  };
  /** Everything written since `mark`, joined. */
  const since = (mark: number): string => writes.slice(mark).map((w) => w.data).join("");
  const run = (line: string): string => {
    const mark = writes.length;
    shell.input(`${line}\r`);
    return since(mark);
  };
  /** What a command wrote: after its own line, before the prompt that followed it. */
  const output = (line: string): string => {
    const raw = run(line);
    return raw.slice(raw.indexOf("\r\n") + 2, raw.lastIndexOf("\r\x1b[J"));
  };
  return {
    shell,
    writes,
    advance,
    view,
    since,
    run,
    output,
    pending: () => timers.length,
    switched,
    closed: () => closed,
    /** The page's order: the terminal takes its new size, then the shell is told. */
    async resize(toColumns: number, toRows = rows) {
      await parsed;
      columns = toColumns;
      rows = toRows;
      term.resize(toColumns, toRows);
      shell.resize(toColumns, toRows);
    },
  };
}

const PROMPT = "vitrea main % ";
/** A prompt with nothing typed. xterm trims only cells never written, so its blank stays. */
const IDLE = PROMPT;

/** The rows from the last one a prompt starts, to the cursor's: the line being edited. */
function region(v: View, prompt = PROMPT): readonly string[] {
  let at = v.lines.length - 1;
  while (at > 0 && !(v.lines[at] as string).startsWith(prompt)) at--;
  return v.lines.slice(at);
}
const plain = stripAnsi;
const started = (options: Options = {}) => {
  const h = harness(options);
  h.shell.start();
  return h;
};

describe("the session's start", () => {
  it("greets like macOS, says it is simulated, and prompts in the repository", async () => {
    const h = started();
    const v = await h.view();
    const [login, note, prompt] = v.lines;
    expect(login).toMatch(/^Last login: \w{3} \w{3} [ \d]\d \d\d:\d\d:\d\d on ttys000$/);
    expect(note).toMatch(/^A simulated shell over a vitrea repository snapshot/);
    expect(note).toMatch(/help/);
    expect(prompt).toBe(IDLE);
    expect(v.cursor).toEqual({ x: PROMPT.length, y: 2 });
    // The directory in bold blue, the branch in magenta.
    expect(h.since(0)).toContain("\x1b[1;34mvitrea\x1b[0m \x1b[35mmain\x1b[0m % ");
  });
});

describe("line editing", () => {
  it("redraws an edit in the middle of the line and leaves the cursor on it", async () => {
    const h = started();
    h.shell.input("echo hello");
    h.shell.input("\x1b[D\x1b[D\x1b[D");
    h.shell.input("X");
    let v = await h.view();
    expect(v.tail()).toEqual([`${PROMPT}echo heXllo`]);
    expect(v.cursor.x).toBe(PROMPT.length + 8);
    h.shell.input("\x7f\x1b[3~");
    v = await h.view();
    expect(v.tail()).toEqual([`${PROMPT}echo helo`]);
    expect(v.cursor.x).toBe(PROMPT.length + 7);
    const keys = [
      ["\x1b[H", 0], ["\x1b[F", 9], ["\x1bOH", 0], ["\x1bOF", 9], ["\x1b[1~", 0], ["\x1b[4~", 9],
      ["\x01", 0], ["\x05", 9], ["\x02", 8], ["\x06", 9],
    ] as const;
    for (const [key, x] of keys) {
      h.shell.input(key);
      expect((await h.view()).cursor.x, JSON.stringify(key)).toBe(PROMPT.length + x);
    }
    expect(plain(h.run(""))).toContain("helo");
  });

  it("kills, yanks and moves by words", async () => {
    const h = started();
    h.shell.input("echo one two three");
    h.shell.input("\x17");
    expect((await h.view()).tail()).toEqual([`${PROMPT}echo one two `]);
    h.shell.input("\x1bb\x0b");
    expect((await h.view()).tail()).toEqual([`${PROMPT}echo one `]);
    h.shell.input("\x19");
    expect((await h.view()).tail()).toEqual([`${PROMPT}echo one two `]);
    h.shell.input("\x01\x1bf");
    expect((await h.view()).cursor.x).toBe(PROMPT.length + 4);
    h.shell.input("\x1b[1;3C");
    expect((await h.view()).cursor.x).toBe(PROMPT.length + 8);
    h.shell.input("\x15");
    const v = await h.view();
    expect(v.tail()).toEqual([`${PROMPT} two `]);
    expect(v.cursor.x).toBe(PROMPT.length);
  });

  it("wraps a long line across rows and keeps the cursor arithmetic across the wrap", async () => {
    const h = started({ columns: 30 });
    const top = (await h.view()).cursor.y;
    const text = "echo abcdefghijklmnopqrstuvwxyz0123456789";
    h.shell.input(text);
    const full = PROMPT + text;
    let v = await h.view();
    expect(v.tail(2)).toEqual([full.slice(0, 30), full.slice(30)]);
    expect(v.cursor).toEqual({ x: full.length - 30, y: top + 1 });
    h.shell.input("\x01");
    expect((await h.view()).cursor).toEqual({ x: PROMPT.length, y: top });
    h.shell.input("Z");
    const edited = PROMPT + "Z" + text;
    v = await h.view();
    expect(v.lines.slice(top)).toEqual([edited.slice(0, 30), edited.slice(30)]);
    expect(v.cursor).toEqual({ x: PROMPT.length + 1, y: top });
    h.shell.input("\x05");
    expect((await h.view()).cursor).toEqual({ x: edited.length - 30, y: top + 1 });
    // Deleting back across the row boundary leaves nothing behind on the row below.
    h.shell.input("\x7f".repeat(edited.length - 29));
    v = await h.view();
    expect(v.lines.slice(top)).toEqual([edited.slice(0, 29)]);
    expect(v.cursor).toEqual({ x: 29, y: top });
  });

  it("puts the cursor on the next row when the line fills its row exactly", async () => {
    const h = started({ columns: 30 });
    const top = (await h.view()).cursor.y;
    h.shell.input("x".repeat(30 - PROMPT.length));
    expect((await h.view()).cursor).toEqual({ x: 0, y: top + 1 });
    h.shell.input("y");
    let v = await h.view();
    expect(v.tail(2)).toEqual([PROMPT + "x".repeat(16), "y"]);
    expect(v.cursor).toEqual({ x: 1, y: top + 1 });
    h.shell.input("\x7f\x7f");
    v = await h.view();
    expect(v.lines.slice(top)).toEqual([PROMPT + "x".repeat(15)]);
    expect(v.cursor).toEqual({ x: 29, y: top });
    // Enter on a line that filled its row starts the output on the row below, with no gap.
    h.shell.input("x\r");
    const below = (await h.view()).lines.slice(top + 1);
    expect(below.slice(0, -1).join("")).toBe(`zsh: command not found: ${"x".repeat(16)}`);
    expect(below.at(-1)).toBe(IDLE);
  });

  it("counts a Hangul syllable as two cells", async () => {
    const h = started();
    h.shell.input("echo ");
    h.shell.input("안녕하세요");
    expect((await h.view()).cursor.x).toBe(PROMPT.length + 5 + 10);
    h.shell.input("\x1b[D\x1b[D");
    expect((await h.view()).cursor.x).toBe(PROMPT.length + 5 + 6);
    h.shell.input("!");
    let v = await h.view();
    expect(v.tail()).toEqual([`${PROMPT}echo 안녕하!세요`]);
    expect(v.cursor.x).toBe(PROMPT.length + 5 + 7);
    h.shell.input("\x7f\x7f");
    v = await h.view();
    expect(v.tail()).toEqual([`${PROMPT}echo 안녕세요`]);
    expect(v.cursor.x).toBe(PROMPT.length + 5 + 4);
    expect(plain(h.run(""))).toContain("안녕세요");
  });

  it("moves a wide character that does not fit whole to the next row, and back", async () => {
    const h = started({ columns: 20 });
    const top = (await h.view()).cursor.y;
    h.shell.input("abcde");
    expect((await h.view()).cursor).toEqual({ x: 19, y: top });
    h.shell.input("한");
    let v = await h.view();
    expect(v.tail(2)).toEqual([`${PROMPT}abcde`, "한"]);
    expect(v.cursor).toEqual({ x: 2, y: top + 1 });
    h.shell.input("\x1b[D");
    expect((await h.view()).cursor).toEqual({ x: 0, y: top + 1 });
    // With one cell fewer before it, the syllable fits the first row's last two cells.
    h.shell.input("\x7f");
    v = await h.view();
    expect(v.lines.slice(top, top + 1)).toEqual([`${PROMPT}abcd한`]);
    expect(v.cursor).toEqual({ x: 18, y: top });
  });

  it("keeps a combining accent with its letter", async () => {
    const h = started();
    h.shell.input("cafe");
    h.shell.input("\u0301");
    expect((await h.view()).cursor.x).toBe(PROMPT.length + 4);
    h.shell.input("\x1b[D!");
    expect(plain(h.run(""))).toContain("caf!e\u0301");
  });

  it("abandons the line on Ctrl-C and clears the screen on Ctrl-L, keeping the line", async () => {
    const h = started();
    h.shell.input("echo never");
    h.shell.input("\x03");
    expect((await h.view()).tail(2)).toEqual([`${PROMPT}echo never^C`, IDLE]);
    h.shell.input("echo kept\x1b[D\x0c");
    const v = await h.view();
    expect(v.tail()).toEqual([`${PROMPT}echo kept`]);
    // The line is on the screen's top row now.
    expect(v.cursor.y - (v.lines.length - 1)).toBe(0);
    expect(v.cursor.x).toBe(PROMPT.length + 8);
  });
});

describe("resize, against what xterm does to wrapped rows", () => {
  // The greeting above the prompt reflows with each width, which moves the prompt's row; the
  // assertions read the line from wherever its prompt now is.
  it("redraws a wrapped line at a wider and a narrower width without leaving a copy", async () => {
    const h = started({ columns: 30 });
    const line = `${PROMPT}echo ${"x".repeat(19)}`;
    h.shell.input("echo " + "x".repeat(19));
    await h.resize(60);
    let v = await h.view();
    expect(region(v)).toEqual([line]);
    expect(v.lines.filter((row) => row.startsWith(PROMPT))).toHaveLength(1);
    expect(v.cursor.x).toBe(line.length);
    await h.resize(20);
    v = await h.view();
    expect(region(v)).toEqual([line.slice(0, 20), line.slice(20, 40)]);
    expect(v.lines.filter((row) => row.startsWith(PROMPT))).toHaveLength(1);
    h.shell.input("\x01Z");
    v = await h.view();
    const edited = `${PROMPT}Zecho ${"x".repeat(19)}`;
    expect(region(v)).toEqual([edited.slice(0, 20), edited.slice(20, 40)]);
    expect(v.cursor).toEqual({ x: PROMPT.length + 1, y: v.lines.length - 2 });
  });

  it("keeps a line that filled its row exactly as one line through a resize", async () => {
    const h = started({ columns: 30 });
    h.shell.input("x".repeat(16));
    await h.resize(20);
    await h.resize(40);
    const v = await h.view();
    expect(region(v)).toEqual([PROMPT + "x".repeat(16)]);
    expect(v.cursor).toEqual({ x: 30, y: v.lines.length - 1 });
  });

  it("takes no more than a short screen can show, so a redraw never loses its first row", async () => {
    const h = started({ columns: 30, rows: 5 });
    h.shell.input("a".repeat(150));
    h.shell.input("\x7f");
    const v = await h.view();
    const shown = v.lines.filter((row) => row.startsWith(IDLE));
    expect(shown).toHaveLength(1);
    // Five rows of thirty cells: the prompt, then what fits before the last cell of the last row.
    const typed = v.lines.slice(v.lines.indexOf(shown[0] as string)).join("");
    expect(typed).toBe(PROMPT + "a".repeat(5 * 30 - PROMPT.length - 2));
  });

  it("keeps every character when the screen shrinks below the line, and refuses more", async () => {
    const h = started({ columns: 30, rows: 10 });
    h.shell.input("b".repeat(100));
    await h.resize(30, 3);
    // What the rows-shrink pushed into the scrollback stays there; the screen is redrawn whole.
    let screen = (await h.view()).lines.slice(-3);
    expect(screen.filter((row) => row.startsWith(PROMPT)).length).toBeLessThanOrEqual(1);
    expect(screen.join("").endsWith("b".repeat(60))).toBe(true);
    // Nothing typed is lost to the smaller screen: Enter still runs the whole line.
    h.shell.input("\x7f\x7f");
    screen = (await h.view()).lines.slice(-3);
    expect(screen.filter((row) => row.startsWith(PROMPT))).toHaveLength(0);
    expect(screen.join("")).toContain("b".repeat(60));
    expect(plain(h.run(""))).toContain(`command not found: ${"b".repeat(98)}`);
    // And the full-field rule still refuses new text past the last row.
    await h.resize(30, 10);
    h.shell.input("c".repeat(400));
    const typed = region(await h.view()).join("");
    expect(typed.length).toBe(10 * 30 - 1);
  });
});

describe("history", () => {
  it("walks back and forth, and returns to the line being typed", async () => {
    const h = started();
    h.run("echo one");
    h.run("echo two");
    h.shell.input("ec");
    h.shell.input("\x1b[A");
    expect((await h.view()).tail()).toEqual([`${PROMPT}echo two`]);
    h.shell.input("\x1b[A\x1b[A");
    expect((await h.view()).tail()).toEqual([`${PROMPT}echo one`]);
    h.shell.input("\x1b[B");
    expect((await h.view()).tail()).toEqual([`${PROMPT}echo two`]);
    h.shell.input("\x1b[B");
    expect((await h.view()).tail()).toEqual([`${PROMPT}ec`]);
    h.shell.input("\x15");
    const listed = plain(h.run("history")).split("\r\n").slice(1, 3);
    expect(listed).toEqual(["    1  echo one", "    2  echo two"]);
  });
});

describe("completion", () => {
  it("completes a directory, lists an ambiguity on the second Tab, then the rest", async () => {
    const h = started();
    h.shell.input("cd pack\t");
    expect((await h.view()).tail()).toEqual([`${PROMPT}cd packages/`]);
    h.shell.input("c\t");
    expect((await h.view()).tail()).toEqual([`${PROMPT}cd packages/c`]);
    h.shell.input("\t");
    const listed = (await h.view()).tail(3);
    expect(listed[1]).toMatch(/^calibration\/\s+core\/$/);
    expect(listed[2]).toBe(`${PROMPT}cd packages/c`);
    h.shell.input("o\t");
    expect((await h.view()).tail()).toEqual([`${PROMPT}cd packages/core/`]);
    h.run("");
    expect((await h.view()).tail()).toEqual(["core main % "]);
  });

  it("completes command names, subcommands and profile ids", async () => {
    const h = started();
    h.shell.input("hist\t");
    expect((await h.view()).tail()).toEqual([`${PROMPT}history `]);
    h.shell.input("\x15git lo\t");
    expect((await h.view()).tail()).toEqual([`${PROMPT}git log `]);
    h.shell.input("\x15profile clear-l\t");
    expect((await h.view()).tail()).toEqual([`${PROMPT}profile clear-light `]);
  });

  it("escapes a blank in a completed path, and the parser reads it back", async () => {
    const h = started();
    h.shell.input("ls Fig\t");
    expect((await h.view()).tail()).toEqual([`${PROMPT}ls Figma\\ Design/`]);
    const out = plain(h.run(""));
    expect(out).not.toMatch(/No such file/);
    const figma = lookup(`${REPO}/Figma Design`);
    expect(figma.kind).toBe("found");
    if (figma.kind === "found" && figma.node.kind === "dir") {
      const first = [...(figma.node.entries?.keys() ?? [])].sort()[0] as string;
      expect(out).toContain(first);
    }
  });
});

describe("the filesystem", () => {
  it("changes directory and lists what the snapshot holds there", async () => {
    const h = started();
    h.run("cd packages");
    expect((await h.view()).tail()).toEqual(["packages main % "]);
    const out = h.run("ls");
    expect(out).toContain("\x1b[1;34mcore\x1b[0m");
    expect(plain(h.run("cd -"))).toContain("~/vitrea");
    expect((await h.view()).tail()).toEqual([IDLE]);
    h.run("cd ~; echo $PWD");
    expect((await h.view()).tail(2)).toEqual(["/Users/guest", "~ % "]);
    expect(plain(h.run("pwd"))).toContain("/Users/guest\r\n");
    expect(plain(h.run("cd vitrea/nope"))).toContain("cd: no such file or directory: vitrea/nope");
    h.run("cd vitrea/packages/core/../..");
    expect((await h.view()).tail()).toEqual([IDLE]);
  });

  it("lays ls out in columns for the terminal's width now, one per line into a pipe", async () => {
    const h = started({ columns: 160 });
    const wide = plain(h.run("ls")).split("\r\n").length;
    await h.resize(40);
    const narrow = plain(h.run("ls")).split("\r\n").length;
    expect(narrow).toBeGreaterThan(wide);
    const piped = h.output("ls | cat");
    expect(piped).not.toContain("\x1b[");
    expect(piped.split("\r\n")).toContain("packages");
  });

  it("prints the long format with modes, links, sizes and dates", () => {
    const h = started();
    const out = plain(h.run("ls -l"));
    expect(out).toMatch(/^total \d+$/m);
    expect(out).toMatch(/^drwxr-xr-x +\d+ guest {2}staff +\d+ \w{3} [ \d]\d ( \d{4}|\d\d:\d\d) packages$/m);
    const readme = lookup(`${REPO}/README.md`);
    if (readme.kind !== "found" || readme.node.kind !== "file") throw new Error("README.md is missing");
    expect(out).toMatch(new RegExp(`^-rw-r--r-- +1 guest {2}staff +${readme.node.size} .* README\\.md$`, "m"));
    expect(plain(h.run("ls -a"))).toMatch(/\.gitignore/);
    expect(plain(h.run("ls"))).not.toMatch(/\.gitignore/);
  });

  it("reads the files the snapshot carries and says which it does not", () => {
    const h = started();
    const readme = lookup(`${REPO}/README.md`);
    if (readme.kind !== "found" || readme.node.kind !== "file") throw new Error("README.md is missing");
    const firstLine = (readme.node.text ?? "").split("\n")[0] as string;
    expect(plain(h.run("cat README.md"))).toContain(firstLine);
    expect(plain(h.run("head -n 2 package.json")).split("\r\n").slice(1, 3)).toEqual(['{', '  "name": "vitrea-monorepo",']);
    const unread = plain(h.run("cat packages/core/src/index.ts"));
    expect(unread).toMatch(/cat: packages\/core\/src\/index\.ts: not in the snapshot \([\d,]+ bytes\)/);
    expect(plain(h.run("cat nope"))).toContain("cat: nope: No such file or directory");
    expect(plain(h.run("cat packages"))).toContain("cat: packages: Is a directory");
  });

  it("says a directory it elided is not in the snapshot, with its counts", () => {
    const h = started();
    const results = lookup(`${REPO}/packages/calibration/results`);
    if (results.kind !== "found" || results.node.kind !== "dir") throw new Error("results is missing");
    const elided = [...(results.node.entries?.values() ?? [])].find((n) => n.kind === "dir" && n.entries === undefined);
    expect(elided).toBeDefined();
    const out = plain(h.run(`ls packages/calibration/results/${elided?.name}`));
    expect(out).toMatch(/not in the snapshot \([\d,]+ files/);
    expect(plain(h.run(`cat packages/calibration/results/${elided?.name}/x.json`))).toMatch(/not in the snapshot/);
  });

  it("draws a tree that agrees with ls", () => {
    const h = started();
    const names = plain(h.run("ls -1 packages")).split("\r\n").slice(1, -1);
    const tree = plain(h.run("tree -L 1 packages")).split("\r\n");
    expect(tree[1]).toBe("packages");
    expect(tree.slice(2, 2 + names.length).map((line) => line.slice(4))).toEqual(names);
    expect(tree[1 + names.length]).toMatch(/^└── /);
    expect(tree).toContain(`${names.length} directories, 0 files`);
    // With no level, the whole of a small directory.
    const whole = plain(h.output("tree packages/policy")).split("\r\n");
    expect(whole).toContain("│   ├── index.ts");
    expect(whole.at(-2)).toMatch(/^\d+ directories, \d+ files$/);
  });

  it("expands a pattern against the snapshot, and says when nothing matches", () => {
    const h = started();
    const manifests = plain(h.run("ls packages/*/package.json | wc -l"));
    const packages = plain(h.run("ls -1 packages")).split("\r\n").slice(1, -1);
    expect(manifests).toContain(`${String(packages.length).padStart(8)}\r\n`);
    expect(plain(h.run("echo nothing*here"))).toContain("zsh: no matches found: nothing*here");
    expect(plain(h.run("echo 'nothing*here'"))).toContain("nothing*here\r\n");
    // A trailing slash asks for directories, and keeps the slash.
    const dirs = plain(h.output("cd packages/core; echo */")).trim().split(" ");
    expect(dirs).toEqual(["src/", "test/"]);
    expect(plain(h.output("cd ../..; ls -1d packages/*/")).split("\r\n")).toContain("packages/core/");
  });

  it("expands the variables a person would echo", () => {
    const h = started();
    expect(plain(h.run("echo $HOME $USER $SHELL $PWD"))).toContain(`/Users/guest guest /bin/zsh ${REPO}\r\n`);
    expect(plain(h.run(`echo '$HOME' "\${USER}"`))).toContain("$HOME guest\r\n");
    // Read when the command runs, not when the line was typed.
    const out = plain(h.output("cd packages; echo $PWD; frob; echo $?"));
    expect(out).toContain(`${REPO}/packages\r\n`);
    expect(out.endsWith("\r\n127\r\n")).toBe(true);
  });
});

describe("paste", () => {
  it("runs each line a return ends, and goes on with the rest", async () => {
    const h = started();
    const mark = h.writes.length;
    h.shell.input("pwd\recho two\rech");
    const out = plain(h.since(mark));
    expect(out).toContain(`${REPO}\r\n`);
    expect(out.indexOf(REPO)).toBeLessThan(out.indexOf("two\r\n"));
    expect((await h.view()).tail()).toEqual([`${PROMPT}ech`]);
  });

  it("holds what was pasted after a replay until the replay ends", () => {
    const h = started();
    const mark = h.writes.length;
    h.shell.input("pnpm test\rpwd\r");
    expect(plain(h.since(mark))).not.toContain(`${REPO}\r\n`);
    h.advance(CAP + 1000);
    const out = plain(h.since(mark));
    const lastRecorded = plain((recordedRun.lines.at(-1) as readonly [number, string])[1]);
    expect(out.indexOf(lastRecorded)).toBeGreaterThan(0);
    expect(out.indexOf(`${REPO}\r\n`)).toBeGreaterThan(out.indexOf(lastRecorded));
  });
});

describe("the recorded run", () => {
  it("replays every recorded line at a pace scaled to at most CAP", () => {
    const h = started();
    const mark = h.writes.length;
    h.shell.input("pnpm test\r");
    h.advance(CAP / 3);
    const early = plain(h.since(mark));
    h.advance(CAP);
    const out = plain(h.since(mark));
    for (const [, line] of recordedRun.lines) expect(out).toContain(plain(line));
    expect(early.length).toBeLessThan(out.length);
    const prompts = h.writes.filter((w) => plain(w.data).includes(PROMPT));
    expect(prompts.at(-1)?.at).toBeLessThanOrEqual(CAP);
    expect(h.pending()).toBe(0);
  });

  it("stops at Ctrl-C and writes nothing more", async () => {
    const h = started();
    h.shell.input("pnpm test\r");
    h.advance(300);
    h.shell.input("ls\r");
    const typedWhileRunning = h.writes.length;
    h.advance(10);
    h.shell.input("\x03");
    expect((await h.view()).tail(2)).toEqual(["^C", IDLE]);
    expect(h.pending()).toBe(0);
    const mark = h.writes.length;
    h.advance(CAP * 2);
    expect(h.writes.length).toBe(mark);
    // The keys typed while it ran were dropped, not queued behind the interrupt.
    expect(plain(h.since(typedWhileRunning))).not.toContain("packages");
  });

  it("takes a Ctrl-C that arrives in the same string as the Enter that started it", async () => {
    const h = started();
    h.shell.input("pnpm test\r\x03echo after\r");
    expect(h.pending()).toBe(0);
    expect((await h.view()).tail(2)).toEqual(["^C", IDLE]);
    h.advance(CAP * 2);
    expect(plain(h.since(0))).not.toContain("after\r\n");
  });

  it("writes the whole run at once under reduced motion", async () => {
    const h = started({ reduced: true });
    const out = plain(h.run("pnpm test"));
    expect(out).toContain(plain((recordedRun.lines.at(-1) as readonly [number, string])[1]));
    expect(h.pending()).toBe(0);
    expect((await h.view()).tail()).toEqual([IDLE]);
  });

  it("finds no package.json outside the repository", () => {
    const h = started({ cwd: "/Users/guest" });
    expect(plain(h.run("pnpm test"))).toContain("ERR_PNPM_NO_IMPORTER_MANIFEST_FOUND");
    expect(plain(h.run("git status"))).toContain("fatal: not a git repository");
  });
});

describe("the intro", () => {
  const INTRO = ["ls", "git log --oneline -n 3"];

  it("types each command at a seeded, human pace, runs it, and leaves an idle prompt", async () => {
    const timeline = async (): Promise<{ at: number; data: string }[]> => {
      const h = started({ intro: INTRO });
      h.advance(20_000);
      expect(h.pending()).toBe(0);
      expect((await h.view()).tail()).toEqual([IDLE]);
      const written = [...h.writes];
      h.shell.input("\x1b[A");
      expect((await h.view()).tail()).toEqual([`${PROMPT}git log --oneline -n 3`]);
      return written;
    };
    const first = await timeline();
    expect(await timeline()).toEqual(first);
    // Each key of "git log …" is one redraw; the gaps between them are the typing pace.
    const typed = (w: { data: string }): boolean => {
      const shown = /% (g[^\r\n]*)$/.exec(plain(w.data));
      return shown !== null && "git log --oneline -n 3".startsWith(shown[1] as string);
    };
    const keys = first.filter(typed);
    const gaps = keys.slice(1).map((w, i) => w.at - (keys[i] as { at: number }).at);
    expect(gaps.length).toBeGreaterThan(10);
    for (const gap of gaps) {
      expect(gap).toBeGreaterThanOrEqual(35);
      expect(gap).toBeLessThanOrEqual(70);
    }
    expect(new Set(gaps).size).toBeGreaterThan(3);
  });

  it("stops at the reader's first key, erases the half-typed line and takes the key", async () => {
    const h = started({ intro: INTRO });
    h.advance(1000);
    expect((await h.view()).tail()[0]).toMatch(/^vitrea main % l/);
    h.shell.input("p");
    expect((await h.view()).tail()).toEqual([`${PROMPT}p`]);
    expect(h.pending()).toBe(0);
    h.shell.input("wd\r");
    expect((await h.view()).tail(2)).toEqual([REPO, IDLE]);
  });

  it("interrupts a replay it started when the reader presses a key", async () => {
    const h = started({ intro: ["pnpm test", "ls"] });
    h.advance(900 + 9 * 70 + 480 + 400);
    expect(plain(h.since(0))).toContain("Replaying pnpm test");
    h.shell.input("e");
    expect((await h.view()).tail(2)).toEqual(["^C", `${PROMPT}e`]);
    expect(h.pending()).toBe(0);
  });

  it("appears whole, with its output, under reduced motion", async () => {
    const h = started({ reduced: true, intro: INTRO });
    expect(h.pending()).toBe(0);
    const lines = (await h.view()).lines;
    expect(lines).toContain(`${PROMPT}ls`);
    expect(lines).toContain(`${PROMPT}git log --oneline -n 3`);
    expect(lines.at(-1)).toBe(IDLE);
  });
});

describe("the window", () => {
  it("lists the profiles and switches through the host", () => {
    const h = started();
    const listed = plain(h.run("profile")).split("\r\n").slice(1, 5);
    expect(listed[0]).toMatch(/^\* clear-dark +Clear Dark +clear glass/);
    expect(listed[1]).toMatch(/^ {2}clear-light/);
    expect(plain(h.run("profile regular-light"))).toContain("Switched to Regular Light.");
    expect(h.switched).toEqual(["regular-light"]);
    const bad = plain(h.run("profile blue"));
    expect(bad).toContain("profile: no such profile: blue");
    expect(bad).toContain("clear-dark, clear-light, regular-dark, regular-light");
    expect(h.switched).toEqual(["regular-light"]);
  });

  it("reports the glass as an aligned table, or says no frame has drawn yet", () => {
    expect(plain(started().run("glass"))).toContain("has not drawn a frame yet");
    const glass = [
      { label: "Renderer", value: "webgpu" },
      { label: "Material", value: "macOS 27 clear, dark" },
      { label: "Sampling group", value: "gpu-texture" },
    ];
    const lines = plain(started({ glass }).run("glass")).split("\r\n").slice(1, 5);
    expect(lines[0]).toBe("This window's glass");
    const columns = lines.slice(1).map((line, i) => line.indexOf(glass[i]?.value as string));
    expect(new Set(columns).size).toBe(1);
  });

  it("prints the page's notes on the environment", () => {
    expect(plain(started().run("tahoe"))).toContain("Lake Tahoe from the east shore, at dusk.\r\nRelief: USGS 3DEP.\r\n");
  });
});

describe("honesty", () => {
  it("answers what it cannot do in one line, and does not know what zsh would not", () => {
    const h = started();
    expect(plain(h.run("vim README.md"))).toContain("vim: this terminal is a simulation in a web page and cannot run vim");
    expect(plain(h.run("rm -rf packages"))).toContain("rm: packages: Read-only file system");
    expect(plain(h.run("echo hi > notes.txt"))).toContain("zsh: read-only file system: notes.txt");
    expect(h.output("echo quiet > /dev/null")).toBe("");
    // A redirect silences the stream it names, and only that one.
    expect(plain(h.output("echo visible 2>/dev/null"))).toBe("visible\r\n");
    expect(h.output("cat nope 2>/dev/null")).toBe("");
    expect(plain(h.output("cat nope >/dev/null"))).toContain("cat: nope: No such file or directory");
    expect(h.output("cat nope &>/dev/null")).toBe("");
    expect(plain(h.output("echo shown 2>&1"))).toBe("shown\r\n");
    expect(plain(h.run("frobnicate"))).toContain("zsh: command not found: frobnicate");
    expect(plain(h.run("git push"))).toMatch(/git push: .*no network/);
    expect(plain(h.run("uname -a"))).not.toMatch(/Darwin/);
    expect(plain(h.run("false && echo no || echo yes"))).toContain("zsh: command not found: false");
  });

  it("prints the log in git's formats and says where the snapshot ends", () => {
    const h = started();
    const log = plain(h.run("git log -n 2"));
    expect(log).toMatch(/^commit [0-9a-f]{40} \(HEAD -> main/m);
    expect(log).toMatch(/^Author: \S/m);
    expect(log).toMatch(/^Date: {3}\w{3} \w{3} \d{1,2} \d\d:\d\d:\d\d \d{4} [+-]\d{4}$/m);
    expect(log.match(/^commit /gm)).toHaveLength(2);
    const oneline = plain(h.run("git log --oneline -3")).split("\r\n").slice(1, 4);
    for (const line of oneline) expect(line).toMatch(/^[0-9a-f]{7,12} /);
    expect(plain(h.run("git log --oneline"))).toMatch(/the snapshot records the last \d+ of the repository's [\d,]+ commits/);
    const show = plain(h.run("git show HEAD~1"));
    expect(show).toMatch(/^commit [0-9a-f]{40}/m);
    expect(show).toContain("(the diff is not in the snapshot)");
    expect(plain(h.run("git status"))).toContain("nothing to commit, working tree clean");
  });

  // A merge whose second parent is the next row of the log is where counting rows and following
  // first parents part ways; the snapshot may hold none, after a quiet stretch of history.
  const merge = commits.find((c, i) => c.parents.length > 1 && commits[i + 1]?.hash === c.parents[1]);
  it.skipIf(merge === undefined)("walks HEAD~N and ^N through parents, not rows of the log", () => {
    const h = started();
    const m = merge as (typeof commits)[number];
    const shown = (rev: string): string | undefined =>
      /^commit ([0-9a-f]{40})/m.exec(plain(h.output(`git show ${rev}`)))?.[1];
    expect(shown(`${m.hash}^2`)).toBe(m.parents[1]);
    const first = m.parents[0] as string;
    if (commits.some((c) => c.hash === first)) expect(shown(`${m.hash}~1`)).toBe(first);
    else expect(plain(h.run(`git show ${m.hash}~1`))).toContain("unknown revision");
    expect(plain(h.output(`git show ${m.hash}`))).toMatch(/^Merge: [0-9a-f]+ [0-9a-f]+$/m);
  });
});

describe("the palette", () => {
  /** SGR parameters the page does not allow: dim, inverse, 256/24-bit, and every background. */
  const forbidden = (text: string): string[] => {
    const found: string[] = [];
    for (const [, params] of text.matchAll(SGR)) {
      for (const code of (params as string).split(";").map(Number)) {
        if (code === 2 || code === 7 || code === 38 || code === 48 || (code >= 40 && code <= 47) || (code >= 100 && code <= 107)) {
          found.push(params as string);
        }
      }
    }
    return found;
  };

  it("writes only the sixteen colours and bold, everywhere but the colors ramp", () => {
    const h = started({ glass: [{ label: "Renderer", value: "webgpu" }], intro: ["ls"] });
    h.advance(10_000);
    for (const line of [
      "help", "ls -la", "ls -F packages", "tree -L 2 packages/core", "cat README.md", "cat nope",
      "grep -n vitest package.json", "grep -r workspace packages", "git log -n 5", "git log --oneline",
      "git show HEAD", "git branch -av", "git status", "git frob", "profile", "profile nope",
      "glass", "tahoe", "history", "date", "uname -a", "vim", "rm x", "foo", "echo 'unclosed",
      "cd nope", "ls packages/calibration/results | head", "node -v",
    ]) {
      h.run(line);
    }
    h.run("pnpm test");
    h.advance(CAP + 100);
    h.shell.input("pnpm test\r");
    h.advance(500);
    h.shell.input("\x03");
    h.shell.input("hist\t\t");
    expect(forbidden(h.since(0))).toEqual([]);

    const reduced = started({ reduced: true, intro: ["pnpm test"] });
    expect(forbidden(reduced.since(0))).toEqual([]);
  });

  it("draws colors' names in their own colours, and its ramp alone in 24-bit", () => {
    const out = started().run("colors");
    for (const [i, name] of ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"].entries()) {
      expect(out).toContain(`\x1b[${30 + i}m${name}\x1b[0m`);
      expect(out).toContain(`\x1b[${90 + i}mbright ${name}\x1b[0m`);
    }
    const extended = [...out.matchAll(SGR)]
      .map((m) => m[1] as string)
      .filter((p) => /(^|;)(38|48)(;|$)/.test(p));
    expect(extended.length).toBeGreaterThan(8);
    for (const params of extended) expect(params).toMatch(/^38;2;\d+;\d+;\d+$/);
  });
});

describe("the session's end", () => {
  it("closes on exit and on Ctrl-D at an empty line, and then ignores input", async () => {
    const h = started();
    h.run("exit");
    expect(h.closed()).toBe(1);
    const mark = h.writes.length;
    h.shell.input("ls\r");
    expect(h.writes.length).toBe(mark);

    const d = started();
    d.shell.input("ab\x01\x04");
    expect((await d.view()).tail()).toEqual([`${PROMPT}b`]);
    expect(d.closed()).toBe(0);
    d.shell.input("\x05\x15\x04");
    expect(d.closed()).toBe(1);
  });

  it("cancels everything it scheduled on dispose", () => {
    const h = started({ intro: ["pnpm test"] });
    h.advance(1500);
    h.shell.dispose();
    expect(h.pending()).toBe(0);
  });
});

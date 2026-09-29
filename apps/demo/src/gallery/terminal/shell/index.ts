/**
 * The simulated shell: everything between a key arriving and the characters written back.
 *
 * `input` receives xterm's `onData` strings, which may hold one key, an escape sequence, a run of
 * typed or composed text, or a whole paste. They are read key by key; the edits a string makes are
 * drawn once at its end, so a long paste costs one redraw, and a return inside it runs the line so
 * far and goes on with the rest. A command that takes time (the replayed test run) holds the rest
 * of the string until it finishes, as a terminal holds typeahead, and while it runs only Ctrl-C
 * does anything; Ctrl-C drops the held text, as a real interrupt flushes the input queue.
 *
 * The intro types its commands through the same line editor and runs them through the same path
 * as Enter, at a seeded, human pace, so it looks like the reader's own shell and ends in the state
 * theirs would. Any key stops it: a half-typed line is erased, a command it is replaying is
 * interrupted, and the key is then handled as if the intro had never been there (except a Ctrl-C
 * that interrupted a replay, which is spent doing so). All time goes through `host.after`.
 */

import {
  boldBlue,
  clusters,
  columns as layoutColumns,
  directory,
  magenta,
  red,
  stripAnsi,
} from "./ansi";
import { clockText, commandNotFound, COMMANDS } from "./commands";
import { complete } from "./complete";
import { LineEditor } from "./editor";
import { CLEAR, type Io, type Job, type Session } from "./io";
import { expand, parse, segmentPattern, type Expanded, type Pipeline } from "./parse";
import { byName, head, HOME, HOST, insideRepository, lookup, resolvePath, USER } from "./snapshot";
import type { Shell, ShellHost, ShellOptions } from "./types";

export type * from "./types";
export { HOME, REPO } from "./snapshot";

/** The intro's pace, in milliseconds. */
const INTRO = {
  /** Before the first key of the first command. */
  first: 900,
  /** Each key: this much, plus up to `spread` more, drawn from the seeded sequence. */
  key: 35,
  spread: 35,
  /** With the line typed, before Enter. */
  beforeEnter: 480,
  /** From the prompt returning to the next command's first key. */
  between: 1100,
} as const;

/** A small, fast, seeded generator (mulberry32): the intro types the same way on every load. */
function seeded(text: string): () => number {
  let seed = 2166136261;
  for (let i = 0; i < text.length; i++) seed = Math.imul(seed ^ text.charCodeAt(i), 16777619);
  return () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

type KeyName =
  | "enter" | "backspace" | "delete" | "left" | "right" | "home" | "end" | "up" | "down"
  | "word-left" | "word-right" | "kill-start" | "kill-end" | "kill-word-back" | "kill-word-forward"
  | "yank" | "interrupt" | "eof" | "clear" | "tab" | "ignore";

type Key = { readonly kind: "text"; readonly text: string } | { readonly kind: KeyName };

const CONTROL: Readonly<Record<string, KeyName>> = {
  "\r": "enter", "\n": "enter", "\x7f": "backspace", "\b": "backspace", "\x01": "home",
  "\x05": "end", "\x02": "left", "\x06": "right", "\x10": "up", "\x0e": "down",
  "\x15": "kill-start", "\x0b": "kill-end", "\x17": "kill-word-back", "\x19": "yank",
  "\x03": "interrupt", "\x04": "eof", "\x0c": "clear", "\t": "tab",
};

const CSI: Readonly<Record<string, KeyName>> = {
  A: "up", B: "down", C: "right", D: "left", H: "home", F: "end",
  "1~": "home", "7~": "home", "4~": "end", "8~": "end", "3~": "delete",
  "1;3C": "word-right", "1;3D": "word-left", "1;5C": "word-right", "1;5D": "word-left",
  "1;9C": "word-right", "1;9D": "word-left",
};

const ALT: Readonly<Record<string, KeyName>> = {
  b: "word-left", f: "word-right", d: "kill-word-forward", "\x7f": "kill-word-back",
  "\b": "kill-word-back",
};

const KILLS = {
  "kill-start": "start",
  "kill-end": "end",
  "kill-word-back": "word-back",
  "kill-word-forward": "word-forward",
} as const;

/** The key at `data[at]`, and how many UTF-16 units it took. */
function readKey(data: string, at: number): [Key, number] {
  const c = data[at] as string;
  if (c === "\x1b") {
    const next = data[at + 1];
    if (next === "[") {
      // Parameters, then one final byte; a sequence cut off at the end of the string is dropped.
      let end = at + 2;
      while (end < data.length && /[0-9;?>]/.test(data[end] as string)) end++;
      const final = data[end];
      if (final === undefined) return [{ kind: "ignore" }, data.length - at];
      const params = data.slice(at + 2, end);
      const plain = params === "" || params === "1";
      const name = final === "~" ? `${params}~` : plain ? final : `${params}${final}`;
      return [{ kind: CSI[name] ?? "ignore" }, end + 1 - at];
    }
    if (next === "O" && at + 2 < data.length) {
      return [{ kind: CSI[data[at + 2] as string] ?? "ignore" }, 3];
    }
    if (next === undefined) return [{ kind: "ignore" }, 1];
    return [{ kind: ALT[next] ?? "ignore" }, 2];
  }
  if (c === "\r" && data[at + 1] === "\n") return [{ kind: "enter" }, 2];
  const control = CONTROL[c];
  if (control !== undefined) return [{ kind: control }, 1];
  if (c < " ") return [{ kind: "ignore" }, 1];
  let end = at;
  while (end < data.length && (data[end] as string) >= " " && data[end] !== "\x7f") end++;
  return [{ kind: "text", text: data.slice(at, end) }, end - at];
}

export function createShell(host: ShellHost, options: ShellOptions): Shell {
  let columns = Math.max(1, host.columns());
  const editor = new LineEditor(columns, host.rows());
  const history: string[] = [];
  const timers = new Set<() => void>();
  let historyIndex = 0;
  let draft = "";
  let killed = "";
  let lastStatus = 0;
  let tabbed = false;
  let atLineStart = true;
  let started = false;
  let closed = false;
  let exitRequested = false;
  /** The job streaming now, and what to do when the reader interrupts it. */
  let running: { cancel(): void } | undefined;
  let typeahead = "";
  let intro: { cancel: (() => void) | undefined } | undefined;

  const startCwd = lookup(resolvePath("/", options.cwd));
  const session: Session = {
    host,
    cwd: startCwd.kind === "found" && startCwd.node.kind === "dir" ? startCwd.node.path : HOME,
    previousCwd: undefined,
    history,
    columns: () => columns,
    variable,
    exit: () => {
      exitRequested = true;
    },
  };

  function variable(name: string): string {
    switch (name) {
      case "HOME":
        return HOME;
      case "USER":
      case "LOGNAME":
        return USER;
      case "SHELL":
        return "/bin/zsh";
      case "PWD":
        return session.cwd;
      case "OLDPWD":
        return session.previousCwd ?? "";
      case "TERM":
        return "xterm-256color";
      case "LANG":
        return "en_US.UTF-8";
      case "HOST":
        return HOST;
      case "?":
        return String(lastStatus);
      default:
        return "";
    }
  }

  function schedule(ms: number, run: () => void): () => void {
    const cancel = host.after(Math.max(0, ms), () => {
      timers.delete(cancel);
      run();
    });
    timers.add(cancel);
    return () => {
      timers.delete(cancel);
      cancel();
    };
  }

  /** Command output: `\n` becomes the terminal's `\r\n`, and the shell notes where it ended. */
  function emit(text: string): void {
    if (text === "") return;
    host.write(text.replace(/\r?\n/g, "\r\n"));
    atLineStart = text.endsWith("\n") || text.endsWith(CLEAR);
  }

  function prompt(): string {
    const cwd = session.cwd;
    const name = cwd === HOME ? "~" : cwd === "/" ? "/" : cwd.slice(cwd.lastIndexOf("/") + 1);
    return `${boldBlue(name)}${insideRepository(cwd) ? ` ${magenta(head.branch)}` : ""} % `;
  }

  function showPrompt(): void {
    // zsh's PROMPT_SP: output that ended mid-line does not leave the prompt beside it.
    if (!atLineStart) host.write("\r\n");
    atLineStart = true;
    historyIndex = history.length;
    draft = "";
    host.write(editor.begin(prompt()));
  }

  // -------------------------------------------------------------------------------------------
  // Running a line.

  /** Every path a pattern word names in the snapshot, sorted; empty when none. */
  function glob(word: Expanded): string[] {
    const wild = word.wild as readonly boolean[];
    const segments: { text: string; wild: boolean[] }[] = [{ text: "", wild: [] }];
    for (let i = 0; i < word.text.length; i++) {
      const c = word.text[i] as string;
      const last = segments[segments.length - 1] as { text: string; wild: boolean[] };
      if (c === "/") segments.push({ text: "", wild: [] });
      else {
        last.text += c;
        last.wild.push(wild[i] === true);
      }
    }
    const absolute = word.text.startsWith("/");
    let paths = [{ shown: absolute ? "/" : "", abs: absolute ? "/" : session.cwd }];
    for (const segment of segments) {
      if (segment.text === "") continue;
      const next: typeof paths = [];
      for (const path of paths) {
        const join = (name: string): { shown: string; abs: string } => {
          const bare = path.shown === "" || path.shown.endsWith("/");
          const shown = bare ? path.shown + name : `${path.shown}/${name}`;
          return { shown, abs: resolvePath(path.abs, name) };
        };
        if (!segment.wild.includes(true)) {
          const found = lookup(resolvePath(path.abs, segment.text));
          if (found.kind === "found") next.push(join(segment.text));
          continue;
        }
        const found = lookup(path.abs);
        const dir = found.kind === "found" && found.node.kind === "dir" ? found.node : undefined;
        if (dir?.entries === undefined) continue;
        const pattern = segmentPattern(segment.text, segment.wild);
        for (const node of dir.entries.values()) {
          if (node.name.startsWith(".") && !segment.text.startsWith(".")) continue;
          if (pattern.test(node.name)) next.push(join(node.name));
        }
      }
      paths = next;
    }
    // A trailing slash asks for directories, and keeps its slash, as `ls -d */` expects.
    if (!word.text.endsWith("/")) return paths.map((path) => path.shown).sort(byName);
    return paths
      .filter((path) => {
        const found = lookup(path.abs);
        return found.kind === "found" && found.node.kind === "dir";
      })
      .map((path) => (path.shown.endsWith("/") ? path.shown : `${path.shown}/`))
      .sort(byName);
  }

  /**
   * One pipeline. Each command's output feeds the next without colour; standard error, and the
   * last command's output, go to the screen in the order they were written. A redirect to a file
   * is refused before its command runs, as zsh refuses one it cannot open.
   */
  function runPipeline(pipeline: Pipeline, next: (status: number) => void): void {
    let screen = "";
    let stdin: string | undefined;
    let status = 0;
    const last = pipeline.commands.length - 1;
    for (const [index, command] of pipeline.commands.entries()) {
      const argv: string[] = [];
      let failed = false;
      for (const word of command.words.map((w) => expand(w, variable))) {
        if (word.wild === undefined) argv.push(word.text);
        else {
          const matches = glob(word);
          if (matches.length === 0) {
            screen += red(`zsh: no matches found: ${word.text}`) + "\n";
            failed = true;
            break;
          }
          argv.push(...matches);
        }
      }
      let outToNull = false;
      let errToNull = false;
      for (const redirect of command.redirects) {
        const target = expand(redirect.target, variable).text;
        if (target === "/dev/null") {
          outToNull ||= redirect.stream !== "err";
          errToNull ||= redirect.stream !== "out";
        } else if (!failed) {
          screen += red(`zsh: read-only file system: ${target}`) + "\n";
          failed = true;
        }
      }
      const [name, ...args] = argv;
      if (failed || name === undefined) {
        status = failed ? 1 : 0;
        stdin = "";
        continue;
      }
      const tty = index === last && !outToNull;
      let piped = "";
      const io: Io = {
        name,
        args,
        stdin,
        tty,
        session,
        out: (text) => {
          if (tty) screen += text;
          else piped += text;
        },
        err: (text) => {
          if (!errToNull) screen += text;
        },
      };
      const outcome = (COMMANDS.get(name) ?? commandNotFound)(io);
      if (typeof outcome === "number") status = outcome;
      else if (tty) {
        emit(screen);
        startJob(outcome, next);
        return;
      } else {
        piped = outcome.text;
        status = 0;
      }
      stdin = outToNull ? "" : stripAnsi(piped);
    }
    emit(screen);
    next(status);
  }

  function startJob(job: Job, next: (status: number) => void): void {
    let finished = false;
    const cancel = job.start(emit, (status) => {
      finished = true;
      running = undefined;
      next(status);
    });
    if (!finished) running = { cancel };
  }

  function runLine(line: string, then: () => void): void {
    const parsed = parse(line, HOME);
    if (!parsed.ok) {
      emit(red(`zsh: ${parsed.error}`) + "\n");
      lastStatus = 1;
      then();
      return;
    }
    const step = (index: number): void => {
      const pipeline = parsed.pipelines[index];
      if (pipeline === undefined || exitRequested) return then();
      const skip =
        (pipeline.join === "&&" && lastStatus !== 0) ||
        (pipeline.join === "||" && lastStatus === 0);
      if (skip) return step(index + 1);
      runPipeline(pipeline, (status) => {
        lastStatus = status;
        step(index + 1);
      });
    };
    step(0);
  }

  /**
   * Enter: the line leaves the editor, joins the history and runs; when it has finished, the
   * prompt returns, `after` runs (the intro's next step), and any typeahead is read.
   */
  function submit(after?: () => void): void {
    const line = editor.text;
    host.write(editor.finish());
    atLineStart = true;
    if (line.trim() !== "" && history[history.length - 1] !== line) history.push(line);
    runLine(line, () => {
      if (exitRequested) return close();
      showPrompt();
      after?.();
      const held = typeahead;
      typeahead = "";
      if (held !== "") handle(held);
    });
  }

  function interrupt(): void {
    running?.cancel();
    running = undefined;
    typeahead = "";
    emit("^C\n");
    lastStatus = 130;
    showPrompt();
  }

  function close(): void {
    closed = true;
    cancelAll();
    host.closeSession();
  }

  function cancelAll(): void {
    for (const cancel of [...timers]) cancel();
    timers.clear();
    running?.cancel();
    running = undefined;
    intro = undefined;
  }

  // -------------------------------------------------------------------------------------------
  // Keys.

  function listCandidates(names: readonly { name: string; dir: boolean }[]): void {
    const text = editor.text;
    const cursor = clusters(editor.beforeCursor).length;
    host.write(editor.finish());
    const shown = names.map(({ name, dir }) => (dir ? `${directory(name)}/` : name));
    emit(layoutColumns(shown, columns).join("\n") + "\n");
    host.write(editor.begin(prompt(), text, cursor));
  }

  function tab(): boolean {
    const before = editor.beforeCursor;
    const profiles = host.profiles().map((p) => p.id);
    const result = complete(before, session.cwd, profiles);
    if (result === undefined) return false;
    const typed = before.slice(result.from);
    const wasTabbed = tabbed;
    tabbed = !result.unique;
    if (result.replacement !== typed) {
      editor.replaceBeforeCursor(clusters(before.slice(0, result.from)).length, result.replacement);
      return true;
    }
    if (!result.unique && wasTabbed) listCandidates(result.candidates);
    return false;
  }

  function walkHistory(direction: -1 | 1): boolean {
    const to = historyIndex + direction;
    if (to < 0 || to > history.length) return false;
    if (historyIndex === history.length) draft = editor.text;
    historyIndex = to;
    editor.setText(to === history.length ? draft : (history[to] as string));
    return true;
  }

  /** Reads `data` key by key into the editor, drawing once at the end. */
  function handle(data: string): void {
    let dirty = false;
    const draw = (): void => {
      if (dirty) host.write(editor.render());
      dirty = false;
    };
    let at = 0;
    while (at < data.length) {
      if (closed) return;
      if (running !== undefined) {
        // The line just entered started a replay. What followed it in the same string waits for
        // it, unless there is a Ctrl-C among it, which interrupts now and drops the rest.
        const rest = data.slice(at);
        if (rest.includes("\x03")) interrupt();
        else typeahead += rest;
        return;
      }
      const [key, length] = readKey(data, at);
      at += length;
      const wasTab = key.kind === "tab";
      switch (key.kind) {
        case "text":
          editor.insert(key.text);
          dirty = true;
          break;
        case "enter":
          draw();
          submit();
          break;
        case "backspace":
          dirty = editor.backspace() || dirty;
          break;
        case "delete":
          dirty = editor.deleteForward() || dirty;
          break;
        case "left":
          dirty = editor.left() || dirty;
          break;
        case "right":
          dirty = editor.right() || dirty;
          break;
        case "home":
          dirty = editor.home() || dirty;
          break;
        case "end":
          dirty = editor.end() || dirty;
          break;
        case "word-left":
          dirty = editor.wordLeft() || dirty;
          break;
        case "word-right":
          dirty = editor.wordRight() || dirty;
          break;
        case "up":
          dirty = walkHistory(-1) || dirty;
          break;
        case "down":
          dirty = walkHistory(1) || dirty;
          break;
        case "kill-start":
        case "kill-end":
        case "kill-word-back":
        case "kill-word-forward": {
          const removed = editor.kill(KILLS[key.kind]);
          if (removed !== "") {
            killed = removed;
            dirty = true;
          }
          break;
        }
        case "yank":
          editor.insert(killed);
          dirty = killed !== "" || dirty;
          break;
        case "interrupt":
          draw();
          host.write(editor.finish("^C"));
          atLineStart = true;
          showPrompt();
          break;
        case "eof":
          if (editor.isEmpty) {
            draw();
            host.write(editor.finish());
            close();
            return;
          }
          dirty = editor.deleteForward() || dirty;
          break;
        case "clear":
          host.write("\x1b[H\x1b[2J" + editor.redrawAtTop());
          dirty = false;
          break;
        case "tab":
          draw();
          dirty = tab();
          break;
        case "ignore":
          break;
      }
      if (!wasTab) tabbed = false;
    }
    draw();
  }

  // -------------------------------------------------------------------------------------------
  // The intro.

  function runIntro(): void {
    const commands = options.intro;
    if (commands.length === 0) return;
    if (host.reducedMotion()) {
      // No typing: each command appears whole with its output, before the reader can type.
      for (const command of commands) {
        if (closed) return;
        editor.setText(command);
        host.write(editor.render());
        submit();
      }
      return;
    }
    const state: { cancel: (() => void) | undefined } = { cancel: undefined };
    intro = state;
    const type = (index: number): void => {
      const command = commands[index];
      if (command === undefined) {
        intro = undefined;
        return;
      }
      const random = seeded(command);
      const keys = clusters(command);
      let k = 0;
      const press = (): void => {
        const key = keys[k++];
        if (key === undefined) {
          state.cancel = schedule(INTRO.beforeEnter, () => {
            state.cancel = undefined;
            submit(() => {
              if (intro === state) state.cancel = schedule(INTRO.between, () => type(index + 1));
            });
          });
          return;
        }
        editor.insert(key);
        host.write(editor.render());
        state.cancel = schedule(INTRO.key + random() * INTRO.spread, press);
      };
      state.cancel = schedule(index === 0 ? INTRO.first : INTRO.key, press);
    };
    type(0);
  }

  /** The reader pressed something during the intro, which ends it. Returns what to handle. */
  function stopIntro(data: string): string {
    intro?.cancel?.();
    intro = undefined;
    if (running !== undefined) {
      interrupt();
      return data.startsWith("\x03") ? data.slice(1) : data;
    }
    if (!editor.isEmpty) {
      editor.setText("");
      host.write(editor.render());
    }
    return data;
  }

  return {
    start() {
      if (started) return;
      started = true;
      emit(`Last login: ${clockText(host.now())} on ttys000\n`);
      emit("A simulated shell over a vitrea repository snapshot; help lists what it can do.\n");
      showPrompt();
      runIntro();
    },
    input(data) {
      if (!started || closed) return;
      if (intro !== undefined) data = stopIntro(data);
      if (running !== undefined) {
        if (data.includes("\x03")) interrupt();
        return;
      }
      handle(data);
    },
    resize(newColumns, newRows) {
      columns = Math.max(1, newColumns);
      if (!closed) host.write(editor.resize(columns, newRows));
    },
    dispose() {
      closed = true;
      cancelAll();
    },
  };
}

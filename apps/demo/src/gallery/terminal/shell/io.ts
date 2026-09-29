/**
 * What a command is handed and what it hands back.
 *
 * A command writes text with `\n` line endings to `out` (its standard output, which is the
 * terminal or the next command's input) and `err` (always the terminal, as a real shell's standard
 * error is). It knows whether its output is a terminal, because the real tools change shape when
 * it is not: `ls` goes to one name per line, and nothing is coloured. Almost every command runs to
 * completion before returning its exit status; the one that takes time returns a `Job` the shell
 * streams and can interrupt.
 */

import type { ShellHost } from "./types";

export interface Session {
  readonly host: ShellHost;
  cwd: string;
  previousCwd: string | undefined;
  /** Every line this session ran, oldest first, the running one last. */
  readonly history: readonly string[];
  columns(): number;
  variable(name: string): string;
  /** Asks the shell to end the session once this command's output is written. */
  exit(): void;
}

export interface Io {
  readonly name: string;
  readonly args: readonly string[];
  /** The previous command's output in a pipeline, already without colour. */
  readonly stdin: string | undefined;
  readonly tty: boolean;
  readonly session: Session;
  out(text: string): void;
  err(text: string): void;
}

export interface Job {
  /**
   * Streams the output through `write` and calls `done` once when it has all been written, unless
   * the returned cancel runs first. `done` may be called before `start` returns.
   */
  start(write: (text: string) => void, done: (status: number) => void): () => void;
  /** Everything it prints, without colour, for when its output is not the terminal. */
  readonly text: string;
}

export type Outcome = number | Job;
export type CommandFn = (io: Io) => Outcome;

/** Clears the screen and its scrollback, as macOS `clear` does. */
export const CLEAR = "\x1b[H\x1b[2J\x1b[3J";

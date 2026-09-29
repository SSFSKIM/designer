/**
 * The contract between the terminal page and its shell.
 *
 * The page cannot run a real shell: it is a static site, and a browser page has no process to
 * spawn. So the shell is simulated, over a snapshot of this repository taken at build time
 * (`content.json`, written by `scripts/build-terminal-content.mjs`), and it is honest about being
 * simulated wherever a command would need a real machine. The page owns the terminal emulator
 * (xterm.js), the glass and the environment; the shell owns everything that happens between a
 * key and the characters written back, and never touches the DOM.
 *
 * Colour is always one of the sixteen ANSI colours (SGR 30–37, 90–97) plus bold, never 24-bit
 * and never a background, dim or inverse: the page designs those sixteen colours against the
 * glass the terminal is drawn on, and a colour the shell chose for itself could not be held to a
 * contrast floor. The one exception is `colors`, which draws a 24-bit ramp as a picture, not as
 * text.
 */

/** A terminal profile: which glass the window is made of, and which colour scheme. */
export type GlassKind = "clear" | "regular";
export type Scheme = "dark" | "light";
export type ProfileId = `${GlassKind}-${Scheme}`;

export interface ProfileSummary {
  readonly id: ProfileId;
  /** The profile's display name, e.g. "Clear Dark". */
  readonly name: string;
  /** One line on what the profile draws. */
  readonly note: string;
  readonly active: boolean;
}

/** One row of the `glass` command's report, read from the runtime at the moment it runs. */
export interface GlassReportRow {
  readonly label: string;
  readonly value: string;
}

/** Everything the shell may ask of the page. */
export interface ShellHost {
  /** Writes to the terminal. Line endings are "\r\n"; the string may carry ANSI sequences. */
  write(data: string): void;
  /** The terminal's current size in cells. */
  columns(): number;
  rows(): number;
  /** The clock, so a test can pin it. */
  now(): Date;
  /**
   * Schedules work, so a test can drive time. Returns a cancel function. Everything the shell
   * does later (typing, replayed output) goes through here, never through setTimeout directly.
   */
  after(ms: number, run: () => void): () => void;
  /** Whether the reader asked for reduced motion: no typing animation, output at once. */
  reducedMotion(): boolean;
  /** The runtime's live report on the window's glass, or undefined before its first frame. */
  glassReport(): readonly GlassReportRow[] | undefined;
  /** The four profiles, the active one marked. */
  profiles(): readonly ProfileSummary[];
  /** Switches profile; false when the id is not one of the four. */
  setProfile(id: ProfileId): boolean;
  /** The lines the `tahoe` command prints about the environment, written by the page. */
  environmentNotes(): readonly string[];
  /** Closes this session's tab (`exit`); the page decides what happens to the last one. */
  closeSession(): void;
}

export interface ShellOptions {
  /** The session's name, shown on its tab: "vitrea" for the first. */
  readonly name: string;
  /** The working directory the session starts in, an absolute path in the snapshot. */
  readonly cwd: string;
  /**
   * Commands the shell types and runs by itself when it starts, before handing over to the
   * reader; any key the reader presses stops the typing and gives them the prompt. Empty for a
   * quiet start.
   */
  readonly intro: readonly string[];
}

export interface Shell {
  /** Prints the greeting and the first prompt, and starts the intro if there is one. */
  start(): void;
  /** Receives xterm's `onData`: typed text, pasted text, and key sequences. */
  input(data: string): void;
  /** Tells the shell the terminal was resized, so layouts like `ls` follow the new width. */
  resize(columns: number, rows: number): void;
  /** Cancels anything scheduled. */
  dispose(): void;
}

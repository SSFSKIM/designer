/**
 * One session's terminal: an xterm.js instance on its DOM renderer, its grid fitted to its box,
 * wired to one simulated shell (`shell/`).
 *
 * The DOM renderer, not the WebGL one: its rows are text the audit can measure and a screen
 * reader can reach, and it has none of the WebGL renderer's transparency faults (thin glyphs, an
 * opaque box behind dim or italic cells). Its background is transparent, so the glass under it is
 * the background. A hidden session keeps its box (`visibility`, never `display`), because xterm
 * measures its cells from it.
 */

import { FitAddon } from "@xterm/addon-fit";
import { Terminal, type ITheme } from "@xterm/xterm";
import "@xterm/xterm/css/xterm.css";
import { useEffect, useLayoutEffect, useRef, type ReactNode } from "react";

import { createShell } from "./shell";
import type { GlassReportRow, ProfileId, ProfileSummary, Shell } from "./shell/types";

export interface SessionSpec {
  readonly id: string;
  readonly name: string;
  readonly cwd: string;
  readonly intro: readonly string[];
}

/** What a session asks of the page, beyond the terminal it owns. */
export interface SessionServices {
  readonly reducedMotion: () => boolean;
  readonly glassReport: () => readonly GlassReportRow[] | undefined;
  readonly profiles: () => readonly ProfileSummary[];
  readonly setProfile: (id: ProfileId) => boolean;
  readonly environmentNotes: () => readonly string[];
}

export const MONO_FACE =
  'ui-monospace, "SF Mono", SFMono-Regular, Menlo, Monaco, "Cascadia Mono", Consolas, "Liberation Mono", monospace';

export function TerminalView(props: {
  readonly session: SessionSpec;
  readonly active: boolean;
  /**
   * Bumped by the page when the person explicitly chooses a session: a click on its tab, the
   * selected one included, or a session closing onto it. The active session's terminal takes
   * focus then, and when it mounts active (the page's first session, a new one). An arrow key in
   * the tablist changes `active` alone, so focus stays in the tabs, as the tabs pattern asks.
   */
  readonly focusKey: number;
  /**
   * Whether the glass has drawn from the map. The shell starts only then, so an intro's `glass`
   * reports the material on the screen, not the moment before the texture arrived.
   */
  readonly ready: boolean;
  readonly theme: ITheme;
  readonly cursorBlink: boolean;
  readonly services: SessionServices;
  readonly onSize: (id: string, columns: number, rows: number) => void;
  readonly onClose: (id: string) => void;
}): ReactNode {
  const { session, active, theme, cursorBlink } = props;
  const element = useRef<HTMLDivElement>(null);
  const terminal = useRef<Terminal | null>(null);
  const pending = useRef<(() => void) | null>(null);
  const latest = useRef(props);
  latest.current = props;

  useLayoutEffect(() => {
    const el = element.current;
    if (el === null) return;
    const term = new Terminal({
      allowTransparency: true,
      theme: latest.current.theme,
      fontFamily: MONO_FACE,
      fontSize: 13,
      lineHeight: 1.25,
      fontWeight: "500",
      fontWeightBold: "700",
      cursorBlink: latest.current.cursorBlink,
      cursorStyle: "bar",
      cursorWidth: 2,
      scrollback: 3000,
      macOptionIsMeta: true,
      screenReaderMode: true,
      drawBoldTextInBrightColors: false,
      minimumContrastRatio: 1,
    });
    const fit = new FitAddon();
    term.loadAddon(fit);
    term.open(el);
    terminal.current = term;

    // Shift-Tab leaves the terminal backward; Escape and then Tab leave it forward. Tab alone
    // stays the shell's, for completion. Returning false hands the key to the browser.
    let escaped = false;
    term.attachCustomKeyEventHandler((event) => {
      if (event.type !== "keydown") return true;
      if (event.key === "Tab" && (event.shiftKey || escaped)) {
        escaped = false;
        return false;
      }
      escaped = event.key === "Escape";
      return true;
    });

    let shell: Shell | undefined;
    let closed = false;
    const services = (): SessionServices => latest.current.services;
    const start = (intro: readonly string[]): Shell =>
      createShell(
        {
          write: (data) => term.write(data),
          columns: () => term.cols,
          rows: () => term.rows,
          now: () => new Date(),
          after: (ms, run) => {
            const timer = window.setTimeout(run, ms);
            return () => window.clearTimeout(timer);
          },
          reducedMotion: () => services().reducedMotion(),
          glassReport: () => services().glassReport(),
          profiles: () => services().profiles(),
          setProfile: (id) => services().setProfile(id),
          environmentNotes: () => services().environmentNotes(),
          closeSession: () => {
            shell?.dispose();
            shell = undefined;
            closed = true;
            // Terminal's own words when a shell exits; the page removes the tab unless it is the
            // last, which stays until a key starts a new shell.
            term.write("\r\n[Process completed]\r\n");
            latest.current.onClose(session.id);
          },
        },
        { name: session.name, cwd: session.cwd, intro },
      );

    const refit = (): void => {
      if (el.clientWidth === 0 || el.clientHeight === 0) return;
      fit.fit();
    };
    refit();
    const data = term.onData((input) => {
      if (shell === undefined && closed) {
        // The last session's shell exited: like Terminal, a key starts a new one in its place.
        closed = false;
        term.write("\r\n");
        shell = start([]);
        shell.start();
        return;
      }
      shell?.input(input);
    });
    const resize = term.onResize(({ cols, rows }) => {
      shell?.resize(cols, rows);
      latest.current.onSize(session.id, cols, rows);
    });
    latest.current.onSize(session.id, term.cols, term.rows);
    pending.current = () => {
      shell = start(session.intro);
      shell.start();
    };
    if (latest.current.ready) {
      pending.current();
      pending.current = null;
    }

    const observer = new ResizeObserver(refit);
    observer.observe(el);
    return () => {
      observer.disconnect();
      data.dispose();
      resize.dispose();
      pending.current = null;
      shell?.dispose();
      term.dispose();
      terminal.current = null;
    };
    // One terminal and one shell for the session's life; its options follow below.
  }, [session.id]);

  useEffect(() => {
    if (!props.ready || pending.current === null) return;
    pending.current();
    pending.current = null;
  }, [props.ready]);
  useEffect(() => {
    const term = terminal.current;
    if (term !== null) term.options.theme = theme;
  }, [theme]);
  useEffect(() => {
    const term = terminal.current;
    if (term !== null) term.options.cursorBlink = cursorBlink;
  }, [cursorBlink]);
  useEffect(() => {
    if (latest.current.active) terminal.current?.focus();
  }, [props.focusKey]);

  return (
    <div
      id={`panel-${session.id}`}
      role="tabpanel"
      aria-labelledby={`tab-${session.id}`}
      className={active ? "session" : "session session-hidden"}
    >
      <div ref={element} className="xterm-box" />
    </div>
  );
}

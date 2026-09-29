/**
 * `pnpm test`, replayed: the run the snapshot recorded, line by line at the pace it arrived.
 *
 * The recording keeps the millisecond each line arrived after the spawn, pnpm's own startup
 * included, so the replay pauses where the real run paused (the ESLint and typecheck tests near
 * the end take most of it). The whole is scaled down, never up, to `CAP` so it reads as a real run
 * without keeping a reader waiting; lines that arrived together are written together. Under
 * reduced motion there is no pace at all: the run is written at once. Every delay goes through the
 * host's `after`, so a test drives it with a virtual clock and Ctrl-C cancels the one pending step.
 */

import { grey, stripAnsi } from "./ansi";
import type { Job } from "./io";
import { recordedRun } from "./snapshot";
import type { ShellHost } from "./types";

/** The longest a replay takes, in milliseconds. */
export const CAP = 3000;

export function replay(host: ShellHost): Job {
  const lines = recordedRun.lines;
  const preface =
    `Replaying pnpm test as recorded in ${recordedRun.cwd} when the snapshot was taken.\n`;
  const body = lines.map(([, line]) => `${line}\n`).join("");
  return {
    text: preface + stripAnsi(body),
    start(write, done) {
      write(grey(preface.trimEnd()) + "\n");
      if (host.reducedMotion() || lines.length === 0) {
        write(body);
        done(0);
        return () => {};
      }
      const total = lines[lines.length - 1]?.[0] ?? 0;
      const scale = total > CAP ? CAP / total : 1;
      let index = 0;
      let cancel: (() => void) | undefined;
      const step = (): void => {
        const at = (lines[index] as readonly [number, string])[0];
        let chunk = "";
        while (index < lines.length && (lines[index] as readonly [number, string])[0] === at) {
          chunk += `${(lines[index] as readonly [number, string])[1]}\n`;
          index++;
        }
        write(chunk);
        const next = lines[index];
        if (next === undefined) {
          cancel = undefined;
          done(0);
        } else cancel = host.after((next[0] - at) * scale, step);
      };
      cancel = host.after((lines[0] as readonly [number, string])[0] * scale, step);
      return () => cancel?.();
    },
  };
}

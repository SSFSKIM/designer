/**
 * The Today window: the day's agenda and the tasks, on one canvas.
 *
 * The host stays still. Its header — the title and the next thing the day holds, sized to be read
 * from across the room — is fixed at the top of the window; below it one child scroller carries
 * the agenda and the tasks, with scroll edges masked on that child at the window's inner edges
 * only while there is content past them. The mask is on the scroller, never on the host or an
 * ancestor of the glass root, where it would re-root the backdrop.
 *
 * Hierarchy is layout, weight and ink: past events drop to the secondary token, the event in
 * progress is lifted on the lighter child fill, done tasks are struck through. Under forced
 * colours the lifted row keeps a border and each checkbox is a bordered circle with a real check.
 */

import { GlassGroup, GlassSurface, type BackdropHint } from "@vitreajs/vitrea-react";
import type { GlassHostHandle } from "@vitreajs/vitrea-web";
import { useCallback, useEffect, useLayoutEffect, useRef, useState, type ReactNode } from "react";

import { AGENDA, TASKS, minutesOf, type AgendaEvent, type Task } from "./data";
import type { Box } from "./environment";
import { CheckGlyph } from "./icons";
import {
  ENVIRONMENT_BACKDROP,
  LOCALE,
  THICKNESS,
  WINDOW_RADIUS,
  boxStyle,
  type GroupMaterial,
} from "./shared";

const timeFormat = new Intl.DateTimeFormat(LOCALE, { hour: "numeric", minute: "2-digit" });

function clockTime(now: Date, time: string): string {
  const date = new Date(now);
  const minutes = minutesOf(time);
  date.setHours(Math.floor(minutes / 60), minutes % 60, 0, 0);
  return timeFormat.format(date);
}

type EventState = "past" | "now" | "next" | "later";

function eventEnd(event: AgendaEvent): number {
  return event.end === undefined ? minutesOf(event.start) + 30 : minutesOf(event.end);
}

function eventStates(now: Date): EventState[] {
  const minute = now.getHours() * 60 + now.getMinutes();
  let nextTaken = false;
  return AGENDA.map((event) => {
    if (eventEnd(event) <= minute) return "past";
    if (minutesOf(event.start) <= minute) return "now";
    if (!nextTaken) {
      nextTaken = true;
      return "next";
    }
    return "later";
  });
}

function relative(minutes: number): string {
  if (minutes < 60) return `in ${minutes} min`;
  const hours = Math.floor(minutes / 60);
  const rest = minutes % 60;
  return rest === 0 ? `in ${hours} h` : `in ${hours} h ${rest} min`;
}

const TASKS_KEY = "daybreak.tasks";

function readTasks(): Task[] {
  try {
    const stored = JSON.parse(localStorage.getItem(TASKS_KEY) ?? "null") as Record<string, boolean> | null;
    if (stored === null) return [...TASKS];
    return TASKS.map((task) => ({ ...task, done: stored[task.id] ?? task.done }));
  } catch {
    return [...TASKS];
  }
}

export function TodayWindow(props: {
  readonly now: Date;
  readonly box: Box;
  readonly hint: BackdropHint | undefined;
  readonly material: GroupMaterial;
  readonly onHost: (handle: GlassHostHandle | null) => void;
}): ReactNode {
  const { now, box, hint, material, onHost } = props;
  const states = eventStates(now);
  const minute = now.getHours() * 60 + now.getMinutes();
  const current = AGENDA.findIndex((_, index) => states[index] === "now");
  const next = AGENDA.findIndex((_, index) => states[index] === "next");

  const [tasks, setTasks] = useState<Task[]>(readTasks);
  const toggle = useCallback((id: string) => {
    setTasks((list) => {
      const updated = list.map((task) => (task.id === id ? { ...task, done: !task.done } : task));
      try {
        localStorage.setItem(TASKS_KEY, JSON.stringify(Object.fromEntries(updated.map((task) => [task.id, task.done]))));
      } catch {
        // A private window with no storage still ticks the task for this visit.
      }
      return updated;
    });
  }, []);
  const left = tasks.filter((task) => !task.done).length;

  // The scroll edges: present only where content continues past an edge.
  const [scroller, setScroller] = useState<HTMLDivElement | null>(null);
  const [edges, setEdges] = useState({ top: false, bottom: false });
  const readEdges = useCallback(() => {
    const element = scroller;
    if (element === null) return;
    const top = element.scrollTop > 1;
    const bottom = element.scrollTop + element.clientHeight < element.scrollHeight - 1;
    setEdges((was) => (was.top === top && was.bottom === bottom ? was : { top, bottom }));
  }, [scroller]);

  // At first paint the window opens on the day as it stands: past events scrolled above the
  // edge, the one in progress (or the next) at the top of the scroller. The host element exists
  // only once the root is built, so this waits for the scroller itself rather than the mount.
  const anchored = useRef(false);
  useLayoutEffect(() => {
    const element = scroller;
    if (element === null || anchored.current) return;
    anchored.current = true;
    const focusIndex = current >= 0 ? current : next;
    const row =
      focusIndex > 0
        ? element.querySelector<HTMLElement>(`[data-agenda-index="${String(focusIndex - 1)}"]`)
        : focusIndex === -1
          ? element.querySelector<HTMLElement>("#tasks-title")
          : null;
    if (row !== null) {
      element.scrollTop =
        row.getBoundingClientRect().top - element.getBoundingClientRect().top + element.scrollTop - 4;
    }
    readEdges();
  }, [scroller, current, next, readEdges]);
  useEffect(() => {
    readEdges();
  }, [box.height, readEdges]);

  const headline =
    current >= 0 ? (
      <>
        <span className="today-when">Now · until {clockTime(now, AGENDA[current]?.end ?? AGENDA[current]?.start ?? "00:00")}</span>
        <span className="today-what">{AGENDA[current]?.title}</span>
      </>
    ) : next >= 0 ? (
      <>
        <span className="today-when">
          Next · {clockTime(now, AGENDA[next]?.start ?? "00:00")} · {relative(minutesOf(AGENDA[next]?.start ?? "00:00") - minute)}
        </span>
        <span className="today-what">{AGENDA[next]?.title}</span>
      </>
    ) : (
      <>
        <span className="today-when">Nothing else today</span>
        <span className="today-what">Tomorrow starts at {clockTime(now, AGENDA[0]?.start ?? "07:00")}</span>
      </>
    );

  return (
    <GlassGroup id="today" backdrop={ENVIRONMENT_BACKDROP} hint={hint} {...material}>
      <GlassSurface asChild radius={WINDOW_RADIUS} thickness={THICKNESS} foreground="vibrant" onHost={onHost}>
        <section aria-labelledby="today-title" data-glass-role="window" className="glass window today" style={boxStyle(box)}>
          <div className="today-inner">
          <header className="today-head">
            <h2 id="today-title" className="window-title">
              Today
            </h2>
            <p className="today-headline">{headline}</p>
          </header>
          <div
            ref={setScroller}
            className="today-scroll"
            onScroll={readEdges}
            data-edge-top={edges.top ? "" : undefined}
            data-edge-bottom={edges.bottom ? "" : undefined}
          >
            <section aria-labelledby="agenda-title" className="today-section">
              <h3 id="agenda-title" className="section-title">
                Agenda
              </h3>
              <ol className="agenda">
                {AGENDA.map((event, index) => (
                  <li
                    key={event.start}
                    className="agenda-event"
                    data-agenda-index={index}
                    data-state={states[index]}
                    aria-current={states[index] === "now" ? "time" : undefined}
                  >
                    <span className="agenda-time">
                      <time>{clockTime(now, event.start)}</time>
                      {event.end === undefined ? null : (
                        <time className="agenda-end">{clockTime(now, event.end)}</time>
                      )}
                    </span>
                    <span className="agenda-body">
                      <span className="agenda-title">{event.title}</span>
                      {event.where === undefined ? null : <span className="agenda-where">{event.where}</span>}
                    </span>
                  </li>
                ))}
              </ol>
            </section>
            <section aria-labelledby="tasks-title" className="today-section">
              <h3 id="tasks-title" className="section-title">
                Tasks <span className="section-count">{left} left</span>
              </h3>
              <ul className="tasks">
                {tasks.map((task) => (
                  <li key={task.id} className="task" data-done={task.done ? "" : undefined}>
                    <label className="task-label">
                      <input
                        type="checkbox"
                        className="task-check"
                        checked={task.done}
                        onChange={() => toggle(task.id)}
                      />
                      <span className="task-mark" aria-hidden="true">
                        <CheckGlyph size={14} />
                      </span>
                      <span className="task-text">
                        <span className="task-title">{task.title}</span>
                        {task.note === undefined ? null : <span className="task-note">{task.note}</span>}
                      </span>
                    </label>
                  </li>
                ))}
              </ul>
            </section>
          </div>
          </div>
        </section>
      </GlassSurface>
    </GlassGroup>
  );
}

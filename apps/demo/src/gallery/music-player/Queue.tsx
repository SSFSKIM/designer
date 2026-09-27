/**
 * The queue panel and its control, which morphs into the playlist menu.
 *
 * The panel is content, not glass: a list of songs with their artists and releases is the
 * decision function's first answer whatever a brief calls it, so it is an opaque panel in the
 * page's neutral ramp, floating at the top right over the artwork the way a printed card would.
 * Its height is bounded at six rows so nothing below it ever moves; a longer queue scrolls inside
 * it. The control is glass, the closed end of a matched-geometry morph, so the menu is the same
 * body of glass growing out of the capsule rather than a second surface fading in beside it.
 */

import { GlassMorph, useGlassRootHandle } from "@vitreajs/vitrea-react";
import {
  useEffect,
  useId,
  useLayoutEffect,
  useRef,
  useState,
  type KeyboardEvent as ReactKeyboardEvent,
  type ReactNode,
} from "react";

import { clock, minutes, releaseOf, type Playlist, type QueueEntry } from "./data";
import { ChevronDownIcon, QueueAddIcon } from "./icons";

export interface QueuePanelProps {
  readonly queue: readonly QueueEntry[];
  readonly status: string | null;
  readonly onPlay: (index: number) => void;
}

export function QueuePanel(props: QueuePanelProps): ReactNode {
  const { queue, status, onPlay } = props;
  const total = queue.reduce((sum, entry) => sum + entry.track.seconds, 0);
  const summary =
    queue.length === 0
      ? "Nothing queued"
      : `${queue.length} ${queue.length === 1 ? "song" : "songs"}, ${minutes(total)} min`;

  return (
    <aside className="mp-queue" aria-labelledby="mp-queue-heading">
      <header className="mp-queue-head">
        <h2 id="mp-queue-heading">Playing Next</h2>
        <p className="mp-queue-summary" aria-live="polite">
          {status ?? summary}
        </p>
      </header>
      {queue.length === 0 ? (
        <p className="mp-queue-empty">The queue is empty. Play a song to start one.</p>
      ) : (
        <ol className="mp-queue-list">
          {queue.map((entry, index) => {
            const release = releaseOf(entry.track);
            return (
              <li key={entry.key}>
                <button type="button" className="mp-row" onClick={() => onPlay(index)}>
                  <span className="mp-row-title">{entry.track.title}</span>
                  <span className="mp-row-time">{clock(entry.track.seconds)}</span>
                  <span className="mp-row-sub">
                    {release.artist}
                    {" · "}
                    {entry.addedByListener ? "Added by you" : release.title}
                  </span>
                </button>
              </li>
            );
          })}
        </ol>
      )}
    </aside>
  );
}

/** The gap the menu opens below the capsule at; the player lays out and measures with it. */
export const MORPH_GAP = 8;

export interface QueueMenuProps {
  readonly open: boolean;
  readonly onOpenChange: (open: boolean) => void;
  readonly playlists: readonly Playlist[];
  readonly queueLength: number;
  /**
   * The tallest the open menu may be, in CSS px: measured by the player from the capsule's foot to
   * the bottom controls' top edge less the padding the material asks between groups, so no open
   * state lays glass over the transport or the volume. Past it the menu scrolls inside itself.
   */
  readonly maxHeight: number | undefined;
  readonly onAdd: (playlistId: string) => void;
  readonly onCreate: () => void;
}

export function QueueMenu(props: QueueMenuProps): ReactNode {
  const { open, onOpenChange, queueLength } = props;
  /** Set when the menu closes by keyboard or by a choice, so the capsule takes focus back. */
  const returnFocus = useRef(false);
  const menuId = useId();
  const empty = queueLength === 0;
  // A workaround, not a design: 0.24.0's matched-geometry morph rebuilds its geometry drivers at
  // zero when the root's motion profile changes, and a pinned morph is never placed again, so
  // flipping Reduce Motion with the page open left the capsule a 0 x 0 box at the viewport's
  // origin. The morph is remounted on that flag, and remounted CLOSED: a fresh morph measures its
  // closed footprint from whatever end is mounted, so remounting it open would pin the menu's
  // box as the capsule's. A flip therefore closes the menu. Remove when the runtime carries the
  // drivers' values across the rebuild, as its materialise morph already does.
  const reducedMotion = useGlassRootHandle().profile.reducedMotionApplied;
  const [mountedFor, setMountedFor] = useState(reducedMotion);
  const flipped = mountedFor !== reducedMotion;
  useLayoutEffect(() => {
    if (!flipped) return;
    setMountedFor(reducedMotion);
    onOpenChange(false);
  }, [flipped, reducedMotion, onOpenChange]);

  const close = (restore: boolean): void => {
    returnFocus.current = restore;
    onOpenChange(false);
  };

  return (
    <GlassMorph
      key={reducedMotion ? "reduced-motion" : "motion"}
      open={open && !flipped}
      groupId="queue-menu"
      radius={23}
      openRadius={24}
      thickness={8}
      openThickness={8}
      placement="below-end"
      gap={MORPH_GAP}
      className="mp-morph"
    >
      {({ open: isOpen }) =>
        isOpen ? (
          <PlaylistMenu {...props} id={menuId} onClose={close} />
        ) : (
          <SaveQueueTrigger
            returnFocus={returnFocus}
            disabled={empty}
            onOpen={() => onOpenChange(true)}
          />
        )
      }
    </GlassMorph>
  );
}

/**
 * The capsule. With nothing queued there is nothing to save, so it is unavailable rather than
 * opening a menu of dead items: `aria-disabled` instead of `disabled`, so it stays focusable and
 * can still take focus back if the queue runs out while the menu is open.
 */
function SaveQueueTrigger(props: {
  readonly returnFocus: { current: boolean };
  readonly disabled: boolean;
  readonly onOpen: () => void;
}): ReactNode {
  const { returnFocus, disabled, onOpen } = props;
  const button = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!returnFocus.current) return;
    returnFocus.current = false;
    button.current?.focus();
  }, [returnFocus]);

  return (
    <button
      ref={button}
      type="button"
      className="mp-save"
      aria-haspopup="menu"
      aria-expanded="false"
      aria-disabled={disabled || undefined}
      onClick={() => {
        if (!disabled) onOpen();
      }}
      onKeyDown={(event) => {
        if (event.key === "ArrowDown" || event.key === "ArrowUp") {
          event.preventDefault();
          if (!disabled) onOpen();
        }
      }}
    >
      <QueueAddIcon size={18} />
      <span>Save Queue</span>
      <ChevronDownIcon size={13} className="mp-save-chevron" />
    </button>
  );
}

function PlaylistMenu(
  props: QueueMenuProps & { readonly id: string; readonly onClose: (restore: boolean) => void },
): ReactNode {
  const { id, playlists, queueLength, maxHeight, onAdd, onCreate, onClose } = props;
  const menu = useRef<HTMLDivElement>(null);
  const sectionId = useId();
  // Held in a ref so a parent re-render (the playback clock ticks four times a second) never
  // re-runs the mount effect below and pulls focus back to the first item.
  const closeRef = useRef(onClose);
  closeRef.current = onClose;

  const items = (): HTMLElement[] =>
    Array.from(menu.current?.querySelectorAll<HTMLElement>('[role="menuitem"]') ?? []);

  useEffect(() => {
    // Focus lands after the commit that promotes the platter to the overlay plane, not before:
    // that promotion moves the platter's node, and a focused element that is moved loses focus.
    const focusFirst = window.setTimeout(() => items()[0]?.focus({ preventScroll: true }), 0);
    const outside = (event: PointerEvent): void => {
      if (menu.current !== null && event.target instanceof Node && menu.current.contains(event.target)) {
        return;
      }
      closeRef.current(false);
    };
    document.addEventListener("pointerdown", outside, true);
    return () => {
      window.clearTimeout(focusFirst);
      document.removeEventListener("pointerdown", outside, true);
    };
  }, []);

  // The queue can run out while the menu is open (the last queued song starts playing), and then
  // the menu has nothing to act on: it closes and the capsule takes focus back.
  useEffect(() => {
    if (queueLength === 0) closeRef.current(true);
  }, [queueLength]);

  const onKeyDown = (event: ReactKeyboardEvent<HTMLDivElement>): void => {
    const list = items();
    const index = list.indexOf(document.activeElement as HTMLElement);
    const focus = (next: number): void => {
      event.preventDefault();
      list[(next + list.length) % list.length]?.focus();
    };
    switch (event.key) {
      case "ArrowDown":
        focus(index + 1);
        break;
      case "ArrowUp":
        focus(index - 1);
        break;
      case "Home":
        focus(0);
        break;
      case "End":
        focus(list.length - 1);
        break;
      case "Escape":
        event.preventDefault();
        onClose(true);
        break;
      case "Tab":
        onClose(false);
        break;
    }
  };

  const songs = `${queueLength} ${queueLength === 1 ? "song" : "songs"}`;

  return (
    <div
      ref={menu}
      id={id}
      role="menu"
      aria-label="Save the queue to a playlist"
      className="mp-menu"
      style={maxHeight === undefined ? undefined : { maxHeight }}
      onKeyDown={onKeyDown}
    >
      <div role="group" aria-labelledby={sectionId}>
        <p id={sectionId} className="mp-menu-section" role="presentation">
          Add {songs} to
        </p>
        {playlists.map((playlist) => (
          <button
            key={playlist.id}
            type="button"
            role="menuitem"
            className="mp-menu-item"
            onClick={() => {
              onAdd(playlist.id);
              onClose(true);
            }}
          >
            <span>{playlist.name}</span>
            <span className="mp-menu-count">{playlist.songs} songs</span>
          </button>
        ))}
      </div>
      <div role="separator" className="mp-menu-rule" />
      <button
        type="button"
        role="menuitem"
        className="mp-menu-item"
        onClick={() => {
          onCreate();
          onClose(true);
        }}
      >
        <span>New Playlist from Queue</span>
      </button>
    </div>
  );
}

/**
 * Playback as a reducer: the sounding track, where it is, what played and what is queued.
 *
 * There is no audio. Position is a clock the root's frame loop advances while playing, which is
 * enough for every control on the page to do what it says: skip, return, scrub, jump into the
 * queue, play a row of the album.
 */

import {
  INITIAL_ELAPSED,
  INITIAL_HISTORY,
  INITIAL_QUEUE,
  INITIAL_TRACK,
  releaseOf,
  type QueueEntry,
  type Track,
} from "./data";

export interface PlaybackState {
  readonly current: QueueEntry;
  readonly elapsed: number;
  readonly playing: boolean;
  readonly history: readonly QueueEntry[];
  readonly queue: readonly QueueEntry[];
  /** Bumped per entry created, so a track re-queued by "previous" gets a fresh key. */
  readonly serial: number;
}

export type PlaybackAction =
  | { readonly type: "toggle" }
  | { readonly type: "next" }
  | { readonly type: "previous" }
  | { readonly type: "seek"; readonly seconds: number }
  | { readonly type: "tick"; readonly seconds: number }
  | { readonly type: "play-queued"; readonly index: number }
  | { readonly type: "play-track"; readonly track: Track };

const entry = (track: Track, serial: number, addedByListener = false): QueueEntry => ({
  key: `e${serial}-${track.id}`,
  track,
  addedByListener,
});

export const INITIAL_PLAYBACK: PlaybackState = {
  current: entry(INITIAL_TRACK, 0),
  elapsed: INITIAL_ELAPSED,
  playing: false,
  history: INITIAL_HISTORY.map((track, index) => entry(track, -1 - index)),
  queue: INITIAL_QUEUE,
  serial: 1,
};

function advance(state: PlaybackState): PlaybackState {
  const [next, ...rest] = state.queue;
  if (next === undefined) {
    // The end of the queue: the last track stays up, finished and stopped, as a player leaves it.
    return { ...state, playing: false, elapsed: state.current.track.seconds };
  }
  return {
    ...state,
    history: [...state.history, state.current],
    current: next,
    queue: rest,
    elapsed: 0,
  };
}

export function playback(state: PlaybackState, action: PlaybackAction): PlaybackState {
  switch (action.type) {
    case "toggle": {
      const finished = state.elapsed >= state.current.track.seconds;
      return { ...state, playing: !state.playing, elapsed: finished ? 0 : state.elapsed };
    }
    case "next":
      return advance(state);
    case "previous": {
      // A few seconds in, "previous" returns to the start of the track; at its start, it steps
      // back and the track it left goes back to the head of the queue.
      const previous = state.history[state.history.length - 1];
      if (state.elapsed > 3 || previous === undefined) return { ...state, elapsed: 0 };
      return {
        ...state,
        history: state.history.slice(0, -1),
        current: previous,
        queue: [state.current, ...state.queue],
        elapsed: 0,
      };
    }
    case "seek":
      return { ...state, elapsed: Math.min(Math.max(action.seconds, 0), state.current.track.seconds) };
    case "tick": {
      if (!state.playing) return state;
      const elapsed = state.elapsed + action.seconds;
      if (elapsed < state.current.track.seconds) return { ...state, elapsed };
      return advance(state);
    }
    case "play-queued": {
      const target = state.queue[action.index];
      if (target === undefined) return state;
      return {
        ...state,
        history: [...state.history, state.current],
        current: target,
        queue: state.queue.slice(action.index + 1),
        elapsed: 0,
        playing: true,
      };
    }
    case "play-track": {
      // Playing a row of a release rebuilds the queue the way a client does: what the listener
      // put there stays ahead, and the release continues after the chosen track.
      const release = releaseOf(action.track);
      const after = release.tracks.filter((track) => track.number > action.track.number);
      const kept = state.queue.filter(
        (queued) => queued.addedByListener && queued.track.id !== action.track.id,
      );
      let serial = state.serial;
      const continuing = after.map((track) => entry(track, (serial += 1)));
      return {
        ...state,
        history: [...state.history, state.current],
        current: entry(action.track, (serial += 1)),
        queue: [...kept, ...continuing],
        elapsed: 0,
        playing: true,
        serial: serial + 1,
      };
    }
  }
}

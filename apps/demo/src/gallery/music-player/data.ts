/**
 * The player's catalogue: one album with its tracks, the single the listener queued ahead of it,
 * and three playlists. Realistic rather than exhaustive: the brief asks for one album, a queue of
 * six and three playlists, and every number here is one a listener would see.
 */

import icehouseUrl from "./images/icehouse.jpg";
import slowThawUrl from "./images/slow-thaw.jpg";

export interface Credit {
  readonly photographer: string;
  readonly profile: string;
  readonly photo: string;
}

export interface Release {
  readonly id: string;
  readonly kind: "Album" | "Single";
  readonly title: string;
  readonly artist: string;
  readonly year: number;
  readonly label: string;
  readonly liner: string;
  readonly artwork: string;
  readonly artworkAlt: string;
  readonly credit: Credit;
  /**
   * The colour the reading wash is painted in, per scheme: the lightest and the deepest tone of
   * the release's own artwork, so the column's ground belongs to the picture it veils.
   */
  readonly wash: { readonly light: string; readonly dark: string };
  readonly tracks: readonly Track[];
}

export interface Track {
  readonly id: string;
  readonly releaseId: string;
  readonly number: number;
  readonly title: string;
  readonly seconds: number;
}

const ALBUM_ID = "pressure-ridge";
const SINGLE_ID = "meltwater";

const albumTrack = (number: number, title: string, seconds: number): Track => ({
  id: `${ALBUM_ID}-${number}`,
  releaseId: ALBUM_ID,
  number,
  title,
  seconds,
});

export const RELEASES: Readonly<Record<string, Release>> = {
  [ALBUM_ID]: {
    id: ALBUM_ID,
    kind: "Album",
    title: "Pressure Ridge",
    artist: "Signe Halvorsen",
    year: 2025,
    label: "Tundra Tapes",
    liner: "Recorded through hydrophones set into the lake ice at Torneträsk, February 2025.",
    artwork: icehouseUrl,
    artworkAlt: "Cracked lake ice seen from directly above, pale blue with trapped air bubbles.",
    credit: {
      photographer: "Abby Santurbane",
      profile: "https://unsplash.com/@santurbanephotography",
      photo: "https://unsplash.com/photos/CMosZWsrIoc",
    },
    wash: { light: "#eef3f6", dark: "#0a1016" },
    tracks: [
      albumTrack(1, "Black Ice", 192),
      albumTrack(2, "Surface Tension", 245),
      albumTrack(3, "Frazil", 167),
      albumTrack(4, "Air Held Under", 298),
      albumTrack(5, "Pressure Ridge", 321),
      albumTrack(6, "Singing Ice", 216),
      albumTrack(7, "Candle Ice", 254),
      albumTrack(8, "The Long Crack", 362),
      albumTrack(9, "Breakup", 309),
    ],
  },
  [SINGLE_ID]: {
    id: SINGLE_ID,
    kind: "Single",
    title: "Meltwater",
    artist: "Kasper Lind",
    year: 2025,
    label: "Floe Records",
    liner: "Written during the spring breakup on Lake Inari.",
    artwork: slowThawUrl,
    artworkAlt: "An aerial view of a frozen lake, blue frost with lighter drifts.",
    credit: {
      photographer: "Aaron Burden",
      profile: "https://unsplash.com/@aaronburden",
      photo: "https://unsplash.com/photos/if9vJoHDQes",
    },
    wash: { light: "#ecf2f8", dark: "#08111a" },
    tracks: [{ id: `${SINGLE_ID}-1`, releaseId: SINGLE_ID, number: 1, title: "Meltwater", seconds: 234 }],
  },
};

export const ALBUM: Release = RELEASES[ALBUM_ID] as Release;
export const SINGLE: Release = RELEASES[SINGLE_ID] as Release;

export function releaseOf(track: Track): Release {
  return RELEASES[track.releaseId] as Release;
}

/** Where the session was left: the album's fourth track, 1:47 in, paused. */
export const INITIAL_TRACK: Track = ALBUM.tracks[3] as Track;
export const INITIAL_ELAPSED = 107;

/** The album's first three tracks have played; the listener put the single next. */
export const INITIAL_HISTORY: readonly Track[] = ALBUM.tracks.slice(0, 3);

/** A queue entry: a track, and whether the listener put it there rather than the album. */
export interface QueueEntry {
  readonly key: string;
  readonly track: Track;
  readonly addedByListener: boolean;
}

export const INITIAL_QUEUE: readonly QueueEntry[] = [
  { key: "q-meltwater", track: SINGLE.tracks[0] as Track, addedByListener: true },
  ...ALBUM.tracks.slice(4).map((track) => ({ key: `q-${track.id}`, track, addedByListener: false })),
];

export interface Playlist {
  readonly id: string;
  readonly name: string;
  readonly songs: number;
}

export const INITIAL_PLAYLISTS: readonly Playlist[] = [
  { id: "late-desk", name: "Late Desk", songs: 48 },
  { id: "cold-mornings", name: "Cold Mornings", songs: 23 },
  { id: "long-drive-north", name: "Long Drive North", songs: 61 },
];

export function clock(seconds: number): string {
  const whole = Math.max(0, Math.floor(seconds));
  const minutes = Math.floor(whole / 60);
  const rest = whole % 60;
  return `${minutes}:${rest.toString().padStart(2, "0")}`;
}

export function minutes(seconds: number): number {
  return Math.round(seconds / 60);
}

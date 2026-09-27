/**
 * The instrument's content. Every number here is derived from the same anchors
 * (DESIGN.md §6) so the sheets agree with each other and with the field.
 */

import { REGION } from "./field/palettes";

export interface Station {
  readonly id: string;
  readonly name: string;
  readonly lat: number;
  readonly lon: number;
  readonly speed: number;
  readonly bearing: number;
  readonly updated: string;
}

export const STATIONS: readonly Station[] = [
  { id: "GY-01", name: "Kuroshio front", lat: 35.12, lon: 141.8, speed: 1.84, bearing: 72, updated: "11:02" },
  { id: "GY-02", name: "Cold-core ring", lat: 33.4, lon: 146.25, speed: 0.61, bearing: 198, updated: "11:04" },
  { id: "GY-03", name: "Shatsky Rise", lat: 32.75, lon: 150.9, speed: 0.27, bearing: 141, updated: "10:58" },
  { id: "GY-04", name: "Recirculation gyre", lat: 31.2, lon: 143.6, speed: 0.48, bearing: 246, updated: "11:06" },
  { id: "GY-05", name: "Warm-core ring", lat: 38.05, lon: 147.3, speed: 0.93, bearing: 15, updated: "11:01" },
  { id: "GY-06", name: "Oyashio confluence", lat: 39.6, lon: 144.15, speed: 0.36, bearing: 168, updated: "10:55" },
];

export const METHOD = {
  grid: "0.08°",
  horizon: "6 h",
  latency: "41 min",
  drifters: "1,900",
  altimetry: "14",
  radar: "23",
  cadence: "10 min",
} as const;

/** A station's position as viewport fractions: u across, v up. */
export function stationToField(station: Station): { readonly u: number; readonly v: number } {
  return {
    u: (station.lon - REGION.west) / (REGION.east - REGION.west),
    v: (station.lat - REGION.south) / (REGION.north - REGION.south),
  };
}

export function formatLat(lat: number): string {
  return `${Math.abs(lat).toFixed(2)}°${lat >= 0 ? "N" : "S"}`;
}

export function formatLon(lon: number): string {
  return `${Math.abs(lon).toFixed(2)}°${lon >= 0 ? "E" : "W"}`;
}

export function formatBearing(bearing: number): string {
  return `${Math.round(bearing).toString().padStart(3, "0")}°`;
}

export function formatTime(date: Date): string {
  const hh = date.getUTCHours().toString().padStart(2, "0");
  const mm = date.getUTCMinutes().toString().padStart(2, "0");
  return `${hh}:${mm} UTC`;
}

export function formatDate(date: Date): string {
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  return `${date.getUTCDate()} ${months[date.getUTCMonth()] ?? ""} ${date.getUTCFullYear()}`;
}

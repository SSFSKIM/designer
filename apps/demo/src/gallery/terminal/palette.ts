/**
 * The terminal's sixteen colours, designed against the glass they are written on.
 *
 * The runtime picks the window's ink by the level of the body it draws: white over a dark body,
 * black over a light one. The terminal follows that pick, never the colour scheme's name, so the
 * palette is keyed by the ink's polarity: `light` ink is for a dark body, `dark` ink for a light
 * one. Each colour is chosen so its relative luminance clears 4.5:1 against the body the page
 * dims toward — at least about 0.36 over the Clear Dark target (encoded 0.19) and at most about
 * 0.08 under the Clear Light one (encoded 0.86) — with room for the map's structure under the
 * glass: the first audit read the dark-ink yellow and grey at 4.46 and 4.35 over the west shore's
 * shaded slopes, and the dark-ink set moved a step darker; the second read the grey at 4.44 on
 * the CSS tier's collapsed body there, and it moved again. The audit reads every rendered line.
 * ANSI "black" and "white" are set to readable greys of the right pole, because a shell's black
 * on a dark body would otherwise be a colour nobody can read, and the terminal's background is
 * fully transparent: the glass is the background.
 */

import type { ITheme } from "@xterm/xterm";

export type InkPolarity = "light" | "dark";

const LIGHT_INK: ITheme = {
  foreground: "#eef1f4",
  cursor: "#f4f6f8",
  cursorAccent: "#10141a",
  selectionBackground: "rgba(134, 183, 255, 0.34)",
  selectionInactiveBackground: "rgba(134, 183, 255, 0.2)",
  black: "#9aa5b1",
  red: "#ff8f86",
  green: "#7fe0a3",
  yellow: "#f2d174",
  blue: "#86b7ff",
  magenta: "#e7a6ff",
  cyan: "#74dde3",
  white: "#dfe4ea",
  brightBlack: "#a9b3bd",
  brightRed: "#ffa39b",
  brightGreen: "#9cf0bb",
  brightYellow: "#ffe08f",
  brightBlue: "#a4c9ff",
  brightMagenta: "#efbcff",
  brightCyan: "#97ecf0",
  brightWhite: "#ffffff",
};

const DARK_INK: ITheme = {
  foreground: "#15181c",
  cursor: "#15181c",
  cursorAccent: "#f4f6f8",
  selectionBackground: "rgba(28, 71, 173, 0.22)",
  selectionInactiveBackground: "rgba(28, 71, 173, 0.12)",
  black: "#1f2328",
  red: "#961a12",
  green: "#12542f",
  yellow: "#5f4200",
  blue: "#1a41a0",
  magenta: "#782289",
  cyan: "#09505d",
  white: "#373e46",
  brightBlack: "#41474f",
  brightRed: "#84170f",
  brightGreen: "#0e4a2b",
  brightYellow: "#553b00",
  brightBlue: "#15388b",
  brightMagenta: "#681c78",
  brightCyan: "#074450",
  brightWhite: "#22272e",
};

export function themeFor(ink: InkPolarity): ITheme {
  return { ...(ink === "light" ? LIGHT_INK : DARK_INK), background: "rgba(0, 0, 0, 0)" };
}

/**
 * The polarity of the ink the runtime published on a host (`--vitrea-foreground`, pure white or
 * pure black at a label alpha), or undefined before it has published one.
 */
export function inkOf(host: HTMLElement): InkPolarity | undefined {
  const value = getComputedStyle(host).getPropertyValue("--vitrea-foreground").trim();
  const channels = /rgba?\(\s*(\d+)[,\s]+(\d+)[,\s]+(\d+)/.exec(value);
  if (channels === null) return undefined;
  const sum = Number(channels[1]) + Number(channels[2]) + Number(channels[3]);
  return sum > 382 ? "light" : "dark";
}

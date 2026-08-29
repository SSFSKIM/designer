/**
 * Turning an author's CSS colour into the seed core carries.
 *
 * The public tint API takes a **CSS colour string**, because that is what an app
 * already has: a design token, a custom property's value, a hex out of a Figma
 * file. Anything narrower would make the flagship colouring API the one place in
 * vitrea where an app cannot write the colour it uses everywhere else.
 *
 * The consequence is that something has to parse it, and this package refuses to
 * ship a second CSS colour parser. So the browser parses it — a 2D canvas
 * context resolves *any* colour syntax the engine knows (named colours,
 * `oklch()`, `color-mix()`, relative colours) to sRGB, clamped, which is exactly
 * the working space X5 locks v1 to. A context is a handful of bytes and results
 * are memoised per string, so the cost is one parse per distinct colour per
 * document.
 *
 * There is a second path, and it exists for one environment rather than as a
 * design choice: jsdom has no canvas context, and the CSSOM round-trip it *does*
 * implement resolves the numeric syntaxes (`#rrggbbaa`, `rgb()`, `rgba()`,
 * space-separated with a slash alpha) but leaves keywords as keywords. Unit
 * tests therefore write numeric colours; a browser takes the canvas path and
 * accepts everything.
 *
 * A colour neither path resolves is **refused**, with a diagnostic naming it,
 * and the surface renders untinted. Guessing at a colour an author wrote and got
 * wrong is exactly the kind of silent invention the rest of this codebase
 * declines to make.
 */

import { glassTint, type GlassTint } from "@vitreajs/vitrea";

import type { PlatformDiagnosticsChannel } from "./diagnostics";

/** `rgb(r, g, b)` / `rgba(r, g, b, a)`, as both parsers normalise to. */
const RGB_FUNCTION = /^rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*(?:,\s*([\d.]+)\s*)?\)$/;
/** `#rgb`, `#rgba`, `#rrggbb`, `#rrggbbaa` — what a canvas context hands back. */
const HEX = /^#([0-9a-f]{3,8})$/i;

function fromNormalised(
  r: number,
  g: number,
  b: number,
  alpha: number,
): GlassTint {
  return glassTint([r, g, b], alpha);
}

/** Parse the normalised form both probes produce. `undefined` when it is neither. */
function fromResolved(resolved: string): GlassTint | undefined {
  const fn = RGB_FUNCTION.exec(resolved.trim());
  if (fn !== null) {
    return fromNormalised(
      Number(fn[1]) / 255,
      Number(fn[2]) / 255,
      Number(fn[3]) / 255,
      fn[4] === undefined ? 1 : Number(fn[4]),
    );
  }

  const hex = HEX.exec(resolved.trim());
  if (hex === null) return undefined;
  const digits = hex[1] as string;
  const short = digits.length === 3 || digits.length === 4;
  if (!short && digits.length !== 6 && digits.length !== 8) return undefined;
  const step = short ? 1 : 2;
  const channel = (index: number): number => {
    const slice = digits.slice(index * step, index * step + step);
    return Number.parseInt(short ? slice + slice : slice, 16) / 255;
  };
  const hasAlpha = digits.length === 4 || digits.length === 8;
  return fromNormalised(channel(0), channel(1), channel(2), hasAlpha ? channel(3) : 1);
}

/**
 * A parser bound to one document, memoised by colour string.
 *
 * Bound rather than free because both probes need a document, and a root already
 * owns one. The cache is unbounded on purpose: its keys are the distinct tint
 * colours an app declares, which is a design-system-sized number, not a
 * frame-sized one.
 */
export function createTintParser(doc: Document): (value: string) => GlassTint | undefined {
  const cache = new Map<string, GlassTint | undefined>();

  /** Canvas: the general resolver. `undefined` where there is no context to use. */
  const viaCanvas = (() => {
    let context: CanvasRenderingContext2D | null | undefined;
    return (value: string): GlassTint | undefined | null => {
      if (context === undefined) context = doc.createElement("canvas").getContext("2d");
      if (context === null) return null;
      // Two sentinels: an unparseable value leaves `fillStyle` at whatever it
      // already held, so agreement across two different starting points is what
      // distinguishes "resolved" from "ignored".
      context.fillStyle = "#000000";
      context.fillStyle = value;
      const first = context.fillStyle;
      context.fillStyle = "#ffffff";
      context.fillStyle = value;
      if (context.fillStyle !== first) return undefined;
      return typeof first === "string" ? fromResolved(first) : undefined;
    };
  })();

  /** CSSOM: the numeric syntaxes, for an environment with no canvas. */
  const viaStyle = (value: string): GlassTint | undefined => {
    const element = doc.createElement("div");
    element.style.color = "rgb(0, 0, 0)";
    element.style.color = value;
    const first = element.style.color;
    element.style.color = "rgb(255, 255, 255)";
    element.style.color = value;
    if (element.style.color !== first) return undefined;
    return fromResolved(first);
  };

  return (value: string): GlassTint | undefined => {
    const cached = cache.get(value);
    if (cached !== undefined || cache.has(value)) return cached;
    const canvas = viaCanvas(value);
    const parsed = canvas === null ? viaStyle(value) : canvas;
    cache.set(value, parsed);
    return parsed;
  };
}

/**
 * Resolve a declaration into what core's node descriptor takes.
 *
 * The three states are distinct and all three are reachable from the public API:
 * `undefined` inherits the group's tint, `null` clears it (`Glass.tint(nil)`),
 * and a colour sets it. A colour that does not parse resolves to `null` — the
 * surface is untinted rather than inheriting something the author did not ask
 * for — and says so once, on the diagnostics channel.
 */
export function resolveTintDeclaration(
  value: string | null | undefined,
  parse: (value: string) => GlassTint | undefined,
  subject: string,
  diagnostics?: PlatformDiagnosticsChannel,
): GlassTint | null | undefined {
  if (value === undefined) return undefined;
  if (value === null) return null;
  const parsed = parse(value);
  if (parsed !== undefined) return parsed;
  diagnostics?.report({
    code: "tint-unparseable",
    severity: "error",
    subjects: [subject],
    message: `Tint "${value}" is not a colour this engine could parse, so "${subject}" rendered untinted. Any CSS colour works in a browser; outside one (jsdom, SSR) only the numeric syntaxes resolve — write #rrggbb, #rrggbbaa, rgb() or rgba() there.`,
  });
  return null;
}

/**
 * The sheet as it is displayed, for the measurement: a field of encoded luma in the sheet's own
 * coordinates, one cell per `CELL` CSS px, rebuilt from the DOM whenever the sheet changes.
 *
 * A glass group that samples the DOM declares what is behind it, and the declaration overrides
 * the runtime's own tone reading, so where an open platter lies over the sheet the number has to
 * be the printed page and not only its paper: headlines, body text, rules, the selected row's
 * wash, the accent bars. The browser gives a page no way to read back its own rendered DOM
 * everywhere (a `foreignObject` snapshot taints the canvas in WebKit, where the CSS tier runs),
 * so the sheet is modelled from its boxes instead and painted, at the field's resolution, into a
 * small canvas whose cells are then read like the photograph's:
 *
 *   paper     the sheet's computed background, everywhere
 *   fills     every element's computed background, its borders side by side, and an inset
 *             zero-blur box-shadow (the accent bars) as the strip it paints
 *   text      every text run's line boxes (a Range's client rects), each filled with the run's
 *             computed colour at its INK COVERAGE: the fraction of the line box the run's own
 *             glyphs cover, measured once per run by drawing its text in its computed font into
 *             an offscreen canvas and summing the alpha
 *   glyphs    the forecast's inline SVG symbols, stroked from their own paths
 *
 * What it leaves out, each under a few per cent of the cells it touches: link underlines, the
 * reduce-transparency switch's thumb (a pseudo-element), focus rings and hover underlines (both
 * transient). An element clipped by `clip-path` is taken as a triangle when the clip has three
 * points (the caution mark) and as hidden otherwise (the visually-hidden pattern).
 *
 * Canvas and browser text both blend in encoded sRGB, so a cell's mean encoded luma here is the
 * mean of the pixels it models, which is the quantity `plane.measure` averages.
 */

export const CELL = 8;

export interface SheetField {
  readonly columns: number;
  readonly rows: number;
  /** Encoded Rec. 709 luma per cell, row-major. */
  readonly luma: Float32Array;
  /** The sheet's left edge in the viewport at build time (its scroll is vertical only). */
  readonly left: number;
}

interface Box {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

const coverageCache = new Map<string, number>();

/** The fraction of a line box `text` inks, drawn in `font` with `letterSpacing`. */
function inkCoverage(text: string, font: string, letterSpacing: string): number {
  const key = `${font}|${letterSpacing}|${text}`;
  const cached = coverageCache.get(key);
  if (cached !== undefined) return cached;
  const probe = document.createElement("canvas");
  const context = probe.getContext("2d", { willReadFrequently: true });
  if (context === null) return 0;
  context.font = font;
  if (letterSpacing !== "normal") context.letterSpacing = letterSpacing;
  // A long paragraph is measured on its opening stretch: coverage is a property of the face and
  // the language, and 2,048 px of it is thousands of glyphs.
  let sample = text;
  while (sample.length > 16 && context.measureText(sample).width > 2048) {
    sample = sample.slice(0, Math.floor(sample.length / 2));
  }
  const metrics = context.measureText(sample);
  const ascent = Math.ceil(metrics.fontBoundingBoxAscent);
  const width = Math.ceil(metrics.width);
  const height = ascent + Math.ceil(metrics.fontBoundingBoxDescent);
  if (width <= 0 || height <= 0) return 0;
  probe.width = width;
  probe.height = height;
  // Resizing a canvas resets its state.
  context.font = font;
  if (letterSpacing !== "normal") context.letterSpacing = letterSpacing;
  context.fillStyle = "#000";
  context.fillText(sample, 0, ascent);
  const { data } = context.getImageData(0, 0, width, height);
  let inked = 0;
  for (let i = 3; i < data.length; i += 4) inked += data[i] ?? 0;
  const coverage = inked / 255 / (width * height);
  coverageCache.set(key, coverage);
  return coverage;
}

function transformText(text: string, transform: string): string {
  if (transform === "uppercase") return text.toUpperCase();
  if (transform === "lowercase") return text.toLowerCase();
  return text;
}

/** How much of an element's box a `clip-path` leaves showing (see the header). */
function clipShare(clip: string): number {
  if (clip === "none") return 1;
  if (clip.startsWith("polygon(") && clip.split(",").length === 3) return 0.5;
  return 0;
}

/** An inset, zero-blur, zero-spread box-shadow is a stroke along the edges it is offset from. */
const INSET_STROKE = /^(.*\))\s+(-?[\d.]+)px\s+(-?[\d.]+)px\s+0px\s+0px\s+inset$/;

function paintElement(
  context: CanvasRenderingContext2D,
  element: Element,
  box: Box,
  share: number,
): void {
  const style = getComputedStyle(element);
  context.globalAlpha = share;
  context.fillStyle = style.backgroundColor;
  context.fillRect(box.x, box.y, box.width, box.height);

  const sides = [
    ["Top", box.x, box.y, box.width, 0],
    ["Bottom", box.x, box.y + box.height, box.width, 0],
    ["Left", box.x, box.y, 0, box.height],
    ["Right", box.x + box.width, box.y, 0, box.height],
  ] as const;
  for (const [side, x, y, w, h] of sides) {
    const width = parseFloat(style.getPropertyValue(`border-${side.toLowerCase()}-width`));
    const kind = style.getPropertyValue(`border-${side.toLowerCase()}-style`);
    if (!(width > 0) || kind === "none" || kind === "hidden") continue;
    context.fillStyle = style.getPropertyValue(`border-${side.toLowerCase()}-color`);
    if (side === "Top") context.fillRect(x, y, w, width);
    else if (side === "Bottom") context.fillRect(x, y - width, w, width);
    else if (side === "Left") context.fillRect(x, y, width, h);
    else context.fillRect(x - width, y, width, h);
  }

  const stroke = INSET_STROKE.exec(style.boxShadow);
  if (stroke !== null) {
    const [, color = "transparent", dx = "0", dy = "0"] = stroke;
    const x = parseFloat(dx);
    const y = parseFloat(dy);
    context.fillStyle = color;
    if (x > 0) context.fillRect(box.x, box.y, x, box.height);
    if (x < 0) context.fillRect(box.x + box.width + x, box.y, -x, box.height);
    if (y > 0) context.fillRect(box.x, box.y, box.width, y);
    if (y < 0) context.fillRect(box.x, box.y + box.height + y, box.width, -y);
  }
  context.globalAlpha = 1;
}

function paintSvg(context: CanvasRenderingContext2D, svg: SVGSVGElement, box: Box): void {
  const view = svg.viewBox.baseVal;
  if (view.width === 0 || view.height === 0) return;
  context.save();
  context.translate(box.x, box.y);
  context.scale(box.width / view.width, box.height / view.height);
  context.translate(-view.x, -view.y);
  for (const shape of svg.querySelectorAll("path, circle")) {
    const style = getComputedStyle(shape);
    const path = new Path2D(shape instanceof SVGPathElement ? (shape.getAttribute("d") ?? "") : "");
    if (shape instanceof SVGCircleElement) {
      const { cx, cy, r } = shape;
      path.arc(cx.baseVal.value, cy.baseVal.value, r.baseVal.value, 0, Math.PI * 2);
    }
    context.lineWidth = parseFloat(style.strokeWidth) || 1;
    context.lineCap = "round";
    context.lineJoin = "round";
    context.strokeStyle = style.stroke;
    const dash = style.strokeDasharray;
    context.setLineDash(dash === "none" ? [] : dash.split(/[\s,]+/).map(parseFloat));
    context.stroke(path);
  }
  context.restore();
}

/** Build the field for `sheet` as it is laid out now. */
export function buildSheetField(sheet: HTMLElement): SheetField {
  const origin = sheet.getBoundingClientRect();
  const columns = Math.max(1, Math.ceil(origin.width / CELL));
  const rows = Math.max(1, Math.ceil(origin.height / CELL));
  const canvas = document.createElement("canvas");
  canvas.width = columns;
  canvas.height = rows;
  const context = canvas.getContext("2d", { willReadFrequently: true });
  if (context === null) throw new Error("park-trails: no 2D context for the sheet field.");
  context.scale(1 / CELL, 1 / CELL);
  const local = (rect: DOMRect): Box => ({
    x: rect.left - origin.left,
    y: rect.top - origin.top,
    width: rect.width,
    height: rect.height,
  });

  context.fillStyle = getComputedStyle(sheet).backgroundColor;
  context.fillRect(0, 0, origin.width, origin.height);

  // Elements that clip themselves away, and everything inside them.
  const hidden = new Set<Element>();
  const walker = document.createTreeWalker(sheet, NodeFilter.SHOW_ELEMENT);
  for (let node = walker.nextNode(); node !== null; node = walker.nextNode()) {
    const element = node as Element;
    const parent = element.parentElement;
    if (parent !== null && hidden.has(parent)) {
      hidden.add(element);
      continue;
    }
    const style = getComputedStyle(element);
    const share = clipShare(style.clipPath);
    if (share === 0 || style.visibility !== "visible" || style.display === "none") {
      hidden.add(element);
      continue;
    }
    if (element instanceof SVGSVGElement) {
      paintSvg(context, element, local(element.getBoundingClientRect()));
      continue;
    }
    if (element instanceof SVGElement) continue;
    paintElement(context, element, local(element.getBoundingClientRect()), share);
  }

  const texts = document.createTreeWalker(sheet, NodeFilter.SHOW_TEXT);
  const range = document.createRange();
  for (let node = texts.nextNode(); node !== null; node = texts.nextNode()) {
    const parent = node.parentElement;
    const raw = node.textContent ?? "";
    if (parent === null || hidden.has(parent) || raw.trim() === "") continue;
    const style = getComputedStyle(parent);
    const font = `${style.fontStyle} ${style.fontWeight} ${style.fontSize} ${style.fontFamily}`;
    const text = transformText(raw.replace(/\s+/g, " ").trim(), style.textTransform);
    const coverage = inkCoverage(text, font, style.letterSpacing);
    if (coverage === 0) continue;
    range.selectNodeContents(node);
    context.globalAlpha = coverage;
    context.fillStyle = style.color;
    for (const rect of range.getClientRects()) {
      if (rect.width <= 0 || rect.height <= 0) continue;
      const box = local(rect);
      context.fillRect(box.x, box.y, box.width, box.height);
    }
  }
  context.globalAlpha = 1;

  const { data } = context.getImageData(0, 0, columns, rows);
  const luma = new Float32Array(columns * rows);
  for (let i = 0; i < luma.length; i += 1) {
    const at = i * 4;
    luma[i] =
      (0.2126 * (data[at] ?? 0) + 0.7152 * (data[at + 1] ?? 0) + 0.0722 * (data[at + 2] ?? 0)) / 255;
  }
  return { columns, rows, luma, left: origin.left };
}

/**
 * The sheet's mean encoded luma over one field column and the 8 px band that starts `top` CSS px
 * below the sheet's top edge, interpolated between the two cell rows the band straddles.
 */
export function sheetLumaAt(field: SheetField, column: number, top: number): number {
  const c = Math.min(field.columns - 1, Math.max(0, column));
  const exact = top / CELL;
  const first = Math.floor(exact);
  const weight = exact - first;
  const at = (row: number): number =>
    field.luma[Math.min(field.rows - 1, Math.max(0, row)) * field.columns + c] ?? 0;
  return at(first) * (1 - weight) + at(first + 1) * weight;
}

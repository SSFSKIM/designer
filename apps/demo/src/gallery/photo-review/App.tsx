/**
 * Photo review: the page. One stage canvas is the live plane (`develop.ts`), three glass
 * surfaces float over the photograph (`Controls.tsx`), and everything else is opaque content
 * on the tonal ground (`Columns.tsx`). The record is `DESIGN.md`.
 */
import {
  GlassGroup,
  useGlassRootHandle,
  useGlassTicker,
  type BackdropHint,
} from "@vitreajs/vitrea-react";
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type PointerEvent,
  type SetStateAction,
} from "react";

import { Compare, COMPARE, PALETTE, Tools, Verdict, VERDICT, type Tool, type View } from "./Controls";
import { FrameColumn, Filmstrip, ShootColumn } from "./Columns";
import { FRAMES, INITIAL_FRAME, PHOTOGRAPHS, type Develop, type Flag, type Frame } from "./data";
import {
  autoExposure,
  cropRect,
  devicePx,
  histogramOf,
  paintStage,
  regionReading,
  type Histogram,
  type Rect,
  type RegionReading,
} from "./develop";

/** The three groups, each one glass function (`DESIGN.md`, the record). */
const GROUPS = ["tools", "compare", "verdict"] as const;
type GroupId = (typeof GROUPS)[number];

/** What the page last measured under one group: the box the runtime drew it at, and the plane. */
interface Measured {
  readonly box: Rect;
  readonly reading: RegionReading | undefined;
}

/**
 * The audit's handles, written through a local view of `window` rather than a global
 * declaration, because the gallery pages share one TypeScript program and a `Window`
 * augmentation would have to match every sibling's to the letter. `select` and `backdrop` are
 * how `DESIGN.md`'s flat-phase table is reproduced: step the frames, read each group's drawn
 * box and the plane's deviation under it.
 */
interface AuditWindow {
  __vitrea?: unknown;
  __glassDemo?: {
    readonly openMenu: () => void;
    readonly setReducedTransparency: (on: boolean) => void;
    readonly select: (index: number) => void;
    readonly backdrop: () => {
      readonly frame: number;
      readonly groups: Partial<Record<GroupId, Measured>>;
    };
  };
}
const audit = window as unknown as AuditWindow;

/** How long the window must hold still before a platter the page closed is re-opened. */
const REOPEN_AFTER_MS = 150;

/** One texture for all three groups: the stage canvas. Module-scoped so it is one object. */
const STAGE_BACKDROP = { kind: "texture", id: "stage" } as const;

/** The filmstrip band's height, and the photograph's margins inside the stage. */
const BAND = 120;
const GUTTER = 204;
const MARGIN_Y = 28;
/** Every floating surface sits this far inside the photograph's edges. */
const INSET = 16;

interface Layout {
  readonly width: number;
  readonly stageHeight: number;
  readonly photo: Rect;
  readonly palette: Rect;
  readonly compare: Rect;
  readonly verdict: Rect;
}

/**
 * Every floating position is derived from the photograph's rectangle, which is derived from the
 * window, so nothing is a constant typed once; and because the rectangle is the frame's whole
 * 3:2 extent whatever the crop, the controls hold still from frame to frame while culling.
 */
function layoutFor(width: number, height: number): Layout {
  const stageHeight = height - BAND;
  const availW = width - 2 * GUTTER;
  const availH = stageHeight - 2 * MARGIN_Y;
  const pw = Math.floor(Math.min(availW, availH * 1.5));
  const ph = Math.floor(pw / 1.5);
  const photo = { x: Math.round((width - pw) / 2), y: Math.round((stageHeight - ph) / 2), w: pw, h: ph };
  const cx = photo.x + photo.w / 2;
  const palette = {
    x: photo.x + photo.w - INSET - PALETTE.w,
    y: Math.round(photo.y + photo.h / 2 - PALETTE.h / 2),
    w: PALETTE.w,
    h: PALETTE.h,
  };
  return {
    width,
    stageHeight,
    photo,
    palette,
    compare: { x: Math.round(cx - COMPARE.w / 2), y: photo.y + INSET, w: COMPARE.w, h: COMPARE.h },
    verdict: { x: Math.round(cx - VERDICT.w / 2), y: photo.y + photo.h - INSET - VERDICT.h, w: VERDICT.w, h: VERDICT.h },
  };
}

function useViewport(): { width: number; height: number; dpr: number } {
  const read = () => ({ width: window.innerWidth, height: window.innerHeight, dpr: window.devicePixelRatio || 1 });
  const [size, setSize] = useState(read);
  useEffect(() => {
    const onResize = () => setSize(read());
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);
  return size;
}

function useScheme(): "light" | "dark" {
  const query = "(prefers-color-scheme: dark)";
  const [dark, setDark] = useState(() => window.matchMedia(query).matches);
  useEffect(() => {
    const list = window.matchMedia(query);
    const onChange = () => setDark(list.matches);
    list.addEventListener("change", onChange);
    return () => list.removeEventListener("change", onChange);
  }, []);
  return dark ? "dark" : "light";
}

/** Decoded images by photograph id, loading the current burst's first. */
function useImages(kind: "full" | "thumb", first: string): ReadonlyMap<string, HTMLImageElement> {
  const [images, setImages] = useState<ReadonlyMap<string, HTMLImageElement>>(() => new Map());
  const firstRef = useRef(first);
  useEffect(() => {
    let live = true;
    const order = [...PHOTOGRAPHS].sort((a, b) => Number(b.id === firstRef.current) - Number(a.id === firstRef.current));
    for (const photo of order) {
      const image = new Image();
      image.decoding = "async";
      image.src = kind === "full" ? photo.full : photo.thumb;
      image
        .decode()
        .then(() => {
          if (live) setImages((prev) => new Map(prev).set(photo.id, image));
        })
        .catch(() => undefined);
    }
    return () => {
      live = false;
    };
  }, [kind]);
  return images;
}

type Hints = Partial<Record<GroupId, BackdropHint>>;

/** A box as the device pixels it covers, so a sub-pixel spring tail does not re-read the canvas. */
const devicePxKey = (rect: Rect, dpr: number): string => {
  const px = devicePx(rect, dpr);
  return `${px.x},${px.y},${px.w},${px.h}`;
};

/**
 * Each group's drawn box: the union of its members' bounds as the runtime read them on its last
 * frame, which is where the glass actually is. An open morph does not follow a layout change,
 * so the box the layout intends and the box on screen can differ; the hint describes the latter.
 */
function drawnBoxes(root: ReturnType<typeof useGlassRootHandle>["root"]): Map<string, Rect> {
  const boxes = new Map<string, Rect>();
  const input = root?.renderInput();
  if (input === undefined) return boxes;
  for (const plane of input.planes) {
    for (const node of plane.nodes) {
      const b = node.bounds;
      const was = boxes.get(node.groupId);
      if (was === undefined) {
        boxes.set(node.groupId, { x: b.x, y: b.y, w: b.width, h: b.height });
        continue;
      }
      const x = Math.min(was.x, b.x);
      const y = Math.min(was.y, b.y);
      boxes.set(node.groupId, {
        x,
        y,
        w: Math.max(was.x + was.w, b.x + b.width) - x,
        h: Math.max(was.y + was.h, b.y + b.height) - y,
      });
    }
  }
  return boxes;
}

export function App({ reduceTransparency, onReduceTransparency }: {
  reduceTransparency: boolean;
  onReduceTransparency: (on: boolean) => void;
}) {
  const { root } = useGlassRootHandle();
  const ticker = useGlassTicker();
  const viewport = useViewport();
  const layout = useMemo(() => layoutFor(viewport.width, viewport.height), [viewport.width, viewport.height]);
  const scheme = useScheme();

  const [frames, setFrames] = useState<readonly Frame[]>(FRAMES);
  const [current, setCurrent] = useState(INITIAL_FRAME);
  const [tool, setToolState] = useState<Tool | null>(null);
  /** A platter the page closed because the window moved the palette, to re-open where it now is. */
  const reopen = useRef<Tool | null>(null);
  /** Every tool change a reader makes goes through here, and cancels a pending re-open. */
  const setTool = useCallback((next: SetStateAction<Tool | null>) => {
    reopen.current = null;
    setToolState(next);
  }, []);
  const [view, setView] = useState<View>("after");
  const [hints, setHints] = useState<Hints>({});
  const [histogram, setHistogram] = useState<Histogram | null>(null);
  const [canvas, setCanvas] = useState<HTMLCanvasElement | null>(null);

  const frame = frames[current] ?? FRAMES[0]!;
  const fulls = useImages("full", frame.photo.id);
  const thumbs = useImages("thumb", frame.photo.id);

  const ground = useMemo(() => {
    void scheme;
    return getComputedStyle(document.documentElement).getPropertyValue("--ground").trim() || "#d9d9d9";
  }, [scheme]);

  // ---- state changes -------------------------------------------------------------------------

  const updateFrame = useCallback((index: number, patch: (frame: Frame) => Frame) => {
    setFrames((prev) => prev.map((f) => (f.index === index ? patch(f) : f)));
  }, []);

  const currentRef = useRef(current);
  currentRef.current = current;

  const onDevelop = useCallback(
    (patch: Partial<Develop>) => {
      updateFrame(currentRef.current, (f) => ({ ...f, develop: { ...f.develop, ...patch } }));
      setView("after");
    },
    [updateFrame],
  );
  const onFlag = useCallback((flag: Flag) => updateFrame(currentRef.current, (f) => ({ ...f, flag })), [updateFrame]);
  const onRating = useCallback((rating: number) => updateFrame(currentRef.current, (f) => ({ ...f, rating })), [updateFrame]);
  const select = useCallback((index: number) => setCurrent(Math.max(0, Math.min(FRAMES.length - 1, index))), []);

  // ---- the platter follows the window by closing and re-opening -------------------------------

  /*
   * An open `GlassMorph` keeps the box it opened at: it re-follows its footprint only while
   * closed and settled. So when the window moves the palette with the platter open, the page
   * closes it, which carries the platter back onto the palette where it now is, and re-opens
   * the same tool once the morph has come to rest and the window has held still, so it opens at
   * the new geometry. A reader's own tool change in between cancels the re-open.
   */
  const placedAt = useRef(layout.palette);
  useEffect(() => {
    const was = placedAt.current;
    placedAt.current = layout.palette;
    if (tool === null || (was.x === layout.palette.x && was.y === layout.palette.y)) return;
    reopen.current = tool;
    setToolState(null);
  }, [layout.palette, tool]);

  const [closedAtRest, setClosedAtRest] = useState(true);
  useEffect(() => {
    if (tool !== null) setClosedAtRest(false);
  }, [tool]);
  const onMorphEnd = useCallback((open: boolean) => setClosedAtRest(!open), []);

  useEffect(() => {
    if (!closedAtRest || tool !== null || reopen.current === null) return;
    const timer = window.setTimeout(() => {
      const next = reopen.current;
      reopen.current = null;
      if (next !== null) setToolState(next);
    }, REOPEN_AFTER_MS);
    return () => window.clearTimeout(timer);
  }, [closedAtRest, tool, layout]);

  // ---- the stage: painted from the root's own frame loop when something changed --------------

  const work = useRef<HTMLCanvasElement | null>(null);
  const developed = useRef<ImageData | null>(null);
  const dirty = useRef(true);
  const paintInput = useRef({ frame, view, tool, ground, layout, dpr: viewport.dpr, fulls, thumbs });
  paintInput.current = { frame, view, tool, ground, layout, dpr: viewport.dpr, fulls, thumbs };
  /** What each group was last measured over, and the frame whose paint it was measured on. */
  const paintedFrame = useRef(0);
  const measured = useRef<{ frame: number; groups: Partial<Record<GroupId, Measured>> }>({ frame: 0, groups: {} });

  useEffect(() => {
    dirty.current = true;
  }, [frame, view, tool, ground, layout, viewport.dpr, fulls, thumbs, canvas]);

  /*
   * One listener on the root's loop paints the stage when something changed, and re-measures a
   * group's hint whenever the stage was repainted or the box the runtime drew that group at has
   * moved by a device pixel, which on a morph is every frame of its flight and then never.
   */
  useEffect(() => {
    if (canvas === null) return;
    return ticker.subscribe(() => {
      const input = paintInput.current;
      let repainted = false;
      if (dirty.current) {
        const image = input.fulls.get(input.frame.photo.id) ?? input.thumbs.get(input.frame.photo.id);
        if (image !== undefined) {
          dirty.current = false;
          work.current ??= document.createElement("canvas");
          const data = paintStage(canvas, work.current, {
            frame: input.frame,
            image,
            before: input.view === "before",
            cropMode: input.tool === "crop" && input.view === "after",
            ground: input.ground,
            dpr: input.dpr,
            photo: input.layout.photo,
          });
          if (data !== null) {
            developed.current = data;
            paintedFrame.current = input.frame.index + 1;
            repainted = true;
            setHistogram(histogramOf(data));
          }
        }
      }
      if (developed.current === null) return;

      const boxes = drawnBoxes(root);
      const was = measured.current.groups;
      const groups: Partial<Record<GroupId, Measured>> = { ...was };
      let changed = false;
      for (const id of GROUPS) {
        const box = boxes.get(id);
        const before = was[id];
        const device = (rect: Rect): string => devicePxKey(rect, input.dpr);
        const moved =
          box === undefined ? before !== undefined : before === undefined || device(box) !== device(before.box);
        if (!repainted && !moved) continue;
        changed = true;
        if (box === undefined) delete groups[id];
        else groups[id] = { box, reading: regionReading(canvas, box, input.dpr) };
      }
      if (!changed) return;
      measured.current = { frame: paintedFrame.current, groups };
      const next: Hints = {};
      for (const id of GROUPS) {
        const hint = groups[id]?.reading?.hint;
        if (hint !== undefined) next[id] = hint;
      }
      setHints((prev) => (JSON.stringify(prev) === JSON.stringify(next) ? prev : next));
    });
  }, [canvas, root, ticker]);

  const onAuto = useCallback(() => {
    const data = developed.current;
    if (data === null) return;
    onDevelop({ ev: autoExposure(data, frame.develop.ev) });
  }, [frame.develop.ev, onDevelop]);

  // ---- the runtime: the texture, and the audit's handles --------------------------------------

  useEffect(() => {
    if (root === null || canvas === null) return;
    root.setBackdropTexture("stage", { kind: "canvas", canvas });
  }, [root, canvas]);

  useEffect(() => {
    if (root !== null) audit.__vitrea = root;
  }, [root]);

  useEffect(() => {
    audit.__glassDemo = {
      openMenu: () => setTool("crop"),
      setReducedTransparency: onReduceTransparency,
      select,
      backdrop: () => measured.current,
    };
  }, [onReduceTransparency, select, setTool]);

  // ---- keyboard: the cull is a keyboard task --------------------------------------------------

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.metaKey || event.ctrlKey || event.altKey || event.defaultPrevented) return;
      const target = event.target instanceof HTMLElement ? event.target : null;
      if (target?.closest("input, textarea, [contenteditable]") && event.key !== "Escape") return;
      const inGroup = target?.closest('[role="radiogroup"], [role="toolbar"]') !== null && target !== null;
      const key = event.key.length === 1 ? event.key.toLowerCase() : event.key;
      let handled = true;
      switch (key) {
        case "ArrowRight":
          if (inGroup) return;
          select(currentRef.current + 1);
          break;
        case "ArrowLeft":
          if (inGroup) return;
          select(currentRef.current - 1);
          break;
        case "p":
          onFlag("pick");
          break;
        case "x":
          onFlag("reject");
          break;
        case "u":
          onFlag(null);
          break;
        case "0": case "1": case "2": case "3": case "4": case "5":
          onRating(Number(key));
          break;
        case "\\":
          setView((v) => (v === "after" ? "before" : "after"));
          break;
        case "e":
          setTool((t) => (t === "exposure" ? null : "exposure"));
          break;
        case "w":
          setTool((t) => (t === "white-balance" ? null : "white-balance"));
          break;
        case "r":
          setTool((t) => (t === "crop" ? null : "crop"));
          break;
        case "Escape":
          setTool(null);
          break;
        default:
          handled = false;
      }
      if (handled) event.preventDefault();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onFlag, onRating, select, setTool]);

  // ---- crop: drag the frame on the stage ------------------------------------------------------

  const drag = useRef<{ dx: number; dy: number } | null>(null);
  const cropMode = tool === "crop" && view === "after";
  const toFrame = (event: PointerEvent<HTMLCanvasElement>) => ({
    u: (event.clientX - layout.photo.x) / layout.photo.w,
    v: (event.clientY - layout.photo.y) / layout.photo.h,
  });
  const onStageDown = (event: PointerEvent<HTMLCanvasElement>) => {
    if (!cropMode) return;
    const { u, v } = toFrame(event);
    const c = cropRect(frame.develop);
    if (u < c.x || u > c.x + c.w || v < c.y || v > c.y + c.h) return;
    drag.current = { dx: u - (c.x + c.w / 2), dy: v - (c.y + c.h / 2) };
    event.currentTarget.setPointerCapture(event.pointerId);
  };
  const onStageMove = (event: PointerEvent<HTMLCanvasElement>) => {
    const grip = drag.current;
    if (grip === null) return;
    const { u, v } = toFrame(event);
    const c = cropRect(frame.develop);
    const cx = Math.min(1 - c.w / 2, Math.max(c.w / 2, u - grip.dx));
    const cy = Math.min(1 - c.h / 2, Math.max(c.h / 2, v - grip.dy));
    onDevelop({ cx: Math.round(cx * 1000) / 1000, cy: Math.round(cy * 1000) / 1000 });
  };
  const onStageUp = () => {
    drag.current = null;
  };

  // ---- the page -------------------------------------------------------------------------------

  const trailX = layout.photo.x + layout.photo.w;
  const stageLabel = `Frame ${frame.index + 1} of ${frames.length}: ${frame.photo.depicts}. ${
    view === "before" ? "Before adjustments." : "After adjustments."
  }`;

  return (
    <div className="app">
      <main className="stage" aria-label="Stage" style={{ height: layout.stageHeight }}>
        <canvas
          ref={setCanvas}
          className={cropMode ? "stage-canvas cropping" : "stage-canvas"}
          role="img"
          aria-label={stageLabel}
          width={Math.round(layout.width * viewport.dpr)}
          height={Math.round(layout.stageHeight * viewport.dpr)}
          style={{ width: layout.width, height: layout.stageHeight }}
          onPointerDown={onStageDown}
          onPointerMove={onStageMove}
          onPointerUp={onStageUp}
          onPointerCancel={onStageUp}
        />
      </main>

      <ShootColumn
        frames={frames}
        style={{ left: 0, top: layout.photo.y, width: layout.photo.x, maxHeight: layout.stageHeight - layout.photo.y }}
        reduceTransparency={reduceTransparency}
        onReduceTransparency={onReduceTransparency}
      />
      <FrameColumn
        frame={frame}
        frames={frames}
        histogram={histogram}
        style={{ left: trailX, top: layout.photo.y, width: layout.width - trailX, maxHeight: layout.stageHeight - layout.photo.y }}
      />
      <Filmstrip frames={frames} current={current} onSelect={select} thumbs={thumbs} ground={ground} />

      <GlassGroup id="tools" backdrop={STAGE_BACKDROP} hint={hints.tools}>
        <Tools
          tool={tool}
          onTool={setTool}
          frame={frame}
          onDevelop={onDevelop}
          onAuto={onAuto}
          anchor={{ x: layout.palette.x, y: layout.palette.y }}
          onMorphEnd={onMorphEnd}
        />
      </GlassGroup>
      <GlassGroup id="compare" backdrop={STAGE_BACKDROP} hint={hints.compare}>
        <Compare view={view} onView={setView} at={layout.compare} />
      </GlassGroup>
      <GlassGroup id="verdict" backdrop={STAGE_BACKDROP} hint={hints.verdict}>
        <Verdict frame={frame} onFlag={onFlag} onRating={onRating} at={layout.verdict} />
      </GlassGroup>
    </div>
  );
}

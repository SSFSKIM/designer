/**
 * The page's state and its one frame callback.
 *
 * Three things are decided here and nowhere else:
 *
 * - **Which photograph the plane shows.** The last window the reader has reached (its top above
 *   70 % of the viewport), resolved through the configuration: the lens window shows the chosen
 *   lens, the finish window the chosen finish. Choosing either changes the picture the bars are
 *   made of, which is the point of putting the configure bar on glass at all.
 * - **Where the scroll edges sit.** Read every frame from the runtime's own measurement of the
 *   floating hosts (`root.scene`), so the fade follows the bars' real boxes, including the lens
 *   platter while it opens, and is never a constant typed once. The mask lives on the scroll
 *   container, a sibling of the glass root, never on an ancestor of it.
 * - **What the CSS tier is told.** Only on that tier, each group declares the luminance of the
 *   frame the canvas holds under its own box (`plane.ts`), re-measured on every frame the canvas
 *   paints, so mid-dissolve the declaration is the blend the reader sees, not the photograph
 *   arriving. On the WebGPU tier the renderer reads the texture per surface and a declaration
 *   would replace that reading.
 *
 * Everything runs on the root's ticker: one loop, the runtime's, never a second rAF.
 */

import {
  DEFAULT_GROUP_SAMPLING,
  resolveAccessibilityPolicy,
  type Rect,
} from "@vitreajs/vitrea";
import {
  useGlassAccessibility,
  useGlassCapabilities,
  useGlassRoot,
  useGlassRootHandle,
  useGlassTicker,
  type BackdropHint,
} from "@vitreajs/vitrea-react";
import {
  samplingPaddingFor,
  type GlassMaterialProfileDocument,
  type GlassRoot as PlatformGlassRoot,
} from "@vitreajs/vitrea-web";
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
  type WheelEvent,
} from "react";

import { Chrome, type GroupId, type SectionId, SECTIONS } from "./Chrome";
import type { FinishId, LensId, PhotoId } from "./content";
import type { LensMenuHandle } from "./LensMenu";
import {
  createPlanePainter,
  DARK_PLANE_DIM,
  hintOf,
  loadPhoto,
  measurePainted,
  type LoadedPhoto,
  type PlanePainter,
} from "./plane";
import { Sheets } from "./Sheets";

type WindowKind = "hero" | "sensor" | "lens" | "finish";

const TOP_GROUPS: readonly GroupId[] = ["nav", "display"];
const BOTTOM_GROUPS: readonly GroupId[] = ["finish", "lens", "order"];
const ALL_GROUPS: readonly GroupId[] = [...TOP_GROUPS, ...BOTTOM_GROUPS];

/** Loaded in the order the reader meets them; the hero decides first paint. */
const LOAD_ORDER: readonly PhotoId[] = [
  "hero",
  "sensor",
  "lens-45",
  "finish-nickel",
  "lens-28",
  "lens-90",
  "finish-graphite",
];

/** Clear plane kept beyond a bar before the sheet starts to fade in, in CSS px. */
const EDGE_CLEAR = 10;

/** A window counts as reached once its top is above this fraction of the viewport. */
const WINDOW_REACHED = 0.7;
/** The section under this fraction of the viewport is the current one in the navigation. */
const READING_LINE = 0.42;

function unionOfGroup(root: PlatformGlassRoot, groupId: GroupId): Rect | undefined {
  let union: Rect | undefined;
  for (const host of document.querySelectorAll<HTMLElement>(`[data-vitrea-group="${groupId}"]`)) {
    const nodeId = host.getAttribute("data-vitrea-node");
    const bounds = nodeId === null ? undefined : root.scene.glassNode(nodeId)?.bounds;
    // A morph's platter parks as a 2 × 2 point until it is placed; it claims no footprint.
    if (bounds === undefined || bounds.width < 4 || bounds.height < 4) continue;
    if (union === undefined) {
      union = bounds;
      continue;
    }
    const x = Math.min(union.x, bounds.x);
    const y = Math.min(union.y, bounds.y);
    union = {
      x,
      y,
      width: Math.max(union.x + union.width, bounds.x + bounds.width) - x,
      height: Math.max(union.y + union.height, bounds.y + bounds.height) - y,
    };
  }
  return union;
}

/**
 * An upper bound on any bottom-bar member's box. The sampling padding is monotone in a member's
 * span and extents, and every member of that bar is 56 tall and narrower than this, so a gap derived
 * from it covers each of them without waiting for a measurement.
 */
const BAR_MEMBER_BOUND: readonly [number, number] = [480, 56];

/**
 * The distance two groups in one bar keep: core's advisory padding or the material's own 3σ,
 * whichever is larger, taken over every state this page can be in (both schemes, Reduce
 * Transparency and Increase Contrast on and off). Held constant rather than recomputed per state
 * because a gap that changed would slide every host along the bar without resizing it, which is
 * the one kind of move the runtime does not re-measure. Derived, never typed.
 */
function worstCaseGroupGap(document: GlassMaterialProfileDocument): number {
  let widest: number = DEFAULT_GROUP_SAMPLING.samplingPadding;
  for (const scheme of ["light", "dark"] as const) {
    for (const reducedTransparency of [false, true]) {
      for (const increasedContrast of [false, true]) {
        const policy = resolveAccessibilityPolicy({
          reducedTransparency,
          reducedMotion: false,
          increasedContrast,
          forcedColors: false,
          reducedTransparencySupported: true,
        });
        widest = Math.max(
          widest,
          samplingPaddingFor({
            members: [BAR_MEMBER_BOUND],
            material: policy.material,
            profile: document.active[scheme].patch,
            ...(document.cssTierMapping === undefined ? {} : { cssTierMapping: document.cssTierMapping }),
          }),
        );
      }
    }
  }
  return Math.ceil(widest);
}

export interface PageProps {
  readonly requested: "webgpu" | "css";
  readonly reduceTransparency: boolean;
  readonly onReduceTransparency: (on: boolean, persist: boolean) => void;
}

/**
 * The audit's handles, written through a local view of `window` rather than a global declaration:
 * six gallery pages share one TypeScript program, and a `Window` augmentation here would have to
 * match every sibling's to the letter.
 */
interface AuditWindow {
  __vitrea?: PlatformGlassRoot;
  __glassDemo?: {
    readonly openMenu?: () => void;
    readonly setReducedTransparency: (on: boolean) => void;
  };
}

export function Page(props: PageProps): ReactNode {
  const root = useGlassRoot();
  const ticker = useGlassTicker();
  const accessibility = useGlassAccessibility();
  const { materialProfileDocument } = useGlassRootHandle();
  const navState = useGlassCapabilities("nav");

  const [finish, setFinish] = useState<FinishId>("nickel");
  const [lens, setLens] = useState<LensId>("45");
  const [windowKind, setWindowKind] = useState<WindowKind>("hero");
  const [section, setSection] = useState<SectionId | null>(null);
  const [hints, setHints] = useState<Partial<Record<GroupId, BackdropHint>>>({});
  const groupGap = useMemo(() => worstCaseGroupGap(materialProfileDocument), [materialProfileDocument]);
  const [ready, setReady] = useState<ReadonlySet<PhotoId>>(() => new Set());
  const [dark, setDark] = useState(
    () => window.matchMedia("(prefers-color-scheme: dark)").matches,
  );
  const dim = dark ? DARK_PLANE_DIM : 0;

  const photos = useRef(new Map<PhotoId, LoadedPhoto>());
  const painter = useRef<PlanePainter | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const scrollerRef = useRef<HTMLDivElement>(null);
  const heroRef = useRef<HTMLDivElement>(null);
  const sensorRef = useRef<HTMLDivElement>(null);
  const lensRef = useRef<HTMLDivElement>(null);
  const finishRef = useRef<HTMLDivElement>(null);
  const priceHeadingRef = useRef<HTMLHeadingElement>(null);
  const lensMenuRef = useRef<LensMenuHandle>(null);

  const target: PhotoId =
    windowKind === "lens" ? `lens-${lens}` : windowKind === "finish" ? `finish-${finish}` : windowKind;
  const cssTier = props.requested === "css" || navState?.activeRenderer === "css";
  const reducedMotion =
    accessibility?.reducedMotion ??
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Refs the frame callback reads, so the one subscription never re-subscribes.
  const cssTierRef = useRef(cssTier);
  cssTierRef.current = cssTier;
  const dimRef = useRef(dim);
  dimRef.current = dim;
  const scrollDirty = useRef(true);
  const hintsDirty = useRef(true);

  // The photographs, decoded and gridded in reading order.
  useEffect(() => {
    let cancelled = false;
    for (const id of LOAD_ORDER) {
      void loadPhoto(id).then(
        (photo) => {
          if (cancelled) return;
          photos.current.set(id, photo);
          setReady((current) => new Set(current).add(id));
        },
        () => undefined,
      );
    }
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const query = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = (): void => setDark(query.matches);
    query.addEventListener("change", onChange);
    return () => query.removeEventListener("change", onChange);
  }, []);

  const heroReady = ready.has("hero");

  // The painter, and the texture handed to the runtime: the canvas itself, placed by its own box.
  useEffect(() => {
    const canvas = canvasRef.current;
    if (root === null || canvas === null || !heroReady) return;
    const created = createPlanePainter(canvas, photos.current, "hero", dimRef.current);
    painter.current = created;
    root.setBackdropTexture("plane", { kind: "canvas", canvas });
    const observer = new ResizeObserver(() => {
      created.resize();
      hintsDirty.current = true;
      scrollDirty.current = true;
    });
    observer.observe(canvas);
    return () => {
      observer.disconnect();
      painter.current = null;
      root.setBackdropTexture("plane", undefined);
    };
  }, [heroReady, root]);

  // A state change dissolves the plane (steps under Reduce Motion) once the photograph is decoded.
  useEffect(() => {
    if (painter.current === null || !ready.has(target)) return;
    painter.current.show(target, reducedMotion);
    hintsDirty.current = true;
  }, [ready, reducedMotion, target]);

  useEffect(() => {
    painter.current?.setDim(dim);
    hintsDirty.current = true;
  }, [dim, heroReady]);

  useEffect(() => {
    hintsDirty.current = true;
    if (!cssTier) setHints({});
  }, [cssTier]);

  // The one frame callback.
  useEffect(() => {
    if (root === null) return;
    let edgeTop = -1;
    let edgeBottom = -1;
    let insetBottom = -1;
    let footprint = "";

    return ticker.subscribe((dtMs) => {
      // The dissolve advances first, so every reading below is of the frame the canvas now holds.
      if (painter.current?.tick(dtMs) === true) hintsDirty.current = true;
      const scroller = scrollerRef.current;
      if (scroller === null) return;
      const viewportHeight = scroller.clientHeight;

      // Scroll edges and insets, from the runtime's measured boxes.
      const tops = TOP_GROUPS.map((id) => unionOfGroup(root, id)).filter((b) => b !== undefined);
      const bottoms = BOTTOM_GROUPS.map((id) => unionOfGroup(root, id)).filter(
        (b) => b !== undefined,
      );
      if (tops.length > 0) {
        const top = Math.max(...tops.map((b) => b.y + b.height)) + EDGE_CLEAR;
        if (Math.abs(top - edgeTop) > 0.25) {
          edgeTop = top;
          scroller.style.setProperty("--edge-top", `${top.toFixed(1)}px`);
        }
      }
      if (bottoms.length > 0) {
        const bottom = viewportHeight - Math.min(...bottoms.map((b) => b.y)) + EDGE_CLEAR;
        if (Math.abs(bottom - edgeBottom) > 0.25) {
          edgeBottom = bottom;
          scroller.style.setProperty("--edge-bottom", `${bottom.toFixed(1)}px`);
        }
        // The resting inset ignores the open platter: content clears the bar, not the menu.
        const resting = BOTTOM_GROUPS.filter((id) => id !== "lens")
          .map((id) => unionOfGroup(root, id))
          .filter((b) => b !== undefined);
        if (resting.length > 0) {
          const inset = viewportHeight - Math.min(...resting.map((b) => b.y)) + EDGE_CLEAR;
          if (Math.abs(inset - insetBottom) > 0.25) {
            insetBottom = inset;
            scroller.style.setProperty("--inset-bottom", `${inset.toFixed(1)}px`);
          }
        }
      }

      // Which window has been reached, and which section is being read.
      if (scrollDirty.current) {
        scrollDirty.current = false;
        const windows: readonly (readonly [WindowKind, HTMLDivElement | null])[] = [
          ["hero", heroRef.current],
          ["sensor", sensorRef.current],
          ["lens", lensRef.current],
          ["finish", finishRef.current],
        ];
        let reached: WindowKind = "hero";
        for (const [kind, element] of windows) {
          if (element !== null && element.getBoundingClientRect().top <= viewportHeight * WINDOW_REACHED) {
            reached = kind;
          }
        }
        setWindowKind(reached);
        let current: SectionId | null = null;
        for (const { id } of SECTIONS) {
          const rect = document.getElementById(id)?.getBoundingClientRect();
          const line = viewportHeight * READING_LINE;
          if (rect !== undefined && rect.top <= line && rect.bottom > line) current = id;
        }
        setSection(current);
      }

      // The CSS tier's declarations: the painted frame under each group's own box, measured again
      // on every frame the canvas paints (each frame of a dissolve, and its last) and whenever a box
      // moves (the lens platter opening is the case that matters).
      const boxes = [...tops, ...bottoms]
        .map((b) => `${Math.round(b.x)},${Math.round(b.y)},${Math.round(b.width)},${Math.round(b.height)}`)
        .join(";");
      if (boxes !== footprint) {
        footprint = boxes;
        hintsDirty.current = true;
      }
      if (hintsDirty.current && cssTierRef.current) {
        const frame = painter.current?.painted();
        const canvas = canvasRef.current;
        if (frame !== undefined && canvas !== null) {
          const viewport = { width: canvas.clientWidth, height: canvas.clientHeight };
          const next: Partial<Record<GroupId, BackdropHint>> = {};
          let complete = true;
          for (const id of ALL_GROUPS) {
            const box = unionOfGroup(root, id);
            const measured =
              box === undefined ? undefined : measurePainted(photos.current, frame, viewport, box);
            if (measured === undefined) {
              complete = false;
              continue;
            }
            next[id] = hintOf(measured);
          }
          if (complete) hintsDirty.current = false;
          setHints((current) => (JSON.stringify(current) === JSON.stringify(next) ? current : next));
        }
      }
    });
  }, [root, ticker]);

  const onReduceTransparency = props.onReduceTransparency;

  // The audit's two handles.
  useEffect(() => {
    if (root === null) return;
    const audit = window as unknown as AuditWindow;
    audit.__vitrea = root;
    audit.__glassDemo = {
      openMenu: () => lensMenuRef.current?.open(),
      setReducedTransparency: (on: boolean) => onReduceTransparency(on, false),
    };
  }, [onReduceTransparency, root]);

  /*
   * The column is the page's scroller, not the document, so a scrolling key pressed anywhere
   * outside it scrolls nothing: before anything has focus, and while focus is on the floating
   * chrome, which is a sibling of the column. Both cases are carried to the column. With nothing
   * focused, focus moves there and the browser scrolls it natively from then on (focus is not taken
   * on load, so the first Tab still reaches the navigation). From the chrome, focus stays where it
   * is, as it would on a link in an ordinary page, and only keys the focused control does not own
   * are forwarded: a key already handled (default prevented), anything inside the open menu,
   * arrows and Home/End on the finish radios, Space on anything it activates, and every key in an
   * editable field.
   */
  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent): void => {
      const scroller = scrollerRef.current;
      if (scroller === null || event.defaultPrevented) return;
      if (event.altKey || event.ctrlKey || event.metaKey) return;
      const page = scroller.clientHeight * 0.85;
      const deltas: Record<string, number> = {
        ArrowDown: 48,
        ArrowUp: -48,
        PageDown: page,
        PageUp: -page,
        " ": event.shiftKey ? -page : page,
        Home: -scroller.scrollHeight,
        End: scroller.scrollHeight,
      };
      const delta = deltas[event.key];
      if (delta === undefined) return;
      const active = document.activeElement;
      const unfocused =
        active === null || active === document.body || active === document.documentElement;
      if (!unfocused) {
        if (!(active instanceof HTMLElement) || scroller.contains(active)) return;
        if (active.isContentEditable || active.matches("input, textarea, select")) return;
        if (active.closest('[role="menu"], [role="listbox"]') !== null) return;
        const paging = event.key === "PageDown" || event.key === "PageUp" || event.key === " ";
        const ownsArrows = '[role="radiogroup"], [role="slider"], [role="tablist"]';
        if (!paging && active.closest(ownsArrows) !== null) return;
        const activatedBySpace =
          'button, summary, [role="button"], [role="radio"], [role="switch"], [role="checkbox"]';
        if (event.key === " " && active.matches(activatedBySpace)) return;
      }
      event.preventDefault();
      if (unfocused) scroller.focus({ preventScroll: true });
      scroller.scrollBy({ top: delta, left: 0 });
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const onWheel = useCallback((event: WheelEvent) => {
    const scale = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? window.innerHeight : 1;
    scrollerRef.current?.scrollBy({ top: event.deltaY * scale, left: 0, behavior: "instant" });
  }, []);

  const onOrder = useCallback(() => {
    document
      .getElementById("price")
      ?.scrollIntoView({ behavior: reducedMotion ? "instant" : "smooth", block: "start" });
    priceHeadingRef.current?.focus({ preventScroll: true });
  }, [reducedMotion]);

  const onTop = useCallback(() => {
    scrollerRef.current?.scrollTo({ top: 0, behavior: reducedMotion ? "instant" : "smooth" });
  }, [reducedMotion]);

  const persistReduceTransparency = useCallback(
    (on: boolean) => onReduceTransparency(on, true),
    [onReduceTransparency],
  );

  return (
    <div className="alder" data-motion={reducedMotion ? "reduced" : "full"}>
      <canvas ref={canvasRef} className="plane" aria-hidden="true" />
      <div
        ref={scrollerRef}
        className="scroller"
        tabIndex={-1}
        onScroll={() => {
          scrollDirty.current = true;
        }}
      >
        <Sheets
          windows={{ hero: heroRef, sensor: sensorRef, lens: lensRef, finish: finishRef }}
          finish={finish}
          lens={lens}
          onFinish={setFinish}
          onLens={setLens}
          priceHeadingRef={priceHeadingRef}
          reduceTransparency={props.reduceTransparency}
          onReduceTransparency={persistReduceTransparency}
        />
      </div>
      <Chrome
        hints={cssTier ? hints : {}}
        section={section}
        finish={finish}
        lens={lens}
        onFinish={setFinish}
        onLens={setLens}
        onOrder={onOrder}
        onTop={onTop}
        reduceTransparency={props.reduceTransparency}
        onReduceTransparency={persistReduceTransparency}
        groupGap={groupGap}
        lensMenuRef={lensMenuRef}
        onWheel={onWheel}
      />
    </div>
  );
}

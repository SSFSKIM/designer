/**
 * The player: the plane, the printed album column, and the floating layer over them.
 *
 * Composition, in the order it was designed (DESIGN.md, part one): the opaque page first, a
 * column of print on the washed left of the artwork and the queue as an opaque panel at the top
 * right; then the controls, each one glass surface over unveiled artwork, grouped by function,
 * spaced by the padding the runtime derives rather than by a number typed here.
 */

import {
  GlassGroup,
  PlanePortal,
  useGlassAccessibility,
  useGlassCapabilities,
  useGlassRootHandle,
  useGlassTicker,
  type BackdropHint,
  type GlassGroupState,
} from "@vitreajs/vitrea-react";
import { DEFAULT_GROUP_SAMPLING } from "@vitreajs/vitrea";
import { samplingPaddingFor } from "@vitreajs/vitrea-web";
import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useMemo,
  useReducer,
  useRef,
  useState,
  type CSSProperties,
  type ReactNode,
  type Ref,
} from "react";

import { Transport, Volume } from "./Controls";
import {
  ALBUM,
  INITIAL_PLAYLISTS,
  SINGLE,
  clock,
  minutes,
  releaseOf,
  type Playlist,
  type Release,
  type Track,
} from "./data";
import { SoundingIcon } from "./icons";
import {
  composeLayer,
  deviceScale,
  loadImage,
  measureRegion,
  present,
  type PlaneFrame,
  type Scheme,
} from "./plane";
import { INITIAL_PLAYBACK, playback } from "./playback";
import { MORPH_GAP, QueueMenu, QueuePanel } from "./Queue";

/** Every group reads the plane; the id joins the declaration to the canvas handed over below. */
const ARTWORK = { kind: "texture", id: "artwork" } as const;

/**
 * The menu's open box with its three playlists, for measuring what it will stand on before it has
 * opened. Its width is fixed; its height grows a row per new playlist up to the measured bound.
 */
const MENU_BOX = { width: 272, height: 200 };

/** The capsule's span, the S rung. */
const CAPSULE_SPAN = 44;

/** The dissolve between two releases' artwork. A state change, so it is short and plain. */
const DISSOLVE_MS = 480;

type GroupId = "transport" | "volume" | "queue-menu";

function useMedia(query: string): boolean {
  const [matches, setMatches] = useState(() => window.matchMedia(query).matches);
  useEffect(() => {
    const list = window.matchMedia(query);
    const update = (): void => setMatches(list.matches);
    update();
    list.addEventListener("change", update);
    return () => list.removeEventListener("change", update);
  }, [query]);
  return matches;
}

function useViewport(): { readonly width: number; readonly height: number } {
  const [size, setSize] = useState(() => ({ width: window.innerWidth, height: window.innerHeight }));
  useEffect(() => {
    const update = (): void => setSize({ width: window.innerWidth, height: window.innerHeight });
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, []);
  return size;
}

export interface PlayerProps {
  readonly reduceTransparency: boolean;
  readonly onReduceTransparency: (on: boolean) => void;
}

export function Player(props: PlayerProps): ReactNode {
  const { reduceTransparency, onReduceTransparency } = props;
  const handle = useGlassRootHandle();
  const { root } = handle;
  const ticker = useGlassTicker();
  const policy = useGlassAccessibility();
  const scheme: Scheme = useMedia("(prefers-color-scheme: dark)") ? "dark" : "light";
  const contrast = useMedia("(prefers-contrast: more)");
  const viewport = useViewport();

  const [state, dispatch] = useReducer(playback, INITIAL_PLAYBACK);
  const [volume, setVolume] = useState(64);
  const [muted, setMuted] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [playlists, setPlaylists] = useState<readonly Playlist[]>(INITIAL_PLAYLISTS);
  const [status, setStatus] = useState<string | null>(null);

  const release = releaseOf(state.current.track);

  /* ---- the audit's handles ------------------------------------------------------------------ */

  // Written through an untyped view of `window`: five sibling pages share this typecheck, and a
  // global declaration here would have to agree with theirs.
  useEffect(() => {
    if (root === null) return;
    (window as unknown as Record<string, unknown>).__vitrea = root;
  }, [root]);

  useEffect(() => {
    (window as unknown as Record<string, unknown>).__glassDemo = {
      openMenu: () => setMenuOpen(true),
      setReducedTransparency: onReduceTransparency,
    };
  }, [onReduceTransparency]);

  /* ---- the clock ---------------------------------------------------------------------------- */

  // Paced by the root's own frame loop, never a second one, and measured by the wall clock: the
  // loop's deltas are capped for motion's sake, and a playback position has to keep real time.
  // State moves four times a second, finer than a pixel of the scrubber on any track here.
  useEffect(() => {
    if (!state.playing) return;
    let last = performance.now();
    return ticker.subscribe(() => {
      const now = performance.now();
      if (now - last < 250) return;
      dispatch({ type: "tick", seconds: (now - last) / 1000 });
      last = now;
    });
  }, [state.playing, ticker]);

  useEffect(() => {
    if (status === null) return;
    const timer = window.setTimeout(() => setStatus(null), 4000);
    return () => window.clearTimeout(timer);
  }, [status]);

  /* ---- what each group stands on ------------------------------------------------------------ */

  // What the visible canvas is showing right now, as `present` drew it: a declared hint overrides
  // the runtime's own tone reading on both tiers, so the hint is measured off this and never off
  // the layer a dissolve is heading to.
  const shown = useRef<PlaneFrame | null>(null);
  const menuMax = useRef<number | undefined>(undefined);
  const [hints, setHints] = useState<Partial<Record<GroupId, BackdropHint>>>({});

  const measure = useCallback(() => {
    const frame = shown.current;
    if (frame === null) return;
    const scale = frame.to.width / window.innerWidth;
    const box = (selector: string): DOMRect | undefined =>
      document.querySelector(selector)?.getBoundingClientRect();
    const next: Partial<Record<GroupId, BackdropHint>> = {};
    for (const group of ["transport", "volume"] as const) {
      const rect = box(`[data-mp-group="${group}"]`);
      const region = rect === undefined ? undefined : measureRegion(frame, rect, scale);
      if (region !== undefined) next[group] = region.hint;
    }
    // The morph's group is the capsule and the box it opens into, below-end of it: one reading
    // over both, because the group is one backdrop statement for both of its ends. Open, that box
    // is the menu as laid out; closed, the three-playlist box within the measured bound.
    const anchor = box(".mp-side [data-vitrea-morph-anchor]");
    if (anchor !== undefined && anchor.width > 0) {
      const menu = box(".mp-menu");
      const open =
        menu !== undefined && menu.height > 0
          ? { width: menu.width, height: menu.height }
          : { width: MENU_BOX.width, height: Math.min(MENU_BOX.height, menuMax.current ?? Infinity) };
      const union = {
        x: anchor.right - open.width,
        y: anchor.top,
        width: open.width,
        height: anchor.height + MORPH_GAP + open.height,
      };
      const region = measureRegion(frame, union, scale);
      if (region !== undefined) next["queue-menu"] = region.hint;
    }
    setHints((previous) => (JSON.stringify(previous) === JSON.stringify(next) ? previous : next));
  }, []);

  /* ---- the plane ---------------------------------------------------------------------------- */

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const columnRef = useRef<HTMLElement>(null);
  /** The newest finished layer: what the plane shows once any dissolve toward it has ended. */
  const latestLayer = useRef<{ readonly releaseId: string; readonly layer: HTMLCanvasElement } | null>(
    null,
  );
  const [planeEpoch, setPlaneEpoch] = useState(0);
  const reducedMotion = policy?.reducedMotion ?? false;

  const handTexture = useCallback(() => {
    const canvas = canvasRef.current;
    if (root === null || canvas === null || canvas.width === 0) return;
    root.setBackdropTexture(ARTWORK.id, { kind: "canvas", canvas });
  }, [root]);

  useEffect(handTexture, [handTexture]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas === null) return;
    let cancelled = false;
    let stop: (() => void) | undefined;
    const scale = deviceScale();
    const columnRight = columnRef.current?.getBoundingClientRect().right ?? viewport.width * 0.34;

    void loadImage(release.artwork).then((image) => {
      if (cancelled) return;
      const layer = composeLayer(
        image,
        { release, scheme, contrast, columnRight },
        viewport.width,
        viewport.height,
        scale,
      );
      const previous = latestLayer.current;
      latestLayer.current = { releaseId: release.id, layer };
      const settle = (): void => {
        handTexture();
        measure();
        setPlaneEpoch((epoch) => epoch + 1);
      };
      if (previous === null || previous.releaseId === release.id || reducedMotion) {
        shown.current = present(canvas, layer, null, 1);
        settle();
        return;
      }
      // The hints follow the picture through the dissolve, re-read every other frame (about 30
      // readings a second, each a few hundred thousand pixels off the two CPU-side layers) and
      // once more when it lands, so no frame of it declares a backdrop that is not on screen.
      let t = 0;
      let frames = 0;
      shown.current = present(canvas, layer, previous.layer, 0);
      measure();
      stop = ticker.subscribe((deltaMs) => {
        t = Math.min(1, t + Math.min(deltaMs, 50) / DISSOLVE_MS);
        const eased = t * t * (3 - 2 * t);
        shown.current = present(canvas, layer, previous.layer, eased);
        if (t < 1) {
          frames += 1;
          if (frames % 2 === 0) measure();
          return;
        }
        stop?.();
        stop = undefined;
        settle();
      });
    });

    return () => {
      cancelled = true;
      stop?.();
    };
  }, [contrast, handTexture, measure, reducedMotion, release, scheme, ticker, viewport]);

  /* ---- the gaps the material asks for ------------------------------------------------------- */

  const gaps = useMemo(() => {
    if (policy === undefined) return { queue: 24, band: 40, menu: 40 };
    const endpoint = handle.materialProfileDocument.active[scheme];
    // Never below the advisory padding core checks every layout against, which is what stands
    // when the material draws no blur at all (forced colours derives zero here, and core still
    // reports two groups closer than its advisory as overlapping). GlassToolbar floors the same way.
    const padding = (members: readonly (readonly [number, number])[]): number =>
      Math.max(
        DEFAULT_GROUP_SAMPLING.samplingPadding,
        samplingPaddingFor({
          members,
          material: policy.material,
          profile: endpoint.patch,
          cssTierMapping: handle.materialProfileDocument.cssTierMapping,
        }),
      );
    // Each is bounded from above by a box that contains its members, which is what the law's
    // monotonicity makes safe. The menu's box is its full width in both directions: it grows a
    // row per new playlist, and its span can never exceed its width.
    const capsule = padding([[MENU_BOX.width, CAPSULE_SPAN]]);
    const menu = padding([[MENU_BOX.width, MENU_BOX.width]]);
    const band = Math.max(padding([[620, 64]]), padding([[200, 44]]));
    return {
      // The capsule stands below the opaque queue panel by its own group's padding, so the body it
      // blurs never reaches under the panel (the texture tier would fold in artwork the panel
      // hides, the CSS tier the panel itself). Open, the menu's padding starts at its own top
      // edge, a capsule and a morph gap lower, and is held to the same line.
      queue: Math.ceil(Math.max(capsule, menu - CAPSULE_SPAN - MORPH_GAP)),
      band: Math.ceil(band),
      // Between the open menu's foot and the bottom band: the larger group's padding.
      menu: Math.ceil(Math.max(menu, band)),
    };
  }, [handle.materialProfileDocument, policy, scheme]);

  /* ---- how far the menu may grow ------------------------------------------------------------ */

  // Measured, not typed: from the capsule's foot plus the morph's gap down to the bottom band's
  // top edge, less the padding the two groups ask between them. The menu scrolls inside itself
  // past this, so no open state lays glass over the transport or the volume at any height.
  const [menuBound, setMenuBound] = useState<number | undefined>(undefined);

  useLayoutEffect(() => {
    const place = (): void => {
      const band = document.querySelector(".mp-band")?.getBoundingClientRect();
      const anchor = document.querySelector(".mp-side [data-vitrea-morph-anchor]")?.getBoundingClientRect();
      if (band === undefined || anchor === undefined || anchor.height === 0) return;
      const next = Math.max(0, Math.floor(band.top - gaps.menu - (anchor.bottom + MORPH_GAP)));
      menuMax.current = next;
      setMenuBound((previous) => (previous === next ? previous : next));
    };
    place();
    // The portal's hosts may not have laid out on the first pass.
    const later = window.setTimeout(place, 120);
    return () => window.clearTimeout(later);
  }, [gaps, root, viewport]);

  useEffect(() => {
    if (root === null) return;
    // Two readings: one as soon as the hosts can have been laid out, and one after the capsule's
    // measured footprint (or the opened menu's) has settled, which a morph takes a moment to publish.
    const soon = window.setTimeout(measure, 120);
    const later = window.setTimeout(measure, 600);
    return () => {
      window.clearTimeout(soon);
      window.clearTimeout(later);
    };
  }, [measure, planeEpoch, root, menuOpen, menuBound, gaps]);

  /* ---- actions ------------------------------------------------------------------------------ */

  const addToPlaylist = (playlistId: string): void => {
    const count = state.queue.length;
    setPlaylists((current) =>
      current.map((playlist) =>
        playlist.id === playlistId ? { ...playlist, songs: playlist.songs + count } : playlist,
      ),
    );
    const name = playlists.find((playlist) => playlist.id === playlistId)?.name ?? "the playlist";
    setStatus(`Added ${count} ${count === 1 ? "song" : "songs"} to ${name}`);
  };

  const createPlaylist = (): void => {
    const name = `Queue, ${new Date().toLocaleDateString("en-GB", { day: "numeric", month: "short" })}`;
    setPlaylists((current) => [
      ...current,
      { id: `new-${current.length}`, name, songs: state.queue.length },
    ]);
    setStatus(`Made ${name}`);
  };

  const capabilities = useGlassCapabilities("transport");

  return (
    <>
      <canvas
        ref={canvasRef}
        className="mp-plane"
        role="img"
        aria-label={`${release.kind} artwork: ${release.artworkAlt}`}
      />

      <AlbumColumn
        ref={columnRef}
        release={release}
        sounding={state.current.track}
        playing={state.playing}
        reduceTransparency={reduceTransparency}
        onReduceTransparency={onReduceTransparency}
        capabilities={capabilities}
        onPlay={(track) => dispatch({ type: "play-track", track })}
      />

      <QueuePanel
        queue={state.queue}
        status={status}
        onPlay={(index) => dispatch({ type: "play-queued", index })}
      />

      <PlanePortal plane="base">
        <section
          className="mp-band"
          aria-label="Player controls"
          style={{ "--mp-band-gap": `${gaps.band}px` } as CSSProperties}
        >
          <GlassGroup id="transport" backdrop={ARTWORK} hint={hints.transport}>
            <Transport
              title={state.current.track.title}
              artist={release.artist}
              seconds={state.current.track.seconds}
              elapsed={state.elapsed}
              playing={state.playing}
              canGoBack={state.history.length > 0}
              canGoForward={state.queue.length > 0}
              onToggle={() => dispatch({ type: "toggle" })}
              onPrevious={() => dispatch({ type: "previous" })}
              onNext={() => dispatch({ type: "next" })}
              onSeek={(seconds) => dispatch({ type: "seek", seconds })}
            />
          </GlassGroup>
          <GlassGroup id="volume" backdrop={ARTWORK} hint={hints.volume}>
            <Volume level={volume} muted={muted} onLevel={setVolume} onMute={setMuted} />
          </GlassGroup>
        </section>

        <section
          className="mp-side"
          aria-label="Queue actions"
          style={{ "--mp-queue-gap": `${gaps.queue}px` } as CSSProperties}
        >
          <GlassGroup id="queue-menu" backdrop={ARTWORK} hint={hints["queue-menu"]}>
            <QueueMenu
              open={menuOpen}
              onOpenChange={setMenuOpen}
              playlists={playlists}
              queueLength={state.queue.length}
              maxHeight={menuBound}
              onAdd={addToPlaylist}
              onCreate={createPlaylist}
            />
          </GlassGroup>
        </section>
      </PlanePortal>
    </>
  );
}

interface AlbumColumnProps {
  readonly ref: Ref<HTMLElement>;
  readonly release: Release;
  readonly sounding: Track;
  readonly playing: boolean;
  readonly reduceTransparency: boolean;
  readonly onReduceTransparency: (on: boolean) => void;
  readonly capabilities: GlassGroupState | undefined;
  readonly onPlay: (track: Track) => void;
}

function tierLine(state: GlassGroupState | undefined): string {
  if (state === undefined) return "Glass by vitrea.";
  if (state.activeRenderer === "webgpu") {
    return state.refraction === "true"
      ? "Glass by vitrea, drawn on WebGPU and refracting the artwork."
      : "Glass by vitrea, drawn on WebGPU.";
  }
  return "Glass by vitrea, drawn on its CSS tier, the same material without refraction.";
}

function AlbumColumn(props: AlbumColumnProps): ReactNode {
  const { ref, release, sounding, playing, reduceTransparency, onReduceTransparency } = props;
  const total = release.tracks.reduce((sum, track) => sum + track.seconds, 0);
  const count = release.tracks.length;
  return (
    <main ref={ref} className="mp-column" aria-labelledby="mp-release-title">
      <header className="mp-top">
        <p className="mp-wordmark">Fathom</p>
        <button
          type="button"
          role="switch"
          aria-checked={reduceTransparency}
          className="mp-switch"
          onClick={() => onReduceTransparency(!reduceTransparency)}
        >
          <span>Reduce transparency</span>
          <span className="mp-switch-track" aria-hidden="true">
            <span className="mp-switch-knob" />
          </span>
        </button>
      </header>

      <section className="mp-release" aria-labelledby="mp-release-title">
        <p className="mp-eyebrow">
          {release.kind} · {release.year}
        </p>
        <h1 id="mp-release-title">{release.title}</h1>
        <p className="mp-artist">{release.artist}</p>
        <p className="mp-meta">
          {count} {count === 1 ? "song" : "songs"}, {minutes(total)} minutes · {release.label}
        </p>

        <ol className="mp-tracks" aria-label={`${release.title} tracklist`}>
          {release.tracks.map((track) => {
            const current = track.id === sounding.id;
            return (
              <li key={track.id}>
                <button
                  type="button"
                  className="mp-track"
                  aria-current={current ? "true" : undefined}
                  onClick={() => props.onPlay(track)}
                >
                  <span className="mp-track-n">
                    {current ? (
                      <>
                        <SoundingIcon size={14} className="mp-sounding" />
                        <span className="mp-sr">{playing ? "Playing" : "Paused"}, </span>
                      </>
                    ) : (
                      track.number
                    )}
                  </span>
                  <span className="mp-track-title">{track.title}</span>
                  <span className="mp-track-time">{clock(track.seconds)}</span>
                </button>
              </li>
            );
          })}
        </ol>
        <p className="mp-liner">{release.liner}</p>
      </section>

      <footer className="mp-credits">
        <p>
          Sleeves: <em>{ALBUM.title}</em> by{" "}
          <a href={ALBUM.credit.profile}>{ALBUM.credit.photographer}</a>, <em>{SINGLE.title}</em> by{" "}
          <a href={SINGLE.credit.profile}>{SINGLE.credit.photographer}</a>, on Unsplash.
        </p>
        <p>{tierLine(props.capabilities)}</p>
      </footer>
    </main>
  );
}

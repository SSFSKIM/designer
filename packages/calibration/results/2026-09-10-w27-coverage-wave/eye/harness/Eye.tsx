/**
 * The eye-sheet harness: one page carrying the 0.16.0 features the shipped demo
 * does not put on screen, at fixed viewport boxes a capture script can clip.
 *
 * Two trees, as everywhere in this repo: the *ground* is ordinary page DOM (the
 * structured backdrops and the controls that drive the captures), and the
 * *glass* lives in `PlanePortal`, because X1 puts glass in viewport-fixed
 * planes. Both trees position with the same `position: fixed` numbers, so they
 * line up by declaration rather than by measurement.
 *
 * Nothing here is a product surface. It exists so the release's eye sheet can
 * show a tinted `GlassButton`, a tinted `GlassGroup`, the four ink levels, an
 * unsplit toolbar beside a split one, and the dark-scheme material — none of
 * which the demo or the playground has a live instance of.
 */

import {
  GlassButton,
  GlassGroup,
  GlassMorph,
  GlassSurface,
  GlassToolbar,
  GlassToolbarSpacer,
  PlanePortal,
  useGlassCapabilities,
  useGlassRoot,
} from "@vitreajs/vitrea-react";
import { useEffect, useRef, useState, type ReactNode } from "react";

/** The registered texture the second capsule sits over: static, drawn once. */
const TEXTURE_ID = "eye.texture";

function EyeTexture(props: { readonly scheme: "light" | "dark" }): ReactNode {
  const root = useGlassRoot();
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (canvas === null || root === null) return;
    const context = canvas.getContext("2d");
    if (context === null) return;
    const dpr = window.devicePixelRatio;
    const { width, height } = canvas.getBoundingClientRect();
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
    context.setTransform(dpr, 0, 0, dpr, 0, 0);
    // The same hard vertical repeat as the DOM half of this row, so the two
    // sampling backends are compared over the same kind of structure.
    for (let x = 0; x < width; x += 20) {
      context.fillStyle = props.scheme === "dark" ? "#0b0d12" : "#f4f6f8";
      context.fillRect(x, 0, 8, height);
      context.fillStyle = `hsl(${(x / width) * 150 + 200} 70% ${props.scheme === "dark" ? 38 : 52}%)`;
      context.fillRect(x + 8, 0, 12, height);
    }
    root.setBackdropTexture(TEXTURE_ID, { kind: "canvas", canvas });
    return () => root.setBackdropTexture(TEXTURE_ID, undefined);
  }, [props.scheme, root]);

  return <canvas ref={ref} className="eye-texture" aria-hidden="true" />;
}

/** The group ids the capture script asks the runtime about, by row. */
export const EYE_GROUPS = [
  "eye-bar-split",
  "eye-bar-split-1",
  "eye-bar-plain",
  "eye-tint-a",
  "eye-tint-b",
  "eye-tint-c",
  "eye-tint-d",
  "eye-group-tint",
  "eye-ink",
  "eye-presence",
  "eye-morph-materialize",
  "eye-morph-matched",
  "eye-lens",
  "eye-lens-texture",
] as const;

function StateProbe(props: { readonly id: string }): ReactNode {
  const state = useGlassCapabilities(props.id);
  return (
    <span
      data-eye-state={props.id}
      data-renderer={state?.activeRenderer ?? "—"}
      data-backend={state?.samplingBackend ?? "—"}
      data-health={state?.health ?? "—"}
      data-demotion={state?.demotionReason ?? "—"}
    />
  );
}

export function Eye(props: { readonly scheme: "light" | "dark" }): ReactNode {
  const [present, setPresent] = useState(true);
  const [materializeOpen, setMaterializeOpen] = useState(false);
  const [matchedOpen, setMatchedOpen] = useState(false);

  return (
    <>
      {/* ── ground: structured backdrops and the capture's own controls ─────── */}
      <main className="eye-page">
        <div className="eye-ground eye-ground--a" data-eye-clip="toolbar-split" />
        <div className="eye-ground eye-ground--b" data-eye-clip="tint-ink" />
        <div className="eye-ground eye-ground--c" data-eye-clip="presence" />
        <div className="eye-ground eye-ground--d" data-eye-clip="lens" />
        <EyeTexture scheme={props.scheme} />

        <div className="eye-controls">
          <button type="button" data-eye="presence-toggle" onClick={() => setPresent((v) => !v)}>
            presence {present ? "on" : "off"}
          </button>
          <button
            type="button"
            data-eye="materialize-toggle"
            onClick={() => setMaterializeOpen((v) => !v)}
          >
            materialize {materializeOpen ? "open" : "closed"}
          </button>
          <button
            type="button"
            data-eye="matched-toggle"
            onClick={() => setMatchedOpen((v) => !v)}
          >
            matched {matchedOpen ? "open" : "closed"}
          </button>
          <span data-eye="scheme">{props.scheme}</span>
        </div>

        <div className="eye-probes">
          {EYE_GROUPS.map((id) => (
            <StateProbe key={id} id={id} />
          ))}
        </div>
      </main>

      {/* ── row A: a toolbar that splits its shared background, and one that does not */}
      <PlanePortal plane="base">
        <div className="eye-bar eye-bar--split">
          <GlassToolbar
            aria-label="Split toolbar"
            className="eye-toolbar"
            groupProps={{ id: "eye-bar-split" }}
          >
            <GlassButton className="eye-control">Share</GlassButton>
            <GlassButton className="eye-control">Duplicate</GlassButton>
            <GlassToolbarSpacer kind="flexible" />
            <GlassButton className="eye-control" sharedBackground="hidden" tint="#ff9500">
              Publish
            </GlassButton>
          </GlassToolbar>
        </div>
        <div className="eye-bar eye-bar--plain">
          <GlassToolbar
            aria-label="Unsplit toolbar"
            className="eye-toolbar"
            groupProps={{ id: "eye-bar-plain" }}
          >
            <GlassButton className="eye-control">Share</GlassButton>
            <GlassButton className="eye-control">Duplicate</GlassButton>
            <GlassButton className="eye-control" tint="#ff9500">
              Publish
            </GlassButton>
          </GlassToolbar>
        </div>
      </PlanePortal>

      {/* ── row B: tinted buttons, a tinted group, the four ink levels ───────── */}
      <PlanePortal plane="base">
        <div className="eye-tints">
          <GlassGroup id="eye-tint-a">
            <GlassButton className="eye-control eye-control--wide" tint="#ff9500">
              Orange
            </GlassButton>
          </GlassGroup>
          <GlassGroup id="eye-tint-b">
            <GlassButton className="eye-control eye-control--wide" tint="#0a84ff">
              Blue
            </GlassButton>
          </GlassGroup>
          <GlassGroup id="eye-tint-c">
            <GlassButton className="eye-control eye-control--wide" tint="rgb(255 149 0 / 50%)">
              Half
            </GlassButton>
          </GlassGroup>
          <GlassGroup id="eye-tint-d">
            <GlassButton className="eye-control eye-control--wide">Untinted</GlassButton>
          </GlassGroup>
        </div>

        <div className="eye-group-tint">
          <GlassGroup id="eye-group-tint" tint="#30d158">
            <GlassSurface className="eye-plate eye-plate--small" radius={18} thickness={10}>
              <strong>inherits</strong>
              <span>the group&rsquo;s seed</span>
            </GlassSurface>
            <GlassSurface className="eye-plate eye-plate--small" radius={18} thickness={10} tint={null}>
              <strong>tint={"{null}"}</strong>
              <span>opts out</span>
            </GlassSurface>
          </GlassGroup>
        </div>

        <div className="eye-ink">
          <GlassGroup id="eye-ink">
            <GlassSurface className="eye-plate eye-plate--ink" radius={22} thickness={12}>
              <p className="ink ink--primary">--vitrea-foreground · primary label</p>
              <p className="ink ink--secondary">--vitrea-foreground-secondary · holds 4.5</p>
              <p className="ink ink--tertiary">--vitrea-foreground-tertiary · supporting</p>
              <p className="ink ink--quaternary">--vitrea-foreground-quaternary · decoration</p>
              <hr className="ink-rule" />
            </GlassSurface>
          </GlassGroup>
        </div>
      </PlanePortal>

      {/* ── row C: presence, and the two morph transitions ───────────────────── */}
      <PlanePortal plane="base">
        <div className="eye-presence">
          <GlassGroup id="eye-presence">
            <GlassSurface
              className="eye-plate eye-plate--presence"
              radius={22}
              thickness={12}
              present={present}
              data-eye-host="presence"
            >
              <strong>present={present ? "{true}" : "{false}"}</strong>
              <span>the content stays where the app wrote it</span>
            </GlassSurface>
          </GlassGroup>
        </div>

        <div className="eye-morph eye-morph--materialize">
          <GlassGroup id="eye-morph-materialize">
          <GlassMorph
            open={materializeOpen}
            transition="materialize"
            radius={14}
            openRadius={22}
            thickness={8}
            openThickness={16}
            placement="below-start"
            gap={10}
            className="eye-platter"
            aria-label="materialize"
          >
            {({ open }) =>
              open ? (
                <div className="eye-platter__body">
                  <strong>materialize</strong>
                  <span>two bodies, each on its own geometry</span>
                </div>
              ) : (
                <button
                  type="button"
                  className="eye-control"
                  onClick={() => setMaterializeOpen(true)}
                >
                  materialize ▾
                </button>
              )
            }
          </GlassMorph>
          </GlassGroup>
        </div>

        <div className="eye-morph eye-morph--matched">
          <GlassGroup id="eye-morph-matched">
          <GlassMorph
            open={matchedOpen}
            transition="matchedGeometry"
            radius={14}
            openRadius={22}
            thickness={8}
            openThickness={16}
            placement="below-start"
            gap={10}
            className="eye-platter"
            aria-label="matched geometry"
          >
            {({ open }) =>
              open ? (
                <div className="eye-platter__body">
                  <strong>matchedGeometry</strong>
                  <span>one body travelling between two shapes</span>
                </div>
              ) : (
                <button type="button" className="eye-control" onClick={() => setMatchedOpen(true)}>
                  matched ▾
                </button>
              )
            }
          </GlassMorph>
          </GlassGroup>
        </div>
      </PlanePortal>

      {/* ── row D: the lens answering the pointer ────────────────────────────── */}
      <PlanePortal plane="base">
        <div className="eye-lens">
          <GlassGroup id="eye-lens">
            <GlassButton className="eye-capsule" capsule thickness={14} data-eye-host="lens">
              Capsule
            </GlassButton>
          </GlassGroup>
        </div>
        <div className="eye-lens eye-lens--texture">
          <GlassGroup id="eye-lens-texture" backdrop={{ kind: "texture", id: TEXTURE_ID }}>
            <GlassButton
              className="eye-capsule"
              capsule
              thickness={14}
              data-eye-host="lens-texture"
            >
              Capsule
            </GlassButton>
          </GlassGroup>
        </div>
      </PlanePortal>
    </>
  );
}

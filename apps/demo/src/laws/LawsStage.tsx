/**
 * The laws page's instrument window.
 *
 * The site's split, for the site's reason: glass lives in viewport-fixed planes
 * (X1), so the stage is fixed and the column beside it is what scrolls. And the
 * site's two trees, for the site's reason: the ordinary DOM behind the glass
 * (`LawsGround`) and the same geometry inside the plane (`LawsGlass`) are written
 * twice with identical layout rules, so they line up by construction.
 *
 * One more tree than the site has. The glass-over-glass law puts its pane on the
 * OVERLAY plane, and a surface in that plane's host layer needs its own mirror of
 * the stage's box to be positioned in, so `LawsGlass` is rendered once per plane
 * and draws only the surfaces that belong to the plane it was given.
 *
 * Placement follows `DESIGN.md` §9: top-and-left aligned stacks with a fixed
 * inset, separate sampling groups more than 48 px apart, and nothing in the
 * viewport's origin corner, which belongs to the column.
 */

import { GlassGroup, GlassSurface, type GlassPlane } from "@vitreajs/vitrea-react";
import type { ReactNode } from "react";

import { StageBackdrop } from "../site/StageBackdrop";
import { TONE_SPANS } from "./law";
import { LawsBackdrop, paintChecker, paintFlat, paintSplit, paintText, type Painter } from "./LawsBackdrop";

export type LawMode = "tone" | "tint" | "body" | "lens" | "nested";

export const TEXTURE_SOURCE_ID = "vitrea.laws.stage";

/** The groups each law puts on the planes, for the runtime readouts. */
export const GROUPS_BY_MODE: Record<LawMode, readonly { id: string; label: string }[]> = {
  tone: [{ id: "laws-tone", label: "laws-tone (registered texture, declared level)" }],
  tint: [
    { id: "laws-tint-dark", label: "laws-tint-dark (registered texture, dark half)" },
    { id: "laws-tint-light", label: "laws-tint-light (registered texture, light half)" },
  ],
  body: [{ id: "laws-body", label: "laws-body (registered texture)" }],
  lens: [{ id: "laws-lens", label: "laws-lens (registered texture)" }],
  nested: [
    { id: "laws-nested-base", label: "laws-nested-base (registered texture, base plane)" },
    { id: "laws-nested-over", label: "laws-nested-over (no texture, overlay plane)" },
  ],
};

/** The tint bed's two halves, as linear levels. Dark enough and light enough to differ. */
export const TINT_GROUNDS = { dark: 0.06, light: 0.8 } as const;

/** The nested law's geometry: `scenes.json`'s own `glass-over-glass` component. */
export const NEST = {
  base: { width: 220, height: 130, radius: 24 },
  over: { width: 120, height: 56, radius: 16, offsetY: -8 },
} as const;

/** The authored thickness every surface on this page declares, so only the laws differ. */
const THICKNESS = 8;

/**
 * X6's hint, load-bearing here as on the site: it is the one mechanism for telling
 * the runtime what it cannot see about the ground, and the foreground decision
 * only has a backdrop to reason about when a group declares one. The stage is a
 * dark instrument except where a law paints its own ground, and those groups
 * declare the level they paint.
 */
const STAGE_HINT = { tone: "dark", luminance: 0.16 } as const;

export interface LawsStageProps {
  readonly mode: LawMode;
  /** The tone law's ground, linear 0..1: what the reader is driving. */
  readonly toneLevel: number;
  /** The tint law's seed and strength, already folded into one CSS colour. */
  readonly tint: string;
  /** The body law's short span, CSS px. */
  readonly bodySpan: number;
  readonly animate: boolean;
}

/* ── The ordinary DOM behind the glass ─────────────────────────────────────── */

/*
 * Only the nested law keeps the site's legend, because only it keeps the site's
 * ground: the legend's dim ink was chosen for that dark field and holds no
 * contrast over a checkerboard, a page of text, a split ground or a ground the
 * reader is driving. What those stages mean is in the column.
 */
const LEGENDS: Readonly<Record<LawMode, string | null>> = {
  tone: null,
  tint: null,
  body: null,
  lens: null,
  nested: "A base surface over the texture, and a pane over the base surface.",
};

export function LawsGround(props: LawsStageProps): ReactNode {
  const { mode } = props;
  const painter: Painter | null =
    mode === "tone"
      ? paintFlat(props.toneLevel)
      : mode === "tint"
        ? paintSplit(TINT_GROUNDS.dark, TINT_GROUNDS.light)
        : mode === "body"
          ? paintText
          : mode === "lens"
            ? paintChecker
            : null;
  const legend = LEGENDS[mode];

  return (
    <div className="stage" data-mode={mode} role="region" aria-label="Material window">
      {painter === null ? (
        <StageBackdrop sourceId={TEXTURE_SOURCE_ID} animate={props.animate} />
      ) : (
        <LawsBackdrop sourceId={TEXTURE_SOURCE_ID} painter={painter} />
      )}
      {legend === null ? null : <p className="stage__legend">{legend}</p>}
    </div>
  );
}

/* ── The same geometry, inside a plane ─────────────────────────────────────── */

export function LawsGlass(props: LawsStageProps & { readonly plane: GlassPlane }): ReactNode {
  const { mode, plane } = props;

  return (
    <div className="stage stage--mirror" data-mode={mode} data-plane={plane} role="region" aria-label="Live vitrea surfaces">
      <div className="stage__stack">
        {mode === "tone" && plane === "base" ? (
          /*
           * W9. Two plates at the size law's floor and past its ceiling, one
           * authored thickness, one group over one flat ground whose level the
           * group also declares: the page paints the ground, so it is stating a
           * fact rather than estimating one, and the ink is chosen against the
           * material each plate is actually showing.
           */
          <GlassGroup
            id="laws-tone"
            backdrop={{ kind: "texture", id: TEXTURE_SOURCE_ID }}
            hint={{ tone: props.toneLevel < 0.5 ? "dark" : "light", luminance: props.toneLevel }}
          >
            <GlassSurface
              className="plate plate--sweep plate--sweep-c"
              radius={26}
              thickness={THICKNESS}
              data-testid="tone-large"
            >
              <strong>{TONE_SPANS.large}px</strong>
            </GlassSurface>
            <GlassSurface
              className="plate plate--sweep plate--sweep-a"
              radius={12}
              thickness={THICKNESS}
              data-testid="tone-small"
            >
              <strong>{TONE_SPANS.small}px</strong>
            </GlassSurface>
          </GlassGroup>
        ) : null}

        {mode === "tint" && plane === "base" ? (
          /*
           * W10. The same seed at the same strength on two plates, each in a
           * group of its own over its own half of the ground, so each group can
           * declare the level it actually sits over. The row keeps them well past
           * the 48 px two sampling paddings need.
           */
          <div className="laws-row">
            <GlassGroup
              id="laws-tint-dark"
              backdrop={{ kind: "texture", id: TEXTURE_SOURCE_ID }}
              hint={{ tone: "dark", luminance: TINT_GROUNDS.dark }}
            >
              <GlassSurface
                className="plate plate--laws-tint"
                radius={26}
                thickness={THICKNESS}
                tint={props.tint}
                data-testid="tint-dark"
              >
                <strong>over dark</strong>
              </GlassSurface>
            </GlassGroup>
            <GlassGroup
              id="laws-tint-light"
              backdrop={{ kind: "texture", id: TEXTURE_SOURCE_ID }}
              hint={{ tone: "light", luminance: TINT_GROUNDS.light }}
            >
              <GlassSurface
                className="plate plate--laws-tint"
                radius={26}
                thickness={THICKNESS}
                tint={props.tint}
                data-testid="tint-light"
              >
                <strong>over light</strong>
              </GlassSurface>
            </GlassGroup>
          </div>
        ) : null}

        {mode === "body" && plane === "base" ? (
          /*
           * W11c G1. One plate whose short side is the reader's, over text. The
           * height is the span, so the label's line box is the floor the control
           * can reach and the plate's size is exactly what is being shown.
           */
          <GlassGroup id="laws-body" backdrop={{ kind: "texture", id: TEXTURE_SOURCE_ID }} hint={STAGE_HINT}>
            <GlassSurface
              className="plate plate--laws-body"
              radius={Math.min(26, Math.round(props.bodySpan / 4))}
              thickness={THICKNESS}
              style={{ height: `${props.bodySpan}px` }}
              data-testid="body-plate"
            >
              <strong>{props.bodySpan}px</strong>
            </GlassSurface>
          </GlassGroup>
        ) : null}

        {mode === "lens" && plane === "base" ? (
          /*
           * W11c G2. One plate over the checkerboard. The rung it lenses at is
           * the policy's cap folded with what the sampling backend can deliver,
           * and both are read out beside the control rather than asserted here.
           */
          <GlassGroup
            id="laws-lens"
            backdrop={{ kind: "texture", id: TEXTURE_SOURCE_ID }}
            hint={{ tone: "mixed", luminance: 0.4 }}
          >
            <GlassSurface
              className="plate plate--laws-lens"
              radius={26}
              thickness={THICKNESS}
              data-testid="lens-plate"
            >
              <strong>lens</strong>
            </GlassSurface>
          </GlassGroup>
        ) : null}

        {mode === "nested" ? (
          /*
           * W11a, as `scenes.json` declares it: a base rrect over the texture on
           * the base plane, and a pane on the overlay plane in a group of its own
           * that samples no texture. The nest box is the same in both mirrors, so
           * the pane lands over the base surface without either measuring the
           * other. The pane is not inside the base surface's content: it is a
           * separate host on a separate plane, which is the composition the layer
           * model allows and the reference was captured in.
           */
          <div className="laws-nest">
            {plane === "base" ? (
              <GlassGroup
                id="laws-nested-base"
                backdrop={{ kind: "texture", id: TEXTURE_SOURCE_ID }}
                hint={STAGE_HINT}
              >
                <GlassSurface
                  className="plate plate--laws-nest-base"
                  radius={NEST.base.radius}
                  thickness={THICKNESS}
                  data-testid="nested-base"
                >
                  <strong>base</strong>
                </GlassSurface>
              </GlassGroup>
            ) : (
              <GlassGroup id="laws-nested-over" hint={{ tone: "light", luminance: 0.6 }}>
                <GlassSurface
                  className="plate plate--laws-nest-over"
                  plane="overlay"
                  radius={NEST.over.radius}
                  thickness={THICKNESS}
                  data-testid="nested-over"
                >
                  <strong>pane</strong>
                </GlassSurface>
              </GlassGroup>
            )}
          </div>
        ) : null}
      </div>
    </div>
  );
}

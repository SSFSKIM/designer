/**
 * The tint-and-ink plate: W27a's three published features, live (W27e G2).
 *
 * 0.16.0 shipped a tinted `GlassButton`, a `GlassGroup tint` and the four named
 * ink levels with props, README paragraphs and no instance anywhere a reader
 * could operate (the wave's Surprises, 2026-09-11). This is that instance. What
 * it is composed to show is the part a paragraph cannot: the same three
 * declarations over two grounds at once, with the material's answer to each
 * beside the other's, and the tint under the reader's hand.
 *
 * ## What each piece is, and why it is arranged this way
 *
 * - **`GlassGroup tint`** is declared on the group that holds the plate and the
 *   bookmark button. Neither member declares a colour, so both take the group's
 *   seed — which is the documented rule ("colours every member that declares no
 *   colour of its own") and the reason that group carries two members rather
 *   than one. One member would have been indistinguishable from a tinted
 *   surface.
 * - **`GlassButton tint`** is on `Publish`, in a group of its own. A second seed
 *   inside the first group is one optics pass asked to carry two colours, which
 *   is the dev-mode `tint-mixing` warning; the fix the README names for exactly
 *   this composition is the group this button already has.
 * - **The four ink levels** are on one surface, side by side. The specimens
 *   carry the levels and the word naming each one stays in the primary ink:
 *   tertiary and quaternary sit below WCAG's body-text floor *by design* — the
 *   README says so and Apple says so — so a specimen is what it is, a decorative
 *   sample, and the label that identifies it is readable.
 *
 * Naming `--vitrea-foreground-quaternary` in this page's stylesheet is also what
 * turns on the runtime's own advisory about it: every surface in the playground
 * below the material's thin/thick knee now reports
 * `quaternary-ink-on-thin-material` once, in the panel. That finding is correct
 * — the playground is full of thin controls and this document now names the
 * token — and showing it is worth more than hiding the token behind an inline
 * style the scan cannot see.
 *
 * ## Why the grounds are bytes
 *
 * A hint is a declared fact about what is behind a group, and a hint that lies
 * makes everything downstream of it a lie too. So both grounds are painted from
 * the same 8-bit value the stated level is decoded from: the number the group
 * declares is the number the ground has, rather than a plausible one typed
 * beside a colour someone picked.
 *
 * ## Why the controls are page furniture
 *
 * They sit in the page's own column on the page's own ink, never on the glass,
 * for the reason the presence controls do (`App.tsx`): a control that changes
 * the material must stay readable at every setting of the thing it changes,
 * including a full-strength tint that would take the ink with it.
 */

import {
  GlassButton,
  GlassGroup,
  GlassIconButton,
  GlassSurface,
  PlanePortal,
  useGlassCapabilities,
} from "@vitreajs/vitrea-react";
import { useState, type ReactNode } from "react";

/**
 * sRGB's transfer function, inverted: an 8-bit ground value as a linear level.
 *
 * `BackdropHint.luminance` is a relative luminance, which is linear light, and
 * the ground below is a flat grey — so one decode is the whole conversion, with
 * no averaging over a gradient to make the declared number an approximation of
 * anything.
 */
export function linearLevel(byte: number): number {
  const encoded = byte / 255;
  return encoded <= 0.04045 ? encoded / 12.92 : ((encoded + 0.055) / 1.055) ** 2.4;
}

/** The two grounds, each as the byte it is painted with. */
export const INK_GROUNDS = [
  { key: "light", tone: "light", byte: 231 },
  { key: "dark", tone: "dark", byte: 29 },
] as const satisfies readonly {
  readonly key: string;
  readonly tone: "light" | "dark";
  readonly byte: number;
}[];

export type InkGroundKey = (typeof INK_GROUNDS)[number]["key"];

/**
 * The four levels, in the order they are published.
 *
 * The token is not read here — `styles.css` owns every colour in this app — but
 * it is named beside the level so the class names below are traceable to the
 * property they style against.
 */
export const INK_LEVELS = [
  { level: "primary", token: "--vitrea-foreground" },
  { level: "secondary", token: "--vitrea-foreground-secondary" },
  { level: "tertiary", token: "--vitrea-foreground-tertiary" },
  { level: "quaternary", token: "--vitrea-foreground-quaternary" },
] as const;

/**
 * A seed and a strength, as the one CSS colour the API takes.
 *
 * The colour's own alpha *is* the tint's strength — `rgb(255 149 0 / 50%)` is a
 * half-strength orange — so a strength slider is a slider over the alpha rather
 * than a second prop, and the composed string is shown beside the controls so a
 * reader can see the exact value the props receive.
 */
export function tintDeclaration(hex: string, strengthPercent: number): string {
  const channels = [1, 3, 5].map((offset) => Number.parseInt(hex.slice(offset, offset + 2), 16));
  return `rgb(${channels.join(" ")} / ${String(strengthPercent)}%)`;
}

const GROUP_SEED = "#3f7fe0";
const BUTTON_SEED = "#ff9500";

/** The group id a ground's plate and bookmark share; the readout reads this one. */
export const inkGroupId = (ground: InkGroundKey): string => `ink-${ground}`;

/** The group the tinted button steps out into, so the two seeds never meet. */
const inkActionGroupId = (ground: InkGroundKey): string => `ink-${ground}-action`;

/**
 * What the runtime resolved for one ground's group — never what was asked for.
 *
 * The plate is drawn on whichever tier the visiting machine could give it, and a
 * reader comparing two grounds has to know which one that was; `GlassGroupState`
 * is the only honest source for it, the same one the panel reads.
 */
function TierReadout(props: { readonly ground: InkGroundKey }): ReactNode {
  const state = useGlassCapabilities(inkGroupId(props.ground));

  return (
    <span className="ink-ground__tier" data-testid={`ink-tier-${props.ground}`}>
      {state === undefined || state === null
        ? "resolving"
        : `${state.activeRenderer} · ${state.samplingBackend}`}
    </span>
  );
}

function TintControl(props: {
  readonly id: string;
  readonly label: string;
  readonly seed: string;
  readonly strength: number;
  readonly onSeedChange: (next: string) => void;
  readonly onStrengthChange: (next: number) => void;
}): ReactNode {
  return (
    <div className="ink-control">
      <span className="ink-control__label">{props.label}</span>
      <div className="ink-control__row">
        <label>
          <span className="visually-hidden">{props.label} seed</span>
          <input
            type="color"
            value={props.seed}
            data-testid={`${props.id}-seed`}
            onChange={(event) => props.onSeedChange(event.target.value)}
          />
        </label>
        <label className="ink-control__strength">
          <span className="visually-hidden">{props.label} strength</span>
          <input
            type="range"
            min={0}
            max={100}
            step={5}
            value={props.strength}
            data-testid={`${props.id}-strength`}
            onChange={(event) => props.onStrengthChange(Number(event.target.value))}
          />
        </label>
      </div>
      <p className="ink-control__value" data-testid={`${props.id}-value`}>
        {tintDeclaration(props.seed, props.strength)}
      </p>
    </div>
  );
}

export interface TintInkPlateProps {
  readonly onAction: (action: string) => void;
}

export function TintInkPlate(props: TintInkPlateProps): ReactNode {
  const [groupSeed, setGroupSeed] = useState(GROUP_SEED);
  const [groupStrength, setGroupStrength] = useState(45);
  const [buttonSeed, setButtonSeed] = useState(BUTTON_SEED);
  const [buttonStrength, setButtonStrength] = useState(100);

  const groupTint = tintDeclaration(groupSeed, groupStrength);
  const buttonTint = tintDeclaration(buttonSeed, buttonStrength);

  return (
    <>
      <section className="region region--ink" aria-label="Tint and ink">
        <div className="ink-controls">
          <TintControl
            id="group-tint"
            label="GlassGroup tint"
            seed={groupSeed}
            strength={groupStrength}
            onSeedChange={setGroupSeed}
            onStrengthChange={setGroupStrength}
          />
          <TintControl
            id="button-tint"
            label="GlassButton tint"
            seed={buttonSeed}
            strength={buttonStrength}
            onSeedChange={setButtonSeed}
            onStrengthChange={setButtonStrength}
          />
        </div>

        {INK_GROUNDS.map((ground) => (
          <div
            key={ground.key}
            className="ink-ground"
            data-ground={ground.key}
            // The one colour in this app that is not a visual decision: it is the
            // fact the group's hint declares, so it is derived from the same byte.
            style={{ background: `rgb(${String(ground.byte)} ${String(ground.byte)} ${String(ground.byte)})` }}
          >
            <p className="ink-ground__label">
              {ground.key} ground · {linearLevel(ground.byte).toFixed(3)} linear ·{" "}
              <TierReadout ground={ground.key} />
            </p>
          </div>
        ))}
      </section>

      {/*
        The glass, in the base plane, positioned over the band the page drew.
        Both boxes are the same fixed rectangle and the same three rows, so the
        surfaces stand on their own grounds without either grid knowing about
        the other's contents.
      */}
      <PlanePortal plane="base">
        <div className="ink-overlay" role="region" aria-label="Tint and ink levels">
          <div className="ink-overlay__controls" />
          {INK_GROUNDS.map((ground) => (
            <div className="ink-row" key={ground.key}>
              <GlassGroup
                id={inkGroupId(ground.key)}
                hint={{ tone: ground.tone, luminance: linearLevel(ground.byte) }}
                tint={groupTint}
              >
                <GlassSurface
                  className="ink-plate"
                  radius={18}
                  thickness={12}
                  data-testid={`ink-plate-${ground.key}`}
                >
                  {INK_LEVELS.map((entry) => (
                    <span className={`ink-level ink-level--${entry.level}`} key={entry.level}>
                      {/*
                        Decorative by construction: a specimen exists to be looked
                        at, and two of the four levels are documented as below the
                        body-text floor. The word beside it carries the meaning and
                        keeps the primary ink.
                      */}
                      <span className="ink-level__specimen" aria-hidden="true">
                        Aa
                      </span>
                      <span className="ink-level__name">{entry.level}</span>
                    </span>
                  ))}
                </GlassSurface>
                <GlassIconButton
                  aria-label={`Bookmark the ${ground.key} ground`}
                  className="control control--icon"
                  data-testid={`ink-bookmark-${ground.key}`}
                  onClick={() => props.onAction(`bookmark ${ground.key}`)}
                >
                  <span aria-hidden="true">☆</span>
                </GlassIconButton>
              </GlassGroup>

              <GlassGroup
                id={inkActionGroupId(ground.key)}
                hint={{ tone: ground.tone, luminance: linearLevel(ground.byte) }}
              >
                <GlassButton
                  className="control control--compact"
                  tint={buttonTint}
                  data-testid={`ink-publish-${ground.key}`}
                  onClick={() => props.onAction(`publish ${ground.key}`)}
                >
                  Publish
                </GlassButton>
              </GlassGroup>
            </div>
          ))}
        </div>
      </PlanePortal>
    </>
  );
}

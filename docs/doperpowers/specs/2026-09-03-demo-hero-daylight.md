# Demo hero on a daylight ground (2026-09-03)

> Child of `2026-08-24-vitrea-liquid-glass-design.md` C9b (the public demo site),
> opened from the user's hero-ground decision. The material it shows is W12's;
> it lands after W12 G3 so the hero shows the landed body.

## Purpose

The site's design law (`apps/demo/DESIGN.md` §0) argues that dark is where glass
is easy and that daylight is the harder, unclaimed demonstration — and then puts
the one live window on a near-black ground, where the material adapts onto the
ground and collapses honestly to flat grey plates: no frost, no visible lensing
over the dim field, no size story beyond the labels. Move the instrument window
to a light ground so the page keeps its own promise: the frost, the soft shadow
and the size law read directly on first sight.

## Acceptance

- The material stage (the hero) runs on a light cool ground with dark stage ink,
  dark hairlines and a dark graticule; the colour field survives as gentle tints
  rather than washing to white; the captions and every control label on glass are
  readable.
- `apps/demo/e2e/contrast.spec.ts` holds its floors on the new ground (body text
  4.5:1, large text 3:1, sampled across the drift), `site.spec.ts` and
  `laws.spec.ts` pass, and `pnpm --filter demo dev` reports zero placement
  diagnostics.
- The tone stage's ground sweep, the reference pair (fixture rasters) and the
  behaviour and accessibility stages are unchanged in what they demonstrate.
- `DESIGN.md` §0–§1 say what the stage is now; the token file and the law agree.
- By eye on the landed W12 material at 2x, next to the dark version: the user's
  verdict, recorded here.

## Design (advisory unless marked)

Prototype values that produced the screenshot the user chose (binding as the
starting point, free to tune while the acceptance holds):

- `StageBackdrop`: `DEFAULT_GROUND.fill` `#0c151a` → `#dfe5ec`,
  `DEFAULT_GROUND_LUMINANCE` 0.0069 → the fill's real linear luminance (about
  0.77 — compute it, do not copy the estimate); the colour lobes composited by
  `multiply` instead of `lighter`, `LOBE_LIGHTNESS` 0.4 → about 0.86 so the
  tints stay gentle; the graticule stroke `rgb(255 255 255 / 0.11)` →
  `rgb(0 0 0 / 0.10)`.
- Tokens: `--stage-ink` → about `oklch(0.250 0.017 232)`, `--stage-ink-dim` →
  about `oklch(0.450 0.011 232)`, `--stage-rule` → `rgb(0 0 0 / 0.14)`;
  `--stage-0` / `--stage-1` / `--stage-graticule` / `--accent-stage` retuned to
  the light surface by the same rule that set them for the dark one.
- `.stage--mirror` and `.platter` declare `color-scheme: dark` because the
  ground was dark; on a light ground the fallback ink must resolve light-scheme.
  Change the declaration and keep its doc comment true.
- The hinted groups' `DEFAULT_GROUND_LUMINANCE` is a real level the runtime
  trusts over sampling: it must be the new ground's, not an estimate.
- The contrast test's sample phases and floors do not change; if a label fails,
  fix the ink or the field, not the test.

## Decision Log

### Decision Log 1 — B, the light ground (2026-09-03; user-decided)

Two screenshots on the current build (ω 0.8 material, GPU tier, 2x): A, the dark
window as shipped; B, the light-ground prototype with dark ink and graticule.
Recommendation given: B, because the page's own law calls daylight the harder
demonstration and the dark ground hides the frost. **Decided (user): "B indeed."**
Sequenced after W12 G3 lands so the by-eye check is on the landed body.

## Surprises

Two things the Design section did not anticipate, both found by running the page
rather than by reading it.

1. **The graticule's stroke belongs to the ground, not to the page.** Turning the
   one stroke constant black made it invisible on the *tone* stage, whose ground is
   a grey swept from near-black — so the one stage whose whole subject is what a
   surface reads underneath it lost the high-frequency half of its backdrop. The
   stroke became a third member of `StageGroundPaint` alongside `fill` and `field`:
   the window's own ground affords black at 0.10, the tone stage's affords white at
   0.11, and each ground now states its own. Nothing about the tone stage's sweep
   moved.
2. **`e2e/site.spec.ts`'s "untinted" premise was a statement about the dark
   ground.** It asserted that the 40 px plate is *not* white, because on a
   near-black ground backdrop tone adaptation pulled its body onto the ground. The
   light window sits well above the band that law operates in, so nothing adapts the
   colour away and both plates start at the material's own white. The premise was
   re-derived rather than relaxed: the two plates now have to share the colour
   `255,255,255` **and** differ in alpha, which is the size law still separating them
   (measured `rgba(255, 255, 255, 0.79)` on the 112 px plate against
   `rgba(255, 255, 255, 0.815)` on the 40 px one). The tint assertions downstream are
   untouched.

## Deferred

- `e2e/reference-panel.gpu.spec.ts` fails on this machine at a mean encoded-luma
  delta of 0.021933303624480347 against a bound of 0.02. It is **not** this round's:
  the same test fails with the bit-identical number on the clean tree at 6ff1319,
  and the reference stage draws over fixture rasters that this round does not touch.
  It belongs to the fidelity waves' bed, not to the demo's ground.

## Tracking

| step | where | status |
| --- | --- | --- |
| prototype | this session's screenshots (scratch) | DONE 2026-09-03 |
| the round | worktree branch, refereed by the demo suites | DONE 2026-09-03 |
| landing | cherry-picked onto `main` (52092d8) once G3 was held at `main`'s material (claims §5.58): the body under the hero is the landed one either way; by-eye verdict on the live site is the user's | LANDED 2026-09-03 |

The round's evidence: `pnpm --filter demo test:e2e` 33 passed, 1 failed (the
pre-existing GPU reference-panel cell above); `pnpm --filter demo lint` clean;
`pnpm run ci` exit 0. `e2e/contrast.spec.ts` holds all four floors on the new
ground, worst per test — control labels 6.55:1 ("Publish"), segment labels 15.73:1
("Month"), plate labels on the material stage 15.53:1 ("112px"), plate labels across
the tone sweep 4.62:1 ("40px" at ground 0.026) — against floors of 4.5, 4.5, 3 and 3.
`pnpm --filter demo dev` on port 5177, loaded at 1440x900 deviceScaleFactor 2 with
the console captured, reported zero placement diagnostics (three messages, all
Vite's HMR handshake and React's DevTools notice).

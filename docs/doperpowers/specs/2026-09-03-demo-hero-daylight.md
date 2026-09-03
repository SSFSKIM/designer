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

## Tracking

| step | where | status |
| --- | --- | --- |
| prototype | this session's screenshots (scratch) | DONE 2026-09-03 |
| the round | worktree branch, refereed by the demo suites | OPENED 2026-09-03 |
| landing | after W12 G3 lands on `main` | — |

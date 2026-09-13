# W27e G2 (operator half) — declared before the change

Committed before any file under `packages/*/src` moved. Claims section reserved: **§5.140**.
Gate: W27 coverage wave, child W27e gate G2 (§Children); §Design *Where each feature lives*
(binding); contracts **X1**, **X2**, **X4**, X9; Decision Logs 9, 15 and 16. Consumes claims
§5.137 (the operator's semantics and its two tiers) and §5.138 (the selector reading).

Nothing here reopens Decision Log 15 or 16. The ink colour, the alpha, the ladder, the floor and
the selector arrive as rulings; what this gate decides is only how they are carried by the runtime,
and every such decision is named in §2 so that it can be read against the design rather than found
in a diff.

## 1. What is being built

1. Apple's label operator in the runtime, as a function of an ink and nothing else.
2. The four published ink tokens re-derived through it — pure black / pure white at the macOS
   ladder's alphas, Decision Log 9's WCAG 4.5 floor kept as a minimum on secondary.
3. The operator applied to vitrea's own controls' labels by default, and to `asChild` content under
   `foreground="vibrant"`; the token path kept, with its precedence, for everything else.
4. The `foregroundTone` channel consumed: the ink crosses the selector's threshold through the
   channel's declared hysteresis and 180 ms crossfade instead of snapping.
5. Tier coherence pinned on the ink, and the CSS tier's residual against the per-pixel path
   measured rather than asserted.

## 2. The implementation decisions this gate takes, declared before they are taken

**(a) The operator is folded on the CPU on both tiers. No `filter` and no `mix-blend-mode` is
installed anywhere.** §5.137 §3 states the fold and the per-pixel path are the same function
because the operator carries no backdrop term, and §5.137 §4 measured them 0.00 and 0.04 code
values apart on the only two cells that can test it. Against that, a `filter` inside a host is a
measured hazard on this tier — `css-tier.ts`'s own host comment records that a `filter`, a `mask`,
an `opacity` or a blend mode on the host cuts the created layers off from the page behind them, and
§5.133 §5 measured a `mix-blend-mode` inside the host collapsing a DOM-proxied group's sampling.
A per-pixel path would also *diverge* from Apple where the two differ: §5.136 §4 found Apple
installs the operator on the automatic colour and declines to rewrite an authored one, and a filter
over a subtree saturates the author's colour too. The fold is therefore both the cheaper and the
more faithful mechanism, and the per-pixel path is not shipped.

**(b) "The operator by default on vitrea's own controls" is therefore a precedence statement.**
After Decision Log 15 (a) the published token *is* the operator's output, so the operator path and
the token path resolve to the same colour and differ only in who owns the declaration. vitrea's own
controls mark their host, and the ink stylesheet gains one rule for marked hosts at attribute
specificity (0,1,0) beside the existing `:where()` rule at (0,0,0). A marked host outranks a bare
tag or universal application rule and still loses to any application rule that names the element —
which is Apple's own behaviour on a label that names its own colour (§5.136 §4), and leaves root
Decision Log #34(c) intact.

**(c) The opt-in is spelled on the existing `foreground` prop**, as §Design writes it. That prop
today carries `ForegroundAdaptation` (the adaptation cadence), so the union `ForegroundAdaptation |
"vibrant" | "token"` makes the two axes mutually exclusive: an author who needs `sampled-async` on a
vibrant surface cannot say so. The spelling is binding and the limitation is additive to remove
later (a field on the object form), so it ships and is logged in the tracker rather than resolved
here.

**(d) The crossfade folds two ink layers into one colour.** A crossfade of two rendered texts is the
arriving ink at weight *t* composited source-over onto the departing ink at weight 1 − *t*, and
source-over is associative, so the pair folds exactly into one non-premultiplied `rgb()` that
composites over the material to the same result. The arriving pole is on top, because that is what a
fade-in is; the departing-pole-on-top ordering differs mid-fade and is recorded as a residual, not
measured against anything, since Apple's ordering is not in evidence.

**(e) The driver's threshold is the optics constant, not the tunable's.** `foregroundTone`'s
tunable carries `threshold: 0.5`; the selector Decision Log 16 ruled is
`CSS_TIER_MAPPING.foregroundCrossover` at 0.475. The driver is constructed with the crossover
substituted, because the motion package may not import an optics constant and the tunables are
advisory until calibrated. The hysteresis (0.08) and the crossfade (180 ms) are taken as declared.

**(f) Rounding.** A documented constant is published as documented; a solved bound is rounded the
way the bound may safely land. The ladder's alphas — Apple's, and Apple's × the operator's 0.95 —
are quantised to nearest 1e-6, so the dark pole publishes 0.804706 exactly as §5.137 §5 records it.
A secondary alpha solved against the WCAG floor is quantised **up** at 1e-6, which is the side a
contrast floor may land on and the rule `inkAtAlpha` already followed at 1e-3.

## 3. The files expected to move

Runtime:

- `packages/platform-web/src/vibrancy.ts` — **new**: Apple's two matrices, the matrix application,
  the level selector, the macOS ladder and the crossfade fold.
- `packages/platform-web/src/css-tier.ts` — `FOREGROUND_INK`, `FOREGROUND_INK_CHANNELS`,
  `FOREGROUND_DEFAULT`, `FOREGROUND_LEVEL_ALPHA`, `alphaFor`, `inkAtAlpha`, `foregroundInk`,
  `foregroundLevelInks`, `foregroundDeclarations`.
- `packages/platform-web/src/ink-stylesheet.ts` — the second rule.
- `packages/platform-web/src/host.ts` — the marker attribute.
- `packages/platform-web/src/root.ts` — the per-host `foregroundTone` driver, its advance, the
  marker, and the tone passed to both tiers' ink.
- `packages/react/src/surface.tsx`, `group.tsx`, `controls/button.tsx`,
  `controls/segmented-control.tsx` — the prop union and the controls' default.

Evidence and record:

- `packages/calibration/scripts/vibrancy.ts` — the operator is imported from the runtime instead of
  being defined twice; the corpus pins stay where they are.
- `packages/calibration/test/tier-coherence.test.ts` — the ink pins; the new coherence pin.
- `.changeset/` — one minor on `@vitreajs/vitrea-web`.
- `docs/doperpowers/specs/c9a-fidelity-claims.md` §5.140; the wave spec's W27e Status, Tracking row,
  Revision Notes and Deferred/tracker entries.

Nothing under `packages/renderer-webgpu`, no material profile document, no fixture, no renderer
golden, no `scenes.json` entry and no canonical `results/matrix.json` row is expected to move.

## 4. The assertions expected to move, and what causes each move

Every move below is attributed to exactly one of the four rulings: **the ink colour** (pure
black/white for `#1c1c1e`/`#f5f5f7`), **the alpha** (Apple's, and the operator's 0.95 on the light
pole), **the ladder** (macOS's, replacing the iOS one) and **the floor** (Decision Log 9's, whose
ceiling moves from opaque to the primary's alpha).

| file | assertions | cause |
| --- | ---: | --- |
| `packages/platform-web/test/css-tier.test.ts` | 8 primary-ink equalities (`#1c1c1e` / `#f5f5f7` / the `light-dark()` default) | the ink colour, the alpha |
| `packages/platform-web/test/css-tier.test.ts` | the level-alpha and floor cases (`0.6` / `0.3` / `0.18`, the two `inkAlphaHoldingContrast` probes, the crossover-driven ink pair) | the ladder, the floor |
| `packages/platform-web/test/untinted-ink.test.ts` | 2 | the ink colour, the alpha |
| `packages/platform-web/test/tint.test.ts` | 3 | the ink colour, the alpha |
| `packages/calibration/test/tier-coherence.test.ts` | 2 | the ink colour, the alpha |
| `packages/platform-web/e2e/gpu/foreground-audit.spec.ts` | 1 | the ink colour, the alpha |
| `packages/platform-web/e2e/shared/ink-precedence.spec.ts` | 2 | the ink colour, the alpha |
| `packages/platform-web/e2e/pixel/css-tier-pixels.spec.ts` | 1 | the ink colour, the alpha |

Roughly nineteen, against the "~13" the child's G3 clause estimated; the estimate was taken over the
primary-ink equalities alone and the ladder and the floor carry the rest.

## 5. The stops — what would halt this change rather than be worked around

- **S1.** Any renderer golden moves. Nothing in this change reaches `renderer-webgpu`, so a moved
  golden means the change is not what it says it is: stop and report rather than re-record.
- **S2.** Any material profile document, fixture, `scenes.json` entry or canonical
  `results/matrix.json` row moves. Same rule.
- **S3.** The CSS-tier fold measured against the per-pixel path on a real composite exceeds
  **1 code value of 255** — the bound §5.137 §4 declared for the same comparison and measured at
  0.54. Above it, §5.137 §3's "the fold loses nothing" is refuted on the shipped composite and the
  residual is named in the ledger instead of the claim being repeated.
- **S4.** The demo's contrast harness reads below the floor it holds today on any label of the
  tint-and-ink band. Apple's alpha is a deliberate loss of contrast against an opaque ink and
  Decision Log 15 (b) kept the WCAG floor as a minimum precisely so that this cannot happen; a
  reading below it means the floor's re-derivation is wrong.
- **S5.** Any browser run — Playwright suite, sheet or contrast reading — taken while the machine's
  Reduce Transparency is on. `defaults read com.apple.universalaccess reduceTransparency` must read
  **0** at the time of the run, and the value read is recorded beside every browser figure. A run
  taken at 1 is not evidence and is discarded rather than reinterpreted.

## 6. What this gate does not do

No pixel of Apple's is captured; there is no native label fixture and under the no-text fixture rule
there cannot be one (§5.137 §7), so nothing here is a measurement of vitrea against macOS. The
selector's two open questions stay open (Decision Log 16): whether Apple's input is an adapted-state
bit or a level against a threshold, and where its dark-scheme threshold sits. The ledger's §3.3 is
G3's to rewrite. The user's eye is G3's.

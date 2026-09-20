# The strip a thin σ leaves undrawn — the cause, the line, and the fix

**W30 G3b, claims §5.159b, charter Decision Log 5 (a).** Evidence for the defect
W30 G3 recorded in `results/2026-09-20-w30-g3-operators/thin-sigma-band.md` and
claims §5.159 §6.

## The cause, in one line

`packages/renderer-webgpu/src/wgsl/optics.ts`, `outer_shadow_falloff`:

```wgsl
return 0.5 * (1.0 + tanh(0.7978845608028654 * (x + 0.044715 * x * x * x)));
```

`x` is the distance to the shadow's silhouette measured in σ, negated, so it is
POSITIVE inside the silhouette and grows as the caster gets deeper or σ gets
smaller. The cubic makes the tanh argument `t` grow as the cube of it, and a
backend that lowers `tanh` to `(exp(2t) − 1)/(exp(2t) + 1)` — which is what
Metal's fast-math path does, and Chromium on this machine runs Dawn on Metal —
overflows f32's `exp` when `2t > 88.7228`. `Inf/Inf` is NaN. That happens at

    t = 44.3614  ⟺  x + 0.044715·x³ = 55.60  ⟺  x = 10.0610

so **every pixel more than 10.06 σ inside the shadow's silhouette returned NaN**.

The NaN is the shadow's `falloff`, so `shadowAlpha = alpha · falloff` is NaN, and
the optics pass's last line carries it into the alpha channel:

```wgsl
return vec4f(body.rgb + liftEncoded * (1.0 - coverage), body.a + shadowAlpha * (1.0 - coverage));
```

A coverage of exactly 1 — which is what the deep interior of a surface has — does
not stop it: `NaN · 0` is NaN. The canvas quantises the NaN to 0, so the surface
is simply absent there and the page shows through. The colour channels are fine,
which is why the composite reads as a hole rather than as a wrong colour.

## Why no shipped material had ever reached it

10.06 σ has to be less than the caster's own half-depth plus the spread. At the
macOS 26.5 σ of 15.55 that is 156 CSS px; at macOS 27's 11.0 it is 111; the
deepest caster in the whole bed is 80 (`rrect-lg`, span 160). Nothing came close.

macOS 27's σ law draws **σ(44) = 2.13**, where 10.06 σ is 21.43 CSS px — and a
44 px capsule's own centre line is 22 + 3.1 = 25.1 CSS px inside the shadow's
silhouette. That is the whole of it.

It is a property of the CASTER's depth against its own σ, which is why it lands
exactly where §5.159 §6 found it:

| component | half-depth + spread | 10.06·σ(span) | NaN |
| --- | ---: | ---: | :---: |
| `capsule-button`, span 44 | 25.1 | 21.4 | yes |
| `toolbar-group`, three span-44 members | 25.1 | 21.4 | yes |
| `rrect-sm`, span 32 | 19.1 | 21.4 | no |
| `rrect-md`, span 96 | 51.1 | 90.1 | no |
| `rrect-ml`, span 128 | 67.1 | 132.4 | no |
| `rrect-lg`, span 160 | 83.1 | 174.7 | no |

## The band, predicted from the arithmetic and then measured

For a capsule of half-height `H` centred on row `c`, NaN covers the sampled rows
where `|s − c| ≤ H + spread − 10.06·σ`, and the shadow's read is offset upward by
`offsetPx`, so the drawn rows are that band shifted DOWN by the offset. Every row
of §5.159 §6's bisect table falls out of that one expression, to the row, with no
free parameter:

| document (all on the sealed light document, capsule rows 78…121) | σ(44) | predicted | §5.159 §6 measured |
| --- | ---: | --- | --- |
| the fitted law | 2.1272 | 103.9…111.0 | **104…111** |
| the fitted law, `offsetPx` 0 | 2.1272 | 95.9…103.1 | **96…103** |
| the fitted law, `spreadPx` 0 | 2.1272 | 106.9…108.0 | **107…108** |
| `sigmaPx` 8 | 1.1672 | 94.2…120.7 | **95…121** |
| `sigmaPx` 4 (σ negative, clamped to 1e-4) | 0.0001 | 82.5…132.5, clipped at the surface | **83…121** |
| 0.19.0, `sigmaPx` 11 with the law inert | 11.0 | none | **none** |

`nan-band.py` in this directory is that expression and prints the table.

**§5.159 §6's own reading of the table — "the strip's bottom edge sits 24 CSS px
above the group field rect's bottom edge" — is a coincidence of one σ, recorded
here beside it rather than over it.** The gap is
`reach + offset + spread − (H + spread − 10.06σ) − 0.5`, which is about
`11.05·σ − 0.5` and reads 23.0 at σ = 2.13; all three rows that produced the
"constant" were at that σ. At σ = 1.1672 the same expression reads 12.4, and the
fifth row of the table above has the rect's bottom edge 12 rows below the strip's,
not 24.

## One correction to §5.159 §6's reproduction, measured

§5.159 §6 says the defect reproduces "on the macOS 27 light document as 0.19.0
ships it with `sigmaPx: 8` and no W30 leaf involved". Run at this gate, that
command does reproduce — but **not with no W30 leaf involved**, and the
difference matters for what the defect is a function of. `--material-profile`
supplies a PATCH, and the leaves it does not name come from the runtime material
its `profileKey` selects, which on this branch is the macOS 27 document W30 G3
sealed: `sigmaSlopePerSpan` 0.1314 and `sigmaThinOffsetPx` −6.8328 are live, and
`sigmaPx: 8` composes with them to **σ(44) = 1.1672**, not 8.

Captured both ways, one scene each, `--alpha`, scratch matrices:

| document | σ(44) | drawn px | declared px | IoU |
| --- | ---: | ---: | ---: | ---: |
| 0.19.0's leaves, `sigmaPx` 11 | 11.0 | 4872 | 4872 | 1.0000 |
| 0.19.0's leaves, `sigmaPx` 8, the runtime's law live | 1.1672 | — | 4872 | interior alpha 0.0000, conformance REFUSED |
| the three law leaves explicitly 0, `sigmaPx` 8 | 8.0 | 4872 | 4872 | 1.0000 |
| the three law leaves explicitly 0, `sigmaPx` 2.13 | 2.13 | 4220 | 4872 | 0.8662 |

The third row is the one §5.159 §6 believed it was taking, and it draws clean.
**The defect is a function of σ alone (against the caster's depth), and 8 CSS px
is above its threshold; 2.13 is below it.** The finding, the blocking verdict and
Decision Log 5 (a) are unaffected — the fitted law does draw σ 2.13 at span 44,
which is the row that fails — but a reader who took the reproduction literally
would look for a defect that depends on something other than σ.

## The fix

The tanh argument is clamped to ±20, in the shader and in both mirrors
(`packages/renderer-webgpu/src/wgsl/optics.ts`,
`packages/renderer-webgpu/src/material.ts`,
`packages/platform-web/src/optics.ts`):

```wgsl
let t = clamp(0.7978845608028654 * (x + 0.044715 * x * x * x), -20.0, 20.0);
return 0.5 * (1.0 + tanh(t));
```

**It is the identity, not an approximation.** `tanh` reaches exactly 1.0 in f32 by
|t| = 9.011 and in f64 by |t| = 18.2, so every |t| above 20 already returned
exactly ±1 wherever the unclamped form returned anything at all. ±20 is the
smallest round bound above f64's own saturation point, which is what lets the
same clamp stand in the JS mirrors without moving a digit of `outerShadowReachPx`
— whose bisection is the one place the f64 falloff is read for a number.

No material constant moves, no leaf is added, `DEFAULT_MATERIAL_PROFILE` is
untouched (X1).

## The proofs

| proof | result |
| --- | --- |
| `pnpm --filter @vitrea/renderer-webgpu test:golden` | **34 passed**, `git status` over `e2e/goldens` empty. They render at σ 15.55, where `t` peaks near 2 — five times under the clamp and twenty under the overflow — so byte-identity is what the clamp being the identity predicts |
| `e2e/gpu/w30-thin-sigma-coverage.spec.ts`, **new**, on the pre-fix renderer | **2 failed**: capsule 652 of 4,780 declared px undrawn (IoU 0.8636), toolbar 132 of 4,308 (IoU 0.9694); the σ sweep 15.55 / 8.96 / 2.1272 / the law reads 0 / 0 / 784 / 784 undrawn |
| the same spec, on the fixed renderer | **2 passed** |
| `pnpm --filter @vitrea/renderer-webgpu test:gpu` | **33 passed**, the two new cases included |
| the calibration reproduction at the fixed renderer | `checkerboard__capsule-button__rest`, flat σ 2.13: **4872 / 4872, IoU 1.0000**, against 4220 / 4872 and 0.8662 before |
| renderer unit suite | 511 passed |
| platform-web unit suite | 631 passed |

# The two call sites the carrier reached, as they stood for §4's captures

Reverted before anything was committed (`git status` clean outside this directory at the commit);
recorded here so §4's readings can be reproduced exactly rather than approximately. Both edits are
against `main` at `2fb88ce`.

## 1. `packages/platform-web/src/css-tier-layers.ts` — the primitive

`CssTierFilterDefs.ensure` took a second, optional argument, and the cache key grew to carry it so
that a re-solve rebuilds the definition instead of being swallowed by the `built` set:

```ts
ensure(sigmaCssPx: number, transfer?: { readonly slope: number; readonly intercept: number }): void;
```

```ts
ensure(sigmaCssPx, transfer) {
  const id = referenceFilterId(prefix, sigmaCssPx);
  const key = transfer === undefined ? id : `${id}|${transfer.slope}|${transfer.intercept}`;
  if (built.has(key)) return;
  defs.querySelector(`#${CSS.escape(id)}`)?.remove();
  ...
  filter.append(blur);
  if (transfer !== undefined) {
    const componentTransfer = doc.createElementNS(NS, "feComponentTransfer");
    for (const channel of ["feFuncR", "feFuncG", "feFuncB"]) {
      const fn = doc.createElementNS(NS, channel);
      fn.setAttribute("type", "linear");
      fn.setAttribute("slope", String(transfer.slope));
      fn.setAttribute("intercept", String(transfer.intercept));
      componentTransfer.append(fn);
    }
    filter.append(componentTransfer);
  }
  defs.append(filter);
  built.add(key);
}
```

The stage goes **after** the blur and **inside** the `color-interpolation-filters="linearRGB"`
chain, which is where the conversion has to live: the renderer's lerp is in linear light and the
transfer is a transfer of the body the tint composites over, not of the page.

## 2. `packages/platform-web/src/root.ts` — the solve

`ensureCssTierFilters` took the transfer and applied it to the **first** width only, which is the
sharp one:

```ts
sigmas.forEach((sigma, index) => {
  cssTierFilterDefs?.ensure(sigma, index === 0 ? transfer : undefined);
});
```

and at the CSS-tier paint site, immediately before `ensureCssTierFilters(...)`, the renderer's
composite was rebuilt in the **shader's** order — the size law's occlusion sized into the alpha
before the W9 response solve, which is where the shader puts it and where `root.ts` does not (§2) —
and handed to the solve with the derived excess and the overlay the tier had just declared:

```ts
const w17Sized = {
  ...gpuOptics[variant],
  tintAlpha: sizeOcclusionAlphaAt(gpuOptics[variant].tintAlpha, surfaceThickness, sizeConstants),
};
const w17Responded = backdropTone === undefined ? w17Sized : toneRespondedSourceOptics(
  w17Sized, backdropTone, surfaceThickness, backdropAdaptation,
  (backdropTonePolicyStrength >= 0.999 ? 1 : 0) * Math.min(1, Math.max(0, backdropToneConstants.max)),
  backdropToneResponse,
);
const w17Adapted = adaptedSourceOptics(w17Responded, backdropTone?.rgb, backdropAdaptation);
const w17Transfer = backdropTone === undefined ? undefined : w17CarrierSolve({
  backdropLuminance: backdropTone.linearLuminance,
  rendererAlpha: w17Adapted.tintAlpha,
  rendererTintLuminance: 0.2126 * w17Adapted.tint[0] + 0.7152 * w17Adapted.tint[1]
    + 0.0722 * w17Adapted.tint[2],
  excess: w17DerivedExcess({
    widthCssPx: bounds.width, heightCssPx: bounds.height, radiusCssPx: record.radii[0],
    rimAlpha: gpuOptics[variant].rimAlpha, present: 1 - backdropAdaptation,
  }),
  ...w17Overlay(declarations.layers?.overlay["background-color"]),
});
ensureCssTierFilters(referenceFilterSigmas(declarations.body), w17Transfer);
```

The `carrier` run of §4 read the overlay from `nodeOptics` instead of from the declaration block;
the `carrier2` run read it from the declaration, which is the tier's own final word on the layer
after the size law's occlusion and the accessibility folds. §4 reports `carrier2` and records
`carrier` beside it, because the difference between the two is a reading and not a correction: it
moved the level by −0.005 to −0.007 at 1x and −0.005 at 2x and changed no verdict.

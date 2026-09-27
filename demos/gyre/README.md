# Gyre

A live ocean-surface-current instrument, and a demo of Liquid Glass on the web built on the
**published** `@vitreajs/vitrea-react@0.6.0`. The package resolves from npm, not from this
repository's workspace, so what runs here is what an outside app would get.

The whole viewport is the field: a WebGL shader registered with vitrea as the backdrop texture,
so every glass surface on the page refracts it for real on the WebGPU tier. The chrome is the
material's whole vocabulary: a toolbar nav with one tinted action, a draggable glass probe that
reads the field under it, a segmented control for layers, a transport toolbar, and a menu that
morphs out of its trigger. Content lives in ordinary-DOM sheets and never on glass.

```sh
cd demos/gyre
npm install
npm run dev          # http://localhost:5180
npm run build        # a static site in dist/
npm run typecheck
```

`?renderer=css` forces the CSS tier. The default asks for WebGPU and the Rendering sheet prints
what each sampling group actually resolved to.

## Files

| Path | What it is |
| --- | --- |
| `DESIGN.md` | The design law the page is built under: stance, palette usage, type roles, layout strips, placement rules. |
| `src/field/` | The field. `shader.ts` and `noise.ts` carry the same function in GLSL and JavaScript, so the probe reads the pixels it sits on. `palettes.ts` is the three layers and their ramps. |
| `src/glass/` | The controls: `Nav`, `Probe`, `Transport`, `LayerControl`, `LayerMenu`. Every one is a real `<button>` or radio group with the material drawn around it. |
| `src/sheets/` | Stations, Method, Rendering, Request access: content panels, no glass. |
| `scripts/palette.mjs` | The palette arithmetic: OKLCH to sRGB and every contrast ratio the law cites. |

## Placement, in one paragraph

vitrea draws glass in viewport-fixed planes and warns in dev mode when two sampling groups on one
plane come within a sampling padding of each other, or when two surfaces overlap. The layout is
built around that: four reserved strips, a probe clamped to the field with a 28px margin from the
other groups, the morph in a group of its own, and a plain-text wordmark so the viewport's origin
corner, where a morph's platter spends its first frame, stays clear of glass. A clean console is
part of the definition of done.

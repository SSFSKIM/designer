# Demos on the workspace build

Six pages the `designer` skill built on vitrea 0.14.0 to show the Liquid Glass design language
composed, not decorated: a live plane fills the window, navigation and controls float over it as
the only glass, and the page still works with transparency reduced. The initiative, its briefs, its
audit and its acceptance are in `docs/doperpowers/specs/2026-09-10-liquid-glass-into-the-skill.md`.

Each demo is one `index.html` beside its `DESIGN.md` and an `images/` directory. The page imports
the workspace build through an import map, so it is one file plus a served repository:

```html
<script type="importmap">
{ "imports": {
    "@vitreajs/vitrea":     "/packages/core/dist/index.js",
    "@vitreajs/vitrea-web": "/packages/platform-web/dist/index.js"
} }
</script>
<script type="module">
  import { createGlassRoot } from "@vitreajs/vitrea-web";
</script>
```

Build once, then serve the repository root and open a demo over `http://localhost`, which is a
secure context and gets the WebGPU tier in Chromium; every other engine gets the CSS tier:

```bash
pnpm -r build
python3 -m http.server 8788        # from the repository root
open http://localhost:8788/apps/demos/         # index.html lists the six
```

The audit renders a demo the same way and reads the runtime's own diagnostics:

```bash
node docs/research/scripts/glass-audit.mjs apps/demos/music-player
```

| Demo | Brief | The live plane |
|---|---|---|
| `music-player` | a streaming service's desktop player | the album's artwork |
| `transit-ops` | a bus network's control-room map | the city map with live vehicles |
| `photo-review` | a photographer's culling and adjustment tool | the photograph on the stage |
| `film-festival` | a city film festival's programme | the opening film's still |
| `park-trails` | a national park's trails site | the relief map or panorama |
| `product-launch` | a small maker's mirrorless camera | the hero photography |

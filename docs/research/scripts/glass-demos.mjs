#!/usr/bin/env node
// The six Liquid Glass demos (spec: docs/doperpowers/specs/2026-09-10-liquid-glass-into-the-skill.md).
//
//   node glass-demos.mjs prompt <slug> [--port 8790]   the builder's prompt for one demo
//   node glass-demos.mjs list                          the slugs
//
// A builder is a fresh agent reading the live skill; the brief is verbatim from the spec, and the
// mechanics — the import map to the workspace build, the served origin, the two window handles the
// audit reads — are stated once here so every demo is built and audited the same way.
import path from "node:path";
import { fileURLToPath } from "node:url";

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const BRIEFS = {
  "music-player": "Design a desktop music player for a streaming service's Mac web client. The current album's artwork fills the window; the transport (play, pause, previous, next, a scrubber), the queue and the volume float over it, and a menu opens from the queue control for playlist actions. Realistic data: one album with its tracks, a queue of six, three playlists.",
  "transit-ops": "Design the desktop operations map for a city bus network's control room. A city map fills the window with live vehicle positions on their routes; a search field, a route-and-status filter toolbar and a selected-vehicle platter float over the map, and a sidebar lists the active alerts. Realistic data: forty vehicles on eight routes, six alerts.",
  "photo-review": "Design a desktop photo review and adjustment tool for a working photographer culling a shoot. The selected photograph fills the stage; a tool palette, the adjustment controls (exposure, white balance, crop) and a before-and-after compare toggle float over it, and a filmstrip of the shoot runs beneath. Realistic data: a shoot of thirty frames with ratings and flags.",
  "film-festival": "Design the programme page for a city film festival. A full-bleed still from the opening film fills the first screen with the navigation and the date-and-tickets controls floating over it; the schedule by day and venue, the strands and the passes extend beneath. Realistic data: four days, three venues, twenty-four films.",
  "park-trails": "Design the trails site for a national park. A full-bleed relief map or panoramic photograph of the park fills the window with a floating trip planner (route, distance, weather, permits) over it; the trail list, the conditions and the permit steps extend beneath the floating bar. Realistic data: twelve trails with distance, elevation and current conditions.",
  "product-launch": "Design the launch page for a mirrorless camera from a small maker. Hero photography of the camera fills the first screen with the navigation floating over it; the sensor, the lenses, the body and the price scroll beneath the floating bar, and a configure-and-buy bar floats at the bottom. Realistic data: three lens options, two body colours, a price.",
};
const TAIL = " Desktop at 1440 wide. One HTML file on vitrea 0.14.0 (the workspace build through the import map), served from the repository root.";

function prompt(slug, port) {
  const dir = path.join(repo, "apps/demos", slug);
  return `You are a fresh design agent building one of six demos. Follow the design skill at \`${repo}/skills/designer/SKILL.md\` exactly, reading its reference files as it routes you (they are on disk under \`${repo}/skills/designer/\`). The brief's material model is glass over planes, so the skill will route you to \`references/material.md\` and \`references/liquid-glass.md\`; read both in full before composing.

Brief (verbatim): "${BRIEFS[slug]}${TAIL}"

Deliverable: \`${dir}/index.html\` (create the directory), with \`${dir}/DESIGN.md\` written the way the skill prescribes (its §4 must carry the plane split, the floating-layer inventory, the group plan, the size family and the backdrop design), and \`${dir}/images/\` for the page's photographs. Inline CSS and JS; no framework; no build step; realistic content, never lorem ipsum. The one external module is vitrea, imported through this import map exactly:

<script type="importmap">
{ "imports": { "@vitreajs/vitrea": "/packages/core/dist/index.js", "@vitreajs/vitrea-web": "/packages/platform-web/dist/index.js" } }
</script>
<script type="module">import { createGlassRoot } from "@vitreajs/vitrea-web"; …</script>

Create the root with \`createGlassRoot({ renderer: "webgpu", devMode: true })\` and assign \`window.__vitrea = root\`; if the page has a menu or platter that opens from a control, expose \`window.__glassDemo = { openMenu() { … } }\` so the audit can capture it open. Photographs: use the skill's imagery ladder (\`node ${repo}/skills/designer/scripts/find-image.mjs search … | pick …\`), then download the chosen file into \`images/\` and reference it by relative path, with the credit the source requires on the page — a same-origin file is what the texture path needs; a cross-origin image can taint the source and demote the group. A drawn plane (a map) is drawn on a canvas you paint.

Serve and look: from \`${repo}\` run \`python3 -m http.server ${port}\` in the background and open \`http://localhost:${port}/apps/demos/${slug}/index.html\` — localhost is a secure context, so Chromium resolves the WebGPU tier. Use \`playwright-cli\` for screenshots at 1440×900 and read \`window.__vitrea\`'s state in the page: the renderer that drew, and every diagnostic. Before you finish, run \`node ${repo}/docs/research/scripts/glass-audit.mjs apps/demos/${slug}\` from the repository root and fix what it flags (a nested glass host, a same-plane overlap, a content-layer host, a demoted backdrop root, a missing hint, a page error, an over-wide capture); then run the skill's QA protocol including its glass page pass. Stop the server you started. Do not run git. Do not modify anything outside \`${dir}\`.

Report in under 200 words: the live plane, the floating-layer inventory, the groups, the size family, the tier that resolved, the audit's diagnostic count, and anything the skill's references did not tell you that you had to decide.`;
}

const [cmd, slug, ...rest] = process.argv.slice(2);
if (cmd === "list") console.log(Object.keys(BRIEFS).join("\n"));
else if (cmd === "prompt" && BRIEFS[slug]) console.log(prompt(slug, rest.includes("--port") ? rest[rest.indexOf("--port") + 1] : 8790));
else { console.error("usage: glass-demos.mjs list | prompt <slug> [--port n]"); process.exit(1); }

#!/usr/bin/env node
// Seed a build ledger from the settling experiment's builds, for the layout-arm run
// (docs/doperpowers/specs/2026-10-12-routing-ledger-and-layout-arm.md, part B "Seeding").
//
//   node ledger-seed.mjs --exclude-brief <key> [--arms v1.1,v2.0,v2.1] [--out <file>] [--print]
//
// One entry per skill-arm build of every brief except the excluded one, so a cell's ledger holds
// realistic prior work and never a sibling of its own brief. Tokens come from measurements.json
// (rendered, the settling spec's footing), the form from topology.json, and the declared accent job,
// ground temperature, signature line, posture, activity, relation and prior from the build's own
// DESIGN.md where the arm wrote one — read best-effort, and a field the regexes cannot find is left
// out, which the ledger treats as "never flags". Entries carry source: measured.
import fs from "node:fs";
import path from "node:path";

const repo = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../../../..");
const ws = process.env.SETTLING_WS || path.join(repo, "figma-design-workspace/settling");
const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i === -1 ? d : args[i + 1]; };
const exclude = opt("--exclude-brief", null);
const arms = new Set((opt("--arms", "v1.1,v2.0,v2.1")).split(","));
const out = opt("--out", null);

const CATEGORY = { console: "console", narrative: "landing", pair: "compare" };
const BRIEF = {
  rail: "freight rail dispatch console", pharmacy: "hospital pharmacy inventory console",
  fleet: "bus fleet maintenance console", library: "children's library summer reading page",
  hardware: "family hardware store landing page", rebate: "city home-battery rebate page",
  compare: "tyre supplier quote comparison",
};
const ACTIVITIES = "monitor|find|browse|compare|operate|read|decide";
const RELATIONS = "sequence|hierarchy|matrix|network|spatial[ -]field|set";
const PRIORS = "exception-first|list beside detail|list-detail|table-led|grid of equals|map-led|canvas-plus-palette|primary region with supporting pane|center stage|wizard|hub and spoke|titled sections|editorial stack|asymmetric split|full-bleed image|typographic poster|product object|reading column|product detail|lookbook";

const strip = (s) => s.replace(/[*_`]/g, "").replace(/\s+/g, " ").trim();
function field(md, label, values) {
  // "- Accent job: **none** —", "**Accent job — directional.**", "Posture: **workspace**"
  // The records vary in punctuation and in how much prose sits between the label and the value
  // ("relation the first read acts on is a **matrix**"), so the window after the label is wide.
  const re = new RegExp(`${label}[^\\n]{0,60}?\\b(${values})\\b`, "i");
  const m = md.match(re);
  return m ? m[1].toLowerCase().replace(/\s+/g, "-") : undefined;
}
function signature(md) {
  const m = md.match(/Signature element[*_ .:—-]*([^\n]+(?:\n[^\n*#-][^\n]*)?)/i);
  if (!m) return undefined;
  const s = strip(m[1]).replace(/^[.:—-]\s*/, "");
  const first = s.split(/(?<=[.!?])\s/)[0];
  return first.length > 140 ? first.slice(0, 137) + "…" : first;
}
function prior(md) {
  const m = md.match(new RegExp(`Prior adopted[^\\n]{0,40}?\\b(${PRIORS})\\b`, "i")) || md.match(new RegExp(`\\b(${PRIORS})\\b[^\\n]{0,40}earned by`, "i"));
  return m ? m[1].toLowerCase() : undefined;
}
function temperatureOf(ground, md) {
  const declared = field(md, "Ground temperature", "warm|neutral|cool|brand-tinted");
  if (declared) return declared;
  if (!ground || ground.C === undefined) return undefined;
  if (ground.C < 0.012) return "neutral";
  if (ground.H >= 20 && ground.H <= 110) return "warm";
  if (ground.H >= 180 && ground.H <= 300) return "cool";
  return "brand-tinted";
}

const manifest = JSON.parse(fs.readFileSync(path.join(ws, "manifest.json"), "utf8")).cells;
const meas = JSON.parse(fs.readFileSync(path.join(ws, "measurements.json"), "utf8")).builds;
const topo = JSON.parse(fs.readFileSync(path.join(ws, "topology.json"), "utf8")).builds || {};
const topoByFile = {};
for (const [k, v] of Object.entries(topo)) topoByFile[path.basename(path.dirname(v.file || k))] = v;

const entries = [];
for (const c of manifest) {
  if (!arms.has(c.arm) || c.brief === exclude) continue;
  const m = meas[c.id];
  if (!m) continue;
  const designPath = path.join(ws, "builds", c.id, "DESIGN.md");
  const md = fs.existsSync(designPath) ? fs.readFileSync(designPath, "utf8") : "";
  const job = field(md, "Accent job", "none|status-only|directional|atmospheric");
  const e = {
    at: m.measuredAt || new Date().toISOString(), source: "measured", settlingId: c.id, arm: c.arm,
    project: `${c.brief}-${c.arm}-${c.seedLabel}`, brief: BRIEF[c.brief], category: CATEGORY[c.category],
  };
  if (job) e.accentJob = job;
  if (job === "none" || job === "status-only") e.accentHue = "none";
  else if (m.accent && typeof m.accent.H === "number") e.accentHue = Math.round(m.accent.H);
  if (m.ground) { e.groundL = m.ground.L; e.groundHue = Math.round(m.ground.H); }
  const t = temperatureOf(m.ground, md); if (t) e.groundTemperature = t;
  if (m.families) for (const k of ["display", "body", "mono"]) if (m.families[k] && m.families[k] !== "None") e[k] = m.families[k];
  const sig = signature(md); if (sig) e.signature = sig;
  const posture = field(md, "Posture", "workspace|transient|narrative"); if (posture) e.posture = posture;
  const activity = field(md, "activity", ACTIVITIES); if (activity) e.activity = activity;
  const relation = field(md, "relation", RELATIONS); if (relation) e.relation = relation;
  const p = prior(md); if (p) e.prior = p;
  const tp = topoByFile[c.id]; if (tp && tp.signature) e.dominance = `${tp.signature.dominant} ${tp.signature.dominance}`;
  entries.push(e);
}
entries.sort((a, b) => a.at.localeCompare(b.at));
const text = entries.map((e) => JSON.stringify(e)).join("\n") + "\n";
if (out) { fs.mkdirSync(path.dirname(out), { recursive: true }); fs.writeFileSync(out, text); console.log(`${entries.length} entries → ${out}`); }
else process.stdout.write(text);

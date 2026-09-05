#!/usr/bin/env node
// The settling experiment's cell manifest and builder prompts (docs/doperpowers/specs/2026-09-05-settling-experiment.md).
//
//   node cells.mjs init              write manifest.json (idempotent: keeps existing ids)
//   node cells.mjs wave <n>          list the cells of wave n with their status
//   node cells.mjs prompt <id>       print the builder prompt for one cell
//   node cells.mjs status            every cell with whether index.html exists
//
// Briefs are read verbatim from evals/evals.json; brief 11 is reworded for a fresh agent (see spec).

import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

const repo = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../../../..");
const ws = path.join(repo, "figma-design-workspace/settling");
const manifestPath = path.join(ws, "manifest.json");

const BRIEFS = [
  { key: "rail", eval: 1, category: "console" },
  { key: "pharmacy", eval: 7, category: "console" },
  { key: "fleet", eval: 10, category: "console" },
  { key: "library", eval: 3, category: "narrative" },
  { key: "hardware", eval: 4, category: "narrative" },
  { key: "rebate", eval: 12, category: "narrative" },
  { key: "compare", eval: 11, category: "pair" },
];
const REWORD = {
  11: "Design the page where a regional bus operator's fleet manager compares three tyre suppliers' quotes on the same criteria — price per axle, lead time, warranty, on-site fitting — and picks one. Single HTML file with realistic data.",
};
const ARMS = {
  none: null,
  "v1.1": "skills/v1.1.0/designer",
  "v2.0": "skills/v2.0.0/designer",
  "v2.1": "skills/v2.1.0/designer",
};
// Wave plan: one console and one narrative brief per wave, seed A before seed B; compare in wave 4.
const WAVES = [
  [["rail", "A"], ["rebate", "A"]],
  [["pharmacy", "A"], ["library", "A"]],
  [["fleet", "A"], ["hardware", "A"]],
  [["compare", "A"], ["rail", "B"]],
  [["rebate", "B"], ["pharmacy", "B"]],
  [["library", "B"], ["fleet", "B"]],
  [["hardware", "B"]],
];

function briefText(b) {
  if (REWORD[b.eval]) return REWORD[b.eval];
  const evals = JSON.parse(fs.readFileSync(path.join(repo, "evals/evals.json"), "utf8")).evals;
  return evals.find((e) => e.id === b.eval).prompt;
}

function init() {
  const old = fs.existsSync(manifestPath) ? JSON.parse(fs.readFileSync(manifestPath, "utf8")) : { cells: [] };
  const cells = [];
  WAVES.forEach((wave, wi) => {
    for (const [key, seedLabel] of wave) {
      const b = BRIEFS.find((x) => x.key === key);
      const seed = (seedLabel === "A" ? 1000 : 2000) + b.eval;
      for (const arm of Object.keys(ARMS)) {
        const prev = old.cells.find((c) => c.brief === key && c.arm === arm && c.seedLabel === seedLabel);
        cells.push(prev || {
          id: crypto.randomBytes(3).toString("hex"), brief: key, eval: b.eval, category: b.category,
          arm, seedLabel, seed, wave: wi + 1,
        });
      }
    }
  });
  fs.mkdirSync(ws, { recursive: true });
  fs.writeFileSync(manifestPath, JSON.stringify({ created: old.created || new Date().toISOString(), cells }, null, 1));
  console.log(`${cells.length} cells → ${manifestPath}`);
}

function load() { return JSON.parse(fs.readFileSync(manifestPath, "utf8")); }
const built = (c) => fs.existsSync(path.join(ws, "builds", c.id, "index.html"));

function prompt(id) {
  const c = load().cells.find((x) => x.id === id);
  if (!c) throw new Error("no cell " + id);
  const b = BRIEFS.find((x) => x.key === c.brief);
  const out = path.join(ws, "builds", c.id);
  const skill = ARMS[c.arm];
  const brief = briefText(b);
  const common = `Brief (verbatim): "${brief}"

Deliverable: \`${out}/index.html\` (create the directory), one self-contained file — inline CSS and JS, no build step, no external framework; realistic content, never lorem ipsum or placeholder text. If \`playwright-cli\` is available you may render and screenshot your page to check it. Do not read anything under \`${repo}/figma-design-workspace/\` other than your own output directory. Do not commit anything. When done, report in under 200 words: the files you wrote, the visual direction you chose in two sentences, and which checks you ran.`;
  if (!skill) {
    return `You are a fresh design agent building a page from a brief. Use your own judgment about what a good page for this brief is. Do not read \`${repo}/skills/\` or any design skill, plugin, or reference material; do not invoke any skill.

${common}`;
  }
  const sp = path.join(ws, skill);
  return `You are a fresh design agent running an evaluation build. Follow the design skill at \`${sp}/SKILL.md\` exactly, reading its reference files as it routes you (read the files on disk under \`${sp}/\`; do NOT rely on any installed "designer" plugin skill, on \`${repo}/skills/\`, or on memory of another version). Write whatever design record the skill asks for (its \`DESIGN.md\`) into the output directory, per the skill's own authoring reference, before any UI code. Where the skill runs its sampler, run \`node ${sp}/scripts/sample-ingredients.mjs --seed ${c.seed}\` and treat its output per its own preamble. No persona is invoked. Run the QA the skill asks for.

${common}`;
}

const [cmd, arg] = process.argv.slice(2);
if (cmd === "init") init();
else if (cmd === "prompt") console.log(prompt(arg));
else if (cmd === "wave") {
  for (const c of load().cells.filter((x) => x.wave === +arg)) console.log(`${c.id}  ${c.brief.padEnd(9)} ${c.arm.padEnd(5)} ${c.seedLabel} seed=${c.seed}  ${built(c) ? "built" : "-"}`);
} else if (cmd === "status") {
  const cells = load().cells; let n = 0;
  for (const c of cells) { const ok = built(c); n += ok; console.log(`w${c.wave} ${c.id}  ${c.brief.padEnd(9)} ${c.arm.padEnd(5)} ${c.seedLabel}  ${ok ? "built" : "-"}`); }
  console.log(`${n}/${cells.length} built`);
} else { console.log("usage: cells.mjs init | wave <n> | prompt <id> | status"); process.exit(1); }

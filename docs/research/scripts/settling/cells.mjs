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
import { execFileSync } from "node:child_process";

const repo = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../../../..");
const ws = process.env.SETTLING_WS || path.join(repo, "figma-design-workspace/settling");
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
  // The layout-arm run (docs/doperpowers/specs/2026-10-12-routing-ledger-and-layout-arm.md, part C)
  // runs in its own workspace (SETTLING_WS=figma-design-workspace/layout-arm) with `init --arms`;
  // the four settling arms above are its baseline, read from the settling workspace unchanged.
  "v2.4": "skills/v2.4.0/designer",          // compressed SKILL.md plus the build ledger
  "v2.1-one": "skills/v2.1.0-one/designer",  // the frozen 2.1 copy with one candidate, no comparison
};
const LEDGER_ARMS = new Set(["v2.4"]);
const baselineWs = process.env.SETTLING_BASELINE_WS || null;
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

function init(armList) {
  const arms = armList ? armList.split(",") : ["none", "v1.1", "v2.0", "v2.1"];
  for (const a of arms) if (!(a in ARMS)) throw new Error("unknown arm " + a);
  const old = fs.existsSync(manifestPath) ? JSON.parse(fs.readFileSync(manifestPath, "utf8")) : { cells: [] };
  const cells = [];
  WAVES.forEach((wave, wi) => {
    for (const [key, seedLabel] of wave) {
      const b = BRIEFS.find((x) => x.key === key);
      const seed = (seedLabel === "A" ? 1000 : 2000) + b.eval;
      for (const arm of arms) {
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
const built = (c) => fs.existsSync(path.join(ws, "builds", c.id, "index.html")) && !fs.existsSync(path.join(ws, "builds", c.id, ".incomplete"));

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
  // A ledger arm's cell carries a seeded ledger (`seed-ledgers`) holding the other briefs' builds;
  // the builder's own environment does not carry the variable, so the prompt names it per command.
  const ledger = LEDGER_ARMS.has(c.arm)
    ? ` Where the skill runs its build ledger, every \`build-ledger.mjs\` command is run with the environment variable \`DESIGNER_LEDGER=${out}/ledger.jsonl\` set (prefix the command: \`DESIGNER_LEDGER=${out}/ledger.jsonl node ${sp}/scripts/build-ledger.mjs …\`); that file already holds prior builds and is the only ledger this build may read or write. Save the output of each \`nearest\` run you make, verbatim, appended to \`${out}/ledger-report.txt\`.`
    : "";
  return `You are a fresh design agent running an evaluation build. Follow the design skill at \`${sp}/SKILL.md\` exactly, reading its reference files as it routes you (read the files on disk under \`${sp}/\`; do NOT rely on any installed "designer" plugin skill, on \`${repo}/skills/\`, or on memory of another version). Write whatever design record the skill asks for (its \`DESIGN.md\`) into the output directory, per the skill's own authoring reference, before any UI code. Where the skill runs its sampler, run \`node ${sp}/scripts/sample-ingredients.mjs --seed ${c.seed}\` and treat its output per its own preamble.${ledger} No persona is invoked. Run the QA the skill asks for.

${common}`;
}

// The seeded ledger for every ledger-arm cell: the settling run's skill-arm builds of every brief
// but this cell's own, so the agent sees realistic prior work and never a sibling of its brief.
function seedLedgers() {
  const seedScript = path.join(path.dirname(new URL(import.meta.url).pathname), "ledger-seed.mjs");
  const from = baselineWs || path.join(repo, "figma-design-workspace/settling");
  let n = 0;
  for (const c of load().cells.filter((x) => LEDGER_ARMS.has(x.arm))) {
    const dir = path.join(ws, "builds", c.id);
    fs.mkdirSync(dir, { recursive: true });
    const outFile = path.join(dir, "ledger.jsonl");
    if (fs.existsSync(outFile)) continue;
    execFileSync(process.execPath, [seedScript, "--from", from, "--exclude-brief", c.brief, "--out", outFile], { stdio: "inherit" });
    n++;
  }
  console.log(`${n} ledgers seeded`);
}

const FIT_QUESTIONS = {
  console: [
    "q1 The region where the operator's work happens (the exceptions, the lots, the vehicles, the trains) is the first thing read: first in document order among content and top-left in the first viewport.",
    "q2 Nothing full-width sits above that work region except chrome (a top bar, a title line).",
    "q3 There is no row of numeric summary tiles (a stat row, KPI strip) placed before the work region.",
    "q4 There is no side column that carries material unrelated to the task in view (a rail of links, tips, promotions, or generic widgets).",
    "q5 The dominant region's form matches the brief's unit and relation: a table or schedule for lots and stock, a queue or list for defects and exceptions, positions on a field or line for trains, a time grid for windows and bays.",
  ],
  narrative: [
    "q1 One region carries the proposition (what this is and why it matters to the reader) and dominates the first viewport.",
    "q2 The primary action the brief names (sign up, apply, buy or pick up) is reachable in the first viewport.",
    "q3 There is no row of three equal peers (three cards, three features, three plans) that the brief did not itself count as three.",
    "q4 The headline does not sit beside an empty half or a decorative filler; the space beside it is content or there is no split.",
    "q5 Every section the brief names is present as its own region, in an order a reader of this brief would expect.",
  ],
};
FIT_QUESTIONS.pair = [
  "q1 The three suppliers are compared on one axis in one region (rows or columns of one table or grid), not as three separate cards or panels.",
  "q2 Every criterion the brief names (price per axle, lead time, warranty, on-site fitting) is readable across all three suppliers without leaving the region.",
  "q3 The action of picking one is present and fixed in position, not buried below the comparison.",
  "q4 There is no marketing band, hero, or summary strip above the comparison.",
  "q5 Nothing on the page is a card grid or a stat row.",
];

function fitPrompt(brief) {
  // With SETTLING_BASELINE_WS set, the baseline workspace's built pages of the same brief are rated in
  // the same frame as this workspace's, so the new arms' fit is read beside the old arms' by one rater.
  const here = load().cells.filter((c) => c.brief === brief && built(c)).map((c) => ({ id: c.id, ws }));
  const there = baselineWs
    ? JSON.parse(fs.readFileSync(path.join(baselineWs, "manifest.json"), "utf8")).cells
        .filter((c) => c.brief === brief && fs.existsSync(path.join(baselineWs, "builds", c.id, "index.html")))
        .map((c) => ({ id: c.id, ws: baselineWs }))
    : [];
  const pages = [...here, ...there];
  if (!pages.length) throw new Error("nothing built for " + brief);
  const b = BRIEFS.find((x) => x.key === brief);
  // fixed shuffle so the order does not follow the manifest
  pages.sort((x, y) => x.id.localeCompare(y.id));
  const qs = FIT_QUESTIONS[b.category];
  const outFile = path.join(ws, "fit", brief + ".json");
  return `You are a blinded structural rater for a design experiment. You will see several pages built from the same brief by different builders; you do not know which builder made which, and you must not try to find out (do not open anything under the build directories except the two screenshots named per page). Rate structure only, not taste.

Brief (verbatim): "${briefText(b)}"

Pages (id, first-viewport screenshot, full-page screenshot):
${pages.map((p) => `- ${p.id}: ${path.join(p.ws, "builds", p.id, "shot-fv.png")} and ${path.join(p.ws, "builds", p.id, "shot-full.png")}`).join("\n")}

For each page, read both screenshots, then answer each statement below with 1 (true of this page) or 0 (not true), with a clause of evidence for each answer:
${qs.map((q) => "- " + q).join("\n")}

Write the result as JSON to \`${outFile}\` (create the directory) in exactly this shape, one entry per page id:
{"<id>": {"answers": {"q1": 0 or 1, "q2": …, "q5": …}, "evidence": {"q1": "…", …}}, …}
Then report in under 120 words which pages scored 5 and which scored 2 or less, with the failing statements named. Do not modify anything else.`;
}

const [cmd, arg] = process.argv.slice(2);
const flag = (k) => { const i = process.argv.indexOf(k); return i === -1 ? null : process.argv[i + 1]; };
if (cmd === "init") init(flag("--arms"));
else if (cmd === "seed-ledgers") seedLedgers();
else if (cmd === "prompt") console.log(prompt(arg));
else if (cmd === "fitprompt") console.log(fitPrompt(arg));
else if (cmd === "wave") {
  for (const c of load().cells.filter((x) => x.wave === +arg)) console.log(`${c.id}  ${c.brief.padEnd(9)} ${c.arm.padEnd(5)} ${c.seedLabel} seed=${c.seed}  ${built(c) ? "built" : "-"}`);
} else if (cmd === "status") {
  const cells = load().cells; let n = 0;
  for (const c of cells) { const ok = built(c); n += ok; console.log(`w${c.wave} ${c.id}  ${c.brief.padEnd(9)} ${c.arm.padEnd(5)} ${c.seedLabel}  ${ok ? "built" : "-"}`); }
  console.log(`${n}/${cells.length} built`);
} else { console.log("usage: cells.mjs init [--arms a,b] | seed-ledgers | wave <n> | prompt <id> | fitprompt <brief> | status"); process.exit(1); }

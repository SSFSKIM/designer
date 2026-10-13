#!/usr/bin/env node
// scripts/build-ledger.mjs — what recent builds chose, in view at the moment of choice.
//
// Derivation by criteria funnels to one answer the way a catalogue does, one level down: remove the
// hex block and the convergence reappears as the "best answer" family, the leftover hue, the same
// signature motif, the same composition form for a different unit. Bands named in a calibration
// file are remembered; this ledger is where they are seen. It is per machine, because the clone is
// across the products one agent builds, not within one project.
//
//   node build-ledger.mjs nearest [flags] [--n 20]
//       the most recent entries, nearest first, with the flags the candidate raises against each
//   node build-ledger.mjs record [flags]
//       append one entry for a finished build (run at QA, from the build's own record)
//   node build-ledger.mjs list [--category <c>] [--n 20]
//   node build-ledger.mjs path
//
// Flags, every one optional — a missing field is recorded as missing and never flags:
//   --project <name> --brief "<one line>" --category <one word: console, landing, docs, commerce, …>
//   --accent-hue <0–360 | none> --accent-job <none | status-only | directional | atmospheric>
//   --ground-l <0–1> --ground-hue <0–360> --ground-temperature <warm | neutral | cool | brand-tinted>
//   --display "<family>" --body "<family>" --mono "<family>"
//   --signature "<the signature element, one line>"
//   --posture <workspace | transient | narrative> --activity <monitor | find | browse | compare | operate | read | decide>
//   --relation <sequence | hierarchy | matrix | network | spatial-field | set> --dominance "<…>" --prior "<…>"
//
// The file is DESIGNER_LEDGER, else ~/.config/designer/build-ledger.jsonl, one JSON object per line.
import { readFileSync, existsSync, mkdirSync, appendFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { join, dirname } from "node:path";
import { homedir } from "node:os";

export const FIELDS = [
  "project", "brief", "category", "accentHue", "accentJob", "groundL", "groundHue",
  "groundTemperature", "display", "body", "mono", "signature", "posture", "activity", "relation",
  "dominance", "prior",
];
const NUMERIC = new Set(["accentHue", "groundL", "groundHue"]);
export const ACCENT_BAND = 30;      // degrees; the stance spec's A1 bar (two consoles landed 20° apart)
export const GROUND_BAND = 20;      // degrees; the neutral-ramp family width in stances.md
export const FAMILY_WINDOW = 10;    // the last n builds of the same category a family is checked against
export const DEFAULT_N = 20;

export function ledgerPath(env = process.env) {
  return env.DESIGNER_LEDGER || join(homedir(), ".config", "designer", "build-ledger.jsonl");
}

const camel = (flag) => flag.replace(/-([a-z])/g, (_, c) => c.toUpperCase());

// --accent-hue none is a legitimate value (the accent job is none); numbers are numbers.
export function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith("--")) continue;
    const key = camel(a.slice(2));
    const raw = argv[i + 1] !== undefined && !argv[i + 1].startsWith("--") ? argv[++i] : "";
    if (NUMERIC.has(key)) {
      if (raw === "none" || raw === "") { if (key === "accentHue") out[key] = "none"; continue; }
      const n = Number(raw);
      if (!Number.isFinite(n)) { console.error(`${a} needs a number (got ${JSON.stringify(raw)})`); process.exit(1); }
      out[key] = n;
    } else if (key === "n") {
      out.n = Number(raw) || DEFAULT_N;
    } else {
      out[key] = raw.trim();
    }
  }
  return out;
}

export function load(path) {
  if (!existsSync(path)) return [];
  return readFileSync(path, "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
}

export function append(path, entry) {
  mkdirSync(dirname(path), { recursive: true });
  appendFileSync(path, JSON.stringify(entry) + "\n");
}

export function entryFrom(args, now = new Date()) {
  const e = { at: now.toISOString(), source: args.source || "record" };
  for (const f of FIELDS) if (args[f] !== undefined && args[f] !== "") e[f] = args[f];
  return e;
}

export function hueDistance(a, b) {
  const d = Math.abs(((a - b) % 360 + 360) % 360);
  return d > 180 ? 360 - d : d;
}

const directional = (job, hue) => typeof hue === "number" && (job === "directional" || job === "atmospheric" || job === undefined);
const sameFamily = (a, b) => a && b && a.trim().toLowerCase() === b.trim().toLowerCase();
const STOP = new Set(["about", "above", "after", "again", "against", "along", "among", "around", "because", "before", "being", "below", "between", "every", "first", "other", "their", "there", "these", "those", "through", "under", "where", "which", "while", "whole", "would", "element", "signature", "region", "single"]);
export function contentWords(s) {
  return new Set((s || "").toLowerCase().replace(/[^a-z\s-]/g, " ").split(/[\s-]+/).filter((w) => w.length >= 5 && !STOP.has(w)));
}

// The flags a candidate raises against one prior entry. `sameCategoryRank` is the entry's position
// among the ledger's most recent entries of the candidate's category (0 = most recent), or -1.
export function flagsFor(cand, entry, sameCategoryRank = -1) {
  const flags = [];
  if (directional(cand.accentJob, cand.accentHue) && directional(entry.accentJob, entry.accentHue)) {
    const d = hueDistance(cand.accentHue, entry.accentHue);
    if (d <= ACCENT_BAND) flags.push(`accent: ${Math.round(d)}° from ${entry.project || "?"}'s ${Math.round(entry.accentHue)}°`);
  }
  const tinted = (t) => t && t !== "neutral";
  if (typeof cand.groundL === "number" && typeof entry.groundL === "number" && typeof cand.groundHue === "number" && typeof entry.groundHue === "number"
      && tinted(cand.groundTemperature) && tinted(entry.groundTemperature) && (cand.groundL >= 0.5) === (entry.groundL >= 0.5)) {
    const d = hueDistance(cand.groundHue, entry.groundHue);
    if (d <= GROUND_BAND) flags.push(`ground: same side, ${Math.round(d)}° from ${entry.project || "?"}'s ${cand.groundTemperature} ground at ${Math.round(entry.groundHue)}°`);
  }
  if (sameCategoryRank >= 0 && sameCategoryRank < FAMILY_WINDOW) {
    // One family often fills both slots on either side; each candidate family is reported once.
    const families = [...new Set(["display", "body"].map((s) => cand[s]).filter(Boolean).map((f) => f.trim()))];
    for (const fam of families) {
      const hits = ["display", "body"].filter((s) => sameFamily(fam, entry[s]));
      if (hits.length) flags.push(`family: ${fam} is already the ${hits.join(" and ")} of ${entry.project || "?"}`);
    }
  }
  const shared = [...contentWords(cand.signature)].filter((w) => contentWords(entry.signature).has(w));
  if (shared.length) flags.push(`signature: "${shared.join('", "')}" also in ${entry.project || "?"}'s — "${entry.signature}"`);
  if (cand.activity && cand.relation && cand.prior && cand.activity === entry.activity && cand.relation === entry.relation
      && sameFamily(cand.prior, entry.prior) && !(cand.brief && entry.brief && cand.brief.toLowerCase() === entry.brief.toLowerCase())) {
    flags.push(`form: ${entry.project || "?"} compiled to ${entry.prior} (${entry.activity}, ${entry.relation}) for a different brief`);
  }
  return flags;
}

// The recent directional accents by 30° band. A report that only lists neighbours steers the
// candidate into whatever band the neighbours leave empty — the first run of this ledger put four
// of six directional accents in the one band its seeded entries did not occupy — so the report
// shows the coverage and names the gap, with the calibration rule that an empty band is a
// constraint, not a source.
export const BANDS = 12;
export function coverage(entries) {
  const bins = new Array(BANDS).fill(0);
  for (const e of entries) if (directional(e.accentJob, e.accentHue)) bins[Math.floor((((e.accentHue % 360) + 360) % 360) / (360 / BANDS))]++;
  return bins;
}

export function gapFlag(cand, entries) {
  if (!directional(cand.accentJob, cand.accentHue)) return null;
  const bins = coverage(entries);
  const total = bins.reduce((a, b) => a + b, 0);
  const occupied = bins.filter(Boolean).length;
  if (total < 3 || occupied > BANDS / 2) return null;         // too few to cluster, or spread already
  const mine = Math.floor((((cand.accentHue % 360) + 360) % 360) / (360 / BANDS));
  if (bins[mine] || bins[(mine + 1) % BANDS] || bins[(mine + BANDS - 1) % BANDS]) return null;
  const where = bins.map((c, i) => (c ? `${i * 30}–${i * 30 + 30}° (${c})` : null)).filter(Boolean).join(", ");
  return `gap: no recent directional accent sits within 30° of ${Math.round(cand.accentHue)}°; the ${total} recent ones cluster at ${where}. The empty band is a constraint, not a source — the record names what in this product's own world put the hue here, or the accent job is none.`;
}

export function nearest(entries, cand, n = DEFAULT_N) {
  const recent = [...entries].reverse();           // most recent first
  let rank = 0;
  const scored = recent.map((e, i) => {
    const same = cand.category && e.category && cand.category.toLowerCase() === e.category.toLowerCase();
    const r = same ? rank++ : -1;
    return { entry: e, recency: i, same, flags: flagsFor(cand, e, r) };
  });
  scored.sort((a, b) => b.flags.length - a.flags.length || (b.same - a.same) || a.recency - b.recency);
  return scored.slice(0, n);
}

const fmtAccent = (e) => e.accentHue === undefined ? "—" : e.accentHue === "none" ? "none" : `${Math.round(e.accentHue)}°${e.accentJob ? " " + e.accentJob : ""}`;
const fmtGround = (e) => e.groundL === undefined ? "—" : `L${e.groundL}${e.groundHue !== undefined ? " h" + Math.round(e.groundHue) : ""}${e.groundTemperature ? " " + e.groundTemperature : ""}`;
const fmtFamilies = (e) => [e.display, e.body, e.mono].map((f) => f || "—").join(" / ");
const fmtForm = (e) => [e.prior, e.activity && e.relation ? `(${e.activity}, ${e.relation})` : e.activity || e.relation].filter(Boolean).join(" ") || "—";

export function summary(e) {
  return `${e.category || "?"} · accent ${fmtAccent(e)} · ground ${fmtGround(e)} · ${fmtFamilies(e)} · ${fmtForm(e)}${e.signature ? ` · "${e.signature}"` : ""}`;
}

export function report(entries, cand, path, n = DEFAULT_N) {
  const lines = [];
  lines.push(`build ledger — ${entries.length} entr${entries.length === 1 ? "y" : "ies"} in ${path}`);
  lines.push(`candidate: ${summary(cand)}`);
  lines.push("");
  if (!entries.length) {
    lines.push("The ledger is empty: nothing to compare against. Record this build at QA (`build-ledger.mjs record …`) so the next derivation on this machine can see it.");
    return lines.join("\n");
  }
  lines.push("A flag is evidence for the clone check, never a verdict. A value inside a flagged band is allowed when the design record names what in this product's own world put it there; a value that is there because the criteria led to the same best answer as last time moves — and it does not move into the one band nobody has used, which is the same convergence by elimination. Nearest first; a missing field on either side never flags.");
  lines.push("");
  const bins = coverage(entries);
  if (bins.some(Boolean)) lines.push("recent directional accents by band: " + bins.map((c, i) => (c ? `${i * 30}–${i * 30 + 30}° ×${c}` : null)).filter(Boolean).join(" · "));
  const gap = gapFlag(cand, entries);
  if (gap) lines.push(`! ${gap}`);
  if (bins.some(Boolean) || gap) lines.push("");
  const rows = nearest(entries, cand, n);
  for (const { entry, flags } of rows) {
    const when = (entry.at || "").slice(0, 10);
    lines.push(`${flags.length ? "!" : " "} ${when}  ${entry.project || "?"}${entry.brief ? ` — ${entry.brief}` : ""}`);
    lines.push(`    ${summary(entry)}`);
    for (const f of flags) lines.push(`    ↳ ${f}`);
  }
  const flagged = rows.filter((r) => r.flags.length).length;
  lines.push("");
  lines.push((flagged ? `${flagged} of ${rows.length} shown raise a flag.` : `No flags among the ${rows.length} shown.`) + (gap ? " The gap flag stands." : ""));
  return lines.join("\n");
}

function main(argv) {
  const [cmd, ...rest] = argv;
  const args = parseArgs(rest);
  const path = ledgerPath();
  if (cmd === "path") { console.log(path); return; }
  if (cmd === "record") {
    const e = entryFrom(args);
    if (Object.keys(e).length <= 2) { console.error("record: no fields given; see the flags in this file's header"); process.exit(1); }
    append(path, e);
    console.log(`recorded → ${path}\n${summary(e)}`);
    return;
  }
  if (cmd === "nearest") { console.log(report(load(path), args, path, args.n || DEFAULT_N)); return; }
  if (cmd === "list") {
    let entries = load(path);
    if (args.category) entries = entries.filter((e) => (e.category || "").toLowerCase() === args.category.toLowerCase());
    for (const e of entries.slice(-(args.n || DEFAULT_N))) console.log(`${(e.at || "").slice(0, 10)}  ${e.project || "?"}  ${summary(e)}`);
    if (!entries.length) console.log(`no entries${args.category ? " for " + args.category : ""} in ${path}`);
    return;
  }
  console.log("usage: build-ledger.mjs nearest [flags] | record [flags] | list [--category c] | path   (flags in the file header)");
  process.exit(cmd ? 1 : 0);
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) main(process.argv.slice(2));

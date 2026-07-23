#!/usr/bin/env node
// scripts/sample-ingredients.mjs — replicates Figma Make's create_make_theme sampler.
import { readFileSync } from "node:fs";
import { randomInt } from "node:crypto";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const lib = JSON.parse(readFileSync(join(here, "ingredients.json"), "utf8"));

const seedIdx = process.argv.indexOf("--seed");
let seed = null;
if (seedIdx !== -1) {
  seed = Number(process.argv[seedIdx + 1]);
  if (!Number.isInteger(seed)) {
    // Guard the boundary: Number("abc") is NaN and NaN|0 is 0 inside mulberry32,
    // so without this an invalid seed would silently masquerade as seed 0.
    console.error(
      `--seed requires an integer (got ${JSON.stringify(process.argv[seedIdx + 1])}).`
    );
    process.exit(1);
  }
}

function mulberry32(a) {
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const rand =
  seed === null
    ? (max) => randomInt(max)
    : (() => {
        const r = mulberry32(seed);
        return (max) => Math.floor(r() * max);
      })();

function draw(pool, n) {
  const copy = [...pool];
  const out = [];
  while (out.length < n) out.push(copy.splice(rand(copy.length), 1)[0]);
  return out;
}

const stances = draw(lib.stances, 3);
const traditions = draw(lib.typographyTraditions, 2);
const [canvas] = draw(lib.canvasTreatments, 1);

const lines = [
  "Here are some aesthetic ingredients to consider for this user's project.",
  "",
  "Lean especially toward these directions to break out of trained defaults. Treat them as tiebreakers when the brief is silent on aesthetic, not overrides — if the brief explicitly names an aesthetic, honor it literally. If two directions feel equally plausible, pick the less-common one.",
  "",
  "**Stances to consider:**",
  ...stances.map((s, i) => `${i + 1}. **${s.name}** — ${s.description}`),
  "",
  "**Typography traditions:**",
  ...traditions.map((t, i) => `${i + 1}. ${t.name} (${t.examples})`),
  "",
  "**Canvas treatment:**",
  `1. ${canvas.name}`,
  "",
  "YOUR TASK: Combine any preferences the user expressed with these directions to make a great theme for them. Be opinionated and specific. Commit to one stance — the most memorable outputs come from full commitment to one direction rather than hedging.",
];

console.log(lines.join("\n"));

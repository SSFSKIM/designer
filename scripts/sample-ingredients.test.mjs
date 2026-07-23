// scripts/sample-ingredients.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";

const run = (args = []) =>
  execFileSync("node", ["scripts/sample-ingredients.mjs", ...args], { encoding: "utf8" });

test("emits the verbatim card frame", () => {
  const out = run(["--seed", "7"]);
  assert.ok(out.startsWith("Here are some aesthetic ingredients to consider for this user's project."));
  assert.match(out, /Lean especially toward these directions to break out of trained defaults\. Treat them as tiebreakers when the brief is silent on aesthetic, not overrides — if the brief explicitly names an aesthetic, honor it literally\. If two directions feel equally plausible, pick the less-common one\./);
  assert.match(out, /YOUR TASK: Combine any preferences the user expressed with these directions to make a great theme for them\. Be opinionated and specific\. Commit to one stance — the most memorable outputs come from full commitment to one direction rather than hedging\.\s*$/);
});

test("draws exactly 3 stances, 2 traditions, 1 canvas, no duplicates", () => {
  const out = run(["--seed", "42"]);
  const stances = out.match(/^\d\. \*\*[^*]+\*\* — .+$/gm) ?? [];
  assert.equal(stances.length, 3);
  assert.equal(new Set(stances).size, 3);
  const traditionsSection = out.split("**Typography traditions:**")[1].split("**Canvas treatment:**")[0];
  const traditions = traditionsSection.match(/^\d\. .+ \(.+\)$/gm) ?? [];
  assert.equal(traditions.length, 2);
  assert.match(out, /\*\*Canvas treatment:\*\*\n1\. .+/);
});

test("same seed reproduces the draw; different seeds diverge", () => {
  assert.equal(run(["--seed", "7"]), run(["--seed", "7"]));
  const a = run(["--seed", "1"]);
  const b = run(["--seed", "2"]);
  const c = run(["--seed", "3"]);
  assert.ok(a !== b || b !== c, "three different seeds all produced identical draws");
});

test("rejects a non-numeric --seed instead of silently seeding zero", () => {
  assert.throws(
    () =>
      execFileSync("node", ["scripts/sample-ingredients.mjs", "--seed", "abc"], {
        encoding: "utf8",
        stdio: "pipe",
      }),
    (err) => {
      assert.equal(err.status, 1);
      assert.match(err.stderr, /--seed requires an integer/);
      return true;
    }
  );
});

test("library integrity: figma-verbatim entries intact", () => {
  const lib = JSON.parse(readFileSync("scripts/ingredients.json", "utf8"));
  assert.equal(lib.stances.filter((s) => s.origin === "figma").length, 10);
  assert.equal(lib.typographyTraditions.length, 13);
  assert.equal(lib.canvasTreatments.length, 5);
  assert.ok(lib.stances.length >= 16);
  const warm = lib.stances.find((s) => s.name === "warm");
  assert.equal(
    warm.description,
    "Aesop, Le Labo, boutique hospitality. Cream bases, muted earth tones, serif type, tactile-feeling imagery."
  );
});

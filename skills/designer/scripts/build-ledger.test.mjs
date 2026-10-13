// scripts/build-ledger.test.mjs — the distance, the five flags, the ordering, the missing-field rule,
// and a record-then-nearest round trip through a temporary ledger.
import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { hueDistance, flagsFor, nearest, parseArgs, entryFrom, load, append, report, contentWords } from "./build-ledger.mjs";

const script = fileURLToPath(new URL("./build-ledger.mjs", import.meta.url));
const pharmacy = { at: "2026-09-05T10:00:00Z", project: "pharmacy", brief: "hospital pharmacy inventory console", category: "console",
  accentHue: 308, accentJob: "directional", groundL: 0.17, groundHue: 265, groundTemperature: "neutral",
  display: "Commissioner", body: "Atkinson Hyperlegible Next", mono: "JetBrains Mono",
  signature: "the controlled-substance custody column", posture: "workspace", activity: "monitor", relation: "matrix", prior: "exception-first" };
const windfarm = { at: "2026-09-06T10:00:00Z", project: "wind-farm", brief: "wind-farm operations console", category: "console",
  accentHue: 328, accentJob: "directional", groundL: 0.975, groundHue: 90, groundTemperature: "warm",
  display: "Literata", body: "Barlow", mono: "JetBrains Mono",
  signature: "the survey plate with its string-line board", posture: "workspace", activity: "monitor", relation: "spatial-field", prior: "map-led" };
const library = { at: "2026-09-07T10:00:00Z", project: "library", brief: "summer reading programme page", category: "landing",
  accentHue: 25, accentJob: "directional", groundL: 0.885, groundHue: 150, groundTemperature: "brand-tinted",
  display: "Arvo", body: "Public Sans", signature: "a reader's stamp card with eight boxes", posture: "narrative", activity: "decide", relation: "sequence", prior: "asymmetric split" };

test("hue distance is circular", () => {
  assert.equal(hueDistance(10, 350), 20);
  assert.equal(hueDistance(308, 328), 20);
  assert.equal(hueDistance(0, 180), 180);
  assert.equal(hueDistance(-10, 10), 20);
});

test("accent flags inside the 30° band for directional accents only", () => {
  assert.match(flagsFor({ accentHue: 320, accentJob: "directional" }, pharmacy).join("|"), /accent: 12°/);
  assert.equal(flagsFor({ accentHue: 20, accentJob: "directional" }, pharmacy).length, 0);
  // a status-only or none job never flags, on either side
  assert.equal(flagsFor({ accentHue: 310, accentJob: "status-only" }, pharmacy).length, 0);
  assert.equal(flagsFor({ accentHue: "none", accentJob: "none" }, pharmacy).length, 0);
  assert.equal(flagsFor({ accentHue: 310, accentJob: "directional" }, { ...pharmacy, accentJob: "status-only" }).length, 0);
});

test("ground flags only when both grounds are tinted, on the same side, within 20°", () => {
  const warmLight = { groundL: 0.95, groundHue: 80, groundTemperature: "warm" };
  assert.match(flagsFor(warmLight, windfarm).join("|"), /ground: same side, 10°/);
  assert.equal(flagsFor({ ...warmLight, groundL: 0.2 }, windfarm).length, 0, "other side");
  assert.equal(flagsFor({ ...warmLight, groundTemperature: "neutral" }, windfarm).length, 0, "neutral never flags");
  assert.equal(flagsFor({ groundL: 0.95, groundHue: 265, groundTemperature: "cool" }, pharmacy).length, 0, "entry neutral");
});

test("family flags against the same category's last ten only", () => {
  const cand = { category: "console", display: "Atkinson Hyperlegible Next" };
  assert.match(flagsFor(cand, pharmacy, 0).join("|"), /family: Atkinson Hyperlegible Next is already the body of pharmacy/);
  assert.equal(flagsFor(cand, pharmacy, -1).length, 0, "different category");
  assert.equal(flagsFor(cand, pharmacy, 10).length, 0, "outside the window");
  assert.equal(flagsFor({ category: "console", display: "literata" }, windfarm, 3).length, 1, "case-insensitive");
});

test("signature flags on a shared content word", () => {
  assert.deepEqual([...contentWords("a reader's stamp card with eight boxes")].sort(), ["boxes", "eight", "reader", "stamp"]);
  const f = flagsFor({ signature: "a sheet of ten perforated week-stamps" }, library);
  assert.equal(f.length, 0, "stamps ≠ stamp: a different word");
  assert.match(flagsFor({ signature: "a stamp sheet" }, library).join("|"), /signature: "stamp" also in library's/);
});

test("form flags the same activity, relation and prior for a different brief", () => {
  const cand = { brief: "regional bus fleet maintenance console", activity: "monitor", relation: "matrix", prior: "Exception-first" };
  assert.match(flagsFor(cand, pharmacy).join("|"), /form: pharmacy compiled to exception-first/);
  assert.equal(flagsFor({ ...cand, brief: pharmacy.brief }, pharmacy).length, 0, "the same brief is expected to share its form");
  assert.equal(flagsFor({ ...cand, relation: "sequence" }, pharmacy).length, 0);
  assert.equal(flagsFor({ activity: "monitor", relation: "matrix" }, pharmacy).length, 0, "no prior given: never flags");
});

test("a candidate with nothing filled in flags nothing", () => {
  for (const e of [pharmacy, windfarm, library]) assert.deepEqual(flagsFor({}, e, 0), []);
});

test("nearest orders by flag count, then same category, then recency", () => {
  const cand = { category: "console", accentHue: 320, accentJob: "directional", display: "Literata", signature: "a stamp" };
  const rows = nearest([pharmacy, windfarm, library], cand);
  assert.deepEqual(rows.map((r) => r.entry.project), ["wind-farm", "pharmacy", "library"]);
  assert.equal(rows[0].flags.length, 2, "accent 8° and the Literata display");
  assert.equal(rows[1].flags.length, 1, "accent 12°");
  assert.equal(rows[2].flags.length, 1, "the stamp");
  assert.equal(nearest([pharmacy, windfarm, library], cand, 1).length, 1);
});

test("parseArgs reads the flags, numbers, none and the empty ledger report", () => {
  const a = parseArgs(["--project", "p", "--accent-hue", "none", "--accent-job", "none", "--ground-l", "0.94", "--display", "Arvo", "--n", "5"]);
  assert.deepEqual(a, { project: "p", accentHue: "none", accentJob: "none", groundL: 0.94, display: "Arvo", n: 5 });
  const e = entryFrom(a, new Date("2026-10-12T00:00:00Z"));
  assert.equal(e.at, "2026-10-12T00:00:00.000Z");
  assert.equal(e.source, "record");
  assert.equal(e.n, undefined, "n is not a field");
  assert.match(report([], a, "/tmp/x"), /The ledger is empty/);
});

test("record then nearest round-trips through DESIGNER_LEDGER", () => {
  const dir = mkdtempSync(join(tmpdir(), "build-ledger-"));
  const file = join(dir, "nested", "ledger.jsonl");
  const env = { ...process.env, DESIGNER_LEDGER: file };
  const run = (...args) => execFileSync(process.execPath, [script, ...args], { env, encoding: "utf8" });
  assert.equal(run("path").trim(), file);
  run("record", "--project", "pharmacy", "--category", "console", "--accent-hue", "308", "--accent-job", "directional", "--display", "Commissioner", "--signature", "the custody column");
  run("record", "--project", "library", "--category", "landing", "--accent-hue", "25", "--accent-job", "directional");
  assert.equal(load(file).length, 2);
  const out = run("nearest", "--category", "console", "--accent-hue", "300", "--accent-job", "directional", "--display", "commissioner");
  assert.match(out, /2 entries/);
  assert.match(out, /! 20\d\d-\d\d-\d\d  pharmacy/);
  assert.match(out, /accent: 8° from pharmacy's 308°/);
  assert.match(out, /family: commissioner is already the display of pharmacy/);
  assert.match(out, /1 of 2 shown raise a flag/);
  assert.match(run("list", "--category", "landing"), /library/);
  append(file, { at: "2026-01-01T00:00:00Z", project: "x" });
  assert.equal(load(file).length, 3);
});

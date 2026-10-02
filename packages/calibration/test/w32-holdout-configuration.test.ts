import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { cpSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { describe, expect, it } from "vitest";

/**
 * W32 G0b — the holdout rule's artifact, at the cross-gate location (claims §5.167).
 *
 * W31 Decision Log 1 (b) made the holdout rule enforceable by a committed LOG
 * rather than by a reviewer's memory, and the thing it guards against leaves no
 * trace in any number: a second holdout read at the same material turns the
 * anti-overfitting split's third set into a second validation set, and every
 * figure it produces looks exactly like a figure produced honestly. So the
 * refusal is the whole artifact, and a refusal nothing exercises is a refusal
 * nobody has run.
 *
 * The script is exercised AS COMMITTED, over a synthetic repository: a tree with
 * the six source paths and the four profile documents the configuration names,
 * at the depth the script resolves them from. That is what lets the test move a
 * source byte and a document byte — the two axes the rule turns on — without
 * touching the real ones, and it means the bytes under test are the bytes a gate
 * will run rather than a re-implementation of them.
 */
const PACKAGE_ROOT = resolve(import.meta.dirname, "..");
const SCRIPT = resolve(PACKAGE_ROOT, "results", "holdout-configuration", "configuration.py");
const LEDGER_LOG = resolve(PACKAGE_ROOT, "results", "holdout-configuration", "configuration-log.json");
const W31_G3_LOG = resolve(
  PACKAGE_ROOT, "results", "2026-09-21-w31-g3-chroma-fit", "configuration-log.json");

const DOCUMENTS = [
  "apple-macos-27.0-1x-light-standard-glass0.5.json",
  "apple-macos-27.0-1x-dark-standard-glass0.5.json",
  "apple-macos-27.0-1x-light-standard-glass0.5-receded.json",
  "apple-macos-27.0-1x-dark-standard-glass0.5-receded.json",
] as const;

/** The 0.25 generation's four documents, the second set `--documents glass0.25` names (W43 G3 (ii)). */
const DOCUMENTS_025 = [
  "apple-macos-27.0-1x-light-standard-glass0.25.json",
  "apple-macos-27.0-1x-dark-standard-glass0.25.json",
  "apple-macos-27.0-1x-light-standard-glass0.25-receded.json",
  "apple-macos-27.0-1x-dark-standard-glass0.25-receded.json",
] as const;

/** The six entries of `SOURCE_LIST`, as paths beneath the synthetic root. */
const SOURCES = [
  "packages/renderer-webgpu/src/wgsl/optics.ts",
  "packages/renderer-webgpu/src/material.ts",
  "packages/renderer-webgpu/src/renderer.ts",
  "packages/renderer-webgpu/src/passes.ts",
  "packages/platform-web/src/optics.ts",
  "packages/platform-web/src/css-tier.ts",
] as const;

interface Ledger {
  readonly reads: readonly {
    readonly at: string;
    readonly head: string;
    readonly claims: string;
    readonly documents: Record<string, string>;
    readonly sourceSha256: string;
    readonly sourceFileCount: number;
    readonly sourceListSha256?: string;
    readonly sourceMovedBecause?: string;
  }[];
}

/**
 * A repository the script can resolve its way around: the script sits at
 * `<root>/packages/calibration/results/holdout-configuration/`, reads documents
 * from `<root>/packages/calibration/profiles/` and sources from `<root>/packages/`.
 * Nothing here is a git repository, which the script already tolerates — `head()`
 * reports `unknown` rather than failing, because a read taken outside a checkout
 * is still a read that has to be refused a second time.
 */
function synthetic(): { root: string; log: string } {
  const root = mkdtempSync(join(tmpdir(), "w32-g0b-configuration-"));
  const gate = join(root, "packages", "calibration", "results", "holdout-configuration");
  mkdirSync(gate, { recursive: true });
  cpSync(SCRIPT, join(gate, "configuration.py"));
  mkdirSync(join(root, "packages", "calibration", "profiles"), { recursive: true });
  for (const name of [...DOCUMENTS, ...DOCUMENTS_025]) {
    writeFileSync(join(root, "packages", "calibration", "profiles", name), `{"patch":{},"n":"${name}"}\n`);
  }
  for (const rel of SOURCES) {
    const path = join(root, ...rel.split("/"));
    mkdirSync(resolve(path, ".."), { recursive: true });
    writeFileSync(path, `// ${rel}\n`);
  }
  return { root, log: join(gate, "configuration-log.json") };
}

function run(root: string, args: readonly string[]): { status: number | null; output: string } {
  const script = join(root, "packages", "calibration", "results", "holdout-configuration", "configuration.py");
  const result = spawnSync("python3", [script, ...args], {
    cwd: root, encoding: "utf8", timeout: 120_000,
  });
  return { status: result.status, output: `${result.stdout ?? ""}${result.stderr ?? ""}` };
}

const ledger = (path: string): Ledger => JSON.parse(readFileSync(path, "utf8")) as Ledger;

describe("the holdout configuration artifact (W31 Decision Log 1 (b); claims §5.167)", () => {
  it("records a first read, then refuses a second at the same documents and sources", () => {
    const { root, log } = synthetic();

    const first = run(root, ["record", "--claims", "c9a §5.NNN"]);
    expect(first.status, first.output).toBe(0);
    expect(first.output).toContain("RECORDED — holdout read 1");
    expect(ledger(log).reads).toHaveLength(1);

    const second = run(root, ["record", "--claims", "c9a §5.NNN"]);
    expect(second.status, second.output).toBe(1);
    expect(second.output).toContain("REFUSED: identical document bytes AND identical sources");
    // The refusal is the point, and so is what it leaves behind: a refused read
    // appends nothing, or the log would grow a record of a read nobody took.
    expect(ledger(log).reads).toHaveLength(1);
  });

  it("refuses a moved source with no reason, and admits it with the reason recorded", () => {
    const { root, log } = synthetic();
    expect(run(root, ["record", "--claims", "c9a §5.NNN"]).status).toBe(0);

    // A renderer fix: one source byte moves, the documents do not.
    writeFileSync(join(root, ...SOURCES[2].split("/")), "// renderer.ts, after a fix\n");

    const unexplained = run(root, ["record", "--claims", "c9a §5.NNN"]);
    expect(unexplained.status, unexplained.output).toBe(1);
    expect(unexplained.output).toContain("the sources moved and no reason is named");
    expect(ledger(log).reads).toHaveLength(1);

    const reason = "a renderer fix, no fitted constant moved";
    const explained = run(root, [
      "record", "--claims", "c9a §5.NNN", "--source-moved-because", reason]);
    expect(explained.status, explained.output).toBe(0);
    const reads = ledger(log).reads;
    expect(reads).toHaveLength(2);
    expect(reads[1]?.sourceMovedBecause).toBe(reason);
    // Both halves are required together, so the record has to carry both: the
    // reason, and the moved hash it is the reason for.
    expect(reads[1]?.sourceSha256).not.toBe(reads[0]?.sourceSha256);
  });

  it("refuses a third read at sources that moved away and back, reason or not", () => {
    // W32 G0b review closure, NB1 (claims §5.167 §8). A configuration is a set of bytes,
    // not a position in a list. Comparing only against the LAST record at these documents
    // admitted A → B → A: the third read is at the sources the first read was taken at,
    // and the read in between does not make it a new configuration. That is the exact
    // thing Decision Log 1 (b) forbids, arrived at by a route the refusal did not watch —
    // a renderer fix and its revert, or a rebase that lands on an earlier tree.
    const { root, log } = synthetic();
    const source = join(root, ...SOURCES[2].split("/"));
    const original = readFileSync(source);

    expect(run(root, ["record", "--claims", "c9a §5.NNN"]).status).toBe(0);

    writeFileSync(source, "// renderer.ts, after a fix\n");
    const moved = run(root, [
      "record", "--claims", "c9a §5.NNN", "--source-moved-because", "a renderer fix"]);
    expect(moved.status, moved.output).toBe(0);
    expect(ledger(log).reads).toHaveLength(2);

    writeFileSync(source, original);
    const returned = run(root, [
      "record", "--claims", "c9a §5.NNN", "--source-moved-because", "the fix was reverted"]);
    expect(returned.status, returned.output).toBe(1);
    expect(returned.output).toContain("REFUSED: identical document bytes AND identical sources");
    // The reason is answered rather than ignored: a reader who supplied one is told why
    // it does not help, or the next attempt is a longer reason.
    expect(returned.output).toContain("It cannot re-open a");
    expect(ledger(log).reads).toHaveLength(2);
    // And the read it names is the FIRST one at those sources — the read this would have
    // been a second of — rather than the most recent entry in the log, which is the one
    // the defect looked at.
    const first = ledger(log).reads[0];
    expect(returned.output).toContain(`${first?.at}, head ${first?.head}, claims ${first?.claims}.`);
  });

  it("takes a read at moved document bytes without a reason — it is a new configuration", () => {
    const { root, log } = synthetic();
    expect(run(root, ["record", "--claims", "c9a §5.NNN"]).status).toBe(0);

    writeFileSync(
      join(root, "packages", "calibration", "profiles", DOCUMENTS[0]),
      `{"patch":{"refit":1},"n":"${DOCUMENTS[0]}"}\n`,
    );
    const refit = run(root, ["record", "--claims", "c9a §5.MMM"]);
    expect(refit.status, refit.output).toBe(0);
    expect(refit.output).toContain("RECORDED — holdout read 2");
    expect(refit.output).not.toContain("a holdout read already exists");
    expect(ledger(log).reads).toHaveLength(2);
  });

  it("records the source LIST's digest beside the sources', so a widened list is visible", () => {
    // `sourceSha256` is only comparable across two reads taken over the same
    // enumeration, and the enumeration is narrower than the render's import
    // closure by fifty files (claims §5.167). Recording the definition's own
    // digest is what makes a later widening a field that moved rather than a
    // comparison that quietly stopped meaning anything.
    const { root, log } = synthetic();
    expect(run(root, ["record", "--claims", "c9a §5.NNN"]).status).toBe(0);
    const recorded = ledger(log).reads[0]?.sourceListSha256;
    expect(recorded).toMatch(/^[0-9a-f]{64}$/);
    expect(run(root, ["show"]).output).toContain(recorded ?? "");
  });

  it("pins both document sets: 0.5 by default, 0.25 by --documents, each refused only by itself", () => {
    // W43 G3 (ii): one ledger for two generations. The default set is the 0.5 one, unchanged;
    // a 0.25 read records its own four documents and `documentSet`, and a second 0.25 read at
    // the same bytes and sources is refused exactly as a second 0.5 read is.
    const { root, log } = synthetic();
    expect(run(root, ["record", "--claims", "c9a §5.NNN"]).status).toBe(0);
    const first025 = run(root, ["record", "--claims", "c9a §5.201", "--documents", "glass0.25"]);
    expect(first025.status, first025.output).toBe(0);
    expect(first025.output).not.toContain("a holdout read already exists");
    const reads = ledger(log).reads as readonly (Ledger["reads"][number] & { documentSet?: string })[];
    expect(reads).toHaveLength(2);
    expect(Object.keys(reads[0]!.documents).sort()).toEqual([...DOCUMENTS].sort());
    expect(reads[0]!.documentSet).toBeUndefined();
    expect(Object.keys(reads[1]!.documents).sort()).toEqual([...DOCUMENTS_025].sort());
    expect(reads[1]!.documentSet).toBe("glass0.25");
    const again025 = run(root, ["record", "--claims", "c9a §5.201", "--documents", "glass0.25"]);
    expect(again025.status, again025.output).toBe(1);
    expect(again025.output).toContain("REFUSED: identical document bytes AND identical sources");
    const again05 = run(root, ["record", "--claims", "c9a §5.NNN"]);
    expect(again05.status, again05.output).toBe(1);
    expect(ledger(log).reads).toHaveLength(2);
    const unknown = run(root, ["show", "--documents", "glass0.7"]);
    expect(unknown.status).not.toBe(0);
    expect(unknown.output).toContain("names no document set");
  });

  it("records a referee manifest as witness-only metadata and leaves the default read unchanged", () => {
    // W44 G0 (d), charter clause 7 and X49: the exposure reads the canonical holdout and the
    // referee cells together, and the ledger's record names which manifest it exposed. The
    // manifest is a WITNESS: it never makes a configuration new, so a second read at the same
    // documents and sources is refused whatever manifest it names.
    const { root, log } = synthetic();
    const manifest = join(root, "referees.json");
    const body = { schema: "w44-referees-1", profiles: ["p"], scenes: ["s"] };
    writeFileSync(manifest, `${JSON.stringify(body)}\n`);

    // The default read writes exactly the entry it wrote before W44.
    expect(run(root, ["record", "--claims", "c9a §5.NNN"]).status).toBe(0);
    const plain = ledger(log).reads[0] as Record<string, unknown>;
    expect(Object.keys(plain).sort()).toEqual(
      ["at", "claims", "documents", "head", "sourceFileCount", "sourceListSha256", "sourceSha256"]);

    // A first 0.25 read with the manifest records its path and hash beside the documents.
    const witnessed = run(root, [
      "record", "--claims", "c9a §5.203", "--documents", "glass0.25", "--referees", manifest]);
    expect(witnessed.status, witnessed.output).toBe(0);
    const entry = ledger(log).reads[1] as Record<string, unknown> & {
      refereeManifest?: { path: string; sha256: string } };
    const digest = createHash("sha256").update(readFileSync(manifest)).digest("hex");
    expect(entry.refereeManifest).toEqual({ path: "referees.json", sha256: digest });
    expect(entry["documentSet"]).toBe("glass0.25");

    // Not a discriminator: another manifest at the same documents and sources is refused, and
    // the refusal lists the earlier read WITH its manifest; an old-style read (no manifest) is
    // still the configuration it was, so the default set's second read is refused as before.
    writeFileSync(manifest, `${JSON.stringify({ ...body, scenes: ["s", "t"] })}\n`);
    const again = run(root, [
      "record", "--claims", "c9a §5.203", "--documents", "glass0.25", "--referees", manifest]);
    expect(again.status, again.output).toBe(1);
    expect(again.output).toContain("REFUSED: identical document bytes AND identical sources");
    expect(again.output).toContain(`referees ${digest.slice(0, 12)}`);
    const old = run(root, ["record", "--claims", "c9a §5.NNN", "--referees", manifest]);
    expect(old.status, old.output).toBe(1);
    expect(old.output).toContain("REFUSED: identical document bytes AND identical sources");
    expect(ledger(log).reads).toHaveLength(2);

    // Something that is not a manifest is refused before anything is written.
    writeFileSync(manifest, "{\"schema\": \"other\"}\n");
    writeFileSync(join(root, ...SOURCES[2].split("/")), "// renderer.ts, moved\n");
    const notOne = run(root, [
      "record", "--claims", "c9a §5.NNN", "--source-moved-because", "a fix", "--referees", manifest]);
    expect(notOne.status).not.toBe(0);
    expect(notOne.output).toContain("is not a referee manifest");
    expect(ledger(log).reads).toHaveLength(2);
  });

  it("carries W31 G3's and G3c's two reads across the move, unbroken", () => {
    // The seeded history is the reason this directory could be created at all
    // rather than started: a ledger that begins empty refuses nothing that came
    // before it. The G3 copy is the witness and is not edited; this asserts the
    // seed against it rather than against a transcription.
    const seeded = ledger(LEDGER_LOG).reads;
    const witness = ledger(W31_G3_LOG).reads;
    expect(witness).toHaveLength(2);
    expect(seeded.slice(0, witness.length)).toEqual(witness);
    expect(seeded[0]?.claims).toBe("c9a §5.164");
    expect(seeded[1]?.claims).toBe("c9a §5.164 §13");
  });
});

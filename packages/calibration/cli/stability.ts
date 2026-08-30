#!/usr/bin/env tsx
/**
 * Classify every cell of a capture bed across many runs of one protocol.
 *
 * The stability study's reading instrument. `materialize` asks "may this cell be
 * published?" over the two or three runs of an ordinary capture; this asks "what
 * does this cell DO?" over eight runs of one protocol arm, and answers per cell
 * rather than per bed.
 *
 * It classifies with the same rule `materialize` publishes by — `resolveCell`
 * over `differenceSummary` — deliberately. A study that measured stability one
 * way and a bed that was published another would produce a doctrine about a
 * different instrument than the one it governs.
 *
 * Usage:
 *   stability.ts --label baseline --runs dirA,dirB,dirC[,…]
 *
 * Each directory is a whole run snapshot: profile directories plus that run's
 * `manifest.json`. Nothing is written and no bed is touched.
 */
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { createHash } from "node:crypto";
import { resolve } from "node:path";

import { decodePng } from "../src/image";
import {
  classifyDifference,
  differenceSummary,
  type CaptureVariant,
  type VariantDifference,
} from "../src/plurality";

interface RunSnapshot {
  readonly label: string;
  readonly dir: string;
  readonly entries: Map<string, Record<string, unknown>>;
}

/** What a cell did across the arm's runs. */
type CellClass =
  | "deterministic"
  | "bistable"
  | "multi-state"
  | "noisy"
  /**
   * At least one contributing run did not attest the window key and the app
   * active while this cell was captured.
   *
   * Liquid Glass renders a flat, unfocused pose in that state, so the bytes are
   * a photograph of the wrong material. This is not a verdict about the cell and
   * must never be averaged in with one — measured 2026-08-31, a session that
   * auto-locked mid-study turned eight cells of one run and all 54 of the next
   * into exactly this, and the attestation caught every one.
   */
  | "unattested";

interface CellVerdict {
  readonly cell: string;
  readonly profile: string;
  readonly scene: string;
  readonly verdict: CellClass;
  readonly variants: readonly CaptureVariant[];
  /** Worst difference between the leading variant and any structurally distinct one. */
  readonly worst?: VariantDifference;
  /** Capture-order position, when every run agreed on one. */
  readonly orderIndex?: number;
  /**
   * Distinct positions this cell was captured at across the arm.
   *
   * Zero means the runs predate schema 3 and did not record it, which is not the
   * same as "the order varied" and must not be printed as if it were.
   */
  readonly orderPositions: number;
}

const sha = (bytes: Uint8Array): string => createHash("sha256").update(bytes).digest("hex");

function loadRun(spec: string): RunSnapshot {
  const dir = resolve(process.cwd(), spec);
  const manifestPath = resolve(dir, "manifest.json");
  if (!existsSync(manifestPath)) throw new Error(`run ${spec}: no manifest.json under ${dir}`);
  const manifest = JSON.parse(readFileSync(manifestPath, "utf8")) as {
    profiles?: { profileKey?: string; fixtures?: { sceneId?: string }[] }[];
    captureProtocol?: Record<string, unknown>;
  };
  const entries = new Map<string, Record<string, unknown>>();
  for (const profile of manifest.profiles ?? []) {
    for (const fixture of profile.fixtures ?? []) {
      entries.set(`${profile.profileKey}/${fixture.sceneId}`, fixture as Record<string, unknown>);
    }
  }
  const label = String(
    (manifest.captureProtocol?.["runLabel"] as string | undefined) ?? dir.split("/").pop() ?? spec,
  );
  return { label, dir, entries };
}

function verdictFor(
  cell: string,
  profile: string,
  scene: string,
  runs: readonly RunSnapshot[],
): CellVerdict {
  const byHash = new Map<string, { runs: string[]; settled: boolean }>();
  const images = new Map<string, Uint8Array>();
  const positions = new Set<number>();
  const unattested: string[] = [];
  for (const run of runs) {
    const path = resolve(run.dir, profile, `${scene}.png`);
    if (!existsSync(path)) continue;
    if (run.entries.get(cell)?.["presentedActive"] !== true) {
      unattested.push(run.label);
      continue;
    }
    const data = new Uint8Array(readFileSync(path));
    const hash = sha(data);
    images.set(hash, data);
    const entry = run.entries.get(cell);
    const settled = entry?.["deterministic"] === true;
    const at = entry?.["orderIndex"];
    if (typeof at === "number") positions.add(at);
    const existing = byHash.get(hash);
    if (existing === undefined) byHash.set(hash, { runs: [run.label], settled });
    else {
      existing.runs.push(run.label);
      existing.settled = existing.settled && settled;
    }
  }

  const variants: CaptureVariant[] = [...byHash]
    .map(([sha256, v]) => ({ sha256, runs: v.runs, settled: v.settled }))
    .sort((a, b) => b.runs.length - a.runs.length);
  const orderIndex = positions.size === 1 ? [...positions][0] : undefined;
  const base = { cell, profile, scene, variants, orderPositions: positions.size } as const;

  // A cell is only classified over the runs that attested it. Fewer than two of
  // those and there is nothing to compare, so it is reported as unattested
  // rather than silently read as stable — which is what a single surviving
  // observation would otherwise look like.
  if (unattested.length > 0 && variants.length < 2) {
    return { ...base, verdict: "unattested", ...(orderIndex === undefined ? {} : { orderIndex }) };
  }

  if (variants.length <= 1) {
    return { ...base, verdict: "deterministic", ...(orderIndex === undefined ? {} : { orderIndex }) };
  }

  const leader = variants[0] as CaptureVariant;
  const difference = (other: CaptureVariant): VariantDifference => {
    const a = decodePng(images.get(leader.sha256) as Uint8Array);
    const b = decodePng(images.get(other.sha256) as Uint8Array);
    return differenceSummary(a.data, b.data, a.width, a.height);
  };
  const structured = variants
    .slice(1)
    .map((other) => ({ other, d: difference(other) }))
    .filter(({ other, d }) => other.settled && leader.settled && classifyDifference(d) === "structured");

  if (structured.length === 0) {
    return { ...base, verdict: "noisy", ...(orderIndex === undefined ? {} : { orderIndex }) };
  }
  const worst = structured.reduce((a, b) => (b.d.maxDelta > a.d.maxDelta ? b : a)).d;
  return {
    ...base,
    verdict: structured.length === 1 ? "bistable" : "multi-state",
    worst,
    ...(orderIndex === undefined ? {} : { orderIndex }),
  };
}

function main(): void {
  const argv = process.argv.slice(2);
  const flag = (name: string): string | undefined => {
    const i = argv.indexOf(`--${name}`);
    return i >= 0 ? argv[i + 1] : undefined;
  };
  const label = flag("label") ?? "arm";
  const specs = (flag("runs") ?? "").split(",").map((s) => s.trim()).filter(Boolean);
  if (specs.length < 2) throw new Error("stability: --runs takes at least two run snapshot directories.");
  const runs = specs.map(loadRun);
  const first = runs[0] as RunSnapshot;
  const profiles = readdirSync(first.dir, { withFileTypes: true })
    .filter((e) => e.isDirectory())
    .map((e) => e.name)
    .sort();

  const verdicts: CellVerdict[] = [];
  for (const profile of profiles) {
    for (const name of readdirSync(resolve(first.dir, profile)).filter((n) => n.endsWith(".png")).sort()) {
      verdicts.push(verdictFor(`${profile}/${name.slice(0, -4)}`, profile, name.slice(0, -4), runs));
    }
  }

  if (argv.includes("--json")) {
    process.stdout.write(
      `${JSON.stringify(
        {
          arm: label,
          runs: runs.map((r) => r.label),
          cells: verdicts.map((v) => ({
            cell: v.cell,
            profile: v.profile,
            scene: v.scene,
            verdict: v.verdict,
            orderPositions: v.orderPositions,
            ...(v.orderIndex === undefined ? {} : { orderIndex: v.orderIndex }),
            variants: v.variants.map((x) => ({ sha: x.sha256.slice(0, 12), runs: x.runs, settled: x.settled })),
            ...(v.worst === undefined ? {} : { worst: v.worst }),
          })),
        },
        null,
        2,
      )}\n`,
    );
    return;
  }

  const counts = new Map<CellClass, number>();
  for (const v of verdicts) counts.set(v.verdict, (counts.get(v.verdict) ?? 0) + 1);
  process.stdout.write(
    `arm '${label}': ${runs.length} run(s) [${runs.map((r) => r.label).join(", ")}], ${verdicts.length} cell(s)\n` +
      `  ${(["deterministic", "noisy", "bistable", "multi-state", "unattested"] as CellClass[])
        .map((k) => `${k} ${counts.get(k) ?? 0}`)
        .join(" · ")}\n`,
  );
  for (const v of verdicts.filter((x) => x.verdict === "bistable" || x.verdict === "multi-state")) {
    const split = v.variants.map((x) => `${x.sha256.slice(0, 8)}×${x.runs.length}`).join(" / ");
    const w = v.worst;
    process.stdout.write(
      `  ${v.verdict.toUpperCase().padEnd(11)} ${v.cell}\n` +
        `      ${split}` +
        (w ? `  | maxDelta ${w.maxDelta}, ${w.changedPx} px, coherence ${w.coherence.toFixed(3)}` : "") +
        (v.orderPositions === 0
          ? "  | order not recorded"
          : v.orderPositions === 1
            ? `  | order ${v.orderIndex}`
            : `  | order varied across ${v.orderPositions} positions`) +
        "\n",
    );
  }
  for (const v of verdicts.filter((x) => x.verdict === "noisy")) {
    process.stdout.write(`  noisy       ${v.cell} (${v.variants.length} variants, all within the raster's precision)\n`);
  }
}

try {
  main();
} catch (error) {
  process.stderr.write(`stability: ${error instanceof Error ? error.message : String(error)}\n`);
  process.exit(1);
}

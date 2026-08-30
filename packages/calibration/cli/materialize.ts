#!/usr/bin/env tsx
/**
 * Materialise the reference bed from several raw capture runs.
 *
 * Each run is a whole snapshot of the fixture profiles it captured, taken before
 * anything was decided — `--run E=<dir>` and so on, where `<dir>` holds the
 * profile directories plus that run's `manifest.json`. This tool decides, per
 * cell, which run's bytes are published, and writes both the PNG and *that run's
 * own manifest entry*, so a cell's recorded checksum, chroma and attestations
 * always describe the bytes beside them.
 *
 * The decision is `resolveCell` (see `src/plurality.ts`): a majority where the
 * disagreement is noise, and a refusal where the runs returned two settled
 * appearances that differ structurally. A refusal is not an error the tool can
 * repair — it is the finding, and it exits non-zero with both variants named.
 *
 * Nothing is written unless every cell resolves. A bed half-published under a
 * manifest describing the other half is the failure mode the harness's own
 * staging discipline exists to prevent, and this inherits it.
 */
import { copyFileSync, existsSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { decodePng } from "../src/image";
import {
  differenceSummary,
  resolveCell,
  type CaptureVariant,
  type CellResolution,
} from "../src/plurality";

const PACKAGE_ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..");
const REPO_ROOT = resolve(PACKAGE_ROOT, "..", "..");
const FIXTURES = resolve(REPO_ROOT, "apps", "reference-apple", "fixtures");
const SCENES = resolve(REPO_ROOT, "apps", "reference-apple", "scenes.json");

/**
 * The declared role of every scene, read from the scene matrix rather than from
 * the manifest the capture wrote.
 *
 * A role is a property of the *declaration*, not of the bytes: moving a scene
 * between sets cannot change a pixel. So when a run is materialised the role is
 * taken from the declaration as it stands now, and every change is printed. The
 * alternative — publishing the role the capture happened to be run under — would
 * make a bed that disagrees with its own scene matrix, which `compare` then
 * refuses by name and which no re-capture can fix without a GUI session.
 */
function declaredRoles(): Map<string, string> {
  const spec = JSON.parse(readFileSync(SCENES, "utf8")) as {
    split?: Record<string, readonly string[] | undefined>;
  };
  const roles = new Map<string, string>();
  for (const role of ["calibration", "validation", "holdout", "recorded"]) {
    for (const id of spec.split?.[role] ?? []) roles.set(id, role);
  }
  return roles;
}

interface RunSnapshot {
  readonly label: string;
  readonly dir: string;
  /** `profileKey/sceneId` → the manifest entry that run recorded for it. */
  readonly entries: Map<string, Record<string, unknown>>;
}

function loadRun(label: string, dir: string): RunSnapshot {
  const manifestPath = resolve(dir, "manifest.json");
  if (!existsSync(manifestPath)) {
    throw new Error(`run ${label}: no manifest.json under ${dir} — snapshot the whole run, not just its PNGs.`);
  }
  const manifest = JSON.parse(readFileSync(manifestPath, "utf8")) as {
    profiles?: { profileKey?: string; fixtures?: { sceneId?: string }[] }[];
  };
  const entries = new Map<string, Record<string, unknown>>();
  for (const profile of manifest.profiles ?? []) {
    for (const fixture of profile.fixtures ?? []) {
      entries.set(`${profile.profileKey}/${fixture.sceneId}`, fixture as Record<string, unknown>);
    }
  }
  return { label, dir, entries };
}

const sha = (bytes: Uint8Array): string => createHash("sha256").update(bytes).digest("hex");

/**
 * Group the runs' bytes into distinct variants.
 *
 * `settled` is the AND over the runs that produced a variant: one unsettled run
 * is enough to stop the variant standing as evidence of a state, because the
 * claim being made is "the machine returns this on purpose".
 */
function variantsOf(
  cell: string,
  runs: readonly RunSnapshot[],
  bytes: Map<string, Uint8Array>,
): { variants: CaptureVariant[]; images: Map<string, Uint8Array> } {
  const byHash = new Map<string, { runs: string[]; settled: boolean }>();
  const images = new Map<string, Uint8Array>();
  for (const run of runs) {
    const data = bytes.get(run.label);
    if (data === undefined) continue;
    const hash = sha(data);
    images.set(hash, data);
    const entry = run.entries.get(cell);
    const settled = entry?.["deterministic"] === true;
    const existing = byHash.get(hash);
    if (existing === undefined) byHash.set(hash, { runs: [run.label], settled });
    else {
      existing.runs.push(run.label);
      existing.settled = existing.settled && settled;
    }
  }
  return {
    variants: [...byHash].map(([sha256, v]) => ({ sha256, runs: v.runs, settled: v.settled })),
    images,
  };
}

function parseArgs(argv: readonly string[]): {
  runs: { label: string; dir: string }[];
  profiles: string[];
  apply: boolean;
} {
  const runs: { label: string; dir: string }[] = [];
  const profiles: string[] = [];
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === "--run") {
      const raw = argv[i + 1] ?? "";
      const [label, ...rest] = raw.split("=");
      if (label === undefined || rest.length === 0) {
        throw new Error(`--run expects LABEL=DIR, got '${raw}'.`);
      }
      runs.push({ label, dir: resolve(process.cwd(), rest.join("=")) });
      i += 1;
    } else if (argv[i] === "--profile") {
      profiles.push(...(argv[i + 1] ?? "").split(",").map((s) => s.trim()).filter(Boolean));
      i += 1;
    }
  }
  if (runs.length < 2) throw new Error("materialize: give at least two --run LABEL=DIR snapshots.");
  return { runs, profiles, apply: argv.includes("--apply") };
}

function main(): void {
  const options = parseArgs(process.argv.slice(2));
  const runs = options.runs.map((r) => loadRun(r.label, r.dir));
  const first = runs[0] as RunSnapshot;
  const profiles =
    options.profiles.length > 0
      ? options.profiles
      : readdirSync(first.dir, { withFileTypes: true })
          .filter((e) => e.isDirectory())
          .map((e) => e.name);

  const decisions: { cell: string; profile: string; scene: string; outcome: CellResolution }[] = [];
  const publish: { from: string; profile: string; scene: string; entry: Record<string, unknown> }[] = [];

  for (const profile of profiles) {
    const names = readdirSync(resolve(first.dir, profile))
      .filter((n) => n.endsWith(".png"))
      .sort();
    for (const name of names) {
      const scene = name.slice(0, -4);
      const cell = `${profile}/${scene}`;
      const bytes = new Map<string, Uint8Array>();
      for (const run of runs) {
        const path = resolve(run.dir, profile, name);
        if (existsSync(path)) bytes.set(run.label, new Uint8Array(readFileSync(path)));
      }
      if (bytes.size !== runs.length) {
        throw new Error(`${cell}: only ${bytes.size} of ${runs.length} runs captured it — the runs are not comparable.`);
      }

      const { variants, images } = variantsOf(cell, runs, bytes);
      const outcome = resolveCell(variants, (a, b) => {
        const left = decodePng(images.get(a.sha256) as Uint8Array);
        const right = decodePng(images.get(b.sha256) as Uint8Array);
        return differenceSummary(left.data, right.data, left.width, left.height);
      });
      decisions.push({ cell, profile, scene, outcome });
      if (outcome.kind !== "refused") {
        const winner = outcome.chosen.runs[0] as string;
        const entry = runs.find((r) => r.label === winner)?.entries.get(cell);
        if (entry === undefined) throw new Error(`${cell}: run ${winner} published bytes with no manifest entry.`);
        publish.push({ from: resolve(options.runs.find((r) => r.label === winner)?.dir ?? "", profile, name), profile, scene, entry });
      }
    }
  }

  const refused = decisions.filter((d) => d.outcome.kind === "refused");
  const voted = decisions.filter((d) => d.outcome.kind === "voted");
  const ambiguous = refused.filter((d) => d.outcome.kind === "refused" && d.outcome.stateAmbiguous);

  process.stdout.write(
    `${decisions.length} cell(s) over ${profiles.length} profile(s) from ${runs.length} run(s): ` +
      `${decisions.length - voted.length - refused.length} unanimous, ${voted.length} voted, ` +
      `${refused.length} refused (${ambiguous.length} state-ambiguous)\n`,
  );
  for (const d of voted) {
    if (d.outcome.kind !== "voted") continue;
    process.stdout.write(`  voted    ${d.cell} → ${d.outcome.chosen.runs.join("")}; ${d.outcome.reason}\n`);
  }
  for (const d of refused) {
    if (d.outcome.kind !== "refused") continue;
    process.stdout.write(
      `  ${d.outcome.stateAmbiguous ? "AMBIGUOUS" : "NO PLURALITY"} ${d.cell}\n    ${d.outcome.reason}\n`,
    );
  }

  if (refused.length > 0) {
    process.stderr.write(
      `\nmaterialize: nothing written. ${refused.length} cell(s) cannot be published without a ruling, ` +
        `and a bed materialised around them would be a bed with a hole the manifest does not mention.\n`,
    );
    process.exit(1);
  }
  if (!options.apply) {
    process.stdout.write("\nevery cell resolves. Re-run with --apply to write the bed.\n");
    return;
  }

  const roles = declaredRoles();
  const manifestPath = resolve(FIXTURES, "manifest.json");
  const manifest = JSON.parse(readFileSync(manifestPath, "utf8")) as {
    profiles?: { profileKey?: string; fixtures?: { sceneId?: string }[] }[];
  };
  const rerolled: string[] = [];
  for (const p of publish) {
    copyFileSync(p.from, resolve(FIXTURES, p.profile, `${p.scene}.png`));
    const profile = manifest.profiles?.find((m) => m.profileKey === p.profile);
    if (profile === undefined) continue;
    const at = profile.fixtures?.findIndex((f) => f.sceneId === p.scene) ?? -1;
    if (at < 0 || profile.fixtures === undefined) continue;
    const role = roles.get(p.scene);
    if (role === undefined) {
      throw new Error(`${p.profile}/${p.scene}: the scene matrix gives it no role, so it cannot be published.`);
    }
    const entry = { ...p.entry, fixtureSet: role } as { sceneId?: string };
    if (p.entry["fixtureSet"] !== role) rerolled.push(`${p.profile}/${p.scene}: ${String(p.entry["fixtureSet"])} → ${role}`);
    profile.fixtures[at] = entry;
  }
  const split = (JSON.parse(readFileSync(SCENES, "utf8")) as { split?: Record<string, unknown> }).split ?? {};
  const declaration = manifest as unknown as { split?: Record<string, unknown> };
  if (declaration.split !== undefined) {
    for (const role of ["calibration", "validation", "holdout", "recorded"]) {
      declaration.split[role] = (split[role] as readonly string[] | undefined) ?? [];
    }
  }
  for (const line of rerolled) process.stdout.write(`  re-rolled ${line}\n`);
  writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);
  process.stdout.write(`\nbed materialised: ${publish.length} cell(s) written with their own run's manifest entry.\n`);
}

try {
  main();
} catch (error) {
  process.stderr.write(`materialize: ${error instanceof Error ? error.message : String(error)}\n`);
  process.exit(1);
}

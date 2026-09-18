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
 *
 * `--set LABEL,...` narrows publication to the scenes the matrix declares in
 * those roles. It exists because publication is otherwise by whole profile
 * directory, so a run that adds new cells to a bed republishes every old one
 * beside them — the sitting's bytes over a frozen bed's, silently, with the
 * gate then reading a bed nobody meant to re-capture. `--set probe` is the form
 * W25's sitting uses: capture everything the profile declares, publish only the
 * cells the amendment added (W25 Decision Log 3 (e)). The default is every
 * role, which is what every bed before this was built under.
 *
 * `--frequency-settle` is the freezing mode Decision Log 21 adopted, and it is
 * deliberately a separate flag rather than a fallback. Under it a cell that holds
 * more than one settled state is published at its **majority** state and marked
 * `frequencySettled` in the manifest, with the observed frequencies beside it, so
 * a reader can see that the cell was decided by counting rather than by agreement.
 * A tie is still refused: frequency cannot settle what has no majority. The bed
 * also gains a provenance block naming the run count and the confidence that
 * count buys, because "deterministic" is only ever a claim about how hard anyone
 * looked.
 */
import { copyFileSync, existsSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { decodePng } from "../src/image";
import { FIXTURE_SETS } from "../src/profile";
import {
  differenceSummary,
  resolveCell,
  type CaptureVariant,
  type CellResolution,
} from "../src/plurality";
import { parseAttestRead, runProvenanceProblems, type RunProvenance } from "../src/run-provenance";

const PACKAGE_ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..");
const REPO_ROOT = resolve(PACKAGE_ROOT, "..", "..");
// The probe-bed env overrides the whole pipeline honours (claims §5.30).
const FIXTURES =
  process.env["VITREA_FIXTURES"] ?? resolve(REPO_ROOT, "apps", "reference-apple", "fixtures");
const SCENES =
  process.env["VITREA_SCENES"] ?? resolve(REPO_ROOT, "apps", "reference-apple", "scenes.json");

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
  for (const role of ["calibration", "validation", "holdout", "recorded", "probe"]) {
    for (const id of spec.split?.[role] ?? []) roles.set(id, role);
  }
  return roles;
}

interface RunSnapshot {
  readonly label: string;
  readonly dir: string;
  /** `profileKey/sceneId` → the manifest entry that run recorded for it. */
  readonly entries: Map<string, Record<string, unknown>>;
  /** `background@Nx` → the path the run recorded for the raster it composited. */
  readonly backgrounds: Record<string, string>;
  /**
   * What the run says about the machine it was taken on, read out of its own
   * manifest and out of the `attest.read` the run script wrote beside it. Judged
   * against the profile keys the run filed under by `src/run-provenance.ts`.
   */
  readonly provenance: RunProvenance;
}

function loadRun(label: string, dir: string): RunSnapshot {
  const manifestPath = resolve(dir, "manifest.json");
  if (!existsSync(manifestPath)) {
    throw new Error(`run ${label}: no manifest.json under ${dir} — snapshot the whole run, not just its PNGs.`);
  }
  const manifest = JSON.parse(readFileSync(manifestPath, "utf8")) as {
    profiles?: { profileKey?: string; fixtures?: { sceneId?: string }[] }[];
    backgrounds?: Record<string, string>;
    hardware?: { osVersion?: string; osBuild?: string };
  };
  const entries = new Map<string, Record<string, unknown>>();
  for (const profile of manifest.profiles ?? []) {
    for (const fixture of profile.fixtures ?? []) {
      entries.set(`${profile.profileKey}/${fixture.sceneId}`, fixture as Record<string, unknown>);
    }
  }
  // The attestation is read if it is there and its absence is carried forward as
  // an absence rather than as an empty record: whether a run needed one depends
  // on the axes its keys claim, and that is the rule's judgement, not this
  // loader's (`run-provenance.ts`).
  const attestPath = resolve(dir, "attest.read");
  const attested = existsSync(attestPath)
    ? parseAttestRead(readFileSync(attestPath, "utf8"))
    : null;
  return {
    label,
    dir,
    entries,
    backgrounds: manifest.backgrounds ?? {},
    provenance: {
      label,
      hardware: manifest.hardware ?? {},
      attested,
      profileKeys: (manifest.profiles ?? [])
        .map((profile) => profile.profileKey)
        .filter((key): key is string => typeof key === "string"),
    },
  };
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
  sets: string[];
  apply: boolean;
  frequencySettle: boolean;
  omit: { cell: string; reason: string }[];
} {
  const runs: { label: string; dir: string }[] = [];
  const profiles: string[] = [];
  const sets: string[] = [];
  const omit: { cell: string; reason: string }[] = [];
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
    } else if (argv[i] === "--set") {
      sets.push(...(argv[i + 1] ?? "").split(",").map((s) => s.trim()).filter(Boolean));
      i += 1;
    } else if (argv[i] === "--omit") {
      /*
       * A ruling on a cell the runs could not settle: `--omit PROFILE/SCENE=REASON`
       * leaves that cell OUT of the bed and writes the hole, with its reason and
       * the states the runs returned, into the provenance block. It is the only
       * way past a refusal, and it is deliberately loud: the cell is named twice,
       * once here and once in the manifest, so a bed with a hole never reads as a
       * bed that was complete.
       */
      const raw = argv[i + 1] ?? "";
      const at = raw.indexOf("=");
      if (at <= 0 || at === raw.length - 1) {
        throw new Error(`--omit expects PROFILE/SCENE=REASON, got '${raw}'.`);
      }
      omit.push({ cell: raw.slice(0, at), reason: raw.slice(at + 1) });
      i += 1;
    }
  }
  if (runs.length < 2) throw new Error("materialize: give at least two --run LABEL=DIR snapshots.");
  for (const set of sets) {
    if (!(FIXTURE_SETS as readonly string[]).includes(set)) {
      throw new Error(`materialize: --set takes ${FIXTURE_SETS.join("|")}, not '${set}'`);
    }
  }
  return {
    runs,
    profiles,
    sets,
    apply: argv.includes("--apply"),
    frequencySettle: argv.includes("--frequency-settle"),
    omit,
  };
}

/**
 * The chance a state held by a fraction `p` of draws would have been seen at
 * least once in `n` runs.
 *
 * Reported rather than assumed, because §5.23 measured minority states as low as
 * one draw in six and a bed is only "unanimous" to the confidence its run count
 * buys.
 */
const confidenceAt = (n: number, p: number): number => 1 - Math.pow(1 - p, n);

function main(): void {
  const options = parseArgs(process.argv.slice(2));
  const runs = options.runs.map((r) => loadRun(r.label, r.dir));
  /*
   * Before a single PNG is opened: were these runs taken on the machine their
   * profile keys describe, and were they all taken on the same one?
   *
   * First because it is decidable from the manifests and the attestations alone,
   * and because everything after it is a decision BETWEEN the runs — a plurality
   * over seven runs from two operating systems is a majority vote between two
   * materials rather than a majority over one. The harness never made this check:
   * it validates a profile's accessibility mode and its scale against the machine
   * and reads the OS version only to record it, so nothing there would stop a 27
   * run filing into a 26.5 directory (W29 Grounding; the gate lives in TypeScript
   * because the granted bundle is never rebuilt, contract X4).
   */
  const provenance = runProvenanceProblems(runs.map((run) => run.provenance));
  if (provenance.length > 0) {
    throw new Error(
      `${provenance.length} run(s) disagree with the profile keys they filed under, and ` +
        `nothing was read:\n  - ${provenance.join("\n  - ")}`,
    );
  }
  /*
   * Read up front, because the declaration is now both the publication filter
   * and the role a published entry carries. A cell outside the selected roles
   * is skipped before its bytes are read, so "not published" means not opened.
   */
  const roles = declaredRoles();
  const selected = options.sets.length > 0 ? new Set(options.sets) : undefined;
  const first = runs[0] as RunSnapshot;
  const profiles =
    options.profiles.length > 0
      ? options.profiles
      : readdirSync(first.dir, { withFileTypes: true })
          // A run snapshot carries its rendered backdrops beside the profile
          // directories; they are rasters, not a profile, and must not be
          // counted as one in the provenance block.
          .filter((e) => e.isDirectory() && e.name !== "backgrounds")
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
      if (selected !== undefined && !selected.has(roles.get(scene) ?? "")) continue;
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
      // Under --frequency-settle a state-ambiguous cell is published at its
      // majority rather than refused — but only if it HAS a majority. A tie has
      // no frequency to settle by and stays refused whatever the flag says.
      let settled: CaptureVariant | undefined;
      let settleNote: Record<string, unknown> | undefined;
      if (options.frequencySettle && outcome.kind === "refused" && outcome.stateAmbiguous) {
        const ranked = [...variants].sort((a, b) => b.runs.length - a.runs.length);
        const top = ranked[0] as CaptureVariant;
        const tied = ranked.filter((v) => v.runs.length === top.runs.length).length > 1;
        if (!tied) {
          settled = top;
          settleNote = {
            frequencySettled: true,
            observedStates: ranked.length,
            stateFrequencies: ranked.map((v) => ({
              sha256: v.sha256,
              runs: v.runs.length,
              share: Number((v.runs.length / runs.length).toFixed(4)),
            })),
          };
        }
      }

      const chosen = outcome.kind !== "refused" ? outcome.chosen : settled;
      if (chosen !== undefined) {
        const winner = chosen.runs[0] as string;
        const entry = runs.find((r) => r.label === winner)?.entries.get(cell);
        if (entry === undefined) throw new Error(`${cell}: run ${winner} published bytes with no manifest entry.`);
        publish.push({
          from: resolve(options.runs.find((r) => r.label === winner)?.dir ?? "", profile, name),
          profile,
          scene,
          entry: settleNote === undefined ? entry : { ...entry, ...settleNote },
        });
      }
    }
  }

  if (decisions.length === 0) {
    throw new Error(
      `materialize: --set ${options.sets.join(",")} selected no cell of ${profiles.length} ` +
        `profile(s). A filter that matches nothing publishes nothing, which is indistinguishable ` +
        `from a run that succeeded.`,
    );
  }

  const settledCells = new Set(publish.filter((p) => p.entry["frequencySettled"] === true).map((p) => `${p.profile}/${p.scene}`));
  const refused = decisions.filter(
    (d) => d.outcome.kind === "refused" && !settledCells.has(d.cell),
  );
  const voted = decisions.filter((d) => d.outcome.kind === "voted");
  const ambiguous = refused.filter((d) => d.outcome.kind === "refused" && d.outcome.stateAmbiguous);

  const settledCount = settledCells.size;
  process.stdout.write(
    `${decisions.length} cell(s) over ${profiles.length} profile(s) from ${runs.length} run(s): ` +
      `${decisions.length - voted.length - refused.length - settledCount} unanimous, ` +
      `${voted.length} voted, ${settledCount} frequency-settled, ` +
      `${refused.length} refused (${ambiguous.length} state-ambiguous)\n`,
  );
  for (const cell of [...settledCells].sort()) {
    const entry = publish.find((p) => `${p.profile}/${p.scene}` === cell)?.entry;
    const freqs = (entry?.["stateFrequencies"] ?? []) as { sha256: string; runs: number; share: number }[];
    process.stdout.write(
      `  settled  ${cell} -> ${freqs.map((f) => `${f.sha256.slice(0, 8)}×${f.runs}`).join(" / ")} ` +
        `(majority share ${(freqs[0]?.share ?? 0).toFixed(2)})\n`,
    );
  }
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

  // A refused cell the caller has ruled on by name is omitted, and the omission
  // travels with the bed (below); one the caller has not ruled on still stops
  // everything, because a hole the manifest does not mention is a lie.
  const omissions = refused
    .map((d) => ({ decision: d, ruling: options.omit.find((o) => o.cell === d.cell) }))
    .filter((o) => o.ruling !== undefined)
    .map((o) => ({
      cell: o.decision.cell,
      reason: (o.ruling as { reason: string }).reason,
      observedStates: o.decision.outcome.kind === "refused" ? o.decision.outcome.reason : "",
    }));
  const unruled = refused.filter((d) => !omissions.some((o) => o.cell === d.cell));
  for (const o of omissions) process.stdout.write(`  OMITTED  ${o.cell}\n    ruling: ${o.reason}\n`);
  const unknownOmit = options.omit.filter((o) => !decisions.some((d) => d.cell === o.cell));
  if (unknownOmit.length > 0) {
    throw new Error(`--omit names a cell the runs do not carry: ${unknownOmit.map((o) => o.cell).join(", ")}`);
  }
  if (unruled.length > 0) {
    process.stderr.write(
      `\nmaterialize: nothing written. ${unruled.length} cell(s) cannot be published without a ruling, ` +
        `and a bed materialised around them would be a bed with a hole the manifest does not mention.\n`,
    );
    process.exit(1);
  }
  if (!options.apply) {
    process.stdout.write("\nevery cell resolves. Re-run with --apply to write the bed.\n");
    return;
  }

  const manifestPath = resolve(FIXTURES, "manifest.json");
  const manifest = JSON.parse(readFileSync(manifestPath, "utf8")) as {
    profiles?: { profileKey?: string; fixtures?: { sceneId?: string }[] }[];
    backgrounds?: Record<string, string>;
  };
  const rerolled: string[] = [];
  /*
   * The backdrop index, carried forward with the cells.
   *
   * A fixture is a component over a raster, and the manifest's `backgrounds` map
   * is the only place the bundle says which raster. Publishing cells over a
   * background the bundle has never seen therefore leaves fixtures whose backdrop
   * nothing can name — and the calibration page refuses such a scene outright, so
   * the bed publishes and then cannot be read. That is how W27c's `mid-chroma-solid`
   * was found missing (claims §5.139).
   *
   * Three things have to agree, and the tool establishes all three across every
   * run before it writes anything. The raster a run declares must be in the run,
   * because a cell whose backdrop was never snapshotted cannot be filed under one.
   * The PATH must agree with the index where the index already has the id: the
   * fixtures already filed under it were drawn over the raster the index names, so
   * re-pointing the id at a different file would misattribute them, and a
   * disagreement is a stop rather than a repair. And the BYTES must agree — the
   * copy in the bundle, at the path the index gives, against every run's copy.
   *
   * Validating everything first is what makes the failure clean. Interleaving the
   * checks with the copies would let a later id's stop leave earlier rasters in the
   * fixture root that no index entry names, which is the half-published bed this
   * tool's whole staging discipline exists to prevent.
   */
  interface BackgroundPlan {
    /** Where the bundle files this raster: the index's path if it has one. */
    readonly path: string;
    readonly from: string;
    readonly sha256: string;
    readonly declaredBy: string;
  }
  const plan = new Map<string, BackgroundPlan>();
  for (const run of runs) {
    for (const [id, path] of Object.entries(run.backgrounds)) {
      const fromRun = resolve(run.dir, path);
      if (!existsSync(fromRun)) {
        throw new Error(
          `background ${id}: run ${run.label} records it at ${path} and did not snapshot it. ` +
            `Snapshot the whole run, its rasters included — the cells beside it have no backdrop.`,
        );
      }
      const digest = sha(readFileSync(fromRun));
      const indexed = manifest.backgrounds?.[id];
      if (indexed !== undefined && indexed !== path) {
        throw new Error(
          `background ${id}: the bundle indexes it at ${indexed} and run ${run.label} composited ` +
            `over ${path}. The fixtures already filed under this id were drawn over the indexed ` +
            `raster, so re-pointing the id would file them under one they were never drawn on.`,
        );
      }
      const seen = plan.get(id);
      if (seen !== undefined && seen.path !== path) {
        throw new Error(
          `background ${id}: run ${seen.declaredBy} composited over ${seen.path} and run ` +
            `${run.label} over ${path}. The runs are not comparable and their cells cannot ` +
            `share one index entry.`,
        );
      }
      if (seen !== undefined && seen.sha256 !== digest) {
        throw new Error(
          `background ${id}: runs ${seen.declaredBy} and ${run.label} composited over different ` +
            `bytes at the same path. The runs are not comparable.`,
        );
      }
      // The bytes compared are the ones at the INDEXED path, which is what the
      // fixtures already in the bundle were drawn over.
      const inBundle = resolve(FIXTURES, indexed ?? path);
      if (existsSync(inBundle) && sha(readFileSync(inBundle)) !== digest) {
        throw new Error(
          `background ${id}: the bundle's raster at ${indexed ?? path} is not the one run ` +
            `${run.label} composited over. Publishing the cells beside it would file them under ` +
            `a backdrop they were not drawn on.`,
        );
      }
      plan.set(id, { path: indexed ?? path, from: fromRun, sha256: digest, declaredBy: run.label });
    }
  }
  const backgroundsAdded: string[] = [];
  for (const [id, raster] of [...plan].sort(([a], [b]) => a.localeCompare(b))) {
    const inBundle = resolve(FIXTURES, raster.path);
    if (!existsSync(inBundle)) copyFileSync(raster.from, inBundle);
    if (manifest.backgrounds?.[id] === undefined) {
      (manifest.backgrounds ??= {})[id] = raster.path;
      backgroundsAdded.push(id);
    }
  }
  for (const p of publish) {
    copyFileSync(p.from, resolve(FIXTURES, p.profile, `${p.scene}.png`));
    const profile = manifest.profiles?.find((m) => m.profileKey === p.profile);
    if (profile === undefined) continue;
    if (profile.fixtures === undefined) continue;
    const at = profile.fixtures.findIndex((f) => f.sceneId === p.scene);
    const role = roles.get(p.scene);
    if (role === undefined) {
      throw new Error(`${p.profile}/${p.scene}: the scene matrix gives it no role, so it cannot be published.`);
    }
    const entry = { ...p.entry, fixtureSet: role } as { sceneId?: string };
    if (p.entry["fixtureSet"] !== role) rerolled.push(`${p.profile}/${p.scene}: ${String(p.entry["fixtureSet"])} → ${role}`);
    // Appended when the scene is new to this bed. Replacing only what already
    // existed would copy a new cell's PNG in and leave the manifest silent about
    // it — a fixture on disk that the record does not describe, which is the one
    // thing the manifest exists to make impossible.
    if (at < 0) profile.fixtures.push(entry);
    else profile.fixtures[at] = entry;
    profile.fixtures.sort((a, b) => (a.sceneId ?? "").localeCompare(b.sceneId ?? ""));
  }
  // The bed's own provenance. "Unanimous" is a claim about how hard anyone
  // looked, so the run count and what it buys travel with the bytes.
  const settledEntries = publish.filter((p) => p.entry["frequencySettled"] === true);
  // Accumulated, not replaced: the bed is materialised one phase at a time, so a
  // provenance block that overwrote itself would leave the finished bed claiming
  // to have been built from whichever phase happened to run last.
  const provenanceHost = manifest as unknown as { bedProvenance?: unknown[] };
  const priorProvenance = Array.isArray(provenanceHost.bedProvenance) ? provenanceHost.bedProvenance : [];
  const publishedCells = publish.map((p) => `${p.profile}/${p.scene}`).sort();
  const thisPhase = {
    profiles: profiles.slice().sort(),
    runs: runs.length,
    runLabels: runs.map((r) => r.label),
    cellsPublished: publish.length,
    /*
     * What this phase published, as a digest: the sorted `profile/scene` list, one
     * per line, hashed. The list itself is not carried because it is 156 names for
     * a single phase of W27c's bed and the manifest is already the largest file in
     * the bundle, while the only question the block has to answer — is that prior
     * block THIS phase — a digest answers exactly.
     */
    cellsSha256: sha(new TextEncoder().encode(publishedCells.join("\n"))),
    unanimousOrVoted: publish.length - settledEntries.length,
    frequencySettled: settledEntries.length,
    frequencySettledCells: settledEntries.map((p) => `${p.profile}/${p.scene}`).sort(),
    // The holes, each with the ruling that left it: a cell the runs returned in
    // states no majority could settle and the caller declined to publish.
    omitted: omissions,
    confidenceBought: {
      note:
        "probability a state held by fraction p of draws would have been seen at least once " +
        `in ${runs.length} runs`,
      atP0_50: Number(confidenceAt(runs.length, 0.5).toFixed(4)),
      atP0_33: Number(confidenceAt(runs.length, 0.33).toFixed(4)),
      atP0_25: Number(confidenceAt(runs.length, 0.25).toFixed(4)),
      atP0_167: Number(confidenceAt(runs.length, 0.167).toFixed(4)),
      atP0_10: Number(confidenceAt(runs.length, 0.1).toFixed(4)),
    },
  };
  /*
   * A phase is identified by its profiles, its run labels, how many cells it
   * published AND which cells those were — not by its profiles alone.
   *
   * Keying on the profiles was right while each phase was the only publication
   * its profiles had ever had, and it made re-running the same command
   * idempotent. It is wrong as soon as a second phase publishes DIFFERENT cells
   * into profiles an earlier phase already filled: W27c's 26.5 checking bed adds
   * 62 probe cells to the two 2x standard profiles that the frozen bed built at
   * the seventeen-run freeze bar, and dropping by profile set would have deleted
   * the record of how the 455 cells already in the bundle were taken (claims
   * §5.139). The bed would then have claimed seven runs for bytes that had
   * seventeen.
   *
   * Profiles, labels and count are still not enough. Run labels are generic
   * (`run-1`…`run-7` is what every sitting calls its runs), so two sittings that
   * publish different scenes into the same profiles at the same count collide —
   * and the collision deletes a block whose fixtures are still in the bed, which
   * is the exact failure this key exists to prevent. `cellsSha256` closes it: the
   * identity now names WHICH cells, so only a phase that published the same ones
   * replaces the earlier record of them.
   */
  const phaseKey = (p: unknown): unknown[] => {
    const block = p as {
      profiles?: unknown;
      runLabels?: unknown;
      cellsPublished?: unknown;
      cellsSha256?: unknown;
    };
    return [block.profiles, block.runLabels, block.cellsPublished, block.cellsSha256 ?? null];
  };
  const phaseIdentity = (p: unknown): string => JSON.stringify(phaseKey(p));
  /*
   * The migration, and the one place the weaker key is still used.
   *
   * A block written before `cellsSha256` existed cannot be matched on it. Keeping
   * every such block unconditionally would leave the bundle carrying two records
   * of the same publication, differing only in that one names its cells — a bed
   * that looks like it was published twice. So a prior block WITHOUT the digest
   * is superseded when the other three parts agree, which is the identity that
   * wrote it, and one WITH the digest is matched on all four.
   *
   * What that costs is bounded and worth naming: on a bed whose blocks predate
   * the digest, two genuinely different phases with the same profiles, labels and
   * count would still collide once. Nothing can distinguish them — the older block
   * does not say what it published — and after this run every block does.
   */
  const legacyIdentity = (p: unknown): string => JSON.stringify(phaseKey(p).slice(0, 3));
  const superseded = (p: unknown): boolean =>
    (p as { cellsSha256?: unknown }).cellsSha256 === undefined &&
    legacyIdentity(p) === legacyIdentity(thisPhase);
  const supersededCount = priorProvenance.filter(superseded).length;
  if (supersededCount > 0) {
    process.stdout.write(
      `  provenance: ${supersededCount} earlier block(s) for these profiles, run labels and cell ` +
        `count predate cellsSha256 and are superseded by this phase's, which names its cells.\n`,
    );
  }
  provenanceHost.bedProvenance = [
    ...priorProvenance.filter((p) => phaseIdentity(p) !== phaseIdentity(thisPhase) && !superseded(p)),
    thisPhase,
  ];
  const split = (JSON.parse(readFileSync(SCENES, "utf8")) as { split?: Record<string, unknown> }).split ?? {};
  const declaration = manifest as unknown as { split?: Record<string, unknown> };
  if (declaration.split !== undefined) {
    for (const role of ["calibration", "validation", "holdout", "recorded", "probe"]) {
      declaration.split[role] = (split[role] as readonly string[] | undefined) ?? [];
    }
  }
  for (const line of rerolled) process.stdout.write(`  re-rolled ${line}\n`);
  for (const id of backgroundsAdded.sort()) process.stdout.write(`  background ${id} added to the index\n`);
  writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);
  process.stdout.write(
    `\nbed materialised: ${publish.length} cell(s) written with their own run's manifest entry` +
      (settledEntries.length > 0 ? `, ${settledEntries.length} of them frequency-settled` : "") +
      `. Provenance: ${runs.length} runs, ` +
      `${(confidenceAt(runs.length, 0.167) * 100).toFixed(1)}% confidence at a one-in-six minority.\n`,
  );
}

try {
  main();
} catch (error) {
  process.stderr.write(`materialize: ${error instanceof Error ? error.message : String(error)}\n`);
  process.exit(1);
}

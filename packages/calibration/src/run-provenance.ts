/**
 * Whether a raw capture run may be published under the profile keys it claims.
 *
 * `plurality.ts` decides which of several runs' bytes are published; this
 * decides whether those runs were taken on the machine their keys describe. The
 * two questions are separate and this one comes first: a plurality over seven
 * runs from two operating systems is a majority vote between two materials.
 *
 * The check exists because nothing in the capture path ever made it. The Swift
 * harness validates a profile's accessibility mode and its scale against the
 * machine and refuses to file a mislabelled fixture on either axis, but it reads
 * the OS version only to *record* it (`Manifest.swift`) and has no `#available`
 * anywhere — so nothing would have stopped a macOS 27 run writing into a 26.5
 * directory (W29 Grounding). W29's charter puts that gate here rather than in
 * Swift deliberately: the granted reference bundle holds the wave's one
 * irreplaceable Screen Recording grant and is never rebuilt (contract X4), so a
 * refusal it does not already implement has to live above it, in TypeScript.
 *
 * What is compared is always a *read against a claim*. The claim is the profile
 * key, which names every axis that can move a pixel (contract X6). The read is
 * either the manifest the capture itself wrote — `hardware.osVersion` and
 * `hardware.osBuild`, both taken from the running system — or the run script's
 * own attestation file, which records the axes the harness does not: macOS 27's
 * appearance slider, Show Borders, the display's mode and the capturing
 * binary's linked SDK. Nothing here reads the environment, and nothing here is
 * a transcription: an axis whose value cannot be read is a refusal rather than
 * an assumption (contract X2).
 *
 * Pure, and over strings the caller has already read, for the reason the whole
 * package is: the reading belongs to the CLI and the rule belongs here, where it
 * can be tested without a capture machine.
 */

import { parseProfileKey } from "./profile";

/**
 * The `hardware` block of a run's manifest, as much of it as this rule reads.
 *
 * Optional because the rule's job is to notice an absence. A manifest with no
 * `osVersion` is not a manifest whose OS happens to match — it is a snapshot
 * that cannot say, and a bed published from it would carry no record of the
 * system that drew it.
 */
export interface RunHardware {
  readonly osVersion?: string | undefined;
  readonly osBuild?: string | undefined;
}

/** One raw run, as `materialize` has read it off disk. */
export interface RunProvenance {
  /** The `--run LABEL=DIR` label, so a problem names the run a reader can find. */
  readonly label: string;
  readonly hardware: RunHardware;
  /**
   * The run script's attestation read, parsed from the `attest.read` beside the
   * run's manifest, or `null` when the run carries none.
   *
   * Null is not a failure by itself: the 26.5 bed was captured before the file
   * existed, and its keys state no axis that only the file can attest. It
   * becomes a failure the moment a key claims one — see `runProvenanceProblems`.
   */
  readonly attested: Readonly<Record<string, string>> | null;
  /** Every profile key this run filed under. */
  readonly profileKeys: readonly string[];
}

/**
 * The `key=value` lines of an `attest.read` file.
 *
 * Deliberately forgiving about what it does not recognise and strict about
 * nothing: the file is a record first, and a field this rule has no use for
 * today is still a field a later reading wants. The first `=` splits, so a value
 * containing one — a note, a path — survives.
 */
export function parseAttestRead(text: string): Record<string, string> {
  const fields: Record<string, string> = {};
  for (const line of text.split("\n")) {
    const at = line.indexOf("=");
    if (at <= 0) continue;
    fields[line.slice(0, at)] = line.slice(at + 1);
  }
  return fields;
}

/**
 * The `major.minor` series of an OS version string, or null.
 *
 * Parsed rather than prefix-matched, because the two sources spell the same
 * system differently: `hardware.osVersion` is
 * `ProcessInfo.operatingSystemVersionString` and reads `Version 27.0 (Build
 * 26A428)`, while a profile key's token is the bare `27.0`. A prefix match
 * between those two is either always false or accidentally true.
 */
export function osSeriesOf(osVersion: string): string | null {
  const found = /(\d+)\.(\d+)/.exec(osVersion);
  return found === null ? null : `${found[1] as string}.${found[2] as string}`;
}

/**
 * Every disagreement between what these runs claim and what they recorded.
 *
 * Returned as a list rather than thrown one at a time, so a caller reports all
 * of them at once: a sitting is hours of machine time and finding its second
 * problem after fixing its first costs another sitting.
 *
 * Six rules, in the order a reader should take them.
 */
export function runProvenanceProblems(runs: readonly RunProvenance[]): string[] {
  const problems: string[] = [];

  for (const run of runs) {
    const recorded = run.hardware.osVersion;
    const series = recorded === undefined ? null : osSeriesOf(recorded);
    for (const key of run.profileKeys) {
      const claimed = parseProfileKey(key);
      if (claimed === null) {
        problems.push(
          `run ${run.label}: '${key}' is not a profile key this grammar can parse, so nothing ` +
            `can be checked against it.`,
        );
        continue;
      }
      // 1. The OS the capture itself recorded, against the OS the key claims.
      if (series === null) {
        problems.push(
          `run ${run.label}: the manifest records osVersion ${JSON.stringify(recorded)}, which ` +
            `states no major.minor version, and ${key} claims ${claimed.osVersion}.`,
        );
      } else if (series !== claimed.osVersion) {
        problems.push(
          `run ${run.label}: the manifest records macOS ${series} (${String(recorded)}) and ` +
            `${key} claims ${claimed.osVersion}. Nothing in the harness stops a run of one OS ` +
            `filing into the other's directory, which is why this refuses here.`,
        );
      }
      // 2. The two accessibility toggles, against the mode the key names.
      //    `a11yMode` in a manifest is `SystemAccessibility.current`, which
      //    answers "is contrast on" and cannot distinguish the coupled state
      //    from contrast alone — the distinction macOS 27 created by decoupling
      //    the toggles, and the one W29 Decision Log 4 (b) captures a bed to
      //    resolve. Only the run script's attestation reads both booleans, so
      //    this is where the two increased-contrast keys are held apart. A key
      //    claiming the coupled state needs an attestation and refuses without
      //    one; a key claiming contrast alone is checked only where a run
      //    attested, which is the proportionality the slider rule uses and the
      //    reason the 26.5 bed — captured before the file existed, in the only
      //    state its OS allowed — still wears the plain token.
      const contrastMode =
        claimed.a11yMode === "increased-contrast"
        || claimed.a11yMode === "increased-contrast-coupled";
      if (contrastMode) {
        const wantCoupled = claimed.a11yMode === "increased-contrast-coupled";
        const ic = run.attested?.["increaseContrast"];
        const rt = run.attested?.["reduceTransparency"];
        if (ic === undefined || rt === undefined) {
          if (wantCoupled) {
            problems.push(
              `run ${run.label}: ${key} claims Increase Contrast and Reduce Transparency both ` +
                `on, and the run attested increaseContrast=${JSON.stringify(ic ?? null)} ` +
                `reduceTransparency=${JSON.stringify(rt ?? null)}. No manifest field carries ` +
                `the two toggles separately, so a run that cannot say both stood on cannot be ` +
                `published under a key that claims they did (X2).`,
            );
          }
        } else if (ic === "0") {
          problems.push(
            `run ${run.label}: ${key} claims increased contrast and the run attested ` +
              `increaseContrast=0.`,
          );
        } else if (wantCoupled && rt === "0") {
          problems.push(
            `run ${run.label}: ${key} claims the COUPLED state — contrast with reduce ` +
              `transparency — and the run attested reduceTransparency=0. That run is the ` +
              `decoupled bed and belongs under the plain increased-contrast key.`,
          );
        } else if (!wantCoupled && rt !== "0") {
          problems.push(
            `run ${run.label}: ${key} names increased contrast alone and the run attested ` +
              `reduceTransparency=${rt}. macOS 27 decouples the two toggles, so a run with ` +
              `both on is the coupled state and belongs under the ` +
              `increased-contrast-coupled key; filing it here is the confound claims §5.151 §9 ` +
              `records.`,
          );
        }
      }
      // 3. The appearance slider, which only the run script can attest. A key
      //    that names the axis and a run that cannot say where it stood are not
      //    publishable together: the position moves every cell of every arm
      //    beyond its own run-to-run spread (claims §5.149 §4), so an unattested
      //    one is an unmeasured axis inside a bed that claims to name it.
      if (claimed.glass === undefined) continue;
      if (run.attested === null) {
        problems.push(
          `run ${run.label}: ${key} states appearance-slider position ${claimed.glass} and the ` +
            `run carries no attest.read. The slider is not in any manifest field, so a run with ` +
            `no attestation cannot say where it stood.`,
        );
        continue;
      }
      const read = run.attested["glassTintAmount"];
      const value = read === undefined ? Number.NaN : Number(read);
      if (!Number.isFinite(value)) {
        problems.push(
          `run ${run.label}: ${key} states appearance-slider position ${claimed.glass} and the ` +
            `attestation reads ${JSON.stringify(read ?? null)}. A value nothing could read is ` +
            `not an attestation (X2).`,
        );
      } else if (value !== claimed.glass) {
        problems.push(
          `run ${run.label}: ${key} states appearance-slider position ${claimed.glass} and the ` +
            `run attested ${value}. Every 27 cell moves with this axis, so the key and the ` +
            `machine must agree on it exactly.`,
        );
      }
      // 4. The attestation's own OS reading, against the same key. The manifest
      //    and the attestation are two independent reads of one machine — the
      //    harness's, through Foundation, and the run script's, through
      //    `sw_vers` — and a bed is stronger for having both agree than for
      //    having either alone.
      const attestedOs = run.attested["osProductVersion"];
      const attestedSeries = attestedOs === undefined ? null : osSeriesOf(attestedOs);
      if (attestedSeries !== claimed.osVersion) {
        problems.push(
          `run ${run.label}: ${key} claims macOS ${claimed.osVersion} and the attestation read ` +
            `${JSON.stringify(attestedOs ?? null)}.`,
        );
      }
      const attestedBuild = run.attested["osBuild"];
      if (attestedBuild === undefined || attestedBuild !== run.hardware.osBuild) {
        problems.push(
          `run ${run.label}: the manifest records build ` +
            `${JSON.stringify(run.hardware.osBuild ?? null)} and the attestation read ` +
            `${JSON.stringify(attestedBuild ?? null)}. Two reads of one machine that disagree ` +
            `leave the bed unable to say which build drew its pixels.`,
        );
      }
    }
  }

  // 5. The runs against each other. Every rule above is per run, so seven runs
  //    could each agree with their own keys and still have been taken on two
  //    builds of the same OS series — a point update is a different material and
  //    a Decision Log entry, and a plurality across one would be a vote between
  //    two of them.
  const builds = new Map<string, string[]>();
  for (const run of runs) {
    const build = run.hardware.osBuild ?? "(unrecorded)";
    const seen = builds.get(build);
    if (seen === undefined) builds.set(build, [run.label]);
    else seen.push(run.label);
  }
  if (builds.size > 1) {
    problems.push(
      `the runs were taken on ${builds.size} different OS builds — ` +
        [...builds]
          .map(([build, labels]) => `${build}: ${labels.join(", ")}`)
          .join("; ") +
        `. A plurality across them is a vote between two materials, not a majority over one.`,
    );
  }

  // 6. And against each other on the declaration they read. `sceneSpecVersion`
  //    in the manifest would catch a version bump but not an edit inside one, and
  //    the declaration decides which cells exist and where their geometry puts
  //    them — so two runs of one pass taken across an edit are two beds. Only
  //    runs that carry an attestation are compared, which is the same
  //    proportionality the slider rule uses: a bed captured before the field
  //    existed is not asked for it.
  const specs = new Map<string, string[]>();
  for (const run of runs) {
    const digest = run.attested?.["passSpecSha256"];
    if (digest === undefined) continue;
    const seen = specs.get(digest);
    if (seen === undefined) specs.set(digest, [run.label]);
    else seen.push(run.label);
  }
  if (specs.size > 1) {
    problems.push(
      `the runs read ${specs.size} different scene declarations — ` +
        [...specs]
          .map(([digest, labels]) => `${digest.slice(0, 12)}: ${labels.join(", ")}`)
          .join("; ") +
        `. The declaration decides which cells exist and where their geometry puts them, so ` +
        `runs taken across an edit to it are two beds rather than seven runs of one.`,
    );
  }

  return problems;
}

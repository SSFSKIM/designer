/**
 * Publishing a profile the bed has never held before.
 *
 * Until W29 this path could not run: every publication appended cells to one of
 * the six profiles the 2026-08-30 bundle already declared, so the lookup in
 * `cli/materialize.ts` always hit. The macOS 27 bed is the first publication of
 * six NEW keys, and on that path the old code copied every PNG into the bundle
 * and then skipped the manifest without a word — 624 fixtures on disk that the
 * record does not describe, which is the one thing the manifest exists to make
 * impossible, and which nothing downstream would have noticed because `compare`
 * reads the manifest rather than the directory.
 *
 * Driven as a subprocess against a synthetic bundle in a temporary directory,
 * the way `capture-integrity.test.ts` drives its own driver: the behaviour under
 * test is the tool's, including its refusals and its exit status, and a unit call
 * into an un-exported `main()` would test neither.
 */
import { spawnSync } from "node:child_process";
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { resolve } from "node:path";

import { afterAll, describe, expect, it } from "vitest";

import { encodePng, solidLuminance } from "./synthesise";

const PACKAGE_ROOT = resolve(import.meta.dirname, "..");
const REPO_ROOT = resolve(PACKAGE_ROOT, "..", "..");
const SCENES = resolve(REPO_ROOT, "apps", "reference-apple", "scenes.json");

/** A scene the canonical matrix declares, so `materialize` can give it a role. */
const SCENE = "photo__rrect-md__rest";
const KEY = "apple-macos-27.0-2x-light-standard-glass0.5";

const roots: string[] = [];
afterAll(() => {
  for (const root of roots) rmSync(root, { recursive: true, force: true });
});

/**
 * One small grey cell, identical in every run.
 *
 * Identical on purpose: `resolveCell` reaches the image comparator only when the
 * runs returned DIFFERENT bytes, and nothing here is about the plurality — the
 * behaviour under test is what happens to the manifest when the profile is new.
 */
const png = (): Uint8Array => encodePng(solidLuminance(4, 4, 0.5));

interface RunOptions {
  readonly hardware?: Record<string, unknown>;
  readonly attest?: string | null;
  readonly display?: Record<string, unknown>;
}

function stage(runs: readonly (readonly [string, RunOptions])[]): {
  fixtures: string;
  dirs: { label: string; dir: string }[];
} {
  const root = mkdtempSync(resolve(tmpdir(), "vitrea-materialize-"));
  roots.push(root);
  const fixtures = resolve(root, "fixtures");
  mkdirSync(resolve(fixtures, "backgrounds"), { recursive: true });
  // A bundle that holds no profile at all — the shape a bed has before its first
  // publication, and the shape the 26.5 bundle had for the six 27 keys.
  writeFileSync(
    resolve(fixtures, "manifest.json"),
    `${JSON.stringify(
      {
        schemaVersion: 3,
        sceneSpecVersion: 6,
        generatedAt: "2026-09-19T00:00:00Z",
        hardware: { model: "Mac14,12", osVersion: "Version 26.5.2 (Build 25F84)", osBuild: "25F84" },
        backgrounds: {},
        caveats: [],
        split: { calibration: [], validation: [], holdout: [], recorded: [], probe: [] },
        profiles: [],
      },
      null,
      2,
    )}\n`,
  );
  const dirs = runs.map(([label, options]) => {
    const dir = resolve(root, `run-${label}`);
    mkdirSync(resolve(dir, KEY), { recursive: true });
    writeFileSync(resolve(dir, KEY, `${SCENE}.png`), png());
    writeFileSync(
      resolve(dir, "manifest.json"),
      `${JSON.stringify({
        schemaVersion: 3,
        sceneSpecVersion: 6,
        hardware: options.hardware ?? {
          model: "Mac14,12",
          cpu: "Apple M2 Pro",
          osVersion: "Version 27.0 (Build 26A428)",
          osBuild: "26A428",
        },
        backgrounds: {},
        profiles: [
          {
            profileKey: KEY,
            colorScheme: "light",
            a11yMode: "standard",
            display: options.display ?? {
              requestedScale: 2,
              actualBackingScale: 2,
              pixelSize: [640, 400],
              colorSpace: "kCGColorSpaceSRGB",
            },
            fixtures: [
              {
                sceneId: SCENE,
                file: `${KEY}/${SCENE}.png`,
                fixtureSet: "probe",
                captureMethod: "screencapturekit",
                materialRendered: true,
                width: 1,
                height: 1,
                deterministic: true,
                repeatNoise: 0,
                presentedActive: true,
                capturedAt: "2026-09-19T00:00:00Z",
                hidIdleSeconds: 300,
              },
            ],
          },
        ],
      })}\n`,
    );
    const attest =
      options.attest === undefined
        ? [
            "phase=open",
            "pass=standard-active-2x",
            `readAt=2026-09-19T00:0${label}:00Z`,
            "osProductVersion=27.0",
            "osBuild=26A428",
            "glassTintAmount=0.5",
            "showBorders=0",
            "displayplacerMode=68",
          ].join("\n")
        : options.attest;
    if (attest !== null) writeFileSync(resolve(dir, "attest.read"), `${attest}\n`);
    return { label, dir };
  });
  return { fixtures, dirs };
}

function materialize(
  fixtures: string,
  dirs: readonly { label: string; dir: string }[],
  extra: readonly string[] = [],
): { status: number | null; output: string; manifest: Record<string, unknown> } {
  const args = ["tsx", resolve(PACKAGE_ROOT, "cli", "materialize.ts")];
  for (const run of dirs) args.push("--run", `${run.label}=${run.dir}`);
  const result = spawnSync("npx", [...args, ...extra], {
    cwd: PACKAGE_ROOT,
    encoding: "utf8",
    env: { ...process.env, VITREA_FIXTURES: fixtures, VITREA_SCENES: SCENES },
    timeout: 120_000,
  });
  return {
    status: result.status,
    output: `${result.stdout ?? ""}${result.stderr ?? ""}`,
    manifest: JSON.parse(readFileSync(resolve(fixtures, "manifest.json"), "utf8")) as Record<
      string,
      unknown
    >,
  };
}

describe("materialising a profile the bed has never held (W29 G1 Part B)", () => {
  it("writes the manifest entry, not just the PNG", () => {
    const { fixtures, dirs } = stage([
      ["A", {}],
      ["B", {}],
    ]);
    const { status, output, manifest } = materialize(fixtures, dirs, ["--apply"]);
    expect(status, output).toBe(0);
    expect(output).toContain(`profile ${KEY} is new to this bed`);
    const profiles = manifest["profiles"] as { profileKey: string; fixtures: unknown[] }[];
    expect(profiles.map((p) => p.profileKey)).toEqual([KEY]);
    // The cell is described, not merely on disk. This is the assertion the old
    // code would have failed while still exiting 0 and copying the file.
    expect(profiles[0]?.fixtures).toHaveLength(1);
  });

  it("takes the profile's header from the runs rather than inventing it", () => {
    // `colorScheme`, `a11yMode` and above all `display` are measurements — the
    // backing scale in `display` is what the harness actually rendered at, and a
    // bed that guessed it would mislabel every fixture under the key with nothing
    // in the bytes to say so.
    const { fixtures, dirs } = stage([
      ["A", {}],
      ["B", {}],
    ]);
    const { manifest } = materialize(fixtures, dirs, ["--apply"]);
    const profile = (manifest["profiles"] as Record<string, unknown>[])[0] as Record<
      string,
      unknown
    >;
    expect(profile["colorScheme"]).toBe("light");
    expect(profile["a11yMode"]).toBe("standard");
    expect((profile["display"] as Record<string, unknown>)["actualBackingScale"]).toBe(2);
  });

  it("refuses when the runs describe the profile differently", () => {
    // A profile captured at two backing scales across the runs of one phase is
    // not one profile, and publishing a plurality over it would pick a header by
    // accident — from whichever run happened to be first.
    const { fixtures, dirs } = stage([
      ["A", {}],
      ["B", { display: { requestedScale: 2, actualBackingScale: 1, pixelSize: [320, 200] } }],
    ]);
    const { status, output } = materialize(fixtures, dirs, ["--apply"]);
    expect(status).not.toBe(0);
    expect(output).toContain("the runs describe this profile differently");
  });

  it("records the capturing machine on the profile and leaves the bundle's own block alone", () => {
    // One top-level `hardware` block cannot describe two beds captured on two
    // operating systems. The 26.5 block is frozen evidence about the bed it
    // describes; the second bed's record is added beside it, per profile.
    const { fixtures, dirs } = stage([
      ["A", {}],
      ["B", {}],
    ]);
    const { manifest } = materialize(fixtures, dirs, ["--apply"]);
    expect((manifest["hardware"] as Record<string, string>)["osBuild"]).toBe("25F84");
    const profile = (manifest["profiles"] as Record<string, unknown>[])[0] as Record<
      string,
      unknown
    >;
    expect((profile["hardware"] as Record<string, string>)["osBuild"]).toBe("26A428");
    const attestation = profile["attestation"] as Record<string, string>;
    expect(attestation["glassTintAmount"]).toBe("0.5");
    expect(attestation["displayplacerMode"]).toBe("68");
    expect(attestation["runs"]).toBe("2");
    // Per-run by construction, so not a property of the bed.
    expect(attestation["readAt"]).toBeUndefined();
    expect(attestation["phase"]).toBeUndefined();
    expect(attestation["pass"]).toBeUndefined();
  });

  it("records only what every run of the profile agreed on", () => {
    // A value that moved between the runs is not a property of the bed. It is
    // dropped rather than taken from the first run, which would record one run's
    // reading as the bed's.
    const { fixtures, dirs } = stage([
      ["A", {}],
      [
        "B",
        {
          attest: [
            "phase=open",
            "pass=standard-active-2x",
            "readAt=2026-09-19T00:05:00Z",
            "osProductVersion=27.0",
            "osBuild=26A428",
            "glassTintAmount=0.5",
            "showBorders=0",
            "displayplacerMode=69",
          ].join("\n"),
        },
      ],
    ]);
    const { manifest } = materialize(fixtures, dirs, ["--apply"]);
    const profile = (manifest["profiles"] as Record<string, unknown>[])[0] as Record<
      string,
      unknown
    >;
    const attestation = profile["attestation"] as Record<string, string>;
    expect(attestation["glassTintAmount"]).toBe("0.5");
    expect(attestation["displayplacerMode"]).toBeUndefined();
  });

  it("refuses when two runs record different machines", () => {
    const { fixtures, dirs } = stage([
      ["A", {}],
      [
        "B",
        {
          hardware: {
            model: "Mac14,12",
            cpu: "Apple M2 Pro",
            osVersion: "Version 27.0 (Build 26A428)",
            osBuild: "26A428",
            extra: "different",
          },
        },
      ],
    ]);
    const { status, output } = materialize(fixtures, dirs, ["--apply"]);
    expect(status).not.toBe(0);
    // `run-provenance` catches the OS-level case first; this is the tighter one,
    // where the OS agrees and the rest of the machine record does not.
    expect(output).toMatch(/records a different machine|different OS builds/);
  });
});

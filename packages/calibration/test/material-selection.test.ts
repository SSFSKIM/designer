/**
 * The calibration page's two declared selection modes (W43 G0 (f); charter
 * `2026-10-01-w43-glass-0-25-generation.md`, Surprises 1, X45), red case by red case.
 *
 * Strict shipped mode selects by (OS, glass) and refuses an unshipped or ambiguous pair.
 * Candidate mode reads a declared document whose four endpoints and CSS mapping are matched
 * by hash, and refuses a partial candidate, a glass token that differs from the declared
 * position, and a candidate that names a shipped document. The browser half of the proof,
 * byte identity between the two modes, is in `results/2026-10-01-w43-g0-declaration/seam/`.
 */

import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { copyFileSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, symlinkSync, writeFileSync }
  from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { describe, expect, it } from "vitest";

import {
  macos26MaterialProfileDocument,
  macos27CssTierMapping,
  macos27MaterialProfileDocument,
  SHIPPED_MATERIAL_PROFILE_DOCUMENTS,
  type GlassMaterialProfileDocument,
} from "@vitreajs/vitrea-web";

import {
  candidateDocumentRefusals,
  candidateMaterialLabel,
  carriesCrossPositionStamp,
  crossPositionClause,
  crossPositionRefusal,
  documentPosition,
  selectShippedDocument,
  type MaterialDocumentLike,
} from "../src/material-selection";
import {
  CANDIDATE_DECLARATION_KIND,
  cssTierMappingSha256,
  readCandidateDocument,
} from "../scripts/candidate-document";
import { withinTree } from "../src/matrix-write-guard";
import { crossPositionVerdict } from "../src/document-position";

const PACKAGE = resolve(import.meta.dirname, "..");
const PROFILES = resolve(PACKAGE, "profiles");
const KEY_05 = "apple-macos-27.0-1x-light-standard-glass0.5";
const KEY_025 = "apple-macos-27.0-1x-light-standard-glass0.25";

/** The shipped 0.5 document's content under the 0.25 keys: the proof's candidate. */
function relabel(document: GlassMaterialProfileDocument, glass: string): MaterialDocumentLike {
  const key = (endpoint: { readonly profileKey?: string }) =>
    endpoint.profileKey?.replace("-glass0.5", `-glass${glass}`);
  return {
    ...document,
    name: `apple-macos-27.0-glass${glass}`,
    glassTintAmount: Number(glass),
    active: {
      light: { ...document.active.light, profileKey: key(document.active.light)! },
      dark: { ...document.active.dark, profileKey: key(document.active.dark)! },
    },
    receded: {
      light: { ...document.receded.light, profileKey: key(document.receded.light)! },
      dark: { ...document.receded.dark, profileKey: key(document.receded.dark)! },
    },
  };
}

describe("strict shipped mode", () => {
  it("selects the macOS 27 document at glass 0.5, by an active or a receded key", () => {
    expect(selectShippedDocument(KEY_05, SHIPPED_MATERIAL_PROFILE_DOCUMENTS))
      .toBe(macos27MaterialProfileDocument);
    expect(selectShippedDocument(`${KEY_05.replace("light", "dark")}-receded`,
      SHIPPED_MATERIAL_PROFILE_DOCUMENTS)).toBe(macos27MaterialProfileDocument);
  });

  it("selects the macOS 26.5 document by a key with no glass token", () => {
    expect(selectShippedDocument("apple-macos-26.5-1x-dark-standard",
      SHIPPED_MATERIAL_PROFILE_DOCUMENTS)).toBe(macos26MaterialProfileDocument);
  });

  it("reads each shipped document's position from its own statements", () => {
    expect(documentPosition(macos27MaterialProfileDocument)).toEqual({ osVersion: "27.0", glass: 0.5 });
    expect(documentPosition(macos26MaterialProfileDocument))
      .toEqual({ osVersion: "26.5", glass: undefined });
  });

  it("red: refuses glass 0.25, the pair the OS token alone would have answered with 0.5", () => {
    expect(() => selectShippedDocument(KEY_025, SHIPPED_MATERIAL_PROFILE_DOCUMENTS))
      .toThrow(/ships no material at that pair/);
  });

  it("red: refuses a macOS 27 key with no glass token, a 26.5 key with one, and an unshipped OS", () => {
    for (const key of [
      "apple-macos-27.0-1x-light-standard",
      "apple-macos-26.5-1x-light-standard-glass0.5",
      "apple-macos-28.0-1x-light-standard-glass0.5",
    ]) {
      expect(() => selectShippedDocument(key, SHIPPED_MATERIAL_PROFILE_DOCUMENTS), key)
        .toThrow(/ships no material at that pair/);
    }
  });

  it("red: refuses a key the grammar does not parse", () => {
    expect(() => selectShippedDocument("apple-macos-27.0-light", SHIPPED_MATERIAL_PROFILE_DOCUMENTS))
      .toThrow(/does not parse/);
  });

  it("red: refuses an ambiguous pair, two shipped documents at one position", () => {
    const twin = { ...macos27MaterialProfileDocument, name: "apple-macos-27.0-glass0.5-twin" };
    expect(() => selectShippedDocument(KEY_05, [macos27MaterialProfileDocument, twin]))
      .toThrow(/2 shipped documents sit there/);
  });

  it("red: refuses a registry holding a document whose statements disagree", () => {
    const torn = { ...macos27MaterialProfileDocument, glassTintAmount: 0.25 };
    expect(() => selectShippedDocument(KEY_05, [torn, macos26MaterialProfileDocument]))
      .toThrow(/no readable position/);
  });

  it("selects by the pair when a second position ships beside the first", () => {
    const at025 = relabel(macos27MaterialProfileDocument, "0.25");
    const registry = [at025, macos27MaterialProfileDocument, macos26MaterialProfileDocument];
    expect(selectShippedDocument(KEY_025, registry)).toBe(at025);
    expect(selectShippedDocument(KEY_05, registry)).toBe(macos27MaterialProfileDocument);
  });
});

describe("candidate mode, the document the page draws", () => {
  const good = relabel(macos27MaterialProfileDocument, "0.25");
  const refusals = (candidate: MaterialDocumentLike) =>
    candidateDocumentRefusals(candidate, SHIPPED_MATERIAL_PROFILE_DOCUMENTS);

  it("admits the 0.5 content under the scratch 0.25 keys", () => {
    expect(refusals(good)).toEqual([]);
  });

  it("red: refuses a partial candidate, one missing piece at a time", () => {
    const { dark: _dark, ...recededLightOnly } = good.receded;
    void _dark;
    const cases: [string, MaterialDocumentLike][] = [
      ["no receded.dark", { ...good, receded: recededLightOnly as MaterialDocumentLike["receded"] }],
      ["no patch", { ...good, active: { ...good.active, dark: { ...good.active.dark, patch: {} } } }],
      ["no digest", { ...good, receded: { ...good.receded,
        light: { profileKey: good.receded.light.profileKey!, patch: good.receded.light.patch! } } }],
      ["no key", { ...good, active: { ...good.active,
        light: { patch: good.active.light.patch!, resolvedMaterialSha256: "be13dae45098fc89" } } }],
      ["no mapping", { ...good, cssTierMapping: {} }],
      ["no position", (({ glassTintAmount: _g, ...rest }) => { void _g; return rest; })(good)],
    ];
    for (const [label, candidate] of cases) {
      expect(refusals(candidate).join("; "), label).toMatch(/^partial: /);
    }
  });

  it("red: refuses keys whose glass token differs from the declared position", () => {
    expect(refusals({ ...good, glassTintAmount: 0.5 }).join("; "))
      .toMatch(/glass token: active\.light key .* names glass 0\.25, the candidate declares 0\.5/);
    const oneOff = { ...good, receded: { ...good.receded,
      dark: { ...good.receded.dark, profileKey: "apple-macos-27.0-1x-dark-standard-glass0.75-receded" } } };
    expect(refusals(oneOff)).toEqual([
      "glass token: receded.dark key 'apple-macos-27.0-1x-dark-standard-glass0.75-receded' names " +
        "glass 0.75, the candidate declares 0.25",
    ]);
  });

  it("red: refuses a key in the wrong slot", () => {
    const swapped = { ...good, active: { light: good.active.dark, dark: good.active.light } };
    expect(refusals(swapped).join("; ")).toMatch(/active\.light key .* is a dark key/);
    const receded = { ...good, receded: { ...good.receded, light: good.active.light } };
    expect(refusals(receded).join("; ")).toMatch(/receded\.light key .* is not a receded key/);
  });

  it("red: refuses a candidate that names a shipped document, by name or by any endpoint key", () => {
    expect(refusals({ ...good, name: macos27MaterialProfileDocument.name }).join("; "))
      .toMatch(/names a shipped document: 'apple-macos-27\.0-glass0\.5'/);
    const shipped = { ...macos27MaterialProfileDocument, name: "scratch", glassTintAmount: 0.5 };
    expect(refusals(shipped).filter((p) => p.startsWith("names a shipped document"))).toHaveLength(4);
  });

  it("stamps the capture path so a document-clause parser cannot read it as shipped", () => {
    const label = candidateMaterialLabel({
      declaration: "x/candidate.json", sha256: "0123456789ab", name: good.name, glassTintAmount: 0.25,
    });
    expect(label).toMatch(/^materialProfile=candidate /);
    expect(label).not.toMatch(/sha256:/);
  });
});

describe("both modes, the position a material is read against", () => {
  const at025 = ["apple-macos-27.0-1x-light-standard-glass0.25", "apple-macos-27.0-2x-dark-standard-glass0.25"];
  const at05 = ["apple-macos-27.0-1x-light-standard-glass0.5", "apple-macos-27.0-2x-dark-standard-glass0.5"];

  it("admits profiles at the material's own position without the flag", () => {
    expect(crossPositionRefusal("candidate", 0.25, at025, false)).toBeUndefined();
    expect(crossPositionRefusal("shipped", 0.5, at05, false)).toBeUndefined();
    expect(crossPositionRefusal("shipped", undefined, ["apple-macos-26.5-1x-light-standard"], false))
      .toBeUndefined();
  });

  it("red: refuses a profile at another position, or none, without --cross-position", () => {
    expect(crossPositionRefusal("candidate", 0.25, [...at025, at05[0]!], false))
      .toMatch(/the candidate is at glass 0\.25 and is read against .*glass0\.5 \(glass 0\.5\)/);
    expect(crossPositionRefusal("candidate", 0.25, ["apple-macos-26.5-1x-light-standard"], false))
      .toMatch(/\(glass none\)/);
    expect(crossPositionRefusal("shipped", 0.5, [at025[0]!], false))
      .toMatch(/the shipped material is at glass 0\.5 and is read against .*glass0\.25 \(glass 0\.25\)/);
    expect(crossPositionRefusal("shipped", undefined, [at05[0]!], false))
      .toMatch(/the shipped material is at glass none/);
  });

  it("admits every profile at another position under --cross-position", () => {
    expect(crossPositionRefusal("candidate", 0.25, at05, true)).toBeUndefined();
    expect(crossPositionRefusal("shipped", 0.5, at025, true)).toBeUndefined();
  });

  it("red: refuses --cross-position over any profile at the material's own position", () => {
    expect(crossPositionRefusal("candidate", 0.25, at025, true)).toMatch(/the stamp would be false/);
    expect(crossPositionRefusal("candidate", 0.25, [...at05, at025[1]!], true))
      .toMatch(/the stamp would be false/);
    expect(crossPositionRefusal("shipped", 0.5, [...at025, at05[0]!], true)).toMatch(/the stamp would be false/);
  });

  it("stamps both modes with one clause the publisher recognises", () => {
    const shipped = crossPositionClause("shipped", 0.5, "0.25");
    expect(shipped).toBe(", crossPosition=shipped-glass0.5-against-glass0.25");
    expect(crossPositionClause("candidate", 0.25, "none"))
      .toBe(", crossPosition=candidate-glass0.25-against-glassnone");
    expect(carriesCrossPositionStamp(`materialProfile=x sha256:aaaaaaaaaaaa${shipped}`)).toBe(true);
    expect(carriesCrossPositionStamp("materialProfile=x sha256:aaaaaaaaaaaa")).toBe(false);
  });
});

/*
 * The G0 review's first finding: a row's position is derived from the documents its capture
 * path names, each read and checked against the hash the row records, and the stamp is a label
 * that must agree with them.
 */
describe("both modes, the position a row's documents derive", () => {
  const REPO = resolve(PACKAGE, "../..");
  const DOC05 = "materialProfile=packages/calibration/profiles/" +
    "apple-macos-27.0-1x-light-standard-glass0.5.json sha256:85ad7f7e3e0d sections=renderer+cssTierMapping";
  const STAMP = ", crossPosition=shipped-glass0.5-against-glass0.25";
  const verdict = (profileKey: string, capturePath: string, crossPosition: boolean, authoritative = false) =>
    crossPositionVerdict({ profileKey, capturePath }, { crossPosition, authoritative, repoRoot: REPO });

  it("admits an unstamped row at its documents' own position", () => {
    expect(verdict(KEY_05, DOC05, false)).toBeUndefined();
    expect(verdict(KEY_05, DOC05, false, true)).toBeUndefined();
  });

  it("red: an unstamped 0.5-document row against a 0.25 profile, at a stage and in scratch", () => {
    expect(verdict(KEY_025, DOC05, false, true)).toMatch(/never enters a stage or a publication/);
    expect(verdict(KEY_025, DOC05, true, true)).toMatch(/never enters a stage or a publication/);
    expect(verdict(KEY_025, DOC05, false)).toMatch(/declare it with --cross-position, into scratch/);
  });

  it("red: under --cross-position, a capture with no stamp or another stamp is refused, not re-stamped", () => {
    expect(verdict(KEY_025, DOC05, true))
      .toMatch(/must carry, crossPosition=shipped-glass0\.5-against-glass0\.25, and it carries no stamp/);
    expect(verdict(KEY_025, `${DOC05}, crossPosition=candidate-glass0.25-against-glass0.5`, true))
      .toMatch(/it carries crossPosition=candidate-glass0\.25-against-glass0\.5/);
  });

  it("green: under --cross-position, the stamp the documents derive is admitted in scratch", () => {
    expect(verdict(KEY_025, `${DOC05}${STAMP}`, true)).toBeUndefined();
  });

  it("red: a stamp on a same-position row is false, and a stamp never proves a position", () => {
    expect(verdict(KEY_05, `${DOC05}${STAMP}`, false)).toMatch(/the stamp is false/);
    expect(verdict(KEY_05, `${DOC05}${STAMP}`, true)).toMatch(/the stamp is false/);
  });

  it("red: a document whose bytes are not the row's hash yields no position", () => {
    expect(verdict(KEY_05, DOC05.replace("85ad7f7e3e0d", "85ad7f7e3e0e"), false))
      .toMatch(/hashes to 85ad7f7e3e0d, and the row records 85ad7f7e3e0e/);
  });

  it("derives a candidate row's position from its declaration's endpoint keys", () => {
    const declaration = "packages/calibration/results/2026-10-01-w43-g0-declaration/seam/" +
      "scratch-candidate/candidate.json";
    const label = `materialProfile=candidate candidateDocument=${declaration} declarationSha256=` +
      `${sha(readFileSync(resolve(REPO, declaration), "utf8")).slice(0, 12)} name=x glassTintAmount=0.25`;
    expect(verdict(KEY_025, label, false)).toBeUndefined();
    expect(verdict(KEY_05, label, false)).toMatch(/at glass 0\.25 and the profile .*glass0\.5 at glass 0\.5/);
    expect(verdict(KEY_05, `${label}, crossPosition=candidate-glass0.25-against-glass0.5`, true))
      .toBeUndefined();
  });
});

// ---------------------------------------------------------------------------
// The driver's half: the declaration file, every piece matched by hash
// ---------------------------------------------------------------------------

const SOURCES = {
  "active.light": "apple-macos-27.0-1x-light-standard-glass0.5",
  "active.dark": "apple-macos-27.0-1x-dark-standard-glass0.5",
  "receded.light": "apple-macos-27.0-1x-light-standard-glass0.5-receded",
  "receded.dark": "apple-macos-27.0-1x-dark-standard-glass0.5-receded",
} as const;
type Slot = keyof typeof SOURCES;

const sha = (text: string) => createHash("sha256").update(text).digest("hex");

/**
 * A scratch directory holding the four 0.5 documents relabelled to `glass`, and a correct
 * declaration over them. `edit` changes one document before it is hashed; `after` changes
 * the declaration or a file after hashing.
 */
function scratch(options: {
  glass?: string;
  edit?: (slot: Slot, document: Record<string, unknown>) => void;
  declaration?: (declaration: Record<string, unknown>) => void;
  after?: (dir: string) => void;
} = {}): string {
  const glass = options.glass ?? "0.25";
  const dir = mkdtempSync(join(tmpdir(), "w43-candidate-"));
  const endpoints: Record<string, { path: string; sha256: string }> = {};
  let mapping: unknown;
  for (const [slot, key] of Object.entries(SOURCES) as [Slot, string][]) {
    const document = JSON.parse(readFileSync(resolve(PROFILES, `${key}.json`), "utf8")) as
      Record<string, unknown>;
    document["profileKey"] = (document["profileKey"] as string).replace("-glass0.5", `-glass${glass}`);
    options.edit?.(slot, document);
    const text = `${JSON.stringify(document, null, 2)}\n`;
    writeFileSync(join(dir, `${slot}.json`), text);
    endpoints[slot] = { path: `${slot}.json`, sha256: sha(text) };
    if (slot === "active.light") mapping = document["cssTierMapping"];
  }
  const declaration: Record<string, unknown> = {
    kind: CANDIDATE_DECLARATION_KIND,
    schemaVersion: 1,
    name: `apple-macos-27.0-glass${glass}`,
    platform: "macOS 27.0",
    glassTintAmount: Number(glass),
    endpoints,
    cssTierMappingSha256: mapping === undefined ? "0".repeat(64) : cssTierMappingSha256(mapping),
  };
  options.declaration?.(declaration);
  writeFileSync(join(dir, "candidate.json"), `${JSON.stringify(declaration, null, 2)}\n`);
  options.after?.(dir);
  return join(dir, "candidate.json");
}

describe("candidate mode, the declaration the driver reads", () => {
  it("assembles the 0.5 content under 0.25 keys into the shipped document's material", () => {
    const candidate = readCandidateDocument(scratch());
    const { document } = candidate;
    expect(document.glassTintAmount).toBe(0.25);
    expect(document.cssTierMapping).toEqual(macos27CssTierMapping);
    for (const pose of ["active", "receded"] as const) {
      for (const scheme of ["light", "dark"] as const) {
        const shipped = macos27MaterialProfileDocument[pose][scheme];
        expect(document[pose][scheme].patch).toEqual(shipped.patch);
        expect(document[pose][scheme].resolvedMaterialSha256).toBe(shipped.resolvedMaterialSha256);
        expect(document[pose][scheme].profileKey)
          .toBe(shipped.profileKey!.replace("-glass0.5", "-glass0.25"));
      }
    }
  });

  it("red: refuses a file whose bytes are not the declared hash", () => {
    const path = scratch({ after: (dir) => writeFileSync(join(dir, "receded.dark.json"),
      `${readFileSync(join(dir, "receded.dark.json"), "utf8")} `) });
    expect(() => readCandidateDocument(path)).toThrow(/receded\.dark declares sha256 .* has /);
  });

  it("red: refuses a partial declaration and an invented slot", () => {
    expect(() => readCandidateDocument(scratch({
      declaration: (d) => { delete (d["endpoints"] as Record<string, unknown>)["active.dark"]; },
    }))).toThrow(/partial: no active\.dark endpoint/);
    expect(() => readCandidateDocument(scratch({
      declaration: (d) => {
        const e = d["endpoints"] as Record<string, unknown>;
        e["pressed.light"] = e["active.light"];
      },
    }))).toThrow(/declares endpoint slots no document has: pressed\.light/);
  });

  it("red: refuses an endpoint whose recorded digest does not reproduce over the runtime default", () => {
    const path = scratch({ edit: (slot, d) => {
      if (slot === "active.dark") (d["patch"] as Record<string, unknown>)["tintChromaScale"] = 0.5;
    } });
    expect(() => readCandidateDocument(path))
      .toThrow(/active\.dark records resolvedMaterialSha256 2a4323f33df8d799, and its patch .* resolves to/);
  });

  it("red: refuses a receded endpoint composed over another active endpoint", () => {
    const path = scratch({ edit: (slot, d) => {
      if (slot === "active.light") (d["patch"] as Record<string, unknown>)["tintChromaScale"] = 0.5;
      if (slot === "active.light") d["resolvedMaterialSha256"] = "0000000000000000";
    } });
    expect(() => readCandidateDocument(path)).toThrow(/active\.light records resolvedMaterialSha256/);
  });

  it("red: refuses a mapping hash the assembled mapping does not have", () => {
    expect(() => readCandidateDocument(scratch({
      declaration: (d) => { d["cssTierMappingSha256"] = "0".repeat(64); },
    }))).toThrow(/declares cssTierMappingSha256 0{64}, and the assembled mapping hashes to/);
  });

  it("red: refuses a candidate with no mapping, and two active documents that disagree on one", () => {
    expect(() => readCandidateDocument(scratch({ edit: (slot, d) => {
      if (slot === "active.light") delete d["cssTierMapping"];
    } }))).toThrow(/partial: the active\.light document carries no cssTierMapping/);
    expect(() => readCandidateDocument(scratch({ edit: (slot, d) => {
      if (slot === "active.dark") d["cssTierMapping"] = { blurSigmaScale: 2.3 };
    } }))).toThrow(/cssTierMapping\.blurSigmaScale: the active\.light document says 2\.2/);
  });

  it("red: refuses a receded endpoint that carries a CSS mapping", () => {
    expect(() => readCandidateDocument(scratch({ edit: (slot, d) => {
      if (slot === "receded.light") d["cssTierMapping"] = { blurSigmaScale: 2.2 };
    } }))).toThrow(/receded document is a difference/);
  });

  it("red: refuses keys whose glass token differs from the declared position", () => {
    expect(() => readCandidateDocument(scratch({
      declaration: (d) => { d["glassTintAmount"] = 0.5; },
    }))).toThrow(/glass token: active\.light key .* names glass 0\.25, the candidate declares 0\.5/);
  });

  it("red: refuses a candidate that names the shipped 0.5 document", () => {
    expect(() => readCandidateDocument(scratch({ glass: "0.5" })))
      .toThrow(/names a shipped document: 'apple-macos-27\.0-glass0\.5'/);
  });
});

/*
 * The flags that would put another material's half beside a candidate, refused by both
 * command lines before any browser or server starts. Run as child processes because both
 * drivers act on import.
 */
describe("both modes, the command lines", () => {
  const run = (script: string, args: readonly string[], env: Record<string, string | undefined> = {}) => {
    const merged: Record<string, string | undefined> = { ...process.env, ...env };
    for (const [name, value] of Object.entries(merged)) if (value === undefined) delete merged[name];
    return spawnSync("npx", ["tsx", script, ...args], { cwd: PACKAGE, encoding: "utf8", env: merged });
  };
  const candidate = scratch();
  const active = resolve(PROFILES, `${KEY_05}.json`);
  const receded = resolve(PROFILES, `${KEY_05}-receded.json`);

  it("red: capture-web refuses a candidate beside --material-profile or --receded-profile", () => {
    for (const extra of [["--material-profile", active], ["--receded-profile", receded]]) {
      const out = run("scripts/capture-web.ts",
        ["photo__rrect-md__rest", "--out", "/tmp/w43-never", "--candidate-document", candidate, ...extra]);
      expect(out.status).not.toBe(0);
      expect(out.stderr).toMatch(/takes no --material-profile or --receded-profile beside it/);
    }
  }, 60_000);

  it("red: capture-web refuses a candidate into the canonical capture tree", () => {
    const out = run("scripts/capture-web.ts", ["photo__rrect-md__rest", "--candidate-document", candidate]);
    expect(out.status).not.toBe(0);
    expect(out.stderr).toMatch(/would write into the canonical capture tree/);
  }, 60_000);

  it("red: compare refuses a candidate beside a document flag, into a stage, or into the canonical tree", () => {
    const scratchTree = { VITREA_WEB_CAPTURES: "/tmp/w43-never" };
    const beside = run("cli/compare.ts", ["--candidate-document", candidate, "--material-profile", active,
      "--out-matrix", "/tmp/w43-never.json"], scratchTree);
    expect(beside.status).not.toBe(0);
    expect(beside.stderr).toMatch(/takes no --material-profile or --receded-profile beside it/);
    const staged = run("cli/compare.ts", ["--candidate-document", candidate, "--stage", "/tmp/w43-never"],
      scratchTree);
    expect(staged.status).not.toBe(0);
    expect(staged.stderr).toMatch(/cannot measure into the stage .*, named by --stage/);
    const canonical = run("cli/compare.ts", ["--candidate-document", candidate,
      "--out-matrix", "/tmp/w43-never.json"], { VITREA_WEB_CAPTURES: undefined });
    expect(canonical.status).not.toBe(0);
    expect(canonical.stderr).toMatch(/would write its captures into the canonical tree/);
  }, 120_000);

  const scratchTree = { VITREA_WEB_CAPTURES: "/tmp/w43-never-captures" };
  const compareAgainst = (material: readonly string[], profile: string, extra: readonly string[]) =>
    run("cli/compare.ts", [...material, "--profile", profile, "--scene", "photo__rrect-md__rest",
      "--out-matrix", "/tmp/w43-never.json", "--skip-capture", ...extra], scratchTree);
  const asCandidate = ["--candidate-document", candidate];
  const asShipped05 = ["--material-profile", active];
  const KEY_265 = "apple-macos-26.5-1x-light-standard";

  it("red: compare refuses the 0.25 candidate against 0.5 fixtures without --cross-position", () => {
    const out = compareAgainst(asCandidate, KEY_05, []);
    expect(out.status).not.toBe(0);
    expect(out.stderr).toMatch(/the candidate is at glass 0\.25 and is read against .*glass0\.5/);
  }, 60_000);

  it("green: compare admits it under --cross-position, past the gate to the capture lookup", () => {
    const out = compareAgainst(asCandidate, KEY_05, ["--cross-position"]);
    expect(`${out.stdout}${out.stderr}`).not.toMatch(/is read against|stamp would be false/);
    expect(`${out.stdout}${out.stderr}`).toMatch(/no webgpu-tier capture on disk/);
  }, 60_000);

  it("red: strict mode refuses the shipped 0.5 material against fixtures at another position", () => {
    const out = compareAgainst(asShipped05, KEY_265, []);
    expect(out.status).not.toBe(0);
    expect(out.stderr).toMatch(
      /the shipped material is at glass 0\.5 and is read against apple-macos-26\.5-1x-light-standard \(glass none\)/);
  }, 60_000);

  it("green: strict mode admits it under --cross-position, past the gate to the capture lookup", () => {
    const out = compareAgainst(asShipped05, KEY_265, ["--cross-position"]);
    expect(`${out.stdout}${out.stderr}`).not.toMatch(/is read against|stamp would be false/);
    expect(`${out.stdout}${out.stderr}`).toMatch(/no webgpu-tier capture on disk/);
  }, 60_000);

  it("green: strict mode at its own position needs no flag, and the flag there is refused", () => {
    const plain = compareAgainst(asShipped05, KEY_05, []);
    expect(`${plain.stdout}${plain.stderr}`).toMatch(/no webgpu-tier capture on disk/);
    const flagged = compareAgainst(asShipped05, KEY_05, ["--cross-position"]);
    expect(flagged.status).not.toBe(0);
    expect(flagged.stderr).toMatch(/the shipped material's own glass 0\.5, so the stamp would be false/);
  }, 60_000);

  /*
   * The G0 review's second finding: a scratch path that is a symbolic link to the canonical tree,
   * or that runs through a link to the package, is the canonical tree. The canonical tree need
   * not exist (it is absent in a fresh worktree), so the first link is also a dangling one.
   */
  const CANONICAL_TREE = resolve(PACKAGE, "web-captures");
  const links = mkdtempSync(join(tmpdir(), "w43-links-"));
  symlinkSync(CANONICAL_TREE, join(links, "to-tree"));
  symlinkSync(PACKAGE, join(links, "to-package"));
  const aliases = [join(links, "to-tree", "run"), join(links, "to-package", "web-captures", "run")];

  it("resolves every link before the containment check, a dangling one included", () => {
    for (const alias of aliases) expect(withinTree(alias, CANONICAL_TREE), alias).toBe(true);
    const plain = join(links, "plain");
    mkdirSync(plain);
    expect(withinTree(plain, CANONICAL_TREE)).toBe(false);
    expect(withinTree(join(links, "to-package", "web-captures-scratch"), CANONICAL_TREE)).toBe(false);
  });

  it("red: a linked alias of the canonical tree is refused for candidate and cross-position runs", () => {
    for (const alias of aliases) {
      for (const material of [asCandidate, [...asShipped05, "--cross-position", "0.25"]]) {
        const capture = run("scripts/capture-web.ts", ["photo__rrect-md__rest", "--out", alias, ...material]);
        expect(capture.status, alias).not.toBe(0);
        expect(capture.stderr).toMatch(/would write into the canonical capture tree/);
      }
      for (const material of [asCandidate, [...asShipped05, "--cross-position"]]) {
        const compare = run("cli/compare.ts", [...material, "--out-matrix", "/tmp/w43-never.json"],
          { VITREA_WEB_CAPTURES: alias });
        expect(compare.status, alias).not.toBe(0);
        expect(compare.stderr).toMatch(/would write its captures into the canonical tree/);
      }
    }
  }, 180_000);

  /*
   * The G0 review's first finding, on compare's `--skip-capture` path: the capture on disk is
   * judged by its own documents, whatever this run's flags say.
   */
  const AT265 = "apple-macos-26.5-1x-light-standard";
  const skipCapture = (capturePath: string) => {
    const tree = mkdtempSync(join(tmpdir(), "w43-skip-"));
    const dir = join(tree, AT265, "photo__rrect-md__rest");
    mkdirSync(dir, { recursive: true });
    copyFileSync(resolve(PACKAGE, "../../apps/reference-apple/fixtures", AT265, "photo__rrect-md__rest.png"),
      join(dir, "photo__rrect-md__rest__webgpu.png"));
    writeFileSync(join(dir, "cell__webgpu.json"), JSON.stringify({ engine: "chromium",
      engineVersion: "1", renderer: "webgpu", samplingBackend: "gpu-texture", gpuAdapter: "apple/metal-3",
      colorSpace: "srgb", capturePath, sceneId: "photo__rrect-md__rest", pixelSize: [320, 200],
      deterministic: true, repeatNoise: 0 }));
    const matrix = join(tree, "matrix.json");
    const out = run("cli/compare.ts", [...asShipped05, "--profile", AT265, "--scene", "photo__rrect-md__rest",
      "--set", "calibration", "--skip-capture", "--cross-position", "--out-matrix", matrix],
    { VITREA_WEB_CAPTURES: tree });
    return { out, matrix };
  };
  const DOC05 = "materialProfile=packages/calibration/profiles/" +
    "apple-macos-27.0-1x-light-standard-glass0.5.json sha256:85ad7f7e3e0d sections=renderer+cssTierMapping";

  it("red: compare --skip-capture --cross-position over an unstamped capture is refused", () => {
    const { out } = skipCapture(DOC05);
    expect(out.status).not.toBe(0);
    expect(`${out.stdout}${out.stderr}`)
      .toMatch(/must carry, crossPosition=shipped-glass0\.5-against-glassnone, and it carries no stamp/);
  }, 60_000);

  it("green: the same run over a capture stamped from the derived pair writes a stamped row", () => {
    const { out, matrix } = skipCapture(`${DOC05}, crossPosition=shipped-glass0.5-against-glassnone`);
    expect(out.status, `${out.stdout}${out.stderr}`).toBe(0);
    const row = JSON.parse(readFileSync(matrix, "utf8")).cells[0];
    expect(row.key.profileKey).toBe(AT265);
    expect(row.key.web.capturePath).toMatch(/, crossPosition=shipped-glass0\.5-against-glassnone$/);
  }, 60_000);

  /*
   * The second review round: a declared stage is recognised by its declaration, whichever flag
   * names its matrix file. The reviewer's reproduction, a stamped candidate-against-0.5 capture
   * written through --matrix / --out-matrix into a declared 0.5 stage, on both command lines.
   */
  const SCENE = "photo__rrect-md__rest";
  const FIXTURE05 = resolve(PACKAGE, "../../apps/reference-apple/fixtures", KEY_05, `${SCENE}.png`);
  const CANDIDATE_REL = "packages/calibration/results/2026-10-01-w43-g0-declaration/seam/" +
    "scratch-candidate/candidate.json";
  const stampedCandidateCell = () => JSON.stringify({ engine: "chromium", engineVersion: "1",
    renderer: "webgpu", samplingBackend: "gpu-texture", gpuAdapter: "apple/metal-3", colorSpace: "srgb",
    capturePath: `materialProfile=candidate candidateDocument=${CANDIDATE_REL} declarationSha256=` +
      `${sha(readFileSync(resolve(PACKAGE, "../..", CANDIDATE_REL), "utf8")).slice(0, 12)} ` +
      "name=apple-macos-27.0-glass0.25-w43-g0-scratch glassTintAmount=0.25, " +
      "crossPosition=candidate-glass0.25-against-glass0.5",
    sceneId: SCENE, pixelSize: [320, 200], deterministic: true, repeatNoise: 0 });
  const declaredStage05 = () => {
    const stage = join(mkdtempSync(join(tmpdir(), "w43-stage-")), "stage");
    const declared = spawnSync(process.execPath, ["--import", "tsx", "cli/matrix.ts", "stage", stage,
      "--profile", KEY_05, "--renderer", "webgpu", "--set", "calibration", "--material-profile", active],
    { cwd: PACKAGE, encoding: "utf8", env: { ...process.env, VITREA_MATRIX_PATH: "" } });
    expect(declared.status, declared.stderr).toBe(0);
    return stage;
  };
  const snapshot = (dir: string) =>
    readdirSync(dir).sort().map((name) => `${name} ${sha(readFileSync(join(dir, name), "utf8"))}`);

  it("red/green: diff --matrix into a declared stage is that stage; into scratch it writes", () => {
    const stage = declaredStage05();
    const before = snapshot(stage);
    const cell = join(mkdtempSync(join(tmpdir(), "w43-cell-")), "cell.json");
    writeFileSync(cell, stampedCandidateCell());
    const diff = (matrix: string) => run("cli/diff.ts", ["--native", FIXTURE05, "--web", FIXTURE05,
      "--profile", KEY_05, "--scene", SCENE, "--web-cell", cell, "--matrix", matrix, "--cross-position"]);
    const staged = diff(join(stage, "matrix.json"));
    expect(staged.status).not.toBe(0);
    expect(staged.stderr)
      .toMatch(/--cross-position cannot measure into the stage .*named by --stage or by its matrix\.json/);
    expect(snapshot(stage)).toEqual(before);
    const scratchMatrix = join(mkdtempSync(join(tmpdir(), "w43-scratch-")), "matrix.json");
    const scratchRun = diff(scratchMatrix);
    expect(scratchRun.status, scratchRun.stderr).toBe(0);
    expect(JSON.parse(readFileSync(scratchMatrix, "utf8")).cells[0].key.web.capturePath)
      .toMatch(/, crossPosition=candidate-glass0\.25-against-glass0\.5$/);
  }, 120_000);

  it("red/green: compare --out-matrix into a declared stage is that stage; into scratch it writes", () => {
    const stage = declaredStage05();
    const before = snapshot(stage);
    const tree = mkdtempSync(join(tmpdir(), "w43-skip-candidate-"));
    const dir = join(tree, KEY_05, SCENE);
    mkdirSync(dir, { recursive: true });
    copyFileSync(FIXTURE05, join(dir, `${SCENE}__webgpu.png`));
    writeFileSync(join(dir, "cell__webgpu.json"), stampedCandidateCell());
    const compare = (matrix: string) => run("cli/compare.ts", ["--candidate-document",
      resolve(PACKAGE, "../..", CANDIDATE_REL), "--cross-position", "--profile", KEY_05, "--scene", SCENE,
      "--set", "calibration", "--skip-capture", "--out-matrix", matrix], { VITREA_WEB_CAPTURES: tree });
    const staged = compare(join(stage, "matrix.json"));
    expect(staged.status).not.toBe(0);
    expect(staged.stderr)
      .toMatch(/cannot measure into the stage .*named by --stage or by its matrix\.json/);
    expect(snapshot(stage)).toEqual(before);
    const scratchMatrix = join(mkdtempSync(join(tmpdir(), "w43-scratch-")), "matrix.json");
    const scratchRun = compare(scratchMatrix);
    expect(scratchRun.status, `${scratchRun.stdout}${scratchRun.stderr}`).toBe(0);
    expect(JSON.parse(readFileSync(scratchMatrix, "utf8")).cells[0].key.web.capturePath)
      .toMatch(/, crossPosition=candidate-glass0\.25-against-glass0\.5$/);
  }, 120_000);

  it("red: --cross-position is scratch only: no stage, no canonical tree, no authoritative matrix", () => {
    const staged = run("cli/compare.ts", [...asShipped05, "--cross-position", "--stage", "/tmp/w43-never"],
      scratchTree);
    expect(staged.status).not.toBe(0);
    expect(staged.stderr).toMatch(/--cross-position cannot measure into the stage .*, named by --stage/);
    const tree = run("cli/compare.ts", [...asShipped05, "--cross-position", "--out-matrix",
      "/tmp/w43-never.json"], { VITREA_WEB_CAPTURES: undefined });
    expect(tree.status).not.toBe(0);
    expect(tree.stderr).toMatch(/--cross-position would write its captures into the canonical tree/);
    for (const destination of [["--out-matrix", resolve(PACKAGE, "results/matrix.json")], []]) {
      const authoritative = run("cli/compare.ts", [...asShipped05, "--profile", KEY_265, "--scene",
        "photo__rrect-md__rest", "--skip-capture", "--cross-position", ...destination], scratchTree);
      expect(authoritative.status).not.toBe(0);
      expect(authoritative.stderr).toMatch(/is canonical, immutable matrix evidence/);
    }
    const capture = run("scripts/capture-web.ts", ["photo__rrect-md__rest", ...asShipped05,
      "--cross-position", "0.25"]);
    expect(capture.status).not.toBe(0);
    expect(capture.stderr).toMatch(/--cross-position would write into the canonical capture tree/);
  }, 120_000);

  it("red: --cross-position with no positioned material, on both command lines", () => {
    const none = run("cli/compare.ts", ["--cross-position", "--out-matrix", "/tmp/w43-never.json"],
      scratchTree);
    expect(none.status).not.toBe(0);
    expect(none.stderr).toMatch(/names neither a --candidate-document nor a --material-profile/);
    const bare = join(mkdtempSync(join(tmpdir(), "w43-bare-")), "bare.json");
    writeFileSync(bare, '{ "tintChromaScale": 0.5 }\n');
    const barePatch = compareAgainst(["--material-profile", bare], KEY_265, ["--cross-position"]);
    expect(barePatch.status).not.toBe(0);
    expect(barePatch.stderr).toMatch(/bare patch with no profileKey/);
    const capture = run("scripts/capture-web.ts",
      ["photo__rrect-md__rest", "--out", "/tmp/w43-never", "--cross-position", "0.5"]);
    expect(capture.status).not.toBe(0);
    expect(capture.stderr).toMatch(/names neither a --candidate-document nor a keyed --material-profile/);
  }, 120_000);

  it("red: capture-web refuses a cross-position stamp at the material's own position", () => {
    for (const material of [[...asCandidate, "--cross-position", "0.25"],
      [...asShipped05, "--cross-position", "0.5"]]) {
      const out = run("scripts/capture-web.ts", ["photo__rrect-md__rest", "--out", "/tmp/w43-never",
        ...material]);
      expect(out.status).not.toBe(0);
      expect(out.stderr).toMatch(/is the material's own glass position/);
    }
  }, 60_000);
});

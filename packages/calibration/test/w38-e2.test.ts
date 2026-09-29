/** W38 E2's fixed-reference rendered-edge baseline, charter clause 1c. */
import { loadGeneration, legacyEnvelopeDigest } from "../src/matrix-store";
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { gunzipSync } from "node:zlib";
import { describe, expect, it } from "vitest";

const root = resolve(import.meta.dirname, "../results/2026-09-25-w38-g0-rim-axis-cut");
const read = (name: string) => {
  const bytes = readFileSync(resolve(root, name));
  return JSON.parse((name.endsWith(".gz") ? gunzipSync(bytes) : bytes).toString());
};
const run = (args: string[]) => spawnSync("python3.12", [resolve(root, "e2.py"), ...args], {
  encoding: "utf8", timeout: 180_000,
  env: { ...process.env, OPENBLAS_NUM_THREADS: "1", VECLIB_MAXIMUM_THREADS: "1" },
});

describe("W38 E2 declaration and pre-change reference", () => {
  it("rederives the baseline against fixed native bytes and matrix-named captures", () => {
    const result = run(["--verify"]);
    expect(result.status, result.stderr).toBe(0);
    const check = JSON.parse(result.stdout);
    expect(check.cells).toBe(212);
    // The canonical web capture tree is gitignored and absent on CI. E2 still
    // checks the complete frozen population, native references and documents;
    // every missing web cell must be explicitly UNMEASURED, never a passing bin.
    const canonicalCaptures = "/Users/new/Developer/GitHub/designer/packages/calibration/web-captures";
    if (existsSync(canonicalCaptures)) {
      expect(check.sameBaseline).toBe(true);
      expect(check.absentCells).toEqual([]);
    } else {
      expect(check.sameBaseline).toBe(false);
      expect(check.absentCells).toEqual(read("e2-declaration.json").cells.map(
        (cell: { cell: string }) => cell.cell));
      expect(check.measuredRows).toBe(0);
      expect(check.unmeasuredRows).toBe(212);
    }
  }, 180_000);

  it("does not turn absent capsule sides or undersampled arc bins into passing bins", () => {
    const decl = read("e2-declaration.json");
    const rows = read("e2-baseline.json.gz");
    expect(rows).toHaveLength(decl.cells.length);
    expect(rows.filter((row: { role: string }) => row.role === "probe")).toHaveLength(140);
    expect(rows.filter((row: { role: string }) => row.role === "holdout")).toHaveLength(0);
    expect(rows.some((row: { estimator: string }) => row.estimator === "grouped-arcs")).toBe(true);
    for (const row of rows) {
      const scale = row.cell.includes("-2x-") ? 2 : 1;
      if (row.estimator === "single-straights") {
        expect(row.bins).toHaveLength(24 * scale);
        if (row.cell.includes("__capsule-button__")) {
          expect(row.status).toBe("UNMEASURED");
          for (const side of ["left", "right"]) {
            expect(row.bins.filter((b: { side: string }) => b.side === side)
              .every((b: { status: string }) => b.status === "UNMEASURED")).toBe(true);
          }
        }
      } else {
        expect(row.bins).toHaveLength(3 * 16 * 6 * scale);
        for (const member of [0, 1, 2]) expect(row.bins.some((b: { member: number; status: string }) =>
          b.member === member && b.status === "measured")).toBe(true);
      }
      for (const bin of row.bins) {
        expect(bin.status).toBe(bin.pixels >= decl.minimumPixels ? "measured" : "UNMEASURED");
        if (bin.status === "UNMEASURED") expect(bin.residualRGB).toBeNull();
      }
    }
  });

  it("binds every measured reference to native PNG, matrix capture and both documents", () => {
    const decl = read("e2-declaration.json");
    const calibration = resolve(root, "../..");
    const repo = resolve(calibration, "../..");
    // Reconstruct the whole pre-W38 envelope from its named generations, including
    // frozen 26.5 rows. Future current generations must not move this reference.
    const matrix = { cells: [
      ...loadGeneration("6a9600720477"), ...loadGeneration("950ce1c3e917"),
      ...loadGeneration("85ad7f7e3e0d", "30fbe05986ae"),
      ...loadGeneration("0eac5b294cc2", "5cec8c961201"),
    ] };
    const hash = (bytes: Buffer) => createHash("sha256").update(bytes).digest("hex");
    expect(legacyEnvelopeDigest(matrix.cells)).toBe(decl.preW38.matrixSha256);
    const cells = new Map<string, { key: { web: { capturePath: string } } }>(matrix.cells.map(
      (r: { key: { profileKey: string; sceneId: string; web: { renderer: string; capturePath: string } } }) =>
        [r.key.profileKey + "/" + r.key.sceneId + "/" + r.key.web.renderer, r]));
    for (const ref of decl.cells) {
      const [profile, scene] = ref.cell.split("/");
      const row = cells.get(ref.cell + "/webgpu") as { key: { web: { capturePath: string } } };
      expect(row.key.web.capturePath).toBe(ref.capturePath);
      expect(hash(readFileSync(resolve(repo, "apps/reference-apple/fixtures", profile,
        scene + ".png")))).toBe(ref.nativeSha256);
      expect(Object.keys(ref.documents)).toHaveLength(2);
      for (const [name, sha] of Object.entries(ref.documents)) {
        // Since W41 G2's revert (15478e0f) every pre-W38 document is the live file again, so
        // the retired-copy half never runs here; the next case exercises the resolver itself.
        const stem = name.split("/").pop()!.replace(/\.json$/, "");
        const retired = resolve(calibration,
          "results/2026-09-29-w41-g2-landing/retired-documents", `${stem}.${sha}.json`);
        const live = hash(readFileSync(resolve(repo, name))).slice(0, 12);
        expect(live === sha || hash(readFileSync(retired)).slice(0, 12) === sha).toBe(true);
      }
    }
    expect(decl.outOfEstimator).toHaveLength(26);
    expect(decl.outOfEstimator.every((r: { role: string }) => r.role === "holdout")).toBe(true);
  });

  it("resolves a moved document hash to its byte-exact retired copy, and refuses any other", () => {
    // The archived W41 G2 stage captures name the sealed light receded document, which is no
    // longer the file on disk (c9a §5.193). E2 binds W37's resolver as `document_bytes`; this
    // drives it, and W37's generation check that calls it, with the live hash, the sealed one
    // and hashes nothing holds, so both halves and the refusal run.
    const calibration = resolve(root, "../..");
    const stem = "apple-macos-27.0-1x-light-standard-glass0.5";
    const name = `packages/calibration/profiles/${stem}-receded.json`;
    const active = `packages/calibration/profiles/${stem}.json`;
    const hash = (bytes: Buffer) => createHash("sha256").update(bytes).digest("hex");
    const live = hash(readFileSync(resolve(calibration, "../..", name))).slice(0, 12);
    const sealed = "003940b4c7da";
    const copy = readFileSync(resolve(calibration,
      "results/2026-09-29-w41-g2-landing/retired-documents", `${stem}-receded.${sealed}.json`));
    expect(live, "the retired-copy half runs only while the sealed hash is not live")
      .not.toBe(sealed);
    const nudge = (sha: string) =>
      sha.slice(0, 11) + ((parseInt(sha.charAt(11), 16) + 1) % 16).toString(16);
    const refused = [nudge(sealed), nudge(live), "000000000000"];
    const script = `import hashlib, json, sys
sys.path.insert(0, ${JSON.stringify(root)})
import e2
name, active = ${JSON.stringify(name)}, ${JSON.stringify(active)}
digest = lambda raw: hashlib.sha256(raw).hexdigest()
active_sha = digest((e2.ROOT / active).read_bytes())[:12]
class Metadata:
    def __init__(self, path): self.path = path
    def read(self, cell, kind):
        return json.dumps(dict(capturePath=self.path, deterministic=True, repeatNoise=0)).encode()
def generation(sha):
    path = f'materialProfile={active} sha256:{active_sha} recededProfile={name} sha256:{sha}'
    web = dict(capturePath=path, renderer='webgpu', samplingBackend='gpu-texture')
    row = dict(key=dict(web=web))
    try:
        e2.repaired.old.generation(Metadata(path), 'cell', row)
        return 'admitted'
    except AssertionError:
        return 'refused'
print(json.dumps({sha: dict(bytes=digest(e2.document_bytes(name, sha)), generation=generation(sha))
                  for sha in ${JSON.stringify([live, sealed, ...refused])}}))
`;
    const result = spawnSync("python3.12", ["-c", script], { encoding: "utf8",
      env: { ...process.env, OPENBLAS_NUM_THREADS: "1", VECLIB_MAXIMUM_THREADS: "1" } });
    expect(result.status, result.stderr).toBe(0);
    const resolved = JSON.parse(result.stdout) as
      Record<string, { bytes: string; generation: string }>;
    expect(resolved[live]).toEqual({ bytes: expect.stringMatching(new RegExp("^" + live)),
      generation: "admitted" });
    expect(resolved[sealed]).toEqual({ bytes: hash(copy), generation: "admitted" });
    expect(hash(copy).startsWith(sealed)).toBe(true);
    for (const sha of refused) {
      expect(resolved[sha], sha).toEqual({ bytes: expect.not.stringMatching(new RegExp("^" + sha)),
        generation: "refused" });
    }
  });

  it("rejects changed matrix generation before opening the pixels", () => {
    const result = run(["--self-test"]);
    expect(result.status, result.stderr).toBe(0);
    expect(JSON.parse(result.stdout)).toMatchObject({ rejectsGenerationMismatch: true,
      rejectsMissingGroupMember: true, rejectsHoldout: true,
      shiftedGeometry: true, missingCaptureUnmeasured: true });
    // The self-test replays E2 in full, 22.3 s at green run 36281094139; four times that keeps
    // runner-speed variance from reading as a failure, as it did for the W37 replays.
  }, 90_000);
});

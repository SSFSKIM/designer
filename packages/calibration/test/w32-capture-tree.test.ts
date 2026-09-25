import { createHash } from "node:crypto";
import { mkdirSync, mkdtempSync, readFileSync, symlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { describe, expect, it } from "vitest";
import { checkCaptureTree, formatReport } from "../scripts/check-capture-tree";

/**
 * W32 G0b — the capture-tree checker (claims §5.167; W31 Deferred item 12).
 *
 * The defect the checker exists for is invisible by construction: a stale tree and a
 * current matrix produce sheets that look exactly like honest ones, which is why the
 * macOS 26.5 divergence survived from 2026-09-10 to the W31 charter's grounding read
 * unnoticed. So the cases here are of the checker's VERDICTS rather than of its output,
 * over a scratch tree holding the three shapes the charter names — one matching, one
 * mismatching, one absent — plus the two the distinction between stale-by-choice and
 * stale-by-accident turns on.
 */
const PACKAGE_ROOT = resolve(import.meta.dirname, "..");

const SHIPPED = "aaaaaaaaaaaa";
const RECEDED = "bbbbbbbbbbbb";
const PRIOR = "cccccccccccc";
const PRIOR_RECEDED = "dddddddddddd";
const UNRECORDED = "eeeeeeeeeeee";
const OTHER_RECEDED = "ffffffffffff";

const LIGHT = "apple-macos-27.0-1x-light-standard-glass0.5";
/** Read at the 1x document, as every 2x profile is — which is what makes NB2's case real. */
const LIGHT_2X = "apple-macos-27.0-2x-light-standard-glass0.5";
const FROZEN = "apple-macos-26.5-1x-light-standard";
const FROZEN_RT = "apple-macos-26.5-1x-light-reduced-transparency";

/**
 * The pose clauses the real capture driver writes, derived from the profile key the way the
 * driver derives them. They are on the same string as the documents and are compared beside
 * them (review closure NB2; claims §5.167 §8), so a fabricated `capturePath` that omitted
 * them would be a string no capture ever has — and the cases below turn on which of the two
 * halves disagrees.
 */
interface Pose {
  readonly deviceScaleFactor: string;
  readonly colorScheme: string;
  readonly accessibility: string;
}

const poseFor = (profile: string): Pose => ({
  deviceScaleFactor: profile.includes("-2x-") ? "2" : "1",
  colorScheme: profile.includes("-dark-") ? "dark" : "light",
  accessibility: profile.includes("reduced-transparency")
    ? "reducedTransparency (others explicitly off)"
    : "browser-preferences",
});

const documentClauses = (cell: Cell): string =>
  cell.documents
    .map(([clause, hash], index) =>
      `${index === 0 ? "materialProfile" : "recededProfile"}=packages/calibration/profiles/${clause} `
      + `sha256:${hash}`)
    .join(", ");

const capturePath = (cell: Cell): string => {
  const head = "playwright 151.0.7922.34 element screenshot of #stage, channel=chromium"
    + " --enable-features=Vulkan,WebGPU, viewport=320x200";
  if (cell.poseless === true) return `${head}, ${documentClauses(cell)}`;
  const pose = cell.pose ?? poseFor(cell.profile);
  return `${head} deviceScaleFactor=${pose.deviceScaleFactor},`
    + ` colorScheme=${pose.colorScheme}, animations=disabled, frames=8,`
    + ` accessibility=${pose.accessibility}, ${documentClauses(cell)}`;
};

interface Cell {
  readonly profile: string;
  readonly scene: string;
  readonly renderer: string;
  readonly documents: readonly (readonly [string, string])[];
  /** Overridden only where a case fabricates a capture posed differently from its row. */
  readonly pose?: Pose;
  /** A string carrying no pose clause at all — the capture format moving underneath. */
  readonly poseless?: boolean;
}

function scratch(matrixCells: readonly Cell[], treeCells: readonly (Cell & { sceneId?: string })[]): {
  tree: string;
  matrixPath: string;
  supersededIndexPath: string;
} {
  const root = mkdtempSync(join(tmpdir(), "w32-g0b-capture-tree-"));
  const tree = join(root, "web-captures");
  for (const cell of treeCells) {
    const dir = join(tree, cell.profile, cell.scene);
    mkdirSync(dir, { recursive: true });
    writeFileSync(
      join(dir, `cell__${cell.renderer}.json`),
      JSON.stringify({
        renderer: cell.renderer,
        sceneId: cell.sceneId ?? cell.scene,
        capturePath: capturePath(cell),
      }),
    );
  }
  const matrixPath = join(root, "matrix.json");
  writeFileSync(matrixPath, JSON.stringify({
    schemaVersion: 5,
    cells: matrixCells.map((cell) => ({
      key: {
        profileKey: cell.profile,
        sceneId: cell.scene,
        web: {
          engine: "chromium", engineVersion: "151.0.7922.34",
          renderer: cell.renderer, samplingBackend: "gpu-texture",
          gpuAdapter: "synthetic", colorSpace: "srgb", capturePath: capturePath(cell),
        },
      },
    })),
  }));
  const supersededIndexPath = join(root, "superseded-index.json");
  writeFileSync(supersededIndexPath, JSON.stringify({
    byDocumentSha256: { [PRIOR]: `${PRIOR}.json`, [PRIOR_RECEDED]: `${PRIOR}.json` },
  }));
  return { tree, matrixPath, supersededIndexPath };
}

const current: Cell = {
  profile: LIGHT, scene: "photo__rrect-md__rest", renderer: "webgpu",
  documents: [[`${LIGHT}.json`, SHIPPED]],
};
const inactive: Cell = {
  profile: LIGHT, scene: "photo__rrect-md__inactive", renderer: "webgpu",
  documents: [[`${LIGHT}.json`, SHIPPED], [`${LIGHT}-receded.json`, RECEDED]],
};

const check = (
  paths: ReturnType<typeof scratch>, supersededOk = false,
): ReturnType<typeof checkCaptureTree> =>
  checkCaptureTree({ ...paths, supersededOk });

describe("the capture tree against the working matrix (claims §5.167)", () => {
  it("matches one capture, fails a mismatching one, and reports an absent one without failing", () => {
    // The charter's three shapes in one tree: a capture at the row's generation, a
    // capture at a generation nothing recorded, and a row whose capture is not there at
    // all — which is the normal state of a machine that has run one gate.
    const stale = { ...inactive, documents: [[`${LIGHT}.json`, UNRECORDED]] as const };
    const absent: Cell = { ...current, scene: "photo__rrect-lg__rest" };
    const paths = scratch([current, inactive, absent], [current, stale]);
    const report = check(paths);

    expect(report.findings.map((f) => f.verdict).sort()).toEqual(["match", "mismatch"]);
    expect([...report.rowsWithoutCapture.values()].flat()).toEqual(["photo__rrect-lg__rest"]);
    expect(report.exitCode).toBe(1);

    const mismatch = report.findings.find((f) => f.verdict === "mismatch");
    // Both hashes, on the report, because "they differ" without them sends the reader
    // back to the tree to find out how.
    expect(mismatch?.capture).toEqual([`${LIGHT}.json ${UNRECORDED}`]);
    expect(mismatch?.row).toEqual([`${LIGHT}-receded.json ${RECEDED}`, `${LIGHT}.json ${SHIPPED}`]);

    const text = formatReport(report, false);
    expect(text).toContain(UNRECORDED);
    expect(text).toContain(SHIPPED);
    expect(text).toContain("exit 1");
  });

  it("skips cleanly and exits 0 where there is no tree", () => {
    // The tree is gitignored and lives on the capture machine. A checker that fails on
    // every other machine is a checker somebody disables, and then the rule is gone again.
    const paths = scratch([current], [current]);
    const report = checkCaptureTree({ ...paths, tree: join(paths.tree, "absent"), supersededOk: false });
    expect(report.treePresent).toBe(false);
    expect(report.exitCode).toBe(0);
    expect(formatReport(report, false)).toMatch(/^no capture tree at .*absent; skipped$/);
  });

  it("holds the RECEDED document to the row as well as the active one", () => {
    // An `__inactive` cell is posed with a receded document, and a tree posed from a
    // different one drew a different material at an active hash that matches. The
    // comparison is over the whole set for exactly this case.
    const posedElsewhere = {
      ...inactive,
      documents: [[`${LIGHT}.json`, SHIPPED], [`${LIGHT}-receded.json`, UNRECORDED]] as const,
    };
    const report = check(scratch([inactive], [posedElsewhere]));
    expect(report.findings.map((f) => f.verdict)).toEqual(["mismatch"]);
    expect(report.exitCode).toBe(1);
  });

  it("tells a recorded superseded generation from an unrecorded one, and --superseded-ok demotes it", () => {
    // Stale by CHOICE — every hash is in the split's index, so the tree is at a
    // generation somebody recorded — against stale by ACCIDENT, which is never anything
    // but a failure. The flag moves the first and must not move the second.
    const previous = {
      ...inactive,
      documents: [[`${LIGHT}.json`, PRIOR], [`${LIGHT}-receded.json`, PRIOR_RECEDED]] as const,
    };
    const paths = scratch([inactive], [previous]);

    const strict = check(paths);
    expect(strict.findings.map((f) => f.verdict)).toEqual(["superseded"]);
    expect(strict.exitCode).toBe(1);

    const lenient = check(paths, true);
    expect(lenient.findings.map((f) => f.verdict)).toEqual(["superseded"]);
    expect(lenient.exitCode).toBe(0);

    // Review closure NB4 (claims §5.167 §8). Exit 0 with a demotion behind it is not "the
    // same generation everywhere they meet" — the flag's whole subject is a tree that is
    // deliberately at another one — and a verdict line that hid it is the sentence somebody
    // quotes later as proof the tree was current.
    const verdict = formatReport(lenient, true);
    expect(verdict).toContain("1 capture stands at a superseded generation the indexes have RECORDED");
    expect(verdict).toContain("--superseded-ok");
    expect(verdict).not.toContain("the same generation everywhere they meet");
    // And the line is unchanged where the flag is on with nothing to demote.
    expect(formatReport(check(scratch([current], [current]), true), true))
      .toContain("the same generation everywhere they meet");

    // Half-recorded is not recorded: a generation whose active hash the index knows and
    // whose receded hash it does not was never split, so nobody chose it.
    const half = {
      ...inactive,
      documents: [[`${LIGHT}.json`, PRIOR], [`${LIGHT}-receded.json`, UNRECORDED]] as const,
    };
    const partial = check(scratch([inactive], [half]), true);
    expect(partial.findings.map((f) => f.verdict)).toEqual(["mismatch"]);
    expect(partial.exitCode).toBe(1);
  });

  it("recognizes a retired indexed generation without relying on the historical archive", () => {
    // Retirement leaves the old rows and their bytes in generations/, not superseded/.
    // Build both files in disposable storage; neither the canonical index nor its rows move.
    const previous: Cell = {
      ...inactive,
      documents: [[`${LIGHT}.json`, PRIOR], [`${LIGHT}-receded.json`, PRIOR_RECEDED]],
    };
    const paths = scratch([inactive], [previous]);
    const results = dirname(paths.matrixPath);
    const currentBytes = readFileSync(paths.matrixPath);
    const previousBytes = readFileSync(scratch([previous], []).matrixPath);
    writeFileSync(paths.matrixPath, JSON.stringify({ schemaVersion: 5, cells: [] }));
    writeFileSync(paths.supersededIndexPath, JSON.stringify({ byDocumentSha256: {} }));
    mkdirSync(join(results, "generations"));
    const generation = (cell: Cell, bytes: Buffer, status: "current" | "retired") => {
      const name = `${cell.documents[0]![1]}.json`;
      writeFileSync(join(results, "generations", name), bytes);
      return [name, {
        activeDocumentSha256: cell.documents[0]![1],
        documents: cell.documents.map(([file, sha256]) => ({
          path: `packages/calibration/profiles/${file}`, sha256,
        })),
        rowCount: 1, rowsByProfileKey: { [LIGHT]: 1 },
        bytes: bytes.length, sha256: createHash("sha256").update(bytes).digest("hex"), status,
      }] as const;
    };
    const [currentName, currentEntry] = generation(inactive, currentBytes, "current");
    const [retiredName, retiredEntry] = generation(previous, previousBytes, "retired");
    writeFileSync(join(results, "generations", "index.json"), JSON.stringify({
      schemaVersion: 1,
      files: { [currentName]: currentEntry, [retiredName]: retiredEntry },
      byDocumentSha256: {
        [SHIPPED]: [currentName], [RECEDED]: [currentName],
        [PRIOR]: [retiredName], [PRIOR_RECEDED]: [retiredName],
      },
      currentByProfile: { [LIGHT]: currentName },
    }));

    const strict = check(paths);
    expect(strict.findings.map((f) => f.verdict)).toEqual(["superseded"]);
    expect(strict.findings[0]?.row).toEqual([`${LIGHT}-receded.json ${RECEDED}`, `${LIGHT}.json ${SHIPPED}`]);
    expect(strict.exitCode).toBe(1);
    const lenient = check(paths, true);
    expect(lenient.findings.map((f) => f.verdict)).toEqual(["superseded"]);
    expect(lenient.exitCode).toBe(0);
    expect(formatReport(lenient, true)).toContain("demoted to a warning");

    // A mismatching capture naming only a CURRENT hash cannot borrow the retired
    // classification. It still names no recorded retired generation.
    writeFileSync(join(paths.tree, LIGHT, inactive.scene, "cell__webgpu.json"), JSON.stringify({
      renderer: "webgpu", sceneId: inactive.scene,
      capturePath: capturePath({ ...inactive, documents: [[`${LIGHT}.json`, SHIPPED]] }),
    }));
    const currentOnly = check(paths, true);
    expect(currentOnly.findings.map((f) => f.verdict)).toEqual(["mismatch"]);
    expect(currentOnly.exitCode).toBe(1);
  });

  it("requires the exact retired pair after a receded-only reseal at the same active hash", () => {
    // An active hash has two owners after resealing only the receded document: A/R1
    // is retired, A/R2 is current. Neither A alone nor A/R3 (assembled from two
    // retired entries) was ever a generation, even though every hash is indexed.
    const old = {
      ...inactive,
      documents: [[`${LIGHT}.json`, SHIPPED], [`${LIGHT}-receded.json`, PRIOR_RECEDED]] as const,
    };
    const unrelated: Cell = {
      ...inactive,
      documents: [[`${LIGHT}.json`, PRIOR], [`${LIGHT}-receded.json`, OTHER_RECEDED]],
    };
    const paths = scratch([inactive], [old]);
    const results = dirname(paths.matrixPath);
    const currentBytes = readFileSync(paths.matrixPath);
    const oldBytes = readFileSync(scratch([old], []).matrixPath);
    const unrelatedBytes = readFileSync(scratch([unrelated], []).matrixPath);
    writeFileSync(paths.matrixPath, JSON.stringify({ schemaVersion: 5, cells: [] }));
    writeFileSync(paths.supersededIndexPath, JSON.stringify({ byDocumentSha256: {} }));
    mkdirSync(join(results, "generations"));
    const indexed = (name: string, cell: Cell, bytes: Buffer, status: "current" | "retired") => {
      writeFileSync(join(results, "generations", name), bytes);
      return {
        activeDocumentSha256: cell.documents[0]![1],
        documents: cell.documents.map(([file, sha256]) => ({
          path: `packages/calibration/profiles/${file}`, sha256,
        })),
        rowCount: 1, rowsByProfileKey: { [cell.profile]: 1 },
        bytes: bytes.length, sha256: createHash("sha256").update(bytes).digest("hex"), status,
      };
    };
    const currentName = `${SHIPPED}-${RECEDED}.json`;
    const oldName = `${SHIPPED}.json`;
    const otherName = `${PRIOR}.json`;
    writeFileSync(join(results, "generations", "index.json"), JSON.stringify({
      schemaVersion: 1,
      files: {
        [currentName]: indexed(currentName, inactive, currentBytes, "current"),
        [oldName]: indexed(oldName, old, oldBytes, "retired"),
        [otherName]: indexed(otherName, unrelated, unrelatedBytes, "retired"),
      },
      byDocumentSha256: {
        [SHIPPED]: [currentName, oldName],
        [RECEDED]: [currentName],
        [PRIOR_RECEDED]: [oldName],
        [PRIOR]: [otherName],
        [OTHER_RECEDED]: [otherName],
      },
      currentByProfile: { [LIGHT]: currentName },
    }));

    const atCapture = (cell: Cell, verdict: "match" | "superseded" | "mismatch",
      strictExit: number, lenientExit: number) => {
      writeFileSync(join(paths.tree, LIGHT, inactive.scene, "cell__webgpu.json"), JSON.stringify({
        renderer: "webgpu", sceneId: inactive.scene, capturePath: capturePath(cell),
      }));
      const strict = check(paths);
      const lenient = check(paths, true);
      expect(strict.findings.map((f) => f.verdict)).toEqual([verdict]);
      expect(strict.exitCode).toBe(strictExit);
      expect(lenient.findings.map((f) => f.verdict)).toEqual([verdict]);
      expect(lenient.exitCode).toBe(lenientExit);
    };
    atCapture(old, "superseded", 1, 0);
    atCapture(inactive, "match", 0, 0);
    atCapture({ ...inactive, documents: [[`${LIGHT}.json`, SHIPPED]] }, "mismatch", 1, 1);
    atCapture({
      ...inactive,
      documents: [[`${LIGHT}.json`, SHIPPED], [`${LIGHT}-receded.json`, OTHER_RECEDED]],
    }, "mismatch", 1, 1);
  });

  it("exits 2 where only a FROZEN profile mismatches, and 1 as soon as a live one does", () => {
    // A macOS 26.5 row may not be re-read under contract X1, so a mismatch there is a
    // fact about the tree on this machine and not a fault a gate can clear. Given the
    // same exit code as a live mismatch it would make a merge gate un-passable for a
    // reason nobody is allowed to fix.
    const frozenRow: Cell = {
      profile: FROZEN, scene: "photo__rrect-md__rest", renderer: "webgpu",
      documents: [[`${FROZEN}.json`, SHIPPED]],
    };
    const frozenStale = { ...frozenRow, documents: [[`${FROZEN}.json`, UNRECORDED]] as const };

    const frozenOnly = check(scratch([frozenRow, current], [frozenStale, current]));
    expect(frozenOnly.exitCode).toBe(2);
    expect(formatReport(frozenOnly, false)).toContain("FROZEN");

    const live = { ...current, documents: [[`${LIGHT}.json`, UNRECORDED]] as const };
    expect(check(scratch([frozenRow, current], [frozenStale, live])).exitCode).toBe(1);

    // Review closure NB5 (claims §5.167 §8). The exit-2 class is a GENERATION difference
    // under a frozen key and nothing else. `live` was computed over the whole failing set,
    // so an UNREADABLE capture whose only company was a frozen key exited 2 — reporting a
    // fault anybody may clear (the tree is gitignored; delete the file and copy it again)
    // as one contract X1 forbids anyone to touch, which is how it stays in the tree.
    const frozenUnreadable = { ...frozenRow, sceneId: "photo__rrect-lg__rest" };
    const unreadable = check(scratch([frozenRow], [frozenUnreadable]));
    expect(unreadable.findings.map((f) => f.verdict)).toEqual(["unreadable"]);
    expect(unreadable.exitCode).toBe(1);

    // And a frozen generation mismatch standing beside it does not pull it back down to 2.
    const both = check(scratch(
      [frozenRow, { ...frozenRow, scene: "photo__rrect-sm__rest" }],
      [frozenUnreadable, { ...frozenStale, scene: "photo__rrect-sm__rest" }],
    ));
    expect(both.findings.map((f) => f.verdict).sort()).toEqual(["mismatch", "unreadable"]);
    expect(both.exitCode).toBe(1);
  });

  it("refuses a capture with no provenance and one whose directory disagrees with it", () => {
    // A tree is assembled by copying, and a copy can put a capture in the wrong place.
    // The directory name is what everything downstream keys on, so a capture that names
    // a different scene than the directory it sits in is refused rather than compared.
    const noDocuments = { ...current, documents: [] as const };
    expect(check(scratch([current], [noDocuments])).findings[0]?.note)
      .toContain("names no material profile document");

    const misfiled = { ...current, sceneId: "photo__rrect-lg__rest" };
    const report = check(scratch([current], [misfiled]));
    expect(report.findings[0]?.verdict).toBe("unreadable");
    expect(report.exitCode).toBe(1);
  });

  it("calls a cross-profile miscopy MISFILED, where the documents agree and the pose does not", () => {
    // Review closure NB2 (claims §5.167 §8). Every 2x profile is read at the 1x document
    // and every macOS 26.5 profile at the one light document, so a capture copied from one
    // profile's directory into another's names exactly the documents the row names. The
    // generation compare reads it as a MATCH and the cell is then measured against pixels
    // drawn at a different scale — the one shape of stale tree that passed.
    const row: Cell = {
      profile: LIGHT_2X, scene: "photo__rrect-md__rest", renderer: "webgpu",
      documents: [[`${LIGHT}.json`, SHIPPED]],
    };
    const copiedFrom1x: Cell = { ...row, pose: poseFor(LIGHT) };
    const report = check(scratch([row], [copiedFrom1x]));

    expect(report.findings.map((f) => f.verdict)).toEqual(["misfiled"]);
    expect(report.exitCode).toBe(1);
    // The documents are identical on both sides, which is the whole point: without the
    // pose clauses this capture is indistinguishable from the one the row was read off.
    expect(report.findings[0]?.capture).toEqual(report.findings[0]?.row);
    expect(report.findings[0]?.note).toContain("deviceScaleFactor=1 against the row's deviceScaleFactor=2");
    const text = formatReport(report, false);
    expect(text).toContain("MISFILED");
    expect(text).toContain("misfiled 1");
  });

  it("exits 1 on a misfiled capture under a FROZEN key, where a generation mismatch exits 2", () => {
    // The exit-2 class is a GENERATION difference nobody may clear: contract X1 forbids
    // re-reading a macOS 26.5 row. A capture sitting in a directory it does not belong in
    // is a fault in the copy and the tree is gitignored, so anybody may clear it — and a
    // gate that reported it as unclearable would leave it there.
    const row: Cell = {
      profile: FROZEN_RT, scene: "photo__rrect-md__rest", renderer: "webgpu",
      documents: [[`${FROZEN}.json`, SHIPPED]],
    };
    const copiedFromStandard: Cell = { ...row, pose: poseFor(FROZEN) };
    const report = check(scratch([row], [copiedFromStandard]));
    expect(report.findings.map((f) => f.verdict)).toEqual(["misfiled"]);
    expect(report.exitCode).toBe(1);
    expect(report.findings[0]?.note).toContain("accessibility=browser-preferences");
  });

  it("reports a row whose own string carries no pose clause rather than passing it", () => {
    // Two strings that both say nothing about the scale agree on nothing. If the capture
    // format ever drops a clause, the checker says so instead of reading silence as a match.
    const row: Cell = { ...current, poseless: true };
    const report = check(scratch([row], [current]));
    expect(report.findings.map((f) => f.verdict)).toEqual(["misfiled"]);
    expect(report.findings[0]?.note).toContain("(absent)");
    expect(report.exitCode).toBe(1);
  });

  it("reports a capture with no row and a row with no capture without failing either", () => {
    // The bed is ragged on purpose: probe cells are read at some profiles and not others,
    // and instrument refusals dropped rows whose captures remain. Neither direction is a
    // generation that drifted.
    const probe: Cell = { ...current, scene: "checkerboard-64__rrect-sm__rest" };
    const report = check(scratch([current, inactive], [current, probe]));
    expect(report.exitCode).toBe(0);
    expect(report.findings.filter((f) => f.verdict === "no-row").map((f) => f.scene))
      .toEqual(["checkerboard-64__rrect-sm__rest"]);
    expect([...report.rowsWithoutCapture.values()].flat()).toEqual(["photo__rrect-md__inactive"]);
  });

  it("reports a tree path that is a file, and a dangling symlink inside one, with the path", () => {
    // Review closure NB8 (claims §5.167 §8). Both threw out of the fs call and took the run
    // with them. A tree assembled by copying is exactly where a dangling link comes from,
    // and `VITREA_WEB_CAPTURES` at a file is a typo somebody wants told back to them — so
    // each is reported as unreadable WITH its path, and neither is skipped like an absent
    // tree: somebody who named a path meant to check a tree.
    const paths = scratch([current], [current]);
    const asFile = checkCaptureTree({ ...paths, tree: paths.matrixPath, supersededOk: false });
    expect(asFile.treePresent).toBe(true);
    expect(asFile.findings.map((f) => f.verdict)).toEqual(["unreadable"]);
    expect(asFile.findings[0]?.note).toContain(paths.matrixPath);
    expect(asFile.findings[0]?.note).toContain("is not a directory");
    expect(asFile.exitCode).toBe(1);

    symlinkSync(join(paths.tree, "nowhere"), join(paths.tree, "apple-macos-27.0-1x-dangling"));
    const dangling = check(paths);
    expect(dangling.findings.map((f) => f.verdict).sort()).toEqual(["match", "unreadable"]);
    expect(dangling.findings.find((f) => f.verdict === "unreadable")?.note)
      .toContain("apple-macos-27.0-1x-dangling");
    expect(dangling.exitCode).toBe(1);
  });

  it("parses the committed matrix and superseded index, as the merge gate will", () => {
    // The two real files, through the real code path, over a tree that is present and
    // empty: a checker whose first contact with schema 5 and the live index is a merge
    // is a checker that discovers a parse error at the worst possible moment. The
    // committed matrix is expected to hold exactly ONE generation per profile and
    // renderer — that is what the split leaves behind — and it is asserted rather than
    // assumed, because a second generation in the working file would make every
    // comparison above ambiguous without saying so.
    const tree = join(mkdtempSync(join(tmpdir(), "w32-g0b-empty-")), "web-captures");
    mkdirSync(tree, { recursive: true });
    const report = checkCaptureTree({
      tree,
      matrixPath: resolve(PACKAGE_ROOT, "results", "matrix.json"),
      supersededIndexPath: resolve(PACKAGE_ROOT, "results", "superseded", "index.json"),
      supersededOk: false,
    });
    expect(report.treePresent).toBe(true);
    expect(report.findings).toHaveLength(0);
    expect(report.exitCode).toBe(0);
    expect(report.matrixGenerations.size).toBeGreaterThan(0);
    for (const [key, generations] of report.matrixGenerations) {
      expect(generations, key).toHaveLength(1);
    }
  });
});

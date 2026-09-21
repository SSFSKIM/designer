import { mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
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

const LIGHT = "apple-macos-27.0-1x-light-standard-glass0.5";
const FROZEN = "apple-macos-26.5-1x-light-standard";

const capturePath = (documents: readonly (readonly [string, string])[]): string =>
  `playwright element screenshot of #stage, viewport=320x200, ${documents
    .map(([clause, hash], index) =>
      `${index === 0 ? "materialProfile" : "recededProfile"}=packages/calibration/profiles/${clause} `
      + `sha256:${hash}`)
    .join(", ")}`;

interface Cell {
  readonly profile: string;
  readonly scene: string;
  readonly renderer: string;
  readonly documents: readonly (readonly [string, string])[];
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
        capturePath: capturePath(cell.documents),
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
        web: { renderer: cell.renderer, capturePath: capturePath(cell.documents) },
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

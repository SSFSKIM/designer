/**
 * The canonical capture tree against the working matrix — are they the same generation?
 *
 *   pnpm --filter @vitrea/calibration run check-capture-tree
 *   VITREA_WEB_CAPTURES=<a tree> pnpm --filter @vitrea/calibration run check-capture-tree
 *   … run check-capture-tree -- --superseded-ok
 *
 * `CLAUDE.md` has said since W29 that the canonical `packages/calibration/web-captures/`
 * "lives on the capture machine and is what the sheets and the demo fixture are copied
 * from". That sentence was false from W29 to W31 and nobody noticed, because **nothing
 * reads the tree except a person making a sheet**: every read ran in an agent worktree,
 * captures are gitignored, a worktree inherits none, and the worktree was removed after
 * merge — so the pixels each generation of rows was measured off were deleted as the rows
 * landed (W31 charter Surprises; claims §5.161 §2; tracker, "The canonical `web-captures/`
 * tree held no current generation"). W31 made the copy a step in a charter. A step in a
 * charter is not a rule, and the next wave that reads in a worktree and forgets it puts the
 * tree back where it was. This is the rule (claims §5.167; W31 Deferred item 12).
 *
 * ## What it compares, and why that IS the generation
 *
 * A cell's key carries, inside its own `capturePath`, the material profile documents the
 * capture was driven from and each document's twelve-hex content hash — the ACTIVE document
 * (`--material-profile`) and, on a cell posed inactive, the RECEDED document
 * (`--receded-profile`), which is a difference over the active document of its own scheme.
 * That set of (document, hash) pairs is what the split names a generation by
 * (`results/2026-09-20-w30-g1-split/split-generation.py`), and it is written into the
 * capture's own `cell__<renderer>.json` as well as into the row. So the check is a file walk
 * and a string compare: for every capture in the tree, the documents it names against the
 * documents named by the row the working matrix holds for that profile, renderer and scene.
 * No browser, no capture, no metric — which is what makes it runnable at every merge.
 *
 * The idiom is W31 G4's `sheets.ts`, generalised. That script asserted per cell that a
 * capture named the SHIPPED document bytes before it would photograph it; this asserts
 * per cell that a capture names the bytes the ROW beside it was read at, which is the same
 * question asked of the whole tree instead of of twenty sheets, and does not assume that
 * the matrix's current generation and the shipped documents agree.
 *
 * ## What it cannot see, said here rather than discovered later
 *
 * **Two captures at the same document bytes.** The known macOS 26.5 divergence is exactly
 * that shape: the frozen documents have not moved since W29, and the tree's files are dated
 * 2026-09-10 while the rows were measured 2026-09-11, so two cells of
 * `photo__glass-over-glass__rest` on the two light profiles disagree on `interiorMeanWeb`
 * by 2.8e-03 and 2.5e-03 against pixels this checker reads as MATCHING. A document-hash
 * compare cannot tell a re-capture at unmoved bytes from the capture the row was read off.
 * The instrument that can is a `compare --skip-capture` re-derivation of the metrics from
 * the tree's own PNGs, which is how W31 G0 found it — minutes of CPU rather than a file
 * walk, and a different tool. That remainder is a tracker entry; this one closes the
 * generation half and says so.
 *
 * **Anything outside the documents and the pose.** An engine version, a GPU adapter or a
 * scenes file that moved between the capture and the row is neither a document hash nor a
 * pose clause and is not read here. The scale, the scheme and the accessibility policy ARE
 * read, since the review closure: they are on the same string and a miscopy across profiles
 * moves them while leaving the documents alone (NB2; claims §5.167 §8).
 *
 * ## The verdicts, and why they are not all the same colour
 *
 * - **absent tree** — exit 0 and one line. The tree is gitignored and lives on the capture
 *   machine; a checker that fails on every other machine is a checker somebody disables.
 * - **superseded** — a capture whose documents are not the row's, but whose every hash is in
 *   `results/superseded/index.json`. That is a tree deliberately left at a generation the
 *   split has already recorded — a gate mid-read, or a sheet of a superseded generation made
 *   on purpose. Stale by CHOICE, and nameable; `--superseded-ok` demotes it to a warning.
 *   Stale by ACCIDENT — a generation nothing recorded — is never anything but a failure, and
 *   the difference between the two is the whole reason the flag exists rather than a
 *   blanket tolerance.
 * - **misfiled** — a capture whose `deviceScaleFactor`, `colorScheme` or `accessibility`
 *   clause is not the row's. The documents can agree here and usually do: every macOS 26.5
 *   profile is keyed to the one light or dark document and a macOS 27 accessibility profile
 *   to the standard pair, so a cross-profile miscopy is invisible to a document compare and
 *   is the one shape of stale tree that reads as a MATCH. It exits **1** under a frozen key
 *   as well as a live one — a capture sitting in a directory it does not belong in is a
 *   fault in the copy, not a row anybody is forbidden to re-read.
 * - **frozen** — a GENERATION difference under a macOS 26.5 key exits **2** rather than 1.
 *   Those rows are frozen evidence under contract X1 and no wave may re-read them, so it is
 *   a fact about the tree on this machine and not a fault a gate can clear; reporting it
 *   with the same exit code as a live mismatch would make a merge gate un-passable for a
 *   reason nobody is allowed to fix. It is the exit-2 class on its own: a live mismatch, a
 *   misfiled capture and an unreadable one all exit 1 whatever key they sit under, because
 *   each of those is a fault in the tree rather than a reading of a row (NB5).
 * - **a capture with no row** is reported and does not fail. The bed is ragged on purpose:
 *   probe cells are read at some profiles and not others, and the contour instrument's
 *   refusals dropped rows whose captures remain (tracker). A capture without a row is
 *   evidence of a read that happened, not of a generation that drifted.
 * - **a row with no capture** is reported and does not fail, for the same reason the absent
 *   tree does not: a partial tree is the normal state of a machine that has run one gate.
 */
import { loadCurrentRows } from "../src/matrix-store";
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { resolve, sep } from "node:path";

const PACKAGE = resolve(import.meta.dirname, "..");
const MATRIX = resolve(PACKAGE, "results", "matrix.json");
const SUPERSEDED_INDEX = resolve(PACKAGE, "results", "superseded", "index.json");
const CAPTURES = process.env["VITREA_WEB_CAPTURES"] ?? resolve(PACKAGE, "web-captures");

/** A macOS 26.5 key is frozen evidence: its rows may not be re-read (contract X1). */
const FROZEN = /^apple-macos-26\.5-/;

/**
 * The document clauses a `capturePath` carries. `sheets.ts`'s pattern, widened by
 * nothing: the two clause names the capture driver writes, the document's repo-relative
 * path, and its twelve-hex content hash.
 */
const CLAUSE = /(?:materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})/g;

/**
 * The clauses that say which PROFILE a capture was taken at, beside the ones that say
 * which material it drew. A document compare alone reads a cross-profile miscopy as a
 * MATCH, because a document is shared across profiles by design: all six macOS 26.5
 * profiles are keyed to the one light or dark document, and a macOS 27 accessibility
 * profile is read at the standard pair. So a 1x capture dropped into the 2x directory, or
 * a reduced-transparency capture into the standard one, names exactly the documents the
 * row names and is compared cell for cell against pixels drawn at a different scale or a
 * different policy — which is the shape of every defect this checker exists for, arriving
 * by the one route it could not see (review closure NB2; claims §5.167 §8).
 *
 * Each value runs to the next `, <name>=` clause rather than to the next comma, because
 * `accessibility=` carries spaces and parentheses:
 * `accessibility=reducedTransparency+increasedContrast (others explicitly off)`.
 */
const POSE = ["deviceScaleFactor", "colorScheme", "accessibility"].map(
  (name) => [name, new RegExp(`${name}=(.*?)(?=,\\s*[A-Za-z][A-Za-z0-9]*=|$)`)] as const);

/** `<name>=<value>` for each pose clause, or `<name>=(absent)` where the string has none. */
function poseOf(capturePath: string): readonly string[] {
  return POSE.map(([name, pattern]) => `${name}=${pattern.exec(capturePath)?.[1] ?? "(absent)"}`);
}

/** Sorted `<file name> <hash>` pairs — a generation, in the form both sides are compared in. */
function documentsOf(capturePath: string): readonly string[] {
  return [...capturePath.matchAll(CLAUSE)]
    .map((match) => `${(match[1] ?? "").split("/").pop() ?? ""} ${match[2] ?? ""}`)
    .sort();
}

interface Row {
  readonly documents: readonly string[];
  readonly pose: readonly string[];
}

interface CaptureMeta {
  readonly capturePath: string;
  readonly renderer?: string;
  readonly sceneId?: string;
}

const cellKey = (profile: string, renderer: string, scene: string): string =>
  `${profile}\0${renderer}\0${scene}`;

interface TreeEntry {
  readonly profile: string;
  readonly scene: string;
  readonly renderer: string;
  readonly path: string;
}

/**
 * Every `<profile>/<scene>/cell__<renderer>.json` in a tree, in a stable order, beside the
 * paths the walk could not read at all. A dangling symlink — a tree assembled by copying
 * one gate's captures over another's, or a `cp -s` that outlived its source — threw out of
 * `statSync` and took the whole run with it. It is a fault in how the tree was assembled,
 * which is this checker's subject, so it is reported with its path like any other
 * unreadable capture rather than as a stack trace (review closure NB8; claims §5.167 §8).
 */
function walk(tree: string): { cells: TreeEntry[]; unreadable: { path: string; note: string }[] } {
  const cells: TreeEntry[] = [];
  const unreadable: { path: string; note: string }[] = [];
  const dirs = (at: string): string[] => {
    const out: string[] = [];
    for (const name of readdirSync(at).sort()) {
      try {
        if (statSync(resolve(at, name)).isDirectory()) out.push(name);
      } catch (error) {
        unreadable.push({ path: resolve(at, name), note: `cannot be read: ${String(error)}` });
      }
    }
    return out;
  };
  for (const profile of dirs(tree)) {
    for (const scene of dirs(resolve(tree, profile))) {
      const sceneDir = resolve(tree, profile, scene);
      for (const file of readdirSync(sceneDir).sort()) {
        const renderer = /^cell__(.+)\.json$/.exec(file)?.[1];
        if (renderer !== undefined) cells.push({ profile, scene, renderer, path: resolve(sceneDir, file) });
      }
    }
  }
  return { cells, unreadable };
}

type Verdict = "match" | "superseded" | "mismatch" | "misfiled" | "no-row" | "unreadable";

interface Finding {
  readonly profile: string;
  readonly scene: string;
  readonly renderer: string;
  readonly verdict: Verdict;
  readonly capture: readonly string[];
  readonly row: readonly string[];
  readonly note?: string;
}

export interface Report {
  readonly treePresent: boolean;
  readonly tree: string;
  readonly findings: readonly Finding[];
  /** `<profile>\0<renderer>` → the scenes whose row the tree carries no capture for. */
  readonly rowsWithoutCapture: ReadonlyMap<string, readonly string[]>;
  /** `<profile>\0<renderer>` → every generation the working matrix's rows name. */
  readonly matrixGenerations: ReadonlyMap<string, readonly (readonly string[])[]>;
  readonly exitCode: number;
}

export function checkCaptureTree(options: {
  readonly tree: string;
  readonly matrixPath: string;
  readonly supersededIndexPath: string;
  readonly supersededOk: boolean;
}): Report {
  const empty = new Map<string, never[]>();
  if (!existsSync(options.tree)) {
    return {
      treePresent: false, tree: options.tree, findings: [],
      rowsWithoutCapture: empty, matrixGenerations: empty, exitCode: 0,
    };
  }

  // A `VITREA_WEB_CAPTURES` pointing at a FILE exists and cannot be walked: `readdirSync`
  // threw ENOTDIR out of the run. The path is what the reader needs, so it is reported as
  // unreadable and fails, rather than skipped like an absent tree — somebody who named a
  // path meant to check a tree (review closure NB8; claims §5.167 §8).
  if (!statSync(options.tree).isDirectory()) {
    return {
      treePresent: true, tree: options.tree, rowsWithoutCapture: empty,
      matrixGenerations: empty, exitCode: 1,
      findings: [{
        profile: "(the tree)", scene: "", renderer: "-", verdict: "unreadable",
        capture: [], row: [], note: `${options.tree} is not a directory`,
      }],
    };
  }

  const matrix = { cells: loadCurrentRows({ matrixPath: options.matrixPath }) };
  const rows = new Map<string, Row>();
  const generations = new Map<string, string[][]>();
  for (const cell of matrix.cells) {
    const documents = documentsOf(cell.key.web.capturePath);
    rows.set(
      cellKey(cell.key.profileKey, cell.key.web.renderer, cell.key.sceneId),
      { documents, pose: poseOf(cell.key.web.capturePath) },
    );
    const bucket = generations.get(cellKey(cell.key.profileKey, cell.key.web.renderer, "")) ?? [];
    if (!bucket.some((seen) => seen.join("|") === documents.join("|"))) bucket.push([...documents]);
    generations.set(cellKey(cell.key.profileKey, cell.key.web.renderer, ""), bucket);
  }

  // Every document hash any superseded generation names — active and receded alike. The
  // index is the lookup by construction; a file name is never parsed (the split's rule).
  const supersededHashes = new Set<string>(
    existsSync(options.supersededIndexPath)
      ? Object.keys((JSON.parse(readFileSync(options.supersededIndexPath, "utf8")) as {
          byDocumentSha256?: Record<string, string>;
        }).byDocumentSha256 ?? {})
      : [],
  );

  const findings: Finding[] = [];
  const seen = new Set<string>();
  const tree = walk(options.tree);
  for (const entry of tree.unreadable) {
    const [profile = "(the tree)", ...rest] = entry.path.slice(options.tree.length + 1).split(sep);
    findings.push({
      profile, scene: rest.join("/"), renderer: "-", verdict: "unreadable",
      capture: [], row: [], note: `${entry.path} ${entry.note}`,
    });
  }
  for (const capture of tree.cells) {
    const key = cellKey(capture.profile, capture.renderer, capture.scene);
    seen.add(key);
    let meta: CaptureMeta;
    try {
      meta = JSON.parse(readFileSync(capture.path, "utf8")) as CaptureMeta;
    } catch (error) {
      findings.push({
        ...capture, verdict: "unreadable", capture: [], row: [],
        note: `cell__${capture.renderer}.json does not parse: ${String(error)}`,
      });
      continue;
    }
    const named = documentsOf(meta.capturePath ?? "");
    // A capture naming no document has no provenance at all, which is worse than naming
    // the wrong one: nothing can ever place it in a generation. `sheets.ts` refuses it too.
    if (named.length === 0) {
      findings.push({
        ...capture, verdict: "unreadable", capture: [], row: [],
        note: "the capture names no material profile document",
      });
      continue;
    }
    // A tree assembled by copying is a tree whose directory names can disagree with the
    // files inside it, and the directory name is what everything downstream keys on.
    if (meta.sceneId !== undefined && meta.sceneId !== capture.scene) {
      findings.push({
        ...capture, verdict: "unreadable", capture: named, row: [],
        note: `the capture names scene ${meta.sceneId} and sits in ${capture.scene}`,
      });
      continue;
    }
    if (meta.renderer !== undefined && meta.renderer !== capture.renderer) {
      findings.push({
        ...capture, verdict: "unreadable", capture: named, row: [],
        note: `the capture names renderer ${meta.renderer} and is cell__${capture.renderer}.json`,
      });
      continue;
    }
    const row = rows.get(key);
    if (row === undefined) {
      findings.push({ ...capture, verdict: "no-row", capture: named, row: [] });
      continue;
    }
    // Before the documents, because a miscopy across profiles agrees on them: the scale,
    // the scheme and the accessibility policy the two strings name have to be the same
    // pose, or the comparison below is between a row and pixels drawn at another one.
    const pose = poseOf(meta.capturePath ?? "");
    // A clause the ROW's own string does not carry is reported rather than passed: two
    // strings that both say nothing about the scale agree on nothing, and a checker that
    // reads that as a match is answering a question it never asked.
    const disagreeing = pose.flatMap((clause, index) =>
      clause === row.pose[index] && !clause.endsWith("=(absent)")
        ? []
        : [`${clause} against the row's ${row.pose[index] ?? "(no clause)"}`]);
    if (disagreeing.length > 0) {
      findings.push({
        ...capture, verdict: "misfiled", capture: named, row: row.documents,
        note: `the capture is posed ${disagreeing.join("; ")}`,
      });
      continue;
    }
    if (named.join("|") === row.documents.join("|")) {
      findings.push({ ...capture, verdict: "match", capture: named, row: row.documents });
      continue;
    }
    const everyHashRecorded = named.every((entry) => supersededHashes.has(entry.split(" ")[1] ?? ""));
    findings.push({
      ...capture,
      verdict: everyHashRecorded ? "superseded" : "mismatch",
      capture: named,
      row: row.documents,
    });
  }

  const rowsWithoutCapture = new Map<string, string[]>();
  for (const [key] of rows) {
    if (seen.has(key)) continue;
    const [profile = "", renderer = "", scene = ""] = key.split("\0");
    // Only for profiles the tree actually carries: a tree holding one gate's read is not
    // missing the eleven profiles it was never asked for.
    if (!existsSync(resolve(options.tree, profile))) continue;
    const bucket = rowsWithoutCapture.get(cellKey(profile, renderer, "")) ?? [];
    bucket.push(scene);
    rowsWithoutCapture.set(cellKey(profile, renderer, ""), bucket);
  }

  const failing = findings.filter(
    (finding) =>
      finding.verdict === "mismatch"
      || finding.verdict === "misfiled"
      || finding.verdict === "unreadable"
      || (finding.verdict === "superseded" && !options.supersededOk),
  );
  // Exit 2 is a GENERATION difference under a frozen key and nothing else. Those rows may
  // not be re-read under contract X1, so the difference is a fact about the tree on this
  // machine rather than a fault a gate can clear — which is the entire argument for a
  // second exit code. An unreadable capture, or one misfiled into a directory it does not
  // belong in, is a fault in how the tree was ASSEMBLED: the tree is gitignored and anybody
  // may delete or re-copy a file in it, and X1 has nothing to say about doing so. Computing
  // this over the whole failing set let a frozen key downgrade those to exit 2, which
  // reported a clearable fault as unclearable and left it in the tree (review closure NB5;
  // claims §5.167 §8).
  const unclearable = (finding: Finding): boolean =>
    (finding.verdict === "mismatch" || finding.verdict === "superseded")
    && FROZEN.test(finding.profile);
  return {
    treePresent: true,
    tree: options.tree,
    findings,
    rowsWithoutCapture,
    matrixGenerations: generations,
    exitCode: failing.length === 0 ? 0 : failing.every(unclearable) ? 2 : 1,
  };
}

export function formatReport(report: Report, supersededOk: boolean): string {
  if (!report.treePresent) return `no capture tree at ${report.tree}; skipped`;

  const out: string[] = [];
  out.push("== the canonical capture tree against the working matrix (W32 G0b; claims §5.167) ==");
  out.push(`  tree              ${report.tree}`);
  out.push(`  --superseded-ok   ${supersededOk ? "on — a recorded superseded generation warns" : "off"}`);
  out.push("");

  const profiles = [...new Set(report.findings.map((finding) => finding.profile))].sort();
  for (const profile of profiles) {
    out.push(`  ${profile}${FROZEN.test(profile) ? "   [FROZEN — macOS 26.5, contract X1]" : ""}`);
    const renderers = [...new Set(
      report.findings.filter((finding) => finding.profile === profile).map((finding) => finding.renderer),
    )].sort();
    for (const renderer of renderers) {
      const mine = report.findings.filter(
        (finding) => finding.profile === profile && finding.renderer === renderer);
      const count = (verdict: Verdict): number => mine.filter((f) => f.verdict === verdict).length;
      const missing = report.rowsWithoutCapture.get(cellKey(profile, renderer, "")) ?? [];
      out.push(
        `    ${renderer.padEnd(7)} captures ${String(mine.length).padStart(4)}`
        + `  match ${String(count("match")).padStart(4)}`
        + `  mismatch ${String(count("mismatch")).padStart(3)}`
        + `  misfiled ${String(count("misfiled")).padStart(3)}`
        + `  superseded ${String(count("superseded")).padStart(3)}`
        + `  unreadable ${String(count("unreadable")).padStart(3)}`
        + `  no-row ${String(count("no-row")).padStart(3)}`
        + `  rows-with-no-capture ${String(missing.length).padStart(4)}`,
      );
      const named = report.matrixGenerations.get(cellKey(profile, renderer, "")) ?? [];
      for (const generation of named) {
        out.push(`            matrix ${named.length > 1 ? "generation (of several!)" : "generation"}`
          + `: ${generation.join(" + ")}`);
      }
      for (const finding of mine) {
        if (finding.verdict === "match" || finding.verdict === "no-row") continue;
        out.push(`            ${finding.verdict.toUpperCase()}  ${finding.scene}`);
        if (finding.note !== undefined) out.push(`                ${finding.note}`);
        if (finding.capture.length > 0) out.push(`                capture ${finding.capture.join(" + ")}`);
        if (finding.row.length > 0) out.push(`                row     ${finding.row.join(" + ")}`);
      }
      for (const scene of mine.filter((f) => f.verdict === "no-row").map((f) => f.scene)) {
        out.push(`            no row for this capture: ${scene}`);
      }
      for (const scene of missing) out.push(`            no capture for this row: ${scene}`);
    }
  }

  const total = (verdict: Verdict): number => report.findings.filter((f) => f.verdict === verdict).length;
  out.push("");
  out.push(`  totals   captures ${report.findings.length}  match ${total("match")}`
    + `  mismatch ${total("mismatch")}  misfiled ${total("misfiled")}`
    + `  superseded ${total("superseded")}`
    + `  unreadable ${total("unreadable")}  no-row ${total("no-row")}`);
  // Exit 0 under `--superseded-ok` with a demotion behind it is not "the same generation
  // everywhere they meet" — the flag's whole subject is a tree that is deliberately at
  // another one, and a verdict line that hides the demotion is the sentence somebody quotes
  // later as proof the tree was current (review closure NB4; claims §5.167 §8).
  const demoted = supersededOk ? total("superseded") : 0;
  out.push(
    report.exitCode === 0 && demoted > 0
      ? `  VERDICT  ${demoted} capture${demoted === 1 ? "" : "s"} stand`
        + `${demoted === 1 ? "s" : ""} at a superseded generation the split has RECORDED,`
        + " demoted to a warning by --superseded-ok (exit 0). Every other capture names the"
        + " generation its row was read at."
      : report.exitCode === 0
        ? "  VERDICT  the tree and the working matrix name the same generation everywhere they meet."
        : report.exitCode === 2
          ? "  VERDICT  generation mismatches on FROZEN profiles only (exit 2). Those rows may"
            + " not be re-read under contract X1, so this is a fact about the tree on this machine."
          : "  VERDICT  at least one capture is misfiled, unreadable, or names a generation its"
            + " row does not (exit 1).",
  );
  return out.join("\n");
}

if (import.meta.filename === process.argv[1]) {
  const supersededOk = process.argv.includes("--superseded-ok");
  const report = checkCaptureTree({
    tree: CAPTURES,
    matrixPath: MATRIX,
    supersededIndexPath: SUPERSEDED_INDEX,
    supersededOk,
  });
  process.stdout.write(`${formatReport(report, supersededOk)}\n`);
  process.exitCode = report.exitCode;
}

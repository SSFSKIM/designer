/**
 * W31 G0 review closure (2026-09-21) — the non-blocking findings that are
 * numbers, recomputed rather than transcribed (claims §5.161 §11, findings N2
 * through N6 and N11). Beside `cut.md` / `cut.json`; nothing either wrote is
 * rewritten.
 *
 *   npx tsx results/2026-09-21-w31-g0-chroma-cut/closure-readings.ts
 *
 * Every reading here comes from `cut.json`, which is committed evidence, except
 * the one in §N3 — the invariant twin's ratio needs `interiorOklabLSdDev*`,
 * which the instrument exports on the matrix row and `cut.json` does not
 * distil. That one reads the scratch matrix if it is still on the machine
 * (`VITREA_G0_SCRATCH_MATRIX`, defaulting to `scratch-matrix.json` beside this
 * file) and otherwise reports what it could not read. It writes the values it
 * found into `closure-readings.json`, so the twin's reading survives a scratch
 * tree that is gitignored and already once disappeared (§2, the Surprise).
 *
 * **The declared bed**, wherever "the bed" appears below, is §7 (b)'s: the
 * untinted `photo` cells of the four macOS 27 standard profiles, both scales,
 * `calibration` + `validation`. Several of §3's ranges are over ALL sets, which
 * is finding N4, so both are printed wherever they differ.
 */
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";

const HERE = import.meta.dirname;

/**
 * N2's section is written out a second time as `blurred-reference-closure.txt`,
 * beside `blurred-reference.txt` — the file it corrects — so that a reader of
 * ratio (iii) finds the level correction without having to know this script
 * exists. Same text, same numbers.
 */
const n2: string[] = [];
const sayN2 = (line = ""): void => {
  n2.push(line);
  console.log(line);
};

interface CutRow {
  readonly backdrop: string;
  readonly component: string;
  readonly pose: string;
  readonly span: number;
  readonly scheme: "light" | "dark";
  readonly scale: number;
  readonly os: string;
  readonly a11y: string;
  readonly tinted: boolean;
  readonly active: boolean;
  readonly set: string;
  readonly tier: "texture" | "dom";
  readonly ratioI_native: number;
  readonly ratioI_web: number;
  readonly ratioII_native: number;
  readonly ratioII_web: number;
  readonly ratioIII_native: number | null;
  readonly ratioIII_web: number | null;
  readonly interiorMeanNative: number;
  readonly interiorMeanWeb: number;
  readonly interiorMeanBackdrop: number;
}

const rows = (
  JSON.parse(readFileSync(resolve(HERE, "cut.json"), "utf8")) as { rows: readonly CutRow[] }
).rows;

const DECLARED_SETS = new Set(["calibration", "validation"]);

function photoCells(options: {
  tier?: "texture" | "dom";
  declaredBedOnly: boolean;
}): readonly CutRow[] {
  return rows.filter(
    (row) =>
      row.os === "27" &&
      row.a11y === "standard" &&
      row.backdrop === "photo" &&
      !row.tinted &&
      (options.tier === undefined || row.tier === options.tier) &&
      (!options.declaredBedOnly || DECLARED_SETS.has(row.set)),
  );
}

const sorted = (values: readonly number[]): readonly number[] => [...values].sort((a, b) => a - b);
const range = (values: readonly number[]): string => {
  const s = sorted(values);
  return `${(s[0] ?? Number.NaN).toFixed(4)}–${(s[s.length - 1] ?? Number.NaN).toFixed(4)}`;
};
const median = (values: readonly number[]): number => {
  const s = sorted(values);
  return s.length % 2 === 1
    ? (s[(s.length - 1) / 2] ?? Number.NaN)
    : ((s[s.length / 2 - 1] ?? Number.NaN) + (s[s.length / 2] ?? Number.NaN)) / 2;
};

const findings: Record<string, unknown> = {};

// ---------------------------------------------------------------------------
sayN2("== N2 — ratio (iii) carries a level confound, and correcting it reverses §3's light reading ==\n");
sayN2("  The blurred reference is the BACKDROP blurred, so it sits at the backdrop's");
sayN2("  level while the side sits at its own. OKLab chroma scales as Y^(1/3) under a");
sayN2("  luma-only change, so the comparison has to divide by (Y_side/Y_backdrop)^(1/3)");
sayN2("  before it says anything about how much chroma the body kept.\n");
{
  const readings: Record<string, unknown> = {};
  for (const scheme of ["light", "dark"] as const) {
    const cells = photoCells({ tier: "texture", declaredBedOnly: false }).filter(
      (row) => row.scheme === scheme && row.ratioIII_native !== null,
    );
    const raw = cells.map((row) => row.ratioIII_native ?? Number.NaN);
    const corrected = cells.map(
      (row) =>
        (row.ratioIII_native ?? Number.NaN) /
        (row.interiorMeanNative / row.interiorMeanBackdrop) ** (1 / 3),
    );
    sayN2(
      `  ${scheme.padEnd(5)} native, n=${String(cells.length)}:  as recorded ${range(raw)}   level-corrected ${range(corrected)}`,
    );
    readings[scheme] = { cells: cells.length, raw: sorted(raw), corrected: sorted(corrected) };
  }
  const light = photoCells({ tier: "texture", declaredBedOnly: false }).filter(
    (row) => row.scheme === "light" && row.ratioIII_native !== null,
  );
  const lightCorrected = light.map(
    (row) =>
      (row.ratioIII_native ?? Number.NaN) /
      (row.interiorMeanNative / row.interiorMeanBackdrop) ** (1 / 3),
  );
  const s = sorted(lightCorrected);
  sayN2(
    `\n  So §3's "the LIGHT native body very nearly IS such a blur" is an artefact of the level:\n` +
      `  corrected, Apple's light body REMOVES ${((1 - (s[s.length - 1] ?? 0)) * 100).toFixed(0)}–${((1 - (s[0] ?? 0)) * 100).toFixed(0)} % of the chroma a matched\n` +
      `  blur would leave. The DARK reading is strengthened rather than reversed.`,
  );
  findings["N2"] = readings;
}

// ---------------------------------------------------------------------------
console.log("\n\n== N4 — §3's ratio (ii) columns are over ALL SETS; its medians are the declared bed ==\n");
{
  const table: unknown[] = [];
  for (const scheme of ["light", "dark"] as const) {
    for (const active of [true, false] as const) {
      const all = photoCells({ tier: "texture", declaredBedOnly: false }).filter(
        (row) => row.scheme === scheme && row.active === active,
      );
      const bed = photoCells({ tier: "texture", declaredBedOnly: true }).filter(
        (row) => row.scheme === scheme && row.active === active,
      );
      const label = `${scheme} ${active ? "active" : "inactive"}`;
      console.log(
        `  ${label.padEnd(16)} declared bed (n=${String(bed.length)}): native ${range(bed.map((r) => r.ratioII_native))}  web ${range(bed.map((r) => r.ratioII_web))}`,
      );
      console.log(
        `  ${"".padEnd(16)} all sets     (n=${String(all.length)}): native ${range(all.map((r) => r.ratioII_native))}  web ${range(all.map((r) => r.ratioII_web))}`,
      );
      console.log(
        `  ${"".padEnd(16)} median R on the declared bed: ${median(bed.map((r) => r.ratioI_web / r.ratioI_native)).toFixed(4)}  (range ${range(bed.map((r) => r.ratioI_web / r.ratioI_native))})`,
      );
      table.push({
        bed: label,
        declaredBed: {
          cells: bed.length,
          nativeII: sorted(bed.map((r) => r.ratioII_native)),
          webII: sorted(bed.map((r) => r.ratioII_web)),
          medianR: median(bed.map((r) => r.ratioI_web / r.ratioI_native)),
        },
        allSets: {
          cells: all.length,
          nativeII: sorted(all.map((r) => r.ratioII_native)),
          webII: sorted(all.map((r) => r.ratioII_web)),
        },
      });
    }
  }
  findings["N4"] = table;
}

// ---------------------------------------------------------------------------
console.log("\n\n== N5 — the level stop's baseline: the wrong cell and the wrong population ==\n");
{
  const bed = photoCells({ declaredBedOnly: true });
  const delta = (row: CutRow): number => Math.abs(row.interiorMeanWeb - row.interiorMeanNative);
  const worst = [...bed].sort((a, b) => delta(b) - delta(a));
  console.log("  the four largest |Δlevel| on the declared bed, BOTH tiers:");
  for (const row of worst.slice(0, 4)) {
    console.log(
      `    ${delta(row).toFixed(5)}  ${row.tier.padEnd(8)} ${String(row.scale)}x ${row.scheme.padEnd(5)} ` +
        `${row.component}__${row.pose}   native ${row.interiorMeanNative.toFixed(5)} / web ${row.interiorMeanWeb.toFixed(5)}`,
    );
  }
  console.log("");
  const medians: Record<string, number> = {};
  for (const [label, population] of [
    ["declared bed, both tiers", bed],
    ["declared bed, texture only", bed.filter((row) => row.tier === "texture")],
    ["declared bed, texture, ACTIVE only", bed.filter((row) => row.tier === "texture" && row.active)],
  ] as const) {
    for (const scheme of ["light", "dark"] as const) {
      const cells = population.filter((row) => row.scheme === scheme);
      const m = median(cells.map(delta));
      medians[`${label} / ${scheme}`] = m;
      console.log(
        `  median |Δlevel|  ${label.padEnd(36)} ${scheme.padEnd(5)} n=${String(cells.length).padStart(2)}  ${m.toFixed(4)}   worst ${Math.max(...cells.map(delta)).toFixed(5)}`,
      );
    }
  }
  console.log(
    "\n  §7 (c) names 0.0464 on the 1x `dom` row and medians of 0.0053 / 0.0360. The worst\n" +
      "  is the 2x dark `texture` row and the medians on the stop's own population — the\n" +
      "  declared bed, both tiers, as the stop is written — are 0.0060 light / 0.0210 dark.\n" +
      "  0.0053 / 0.0360 is the texture tier's ACTIVE half. The bound (≤ 0.055) is unmoved\n" +
      "  and is still the worst cell rounded up; what moves is the baseline G3 reads.",
  );
  const worstRow = worst[0];
  findings["N5"] = {
    worst:
      worstRow === undefined
        ? undefined
        : {
            delta: delta(worstRow),
            tier: worstRow.tier,
            scale: worstRow.scale,
            scheme: worstRow.scheme,
            cell: `${worstRow.component}__${worstRow.pose}`,
            native: worstRow.interiorMeanNative,
            web: worstRow.interiorMeanWeb,
          },
    medians,
  };
}

// ---------------------------------------------------------------------------
console.log("\n\n== N6 — `mid-chroma-solid`'s dark level bias ==\n");
{
  const anchors = rows.filter(
    (row) =>
      row.os === "27" &&
      row.a11y === "standard" &&
      row.backdrop === "mid-chroma-solid" &&
      !row.tinted &&
      row.tier === "texture" &&
      row.scale === 1,
  );
  const bias: Record<string, number> = {};
  for (const row of anchors) {
    const factor = (row.interiorMeanWeb / row.interiorMeanNative) ** (-2 / 3);
    bias[`${row.scheme} ${row.component}__${row.pose}`] = factor;
    console.log(
      `  1x ${row.scheme.padEnd(5)} ${`${row.component}__${row.pose}`.padEnd(25)}  native ${row.interiorMeanNative.toFixed(4)}  web ${row.interiorMeanWeb.toFixed(4)}  ` +
        `backdrop ${row.interiorMeanBackdrop.toFixed(4)}  →  ratio (i) biased by ${factor.toFixed(3)}×`,
    );
  }
  console.log(
    "\n  §3 and the Surprises quote the two cells by their levels rather than by their\n" +
      "  names, and they are two different components: 0.0761 against 0.2856 is 1x dark\n" +
      "  `capsule-button__inactive`, and 0.6134 against 0.3957 is 1x light\n" +
      "  `rrect-lg__rest`. The light figure's 0.75× is right; the dark one's is 2.41×,\n" +
      "  not 2.29×. Neither carries a bound — the anchor is granted to G3 for the\n" +
      "  chromaticity direction only — so what the correction moves is how far off the\n" +
      "  anchor's level has to come before it can carry the tolerance.",
  );
  findings["N6"] = bias;
}

// ---------------------------------------------------------------------------
console.log("\n\n== N11 (iv) — \"the CSS tier's R is near 1.0 today\" holds on dark, not on light ==\n");
{
  const byScheme: Record<string, unknown> = {};
  for (const scheme of ["light", "dark"] as const) {
    const all = photoCells({ tier: "dom", declaredBedOnly: false }).filter((row) => row.scheme === scheme);
    const bed = photoCells({ tier: "dom", declaredBedOnly: true }).filter((row) => row.scheme === scheme);
    const R = (row: CutRow): number => row.ratioI_web / row.ratioI_native;
    console.log(
      `  ${scheme.padEnd(5)}  all sets (n=${String(all.length)}): ${range(all.map(R))}   declared bed (n=${String(bed.length)}): ${range(bed.map(R))}`,
    );
    byScheme[scheme] = { allSets: sorted(all.map(R)), declaredBed: sorted(bed.map(R)) };
  }
  console.log(
    "\n  §7 (g) (ii) refuses to adopt on the CSS tier because its R is near 1.0 with no\n" +
      "  chroma operator anywhere. That is true of the DARK cells and not of the light\n" +
      "  ones, which run to 1.57. The refusal stands — a statistic that reads 1.57 where\n" +
      "  the body has no hues in it is no more gateable than one that reads 1.0 — but the\n" +
      "  reason is the structure stop's, not this range's.",
  );
  findings["N11(iv)"] = byScheme;
}

// ---------------------------------------------------------------------------
console.log("\n\n== N3 — the invariant twin is NOT blind, so §1's reason for the declared form is wrong ==\n");
{
  const matrixPath =
    process.env["VITREA_G0_SCRATCH_MATRIX"] ?? resolve(HERE, "scratch-matrix.json");
  if (!existsSync(matrixPath)) {
    console.log(`  the scratch matrix is not on this machine (${matrixPath}).`);
    console.log("  The readings this section took are preserved in closure-readings.json; the");
    console.log("  re-derivation is `scratch-capture.sh 27` followed by this script (§2, N12).");
    findings["N3"] = "not recomputed on this run — no scratch matrix";
  } else {
    interface MatrixCell {
      readonly key: { readonly profileKey: string; readonly sceneId: string };
      readonly fixtureSet: string;
      readonly tier: string;
      readonly material?: Record<string, { readonly value: number } | undefined>;
    }
    const cells = (JSON.parse(readFileSync(matrixPath, "utf8")) as { cells: readonly MatrixCell[] })
      .cells;
    const value = (cell: MatrixCell, field: string): number | undefined =>
      cell.material?.[field]?.value;
    const bedCells = cells.filter((cell) => {
      const { profileKey, sceneId } = cell.key;
      if (!profileKey.startsWith("apple-macos-27.0") || !profileKey.includes("-standard-glass0.5"))
        return false;
      if (cell.tier !== "texture" || !DECLARED_SETS.has(cell.fixtureSet)) return false;
      const parts = sceneId.split("__");
      return parts.length === 3 && parts[0] === "photo" && !(parts[2] ?? "").includes("tint");
    });
    const twin = (cell: MatrixCell): number | undefined => {
      const parts = (["Native", "Web"] as const).map((side) => {
        const a = value(cell, `interiorChromaSdA${side}`);
        const b = value(cell, `interiorChromaSdB${side}`);
        const l = value(cell, `interiorOklabLSdDev${side}`);
        return a === undefined || b === undefined || l === undefined || l === 0
          ? undefined
          : Math.hypot(a, b) / l;
      });
      const [native, web] = parts;
      return native === undefined || web === undefined || native === 0 ? undefined : web / native;
    };
    const declared = (cell: MatrixCell): number | undefined => {
      const native = value(cell, "chromaStructureRatioNative");
      const web = value(cell, "chromaStructureRatioWeb");
      return native === undefined || web === undefined || native === 0 ? undefined : web / native;
    };
    const table: unknown[] = [];
    for (const scheme of ["light", "dark"] as const) {
      for (const active of [true, false] as const) {
        const group = bedCells.filter(
          (cell) =>
            (cell.key.profileKey.includes("-dark-") ? "dark" : "light") === scheme &&
            (cell.key.sceneId.endsWith("__rest") ? true : false) === active,
        );
        const t = group.map(twin).filter((x): x is number => x !== undefined);
        const d = group.map(declared).filter((x): x is number => x !== undefined);
        if (t.length === 0) continue;
        const label = `${scheme} ${active ? "active" : "inactive"}`;
        console.log(
          `  ${label.padEnd(16)} n=${String(t.length).padStart(2)}   twin median ${median(t).toFixed(4)} (${range(t)})` +
            `   declared median ${median(d).toFixed(4)} (${range(d)})`,
        );
        table.push({ bed: label, cells: t.length, twinMedian: median(t), twin: sorted(t), declaredMedian: median(d), declared: sorted(d) });
      }
    }
    // The 1x-against-2x spread of each form, which is the only repeat the bed offers.
    console.log("");
    for (const [label, form] of [["declared", declared], ["twin", twin]] as const) {
      for (const scheme of ["light", "dark"] as const) {
        const pairs = new Map<string, Map<number, number>>();
        for (const cell of bedCells) {
          if ((cell.key.profileKey.includes("-dark-") ? "dark" : "light") !== scheme) continue;
          const read = form(cell);
          if (read === undefined) continue;
          const scale = cell.key.profileKey.includes("-2x-") ? 2 : 1;
          const byScale = pairs.get(cell.key.sceneId) ?? new Map<number, number>();
          byScale.set(scale, read);
          pairs.set(cell.key.sceneId, byScale);
        }
        const spreads: number[] = [];
        for (const byScale of pairs.values()) {
          const one = byScale.get(1);
          const two = byScale.get(2);
          if (one !== undefined && two !== undefined) spreads.push(Math.abs(one - two) / ((one + two) / 2));
        }
        if (spreads.length === 0) continue;
        console.log(
          `  1x-against-2x spread, ${label.padEnd(9)} ${scheme.padEnd(5)} pairs=${String(spreads.length)}  ` +
            `median ${(median(spreads) * 100).toFixed(2)} %  worst ${(Math.max(...spreads) * 100).toFixed(2)} %`,
        );
      }
    }
    console.log(
      "\n  §1 keeps the linear-luma denominator because \"under the OKLab-L denominator the\n" +
        "  plate composite very nearly cancels\". It does not: the twin reads 0.27–0.50 on\n" +
        "  this bed's medians, below the declared form's on every one of the four beds, and\n" +
        "  reproduces about as well across rasters. The declared form is KEPT, on the reason\n" +
        "  that survives: its denominator is `interiorStdDevWeb`, the quantity the structure\n" +
        "  stop bounds and the matrix already carries, so a fit cannot move the denominator\n" +
        "  out from under the statistic. The twin's denominator is bounded by nothing.",
    );
    findings["N3"] = table;
  }
}

writeFileSync(
  resolve(HERE, "blurred-reference-closure.txt"),
  `${n2.join("\n")}\n`,
);
console.log("\nwrote blurred-reference-closure.txt");

writeFileSync(
  resolve(HERE, "closure-readings.json"),
  `${JSON.stringify({ closure: "W31 G0 review closure, claims §5.161 §11", findings }, null, 2)}\n`,
);
console.log("\nwrote closure-readings.json");

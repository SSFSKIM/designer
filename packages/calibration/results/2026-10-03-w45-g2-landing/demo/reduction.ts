/**
 * W45 G2 (claims §5.207): the demo's reduction at the landing's union, as the build embeds it.
 *
 *   cd packages/calibration && pnpm exec tsx results/2026-10-03-w45-g2-landing/demo/reduction.ts
 *
 * Prints the virtual module's SHA-256 (the exact text `matrixReduction()` serves), its size, the
 * reduced cell count per position and `MATRIX_CELL_COUNT`.
 */
import { createHash } from "node:crypto";
import { reduceMatrix } from "../../../../../apps/demo/matrix-reduction.ts";

const { cells, matrixCellCount } = reduceMatrix();
const text = `export const CELLS = ${JSON.stringify(cells)};\n` + `export const MATRIX_CELL_COUNT = ${matrixCellCount};\n`;
const position = (key: string): string => /-glass(\d+(?:\.\d+)?)$/.exec(key)?.[1] ?? "26.5";
const count = new Map<string, number>();
for (const cell of cells as readonly { readonly key: { readonly profileKey: string } }[]) {
  const at = position(cell.key.profileKey);
  count.set(at, (count.get(at) ?? 0) + 1);
}
console.log(JSON.stringify({
  moduleSha256: createHash("sha256").update(text).digest("hex"),
  moduleBytes: Buffer.byteLength(text),
  cells: cells.length,
  perPosition: Object.fromEntries([...count].sort()),
  matrixCellCount,
}, null, 1));

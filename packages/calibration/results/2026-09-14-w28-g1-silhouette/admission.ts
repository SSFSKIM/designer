import { readFileSync } from "node:fs";

const bed = JSON.parse(readFileSync(new URL("../2026-09-11-w27c-g1b/checking-bed.json",
  import.meta.url), "utf8"));
const base = (scene: string): string => scene.split("__").slice(0, 2).join("__");
const checking = new Set<string>([
  ...bed.groups.find((group: any) => group.id === "D").scenes,
  "checkerboard__rrect-ml__inactive",
].map(base));

/** X10 applies at admission, before a page or native fixture can be opened. */
export function admitSelection(scene: string): void {
  if (checking.has(base(scene))) throw new Error(`${scene}: forbidden checking set cell (X10)`);
}

/** A control is selection evidence too; role labels cannot bypass either exclusion. */
export function admitFitRows(
  rows: readonly { profile: string; scene: string }[],
  holdout: ReadonlySet<string>,
): void {
  for (const row of rows) {
    admitSelection(row.scene);
    if (holdout.has(`${row.profile}/${row.scene}`)) {
      throw new Error(`${row.profile}/${row.scene}: unread W28 holdout cannot enter a fit`);
    }
  }
}

// Write the sweep's strengths into the page's constant, the one line that holds them.
import { readFileSync, writeFileSync } from "node:fs";
const { chosen } = JSON.parse(readFileSync("/tmp/sp-clear/sweep.json", "utf8"));
const f = "/Users/new/Developer/GitHub/designer/apps/demo/src/gallery/start-page/shared.ts";
const s = readFileSync(f, "utf8");
const re = /export const CLEAR_DIMMING: Readonly<Record<"light" \| "dark", number>> = \{ light: [\d.]+, dark: [\d.]+ \};/;
if (!re.test(s)) throw new Error("constant line not found");
writeFileSync(f, s.replace(re, `export const CLEAR_DIMMING: Readonly<Record<"light" | "dark", number>> = { light: ${chosen.light}, dark: ${chosen.dark} };`));
console.log("CLEAR_DIMMING now", JSON.stringify(chosen));

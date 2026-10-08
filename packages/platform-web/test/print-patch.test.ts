// @vitest-environment node
/** A generated chart must retain encoded-output tuples, not turn them into input codes or strings. */
import { execFileSync } from "node:child_process";
import process from "node:process";
import { runInNewContext } from "node:vm";
import { expect, it } from "vitest";

it("prints W50's complete chart as four-number tuples without changing normalized ordinates", () => {
  const patch = {
    lowEndStrength: 0.75,
    lowEnd44: [20 / 255, 28 / 255, 50 / 255, 64 / 255],
    lowEnd96: [24 / 255, 32 / 255, 54 / 255, 68 / 255],
    lowEnd160: [28 / 255, 36 / 255, 58 / 255, 72 / 255],
    optics: { regular: { tint: [0.03, 0.03, 0.03], tintAlpha: 0.8 } },
  };
  const printer = new URL("../scripts/print-patch.mjs", import.meta.url).href;
  const source = execFileSync(process.execPath, ["--input-type=module", "-e",
    `import { print } from ${JSON.stringify(printer)}; ` +
      'process.stdout.write(print(JSON.parse(process.argv[1]), ""));',
    JSON.stringify(patch),
  ], { encoding: "utf8" });
  // Numeric tuple syntax is already valid JavaScript; parse the actual printer output rather
  // than asserting that its implementation contains an array branch.
  expect(runInNewContext(`(${source})`)).toEqual(patch);
});

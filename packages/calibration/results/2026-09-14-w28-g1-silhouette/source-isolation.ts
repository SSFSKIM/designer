/** Prove the silhouette-only harness sizing correction leaves source captures unchanged. */
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync, unlinkSync } from "node:fs";
import { resolve } from "node:path";
import { launch, here, pkg, repo } from "./browser";

const oldScene = execFileSync("git", ["-C", repo, "show", "f925156c:packages/calibration/web/scene.ts"],
  { encoding: "utf8" });
const oldHtml = execFileSync("git", ["-C", repo, "show", "f925156c:packages/calibration/web/index.html"],
  { encoding: "utf8" });
const beforeScene = resolve(pkg, "web/w28-source-before.ts");
const beforeHtml = resolve(pkg, "web/w28-source-before.html");
writeFileSync(beforeScene, oldScene);
writeFileSync(beforeHtml, oldHtml.replace("./scene.ts", "./w28-source-before.ts"));
const sha = (bytes: Buffer) => createHash("sha256").update(bytes).digest("hex");
const rows: any[] = [];
let run: Awaited<ReturnType<typeof launch>> | undefined;
try {
  run = await launch("source-harness-isolation");
  for (const tier of ["webgpu", "css"]) {
    for (const scheme of ["light", "dark"]) {
      for (const scene of ["photo__capsule-button__rest", "checkerboard__rrect-md__rest"]) {
        const profile = JSON.parse(readFileSync(resolve(pkg, "profiles",
          `apple-macos-26.5-1x-${scheme}-standard.json`), "utf8"));
        const context = await run.browser.newContext({ viewport: { width: 320, height: 200 },
          deviceScaleFactor: 1, colorScheme: scheme as "light" | "dark" });
        await context.addInitScript((patch) => { window.__vitreaMaterialProfile = patch; }, profile.patch);
        const captures: Buffer[] = [];
        for (const entry of ["w28-source-before.html", "index.html"]) {
          const page = await context.newPage();
          await page.goto(`${run.url}/${entry}?scene=${scene}&renderer=${tier}&scale=1&frames=16`);
          await page.waitForSelector("html[data-scene-ready='1'], html[data-scene-error]", { state: "attached" });
          const failure = await page.getAttribute("html", "data-scene-error");
          if (failure !== null) throw new Error(failure);
          const report = await page.evaluate(() => window.__vitreaCalibration.report);
          if (report.groups.some((g: any) => g.state?.activeRenderer !== tier)) throw new Error("Wrong tier");
          if (tier === "webgpu" && report.adapter.isFallback !== false) throw new Error("Not hardware");
          captures.push(await page.locator("#stage").screenshot({ animations: "disabled" }));
          await page.close();
        }
        await context.close();
        rows.push({ tier, scheme, scene, beforeSha256: sha(captures[0]!),
          afterSha256: sha(captures[1]!), equal: captures[0]!.equals(captures[1]!) });
      }
    }
  }
  writeFileSync(resolve(here, "source-harness-isolation.json"), `${JSON.stringify({
    against: "f925156c calibration/web/scene.ts and index.html; current runtime on both sides",
    scope: "The profile-gated border-box harness correction only; runtime source identity is separately checked by GPU goldens.",
    machineAccessibility: run.machineAccessibility, rows,
  }, null, 2)}\n`);
  if (rows.some((row) => !row.equal)) throw new Error("Source harness isolation failed");
  console.log(`${rows.length}/${rows.length} source captures byte-identical`);
} finally {
  await run?.browser.close();
  await run?.server.close();
  unlinkSync(beforeScene);
  unlinkSync(beforeHtml);
}

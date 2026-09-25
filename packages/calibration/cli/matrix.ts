/** Declare a whole generation, inspect its missing membership, publish it once. */
import { resolve } from "node:path";
import { createStage, stageStatus } from "../src/generation-stage";
import { publishGeneration } from "../src/matrix-write-guard";

try {
  const args = process.argv.slice(2).filter((s) => s !== "--");
  const [verb, directory] = args;
  if (!directory) throw new Error("usage: matrix stage|status|publish <directory> [declaration flags]");
  const flag = (name: string) => {
    const at = args.indexOf(`--${name}`);
    return at < 0 ? undefined : args[at + 1];
  };
  const list = (name: string) => flag(name)?.split(",").filter(Boolean) ?? [];
  if (verb === "stage") {
    const active = flag("material-profile");
    if (!active) throw new Error("stage requires --material-profile");
    createStage(resolve(directory), { profiles: list("profile"), tiers: list("renderer"),
      sets: list("set"), active: resolve(active),
      ...(flag("receded-profile") ? { receded: resolve(flag("receded-profile")!) } : {}) });
    process.stdout.write(`${JSON.stringify(stageStatus(directory), null, 2)}\n`);
  } else if (verb === "status") process.stdout.write(`${JSON.stringify(stageStatus(directory), null, 2)}\n`);
  else if (verb === "publish") process.stdout.write(`${JSON.stringify(publishGeneration(directory), null, 2)}\n`);
  else throw new Error("expected stage, status or publish; retirement happens only through publication");
} catch (error) {
  process.stderr.write(`matrix: ${error instanceof Error ? error.message : String(error)}\n`);
  process.exitCode = 1;
}

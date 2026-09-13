#!/usr/bin/env node

/**
 * Run one browser command only while both relevant macOS accessibility preferences are off.
 * Every attempt is appended to browser-runs.json so claims §5.142 can account for each run.
 */

import { spawnSync } from "node:child_process";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { setTimeout as sleep } from "node:timers/promises";

const here = dirname(fileURLToPath(import.meta.url));
const logPath = join(here, "browser-runs.json");
const command = process.argv.slice(2);
if (command.length === 0) throw new Error("usage: checked-run.mjs <command> [args ...]");

function preference(key) {
  const read = spawnSync("defaults", ["read", "com.apple.universalaccess", key], {
    encoding: "utf8",
  });
  if (read.status !== 0) {
    throw new Error(`could not read com.apple.universalaccess ${key}: ${read.stderr.trim()}`);
  }
  const value = Number(read.stdout.trim());
  if (value !== 0 && value !== 1) throw new Error(`${key} was neither 0 nor 1: ${read.stdout.trim()}`);
  return value;
}

let accessibility;
for (;;) {
  accessibility = {
    reduceTransparency: preference("reduceTransparency"),
    increaseContrast: preference("increaseContrast"),
  };
  if (accessibility.reduceTransparency === 0 && accessibility.increaseContrast === 0) break;
  process.stderr.write(
    `accessibility is not nominal (${JSON.stringify(accessibility)}); polling again in 5s\n`,
  );
  await sleep(5000);
}

const startedAt = new Date().toISOString();
const result = spawnSync(command[0], command.slice(1), {
  cwd: process.cwd(),
  encoding: "utf8",
  env: {
    ...process.env,
    W27E_REDUCE_TRANSPARENCY: String(accessibility.reduceTransparency),
    W27E_INCREASE_CONTRAST: String(accessibility.increaseContrast),
  },
  maxBuffer: 64 * 1024 * 1024,
});
process.stdout.write(result.stdout ?? "");
process.stderr.write(result.stderr ?? "");

const records = existsSync(logPath) ? JSON.parse(readFileSync(logPath, "utf8")) : [];
records.push({
  startedAt,
  completedAt: new Date().toISOString(),
  command,
  accessibility,
  status: result.status,
  signal: result.signal,
});
writeFileSync(logPath, `${JSON.stringify(records, null, 2)}\n`);

if (result.error !== undefined) throw result.error;
process.exit(result.status ?? 1);

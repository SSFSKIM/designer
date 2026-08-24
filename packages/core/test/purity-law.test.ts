/**
 * X4 — proof that the purity law is enforced, not merely declared.
 *
 * The test seeds a real DOM violation into this package's `src/`, runs the two
 * checks that `pnpm lint` runs, asserts each one fails for the right reason, and
 * removes the seed. If either layer is ever weakened, this test goes red.
 *
 * The last block extends the same technique to core's own passivity law: a
 * scheduler that could arm a timer would stop being a contract and start being a
 * loop, so timers and clocks are lint-banned in `src/` the same way the DOM is.
 */

import { spawnSync } from "node:child_process";
import { existsSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { afterEach, describe, expect, it } from "vitest";

const packageRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const seedFile = "src/x4-violation.purity-seed.ts";
const seedPath = join(packageRoot, seedFile);

const SEED_SOURCE = `// Seeded by test/purity-law.test.ts. Removed again in the same test.
export const viewportWidth = window.innerWidth;
export const pageTitle = document.title;
export const agent = navigator.userAgent;

export function measure(host: HTMLElement): number {
  return host.clientWidth;
}
`;

const passiveSeedFile = "src/passive-violation.purity-seed.ts";
const passiveSeedPath = join(packageRoot, passiveSeedFile);

const PASSIVE_SEED_SOURCE = `// Seeded by test/purity-law.test.ts. Removed again in the same test.
export const startedAt = Date.now();
export const measuredAt = performance.now();

export function tick(step: () => void): void {
  setTimeout(step, 16);
  setInterval(step, 16);
  queueMicrotask(step);
}
`;

interface EslintMessage {
  readonly ruleId: string | null;
  readonly message: string;
}

interface EslintResult {
  readonly filePath: string;
  readonly messages: readonly EslintMessage[];
}

function runLocalBin(bin: string, args: readonly string[]) {
  const result = spawnSync(process.execPath, [join(packageRoot, "node_modules", bin), ...args], {
    cwd: packageRoot,
    encoding: "utf8",
  });
  return { status: result.status, stdout: result.stdout ?? "", stderr: result.stderr ?? "" };
}

const runEslint = (args: readonly string[]) => runLocalBin("eslint/bin/eslint.js", args);
const runTsc = (args: readonly string[]) => runLocalBin("typescript/bin/tsc", args);

afterEach(() => {
  if (existsSync(seedPath)) rmSync(seedPath);
  if (existsSync(passiveSeedPath)) rmSync(passiveSeedPath);
});

describe("purity law enforcement (X4)", () => {
  it("fails ESLint on every forbidden browser global, naming the law", () => {
    writeFileSync(seedPath, SEED_SOURCE);

    const { status, stdout } = runEslint([seedFile, "--format", "json"]);
    expect(status).toBe(1);

    const results = JSON.parse(stdout) as readonly EslintResult[];
    const messages = results.flatMap((result) => [...result.messages]);
    const rules = new Set(messages.map((message) => message.ruleId));

    expect(rules).toContain("no-restricted-globals");
    // HTMLElement appears in type position only, so a separate rule owns it.
    expect(rules).toContain("@typescript-eslint/no-restricted-types");

    const text = messages.map((message) => message.message).join("\n");
    for (const global of ["window", "document", "navigator", "HTMLElement"]) {
      expect(text).toContain(global);
    }
    expect(text).toContain("X4");
  }, 60_000);

  it("fails the typecheck too — pure packages compile without the DOM lib", () => {
    writeFileSync(seedPath, SEED_SOURCE);

    const { status, stdout, stderr } = runTsc(["--noEmit", "-p", "tsconfig.json"]);
    const output = stdout + stderr;

    expect(status).not.toBe(0);
    expect(output).toContain("Cannot find name 'window'");
    expect(output).toContain("Cannot find name 'document'");
    expect(output).toContain("Cannot find name 'HTMLElement'");
  }, 120_000);

  it("passes on the real source — the rules do not fire spuriously", () => {
    const { status } = runEslint(["src", "--format", "json"]);
    expect(status).toBe(0);
  }, 60_000);
});

describe("passivity law enforcement (core only)", () => {
  it("fails ESLint on every timer and clock, naming the law", () => {
    writeFileSync(passiveSeedPath, PASSIVE_SEED_SOURCE);

    const { status, stdout } = runEslint([passiveSeedFile, "--format", "json"]);
    expect(status).toBe(1);

    const results = JSON.parse(stdout) as readonly EslintResult[];
    const messages = results.flatMap((result) => [...result.messages]);
    const text = messages.map((message) => message.message).join("\n");

    for (const global of ["Date", "performance", "setTimeout", "setInterval", "queueMicrotask"]) {
      expect(text).toContain(global);
    }
    expect(text).toContain("passive");
  }, 60_000);

  it("still enforces the DOM half of the law it extends", () => {
    writeFileSync(seedPath, SEED_SOURCE);

    const { stdout } = runEslint([seedFile, "--format", "json"]);
    const results = JSON.parse(stdout) as readonly EslintResult[];
    const text = results
      .flatMap((result) => [...result.messages])
      .map((message) => message.message)
      .join("\n");

    expect(text).toContain("X4");
  }, 60_000);
});

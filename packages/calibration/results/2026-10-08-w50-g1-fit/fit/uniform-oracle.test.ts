import assert from "node:assert/strict";
import { test } from "node:test";
import { chartCodes, currentEndpoint, fixedJoins, composedUniformCode } from "./uniform-oracle.ts";

const rows = [[20, 28, 48, 60], [24, 32, 52, 64], [28, 36, 56, 68]]
  .map((row) => row.map((code) => code / 255));

test("composed neutral solve follows the chart rather than the old authority trough", async () => {
  for (const position of [0.25, 0.5] as const) for (const pose of ["active", "receded"] as const) {
    const profile = await currentEndpoint(position, pose);
    for (const dpr of [1, 2]) for (const span of [44, 70, 96, 128, 160, 224]) {
      for (const input of [0, 4, 8, 12, 28, 40]) {
        const result = await composedUniformCode(profile, rows, input, span, dpr);
        assert.ok(Math.abs(result - chartCodes(rows, input, span)) < 1e-8,
          `${position}/${pose}/${dpr}/${span}/${input}: ${result}`);
      }
    }
  }
});

test("join table covers every actual span and both scales without fitting the old law", async () => {
  const profile = await currentEndpoint(0.25, "receded");
  const joins = await fixedJoins(profile);
  assert.equal(joins.length, 386);
  assert.deepEqual([...new Set(joins.map((join) => join.dpr))], [1, 2]);
  for (const join of joins) {
    assert.ok(Number.isFinite(join.value));
    assert.ok(Math.abs(await composedUniformCode(profile, rows, 64, join.span, join.dpr) - join.value) < 1e-10);
  }
});

test("the existing fully collapsed thin state does not acquire chart authority", async () => {
  const profile = await currentEndpoint(0.25, "active");
  const raised = rows.map((row) => row.map((value) => value + 0.1));
  assert.equal(await composedUniformCode(profile, rows, 0, 32, 1),
    await composedUniformCode(profile, raised, 0, 32, 1));
  assert.equal(await composedUniformCode(profile, rows, 0, 32, 1), 0);
});

test("the diagnostic refuses invalid endpoint or chart scope", async () => {
  await assert.rejects(currentEndpoint(0.3 as 0.25, "active"));
  const profile = await currentEndpoint(0.5, "active");
  await assert.rejects(composedUniformCode(profile, [[0, 0, 0, 0]], 4, 44, 1));
  await assert.rejects(composedUniformCode(profile, rows, 65, 44, 1));
  await assert.rejects(composedUniformCode(profile, rows, 4, 225, 1));
});

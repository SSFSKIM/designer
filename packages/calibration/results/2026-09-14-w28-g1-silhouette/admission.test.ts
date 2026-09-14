import { strict as assert } from "node:assert";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { admitSelection, admitFitRows } from "./admission";

const bed = JSON.parse(readFileSync(new URL("../2026-09-11-w27c-g1b/checking-bed.json",
  import.meta.url), "utf8"));
const denied = bed.groups.find((group: any) => group.id === "D").scenes;

test("no checking id can enter a mechanism population, on either pose", () => {
  for (const id of [...denied, "checkerboard__rrect-ml__inactive"]) {
    for (const scene of [id, id.replace("__inactive", "__rest"), `${id}-tint-orange`]) {
      assert.throws(() => admitSelection(scene), /checking set/);
    }
  }
  assert.doesNotThrow(() => admitSelection("photo__capsule-button__inactive"));
});

test("fit rows reject D as a supplying cell, control, or unlabelled sweep row", () => {
  for (const scene of denied) {
    for (const role of ["fit", "control", undefined]) {
      assert.throws(() => admitFitRows([{ profile: "p", scene, role }], new Set()), /checking set/);
    }
  }
});

test("a holdout cannot enter any fit row under another role", () => {
  const scene = "photo__capsule-button__inactive";
  for (const role of ["fit", "control", undefined]) {
    assert.throws(() => admitFitRows([{ profile: "p", scene, role }], new Set([`p/${scene}`])),
      /holdout/);
  }
  assert.doesNotThrow(() => admitFitRows([{ profile: "q", scene }], new Set([`p/${scene}`])));
});

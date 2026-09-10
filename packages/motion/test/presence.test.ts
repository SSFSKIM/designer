import { expect, it } from "vitest";
import { createInteractionMachine, STATE_DRIVEN_CHANNELS } from "../src/index";

it("keeps authored presence even when an interaction machine explicitly carries it", () => {
  const machine = createInteractionMachine({ channels: [...STATE_DRIVEN_CHANNELS, "materialization"] });
  machine.driver("materialization").retarget(0);
  machine.advance(20);
  const before = machine.value("materialization");
  machine.transition("hover");
  expect(machine.driver("materialization").target).toBe(0);
  machine.advance(20);
  expect(machine.value("materialization")).toBeLessThan(before);
});

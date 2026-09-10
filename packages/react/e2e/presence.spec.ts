import { writeFile } from "node:fs/promises";
import { expect, test } from "@playwright/test";
import { gotoPlayground } from "./support";

for (const reducedMotion of [false, true]) {
  test(`authored presence is monotone in place${reducedMotion ? " with reduced motion" : ""}`, async ({ page }, testInfo) => {
    await page.emulateMedia({ reducedMotion: reducedMotion ? "reduce" : "no-preference" });
    await gotoPlayground(page);
    const plate = page.getByTestId("dom-plate");
    await expect(page.getByRole("button", { name: "Dismiss glass" })).toBeVisible();
    await expect.poll(() => plate.evaluate((host) =>
      host.style.getPropertyValue("--vitrea-materialization"))).toBe("1");

    const traces = [];
    for (const target of [0, 1]) {
      const samples = await page.evaluate((destination) => new Promise<{
        time: number; value: number; node: string | null; opacity: string; ancestors: string[]; bodyOpacity: string;
      }[]>((resolve) => {
        const host = document.querySelector<HTMLElement>('[data-testid="dom-plate"]')!;
        const button = document.querySelector<HTMLButtonElement>('[data-testid="presence-toggle"]')!;
        const frames: { time: number; value: number; node: string | null; opacity: string; ancestors: string[]; bodyOpacity: string }[] = [];
        const sample = (time: number): void => {
          const ancestors: string[] = [];
          for (let element = host.parentElement; element !== null; element = element.parentElement) {
            ancestors.push(getComputedStyle(element).opacity);
          }
          const sharp = host.querySelector('[data-vitrea-css-layer="sharp"]')!;
          frames.push({ time, value: Number(host.style.getPropertyValue("--vitrea-materialization")),
            node: host.getAttribute("data-vitrea-node"), opacity: getComputedStyle(host).opacity, ancestors,
            bodyOpacity: getComputedStyle(sharp).opacity });
          if ((frames.length > 1 && frames.at(-1)!.value === destination) || frames.length >= 90) {
            resolve(frames);
          } else requestAnimationFrame(sample);
        };
        requestAnimationFrame((time) => { sample(time); button.click(); });
      }), target);
      expect(samples[0]!.value).toBe(1 - target);
      expect(samples.at(-1)!.value).toBe(target);
      expect(samples.at(-1)!.bodyOpacity).toBe(String(target));
      const intervals = samples.slice(1).map((frame, index) => frame.time - samples[index]!.time);
      const oneFrame = Math.max(...intervals);
      const elapsed = samples.at(-1)!.time - samples[0]!.time;
      expect(elapsed).toBeLessThanOrEqual((reducedMotion ? 0 : 220) + oneFrame + 1);
      if (!reducedMotion) expect(samples.some((frame) => frame.value > 0 && frame.value < 1)).toBe(true);
      for (const [index, frame] of samples.entries()) {
        expect(frame.node).toBe(samples[0]!.node);
        expect(frame.opacity).toBe("1");
        expect(Number(frame.bodyOpacity)).toBeCloseTo(frame.value, 3);
        expect(frame.ancestors.every((opacity) => opacity === "1")).toBe(true);
        if (index > 0) {
          if (target === 0) expect(frame.value).toBeLessThanOrEqual(samples[index - 1]!.value);
          else expect(frame.value).toBeGreaterThanOrEqual(samples[index - 1]!.value);
        }
      }
      traces.push({ target, elapsed, oneFrame, samples });
    }
    const tracePath = testInfo.outputPath("materialization-trace.json");
    await writeFile(tracePath, JSON.stringify({ engine: testInfo.project.name, reducedMotion, traces }, null, 2));
    await testInfo.attach("materialization-trace", { path: tracePath, contentType: "application/json" });
  });
}

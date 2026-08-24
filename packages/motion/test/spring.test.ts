import { describe, expect, it } from "vitest";

import { SpringDriver, type SpringConfig } from "../src/index";

/** A long-tailed spring, so tests observe flight rather than the settled tail. */
const flight = (overrides: Partial<SpringConfig> = {}): SpringConfig => ({
  responseMs: 400,
  dampingRatio: 0.7,
  restDistance: 1e-4,
  restVelocity: 1e-3,
  ...overrides,
});

/**
 * Ground truth for the closed form: RK4 on y'' = -2ζω y' - ω² y, where
 * y = value - target. Fine steps, so the reference is exact to ~1e-12 and any
 * algebra error in the closed form shows up rather than being self-consistent.
 */
function referenceSpring(
  y0: number,
  v0: number,
  omega: number,
  zeta: number,
  seconds: number,
  steps: number,
): { y: number; v: number } {
  const h = seconds / steps;
  const accel = (y: number, v: number) => -2 * zeta * omega * v - omega * omega * y;
  let y = y0;
  let v = v0;
  for (let i = 0; i < steps; i += 1) {
    const k1y = v;
    const k1v = accel(y, v);
    const k2y = v + 0.5 * h * k1v;
    const k2v = accel(y + 0.5 * h * k1y, v + 0.5 * h * k1v);
    const k3y = v + 0.5 * h * k2v;
    const k3v = accel(y + 0.5 * h * k2y, v + 0.5 * h * k2v);
    const k4y = v + h * k3v;
    const k4v = accel(y + h * k3y, v + h * k3v);
    y += (h / 6) * (k1y + 2 * k2y + 2 * k3y + k4y);
    v += (h / 6) * (k1v + 2 * k2v + 2 * k3v + k4v);
  }
  return { y, v };
}

describe("SpringDriver — closed-form damped harmonic oscillator", () => {
  it.each([
    { label: "underdamped", dampingRatio: 0.4 },
    { label: "critically damped", dampingRatio: 1 },
    { label: "overdamped", dampingRatio: 2.5 },
  ])("matches an RK4 reference solution ($label)", ({ dampingRatio }) => {
    const responseMs = 300;
    const omega = (2 * Math.PI * 1000) / responseMs;
    const driver = new SpringDriver(flight({ responseMs, dampingRatio }), 0);
    driver.retarget(1);
    driver.jumpTo(0, 2.5);

    driver.advance(200);

    const reference = referenceSpring(-1, 2.5, omega, dampingRatio, 0.2, 40_000);
    expect(driver.value - 1).toBeCloseTo(reference.y, 9);
    expect(driver.velocity).toBeCloseTo(reference.v, 8);
  });

  it("holds position and velocity exactly across a mid-flight retarget", () => {
    const driver = new SpringDriver(flight(), 0);
    driver.retarget(1);
    driver.advance(60);

    const value = driver.value;
    const velocity = driver.velocity;
    expect(value).toBeGreaterThan(0);
    expect(velocity).toBeGreaterThan(0);

    driver.retarget(-3);

    expect(driver.value).toBe(value);
    expect(driver.velocity).toBe(velocity);
    expect(driver.target).toBe(-3);
  });

  it("continues from the carried velocity after a retarget", () => {
    const driver = new SpringDriver(flight(), 0);
    driver.retarget(1);
    driver.advance(60);
    const velocity = driver.velocity;

    driver.retarget(0);
    const before = driver.value;
    driver.advance(0.01);
    const measured = ((driver.value - before) / 0.01) * 1000;

    // A finite difference over 0.01 ms recovers the carried velocity: the
    // redirect bends the trajectory, it does not restart it.
    expect(measured).toBeCloseTo(velocity, 2);
  });

  it("overshoots when underdamped and never overshoots at or above critical", () => {
    const sample = (dampingRatio: number) => {
      const driver = new SpringDriver(flight({ dampingRatio }), 0);
      driver.retarget(1);
      let peak = 0;
      for (let i = 0; i < 400; i += 1) {
        driver.advance(5);
        peak = Math.max(peak, driver.value);
      }
      return peak;
    };

    expect(sample(0.45)).toBeGreaterThan(1);
    expect(sample(1)).toBeLessThanOrEqual(1 + 1e-12);
    expect(sample(3)).toBeLessThanOrEqual(1 + 1e-12);
  });

  it("reports settled only once inside both the distance and velocity bands", () => {
    const driver = new SpringDriver(flight({ restDistance: 1e-3, restVelocity: 1e-2 }), 0);
    driver.retarget(1);
    expect(driver.settled).toBe(false);

    let elapsed = 0;
    while (!driver.settled && elapsed < 10_000) {
      driver.advance(8);
      elapsed += 8;
    }

    expect(driver.settled).toBe(true);
    expect(Math.abs(driver.value - 1)).toBeLessThanOrEqual(1e-3);
    expect(Math.abs(driver.velocity)).toBeLessThanOrEqual(1e-2);
    expect(elapsed).toBeLessThan(10_000);
  });

  it("starts settled at its own target and stays there", () => {
    const driver = new SpringDriver(flight(), 0.25);
    expect(driver.target).toBe(0.25);
    expect(driver.settled).toBe(true);
    driver.advance(16.7);
    expect(driver.value).toBe(0.25);
    expect(driver.velocity).toBe(0);
  });

  it("ignores non-positive and non-finite deltas", () => {
    const driver = new SpringDriver(flight(), 0);
    driver.retarget(1);
    driver.advance(20);
    const value = driver.value;

    driver.advance(0);
    driver.advance(-16.7);
    driver.advance(Number.NaN);

    expect(driver.value).toBe(value);
  });

  it("stays finite through a stiff, strongly overdamped 200 ms step", () => {
    // Guards the cosh/sinh formulation: cosh(s·t) overflows while e^(-ζωt)
    // underflows, so a naive implementation returns NaN here.
    const driver = new SpringDriver(flight({ responseMs: 5, dampingRatio: 30 }), 0);
    driver.retarget(1);
    driver.advance(200);

    expect(Number.isFinite(driver.value)).toBe(true);
    expect(Number.isFinite(driver.velocity)).toBe(true);
    expect(driver.value).toBeLessThanOrEqual(1);
  });
});

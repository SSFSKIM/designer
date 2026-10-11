import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';
import {
  epsilon, lessEqual, m1WithinBounds, m2StructureVerdict, l1Caps,
} from '../results/2026-10-11-w52-g0-declaration/precision/owner.js';

const m1Bounds = { min: .6, max: 1.4 };
const l1Bounds = { absolute: .055, growth: .005 };
const structure = (reference: number, web: number) => ({
  interiorStdDevWebReference: reference,
  interiorStdDevWeb: web,
  structureDeltaFraction: (web - reference) / reference,
});

describe('W52 prospective owner source precision (not wired to a judge)', () => {
  it('uses binary64 spacing, not rounded log2, at both sides of a binade', () => {
    expect(epsilon(2 - Number.EPSILON)).toBe(64 * Number.EPSILON);
    expect(epsilon(2)).toBe(128 * Number.EPSILON);
    expect(epsilon(255)).toBe(64 * 2 ** -45);
    expect(epsilon(.0005, .003)).toBe(64 * Number.EPSILON);
    expect(epsilon(1, -255)).toBe(64 * 2 ** -45);
  });

  it('matches Python epsilon and inclusive comparison across binade boundaries', () => {
    const cases = [
      [0, 0], [.0005, .003], [1, 1], [1 - 2 ** -53, 1],
      [2 - 2 ** -52, 1], [2, 1], [2 + 2 ** -51, 1],
      [128 - 2 ** -46, 1], [128, 1], [255, 1],
      [256 - 2 ** -45, 1], [256, 1], [256 + 2 ** -44, 1],
      [2 ** 1023, 1], [Number.MAX_VALUE, 1],
      [1 + 64 * Number.EPSILON, 1], [1 + 128 * Number.EPSILON, 1],
      [Math.abs(21 - 19.999999999999996), 1, 21, 19.999999999999996],
    ];
    const comparison = fileURLToPath(new URL(
      '../results/2026-10-11-w52-g0-declaration/precision/comparison.py', import.meta.url));
    const python = spawnSync('python3', ['-I', '-B', '-c', `
import importlib.util, json, sys
spec = importlib.util.spec_from_file_location('comparison', sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
print(json.dumps([[module.epsilon(*v), module.less_equal(*v)]
                  for v in json.loads(sys.argv[2])]))
`, comparison, JSON.stringify(cases)], { encoding: 'utf8' });
    expect(python.status, python.stderr).toBe(0);
    expect(cases.map(([value, bound, ...sources]) => [
      epsilon(value!, bound!, ...sources), lessEqual(value!, bound!, ...sources),
    ])).toEqual(JSON.parse(python.stdout));
  });

  it('includes source operands, accepts only roundoff at the bound, and rejects real excess', () => {
    const error = Math.abs(21 - 19.999999999999996);
    expect(error).toBeGreaterThan(1);
    expect(lessEqual(error, 1, 21, 19.999999999999996)).toBe(true);
    expect(lessEqual(1 + epsilon(255), 1, 255)).toBe(true);
    expect(lessEqual(1 + 2 * epsilon(255), 1, 255)).toBe(false);
    expect(lessEqual(1.00000001, 1, 21)).toBe(false);
  });

  it('keeps the M1 source window, including its lower bound', () => {
    const eps = epsilon(1.4);
    expect(m1WithinBounds(1, .6 - eps / 2, m1Bounds)).toBe(true);
    expect(m1WithinBounds(1, 1.4 + eps, m1Bounds)).toBe(true);
    expect(m1WithinBounds(1, .6 - 2 * eps, m1Bounds)).toBe(false);
    expect(m1WithinBounds(1, 1.4 + 2 * eps, m1Bounds)).toBe(false);
    expect(() => m1WithinBounds(0, 1, m1Bounds)).toThrow(); // Missing ratios belong to the owner.
  });

  it('uses the actual M2 2% cap while keeping toward and beyond exact', () => {
    expect(m2StructureVerdict(structure(1, 1.02), .5, .02)).toBe('within');
    expect(m2StructureVerdict(structure(1, 1.020000001), .5, .02)).toBe('failure');
    expect(m2StructureVerdict(structure(.5, .9), 1, .02)).toBe('named');
    expect(m2StructureVerdict(structure(.5, 1.02), 1, .02)).toBe('named');
    expect(m2StructureVerdict(structure(.5, 1.020000001), 1, .02)).toBe('failure');
    expect(m2StructureVerdict(structure(1, 1.2), 1, .02)).toBe('failure');
    // The sign product is positive but below epsilon: categorical directions are not caps.
    expect(m2StructureVerdict(structure(1e-10, 1e-10 + 1e-11),
      1e-10 + 2e-11, .02)).toBe('named');
    expect(m2StructureVerdict(structure(1e-10, 1e-10 - 1e-11),
      1e-10 + 2e-11, .02)).toBe('failure');
    // A true overshoot is not made "not beyond" by epsilon at the sign product.
    expect(m2StructureVerdict(structure(1e-10, 1e-10 + 2.4e-11),
      1e-10 + 2e-11, .02)).toBe('failure');
  });

  it('keeps L1 .055/.005 and refuses even near-equal changed native references', () => {
    const caps = l1Caps(0, .055, 0, .05, l1Bounds);
    expect(caps.error).toBe(.055);
    expect(caps.referenceError).toBe(.05);
    expect(caps.absoluteWithin).toBe(true);
    expect(caps.growthWithin).toBe(true);
    const near = l1Caps(0, .055 + epsilon(1) / 2, 0, .05, l1Bounds);
    expect(near.absoluteWithin).toBe(true);
    expect(near.growthWithin).toBe(true);
    const excess = l1Caps(0, .055 + 1e-9, 0, .05, l1Bounds);
    expect(excess.absoluteWithin).toBe(false);
    expect(excess.growthWithin).toBe(false);
    expect(() => l1Caps(1, 1, 1 + Number.EPSILON, 1, l1Bounds)).toThrow();
    // Named absolute/growth handling remains independent, with no extra allowed growth.
    const namedAbsolute = l1Caps(0, .066, 0, .066, l1Bounds);
    expect(namedAbsolute.absoluteWithin).toBe(false);
    expect(namedAbsolute.growthWithin).toBe(true);
  });

  it('refuses nonfinite raw and derived operands rather than returning a verdict', () => {
    expect(() => epsilon()).toThrow();
    for (const bad of [NaN, Infinity, -Infinity]) {
      expect(() => lessEqual(bad, 1)).toThrow();
      expect(() => lessEqual(1, bad)).toThrow();
      expect(() => lessEqual(1, 1, bad)).toThrow();
      expect(() => m1WithinBounds(bad, 1, m1Bounds)).toThrow();
      expect(() => m2StructureVerdict(structure(1, bad), 1, .02)).toThrow();
      expect(() => m2StructureVerdict(structure(1, 1), bad, .02)).toThrow();
      expect(() => l1Caps(0, bad, 0, 0, l1Bounds)).toThrow();
    }
    expect(() => m1WithinBounds(Number.MIN_VALUE, 1, m1Bounds)).toThrow();
    expect(() => l1Caps(-Number.MAX_VALUE, Number.MAX_VALUE,
      -Number.MAX_VALUE, 0, l1Bounds)).toThrow();
  });
});

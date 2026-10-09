/** Production material bridge beneath execution.py's prefit/root boundary.
 * Import is inert: it opens no candidate, native observation, coefficient or runtime document.
 * The CLI bootstrap installs the configured source guard before importing this module.
 */
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { isDeepStrictEqual } from 'node:util';

type Pin = { path: string; sha256: string };
type Material = Record<string, unknown>;
const leaves = ['lowEndStrength', 'lowEnd44', 'lowEnd96', 'lowEnd160'];
const hash = (raw: string | Buffer) => createHash('sha256').update(raw).digest('hex');
const canonical = (value: any): any => Array.isArray(value) ? value.map(canonical)
  : value && typeof value === 'object'
    ? Object.fromEntries(Object.keys(value).sort().map(key => [key, canonical(value[key])])) : value;
const held = (value: Material) => Object.fromEntries(Object.entries(value)
  .filter(([name]) => !leaves.includes(name)));

function assertGate0Identity(captured: Material): void {
  if (captured.lowEndStrength !== 0 || leaves.slice(1).some(name => {
    const row = captured[name];
    return !Array.isArray(row) || row.length !== 4 || row.some(value => value !== 0);
  })) throw Error('Captured gate0 endpoint must retain its declared zero chart identity');
}

export function assertHeldResolved(captured: Material, evaluated: Material): void {
  assertGate0Identity(captured);
  if (evaluated.lowEndStrength !== 1 || leaves.slice(1).some(name => {
    const row = evaluated[name];
    return !Array.isArray(row) || row.length !== 4 || row.some((v, i) =>
      typeof v !== 'number' || !Number.isFinite(v) || v < 0 || v > 1 || (i > 0 && v < row[i - 1]));
  })) throw Error('Evaluation chart is outside the declared live family');
  if (!isDeepStrictEqual(held(captured), held(evaluated))) {
    throw Error('Captured arguments cannot transfer across changed held material/sampling leaves');
  }
}

async function production() {
  // Load the additive adapters before G0's permanent runtime-only hook is installed. The outer
  // prospective root hook already guards these imports; G0's own source seal stays unchanged.
  const [builder, oracle, numerical] = await Promise.all([
    import('./candidate.ts'), import('./uniform-oracle.ts'),
    import('../../2026-10-08-w50-g0-declaration/audit/numerical.ts'),
  ]);
  const runtime = await numerical.loadRuntime();
  return { ...runtime, builder, oracle };
}

function checked(pin: Pin): string {
  if (!/^[0-9a-f]{64}$/.test(pin.sha256) || hash(readFileSync(pin.path)) !== pin.sha256) {
    throw Error('Changed candidate content pin');
  }
  return pin.path;
}

async function read(pin: Pin) {
  const runtime = await production();
  const parsed = runtime.candidate.readCandidateDocument(checked(pin));
  const position = parsed.document.glassTintAmount;
  if (![.25, .5].includes(position)) throw Error('Undeclared glass position');
  const materials: Record<string, any> = {};
  for (const scheme of ['light', 'dark'] as const) {
    let material = runtime.renderer.DEFAULT_MATERIAL_PROFILE;
    for (const pose of ['active', 'receded'] as const) {
      material = runtime.renderer.withMaterialOverrides(material, parsed.document[pose][scheme].patch ?? {});
      materials[`${pose}.${scheme}`] = material;
    }
  }
  return { ...runtime, parsed, position, materials };
}

export async function fixedGate0Joins(baseline: Pin) {
  const before = await read(baseline);
  for (const material of Object.values(before.materials)) assertGate0Identity(material);
  const joins: Record<string, unknown> = {};
  for (const pose of ['active', 'receded']) {
    joins[`${pose}.dark.${before.position}`] = await before.oracle.fixedJoins(before.materials[`${pose}.dark`]);
  }
  return { position: before.position, joins, capturedCandidate: baseline };
}

export async function proveTransfer(captured: Pin, evaluation: Pin) {
  const before = await read(captured), after = await read(evaluation);
  if (before.position !== after.position ||
      before.parsed.cssTierMappingSha256 !== after.parsed.cssTierMappingSha256) {
    throw Error('Transferred arguments require the held position and CSS mapping');
  }
  for (const pose of ['active', 'receded'] as const) {
    const light = `${pose}.light` as const;
    if (before.parsed.endpoints[light].sha256 !== after.parsed.endpoints[light].sha256 ||
        !isDeepStrictEqual(before.materials[light], after.materials[light])) {
      throw Error('Light endpoint bytes/material changed');
    }
    assertHeldResolved(before.materials[`${pose}.dark`], after.materials[`${pose}.dark`]);
  }
  return { schema: 'w50-held-sampling-proof-1', position: before.position,
    capturedCandidate: captured, evaluationCandidate: evaluation,
    heldMaterialSha256: hash(JSON.stringify(canonical(Object.fromEntries(
      Object.entries(before.materials).map(([name, material]) => [name, held(material)]))))),
    lightEndpointSha256s: ['active.light', 'receded.light'].map(slot =>
      before.parsed.endpoints[slot as 'active.light' | 'receded.light'].sha256),
    cssTierMappingSha256: before.parsed.cssTierMappingSha256 };
}

/** The existing builder owns document composition/digests and DL5o's X76 records; no parallel
 * implementation. */
export async function assembleCandidate(baseline: Pin, charts: unknown, output: string, provenance: unknown) {
  const { builder } = await production();
  return builder.buildCandidate(baseline, charts, output, provenance);
}

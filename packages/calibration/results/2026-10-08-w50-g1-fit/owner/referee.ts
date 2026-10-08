import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
import { bindSource, assertedNumbers } from './source.ts';
import { decodePng } from '../../../src/image.ts';
import { oklabDeltaE } from '../../../src/metrics/perceptual.ts';
import { opaqueGlassViolations } from '../../../scripts/no-opaque-glass.ts';

export const OWNER_SOURCE_SHA256 = '5b83ea260b3ccf28bf0f4809fa71fa6c41a9ad35faf6411981cd2e50b68012b0';
export const X76_SOURCE_SHA256 = 'bf3a59e651dce26cef91d6ba901e65d3e10740aaa22e469c1239d010c29d623c';
const CAL = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
const OWNER = resolve(CAL, 'test/adopted-thresholds.test.ts');
const C1_SCOPE = "W32 C1 — the shadow's exterior shape, per span (claims §5.169)";
const X1_SCOPE = 'W33 X1 — the native-black exterior stays black (claims §5.173)';
const L1_SCOPE = 'W36 L1 — fixed-native-silhouette level and pre-fit growth (claims §5.180)';
export type Row = any;
export type Pin = { path: string; sha256: string };
export type State = 'MEASURED' | 'UNMEASURED' | 'NOT_APPLICABLE';
export type Evidence = { state: State; verdict?: 'within' | 'named-miss' | 'failure' | 'reported';
  reason?: string; native?: unknown; current?: unknown; candidate?: unknown;
  reference?: unknown; [key: string]: unknown };
const sha = (bytes: Uint8Array | string) => createHash('sha256').update(bytes).digest('hex');
export const identity = (r: Row) => `${r.key.profileKey}/${r.key.web.renderer}/${r.key.sceneId}`;
const cellKey = (r: Row) => `${r.key.profileKey}/${r.key.sceneId}`;
const position = (r: Row) => r.key.profileKey.endsWith('-glass0.25') ? .25
  : r.key.profileKey.endsWith('-glass0.5') ? .5 : undefined;
const value = (r: Row | undefined, field: string): number | undefined => {
  const v = r?.material?.[field]?.value;
  return typeof v === 'number' && Number.isFinite(v) ? v : undefined;
};
/** The owner test's own reading (adopted-thresholds.test.ts, the L1 block's `value`): a metric
 * the row does not carry reads as null, exactly as a recorded `{value:null}` does. The macOS 27
 * generations omit the means of the four dark inactive dark-solid cells rather than nulling
 * them, and the owner excuses those cells under MISSING/MISSING_025 either way; reading the raw
 * field here would leave `undefined`, which no named exclusion admits. A null entry throws, as
 * the owner's `m.value` does, rather than reading as a missing mean. */
const ownerReading = (r: Row | undefined, field: string): unknown => {
  const m = r?.material?.[field];
  return typeof m === 'object' ? m.value : null;
};
const na = (reason: string): Evidence => ({ state: 'NOT_APPLICABLE', reason });
const unread = (reason: string): Evidence => ({ state: 'UNMEASURED', reason });
const measured = (data: Record<string, unknown>, verdict: Evidence['verdict']): Evidence =>
  ({ state: 'MEASURED', ...data, verdict });
const standard = (r: Row) => r.key.profileKey.startsWith('apple-macos-27.0-')
  && r.key.profileKey.includes('-standard-') && position(r) !== undefined;

/** Source-only operation: reads source, not results, fixtures, captures or matrices. */
export function loadContracts(): Record<string, any> & {
  c1: Record<string, any>; text: string; source: Pin;
} {
  const text = readFileSync(OWNER, 'utf8');
  const constants = bindSource(text, OWNER_SOURCE_SHA256, [
    'CHROMA_CELL_MIN', 'CHROMA_CELL_MAX', 'CHROMA_MEDIAN_MIN', 'CHROMA_MEDIAN_MAX',
    'CHROMA_STRUCTURE_TOLERANCE', 'structureVerdict', 'MISSED_27_ROWS',
    'COHERENCE_ROWS', 'REGRESSION_FLOORS', 'NO_SHAPE_AXIS_SCENES', 'DARK_PROFILES',
    'the adopted fidelity gate (claims §5, adopted 2026-08-26 / -29 / -30)/COHERENCE_GATED',
    'UNGATED_PROFILES',
    'the adopted fidelity gate (claims §5, adopted 2026-08-26 / -29 / -30)/it:measures coherence on every profile the rows do not gate/notCoherenceGated',
    'GLASS025_M2_RULED_FAILURES',
    'PREDICATE_EXCLUDES', 'WELL_CONDITIONED_AREA_RATIO', 'reading', 'name', 'isWellConditioned',
    'GLASS025_REFERENCE', `${L1_SCOPE}/BASELINE`, `${L1_SCOPE}/MISSING`,
    `${L1_SCOPE}/MISSING_025`, `${L1_SCOPE}/MISSES`, `${L1_SCOPE}/GROWTH_RULED`,
    `${L1_SCOPE}/growthVerdict`, `${X1_SCOPE}/BLACK`,
  ]);
  const c1 = bindSource(text, OWNER_SOURCE_SHA256, [
    'C1_TOLERANCE', 'C1_SPANS', 'upperMiddle', 'ADMITTED_BANDS', 'CONTRIBUTING_CELLS',
    'BAND_WIDTH_CSS_PX', 'MIN_BACKDROP_SUPPORT', 'axisValue',
  ].map(n => `${C1_SCOPE}/${n}`));
  const l1 = assertedNumbers(text,OWNER_SOURCE_SHA256,['CUT.absoluteBound','CUT.growthBound']);
  const m1 = bindSource(text,OWNER_SOURCE_SHA256,[
    "W31 M1 / M2 — the body's chroma and the structure it is read over (claims §5.165)/CONTRIBUTING_CELLS",
  ]).CONTRIBUTING_CELLS;
  return { ...constants, c1, l1, m1, text, source: { path: OWNER, sha256: OWNER_SOURCE_SHA256 } };
}
export type Contracts = ReturnType<typeof loadContracts>;

export function pinnedBytes(pin: Pin): Buffer {
  const bytes = readFileSync(pin.path);
  if (sha(bytes) !== pin.sha256) throw new Error(`Evidence hash changed: ${pin.path}`);
  return bytes;
}
/** Role-sensitive descriptor parsing: a pair is not an unordered bag of document hashes. */
export function documentRoles(row: Row): Record<'materialProfile'|'recededProfile', Pin> {
  const matches = [...row.key.web.capturePath.matchAll(/(materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})(?![0-9a-f])/g)];
  if (matches.length !== 2 || new Set(matches.map(m => m[1])).size !== 2
    || new Set(matches.map(m => m[2])).size !== 2) throw new Error('Row lacks role-bound document pair');
  return Object.fromEntries(matches.map(m => [m[1],{path:m[2],sha256:m[3]}])) as
    Record<'materialProfile'|'recededProfile', Pin>;
}
export function assertDocumentPair(row: Row, activeSha256: string, recededSha256: string) {
  const pair = documentRoles(row);
  if (![activeSha256,recededSha256].every(hash => /^[0-9a-f]{64}$/.test(hash))
    || pair.materialProfile.sha256 !== activeSha256.slice(0,12)
    || pair.recededProfile.sha256 !== recededSha256.slice(0,12)) {
    throw new Error('Document pair differs from row roles');
  }
}
export function readMatrix(bytes: Uint8Array, expectedSha256: string): Row[] {
  if (sha(bytes) !== expectedSha256) throw new Error('Matrix hash changed');
  const envelope = JSON.parse(Buffer.from(bytes).toString());
  if (envelope.schemaVersion !== 5 || !Array.isArray(envelope.cells)) {
    throw new Error('Expected schema5 canonical envelope');
  }
  const seen = new Set<string>();
  for (const row of envelope.cells) {
    const key = identity(row);
    if (seen.has(key)) throw new Error(`Ambiguous matrix row ${key}`);
    seen.add(key);
  }
  return envelope.cells;
}

/** Cell arithmetic only; the public evaluator also verifies membership, pixels and aggregates.
 * Baseline is the ORIGINAL fixed owner reference, never automatically the current generation.
 */
export function classifyCell(C: Contracts, r: Row, baseline?: Row): Record<string, Evidence> {
  const out = Object.fromEntries(['M1','M2','L1'].map(a => [a, na('Outside owner population')])) as Record<string,Evidence>;
  if (!standard(r) || r.key.web.renderer !== 'webgpu' || r.tier !== 'texture'
    || !['calibration','validation'].includes(r.fixtureSet)) return out;
  const n = value(r, 'interiorMeanNative'), w = value(r, 'interiorMeanWeb');
  const bn = value(baseline, 'interiorMeanNative'), bw = value(baseline, 'interiorMeanWeb');
  const missing = [...C.MISSING, ...C.MISSING_025].includes(cellKey(r));
  if (n === undefined || w === undefined || bn === undefined || bw === undefined) {
    const rawMeans=[r,baseline].flatMap(row=>['interiorMeanNative','interiorMeanWeb']
      .map(field=>ownerReading(row,field)));
    const namedExclusion=missing && baseline!==undefined && n===bn
      && rawMeans.every(v=>v===null || (typeof v==='number' && Number.isFinite(v)))
      && rawMeans.slice(0,2).includes(null);
    out.L1 = { ...unread('Missing fixed-native mean or original baseline'), namedExclusion };
  } else {
    if (n !== bn) throw new Error(`Native L1 reading changed: ${cellKey(r)}`);
    const error = Math.abs(w-n), referenceError = Math.abs(bw-bn), growth = error-referenceError;
    const absolute = error <= C.l1['CUT.absoluteBound'] ? 'within'
      : C.MISSES.includes(cellKey(r)) ? 'named' : 'failure';
    const growthVerdict = position(r) === .5 ? C.growthVerdict(cellKey(r), growth)
      : growth <= C.l1['CUT.growthBound'] ? 'within' : 'failure';
    out.L1 = measured({ native: n, candidate: w, reference: bw, error, referenceError, growth,
      absolute, growthVerdict }, [absolute,growthVerdict].includes('failure') ? 'failure'
      : [absolute,growthVerdict].includes('named') ? 'named-miss' : 'within');
  }
  if (!r.key.sceneId.startsWith('photo__') || r.key.sceneId.includes('-tint-')) return out;
  const cn = value(r, 'chromaStructureRatioNative'), cw = value(r, 'chromaStructureRatioWeb');
  if (cn === undefined || cw === undefined || cn === 0) out.M1 = unread('Missing chroma ratio');
  else {
    const R = cw/cn, named = C.MISSED_27_ROWS[`${C.name(r)} :: chromaStructureRatioR`];
    out.M1 = measured({ native: cn, candidate: cw, R }, R >= C.CHROMA_CELL_MIN
      && R <= C.CHROMA_CELL_MAX ? 'within' : named ? 'named-miss' : 'failure');
  }
  const ns = value(r,'interiorStdDevNative'), ws = value(r,'interiorStdDevWeb');
  const bs = value(baseline,'interiorStdDevWeb');
  if (ns === undefined || ws === undefined || bs === undefined || bs === 0) {
    out.M2 = unread('Missing original structure baseline or structure reading');
  } else {
    const delta = (ws-bs)/bs;
    const verdict = C.structureVerdict({ interiorStdDevWebReference: bs,
      interiorStdDevWeb: ws, structureDeltaFraction: delta }, ns);
    const originalOwnerNamedListMember = Object.hasOwn(C.MISSED_27_ROWS,
      `${C.name(r)} :: interiorStdDevStructureDelta`);
    const originalOwnerRuledFailure = position(r) === .25
      && C.GLASS025_M2_RULED_FAILURES.includes(C.name(r));
    const ruled = verdict === 'failure' && originalOwnerRuledFailure;
    out.M2 = measured({ native: ns, candidate: ws, reference: bs, structureDeltaFraction: delta,
      structureVerdict: verdict, originalOwnerNamedListMember, originalOwnerRuledFailure,
      wouldRequireNewOwnerRecord: verdict !== 'within' && (!originalOwnerNamedListMember
        || (verdict === 'failure' && !originalOwnerRuledFailure)),
      ownerContract: ruled ? 'Original ruled failure against its fixed original reference'
        : 'Source directional verdict; named outcomes require their original owner record' },
      verdict === 'named' || ruled ? 'named-miss' : verdict);
  }
  return out;
}

export interface Capture {
  web: Pin; native: Pin; backdrop: Pin; metadata: Pin;
  /** Full document digests, by descriptor path; receded included even on active rows. */
  documents: Record<string,string>;
}
export function validateCapture(row: Row, capture: Capture, declaration?: any) {
  captureBytes(row, capture, declaration);
}
function captureBytes(row: Row, capture: Capture, declaration?: any) {
  documentRoles(row);
  const metadata = JSON.parse(pinnedBytes(capture.metadata).toString());
  if (metadata.capturePath !== row.key.web.capturePath) throw new Error('Capture descriptor differs from row');
  if (metadata.sceneId !== row.key.sceneId) throw new Error('Capture scene differs from row');
  if (metadata.renderer !== row.key.web.renderer) throw new Error('Capture renderer differs from row');
  if (typeof metadata.samplingBackend !== 'string' || !metadata.samplingBackend
    || metadata.samplingBackend !== row.key.web.samplingBackend) {
    throw new Error('Capture sampling backend differs from row');
  }
  const matches = [...metadata.capturePath.matchAll(/(?:materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})/g)];
  if (matches.length !== Object.keys(capture.documents).length || matches.length !== 2
    || new Set(matches.map((m: any) => m[1])).size !== 2
    || matches.some((m: any) => !/^[0-9a-f]{64}$/.test(capture.documents[m[1]] ?? '')
      || capture.documents[m[1]]?.slice(0,12) !== m[2])) {
    throw new Error('Capture does not bind the complete candidate document pair');
  }
  const bytes = { web: pinnedBytes(capture.web), native: pinnedBytes(capture.native),
    backdrop: pinnedBytes(capture.backdrop) };
  const images = Object.values(bytes).map(decodePng);
  const size = [images[0]!.width, images[0]!.height];
  if (JSON.stringify(metadata.pixelSize) !== JSON.stringify(size)
    || images.some(image => image.width !== size[0] || image.height !== size[1])) {
    throw new Error('Capture/native/backdrop pixel size or dimensions differ');
  }
  const scale = row.key.profileKey.includes('-2x-') ? 2 : 1;
  if (declaration && (size[0] !== declaration.canvas.width * scale
    || size[1] !== declaration.canvas.height * scale)) {
    throw new Error('Capture pixel size differs from declared canvas and profile scale');
  }
  const viewport = metadata.capturePath.match(/viewport=(\d+)x(\d+)/);
  const dpr = metadata.capturePath.match(/deviceScaleFactor=([\d.]+)/);
  if ((dpr && Number(dpr[1]) !== scale) || (viewport
    && (Number(viewport[1]) * scale !== size[0] || Number(viewport[2]) * scale !== size[1]))) {
    throw new Error('Capture pixel size differs from descriptor viewport/scale');
  }
  return bytes;
}

/** Both source-owner masks are recounted against actual hash-checked pixels. */
export function recountBlack(C: Contracts, row: Row, capture: Capture, declaration: any): Evidence {
  const bytes = captureBytes(row,capture,declaration);
  const scene = declaration.scenes.find((s: any) => s.id === row.key.sceneId);
  const fixtures = resolve(CAL,'../../apps/reference-apple/fixtures');
  const scale = row.key.profileKey.includes('-2x-') ? 2 : 1;
  const virtual = new Map([
    [resolve(fixtures,row.key.profileKey,`${row.key.sceneId}.png`),bytes.native],
    [resolve(fixtures,'backgrounds',`${scene.background}@${scale}x.png`),bytes.backdrop],
    [capture.web.path,bytes.web],
  ]);
  const api = bindSource(C.text, OWNER_SOURCE_SHA256, [`${X1_SCOPE}/key`,`${X1_SCOPE}/blackReading`], {
    PACKAGE_ROOT: CAL, resolve, decodePng, declaration,
    scenes: new Map(declaration.scenes.map((s: any) => [s.id,s])),
    readFileSync: (path: string) => {
      if (!virtual.has(path)) throw new Error(`Unbound X1 image ${path}`);
      return virtual.get(path);
    },
    expect: (v: unknown) => ({toEqual: (expected: unknown) => assert.deepEqual(v,expected)}),
  });
  const readings = api.blackReading(row.key.profileKey,row.key.sceneId,capture.web.path);
  const masks = [readings.integer,readings.analytic];
  if (masks.some(m => !m.pixels)) return {...unread('X1 zero black support'), readings};
  return measured({readings, provenance:capture}, masks.some(m => m.aboveZero || m.aboveOne)
    ? 'failure' : 'within');
}

/** Source membership is distinct from W50's optional diagnostic coverage. The adapter uses
 * caller-pinned document generations in place of the owner's live shipped-document registry;
 * all profile and scene-role restrictions are the original source declarations. */
export function coherenceOwnerScope(C: Contracts, row: Row, declaration: any) {
  const {inGatedBed} = bindSource(C.text,OWNER_SOURCE_SHA256,['inRecordedRole','inGatedBed'],{
    RECORDED_SCENES:new Set(declaration.split.recorded ?? []),
    INACTIVE_SCENES:new Set(declaration.scenes.filter((s:any)=>s.state==='inactive').map((s:any)=>s.id)),
    atAShippedDocument:()=>true, // The API already bound the row to a pinned generation.
  });
  const css=row.key.web.renderer==='css' && row.tier==='dom';
  const inBed=css && inGatedBed(row);
  const sourceOwnerNumericWindowAdopted=inBed && C.COHERENCE_GATED.includes(row.key.profileKey);
  const sourceOwnerPresenceRequired=inBed && (sourceOwnerNumericWindowAdopted
    || C.notCoherenceGated.includes(row.key.profileKey));
  return {sourceOwnerPresenceRequired,sourceOwnerNumericWindowAdopted,
    diagnosticOnly:css && !sourceOwnerPresenceRequired};
}

/** Absent twins remain UNMEASURED; the caller records whether presence was required.
 * Whole-canvas ΔE is recomputed, never inferred from means. */
export function pairedCoherence(C: Contracts, css: Row, gpu: Row | undefined,
  cssCapture?: Capture, gpuCapture?: Capture,
  numericWindowAdopted = C.COHERENCE_GATED.includes(css.key.profileKey)): Evidence {
  if (!gpu || !cssCapture || !gpuCapture) return unread('Coherence requires both same-candidate captures');
  if (cellKey(css) !== cellKey(gpu) || css.key.web.renderer !== 'css' || gpu.key.web.renderer !== 'webgpu') {
    throw new Error('Wrong coherence twin');
  }
  const docs = (c: Capture) => JSON.stringify(Object.entries(c.documents).sort());
  if (docs(cssCapture) !== docs(gpuCapture) || cssCapture.native.sha256 !== gpuCapture.native.sha256) {
    throw new Error('Coherence twins are not the same candidate/native generation');
  }
  const cssBytes = captureBytes(css,cssCapture), gpuBytes = captureBytes(gpu,gpuCapture);
  const deltaE = oklabDeltaE(decodePng(gpuBytes.web),decodePng(cssBytes.web)).mean;
  const wm = value(css,'interiorMeanWeb'), gm = value(gpu,'interiorMeanWeb');
  const noShape = C.NO_SHAPE_AXIS_SCENES[css.key.profileKey]?.dom ?? [];
  const ratio = wm === undefined || gm === undefined || wm === 0 ? undefined : gm/wm;
  const deltaPass = deltaE <= C.COHERENCE_ROWS.crossTierOklabDeltaEMean.threshold;
  if (ratio === undefined && !noShape.includes(css.key.sceneId)) {
    return {...unread('Missing non-excluded coherence interior ratio'),deltaE};
  }
  // The macOS 27 owner requires these readings, but adopts no numeric coherence window.
  // Counterfactual comparisons are diagnostic, never the verdict or a new exception budget.
  if (!numericWindowAdopted) return measured({deltaE,ratio:ratio ?? null,
    ratioNotApplicable:ratio === undefined,numericWindowAdopted:false,
    reason:'Numerical coherence windows are not adopted here; caller reports source presence scope',
    counterfactual:{deltaEWithin:deltaPass,ratioWithin:ratio === undefined ? null
      : ratio >= C.COHERENCE_ROWS.interiorLevelRatioGpuOverCss.min
        && ratio <= C.COHERENCE_ROWS.interiorLevelRatioGpuOverCss.max,
      verdict:deltaPass && (ratio === undefined || (ratio >= C.COHERENCE_ROWS.interiorLevelRatioGpuOverCss.min
        && ratio <= C.COHERENCE_ROWS.interiorLevelRatioGpuOverCss.max)) ? 'within' : 'failure'},
    provenance:{css:cssCapture,gpu:gpuCapture}},'reported');
  const conditioned = C.isWellConditioned(css);
  const exclusion = !conditioned && C.PREDICATE_EXCLUDES.includes(C.name(css));
  if (!conditioned && !exclusion) return measured({deltaE,ratio,reason:'New conditioning exclusion'},'failure');
  const floor = C.REGRESSION_FLOORS[`${C.name(css)} :: interiorLevelRatioGpuOverCss`];
  const { min,max } = C.COHERENCE_ROWS.interiorLevelRatioGpuOverCss;
  const ratioPass = ratio === undefined || exclusion || (floor
    ? floor.measured > max ? ratio <= floor.floor : ratio >= floor.floor
    : ratio >= min && ratio <= max);
  return measured({deltaE,ratio:ratio ?? null,conditioned,namedExclusion:exclusion,
    ratioNotApplicable: ratio === undefined, provenance:{css:cssCapture,gpu:gpuCapture}},
    deltaPass && ratioPass ? 'within' : 'failure');
}

/** X76's source algorithm (seal.ts197–230): values are flattened leaf paths, and the
 * full active resolved object is supplied by the candidate's production resolver. Intrinsic
 * evidence is deliberately separate from native/current image measurements. */
export function checkInheritance(input: {activeResolved: any; activePatch: any;
  activeEntries: Record<string,any>; beforePatch: any; beforeEntries: Record<string,any>;
  candidatePatch: any; methods: Record<string,any>}) {
  const flatten = (value: any, prefix = '', out: Record<string,any> = {}) => {
    for (const [k,v] of Object.entries(value)) {
      const path = prefix ? `${prefix}.${k}` : k;
      if (v && typeof v === 'object' && !Array.isArray(v)) flatten(v,path,out);
      else out[path] = v;
    }
    return out;
  };
  const mine = flatten(input.candidatePatch), before = flatten(input.beforePatch);
  const active = flatten(input.activePatch), resolved = flatten(input.activeResolved);
  const equal = (a: unknown,b: unknown) => JSON.stringify(a) === JSON.stringify(b);
  const moved = Object.keys(mine).filter(k => !equal(mine[k],before[k]));
  const inherited = Object.keys(mine).filter(k => equal(mine[k],resolved[k])
    && (input.beforeEntries[k]?.status !== 'measured' || moved.includes(k)));
  inherited.push(...Object.keys(active).filter(k => input.activeEntries[k]?.status === 'measured' && !(k in mine)));
  const methods = inheritanceMethods();
  const held = methods.isHold;
  const fitted = methods.isMethod;
  const missing = inherited.filter(k => !(moved.includes(k) && fitted(input.methods[k])) && !held(input.methods[k]));
  for (const k of moved) if (!inherited.includes(k) && !fitted(input.methods[k])) missing.push(k);
  return {state:'MEASURED' as const,verdict:missing.length ? 'failure' : 'within',
    inherited: [...new Set(inherited)].sort(), moved:moved.sort(),missing:[...new Set(missing)].sort(),
    source:'results/2026-10-07-w49a-g0-declaration/seal/seal.ts:197–230'};
}
export function checkOpacity(posedEndpoints: Record<string,any>) {
  return Object.fromEntries(Object.entries(posedEndpoints).map(([endpoint,patch]) => {
    const violations = opaqueGlassViolations(patch);
    return [endpoint,{state:'MEASURED',verdict:violations.length ? 'failure' : 'within', violations,
      domain:'both tiers; all material variants; dpr1,2; integer CSS spans0..1024; nominal policy'}];
  }));
}

export function inheritanceMethods() {
  const sealSource = resolve(CAL,'results/2026-10-07-w49a-g0-declaration/seal/seal.ts');
  return bindSource(readFileSync(sealSource,'utf8'), X76_SOURCE_SHA256, ['isHold','isMethod']);
}

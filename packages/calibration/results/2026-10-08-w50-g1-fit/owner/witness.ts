import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { isDeepStrictEqual } from 'node:util';
import ts from 'typescript';
import { MATERIAL_VARIANTS } from '@vitrea/renderer-webgpu';
import { X75_MAX_ALPHA_BASE, X75_FLOAT_ALLOWANCE, X75_SPAN_MAX_CSS_PX,
  X75_DEVICE_PIXEL_RATIOS } from '../../../scripts/no-opaque-glass.ts';
import { loadContracts, pinnedBytes, identity, X76_SOURCE_SHA256, type Evidence, type Pin } from './referee.ts';
import { prepareCurrent, type Prepared, type OwnerReport } from './api.ts';

const HERE=dirname(fileURLToPath(import.meta.url));
const CAL=resolve(HERE,'../../..');
const M1_SCOPE="W31 M1 / M2 — the body's chroma and the structure it is read over (claims §5.165)";
const C1_SCOPE="W32 C1 — the shadow's exterior shape, per span (claims §5.169)";
const X1_SCOPE='W33 X1 — the native-black exterior stays black (claims §5.173)';
const L1_SCOPE='W36 L1 — fixed-native-silhouette level and pre-fit growth (claims §5.180)';
const GATE_SCOPE='the adopted fidelity gate (claims §5, adopted 2026-08-26 / -29 / -30)';
const sha=(bytes:Uint8Array)=>createHash('sha256').update(bytes).digest('hex');
const pin=(path:string):Pin=>({path,sha256:sha(readFileSync(path))});
export const IMAGE_AXES=['M1','M2','C1','X1','L1','E2','coherence'] as const;
export interface OwnerRow {profile:string;renderer:string;scene:string;statistic:string}
interface ReadingSchema {
  requiredFinite:string[];
  requiredArrays:string[];
  conditionalFinite:{unless:{field:string;equals:unknown};paths:string[]}[];
  unmeasuredExceptions:({kind:'named-cell';identity:'profile/scene';keys:string[];
    evidenceEquals:Record<string,unknown>}|{kind:'diagnostic-only';evidenceEquals:Record<string,unknown>})[];
  aggregate:null|{requiredFinite:string[];nonemptyObjects:{field:string;requiredFinite:string[]}[]};
}
interface AxisContract {
  sourceSelectors:string[]; limits:Record<string,any>; applicability:Record<string,any>;
  exclusions:Record<string,any>; readingSchema:ReadingSchema;
}
export interface OwnerContracts {
  schema:'w50-owner-contracts-1'; ownerSource:Pin; readerSources:Record<string,Pin>;
  axes:Record<typeof IMAGE_AXES[number],AxisContract>;
  intrinsic:Record<'X75'|'X76',Record<string,any>>;
}
const readingSchema=(requiredFinite:string[],extra:Partial<ReadingSchema>={}):ReadingSchema=>({
  requiredFinite,requiredArrays:[],conditionalFinite:[],unmeasuredExceptions:[],aggregate:null,...extra,
});

/** X1's target object is an inline source assertion, not a copied W50 budget. The
 * owner hash was checked by loadContracts; only this literal AST node is read. */
function x1Targets(text:string) {
  const source=ts.createSourceFile('owner.ts',text,ts.ScriptTarget.Latest,true);
  const matches:Record<string,number>[]=[];
  function visit(node:ts.Node) {
    if(ts.isCallExpression(node)&&ts.isPropertyAccessExpression(node.expression)
      &&node.expression.name.text==='toEqual'&&ts.isCallExpression(node.expression.expression)) {
      const expectation=node.expression.expression;
      if(ts.isIdentifier(expectation.expression)&&expectation.expression.text==='expect'
        &&expectation.arguments[0]?.getText(source)==='CUT.targets') {
        const object=node.arguments[0];
        if(!object||!ts.isObjectLiteralExpression(object)) throw new Error('X1 target assertion changed');
        const entries=object.properties.map(property=>{
          if(!ts.isPropertyAssignment(property)||!ts.isNumericLiteral(property.initializer)
            ||(!ts.isIdentifier(property.name)&&!ts.isStringLiteral(property.name))) {
            throw new Error('X1 target assertion is not a numeric literal object');
          }
          return [property.name.text,Number(property.initializer.text)] as const;
        });
        matches.push(Object.fromEntries(entries));
      }
    }
    ts.forEachChild(node,visit);
  }
  visit(source);
  if(matches.length!==1) throw new Error('Missing/ambiguous X1 target assertion');
  return matches[0]!;
}

/** Source-only snapshot. This reads no matrix, profile document, image or measured result.
 * Its own readers are pinned, so the snapshot cannot retain old limits after an adapter edit.
 * A root must pin the resulting JSON before consuming it as an ownerBudget witness. */
export function ownerContracts(python:string):OwnerContracts {
  const C=loadContracts();
  const edge=JSON.parse(execFileSync(python,['-I','-B',resolve(HERE,'edge.py'),'--contracts'],
    {encoding:'utf8'}));
  const readerSources=Object.fromEntries([
    'api.ts','referee.ts','source.ts','intrinsic.ts','edge.py','bridge.ts','witness.ts',
  ].map(name=>[name,pin(resolve(HERE,name))]));
  readerSources.opacity=pin(resolve(CAL,'scripts/no-opaque-glass.ts'));
  readerSources.candidateDocument=pin(resolve(CAL,'scripts/candidate-document.ts'));
  readerSources.seal=pin(resolve(CAL,'results/2026-10-07-w49a-g0-declaration/seal/seal.ts'));
  if(readerSources.seal.sha256!==X76_SOURCE_SHA256) throw new Error('X76 source contract changed');
  for(const [name,value] of Object.entries(edge.sources)) readerSources[`E2/${name}`]=value as Pin;
  const named=(metric:string)=>Object.keys(C.MISSED_27_ROWS).filter(k=>k.endsWith(` :: ${metric}`)).sort();
  const photoScope={reader:'referee.ts:classifyCell',tier:'texture',renderer:'webgpu',
    profiles:'macOS27 standard at glass0.25/0.5',sets:['calibration','validation'],
    scenes:'photo__ prefix, excluding -tint-'};
  const baseline={glass05:C.BASELINE,glass025:C.GLASS025_REFERENCE};
  const axes:OwnerContracts['axes']={
    M1:{sourceSelectors:['CHROMA_CELL_MIN','CHROMA_CELL_MAX','CHROMA_MEDIAN_MIN',
      'CHROMA_MEDIAN_MAX','MISSED_27_ROWS',`${M1_SCOPE}/CONTRIBUTING_CELLS`],
      limits:{cell:{min:C.CHROMA_CELL_MIN,max:C.CHROMA_CELL_MAX},
        median:{min:C.CHROMA_MEDIAN_MIN,max:C.CHROMA_MEDIAN_MAX},contributingCells:C.m1},
      applicability:photoScope,exclusions:{namedKeys:named('chromaStructureRatioR')},
      readingSchema:readingSchema(['native','candidate','R'],{
        aggregate:{requiredFinite:['median','cells'],nonemptyObjects:[]}})},
    M2:{sourceSelectors:['CHROMA_STRUCTURE_TOLERANCE','structureVerdict','MISSED_27_ROWS',
      'GLASS025_M2_RULED_FAILURES','GLASS025_REFERENCE',`${L1_SCOPE}/BASELINE`],
      limits:{structureDeltaTolerance:C.CHROMA_STRUCTURE_TOLERANCE,
        directionalVerdict:'structureVerdict',baseline},applicability:photoScope,
      exclusions:{namedKeys:named('interiorStdDevStructureDelta'),ruledFailures:C.GLASS025_M2_RULED_FAILURES,
        newOwnerRecords:'wouldRequireNewOwnerRecord remains explicit; no automatic W50 authorisation'},
      readingSchema:readingSchema(['native','candidate','reference','structureDeltaFraction'])},
    C1:{sourceSelectors:[`${C1_SCOPE}/deriveClause`,`${C1_SCOPE}/C1_TOLERANCE`,`${C1_SCOPE}/C1_SPANS`,
      `${C1_SCOPE}/ADMITTED_BANDS`,`${C1_SCOPE}/CONTRIBUTING_CELLS`,`${C1_SCOPE}/MIN_BACKDROP_SUPPORT`],
      limits:{tolerance:C.c1.C1_TOLERANCE,spans:C.c1.C1_SPANS,admittedBands:C.c1.ADMITTED_BANDS,
        bandWidths:C.c1.BAND_WIDTH_CSS_PX,minimumBackdropSupport:C.c1.MIN_BACKDROP_SUPPORT,
        counts05:C.c1.CONTRIBUTING_CELLS,counts025:'Exact contributing membership of frozen current input'},
      applicability:{reader:'api.ts:c1Rows/c1Evidence',sourcePredicate:'deriveClause',
        statistic:'upperMiddle per glass/bed/span; per-cell T is reported, not independently bounded'},
      exclusions:{sourcePredicate:'deriveClause excludes inactive, holdout, recorded, nonstandard/nontexture, '
        +'unsupported spans/backdrop support and incomplete admitted band sets; fixed counts must remain complete'},
      readingSchema:readingSchema(['T'],{requiredArrays:['native','candidate'],
        aggregate:{requiredFinite:[],nonemptyObjects:[{field:'perBed',requiredFinite:['T','cells']}]}})},
    X1:{sourceSelectors:[`${X1_SCOPE}/BLACK`,`${X1_SCOPE}/blackReading`,'expect(CUT.targets).toEqual'],
      limits:{targets:x1Targets(C.text),masks:['integer','analytic'],support:'Both masks require positive counted pixels'},
      applicability:{reader:'api.ts:blackMember',profiles:'macOS27 standard at both glass positions',
        renderer:'webgpu',tier:'texture',sets:['calibration','validation','probe'],
        poses:['rest','inactive'],backgrounds:C.BLACK,kinds:['rrect','capsule']},
      exclusions:{namedMisses:[],compositesAndAccessibility:'Outside the source population'},
      readingSchema:readingSchema(['integer','analytic'].flatMap(mask=>[
        'backdropBlack','nativeNonzero','pixels','aboveZero','aboveOne','fraction',
      ].map(field=>`readings.${mask}.${field}`)))},
    L1:{sourceSelectors:['expect(CUT.absoluteBound).toBe','expect(CUT.growthBound).toBe',
      `${L1_SCOPE}/BASELINE`,'GLASS025_REFERENCE',`${L1_SCOPE}/MISSING`,`${L1_SCOPE}/MISSING_025`,
      `${L1_SCOPE}/MISSES`,`${L1_SCOPE}/GROWTH_RULED`,`${L1_SCOPE}/growthVerdict`],
      limits:{absolute:C.l1['CUT.absoluteBound'],growth:C.l1['CUT.growthBound'],baseline},
      applicability:{reader:'referee.ts:classifyCell',profiles:'macOS27 standard at both glass positions',
        tier:'texture',renderer:'webgpu',sets:['calibration','validation']},
      exclusions:{namedMissingMeans:[...C.MISSING,...C.MISSING_025],absoluteMisses:C.MISSES,
        growthRuled:[...C.GROWTH_RULED].sort(),missingOriginalReference:'Never excused by a named absent mean'},
      readingSchema:readingSchema(['native','candidate','reference','error','referenceError','growth'],{
        unmeasuredExceptions:[{kind:'named-cell',identity:'profile/scene',keys:[...C.MISSING,...C.MISSING_025],
          evidenceEquals:{namedExclusion:true}}]})},
    E2:{sourceSelectors:['edge.py:SOURCES','cut_e2','single_geometry','group_geometry'],
      limits:{mode:'reported-only',minimumBinPixels:edge.minimumBinPixels,
        diagnosticNamedBinGrowthCodes:edge.namedBinGrowthCodes,noAbsoluteGate:true,
        referenceByPosition:{glass025:C.GLASS025_REFERENCE,glass05:'Caller-pinned W50 frozen current price, not a historical owner bound'}},
      applicability:{reader:'api.ts:edgeMember',profiles:'macOS27 standard at both glass positions',
        renderer:'webgpu',samplingBackend:'gpu-texture',sets:['calibration','validation','probe'],
        pose:'rest',kinds:['rrect','capsule','declared three-capsule group']},
      exclusions:{holdout:'Outside population',unmeasured:'Empty supported-bin population remains UNMEASURED'},
      readingSchema:readingSchema(['candidate','reference','growth','worstBinDelta','bins'])},
    coherence:{sourceSelectors:['COHERENCE_ROWS',`${GATE_SCOPE}/COHERENCE_GATED`,
      `${GATE_SCOPE}/it:measures coherence on every profile the rows do not gate/notCoherenceGated`,
      'inGatedBed','inRecordedRole','isWellConditioned','PREDICATE_EXCLUDES','NO_SHAPE_AXIS_SCENES','REGRESSION_FLOORS'],
      limits:{numericWindow:C.COHERENCE_ROWS,numericProfiles:C.COHERENCE_GATED,
        presenceOnlyProfiles:C.notCoherenceGated,wellConditionedAreaRatio:C.WELL_CONDITIONED_AREA_RATIO,
        regressionFloors:Object.fromEntries(Object.entries(C.REGRESSION_FLOORS)
          .filter(([key])=>key.endsWith(' :: interiorLevelRatioGpuOverCss')))},
      applicability:{reader:'referee.ts:coherenceOwnerScope',bedPredicate:'inGatedBed/inRecordedRole',
        numericFlag:'sourceOwnerNumericWindowAdopted',presenceFlag:'sourceOwnerPresenceRequired',
        extraReadings:'Diagnostic only; no additional W50 completeness policy is implied'},
      exclusions:{conditioning:C.PREDICATE_EXCLUDES,noShape:C.NO_SHAPE_AXIS_SCENES},
      readingSchema:readingSchema(['deltaE'],{conditionalFinite:[{
        unless:{field:'ratioNotApplicable',equals:true},paths:['ratio']}],unmeasuredExceptions:[{
        kind:'diagnostic-only',evidenceEquals:{diagnosticOnly:true,sourceOwnerPresenceRequired:false}}]})},
  };
  return {schema:'w50-owner-contracts-1',ownerSource:C.source,readerSources,axes,intrinsic:{
    X75:{sourceSelectors:['opaqueGlassViolations','candidateIntrinsics'],source:readerSources.opacity,
      limits:{maxAlphaBase:X75_MAX_ALPHA_BASE,floatAllowance:X75_FLOAT_ALLOWANCE,
        integerSpanCssPx:{min:0,max:X75_SPAN_MAX_CSS_PX},dpr:X75_DEVICE_PIXEL_RATIOS,variants:MATERIAL_VARIANTS,
        tiers:['webgpu','css'],policy:'nominal'},
      applicability:'All runtime endpoints with production candidate substitution; no native/current scalar budget',
      exclusions:{accessibility:'Nominal-policy invariant, not accessibility occlusion'},
      referenceReading:'NOT_APPLICABLE',candidateCheckRequired:true},
    X76:{sourceSelectors:['isHold','isMethod','checkInheritance','checkRecordApplicability','candidateIntrinsics'],
      source:readerSources.seal,limits:{policy:'Fitted or explicit held record for active inheritance; moved leaves need methods'},
      applicability:'Candidate receded endpoints, role-bound before documents and candidate-specific record envelopes',
      exclusions:{retainedMeasured:'Only exact original measured entries at unchanged resolved values'},
      recordEnvelopes:{activeEntries:['endpointSha256','retainedMeasuredEntries','fittedEntries'],
        methods:['endpointSha256','methods']},referenceReading:'NOT_APPLICABLE',candidateCheckRequired:true},
  }};
}

const at=(object:any,path:string):unknown=>path.split('.').reduce((value,key)=>value?.[key],object);
function finiteTree(value:unknown):void {
  if(typeof value==='number'&&!Number.isFinite(value)) throw new Error('Nonfinite owner evidence');
  if(value&&typeof value==='object') for(const child of Object.values(value)) finiteTree(child);
}
function requireNumbers(value:unknown,paths:string[],label:string) {
  for(const path of paths) {
    const number=at(value,path);
    if(typeof number!=='number'||!Number.isFinite(number)) throw new Error(`${label}: missing finite ${path}`);
  }
}
function validateAxis(evidence:Evidence,contract:AxisContract,row:OwnerRow,axis:string) {
  finiteTree(evidence);
  if(evidence.state==='NOT_APPLICABLE') {
    if(!evidence.reason) throw new Error(`${axis}: applicability reason missing`);
    return;
  }
  if(evidence.state==='UNMEASURED') {
    const allowed=contract.readingSchema.unmeasuredExceptions.some(exception=>
      (exception.kind!=='named-cell'||exception.keys.includes(`${row.profile}/${row.scene}`))
      &&Object.entries(exception.evidenceEquals).every(([key,value])=>isDeepStrictEqual(at(evidence,key),value)));
    if(!allowed||!evidence.reason) throw new Error(`${axis}: unexcused UNMEASURED current evidence`);
    return;
  }
  if(evidence.state!=='MEASURED') throw new Error(`${axis}: invalid evidence state`);
  const schema=contract.readingSchema;
  requireNumbers(evidence,schema.requiredFinite,axis);
  for(const path of schema.requiredArrays) {
    const array=at(evidence,path);
    if(!Array.isArray(array)||!array.length) throw new Error(`${axis}: missing nonempty ${path}`);
  }
  for(const rule of schema.conditionalFinite) {
    if(!isDeepStrictEqual(at(evidence,rule.unless.field),rule.unless.equals)) requireNumbers(evidence,rule.paths,axis);
  }
}

/** A projection certifies the provenance and readability of CURRENT reference evidence,
 * not a candidate gate result. Measured misses/failures are deliberately retained. */
export function projectCurrent(inputsPin:Pin,reportPin:Pin,contractsPin:Pin,row:OwnerRow) {
  if(!row||Object.keys(row).sort().join('/')!=='profile/renderer/scene/statistic'
    ||row.statistic!=='owner-contracts'||!['webgpu','css'].includes(row.renderer)
    ||typeof row.profile!=='string'||typeof row.scene!=='string') throw new Error('Invalid owner row identity');
  const {context,report,snapshot}=projectionContext(inputsPin,reportPin,contractsPin);
  return projectPrepared(context,report,snapshot,row,{inputsPin,reportPin,contractsPin});
}
function projectionContext(inputsPin:Pin,reportPin:Pin,contractsPin:Pin) {
  const inputs=JSON.parse(pinnedBytes(inputsPin).toString());
  const snapshot=JSON.parse(pinnedBytes(contractsPin).toString()) as OwnerContracts;
  if(!isDeepStrictEqual(snapshot,ownerContracts(inputs.python))) throw new Error('Owner contracts differ from source-generated snapshot');
  const context=prepareCurrent(inputs);
  const report=JSON.parse(pinnedBytes(reportPin).toString()) as OwnerReport;
  if(!isDeepStrictEqual(report,context.current)) throw new Error('Owner report differs from reconstructed CURRENT evidence');
  return {context,report,snapshot};
}

export const OWNER_INVENTORY_SHA256='a666c1b00f4b1aff48bddeca9dacc1c1bc05dcf83bf908efddbe46c24c322d0c';
const INVENTORY=resolve(CAL,'results/2026-10-08-w50-g0-declaration/references.json');
/** All and only the original inventory's owner identities. Neither a caller list nor a
 * metric/verdict chooses membership. Other statistics in the same inventory stay separate. */
export function ownerRows(inventory:any):OwnerRow[] {
  if(inventory?.schema!=='w50-reference-inventory-1'||!Array.isArray(inventory.cells)) {
    throw new Error('Unknown original owner inventory schema');
  }
  const rows=inventory.cells.filter((cell:any)=>cell.statistic==='owner-contracts').map((cell:any)=>{
    if(typeof cell.profile!=='string'||!cell.profile||typeof cell.scene!=='string'||!cell.scene
      ||!['webgpu','css'].includes(cell.renderer)) throw new Error('Invalid owner inventory identity');
    return {profile:cell.profile,renderer:cell.renderer,scene:cell.scene,statistic:cell.statistic} as OwnerRow;
  });
  if(rows.length!==640) throw new Error('Original owner inventory must contain all 640 rows');
  const key=(row:OwnerRow)=>JSON.stringify([row.profile,row.renderer,row.scene,row.statistic]);
  if(new Set(rows.map(key)).size!==640) throw new Error('Duplicate owner inventory identity');
  return rows.sort((a:OwnerRow,b:OwnerRow)=>key(a).localeCompare(key(b)));
}
/** Reconstructs CURRENT once, then projects all fixed 640 identities. Immutable full
 * generation envelopes remain the aggregate context; they are not rewritten as subsets. */
export function projectCurrentBatch(inputsPin:Pin,reportPin:Pin,contractsPin:Pin,inventoryPin:Pin) {
  if(inventoryPin.path!==INVENTORY||inventoryPin.sha256!==OWNER_INVENTORY_SHA256) {
    throw new Error('Batch requires the original G0 owner inventory pin');
  }
  const inventory=JSON.parse(pinnedBytes(inventoryPin).toString());
  ownerRows(inventory); // Refuse an incomplete population before any measured input is opened.
  const {context,snapshot}=projectionContext(inputsPin,reportPin,contractsPin);
  const pins={inputsPin,reportPin,contractsPin};
  return {schema:'w50-owner-evidence-batch-1' as const,inventoryPin,...pins,
    rows:projectPreparedInventory(context,snapshot,inventory,pins)};
}
/** In-process projection over an already prepared context; external callers use the
 * pinned batch boundary above. It has no data reader, renderer, or preparation side effect. */
export function projectPreparedInventory(context:Prepared,snapshot:OwnerContracts,inventory:unknown,
  pins:{inputsPin:Pin;reportPin:Pin;contractsPin:Pin}) {
  return ownerRows(inventory).map(row=>projectPrepared(context,context.current,snapshot,row,pins));
}
function projectPrepared(context:Prepared,report:OwnerReport,snapshot:OwnerContracts,row:OwnerRow,
  pins:{inputsPin:Pin;reportPin:Pin;contractsPin:Pin}) {
  const cellId=`${row.profile}/${row.renderer}/${row.scene}`;
  const sourceRow=context.currentRows.find(candidate=>identity(candidate)===cellId);
  const evidence=report.cells[cellId];
  if(!sourceRow||!evidence) throw new Error(`Owner row absent from current report: ${cellId}`);
  if(!isDeepStrictEqual(Object.keys(evidence).sort(),[...IMAGE_AXES].sort())) throw new Error('Owner report axis set changed');
  const axes=Object.fromEntries(IMAGE_AXES.map(axis=>{
    const contract=snapshot.axes[axis],reading=evidence[axis]!;
    validateAxis(reading,contract,row,axis);
    return [axis,{evidence:reading,limits:contract.limits,applicability:contract.applicability,
      exclusions:contract.exclusions,readingSchema:contract.readingSchema}];
  }));
  const aggregateKeys:string[]=[];
  if(evidence.M1!.state!=='NOT_APPLICABLE') aggregateKeys.push(
    `M1/${row.profile.endsWith('-glass0.25')?.25:.5}/${row.profile.includes('-dark-')?'dark':'light'}/${sourceRow.state}`);
  if(evidence.C1!.state!=='NOT_APPLICABLE') aggregateKeys.push('C1');
  for(const key of aggregateKeys) {
    const value=report.aggregates[key];
    if(value?.state!=='MEASURED') throw new Error(`Owner aggregate is incomplete: ${key}`);
    finiteTree(value);
    const schema=snapshot.axes[key==='C1'?'C1':'M1'].readingSchema.aggregate!;
    requireNumbers(value,schema.requiredFinite,key);
    for(const map of schema.nonemptyObjects) {
      const object=at(value,map.field);
      if(!object||typeof object!=='object'||Array.isArray(object)||!Object.keys(object).length) {
        throw new Error(`${key}: missing aggregate ${map.field}`);
      }
      for(const entry of Object.values(object)) requireNumbers(entry,map.requiredFinite,key);
    }
  }
  const intrinsic=Object.fromEntries((['X75','X76'] as const).map(axis=>[axis,{
    contract:snapshot.intrinsic[axis],evidence:(report.intrinsic as Record<string,unknown>)[axis],
    referenceReading:'NOT_APPLICABLE',candidateCheckRequired:true,
  }]));
  return {schema:'w50-owner-evidence-1' as const,row,cellId,...pins,ownerSource:snapshot.ownerSource,
    axes,aggregateKeys,intrinsic};
}

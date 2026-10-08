import { isDeepStrictEqual } from 'node:util';
import { resolve } from 'node:path';
import { createCandidateEngine } from './frozen-engine.ts';
import { readJson, readPinned, samePin, absolutePin, selectOwnerUnion, admittedCandidateRows } from './union.ts';
import type { Pin } from '../owner/referee.ts';

const KEY=['profile','renderer','scene','statistic'];
const keyOf=(row:any)=>KEY.map(field=>row[field]);
const sorted=(values:any[])=>values.map(value=>JSON.stringify(value)).sort();
const equalSet=(a:any[],b:any[])=>isDeepStrictEqual(sorted(a),sorted(b));
export const FROZEN_CLOSURE_SHA256='91517fa49cb753ecddfd67ec724ddca70825c2f3ba5b8343962ea5239ddbd1dd';

/** Pure authenticated-document consistency checks; live.py establishes the nonserializable
 * dispatcher capability before a snapshot can be written or this child invoked. */
export function validateAuthority(snapshot:any,docs:any,configPin:Pin) {
  const {root,contract,batch,claim,gate,gateContract,gateBatch,inventory}=docs;
  if(snapshot.schema!=='w50-owner-live-capture-union-1'||snapshot.phase!=='exposure'
    ||contract.phase!=='exposure'||batch.phase!=='exposure') throw Error('Owner referee requires live exposure');
  const repo=root.repo;
  if(!samePin(snapshot.config,configPin)||!root.inputs?.some((pin:Pin)=>samePin(absolutePin(pin,repo),configPin))) {
    throw Error('Owner candidate config is not registered in live root');
  }
  if(contract.executionRootSha256!==snapshot.executionRoot.sha256
    ||!samePin(absolutePin(contract.batch,repo),snapshot.batch)
    ||!samePin(absolutePin(contract.gateResult,repo),snapshot.gateResult)) throw Error('Exposure pointers differ from live root');
  if(snapshot.claim.path!==snapshot.contract.path+'.started.json'||claim.phase!=='exposure'
    ||claim.contractSha256!==snapshot.contract.sha256||claim.batchSha256!==snapshot.batch.sha256
    ||claim.output!==snapshot.output||!claim.gpuLease||!claim.numericalAdmission) throw Error('Exposure claim differs');
  const cohort=snapshot.cohort;
  if(!Array.isArray(cohort)||!cohort.length||!equalSet(cohort,batch.cohort)||!equalSet(cohort,contract.cohort)
    ||!equalSet(cohort,gateContract.cohort)||!equalSet(cohort,gateBatch.cohort)
    ||!isDeepStrictEqual(gate.report?.candidateSha256s,cohort.map((pin:Pin)=>pin.sha256).sort())) {
    throw Error('Gate/exposure candidate cohort differs');
  }
  if(gateContract.phase!=='gate'||gateBatch.phase!=='gate'
    ||gateContract.executionRootSha256!==snapshot.executionRoot.sha256
    ||gate.contractSha256!==contract.gateContract.sha256
    ||gate.report?.status!=='PASS_EXPOSED_OWNER_PENDING'||gate.report.ownerChecks!=='PENDING_FULL_UNION'
    ||!isDeepStrictEqual(gate.captures,snapshot.gateCaptures)) throw Error('Qualified gate evidence differs');
  const intrinsic=absolutePin(batch.ownerIntrinsicRecords,repo);
  if(!samePin(intrinsic,absolutePin(gateBatch.ownerIntrinsicRecords,repo))
    ||!samePin(intrinsic,snapshot.ownerIntrinsicRecords)) throw Error('Post-fit intrinsic records differ from frozen gate batch');
  const original=inventory.cells.map(keyOf);
  const owners=inventory.cells.filter((row:any)=>row.statistic==='owner-contracts').map(keyOf);
  if(!equalSet(snapshot.unionExpectedCells.map(keyOf),original)
    ||!equalSet(snapshot.ownerUnionKeys,owners)||!equalSet(root.phaseDependencies.ownerUnionKeys,owners)
    ||!equalSet(snapshot.expectedExposureCells.map(keyOf),root.phaseDependencies.exposureKeys)) {
    throw Error('Original owner or phase union membership differs');
  }
}

function jsonNative(value:any):any {
  if(typeof value==='number'&&!Number.isFinite(value)) throw Error('Nonfinite owner candidate evidence');
  if(Array.isArray(value)) return value.map(item=>{
    if(item===undefined) throw Error('Undefined owner array entry');return jsonNative(item);
  });
  if(value&&typeof value==='object') return Object.fromEntries(Object.entries(value)
    .filter(([,item])=>item!==undefined).map(([key,item])=>[key,jsonNative(item)]));
  return value;
}

/** Called only by live-node.mjs after the genuine Python context writer and Node source
 * guard. No CLI autorun and no output write: the wrapper owns its exclusive result path. */
export function executeRequest(request:{snapshot:Pin;config:Pin}) {
  if(!request||!isDeepStrictEqual(Object.keys(request).sort(),['config','snapshot'])) throw Error('Invalid live owner request');
  if(process.env.W50_OWNER_LIVE_CONFIG_SHA256!==request.config.sha256
    ||process.env.W50_OWNER_LIVE_SNAPSHOT_SHA256!==request.snapshot.sha256
    ||process.env.W50_OWNER_LIVE_CONFIG!==request.config.path) throw Error('Missing live owner child admission');
  const config=readJson(request.config),snapshot=readJson(request.snapshot);
  if(config.schema!=='w50-owner-candidate-config-1') throw Error('Unknown candidate owner config');
  if(snapshot.executionRoot.sha256!==process.env.W50_OWNER_LIVE_ROOT_SHA256) throw Error('Unregistered live root');
  const root=readJson(snapshot.executionRoot),repo=root.repo;
  const contract=readJson(snapshot.contract),batch=readJson(snapshot.batch),claim=readJson(snapshot.claim);
  const gate=readJson(snapshot.gateResult);
  const gateContract=readJson(absolutePin(contract.gateContract,repo));
  const gateBatch=readJson(absolutePin(gateContract.batch,repo));
  const inventoryPin=absolutePin(root.references,repo);
  if(!samePin(inventoryPin,config.originalInventory)) throw Error('Owner inventory is not live root original');
  const inventory=readJson(inventoryPin);
  validateAuthority(snapshot,{root,contract,batch,claim,gate,gateContract,gateBatch,inventory},request.config);
  if(!request.snapshot.path.startsWith(resolve(snapshot.output)+'/')) throw Error('Snapshot outside claimed output');
  const frozenClosure=readJson(config.frozenSourceClosure);
  if(config.frozenSourceClosure.sha256!==FROZEN_CLOSURE_SHA256) throw Error('Unregistered frozen owner source closure');
  const frozenPins=new Map(frozenClosure.sources.map((pin:Pin)=>[pin.path,pin.sha256]));
  for(const [path,pin] of Object.entries(config.sourcePins) as [string,Pin][]) {
    if(frozenPins.get(path)!==pin.sha256||pin.path!==resolve(repo,path)) throw Error('Owner function source differs from frozen closure');
    readPinned(pin);
  }
  const declarations=snapshot.cohort.map((pin:Pin)=>absolutePin(pin,repo));
  const engine=createCandidateEngine({sourcePins:config.sourcePins,declarations});
  const inputs=readJson(config.ownerInputs),completed=readJson(config.completedOwnerReferences);
  const contracts=engine.loadContracts();
  if(!isDeepStrictEqual(completed.provenance,{owner:contracts.source,current:inputs.current,
    fixedReferences:inputs.references,declaration:inputs.declaration})) throw Error('Completed current owner report provenance differs');
  const declaration=readJson(inputs.declaration);
  const currentRows=engine.rowsOf(inputs.current),referenceRows=engine.rowsOf(inputs.references);
  const selected=selectOwnerUnion(currentRows,root.phaseDependencies,snapshot.cohort,
    snapshot.gateCaptures,snapshot.exposureCaptures,repo);
  const admitted=admittedCandidateRows(selected.records,engine.identityResolver,declaration,inputs.captures,repo);
  // Only the executable transport changes. Frozen matrices, native/backdrop pixels, completed
  // current report and original baselines are retained verbatim, and the substitution is named.
  const context={inputs:{...inputs,python:config.python},contracts,declaration,currentRows,referenceRows,current:completed};
  const report=engine.evaluateRows(context,admitted.rows,admitted.captures,true);
  const intrinsic=readJson(snapshot.ownerIntrinsicRecords);
  if(!equalSet(intrinsic.candidateDeclarations.map((pin:Pin)=>absolutePin(pin,repo)),declarations)) {
    throw Error('Intrinsic declarations differ from frozen candidate cohort');
  }
  report.intrinsic=engine.candidateIntrinsics({...intrinsic,candidateDeclarations:declarations},admitted.rows,currentRows);
  return jsonNative({...report,liveUnion:{snapshot:request.snapshot,config:request.config,
    gateResult:snapshot.gateResult,claim:snapshot.claim,cohort:snapshot.cohort,
    ownerInputs:config.ownerInputs,completedOwnerReferences:config.completedOwnerReferences,
    intrinsicRecords:snapshot.ownerIntrinsicRecords,sourcePins:config.sourcePins,
    runtimeClosure:config.runtimeClosure,pythonTransport:{from:inputs.python,to:config.python},
    dependencyKeys:currentRows.map((row:any)=>`${row.key.profileKey}/${row.key.web.renderer}/${row.key.sceneId}`).sort(),
    ownerKeys:snapshot.ownerUnionKeys,matrices:admitted.matrices,
    excludedBaselineRecords:selected.excludedBaselineRecords,
    excludedNonownerCanonicalKeys:selected.excludedNonownerCanonicalKeys,
    scope:'FULL_SAME_CANDIDATE_UNION; metric evidence only, full judge owns verdict'}});
}

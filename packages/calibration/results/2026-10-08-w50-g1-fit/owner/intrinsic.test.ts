import test from 'node:test';
import assert from 'node:assert/strict';
import { candidateIntrinsics } from './intrinsic.ts';
test('missing candidate declarations cannot certify intrinsic checks', () => {
  const report = candidateIntrinsics({candidateDeclarations:[],recededRecords:{}},[]);
  assert.equal(report.X75.state,'UNMEASURED');
  assert.equal(report.X76.state,'UNMEASURED');
});

// Small resolved objects exercise the same applicability helper candidateIntrinsics consumes.
// No real endpoint, fixture or matrix file is opened.
import * as intrinsic from './intrinsic.ts';
import * as referee from './referee.ts';
const activeSha='a'.repeat(64), recededSha='b'.repeat(64);
function fittingInput() {
  const historical={status:'measured',value:2,method:['original fit']};
  return {activeSha256:activeSha,recededSha256:recededSha,
    beforeResolved:{retained:2,moved:1},activeResolved:{retained:2,moved:3},
    beforePatch:{retained:2,moved:1},activePatch:{retained:2,moved:3},
    beforeEntries:{retained:historical} as Record<string,any>,
    activeRecords:{endpointSha256:activeSha,retainedMeasuredEntries:{retained:historical},
      fittedEntries:{moved:{status:'measured' as const,value:3,method:['synthetic fit against native']}}},
    recededRecords:{endpointSha256:recededSha,methods:{moved:{held:['held against native']}}}};
}
test('active fitting inventory is applicable only to its endpoint and resolved values',()=>{
  const good=fittingInput();
  assert.equal(intrinsic.checkRecordApplicability(good).state,'MEASURED');
  const wrong=fittingInput(); wrong.activeRecords.endpointSha256='c'.repeat(64);
  assert.throws(()=>intrinsic.checkRecordApplicability(wrong),/endpoint/);
  const stale=fittingInput(); stale.activeRecords.fittedEntries.moved.value=1;
  assert.throws(()=>intrinsic.checkRecordApplicability(stale),/value/);
  const short=fittingInput(); short.activeRecords.endpointSha256='a'.repeat(12);
  assert.throws(()=>intrinsic.checkRecordApplicability(short),/endpoint/);
  const wrongReceded=fittingInput(); wrongReceded.recededRecords.endpointSha256='c'.repeat(64);
  assert.throws(()=>intrinsic.checkRecordApplicability(wrongReceded),/endpoint/);
});
test('changed active values require new fitting methods, not a historical measured status',()=>{
  const missing=fittingInput(); missing.activeRecords.fittedEntries.moved.method=[];
  assert.equal(intrinsic.checkRecordApplicability(missing).state,'UNMEASURED');
  const stale:any=fittingInput();
  stale.beforeEntries.moved={status:'measured',value:1,method:['old fit']};
  delete stale.activeRecords.fittedEntries.moved;
  stale.activeRecords.retainedMeasuredEntries.moved={status:'measured',value:3,method:['old fit']};
  assert.throws(()=>intrinsic.checkRecordApplicability(stale),/historical|retained/);
  const result=intrinsic.checkRecordApplicability(fittingInput());
  assert.deepEqual(result.retainedHistoricalLeaves,['retained']);
  assert.deepEqual(result.newlyFittedLeaves,['moved']);
});
test('endpoint pair binding is role sensitive for both candidate and frozen-current rows',()=>{
  const row={key:{web:{capturePath:`materialProfile=a sha256:${activeSha.slice(0,12)} recededProfile=r sha256:${recededSha.slice(0,12)}`}}};
  assert.doesNotThrow(()=>referee.assertDocumentPair(row,activeSha,recededSha));
  assert.throws(()=>referee.assertDocumentPair(row,recededSha,activeSha),/role|pair/);
});
test('before documents must name their own dark position and pose',()=>{
  const active={profileKey:'apple-macos-27.0-1x-dark-standard-glass0.25',glassTintAmount:.25};
  const receded={profileKey:active.profileKey+'-receded',glassTintAmount:.25,kind:'receded-endpoint'};
  assert.doesNotThrow(()=>intrinsic.assertEndpointIdentity(active,.25,'active'));
  assert.doesNotThrow(()=>intrinsic.assertEndpointIdentity({profileKey:active.profileKey},.25,'active'));
  assert.doesNotThrow(()=>intrinsic.assertEndpointIdentity(receded,.25,'receded'));
  assert.throws(()=>intrinsic.assertEndpointIdentity(receded,.25,'active'),/identity|pose/);
  assert.throws(()=>intrinsic.assertEndpointIdentity(active,.5,'active'),/identity|position/);
});

// DL5o (a): historical family-keyed entries, on small synthetic material objects.
const family={status:'measured and fitted',value:{gain:4,width:2},previous:{gain:1},method:['historical family fit']};
function familyInput() {
  const input:any=fittingInput();
  input.beforeResolved={...input.beforeResolved,rim:{gain:4,width:2},other:5};
  input.activeResolved={...input.activeResolved,rim:{gain:4,width:2},other:5};
  input.beforePatch={...input.beforePatch,rim:{gain:4,width:2}};
  input.activePatch={...input.activePatch,rim:{gain:4,width:2}};
  input.beforeEntries.rim=family;
  return input;
}
test('a family-keyed historical entry is admitted verbatim as its hold when no moved leaf falls under it',()=>{
  const result=intrinsic.checkRecordApplicability(familyInput());
  assert.equal(result.state,'MEASURED');
  assert.deepEqual(result.familyHolds.admitted,{rim:{members:['rim.gain','rim.width']}});
  assert.deepEqual(result.familyHolds.refused,{});
  // A family entry is never retained as a leaf record: the port reads it from the pinned document.
  const carried=familyInput(); carried.activeRecords.retainedMeasuredEntries.rim=family;
  assert.throws(()=>intrinsic.checkRecordApplicability(carried),/Family-keyed/);
  // A value object marks a family even where the key is also a leaf (0.5's bodyChromaRetention).
  const named=familyInput(); named.beforeEntries.moved={status:'measured',value:{moved:1},method:['old']};
  assert.equal(intrinsic.partitionEntries(named.beforeEntries,['moved','retained']).familyEntries.moved,
    named.beforeEntries.moved);
  assert.equal(intrinsic.checkRecordApplicability(named).familyHolds.refused.moved?.reason,
    'A moved leaf falls under the family');
});
test('a family containing a moved leaf needs per-leaf fitted records for every member',()=>{
  const moved=familyInput(); moved.activeResolved.rim={gain:5,width:2}; moved.activePatch.rim={gain:5,width:2};
  const refused=intrinsic.checkRecordApplicability(moved);
  assert.equal(refused.state,'UNMEASURED');
  assert.deepEqual(refused.missingActive,['rim.gain','rim.width']);
  assert.deepEqual(refused.familyHolds.refused.rim,{members:['rim.gain','rim.width'],moved:['rim.gain'],
    reason:'A moved leaf falls under the family'});
  const fitted=familyInput(); fitted.activeResolved.rim={gain:5,width:2}; fitted.activePatch.rim={gain:5,width:2};
  fitted.activeRecords.fittedEntries['rim.gain']={status:'measured',value:5,method:['refit gain']};
  assert.deepEqual(intrinsic.checkRecordApplicability(fitted).missingActive,['rim.width']);
  fitted.activeRecords.fittedEntries['rim.width']={status:'measured',value:2,method:['held at the family fit']};
  assert.equal(intrinsic.checkRecordApplicability(fitted).state,'MEASURED');
  // The name rule is inclusive in the strict direction: a trailing-path match refuses too.
  const elsewhere=familyInput(); elsewhere.activeResolved.clear={width:9}; elsewhere.activePatch.clear={width:9};
  elsewhere.activeRecords.fittedEntries['clear.width']={status:'measured',value:9,method:['fit']};
  assert.deepEqual(intrinsic.checkRecordApplicability(elsewhere).familyHolds.refused.rim?.moved,['clear.width']);
  const silent=familyInput(); silent.beforeEntries.rim={...family,method:[]};
  assert.equal(intrinsic.checkRecordApplicability(silent).familyHolds.refused.rim?.reason,
    'The family entry carries no reading');
});
function recededInput() {
  return {activeResolved:{tone:{x:1,y:2},black:1,width:3},activePatch:{tone:{x:1,y:2},black:1,width:3},
    activeEntries:{} as Record<string,any>,
    beforePatch:{tone:{x:1,y:7},black:1},candidatePatch:{tone:{x:1,y:7},black:1},
    beforeEntries:{toneResponse:{status:'measured, with a floor',previous:{x:0,y:3},method:['x moves to the active']}} as Record<string,any>,
    methods:{black:{held:['black held at the active']}} as Record<string,any>};
}
test('an admitted receded family holds its inherited members; a refused one needs per-leaf records',()=>{
  const good=intrinsic.checkFamilyInheritance(recededInput());
  assert.equal(good.verdict,'within');
  assert.deepEqual(good.familyHolds.heldByFamily,{'tone.x':'toneResponse'});
  // The original leaf-keyed algorithm still requires an explicit hold where no family speaks.
  const bare=recededInput(); bare.methods={};
  assert.deepEqual(intrinsic.checkFamilyInheritance(bare).missing,['black']);
  // Moving a member refuses the family: the moved leaf needs a method, the others a record.
  const moved=recededInput(); moved.candidatePatch.tone={x:1,y:8};
  const refused=intrinsic.checkFamilyInheritance(moved);
  assert.equal(refused.verdict,'failure');
  assert.deepEqual(refused.missing,['tone.x','tone.y']);
  moved.methods['tone.y']=['refit y'];
  assert.deepEqual(intrinsic.checkFamilyInheritance(moved).missing,['tone.x']);
  moved.methods['tone.x']={held:['x held at the active']};
  assert.equal(intrinsic.checkFamilyInheritance(moved).verdict,'within');
  // Dropping a member the before document stated refuses the family too: it needs its own record.
  const dropped=recededInput(); dropped.candidatePatch={tone:{x:1},black:1} as any;
  const refusedByDrop=intrinsic.checkFamilyInheritance(dropped);
  assert.deepEqual(refusedByDrop.familyHolds.refused.toneResponse?.moved,['tone.y']);
  assert.deepEqual(refusedByDrop.missing,['tone.x','tone.y']);
  // A family never covers a leaf the before document did not state at the candidate's value.
  const named=recededInput(); named.candidatePatch={tone:{x:1,y:7},black:1,width:3} as any;
  assert.equal(intrinsic.checkFamilyInheritance(named).familyHolds.refused.toneResponse,undefined);
  assert.deepEqual(intrinsic.checkFamilyInheritance(named).missing,['width']);
});

// The shipped dark pairs, read from W50 G0's references copies (the before documents the live
// records pin). At 0.5 every historical entry is family-keyed; at 0.25 every one is leaf-keyed.
import { readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { DEFAULT_MATERIAL_PROFILE, withMaterialOverrides } from '@vitrea/renderer-webgpu';
const DOCS=resolve(dirname(fileURLToPath(import.meta.url)),'../../2026-10-08-w50-g0-declaration/references/documents');
const doc=(sha:string)=>JSON.parse(readFileSync(resolve(DOCS,sha+'.json'),'utf8'));
const PAIRS={'0.5':['0eac5b294cc235e2ba03841472211e63f85d36258a20951bef6f974931cda445',
  '5cec8c9612012a8988e37ee51a80bcc8de35b306f6f8464d596dfdbbdbcef0d2'],
'0.25':['b2d074d2df2444a614304d11e906b5f91d8968bce161efbd8f34fc8da5be9186',
  '940384c06f73df1cbe2554e395d1db2a09c23a7bb6a57cdb2094807718483735']};
function identityAt(position:'0.5'|'0.25',methods:Record<string,any>) {
  const [a,r]=PAIRS[position],active=doc(a),receded=doc(r);
  const resolved=withMaterialOverrides(DEFAULT_MATERIAL_PROFILE,active.patch);
  const {leafEntries}=intrinsic.partitionEntries(active.entries,Object.keys(flattenLeaves(resolved)));
  const retainedMeasuredEntries=Object.fromEntries(Object.entries(leafEntries).filter(([,e]:any)=>e.status==='measured'));
  const applicability=intrinsic.checkRecordApplicability({activeSha256:a,recededSha256:r,
    beforeResolved:resolved,activeResolved:resolved,beforePatch:active.patch,activePatch:active.patch,
    beforeEntries:active.entries,activeRecords:{endpointSha256:a,retainedMeasuredEntries,fittedEntries:{}},
    recededRecords:{endpointSha256:r,methods}});
  return {applicability,inheritance:intrinsic.checkFamilyInheritance({activeResolved:resolved,activePatch:active.patch,
    activeEntries:applicability.activeEntries,beforePatch:receded.patch,beforeEntries:receded.entries,
    candidatePatch:receded.patch,methods})};
}
function flattenLeaves(node:any,prefix='',out:Record<string,any>={}) {
  for(const [k,v] of Object.entries(node)) {
    const path=prefix?`${prefix}.${k}`:k;
    if(v&&typeof v==='object'&&!Array.isArray(v)) flattenLeaves(v,path,out); else out[path]=v;
  }
  return out;
}
test('the shipped 0.5 pair reads X76 at identity once the two unrecorded inherited leaves are held',()=>{
  const bare=identityAt('0.5',{});
  assert.equal(bare.applicability.state,'MEASURED');
  assert.deepEqual(Object.keys(bare.applicability.familyHolds.admitted).sort(),['backdropToneAdaptation',
    'backdropToneResponse','bodyChromaRetention','cssTierBlur','outerShadow','outerShadowSpanGraded','rim',
    'scatter','scatterScaleSelectivity']);
  assert.deepEqual(bare.inheritance.missing,['backdropToneBlackStrength','optics.clear.rimLevelGain']);
  assert.deepEqual(bare.inheritance.familyHolds.heldByFamily,{backdropToneAnchorX:'backdropToneResponse',
    'outerShadow.liftAmplitude':'outerShadow','outerShadow.thinOcclusionDark':'outerShadow'});
  const held=Object.fromEntries(['backdropToneAnchorX','backdropToneBlackStrength','optics.clear.rimLevelGain',
    'outerShadow.liftAmplitude','outerShadow.thinOcclusionDark'].map(leaf=>[leaf,{held:['held at the active']}]));
  assert.equal(identityAt('0.5',held).inheritance.verdict,'within');
});
test('the shipped 0.25 pair keeps the original leaf-keyed reading',()=>{
  const methods=JSON.parse(readFileSync(resolve(DOCS,'../../../2026-10-07-w49a-g1-landing/seal/method.json'),'utf8'));
  const read=identityAt('0.25',methods);
  assert.deepEqual(read.applicability.familyHolds,{admitted:{},refused:{}});
  assert.equal(read.inheritance.verdict,'within');
  assert.deepEqual(read.inheritance.familyHolds.heldByFamily,{});
  assert.ok(identityAt('0.25',{}).inheritance.missing.length>0);
});

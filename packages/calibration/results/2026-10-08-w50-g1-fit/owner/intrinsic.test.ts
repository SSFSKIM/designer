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
    beforeEntries:{retained:historical},
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

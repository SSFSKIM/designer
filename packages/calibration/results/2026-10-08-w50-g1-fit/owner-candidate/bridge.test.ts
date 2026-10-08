import test from 'node:test';
import assert from 'node:assert/strict';
import { validateAuthority } from './bridge.ts';
const pin=(name:string,letter='a')=>({path:'/repo/'+name,sha256:letter.repeat(64)});
function authority() {
  const configPin=pin('config'),rootPin=pin('root'),contractPin=pin('exposure','b'),batchPin=pin('batch','c');
  const gatePin=pin('gate.result','d'),claimPin=pin('exposure.started.json','e');
  const intrinsicPin=pin('intrinsic','2'),gateContractPin=pin('gate','3'),gateBatchPin=pin('gate.batch','4');
  const cohort=[pin('candidate25','f'),pin('candidate50','1')];
  const deps={ownerUnionKeys:[],gateKeys:[],exposureKeys:[]};
  const snapshot:any={schema:'w50-owner-live-capture-union-1',phase:'exposure',config:configPin,
    executionRoot:rootPin,contract:contractPin,batch:batchPin,claim:claimPin,gateResult:gatePin,
    cohort,ownerIntrinsicRecords:intrinsicPin,ownerUnionKeys:[],expectedExposureCells:[],unionExpectedCells:[],output:'/scratch/run',
    gateCaptures:{status:'CAPTURED'},exposureCaptures:{status:'CAPTURED'}};
  const docs:any={root:{repo:'/repo',inputs:[configPin],phaseDependencies:deps,references:pin('inventory')},
    contract:{phase:'exposure',executionRootSha256:rootPin.sha256,batch:batchPin,cohort,gateResult:gatePin,gateContract:gateContractPin},
    gateContract:{phase:'gate',executionRootSha256:rootPin.sha256,batch:gateBatchPin,cohort},
    gateBatch:{phase:'gate',cohort,ownerIntrinsicRecords:intrinsicPin},
    batch:{phase:'exposure',cohort,ownerIntrinsicRecords:intrinsicPin},claim:{phase:'exposure',contractSha256:contractPin.sha256,
      batchSha256:batchPin.sha256,output:'/scratch/run',gpuLease:'genuine-token',numericalAdmission:{admitted:true}},
    gate:{contractSha256:gateContractPin.sha256,captures:snapshot.gateCaptures,report:{candidateSha256s:cohort.map(p=>p.sha256).sort(),
      status:'PASS_EXPOSED_OWNER_PENDING',ownerChecks:'PENDING_FULL_UNION'}},inventory:{cells:[]}};
  return {snapshot,docs,configPin};
}
test('live owner authority binds exposure claim and same-candidate gate, not exposure result',()=>{
  const a=authority();
  assert.doesNotThrow(()=>validateAuthority(a.snapshot,a.docs,a.configPin));
  const gate=authority();gate.snapshot.phase='gate';
  assert.throws(()=>validateAuthority(gate.snapshot,gate.docs,gate.configPin),/exposure/);
  const wrong=authority();wrong.docs.claim.contractSha256='0'.repeat(64);
  assert.throws(()=>validateAuthority(wrong.snapshot,wrong.docs,wrong.configPin),/claim/);
  const other=authority();other.docs.gate.report.candidateSha256s=['0'.repeat(64)];
  assert.throws(()=>validateAuthority(other.snapshot,other.docs,other.configPin),/candidate|gate/);
});
test('copied gate captures and unregistered config cannot become live owner authority',()=>{
  const a=authority();a.snapshot.gateCaptures={status:'CAPTURED',forged:true};
  assert.throws(()=>validateAuthority(a.snapshot,a.docs,a.configPin),/gate/);
  const b=authority();b.docs.root.inputs=[];
  assert.throws(()=>validateAuthority(b.snapshot,b.docs,b.configPin),/registered/);
});
test('post-fit intrinsic records must be exactly those frozen in the gate batch',()=>{
  const a=authority();a.docs.batch.ownerIntrinsicRecords=pin('other-methods','9');
  assert.throws(()=>validateAuthority(a.snapshot,a.docs,a.configPin),/intrinsic/);
});

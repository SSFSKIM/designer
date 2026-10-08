import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdtempSync, writeFileSync, readFileSync, rmSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { prepareCurrent } from './api.ts';
import { ownerContracts, projectCurrent } from './witness.ts';
import { executeRequest } from './bridge.ts';
const PYTHON='/Users/new/vitrea-w49/py/bin/python';
const home=dirname(fileURLToPath(import.meta.url));
function fixture() {
  const dir=mkdtempSync(join(home,'.synthetic-'));
  const put=(name:string,value:any)=>{
    const bytes=Buffer.from(JSON.stringify(value)),path=join(dir,name);
    writeFileSync(path,bytes);return {path,sha256:createHash('sha256').update(bytes).digest('hex')};
  };
  const profile='apple-macos-27.0-1x-dark-standard-glass0.5',scene='light-solid__rrect-sm__rest';
  const declaration=put('scenes.json',{canvas:{width:100,height:100},
    components:{'rrect-sm':{kind:'rrect',size:[32,32]}},
    scenes:[{id:scene,component:'rrect-sm',background:'light-solid',state:'rest'}],
    split:{validation:[scene]}});
  const matrix=(name:string,a:string,b:string,mean:number)=>{
    const active=a.padEnd(64,'0'),receded=b.padEnd(64,'0');
    return {matrix:put(name,{schemaVersion:5,cells:[{key:{profileKey:profile,sceneId:scene,
      web:{renderer:'webgpu',samplingBackend:'css-backdrop',capturePath:
        `materialProfile=a.json sha256:${active.slice(0,12)} recededProfile=r.json sha256:${receded.slice(0,12)}`}},
      tier:'texture',fixtureSet:'validation',state:'rest',
      material:{interiorMeanNative:{value:.2},interiorMeanWeb:{value:mean}}}]}),
      documents:{'a.json':active,'r.json':receded}};
  };
  const inputs={declaration,current:[matrix('current.json','0eac5b294cc2','b',.4)],
    references:[matrix('reference.json','eab099cc6698','4e68f81869f6',.21)],
    captures:{},referenceCaptures:{},python:PYTHON};
  const inputsPin=put('inputs.json',inputs),report=prepareCurrent(inputs).current;
  const reportPin=put('report.json',report),contracts=ownerContracts(PYTHON),contractsPin=put('contracts.json',contracts);
  const row={profile,renderer:'webgpu',scene,statistic:'owner-contracts'};
  return {dir,put,inputs,inputsPin,reportPin,contractsPin,contracts,report,row};
}
test('source-owned snapshot and current projection round-trip without requiring baseline success',()=>{
  const f=fixture();
  try {
    assert.deepEqual(JSON.parse(JSON.stringify(f.contracts)),f.contracts);
    const result=projectCurrent(f.inputsPin,f.reportPin,f.contractsPin,f.row);
    const bridged=executeRequest({mode:'project-current',inputsPin:f.inputsPin,
      completedReferencesPin:f.reportPin,contractsPin:f.contractsPin,row:f.row});
    assert.deepEqual(bridged,result);
    assert.equal(result.schema,'w50-owner-evidence-1');
    assert.deepEqual(result.row,f.row);
    assert.equal(result.axes.L1.evidence.verdict,'failure');
    assert.equal(result.axes.L1.evidence.candidate,.4);
    assert.equal(result.axes.L1.evidence.native,.2);
    assert.equal(result.axes.L1.evidence.reference,.21);
    assert.deepEqual(result.axes.L1.limits,f.contracts.axes.L1.limits);
    assert.deepEqual(JSON.parse(JSON.stringify(result)),result);
    assert.equal(result.intrinsic.X75.referenceReading,'NOT_APPLICABLE');
    assert.equal(Object.hasOwn(result.intrinsic.X75,'native'),false);
  } finally {rmSync(f.dir,{recursive:true});}
});
test('rehashing a changed budget or numeric report does not make it source-owned',()=>{
  const f=fixture();
  try {
    const snapshot=structuredClone(f.contracts); snapshot.axes.L1.limits.absolute=1;
    assert.throws(()=>projectCurrent(f.inputsPin,f.reportPin,f.put('wrong-contracts.json',snapshot),f.row),/contract/i);
    const report=structuredClone(f.report);report.cells[`${f.row.profile}/webgpu/${f.row.scene}`].L1.candidate=.9;
    assert.throws(()=>projectCurrent(f.inputsPin,f.put('wrong-report.json',report),f.contractsPin,f.row),/report/i);
    assert.throws(()=>projectCurrent(f.inputsPin,f.reportPin,f.contractsPin,{...f.row,scene:'other'}),/row/i);
    assert.throws(()=>projectCurrent(f.inputsPin,f.reportPin,f.contractsPin,{...f.row,statistic:'T1'}),/row/i);
  } finally {rmSync(f.dir,{recursive:true});}
});
test('an actual unmeasured baseline cannot become completed owner evidence',()=>{
  const f=fixture();
  try {
    const inputs={...f.inputs,references:[]};
    const report=prepareCurrent(inputs).current;
    assert.equal(report.cells[`${f.row.profile}/webgpu/${f.row.scene}`].L1.state,'UNMEASURED');
    assert.throws(()=>projectCurrent(f.put('missing-inputs.json',inputs),
      f.put('missing-report.json',report),f.contractsPin,f.row),/unexcused UNMEASURED/);
  } finally {rmSync(f.dir,{recursive:true});}
});
test('an exact named absent mean is explicit evidence, never a fabricated scalar',()=>{
  const f=fixture();
  try {
    const scene='dark-solid__capsule-button__inactive';
    const replace=(input:any,name:string)=>{
      const matrix=JSON.parse(readFileSync(input.matrix.path,'utf8'));
      const row=matrix.cells[0];row.key.sceneId=scene;row.state='inactive';
      row.material={interiorMeanNative:{value:null},interiorMeanWeb:{value:null}};
      return {...input,matrix:f.put(name,matrix)};
    };
    const inputs={...f.inputs,declaration:f.put('null-scene.json',{
      canvas:{width:100,height:100},components:{'capsule-button':{kind:'capsule',size:[96,44]}},
      scenes:[{id:scene,component:'capsule-button',background:'dark-solid',state:'inactive'}],
      split:{validation:[scene]}}),current:[replace(f.inputs.current[0],'null-current.json')],
      references:[replace(f.inputs.references[0],'null-reference.json')]};
    const report=prepareCurrent(inputs).current;
    const result=projectCurrent(f.put('null-inputs.json',inputs),f.put('null-report.json',report),
      f.contractsPin,{...f.row,scene});
    assert.equal(result.axes.L1.evidence.state,'UNMEASURED');
    assert.equal(result.axes.L1.evidence.namedExclusion,true);
    assert.equal(Object.hasOwn(result.axes.L1.evidence,'native'),false);
    assert.equal(Object.hasOwn(result.axes.L1.evidence,'candidate'),false);
  } finally {rmSync(f.dir,{recursive:true});}
});

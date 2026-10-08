import test from 'node:test';
import assert from 'node:assert/strict';
import { selectOwnerUnion, checkDrawnIdentity, admittedCandidateRows } from './union.ts';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const profile='apple-macos-27.0-1x-dark-standard-glass0.25';
const cohort=[{path:'/candidate.json',sha256:'a'.repeat(64)}];
const row=(scene:string)=>({key:{profileKey:profile,sceneId:scene,web:{renderer:'webgpu'}}});
const record=(scene:string,lane='candidate')=>({profile,scene,renderer:'webgpu',sceneSource:'canonical',lane,
  candidate:cohort[0],row:row(scene)});
const bundle=(records:any[])=>({status:'CAPTURED',candidateSha256s:cohort.map(p=>p.sha256),captures:records});
const key=(scene:string)=>[profile,'webgpu',scene,'owner-contracts'];
test('owner union is complete same-candidate gate plus exposure, never baseline fill',()=>{
  const context=[row('gate'),row('exposure')];
  const dependencies={gateKeys:[key('gate')],exposureKeys:[key('exposure')],ownerUnionKeys:[key('gate'),key('exposure')]};
  const result=selectOwnerUnion(context,dependencies,cohort,bundle([record('gate')]),
    bundle([record('exposure'),record('exposure','current')]));
  assert.equal(result.records.length,2);
  assert.equal(result.excludedBaselineRecords,1);
  assert.throws(()=>selectOwnerUnion(context,dependencies,cohort,bundle([record('gate')]),
    bundle([record('exposure','current')])),/missing|membership/i);
  const changed=record('exposure');changed.candidate={...cohort[0],sha256:'b'.repeat(64)};
  assert.throws(()=>selectOwnerUnion(context,dependencies,cohort,bundle([record('gate')]),bundle([changed])),/candidate/i);
});
test('duplicate, wrong-phase and absent dependency records refuse without held context fill',()=>{
  const deps={gateKeys:[key('gate')],exposureKeys:[key('exposure')],ownerUnionKeys:[key('gate')]};
  const before=bundle([record('gate')]);
  assert.throws(()=>selectOwnerUnion([row('gate')],deps,cohort,before,bundle([record('gate')])),/phase|membership/i);
  assert.throws(()=>selectOwnerUnion([row('gate')],deps,cohort,bundle([record('gate'),record('gate')]),
    bundle([record('exposure')])),/duplicate/i);
  assert.throws(()=>selectOwnerUnion([row('gate'),row('held')],deps,cohort,before,
    bundle([record('exposure')])),/held|missing/i);
});
test('drawn endpoint is checked against production-resolved candidate and actual page',()=>{
  const r:any={...record('gate'),endpoint:{profileKey:'candidate-dark',resolvedMaterialSha256:'c'.repeat(16)}};
  const candidate:any={declaration:cohort[0],position:.25,endpoints:{'active.dark':r.endpoint}};
  const page={sceneId:'gate',requestedRenderer:'webgpu',windowActivation:'active',colorScheme:'dark',
    materialMode:'candidate',candidateDocument:{mode:'candidate',declarationSha256:'a'.repeat(12)},
    material:{...r.endpoint,tuned:false,glassTintAmount:.25},groups:[{state:{activeRenderer:'webgpu',health:'ok',
      materialDocument:{...r.endpoint,tuned:false,glassTintAmount:.25}}}]};
  const scene={id:'gate',state:'rest'};
  assert.doesNotThrow(()=>checkDrawnIdentity(r,{page},candidate,scene));
  assert.throws(()=>checkDrawnIdentity(r,{page:{...page,sceneId:'other'}},candidate,scene),/identity/);
  assert.throws(()=>checkDrawnIdentity(r,{page:{...page,material:{...page.material,tuned:true}}},candidate,scene),/endpoint/);
});
test('record admission preserves raw rows and rejects refiled matrix/metadata identities',()=>{
  const dir=mkdtempSync(join(dirname(fileURLToPath(import.meta.url)),'.synthetic-'));
  try {
    const put=(name:string,value:any)=>{const raw=Buffer.from(JSON.stringify(value)),path=join(dir,name);
      writeFileSync(path,raw);return {path,sha256:createHash('sha256').update(raw).digest('hex')};};
    const rawRow:any={...row('gate'),material:{interiorMeanWeb:{value:.2}}};
    rawRow.key.web={renderer:'webgpu',samplingBackend:'gpu-texture',sceneId:'gate',
      capturePath:'materialProfile=candidate candidateDocument=/candidate.json declarationSha256=aaaaaaaaaaaa'};
    const endpoint={path:'/endpoint',sha256:'b'.repeat(64),profileKey:'candidate-dark',resolvedMaterialSha256:'c'.repeat(16)};
    const material={profileKey:endpoint.profileKey,resolvedMaterialSha256:endpoint.resolvedMaterialSha256,
      tuned:false,glassTintAmount:.25};
    const r:any={...record('gate'),row:rawRow,endpoint,matrix:put('matrix.json',{schemaVersion:5,cells:[rawRow]}),
      artifacts:{cell:put('metadata.json',rawRow.key.web),png:{path:'/not-opened.png',sha256:'0'.repeat(64)},
        report:put('report.json',{page:{sceneId:'gate',requestedRenderer:'webgpu',windowActivation:'active',
          colorScheme:'dark',materialMode:'candidate',candidateDocument:{mode:'candidate',declarationSha256:'a'.repeat(12)},
          material,groups:[{state:{activeRenderer:'webgpu',health:'ok',materialDocument:material}}]}})}};
    const resolver={resolve:()=>({declaration:cohort[0],position:.25,endpoints:{'active.dark':endpoint}}),
      documents:()=>({'/endpoint':'b'.repeat(64)})};
    const declaration={scenes:[{id:'gate',state:'rest'}]};
    const originals:any={[`${profile}/webgpu/gate`]:{native:{path:'/native',sha256:'1'.repeat(64)},
      backdrop:{path:'/backdrop',sha256:'2'.repeat(64)}}};
    const before=JSON.stringify(r);
    const result=admittedCandidateRows([r],resolver,declaration,originals);
    assert.deepEqual(result.rows,[rawRow]);assert.equal(JSON.stringify(r),before);
    assert.equal(result.captures[`${profile}/webgpu/gate`].native,originals[`${profile}/webgpu/gate`].native);
    const wrong=structuredClone(r);wrong.row.material.interiorMeanWeb.value=.9;
    assert.throws(()=>admittedCandidateRows([wrong],resolver,declaration,originals),/differs from pinned matrix/);
    const refiled=structuredClone(r);refiled.artifacts.cell=put('wrong-meta.json',{...rawRow.key.web,sceneId:'other'});
    assert.throws(()=>admittedCandidateRows([refiled],resolver,declaration,originals),/metadata differs/);
    assert.throws(()=>admittedCandidateRows([r],resolver,declaration,{}),/original native/);
  }finally{rmSync(dir,{recursive:true});}
});
test('repository-relative cohort spelling is preserved while identity compares resolved pins',()=>{
  const deps={gateKeys:[key('gate')],exposureKeys:[],ownerUnionKeys:[key('gate')]};
  const r=record('gate');r.candidate={path:'candidate.json',sha256:cohort[0].sha256};
  const original=JSON.stringify(r);
  const result=selectOwnerUnion([row('gate')],deps,[{path:'/repo/candidate.json',sha256:cohort[0].sha256}],
    bundle([r]),bundle([]),'/repo');
  assert.equal(result.records[0],r);assert.equal(JSON.stringify(r),original);
});

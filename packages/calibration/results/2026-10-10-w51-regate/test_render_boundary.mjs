import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {test} from 'node:test';
import {fileURLToPath} from 'node:url';
import {mkdtempSync,mkdirSync,writeFileSync,readFileSync,rmSync,realpathSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {resolve,dirname,basename} from 'node:path';
import {createHash} from 'node:crypto';
import {validateAuthority} from './render-admission.mjs';

test('direct renderer wrapper refuses before importing the capture driver', () => {
  const wrapper=fileURLToPath(new URL('./web/capture-web.ts',import.meta.url));
  const result=spawnSync(process.execPath,['--import','tsx',wrapper,'invented-scene','--renderer','webgpu'],
    {cwd:fileURLToPath(new URL('../../',import.meta.url)),env:{...process.env,W51_MEMBER_AUTHORITY:'',W51_MEMBER_AUTHORITY_SHA256:''},encoding:'utf8'});
  assert.notEqual(result.status,0);
  assert.match(result.stderr,/W51 member authority required/);
  assert.doesNotMatch(result.stderr,/playwright|browserType\.launch/);
});

test('renderer admits exactly the claimed member, rejecting changed CLI and consumed phase', () => {
  const folder=realpathSync(mkdtempSync(resolve(tmpdir(),'w51-render-test-')));
  const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
  const put=(path,value)=>{mkdirSync(dirname(path),{recursive:true});writeFileSync(path,JSON.stringify(value));
    return {path,sha256:hash(readFileSync(path))};};
  try {
    const endpoint=put(resolve(folder,'endpoint.json'),{patch:{}});
    const candidate=put(resolve(folder,'candidate.json'),{endpoints:{'active.dark':endpoint}});
    const profile='apple-macos-27.0-1x-dark-standard-glass0.25',scene='synthetic-scene';
    const base={profile,renderer:'webgpu',sceneSource:'canonical',candidate,scenes:[scene]};
    const batch=put(resolve(folder,'batch.json'),{runs:[base]});
    const root=put(resolve(folder,'root.json'),{repo:folder,cohort:[candidate],batches:{gate:batch}});
    writeFileSync(root.path+'.sha256',`${root.sha256}  ${basename(root.path)}\n`);
    const output=resolve(folder,'output');
    const contract=put(resolve(output,'contract.json'),{executionRootSha256:root.sha256,batch,logicalOutput:output});
    const destination=resolve(output,'attempts','000001','quarantine','member');
    const run={...base,captureRoot:resolve(destination,'captures'),matrixPath:resolve(destination,'matrix.json')};
    const member={id:'member',runIndex:0,scene,candidate,lane:'candidate',run};
    const attempt=put(resolve(contract.path+'.phase','attempts','000001','contract.json'),
      {logicalContract:contract,ordinal:1,members:[member]});
    const claim=put(resolve(dirname(attempt.path),'started.json'),
      {attempt,logicalContract:contract,gpuLease:'test-lease',pid:process.pid});
    const authority={root,contract,batch,claim,member};
    const argv=[scene,'--renderer','webgpu','--scale','1','--color-scheme','dark',
      '--candidate-document',candidate.path,'--out',resolve(run.captureRoot,profile),'--alpha'];
    assert.equal(validateAuthority(authority,argv,'test-lease').member,'member');
    assert.throws(()=>validateAuthority(authority,argv.map(v=>v==='webgpu'?'css':v),'test-lease'),/arguments/);
    assert.throws(()=>validateAuthority(authority,argv,'other-lease'),/phase\/lease/);
    const changed=structuredClone(authority);changed.member.scene='different';
    assert.throws(()=>validateAuthority(changed,argv,'test-lease'),/active capture attempt/);
    const checkpoint=resolve(dirname(attempt.path),'members','member.json');
    put(checkpoint,{admitted:true});
    assert.throws(()=>validateAuthority(authority,argv,'test-lease'),/active capture attempt/);
    writeFileSync(contract.path+'.phase/analysis.started.json','{}');
    assert.throws(()=>validateAuthority(authority,argv,'test-lease'),/analysis already consumed/);
  } finally {rmSync(folder,{recursive:true,force:true});}
});
